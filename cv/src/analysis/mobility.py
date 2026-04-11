"""
Mobility analysis: session state, asymmetry detection, ROM tracking, scoring.

Scoring is based on observed range-of-motion vs. clinical reference ROM.
Each joint gets its own score; overall score is the average.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .angles import JointAngles

# ---------------------------------------------------------------------------
# Thresholds
# ---------------------------------------------------------------------------
ASYMMETRY_WARNING_DEG  = 15.0
ASYMMETRY_CRITICAL_DEG = 30.0

# Clinical reference full ROM for each joint (degrees).
# These are the angle-at-joint values measured by compute_angle():
#   full extension ≈ 175°, full flexion varies per joint.
# ROM = extension_angle - flexion_angle
REFERENCE_ROM: dict[str, float] = {
    "elbow":    145.0,   # ~175° extended → ~30° flexed
    "knee":     155.0,   # ~175° extended → ~20° flexed
    "hip":      110.0,   # ~170° standing → ~60° flexed
    "shoulder": 140.0,   # ~160° arm at side → ~20° fully raised
}

# How many frames to collect before scoring / flagging kicks in
CALIBRATION_FRAMES = 30

# EMA smoothing factor (0.15 ≈ ~6-frame window)
EMA_ALPHA = 0.15


# ---------------------------------------------------------------------------
# Output dataclasses
# ---------------------------------------------------------------------------

@dataclass
class JointStatus:
    name:   str
    angle:  Optional[float]
    status: str   # "normal" | "caution" | "restricted" | "unknown"


@dataclass
class JointScore:
    """ROM-based score for one joint pair."""
    left:     float   # 0–100, based on left-side ROM
    right:    float   # 0–100, based on right-side ROM
    combined: float   # average of left and right


@dataclass
class MobilityStatus:
    joint_statuses:   list[JointStatus]
    asymmetry_scores: dict[str, float]       # pair → asymmetry °
    session_rom:      dict[str, float]       # joint_side → ROM observed
    min_angles:       dict[str, float]
    max_angles:       dict[str, float]
    cur_angles:       dict[str, float]
    joint_scores:     dict[str, JointScore]  # pair → JointScore
    overall_score:    float                  # 0–100, avg of joint combined scores
    calibrating:      bool


# ---------------------------------------------------------------------------
# Analyzer
# ---------------------------------------------------------------------------

class MobilityAnalyzer:

    def __init__(self) -> None:
        self.reset()

    def reset(self) -> None:
        self._min_angles: dict[str, float] = {}
        self._max_angles: dict[str, float] = {}
        self._ema_angles: dict[str, float] = {}
        self._frame_count: int = 0

    def update(self, angles: JointAngles) -> MobilityStatus:
        self._frame_count += 1
        calibrating = self._frame_count < CALIBRATION_FRAMES

        raw_map = self._angles_as_dict(angles)

        # EMA smoothing + 5° snap
        angle_map: dict[str, Optional[float]] = {}
        for k, v in raw_map.items():
            if v is None:
                angle_map[k] = None
                continue
            if k not in self._ema_angles:
                self._ema_angles[k] = v
            else:
                self._ema_angles[k] = EMA_ALPHA * v + (1 - EMA_ALPHA) * self._ema_angles[k]
            angle_map[k] = round(self._ema_angles[k] / 5) * 5

        self._update_rom(angle_map)

        # ---- Per-joint classification + asymmetry ----
        joint_statuses: list[JointStatus] = []
        asymmetry_scores: dict[str, float] = {}

        for pair_name, (lk, rk) in _JOINT_PAIRS.items():
            lv = angle_map.get(lk)
            rv = angle_map.get(rk)

            l_status = "unknown" if lv is None else "normal"
            r_status = "unknown" if rv is None else "normal"

            asym = 0.0
            if lv is not None and rv is not None:
                asym = abs(lv - rv)
                if not calibrating:
                    if asym >= ASYMMETRY_CRITICAL_DEG:
                        l_status = r_status = "restricted"
                    elif asym >= ASYMMETRY_WARNING_DEG:
                        l_status = r_status = "caution"
            asymmetry_scores[pair_name] = asym

            joint_statuses.append(JointStatus(f"L {pair_name.title()}", lv, l_status))
            joint_statuses.append(JointStatus(f"R {pair_name.title()}", rv, r_status))

        session_rom = {
            k: self._max_angles[k] - self._min_angles[k]
            for k in self._min_angles
        }

        # ---- Per-joint ROM scores ----
        joint_scores = self._compute_joint_scores(session_rom, calibrating)
        overall_score = (
            sum(js.combined for js in joint_scores.values()) / len(joint_scores)
            if joint_scores and not calibrating else 100.0
        )

        return MobilityStatus(
            joint_statuses=joint_statuses,
            asymmetry_scores=asymmetry_scores,
            session_rom=session_rom,
            min_angles=dict(self._min_angles),
            max_angles=dict(self._max_angles),
            cur_angles={k: v for k, v in angle_map.items() if v is not None},
            joint_scores=joint_scores,
            overall_score=overall_score,
            calibrating=calibrating,
        )

    # ------------------------------------------------------------------
    def _update_rom(self, angle_map: dict[str, Optional[float]]) -> None:
        for name, val in angle_map.items():
            if val is None:
                continue
            if name not in self._min_angles:
                self._min_angles[name] = val
                self._max_angles[name] = val
            else:
                self._min_angles[name] = min(self._min_angles[name], val)
                self._max_angles[name] = max(self._max_angles[name], val)

    def _compute_joint_scores(
        self,
        session_rom: dict[str, float],
        calibrating: bool,
    ) -> dict[str, JointScore]:
        scores: dict[str, JointScore] = {}

        for pair_name, ref_rom in REFERENCE_ROM.items():
            lk = f"{pair_name}_left"
            rk = f"{pair_name}_right"

            if calibrating or (lk not in session_rom and rk not in session_rom):
                scores[pair_name] = JointScore(left=100.0, right=100.0, combined=100.0)
                continue

            l_rom  = session_rom.get(lk, 0.0)
            r_rom  = session_rom.get(rk, 0.0)
            l_score = min(100.0, l_rom / ref_rom * 100.0)
            r_score = min(100.0, r_rom / ref_rom * 100.0)
            combined = (l_score + r_score) / 2.0

            scores[pair_name] = JointScore(left=l_score, right=r_score, combined=combined)

        return scores

    @staticmethod
    def _angles_as_dict(angles: JointAngles) -> dict[str, Optional[float]]:
        return {
            "elbow_left":     angles.left_elbow,
            "elbow_right":    angles.right_elbow,
            "knee_left":      angles.left_knee,
            "knee_right":     angles.right_knee,
            "hip_left":       angles.left_hip,
            "hip_right":      angles.right_hip,
            "shoulder_left":  angles.left_shoulder,
            "shoulder_right": angles.right_shoulder,
        }


# ---------------------------------------------------------------------------
_JOINT_PAIRS: dict[str, tuple[str, str]] = {
    "elbow":    ("elbow_left",    "elbow_right"),
    "knee":     ("knee_left",     "knee_right"),
    "hip":      ("hip_left",      "hip_right"),
    "shoulder": ("shoulder_left", "shoulder_right"),
}

_SEVERITY = {"normal": 0, "caution": 1, "restricted": 2, "unknown": -1}

def _escalate(current: str, candidate: str) -> str:
    if _SEVERITY.get(candidate, -1) > _SEVERITY.get(current, -1):
        return candidate
    return current


# ---------------------------------------------------------------------------
# Build joint color map for SkeletonRenderer — now driven by joint scores
# ---------------------------------------------------------------------------
from ..pose.landmarks import STATUS_COLORS, COLOR_GREEN, COLOR_YELLOW, COLOR_RED_J

_DISPLAY_IDX_TO_PAIR: dict[int, str] = {
    1: "shoulder", 2: "shoulder",
    3: "elbow",    4: "elbow",
    7: "hip",      8: "hip",
    9: "knee",     10: "knee",
}

_DISPLAY_IDX_SIDE: dict[int, str] = {
    1: "left",  2: "right",
    3: "left",  4: "right",
    7: "left",  8: "right",
    9: "left",  10: "right",
}


def _score_to_color(score: float) -> tuple:
    if score >= 80: return COLOR_GREEN
    if score >= 50: return COLOR_YELLOW
    return COLOR_RED_J


def build_joint_colors(status: MobilityStatus) -> dict[int, tuple]:
    colors: dict[int, tuple] = {}
    for disp_idx, pair_name in _DISPLAY_IDX_TO_PAIR.items():
        side = _DISPLAY_IDX_SIDE[disp_idx]
        js = status.joint_scores.get(pair_name)
        if js is None:
            colors[disp_idx] = COLOR_GREEN
        else:
            side_score = js.left if side == "left" else js.right
            colors[disp_idx] = _score_to_color(side_score)
    return colors
