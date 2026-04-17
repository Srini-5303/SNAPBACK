"""
SNAPBACK — Backend API

Endpoints:
  GET  /api/sports                → list all available sports
  GET  /api/sport-preview/{sport} → 4 Claude-generated sport exercises (no user data)
  POST /api/analyze               → CV result → gap analysis (plan optional via skip_plan)
  POST /api/plan                  → generate personalised progressive plan with user profile

Run:
  uvicorn main:app --reload --port 8000
"""

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from config import SPORT_BLUEPRINTS
from models import AnalyzeRequest, AnalysisResponse, PlanRequest, PlanResponse
from pose import get_cv_result
from gap_analysis import compute_gaps
from claude_client import generate_plan, generate_sport_preview

app = FastAPI(title="SNAPBACK API", version="0.3.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/api/sports")
def list_sports():
    return [
        {"key": key, "name": bp["name"], "tag": bp["tag"], "emoji": bp["emoji"]}
        for key, bp in SPORT_BLUEPRINTS.items()
    ]


@app.get("/api/sport-preview/{sport}")
def sport_preview(sport: str):
    if sport not in SPORT_BLUEPRINTS:
        raise HTTPException(status_code=400, detail=f"Unknown sport '{sport}'")
    blueprint = SPORT_BLUEPRINTS[sport]
    exercises = generate_sport_preview(blueprint["name"], blueprint["joints"])
    return {"sport": sport, "sport_name": blueprint["name"], "exercises": exercises}


@app.post("/api/analyze", response_model=AnalysisResponse)
def analyze(request: AnalyzeRequest):
    """
    Gap analysis only (or full pipeline when skip_plan=False).

    Request body:
      sport       — sport key
      use_demo    — use demo CV data
      skip_plan   — if True, return empty plan (plan generated separately via /api/plan)
      cv_result   — real CV server output
      user_profile — dominant_hand + weeks_to_return (used in plan if skip_plan=False)
    """
    if request.sport not in SPORT_BLUEPRINTS:
        raise HTTPException(status_code=400, detail=f"Unknown sport '{request.sport}'")

    cv_data = get_cv_result(
        use_demo=request.use_demo,
        provided=request.cv_result.model_dump() if request.cv_result else None,
    )

    gaps, body_map, readiness_score = compute_gaps(request.sport, cv_data)

    if request.skip_plan:
        plan = []
    else:
        profile = request.user_profile.model_dump() if request.user_profile else None
        plan = generate_plan(SPORT_BLUEPRINTS[request.sport]["name"], gaps, profile)

    return AnalysisResponse(
        sport=request.sport,
        sport_name=SPORT_BLUEPRINTS[request.sport]["name"],
        overall_score=cv_data.get("overall_score", 0.0),
        gaps=gaps,
        body_map=body_map,
        readiness_score=readiness_score,
        plan=plan,
    )


@app.post("/api/plan", response_model=PlanResponse)
def plan(request: PlanRequest):
    """
    Generate a personalised progressive plan after the user answers profile questions.

    Request body:
      sport        — sport key
      use_demo     — use demo CV data when no cv_result
      cv_result    — real CV server output
      user_profile — { dominant_hand, weeks_to_return }
    """
    if request.sport not in SPORT_BLUEPRINTS:
        raise HTTPException(status_code=400, detail=f"Unknown sport '{request.sport}'")

    cv_data = get_cv_result(
        use_demo=request.use_demo,
        provided=request.cv_result.model_dump() if request.cv_result else None,
    )

    gaps, _, _ = compute_gaps(request.sport, cv_data)
    profile    = request.user_profile.model_dump() if request.user_profile else None
    plan_weeks = generate_plan(SPORT_BLUEPRINTS[request.sport]["name"], gaps, profile)

    return PlanResponse(
        sport=request.sport,
        sport_name=SPORT_BLUEPRINTS[request.sport]["name"],
        plan=plan_weeks,
    )
