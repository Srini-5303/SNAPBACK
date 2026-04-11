from pydantic import BaseModel
from typing import Optional, Dict, List
from enum import Enum


class JointStatus(str, Enum):
    GREEN  = "green"
    YELLOW = "yellow"
    RED    = "red"


class JointGap(BaseModel):
    joint_key:        str
    label:            str
    current_rom:      float
    required_rom:     float
    gap:              float          # degrees short of requirement (0 if already met)
    percent_achieved: float          # current / required * 100, capped at 100
    status:           JointStatus


class Exercise(BaseModel):
    name:         str
    target_joint: str                # matches a joint_key
    target_label: str
    status:       JointStatus        # severity of the gap this exercise targets
    sets_reps:    str                # e.g. "3 × 30 seconds each side"
    description:  str
    why:          str                # sport-specific rationale


class WeekPlan(BaseModel):
    week:      int
    exercises: List[Exercise]


class AnalyzeRequest(BaseModel):
    sport:         str
    use_demo:      bool = True
    user_mobility: Optional[Dict[str, float]] = None  # overrides demo data when provided


class AnalysisResponse(BaseModel):
    sport:           str
    sport_name:      str
    user_mobility:   Dict[str, float]
    gaps:            List[JointGap]   # sorted worst → best
    body_map:        Dict[str, str]   # joint_key → "green" | "yellow" | "red"
    readiness_score: float            # 0–100 overall
    plan:            List[WeekPlan]
