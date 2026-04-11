"""
angles.py
Joint angle computation and Range-of-Motion (ROM) summary.

The angle at a vertex V between arms VA and VB is:
    theta = arccos( dot(VA-V, VB-V) / (|VA-V| * |VB-V|) )
This always returns 0–180°, which is the interior angle at the joint.
"""

import numpy as np
from typing import Optional

from config import JOINT_TRIPLETS, CLINICAL_NORMS, MIN_VISIBILITY, SCORE_GOOD, SCORE_MODERATE


# ── Core math ─────────────────────────────────────────────────────────────────

def compute_angle(a: tuple, vertex: tuple, b: tuple) -> float:
    """
    Returns the angle in degrees at `vertex` in the triangle A-Vertex-B.
    Returns None if any input is degenerate (zero vector).
    """
    a      = np.array(a[:2], dtype=float)
    vertex = np.array(vertex[:2], dtype=float)
    b      = np.array(b[:2], dtype=float)

    v1 = a - vertex
    v2 = b - vertex

    norm1 = np.linalg.norm(v1)
    norm2 = np.linalg.norm(v2)

    if norm1 < 1e-6 or norm2 < 1e-6:
        return None

    cos_theta = np.dot(v1, v2) / (norm1 * norm2)
    cos_theta = np.clip(cos_theta, -1.0, 1.0)   # guard floating-point overshoot
    return float(np.degrees(np.arccos(cos_theta)))


# ── Per-frame angle extraction ─────────────────────────────────────────────────

def compute_frame_angles(frame_data: dict) -> dict:
    """
    Given a single frame's landmark dict, return angles for all joints.
    Skips joints where any landmark has visibility < MIN_VISIBILITY.

    Returns: { joint_name: angle_degrees_or_None }
    """
    landmarks = frame_data["landmarks"]
    angles = {}

    for joint_name, (idx_a, idx_v, idx_b) in JOINT_TRIPLETS.items():
        # Check all three points exist and are visible
        if not all(idx in landmarks for idx in (idx_a, idx_v, idx_b)):
            angles[joint_name] = None
            continue

        vis_a = landmarks[idx_a][2]
        vis_v = landmarks[idx_v][2]
        vis_b = landmarks[idx_b][2]

        if min(vis_a, vis_v, vis_b) < MIN_VISIBILITY:
            angles[joint_name] = None
            continue

        pt_a = landmarks[idx_a][:2]
        pt_v = landmarks[idx_v][:2]
        pt_b = landmarks[idx_b][:2]

        angles[joint_name] = compute_angle(pt_a, pt_v, pt_b)

    return angles


# ── Full video processing ──────────────────────────────────────────────────────

def process_all_frames(frames_data: list) -> list:
    """
    Run angle computation on every frame.
    Returns a list of per-frame angle dicts:
        [ { "frame_idx": N, "angles": { joint: float|None } }, ... ]
    """
    result = []
    for fd in frames_data:
        result.append({
            "frame_idx": fd["frame_idx"],
            "angles": compute_frame_angles(fd),
        })
    return result


# ── ROM summary ────────────────────────────────────────────────────────────────

def compute_rom_summary(frame_angles: list) -> dict:
    """
    Across all frames, find the min/max observed angle and compute ROM (range).
    Only considers frames where the angle is not None.

    Returns:
    {
      "shoulder_l": { "min": 22.4, "max": 164.8, "range": 142.4, "sample_count": 412 },
      ...
    }
    """
    accumulators = {j: [] for j in JOINT_TRIPLETS}

    for frame in frame_angles:
        for joint, angle in frame["angles"].items():
            if angle is not None:
                accumulators[joint].append(angle)

    summary = {}
    for joint, values in accumulators.items():
        if not values:
            summary[joint] = {"min": None, "max": None, "range": 0, "sample_count": 0}
        else:
            mn  = float(np.min(values))
            mx  = float(np.max(values))
            rng = float(mx - mn)
            summary[joint] = {
                "min":          round(mn,  1),
                "max":          round(mx,  1),
                "range":        round(rng, 1),
                "sample_count": len(values),
            }

    return summary


# ── Scoring ───────────────────────────────────────────────────────────────────

def score_joint(joint: str, rom_range: float) -> int:
    """
    Score a joint 0–100 based on observed ROM vs clinical normal.
    Score = (range / clinical_norm) * 100, capped at 100.
    """
    norm = CLINICAL_NORMS.get(joint, 90)
    if norm <= 0 or rom_range is None:
        return 0
    return min(100, int(round(rom_range / norm * 100)))


def score_color(score: int) -> tuple:
    """Return BGR color for a given score."""
    from config import COLOR_GOOD, COLOR_MODERATE, COLOR_POOR
    if score >= SCORE_GOOD:
        return COLOR_GOOD
    elif score >= SCORE_MODERATE:
        return COLOR_MODERATE
    else:
        return COLOR_POOR


def build_scores(rom_summary: dict) -> dict:
    """
    Returns { joint: score_0_to_100 } for all joints.
    """
    return {j: score_joint(j, data["range"]) for j, data in rom_summary.items()}


# ── Running max tracker (used by overlay for live HUD) ────────────────────────

class RomTracker:
    """
    Maintains the running maximum ROM seen so far, per joint.
    Updated frame-by-frame during video rendering.
    """
    def __init__(self):
        self._max = {j: 0.0 for j in JOINT_TRIPLETS}
        self._min = {j: 999.0 for j in JOINT_TRIPLETS}

    def update(self, frame_angle_dict: dict):
        for joint, angle in frame_angle_dict.items():
            if angle is None:
                continue
            if angle > self._max[joint]:
                self._max[joint] = angle
            if angle < self._min[joint]:
                self._min[joint] = angle

    def get_range(self, joint: str) -> float:
        rng = self._max[joint] - self._min[joint]
        return max(0.0, rng)

    def get_score(self, joint: str) -> int:
        return score_joint(joint, self.get_range(joint))
