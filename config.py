"""
config.py
All constants live here. Tune this file without touching logic modules.
"""

# ── MediaPipe landmark indices ────────────────────────────────────────────────
LM = {
    "nose": 0,
    "shoulder_l": 11, "shoulder_r": 12,
    "elbow_l": 13,    "elbow_r": 14,
    "wrist_l": 15,    "wrist_r": 16,
    "hip_l": 23,      "hip_r": 24,
    "knee_l": 25,     "knee_r": 26,
    "ankle_l": 27,    "ankle_r": 28,
    "heel_l": 29,     "heel_r": 30,
    "foot_l": 31,     "foot_r": 32,
}

# ── Joint angle triplets (landmark_A, vertex, landmark_B) ────────────────────
# Angle is computed AT the vertex point.
JOINT_TRIPLETS = {
    "shoulder_l": (LM["elbow_l"],    LM["shoulder_l"], LM["hip_l"]),
    "shoulder_r": (LM["elbow_r"],    LM["shoulder_r"], LM["hip_r"]),
    "elbow_l":    (LM["shoulder_l"], LM["elbow_l"],    LM["wrist_l"]),
    "elbow_r":    (LM["shoulder_r"], LM["elbow_r"],    LM["wrist_r"]),
    "hip_l":      (LM["shoulder_l"], LM["hip_l"],      LM["knee_l"]),
    "hip_r":      (LM["shoulder_r"], LM["hip_r"],      LM["knee_r"]),
    "knee_l":     (LM["hip_l"],      LM["knee_l"],     LM["ankle_l"]),
    "knee_r":     (LM["hip_r"],      LM["knee_r"],     LM["ankle_r"]),
    "ankle_l":    (LM["knee_l"],     LM["ankle_l"],    LM["heel_l"]),
    "ankle_r":    (LM["knee_r"],     LM["ankle_r"],    LM["heel_r"]),
}

# ── Skeleton drawing connections ──────────────────────────────────────────────
SKELETON_CONNECTIONS = [
    # Torso
    (LM["shoulder_l"], LM["shoulder_r"]),
    (LM["hip_l"],      LM["hip_r"]),
    (LM["shoulder_l"], LM["hip_l"]),
    (LM["shoulder_r"], LM["hip_r"]),
    # Left arm
    (LM["shoulder_l"], LM["elbow_l"]),
    (LM["elbow_l"],    LM["wrist_l"]),
    # Right arm
    (LM["shoulder_r"], LM["elbow_r"]),
    (LM["elbow_r"],    LM["wrist_r"]),
    # Left leg
    (LM["hip_l"],      LM["knee_l"]),
    (LM["knee_l"],     LM["ankle_l"]),
    (LM["ankle_l"],    LM["heel_l"]),
    # Right leg
    (LM["hip_r"],      LM["knee_r"]),
    (LM["knee_r"],     LM["ankle_r"]),
    (LM["ankle_r"],    LM["heel_r"]),
]

# ── Clinical normal ROM ranges (degrees) ─────────────────────────────────────
# Source: standard physiotherapy reference ranges.
# These are the MAXIMUM expected range for a healthy adult.
CLINICAL_NORMS = {
    "shoulder_l": 180,
    "shoulder_r": 180,
    "elbow_l":    145,
    "elbow_r":    145,
    "hip_l":      120,
    "hip_r":      120,
    "knee_l":     140,
    "knee_r":     140,
    "ankle_l":     50,   # combined plantar + dorsiflexion range
    "ankle_r":     50,
}

# Human-readable display names
JOINT_DISPLAY_NAMES = {
    "shoulder_l": "Shoulder L",
    "shoulder_r": "Shoulder R",
    "elbow_l":    "Elbow L",
    "elbow_r":    "Elbow R",
    "hip_l":      "Hip L",
    "hip_r":      "Hip R",
    "knee_l":     "Knee L",
    "knee_r":     "Knee R",
    "ankle_l":    "Ankle L",
    "ankle_r":    "Ankle R",
}

# ── Scoring thresholds ────────────────────────────────────────────────────────
# Score = (observed_range / clinical_norm) * 100, capped at 100
SCORE_GOOD      = 70   # >= 70 → green
SCORE_MODERATE  = 40   # 40–69 → amber
                       # < 40  → red

# ── Visibility threshold ─────────────────────────────────────────────────────
# Skip landmarks with confidence below this (0–1)
MIN_VISIBILITY = 0.55

# ── Drawing constants (pixels) ────────────────────────────────────────────────
SKELETON_COLOR   = (180, 230, 180)   # BGR: soft green
JOINT_RADIUS     = 7
SKELETON_THICKNESS = 2

COLOR_GOOD     = (100, 210, 120)   # BGR green
COLOR_MODERATE = (60,  180, 230)   # BGR amber-yellow
COLOR_POOR     = (80,  80,  225)   # BGR red

HUD_ALPHA      = 0.72              # transparency of the HUD panel overlay
HUD_BG_COLOR   = (20, 20, 20)      # BGR near-black

# ── Font path (bundled fallback) ──────────────────────────────────────────────
import os
FONT_PATH = os.path.join(os.path.dirname(__file__), "assets", "RobotoMono-Regular.ttf")
FONT_PATH_FALLBACK = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
