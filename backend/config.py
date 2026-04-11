# All constants: sport blueprints, demo CV result, scoring thresholds
#
# Joint keys match the CV server output (cv/server.py):
#   shoulder, elbow, hip, knee
# Each joint has a required session ROM (degrees) for left, right, and combined.

SPORT_BLUEPRINTS = {
    "tennis": {
        "name": "Tennis",
        "tag": "Upper body dominant",
        "emoji": "🎾",
        "joints": {
            "shoulder": {"label": "Shoulder ROM", "required_combined": 90, "required_left": 90, "required_right": 90},
            "elbow":    {"label": "Elbow ROM",    "required_combined": 95, "required_left": 95, "required_right": 95},
            "hip":      {"label": "Hip ROM",      "required_combined": 75, "required_left": 75, "required_right": 75},
            "knee":     {"label": "Knee ROM",     "required_combined": 55, "required_left": 55, "required_right": 55},
        },
    },
    "soccer": {
        "name": "Soccer",
        "tag": "Full body explosive",
        "emoji": "⚽",
        "joints": {
            "shoulder": {"label": "Shoulder ROM", "required_combined": 55, "required_left": 55, "required_right": 55},
            "elbow":    {"label": "Elbow ROM",    "required_combined": 70, "required_left": 70, "required_right": 70},
            "hip":      {"label": "Hip ROM",      "required_combined": 95, "required_left": 95, "required_right": 95},
            "knee":     {"label": "Knee ROM",     "required_combined": 75, "required_left": 75, "required_right": 75},
        },
    },
    "basketball": {
        "name": "Basketball",
        "tag": "Vertical & lateral power",
        "emoji": "🏀",
        "joints": {
            "shoulder": {"label": "Shoulder ROM", "required_combined": 85, "required_left": 85, "required_right": 85},
            "elbow":    {"label": "Elbow ROM",    "required_combined": 90, "required_left": 90, "required_right": 90},
            "hip":      {"label": "Hip ROM",      "required_combined": 85, "required_left": 85, "required_right": 85},
            "knee":     {"label": "Knee ROM",     "required_combined": 75, "required_left": 75, "required_right": 75},
        },
    },
    "swimming": {
        "name": "Swimming",
        "tag": "Shoulder mobility critical",
        "emoji": "🏊",
        "joints": {
            "shoulder": {"label": "Shoulder ROM", "required_combined": 115, "required_left": 115, "required_right": 115},
            "elbow":    {"label": "Elbow ROM",    "required_combined": 80,  "required_left": 80,  "required_right": 80},
            "hip":      {"label": "Hip ROM",      "required_combined": 75,  "required_left": 75,  "required_right": 75},
            "knee":     {"label": "Knee ROM",     "required_combined": 55,  "required_left": 55,  "required_right": 55},
        },
    },
    "running": {
        "name": "Running",
        "tag": "Lower body endurance",
        "emoji": "🏃",
        "joints": {
            "shoulder": {"label": "Shoulder ROM", "required_combined": 55, "required_left": 55, "required_right": 55},
            "elbow":    {"label": "Elbow ROM",    "required_combined": 75, "required_left": 75, "required_right": 75},
            "hip":      {"label": "Hip ROM",      "required_combined": 90, "required_left": 90, "required_right": 90},
            "knee":     {"label": "Knee ROM",     "required_combined": 65, "required_left": 65, "required_right": 65},
        },
    },
    "crossfit": {
        "name": "CrossFit",
        "tag": "Full body strength & power",
        "emoji": "🏋️",
        "joints": {
            "shoulder": {"label": "Shoulder ROM", "required_combined": 100, "required_left": 100, "required_right": 100},
            "elbow":    {"label": "Elbow ROM",    "required_combined": 105, "required_left": 105, "required_right": 105},
            "hip":      {"label": "Hip ROM",      "required_combined": 95,  "required_left": 95,  "required_right": 95},
            "knee":     {"label": "Knee ROM",     "required_combined": 85,  "required_left": 85,  "required_right": 85},
        },
    },
    "golf": {
        "name": "Golf",
        "tag": "Rotational power",
        "emoji": "⛳",
        "joints": {
            "shoulder": {"label": "Shoulder ROM", "required_combined": 80, "required_left": 80, "required_right": 80},
            "elbow":    {"label": "Elbow ROM",    "required_combined": 85, "required_left": 85, "required_right": 85},
            "hip":      {"label": "Hip ROM",      "required_combined": 90, "required_left": 90, "required_right": 90},
            "knee":     {"label": "Knee ROM",     "required_combined": 55, "required_left": 55, "required_right": 55},
        },
    },
    "volleyball": {
        "name": "Volleyball",
        "tag": "Explosive overhead",
        "emoji": "🏐",
        "joints": {
            "shoulder": {"label": "Shoulder ROM", "required_combined": 95, "required_left": 95, "required_right": 95},
            "elbow":    {"label": "Elbow ROM",    "required_combined": 80, "required_left": 80, "required_right": 80},
            "hip":      {"label": "Hip ROM",      "required_combined": 75, "required_left": 75, "required_right": 75},
            "knee":     {"label": "Knee ROM",     "required_combined": 65, "required_left": 65, "required_right": 65},
        },
    },
    "baseball": {
        "name": "Baseball",
        "tag": "Rotational & throwing",
        "emoji": "⚾",
        "joints": {
            "shoulder": {"label": "Shoulder ROM", "required_combined": 110, "required_left": 110, "required_right": 110},
            "elbow":    {"label": "Elbow ROM",    "required_combined": 95,  "required_left": 95,  "required_right": 95},
            "hip":      {"label": "Hip ROM",      "required_combined": 85,  "required_left": 85,  "required_right": 85},
            "knee":     {"label": "Knee ROM",     "required_combined": 65,  "required_left": 65,  "required_right": 65},
        },
    },
    "boxing": {
        "name": "Boxing",
        "tag": "Full body rotational",
        "emoji": "🥊",
        "joints": {
            "shoulder": {"label": "Shoulder ROM", "required_combined": 80, "required_left": 80, "required_right": 80},
            "elbow":    {"label": "Elbow ROM",    "required_combined": 95, "required_left": 95, "required_right": 95},
            "hip":      {"label": "Hip ROM",      "required_combined": 80, "required_left": 80, "required_right": 80},
            "knee":     {"label": "Knee ROM",     "required_combined": 65, "required_left": 65, "required_right": 65},
        },
    },
}

# Demo CV result — mirrors the exact output shape of cv/server.py
# Used when no real CV recording is provided.
DEMO_CV_RESULT = {
    "overall_score": 47.7,
    "joint_scores": {
        "elbow":    {"left": 51.7, "right": 48.3, "combined": 50.0},
        "knee":     {"left": 22.6, "right": 32.3, "combined": 27.4},
        "hip":      {"left": 68.2, "right": 72.7, "combined": 70.5},
        "shoulder": {"left": 46.4, "right": 39.3, "combined": 42.9},
    },
    "min_angles": {
        "elbow_left": 65, "elbow_right": 65,
        "knee_left": 125, "knee_right": 105,
        "hip_left": 80,   "hip_right": 80,
        "shoulder_left": 15, "shoulder_right": 25,
    },
    "max_angles": {
        "elbow_left": 140, "elbow_right": 135,
        "knee_left": 160,  "knee_right": 155,
        "hip_left": 155,   "hip_right": 160,
        "shoulder_left": 80, "shoulder_right": 80,
    },
    "session_rom": {
        "elbow_left": 75,    "elbow_right": 70,
        "knee_left": 35,     "knee_right": 50,
        "hip_left": 75,      "hip_right": 80,
        "shoulder_left": 65, "shoulder_right": 55,
    },
    "asymmetry_scores": {
        "elbow": 0,
        "knee": 0.0,
        "hip": 5,
        "shoulder": 5,
    },
}

# Scoring thresholds (% of required ROM achieved)
GREEN_THRESHOLD  = 80   # >= 80% → sport ready
YELLOW_THRESHOLD = 60   # 60–79% → needs work
# < 60% → priority focus (red)
