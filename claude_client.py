"""
claude_client.py
Sends the ROM summary JSON to Claude and receives:
  - Per-joint mobility scores (0–100)
  - An overall mobility score
  - 3–5 exercise recommendations per restricted joint, tiered by score

One API call. Expects structured JSON back (no preamble).
"""

import json
import re
import anthropic

from config import CLINICAL_NORMS, JOINT_DISPLAY_NAMES, SCORE_GOOD, SCORE_MODERATE
from dotenv import load_dotenv
load_dotenv()

SYSTEM_PROMPT = """
You are an expert sports physiotherapist and movement analyst.
You receive joint range-of-motion (ROM) data extracted from video analysis
and must return a structured mobility assessment.

Clinical reference ranges (maximum healthy ROM in degrees):
- Shoulder: 180° (full flexion arc)
- Elbow: 145°
- Hip: 120°
- Knee: 140°
- Ankle: 50° (combined plantar + dorsiflexion)

Scoring guide:
- Score = (observed_range / clinical_norm) × 100, capped at 100
- 0–39: Restricted — recommend beginner/therapeutic mobility work
- 40–69: Moderate — recommend intermediate mobility exercises
- 70–100: Good — recommend maintenance and advanced exercises

For each joint with a score below 70, provide 3 targeted exercises.
For joints with score >= 70, provide 1 maintenance exercise.

IMPORTANT: Respond ONLY with valid JSON. No preamble, no markdown, no explanation.
The JSON schema must be exactly:
{
  "overall_score": <integer 0-100>,
  "overall_summary": "<2 sentence summary of the person's mobility>",
  "joints": {
    "<joint_name>": {
      "score": <integer 0-100>,
      "assessment": "<one sentence>",
      "exercises": [
        {
          "name": "<exercise name>",
          "description": "<how to perform it, 1-2 sentences>",
          "sets_reps": "<e.g. 3 sets × 10 reps or 30 sec hold>",
          "tier": "<beginner|intermediate|advanced>"
        }
      ]
    }
  }
}
""".strip()


def build_user_message(rom_summary: dict, scores: dict, sport_context: str = "") -> str:
    """
    Build the user message from ROM data.
    sport_context is optional — e.g. "squat", "overhead press", "running gait".
    """
    lines = ["Joint ROM data extracted from video analysis:\n"]

    for joint, data in rom_summary.items():
        display = JOINT_DISPLAY_NAMES.get(joint, joint)
        norm    = CLINICAL_NORMS.get(joint, 90)
        rng     = data.get("range", 0)
        score   = scores.get(joint, 0)
        samples = data.get("sample_count", 0)

        if data["min"] is None:
            lines.append(f"  {display}: NO DATA (joint not visible in video)")
        else:
            lines.append(
                f"  {display}: min={data['min']}°  max={data['max']}°  "
                f"range={rng}°  (norm={norm}°)  score={score}/100  "
                f"[{samples} frames]"
            )

    if sport_context:
        lines.append(f"\nMovement context: {sport_context}")

    lines.append("\nProvide the mobility assessment JSON as specified.")
    return "\n".join(lines)


def call_claude(rom_summary: dict, scores: dict, sport_context: str = "") -> dict:
    """
    Call the Claude API and return the parsed assessment dict.
    Falls back gracefully if JSON parsing fails.
    """
    client = anthropic.Anthropic()

    user_msg = build_user_message(rom_summary, scores, sport_context)

    print("[claude] Sending ROM data to Claude API...")

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_msg}],
    )

    raw = message.content[0].text.strip()

    # Parse JSON — strip any accidental markdown fences
    clean = re.sub(r"^```(?:json)?\s*", "", raw, flags=re.MULTILINE)
    clean = re.sub(r"\s*```$", "", clean, flags=re.MULTILINE)
    clean = clean.strip()

    try:
        result = json.loads(clean)
        print(f"[claude] Assessment received. Overall score: {result.get('overall_score', '?')}/100")
        return result
    except json.JSONDecodeError as e:
        print(f"[claude] WARNING: JSON parse failed ({e}). Returning raw text.")
        return {
            "overall_score": 0,
            "overall_summary": raw,
            "joints": {},
            "_parse_error": True,
        }
