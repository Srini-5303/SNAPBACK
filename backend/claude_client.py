"""
Claude API integration — generates the 4-week return-to-sport mobility plan.

Model  : claude-opus-4-6
Caching: system prompt is cached (stable across all requests)
Thinking: adaptive (model decides depth per request)
Streaming: yes — uses get_final_message() to avoid HTTP timeouts
"""

import os
import json
import anthropic
from models import JointGap, Exercise, WeekPlan, JointStatus

_client: anthropic.Anthropic | None = None


def _get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        _client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
    return _client


# ── System prompt (cached) ────────────────────────────────────────────────────
# This is stable across all sports and users — perfect for prompt caching.
# Cache hit saves ~90% on this portion of input tokens.

_SYSTEM_PROMPT = """You are a board-certified sports physiotherapist specializing in return-to-sport mobility programs.

TASK
Given an athlete's mobility gaps — joints where measured ROM falls below what their sport demands — produce a 4-week progressive return-to-sport exercise plan.

PLAN RULES
- 4–5 exercises per week
- Weeks 1–2: therapeutic and foundational movements (restore range, reduce restriction)
- Weeks 3–4: sport-specific progressions (load and move through newly acquired range)
- Prioritize RED (critical) joints first, then YELLOW (moderate) joints
- Each exercise must specify sets, reps, or hold time
- The "why" field must name the sport and explain the exact movement demand being addressed

OUTPUT FORMAT
Return ONLY valid JSON — no markdown, no code fences, no commentary. Match this structure exactly:

{
  "weeks": [
    {
      "week": 1,
      "exercises": [
        {
          "name": "Exercise Name",
          "target_joint": "joint_key_from_input",
          "target_label": "Human Readable Joint Name",
          "status": "red",
          "sets_reps": "3 × 30 seconds each side",
          "description": "Step-by-step instructions for performing the exercise",
          "why": "Explains why this exercise addresses the sport-specific demand"
        }
      ]
    },
    { "week": 2, "exercises": [...] },
    { "week": 3, "exercises": [...] },
    { "week": 4, "exercises": [...] }
  ]
}

Valid values for "status": "red", "yellow", "green"."""


# ── Fallback exercises per joint (used when API is unavailable) ───────────────

_JOINT_FALLBACKS: dict[str, tuple[str, str, str]] = {
    "hip_flexion":           ("90/90 Hip Flexor Stretch",        "Kneel in a lunge. Tuck pelvis and drive hips forward until a stretch is felt in the front hip.",                              "3 × 60 seconds each side"),
    "hip_extension":         ("Couch Stretch",                   "Kneel with rear foot against a wall. Drive hips forward while keeping torso upright.",                                        "3 × 60 seconds each side"),
    "hip_internal_rotation": ("Seated Hip IR Drill",             "Sit with feet wider than hips. Let both knees drop inward simultaneously, hold at end range.",                               "3 × 30 seconds"),
    "hip_external_rotation": ("Pigeon Pose Hold",                "From plank, bring one shin forward perpendicular to your body. Lower hips toward the floor and hold.",                       "3 × 60 seconds each side"),
    "knee_flexion":          ("Heel Slide",                      "Lie on your back. Slowly slide the heel toward the glutes as far as comfortable. Hold 3 seconds at end range.",              "3 × 15 reps"),
    "ankle_dorsiflexion":    ("Wall Ankle Mobilisation",         "Stand facing a wall. Place front foot 5 cm from the wall. Drive knee toward and past the wall without lifting the heel.",    "3 × 15 reps each side"),
    "ankle_plantarflexion":  ("Seated Calf Raise with Stretch",  "Sit on the edge of a chair. Raise heels to full plantarflexion, pause, then lower slowly.",                                  "3 × 15 reps"),
    "shoulder_flexion":      ("Wall Walk",                       "Stand facing a wall. Walk fingers up the wall reaching as high as possible while keeping the shoulder blade down.",          "3 × 10 reps"),
    "shoulder_extension":    ("Doorway Shoulder Extension",      "Stand in a doorway. Grip the frame at hip height and lean forward, feeling a stretch across the front shoulder.",           "3 × 30 seconds each side"),
    "shoulder_external_rotation": ("Side-Lying External Rotation", "Lie on side, elbow at 90°. Slowly rotate forearm up toward the ceiling. Lower with control.",                            "3 × 15 reps"),
    "shoulder_internal_rotation": ("Sleeper Stretch",            "Lie on your side. Use your top arm to gently press the bottom forearm toward the floor.",                                   "3 × 30 seconds each side"),
    "thoracic_rotation":     ("Seated Thoracic Rotation",        "Sit cross-legged, hands behind head. Rotate torso fully to each side, keeping hips still.",                                 "3 × 10 reps each side"),
    "thoracic_extension":    ("Foam Roller Thoracic Extension",  "Place a foam roller perpendicular to the spine at mid-back. Extend over it, moving segment by segment.",                   "3 × 8 reps"),
    "wrist_extension":       ("Wrist Extension Stretch",         "Arm straight in front, palm down. Use the other hand to gently pull fingers back toward the forearm.",                     "3 × 30 seconds each side"),
}


def _fallback_plan(sport_name: str, gaps: list[JointGap]) -> list[WeekPlan]:
    """Minimal hardcoded plan used when the API is unavailable or returns an error."""
    priority = [g for g in gaps if g.status == JointStatus.RED][:3]
    moderate = [g for g in gaps if g.status == JointStatus.YELLOW][:2]
    targets  = priority + moderate or gaps[:4]

    weeks: list[WeekPlan] = []
    for week_num in range(1, 5):
        exercises: list[Exercise] = []
        for g in targets[:5]:
            fallback = _JOINT_FALLBACKS.get(
                g.joint_key,
                (
                    f"{g.label} Mobility Drill",
                    f"Perform slow, controlled movement through the full available range of {g.label.lower()}.",
                    "3 × 10 reps",
                ),
            )
            exercises.append(Exercise(
                name=fallback[0],
                target_joint=g.joint_key,
                target_label=g.label,
                status=g.status,
                sets_reps=fallback[2],
                description=fallback[1],
                why=(
                    f"Your {g.label.lower()} is {g.gap:.0f}° below what {sport_name} requires. "
                    f"This exercise directly targets that deficit."
                ),
            ))
        weeks.append(WeekPlan(week=week_num, exercises=exercises))
    return weeks


# ── Public API ────────────────────────────────────────────────────────────────

def generate_plan(sport_name: str, gaps: list[JointGap]) -> list[WeekPlan]:
    """
    Call Claude to generate a personalised 4-week return-to-sport plan.

    Falls back to _fallback_plan() if:
      - ANTHROPIC_API_KEY is not set
      - The API call fails for any reason
      - Claude returns malformed JSON
    """
    if not os.environ.get("ANTHROPIC_API_KEY"):
        return _fallback_plan(sport_name, gaps)

    client = _get_client()

    # Build the user message — only includes the volatile, per-request data.
    # The heavy system prompt above is cached and reused across calls.
    gap_lines = [
        f"  - {g.label} ({g.joint_key}): "
        f"current {g.current_rom}° | required {g.required_rom}° | "
        f"gap {g.gap}° | {g.status.value.upper()}"
        for g in gaps
        if g.status in (JointStatus.RED, JointStatus.YELLOW)
    ]
    if not gap_lines:
        gap_lines = ["  - All joints are at or above 80% of sport requirements — maintenance plan only."]

    user_content = (
        f"Sport: {sport_name}\n\n"
        f"Mobility gaps (sorted priority → moderate):\n"
        + "\n".join(gap_lines)
        + "\n\nGenerate the 4-week plan as JSON."
    )

    try:
        # Stream the response — prevents HTTP timeouts on long generations.
        # get_final_message() collects the full response after streaming completes.
        with client.messages.stream(
            model="claude-opus-4-6",
            max_tokens=4096,
            thinking={"type": "adaptive"},          # let the model decide reasoning depth
            system=[{
                "type": "text",
                "text": _SYSTEM_PROMPT,
                "cache_control": {"type": "ephemeral"},  # cache the stable system prompt
            }],
            messages=[{"role": "user", "content": user_content}],
        ) as stream:
            response = stream.get_final_message()

        # Extract only the text block (skip thinking blocks)
        text = next(
            (block.text for block in response.content if block.type == "text"),
            None,
        )
        if not text:
            return _fallback_plan(sport_name, gaps)

        # Strip markdown fences if Claude wrapped the JSON anyway
        text = text.strip()
        if text.startswith("```"):
            parts = text.split("```", 2)
            text  = parts[1]
            if text.startswith("json"):
                text = text[4:]
            text = text.rsplit("```", 1)[0]

        data = json.loads(text.strip())

        weeks: list[WeekPlan] = []
        for week_data in data["weeks"]:
            exercises: list[Exercise] = []
            for ex in week_data["exercises"]:
                raw_status = ex.get("status", "yellow").lower()
                if raw_status not in ("red", "yellow", "green"):
                    raw_status = "yellow"
                exercises.append(Exercise(
                    name=ex["name"],
                    target_joint=ex["target_joint"],
                    target_label=ex["target_label"],
                    status=JointStatus(raw_status),
                    sets_reps=ex["sets_reps"],
                    description=ex["description"],
                    why=ex["why"],
                ))
            weeks.append(WeekPlan(week=week_data["week"], exercises=exercises))
        return weeks

    except Exception:
        # Any failure — JSON parse error, API error, network issue — use fallback
        return _fallback_plan(sport_name, gaps)
