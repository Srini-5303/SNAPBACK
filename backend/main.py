"""
SNAPBACK / ReMotion — Backend API

Endpoints:
  GET  /api/sports          → list all available sports
  POST /api/analyze         → run full pipeline and return analysis + plan

Run:
  uvicorn main:app --reload --port 8000
"""

import anthropic
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from config import SPORT_BLUEPRINTS
from models import AnalyzeRequest, AnalysisResponse
from pose import get_joint_angles
from gap_analysis import compute_gaps
from claude_client import generate_plan

app = FastAPI(title="SNAPBACK API", version="0.1.0")

# Allow all origins during development — tighten this before production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Health check ──────────────────────────────────────────────────────────────

@app.get("/health")
def health():
    return {"status": "ok"}


# ── Sports catalogue ──────────────────────────────────────────────────────────

@app.get("/api/sports")
def list_sports():
    """Return metadata for all supported sports."""
    return [
        {
            "key":   key,
            "name":  bp["name"],
            "tag":   bp["tag"],
            "emoji": bp["emoji"],
        }
        for key, bp in SPORT_BLUEPRINTS.items()
    ]


# ── Main analysis pipeline ────────────────────────────────────────────────────

@app.post("/api/analyze", response_model=AnalysisResponse)
def analyze(request: AnalyzeRequest):
    """
    Full ReMotion pipeline:

    1. Pose analysis   → get joint angles (hardcoded demo until MediaPipe lands)
    2. Gap analysis    → compare angles to sport blueprint, assign green/yellow/red
    3. Plan generation → call Claude API for a 4-week return-to-sport program

    Request body:
      sport          (str)  — sport key from /api/sports
      use_demo       (bool) — use hardcoded demo mobility data (default: true)
      user_mobility  (dict) — optional override: joint_key → ROM in degrees
    """
    if request.sport not in SPORT_BLUEPRINTS:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown sport '{request.sport}'. Call /api/sports for valid keys.",
        )

    # Step 1 — Pose analysis (stubbed)
    user_mobility = get_joint_angles(
        use_demo=request.use_demo,
        provided=request.user_mobility,
    )

    # Step 2 — Gap analysis (programmatic)
    gaps, body_map, readiness_score = compute_gaps(request.sport, user_mobility)

    # Step 3 — Plan generation (Claude API)
    plan = generate_plan(SPORT_BLUEPRINTS[request.sport]["name"], gaps)

    return AnalysisResponse(
        sport=request.sport,
        sport_name=SPORT_BLUEPRINTS[request.sport]["name"],
        user_mobility=user_mobility,
        gaps=gaps,
        body_map=body_map,
        readiness_score=readiness_score,
        plan=plan,
    )
