"""
AI integration — generates the return-to-sport mobility plan.

Primary  : Claude claude-opus-4-6  (Anthropic)
Hardcoded: _fallback_plan()         — used when Claude fails
"""

import os
import json
import traceback
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

_SYSTEM_PROMPT = """You are a sports physiotherapist generating return-to-sport mobility plans.

RULES
- Exactly 3 exercises per week — no more, no less.
- EVERY week MUST use COMPLETELY DIFFERENT exercises — zero repetition across any week of the plan. If an exercise appeared in any previous week, it is FORBIDDEN in subsequent weeks.
- Difficulty MUST increase every single week: each week's exercises must be measurably harder than the previous week's (more range, more load, more speed, or more sport-specificity).
- Follow this strict progression arc:
    Week 1 → passive/assisted range only, zero load
    Week 2 → active unassisted range, bodyweight or band resistance
    Week 3 → loaded dynamic movement, multi-planar, controlled instability
    Week 4+ → sport-specific drills that replicate exact match/game demands
- Prioritise RED joints, then YELLOW. Adjust for dominant hand when relevant.
- Per week: 2 avoid items (short phrases, no em-dashes).
- Keep description to 1 sentence. Keep why to 1 sentence.

OUTPUT: Return ONLY valid JSON — no markdown, no code fences:

{
  "weeks": [
    {
      "week": 1,
      "avoid": ["Overhead pressing", "Full-speed throwing"],
      "exercises": [
        {
          "name": "Exercise Name",
          "target_joint": "joint_key",
          "target_label": "Joint Name",
          "status": "red",
          "sets_reps": "3x10",
          "description": "One sentence how-to.",
          "why": "One sentence rationale."
        }
      ]
    }
  ]
}

Valid status: "red", "yellow", "green"."""


# ── Fallback exercises per joint (used when API is unavailable) ───────────────

# Keyed by the 4 joints the CV server tracks: shoulder, elbow, hip, knee
_JOINT_FALLBACKS: dict[str, tuple[str, str, str]] = {
    "shoulder": (
        "Side-Lying Shoulder Circle",
        "Lie on your side with knees bent. Draw slow large circles with your top arm, moving through the full pain-free range in both directions.",
        "3 × 10 reps each direction",
    ),
    "elbow": (
        "Active Elbow Flexion–Extension",
        "Stand with arms at your sides. Slowly curl both forearms to full flexion, pause, then extend fully. Focus on end-range hold.",
        "3 × 15 reps",
    ),
    "hip": (
        "90/90 Hip Mobility Drill",
        "Sit on the floor with both knees at 90°. Rotate your torso over the front knee, hold, then switch sides. Keep the spine tall throughout.",
        "3 × 60 seconds each side",
    ),
    "knee": (
        "Heel Slide",
        "Lie on your back on a smooth surface. Slowly slide the heel toward the glutes as far as comfortable. Hold 3 seconds at end range, then slide back.",
        "3 × 15 reps each leg",
    ),
}


def _fallback_plan(sport_name: str, gaps: list[JointGap]) -> list[WeekPlan]:
    """Minimal hardcoded plan used when the API is unavailable or returns an error."""
    priority = [g for g in gaps if g.status == JointStatus.RED][:3]
    moderate = [g for g in gaps if g.status == JointStatus.YELLOW][:2]
    targets  = priority + moderate or gaps[:4]

    _WEEK_AVOID_DEFAULTS = [
        [
            "High-impact or explosive movements — tissue not yet prepared for load",
            "Forcing end-range stretches past the point of discomfort",
            "Full-speed sport-specific activities (throwing, serving, jumping)",
            "Loading through compromised joint positions",
        ],
        [
            "Uncontrolled ballistic movements — keep all motion slow and deliberate",
            "Skipping warm-up — tissue is still adapting and needs preparation",
            "Heavy resistance before demonstrating full pain-free range",
            "Sport-specific drills at game speed",
        ],
        [
            "Pushing through sharp or worsening pain — distinguish muscle fatigue from joint pain",
            "Neglecting the non-dominant side — asymmetry must stay within 10%",
            "Returning to full sport contact without clearance",
            "Skipping recovery days — mobility gains occur during rest",
        ],
        [
            "Returning to full competition before completing the full programme",
            "Abandoning mobility maintenance once sport-specific drills feel comfortable",
            "Ignoring early warning signs of re-injury (swelling, sharp pain, clicking)",
            "Overloading the returning athlete in the first week back at full training",
        ],
    ]

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
                    f"Your {g.label.lower()} combined ROM is {g.current_rom:.0f}°, "
                    f"{g.gap:.0f}° below the {g.required_rom:.0f}° required for {sport_name}. "
                    + (f"A {g.asymmetry:.0f}° left–right asymmetry was also detected. " if g.asymmetry > 5 else "")
                    + "This exercise directly targets that deficit."
                ),
            ))
        weeks.append(WeekPlan(
            week=week_num,
            avoid=_WEEK_AVOID_DEFAULTS[week_num - 1],
            exercises=exercises,
        ))
    return weeks


# ── Public API ────────────────────────────────────────────────────────────────

def generate_plan(sport_name: str, gaps: list[JointGap], user_profile: dict | None = None) -> list[WeekPlan]:
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

    # Build the user message
    weeks_to_return = (user_profile or {}).get("weeks_to_return", 4)
    dominant_hand   = (user_profile or {}).get("dominant_hand", "right")
    weight_kg       = (user_profile or {}).get("weight_kg", None)

    gap_lines = [
        f"  - {g.label} ({g.joint_key}): "
        f"left {g.current_left}° / right {g.current_right}° / combined {g.current_rom}° | "
        f"required {g.required_rom}° | gap {g.gap}° | "
        f"asymmetry {g.asymmetry}° | {g.status.value.upper()}"
        for g in gaps
        if g.status in (JointStatus.RED, JointStatus.YELLOW)
    ]
    if not gap_lines:
        gap_lines = ["  - All joints are at or above 80% of sport requirements — maintenance plan only."]

    weight_line = f"Athlete weight: {weight_kg} kg\n" if weight_kg else ""

    user_content = (
        f"Sport: {sport_name}\n"
        f"Dominant hand: {dominant_hand}\n"
        f"Weeks until return to sport: {weeks_to_return}\n"
        + weight_line
        + f"\nMobility gaps (sorted priority → moderate):\n"
        + "\n".join(gap_lines)
        + f"\n\nGenerate a {weeks_to_return}-week plan. EXACTLY 3 exercises per week, 2 avoid items per week. "
        f"No exercise may appear more than once across all weeks. Difficulty must increase every week. "
        f"Keep all text fields brief (1 sentence each). Output only JSON."
        + (f" Scale load for {weight_kg} kg athlete." if weight_kg else "")
    )

    try:
        # Stream the response — prevents HTTP timeouts on long generations.
        # get_final_message() collects the full response after streaming completes.
        with client.messages.stream(
            model="claude-opus-4-6",
            max_tokens=max(16000, weeks_to_return * 2000),
            thinking={"type": "adaptive"},
            system=[{
                "type": "text",
                "text": _SYSTEM_PROMPT,
                "cache_control": {"type": "ephemeral"},
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
            weeks.append(WeekPlan(
                week=week_data["week"],
                avoid=week_data.get("avoid", []),
                exercises=exercises,
            ))
        return weeks

    except Exception as e:
        print(f"[claude_client] Claude generate_plan FAILED: {type(e).__name__}: {e}")
        traceback.print_exc()
        return _fallback_plan(sport_name, gaps)


# ── Sport Preview ─────────────────────────────────────────────────────────────
# Called immediately after sport selection, before any user video/analysis.
# Returns 4 sport-specific exercises that introduce the athlete to what
# we'll be measuring — shown on the Movement Recording screen.

_SPORT_PREVIEW_SYSTEM = """You are a sports physiotherapist. Given a sport and its key joint mobility requirements, generate exactly 4 essential warm-up exercises an athlete should know before their mobility assessment.

These are sport-specific standard recommendations — not personalised yet (no user data exists at this stage).

Return ONLY valid JSON — no markdown, no code fences:
{
  "exercises": [
    {
      "name": "Exercise Name",
      "target_label": "Target Body Area",
      "sets_reps": "3 × 30 seconds each side",
      "description": "Step-by-step how-to (2–3 sentences)",
      "why": "Why this mobility matters specifically for the athlete's sport (1–2 sentences)"
    }
  ]
}

Return exactly 4 exercises. Cover the most important joint areas for this sport."""


def _fallback_sport_preview(sport_name: str, sport_joints: dict) -> list:
    """Hardcoded sport preview when API is unavailable."""
    top_joints = list(sport_joints.items())[:4]
    result = []
    for joint_key, spec in top_joints:
        fallback = _JOINT_FALLBACKS.get(
            joint_key,
            (
                f"{spec['label']} Mobility Drill",
                f"Perform slow, controlled movement through the full range of {spec['label'].lower()}.",
                "3 × 10 reps",
            ),
        )
        result.append({
            "name": fallback[0],
            "target_label": spec["label"],
            "sets_reps": fallback[2],
            "description": fallback[1],
            "why": f"Essential for {sport_name} — requires {spec['required']}° of {spec['label'].lower()}.",
        })
    return result[:4]


def generate_sport_preview(sport_name: str, sport_joints: dict) -> list:
    """
    Generate 4 key sport-specific exercises shown on the Movement Recording screen.
    No user data — pure sport blueprint based.
    """
    if not os.environ.get("ANTHROPIC_API_KEY"):
        return _fallback_sport_preview(sport_name, sport_joints)

    client = _get_client()

    joint_lines = [
        f"  - {spec['label']}: {spec['required']}° required"
        for _, spec in list(sport_joints.items())[:6]
    ]

    user_content = (
        f"Sport: {sport_name}\n\n"
        f"Key joint ROM requirements:\n"
        + "\n".join(joint_lines)
        + "\n\nGenerate 4 essential sport-specific warm-up exercises."
    )

    try:
        with client.messages.stream(
            model="claude-opus-4-6",
            max_tokens=4000,
            thinking={"type": "adaptive"},
            system=[{
                "type": "text",
                "text": _SPORT_PREVIEW_SYSTEM,
                "cache_control": {"type": "ephemeral"},
            }],
            messages=[{"role": "user", "content": user_content}],
        ) as stream:
            response = stream.get_final_message()

        text = next(
            (block.text for block in response.content if block.type == "text"),
            None,
        )
        if not text:
            return _fallback_sport_preview(sport_name, sport_joints)

        text = text.strip()
        if text.startswith("```"):
            parts = text.split("```", 2)
            text  = parts[1]
            if text.startswith("json"):
                text = text[4:]
            text = text.rsplit("```", 1)[0]

        data = json.loads(text.strip())
        return data["exercises"]

    except Exception:
        return _fallback_sport_preview(sport_name, sport_joints)
