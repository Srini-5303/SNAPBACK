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
    current_left:     float
    current_right:    float
    required_rom:     float
    gap:              float
    percent_achieved: float
    asymmetry:        float
    status:           JointStatus


class Exercise(BaseModel):
    name:         str
    target_joint: str
    target_label: str
    status:       JointStatus
    sets_reps:    str
    description:  str
    why:          str


class WeekPlan(BaseModel):
    week:      int
    avoid:     List[str]   = []   # things to avoid this week
    exercises: List[Exercise]


class CVResult(BaseModel):
    """Mirrors the exact JSON output shape of cv/server.py"""
    overall_score:    float
    joint_scores:     Dict[str, Dict[str, float]]
    min_angles:       Dict[str, float]
    max_angles:       Dict[str, float]
    session_rom:      Dict[str, float]
    asymmetry_scores: Dict[str, float]
    timestamp:        Optional[str]   = None
    duration_sec:     Optional[float] = None


class UserProfile(BaseModel):
    dominant_hand:    str            # "left" | "right"
    weeks_to_return:  int            # e.g. 4, 8, 12
    weight_kg:        Optional[float] = None  # athlete body weight in kg


class AnalyzeRequest(BaseModel):
    sport:      str
    use_demo:   bool             = True
    skip_plan:  bool             = False   # when True, skip Claude plan generation
    cv_result:  Optional[CVResult]   = None
    user_profile: Optional[UserProfile] = None


class PlanRequest(BaseModel):
    sport:        str
    use_demo:     bool               = True
    cv_result:    Optional[CVResult]     = None
    user_profile: Optional[UserProfile]  = None


class AnalysisResponse(BaseModel):
    sport:           str
    sport_name:      str
    overall_score:   float
    gaps:            List[JointGap]
    body_map:        Dict[str, str]
    readiness_score: float
    plan:            List[WeekPlan]  # empty when skip_plan=True


class PlanResponse(BaseModel):
    sport:      str
    sport_name: str
    plan:       List[WeekPlan]
