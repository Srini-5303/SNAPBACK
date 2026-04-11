from pydantic import BaseModel
from typing import Optional, Dict, List
from enum import Enum


class JointStatus(str, Enum):
    GREEN  = "green"
    YELLOW = "yellow"
    RED    = "red"


class JointGap(BaseModel):
    joint_key:        str            # e.g. "shoulder", "knee"
    label:            str            # e.g. "Shoulder ROM"
    current_rom:      float          # measured combined ROM in degrees
    current_left:     float          # left side ROM
    current_right:    float          # right side ROM
    required_rom:     float          # required combined ROM for this sport
    gap:              float          # degrees short of requirement (0 if already met)
    percent_achieved: float          # current / required * 100, capped at 100
    asymmetry:        float          # asymmetry score from CV (0 = symmetric)
    status:           JointStatus


class Exercise(BaseModel):
    name:         str
    target_joint: str                # matches a joint_key (shoulder/elbow/hip/knee)
    target_label: str
    status:       JointStatus
    sets_reps:    str                # e.g. "3 × 30 seconds each side"
    description:  str
    why:          str                # sport-specific rationale


class WeekPlan(BaseModel):
    week:      int
    exercises: List[Exercise]


class CVResult(BaseModel):
    """Mirrors the exact JSON output shape of cv/server.py"""
    overall_score:    float
    joint_scores:     Dict[str, Dict[str, float]]  # joint → {left, right, combined}
    min_angles:       Dict[str, float]             # e.g. elbow_left, knee_right
    max_angles:       Dict[str, float]
    session_rom:      Dict[str, float]             # e.g. shoulder_left, hip_right
    asymmetry_scores: Dict[str, float]             # joint → score
    timestamp:        Optional[str] = None
    duration_sec:     Optional[float] = None


class AnalyzeRequest(BaseModel):
    sport:      str
    use_demo:   bool = True
    cv_result:  Optional[CVResult] = None   # real CV output; overrides demo when provided


class AnalysisResponse(BaseModel):
    sport:           str
    sport_name:      str
    overall_score:   float           # raw overall score from CV (or demo)
    gaps:            List[JointGap]  # sorted worst → best
    body_map:        Dict[str, str]  # joint_key → "green" | "yellow" | "red"
    readiness_score: float           # 0–100 computed from gap analysis
    plan:            List[WeekPlan]
