"""
Joint angle computation.

compute_angle(a, b, c) — angle at vertex b, using 3D vectors.
extract_angles(pose_result) — pulls all 8 joint angles from a PoseResult.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Optional

import numpy as np

from ..pose.estimator import PoseResult
from ..pose.landmarks import (
    LEFT_SHOULDER,  RIGHT_SHOULDER,
    LEFT_ELBOW,     RIGHT_ELBOW,
    LEFT_WRIST,     RIGHT_WRIST,
    LEFT_HIP,       RIGHT_HIP,
    LEFT_KNEE,      RIGHT_KNEE,
    LEFT_ANKLE,     RIGHT_ANKLE,
)

VISIBILITY_THRESHOLD = 0.5


# ---------------------------------------------------------------------------
# Core math
# ---------------------------------------------------------------------------

def compute_angle(
    a: np.ndarray,
    b: np.ndarray,
    c: np.ndarray,
) -> Optional[float]:
    """
    Return the angle (degrees) at vertex b formed by rays b→a and b→c.
    Works with 2D or 3D arrays.
    Returns None if either ray is degenerate (zero-length).
    """
    vec_ba = a - b
    vec_bc = c - b

    norm_ba = np.linalg.norm(vec_ba)
    norm_bc = np.linalg.norm(vec_bc)

    if norm_ba < 1e-6 or norm_bc < 1e-6:
        return None

    cos_angle = np.dot(vec_ba, vec_bc) / (norm_ba * norm_bc)
    cos_angle = float(np.clip(cos_angle, -1.0, 1.0))   # guard arccos domain
    return math.degrees(math.acos(cos_angle))


# ---------------------------------------------------------------------------
# JointAngles dataclass
# ---------------------------------------------------------------------------

@dataclass
class JointAngles:
    """All 8 measured joint angles for a single frame. None = not visible."""
    left_elbow:      Optional[float]
    right_elbow:     Optional[float]
    left_knee:       Optional[float]
    right_knee:      Optional[float]
    left_hip:        Optional[float]
    right_hip:       Optional[float]
    left_shoulder:   Optional[float]
    right_shoulder:  Optional[float]


# ---------------------------------------------------------------------------
# Angle triplets: (vertex_mp_idx, ray1_mp_idx, ray2_mp_idx)
# ---------------------------------------------------------------------------
_ANGLE_TRIPLETS = {
    "left_elbow":     (LEFT_ELBOW,      LEFT_SHOULDER,  LEFT_WRIST),
    "right_elbow":    (RIGHT_ELBOW,     RIGHT_SHOULDER, RIGHT_WRIST),
    "left_knee":      (LEFT_KNEE,       LEFT_HIP,       LEFT_ANKLE),
    "right_knee":     (RIGHT_KNEE,      RIGHT_HIP,      RIGHT_ANKLE),
    "left_hip":       (LEFT_HIP,        LEFT_SHOULDER,  LEFT_KNEE),
    "right_hip":      (RIGHT_HIP,       RIGHT_SHOULDER, RIGHT_KNEE),
    "left_shoulder":  (LEFT_SHOULDER,   LEFT_ELBOW,     LEFT_HIP),
    "right_shoulder": (RIGHT_SHOULDER,  RIGHT_ELBOW,    RIGHT_HIP),
}


# ---------------------------------------------------------------------------
# Public extractor
# ---------------------------------------------------------------------------

def extract_angles(pose_result: PoseResult) -> JointAngles:
    """
    Compute all joint angles from a PoseResult.
    Any angle whose landmarks are partially occluded returns None.
    """
    results: dict[str, Optional[float]] = {}

    for name, (vertex, ray1, ray2) in _ANGLE_TRIPLETS.items():
        # Skip if any of the three landmarks is not visible enough
        if (
            pose_result.visibility[vertex] < VISIBILITY_THRESHOLD
            or pose_result.visibility[ray1]   < VISIBILITY_THRESHOLD
            or pose_result.visibility[ray2]   < VISIBILITY_THRESHOLD
        ):
            results[name] = None
            continue

        a = pose_result.landmarks[ray1]
        b = pose_result.landmarks[vertex]
        c = pose_result.landmarks[ray2]
        results[name] = compute_angle(a, b, c)

    return JointAngles(**results)
