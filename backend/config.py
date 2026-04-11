# All constants: sport blueprints, demo CV result, scoring thresholds
#
# Joint keys match the CV server output (cv/server.py):
#   shoulder, elbow, hip, knee
# Each joint has a required session ROM (degrees) for left, right, and combined.
#
# Clinical reference ROMs from Range of Joint Motion Evaluation Chart (PDF):
#   Shoulder flexion: 150°  |  Elbow flexion: 150°
#   Hip flexion: 100°       |  Knee flexion: 150°
#
# CV module reference ROMs (100% score threshold in cv/src/analysis/mobility.py):
#   shoulder: 140°  |  elbow: 145°  |  hip: 110°  |  knee: 155°
#
# Sport required values = sport-demand % × CV reference ROM
# (higher % = sport demands greater share of full clinical range)

SPORT_BLUEPRINTS = {
    "tennis": {
        # Shoulder: 90% (serving requires near-full overhead elevation)
        # Elbow:    80% (groundstroke extension/flexion arc)
        # Hip:      75% (lateral splits, serve rotation)
        # Knee:     75% (split-step absorption, court coverage)
        "name": "Tennis",
        "tag": "Upper body dominant",
        "emoji": "🎾",
        "joints": {
            "shoulder": {"label": "Shoulder ROM", "required_combined": 125, "required_left": 125, "required_right": 125},
            "elbow":    {"label": "Elbow ROM",    "required_combined": 115, "required_left": 115, "required_right": 115},
            "hip":      {"label": "Hip ROM",      "required_combined": 82,  "required_left": 82,  "required_right": 82},
            "knee":     {"label": "Knee ROM",     "required_combined": 115, "required_left": 115, "required_right": 115},
        },
    },
    "basketball": {
        # Shoulder: 80% (shooting, rebounding reach)
        # Elbow:    75% (shooting arc, dribbling)
        # Hip:      80% (jump mechanics, defensive stance)
        # Knee:     80% (deep knee bend in jumps/landing)
        "name": "Basketball",
        "tag": "Vertical & lateral power",
        "emoji": "🏀",
        "joints": {
            "shoulder": {"label": "Shoulder ROM", "required_combined": 112, "required_left": 112, "required_right": 112},
            "elbow":    {"label": "Elbow ROM",    "required_combined": 109, "required_left": 109, "required_right": 109},
            "hip":      {"label": "Hip ROM",      "required_combined": 88,  "required_left": 88,  "required_right": 88},
            "knee":     {"label": "Knee ROM",     "required_combined": 124, "required_left": 124, "required_right": 124},
        },
    },
    "swimming": {
        # Shoulder: 95% (freestyle/butterfly demand near-full overhead arc)
        # Elbow:    70% (pull-through; arm relatively straight in freestyle)
        # Hip:      70% (flutter kick amplitude)
        # Knee:     65% (breaststroke kick, limited knee range needed)
        "name": "Swimming",
        "tag": "Shoulder mobility critical",
        "emoji": "🏊",
        "joints": {
            "shoulder": {"label": "Shoulder ROM", "required_combined": 133, "required_left": 133, "required_right": 133},
            "elbow":    {"label": "Elbow ROM",    "required_combined": 101, "required_left": 101, "required_right": 101},
            "hip":      {"label": "Hip ROM",      "required_combined": 77,  "required_left": 77,  "required_right": 77},
            "knee":     {"label": "Knee ROM",     "required_combined": 101, "required_left": 101, "required_right": 101},
        },
    },
    "crossfit": {
        # Shoulder: 95% (overhead squat, snatch demand maximum elevation)
        # Elbow:    90% (full pressing & pulling range)
        # Hip:      90% (deep squat below parallel)
        # Knee:     88% (full depth squat mechanics)
        "name": "CrossFit",
        "tag": "Full body strength & power",
        "emoji": "🏋️",
        "joints": {
            "shoulder": {"label": "Shoulder ROM", "required_combined": 133, "required_left": 133, "required_right": 133},
            "elbow":    {"label": "Elbow ROM",    "required_combined": 130, "required_left": 130, "required_right": 130},
            "hip":      {"label": "Hip ROM",      "required_combined": 99,  "required_left": 99,  "required_right": 99},
            "knee":     {"label": "Knee ROM",     "required_combined": 136, "required_left": 136, "required_right": 136},
        },
    },
    "golf": {
        # Shoulder: 85% (backswing elevation, follow-through)
        # Elbow:    80% (lead arm extension in backswing)
        # Hip:      85% (hip turn generates rotational power)
        # Knee:     65% (subtle knee flex in address/pivot)
        "name": "Golf",
        "tag": "Rotational power",
        "emoji": "⛳",
        "joints": {
            "shoulder": {"label": "Shoulder ROM", "required_combined": 119, "required_left": 119, "required_right": 119},
            "elbow":    {"label": "Elbow ROM",    "required_combined": 116, "required_left": 116, "required_right": 116},
            "hip":      {"label": "Hip ROM",      "required_combined": 93,  "required_left": 93,  "required_right": 93},
            "knee":     {"label": "Knee ROM",     "required_combined": 101, "required_left": 101, "required_right": 101},
        },
    },
    "volleyball": {
        # Shoulder: 95% (spike/serve require maximum overhead mobility)
        # Elbow:    80% (arm swing mechanics, blocking)
        # Hip:      80% (jump approach, landing depth)
        # Knee:     80% (approach jump, landing absorption)
        "name": "Volleyball",
        "tag": "Explosive overhead",
        "emoji": "🏐",
        "joints": {
            "shoulder": {"label": "Shoulder ROM", "required_combined": 133, "required_left": 133, "required_right": 133},
            "elbow":    {"label": "Elbow ROM",    "required_combined": 116, "required_left": 116, "required_right": 116},
            "hip":      {"label": "Hip ROM",      "required_combined": 88,  "required_left": 88,  "required_right": 88},
            "knee":     {"label": "Knee ROM",     "required_combined": 124, "required_left": 124, "required_right": 124},
        },
    },
    "baseball": {
        # Shoulder: 95% (overhead throw demands maximum shoulder mobility)
        # Elbow:    90% (deceleration phase, UCL load at full flexion)
        # Hip:      85% (hip-shoulder separation drives rotational power)
        # Knee:     70% (fielding crouch, running base paths)
        "name": "Baseball",
        "tag": "Rotational & throwing",
        "emoji": "⚾",
        "joints": {
            "shoulder": {"label": "Shoulder ROM", "required_combined": 133, "required_left": 133, "required_right": 133},
            "elbow":    {"label": "Elbow ROM",    "required_combined": 130, "required_left": 130, "required_right": 130},
            "hip":      {"label": "Hip ROM",      "required_combined": 93,  "required_left": 93,  "required_right": 93},
            "knee":     {"label": "Knee ROM",     "required_combined": 109, "required_left": 109, "required_right": 109},
        },
    },
    "boxing": {
        # Shoulder: 85% (jab extension, uppercut follow-through)
        # Elbow:    90% (full extension on cross/jab, guard flexion)
        # Hip:      80% (hip rotation drives punch power)
        # Knee:     70% (stance flex, slip & roll movements)
        "name": "Boxing",
        "tag": "Full body rotational",
        "emoji": "🥊",
        "joints": {
            "shoulder": {"label": "Shoulder ROM", "required_combined": 119, "required_left": 119, "required_right": 119},
            "elbow":    {"label": "Elbow ROM",    "required_combined": 130, "required_left": 130, "required_right": 130},
            "hip":      {"label": "Hip ROM",      "required_combined": 88,  "required_left": 88,  "required_right": 88},
            "knee":     {"label": "Knee ROM",     "required_combined": 109, "required_left": 109, "required_right": 109},
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
