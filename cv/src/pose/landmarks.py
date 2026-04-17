"""
Landmark constants, display joint mapping, skeleton edge definitions, and draw colors.
Single source of truth — no logic, no imports from other project modules.
"""

# ---------------------------------------------------------------------------
# MediaPipe pose landmark indices
# ---------------------------------------------------------------------------
NOSE = 0
LEFT_SHOULDER  = 11;  RIGHT_SHOULDER  = 12
LEFT_ELBOW     = 13;  RIGHT_ELBOW     = 14
LEFT_WRIST     = 15;  RIGHT_WRIST     = 16
LEFT_HIP       = 23;  RIGHT_HIP       = 24
LEFT_KNEE      = 25;  RIGHT_KNEE      = 26
LEFT_ANKLE     = 27;  RIGHT_ANKLE     = 28

# ---------------------------------------------------------------------------
# Display joint numbering (0-12)
# Maps display joint index → MediaPipe landmark index
# ---------------------------------------------------------------------------
DISPLAY_TO_MP: dict[int, int] = {
    0:  NOSE,
    1:  LEFT_SHOULDER,
    2:  RIGHT_SHOULDER,
    3:  LEFT_ELBOW,
    4:  RIGHT_ELBOW,
    5:  LEFT_WRIST,
    6:  RIGHT_WRIST,
    7:  LEFT_HIP,
    8:  RIGHT_HIP,
    9:  LEFT_KNEE,
    10: RIGHT_KNEE,
    11: LEFT_ANKLE,
    12: RIGHT_ANKLE,
}

# Synthetic joint keys (midpoints, not in DISPLAY_TO_MP)
MID_SHOULDER_KEY = "mid_shoulder"
MID_HIP_KEY      = "mid_hip"

# ---------------------------------------------------------------------------
# Skeleton edge list: (from_joint, to_joint, side)
# from/to may be display joint int OR a synthetic key string
# side: "left" | "right" | "center"
# ---------------------------------------------------------------------------
SKELETON_EDGES: list[tuple] = [
    # Spine / center
    (0,               MID_SHOULDER_KEY, "center"),  # head → neck
    (MID_SHOULDER_KEY, MID_HIP_KEY,    "center"),   # spine
    (1, 2,                             "center"),   # shoulder bar
    (7, 8,                             "center"),   # hip bar

    # Right arm & leg (displayed in blue)
    (2, 4,  "right"),   # R shoulder → R elbow
    (4, 6,  "right"),   # R elbow    → R wrist
    (2, 8,  "right"),   # R shoulder → R hip
    (8, 10, "right"),   # R hip      → R knee
    (10,12, "right"),   # R knee     → R ankle

    # Left arm & leg (displayed in red)
    (1, 3,  "left"),    # L shoulder → L elbow
    (3, 5,  "left"),    # L elbow    → L wrist
    (1, 7,  "left"),    # L shoulder → L hip
    (7, 9,  "left"),    # L hip      → L knee
    (9, 11, "left"),    # L knee     → L ankle
]

# ---------------------------------------------------------------------------
# BGR draw colors
# ---------------------------------------------------------------------------
COLOR_RIGHT  = (255,   0,   0)   # blue  — right side limbs
COLOR_LEFT   = (  0,   0, 255)   # red   — left side limbs
COLOR_CENTER = ( 50,  50,  50)   # dark grey — spine / horizontal bars
COLOR_GREEN  = (  0, 220,   0)   # healthy joint
COLOR_YELLOW = (  0, 200, 220)   # caution joint
COLOR_RED_J  = (  0,   0, 220)   # restricted joint (avoid naming conflict)
COLOR_WHITE  = (255, 255, 255)
COLOR_BLACK  = (  0,   0,   0)

SIDE_COLORS: dict[str, tuple] = {
    "right":  COLOR_RIGHT,
    "left":   COLOR_LEFT,
    "center": COLOR_CENTER,
}

# Map status string → joint circle color
STATUS_COLORS: dict[str, tuple] = {
    "normal":     COLOR_GREEN,
    "caution":    COLOR_YELLOW,
    "restricted": COLOR_RED_J,
}
