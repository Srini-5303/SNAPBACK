"""
SNAPBACK / ReMotion — Backend API

Endpoints:
  GET  /api/sports                → list all available sports
  GET  /api/sport-preview/{sport} → 4 Claude-generated sport exercises (no user data)
  POST /api/analyze               → full pipeline: CV result → gap analysis → Claude plan

Run:
  uvicorn main:app --reload --port 8000
"""

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from config import SPORT_BLUEPRINTS
from models import AnalyzeRequest, AnalysisResponse
from pose import get_cv_result
from gap_analysis import compute_gaps
from claude_client import generate_plan, generate_sport_preview

app = FastAPI(title="SNAPBACK API", version="0.2.0")

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
    """
    Called immediately after sport selection (before recording).
    Returns 4 Claude-generated sport-specific exercises.
    """
    if sport not in SPORT_BLUEPRINTS:
        raise HTTPException(status_code=400, detail=f"Unknown sport '{sport}'")

    blueprint = SPORT_BLUEPRINTS[sport]
    exercises = generate_sport_preview(blueprint["name"], blueprint["joints"])
    return {"sport": sport, "sport_name": blueprint["name"], "exercises": exercises}


@app.post("/api/analyze", response_model=AnalysisResponse)
def analyze(request: AnalyzeRequest):
    """
    Full pipeline:
      1. CV result   — from request body (real recording) or demo data
      2. Gap analysis — compare session_rom vs sport blueprint
      3. Plan        — Claude generates 4-week return-to-sport program

    Request body:
      sport      (str)       — sport key from /api/sports
      use_demo   (bool)      — use demo CV data (default: true)
      cv_result  (CVResult)  — real CV server output; overrides demo when provided
    """
    if request.sport not in SPORT_BLUEPRINTS:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown sport '{request.sport}'. Call /api/sports for valid keys.",
        )

    # Step 1 — get CV result (real or demo)
    cv_data = get_cv_result(
        use_demo=request.use_demo,
        provided=request.cv_result.model_dump() if request.cv_result else None,
    )

    # Step 2 — gap analysis
    gaps, body_map, readiness_score = compute_gaps(request.sport, cv_data)

    # Step 3 — Claude plan
    plan = generate_plan(SPORT_BLUEPRINTS[request.sport]["name"], gaps)

    return AnalysisResponse(
        sport=request.sport,
        sport_name=SPORT_BLUEPRINTS[request.sport]["name"],
        overall_score=cv_data.get("overall_score", 0.0),
        gaps=gaps,
        body_map=body_map,
        readiness_score=readiness_score,
        plan=plan,
    )
