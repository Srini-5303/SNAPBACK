"""
report.py
Generates a self-contained HTML mobility report from:
  - ROM summary
  - Per-joint scores
  - Claude's assessment (exercises, narrative)
  - Path to the annotated video

The HTML file is fully standalone — no external dependencies.
"""

import json
from pathlib import Path
from config import JOINT_DISPLAY_NAMES, CLINICAL_NORMS, SCORE_GOOD, SCORE_MODERATE


def _score_color_css(score: int) -> str:
    if score >= SCORE_GOOD:
        return "#2ec27e"
    elif score >= SCORE_MODERATE:
        return "#e5a50a"
    else:
        return "#e01b24"


def _tier_badge(tier: str) -> str:
    colors = {
        "beginner":     ("#1d9e75", "#e1f5ee"),
        "intermediate": ("#ba7517", "#faeeda"),
        "advanced":     ("#a32d2d", "#fcebeb"),
    }
    fg, bg = colors.get(tier.lower(), ("#555", "#eee"))
    return (
        f'<span style="background:{bg};color:{fg};font-size:11px;'
        f'padding:2px 8px;border-radius:10px;font-weight:500;">{tier}</span>'
    )


def generate_html_report(
    rom_summary: dict,
    scores: dict,
    assessment: dict,
    annotated_video_path: str,
    output_path: str,
    sport_context: str = "",
) -> str:
    """
    Write the HTML report to output_path. Returns the path.
    """
    video_name = Path(annotated_video_path).name
    overall_score = assessment.get("overall_score", 0)
    overall_summary = assessment.get("overall_summary", "")
    joint_assessments = assessment.get("joints", {})

    overall_color = _score_color_css(overall_score)

    # Build joint cards
    joint_cards_html = []
    for joint, data in rom_summary.items():
        display   = JOINT_DISPLAY_NAMES.get(joint, joint)
        norm      = CLINICAL_NORMS.get(joint, 90)
        rng       = data.get("range", 0)
        score     = scores.get(joint, 0)
        color     = _score_color_css(score)
        jdata     = joint_assessments.get(joint, {})
        assessment_text = jdata.get("assessment", "")
        exercises       = jdata.get("exercises", [])

        bar_pct = min(100, int(rng / norm * 100))

        ex_html = ""
        for ex in exercises:
            tier_badge = _tier_badge(ex.get("tier", "beginner"))
            ex_html += f"""
            <div style="padding:10px 14px;border:0.5px solid #e0e0e0;
                        border-radius:8px;margin-bottom:8px;">
              <div style="display:flex;align-items:center;gap:8px;margin-bottom:4px;">
                <span style="font-weight:500;font-size:14px;">{ex.get('name','')}</span>
                {tier_badge}
              </div>
              <p style="margin:4px 0;font-size:13px;color:#555;">{ex.get('description','')}</p>
              <p style="margin:4px 0;font-size:12px;color:#888;">{ex.get('sets_reps','')}</p>
            </div>"""

        joint_cards_html.append(f"""
        <div style="background:#fff;border:0.5px solid #ddd;border-radius:12px;
                    padding:18px 20px;margin-bottom:14px;">
          <div style="display:flex;align-items:center;justify-content:space-between;
                      margin-bottom:10px;">
            <span style="font-weight:500;font-size:15px;">{display}</span>
            <span style="font-size:22px;font-weight:500;color:{color};">{score}</span>
          </div>
          <div style="font-size:12px;color:#888;margin-bottom:6px;">
            ROM: {rng:.1f}° / {norm}° clinical norm
            &nbsp;·&nbsp; min {data.get('min','?')}° → max {data.get('max','?')}°
          </div>
          <div style="background:#f0f0f0;border-radius:4px;height:6px;margin-bottom:10px;">
            <div style="background:{color};width:{bar_pct}%;height:6px;border-radius:4px;"></div>
          </div>
          {"<p style='font-size:13px;color:#444;margin:0 0 10px;'>" + assessment_text + "</p>" if assessment_text else ""}
          {ex_html}
        </div>""")

    joint_cards = "\n".join(joint_cards_html)
    context_line = f"<p style='color:#888;font-size:13px;'>Movement: {sport_context}</p>" if sport_context else ""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Mobility Analysis Report</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
          background: #f5f5f5; color: #1a1a1a; padding: 24px 16px; }}
  .container {{ max-width: 760px; margin: 0 auto; }}
  h1 {{ font-size: 22px; font-weight: 500; margin-bottom: 4px; }}
  h2 {{ font-size: 16px; font-weight: 500; margin: 24px 0 12px; }}
  video {{ width: 100%; border-radius: 10px; background: #000; }}
</style>
</head>
<body>
<div class="container">

  <h1>Mobility Analysis Report</h1>
  {context_line}

  <div style="background:#fff;border:0.5px solid #ddd;border-radius:12px;
              padding:20px;margin:16px 0;display:flex;align-items:center;gap:20px;">
    <div style="text-align:center;min-width:80px;">
      <div style="font-size:48px;font-weight:500;color:{overall_color};
                  line-height:1;">{overall_score}</div>
      <div style="font-size:12px;color:#888;margin-top:4px;">overall score</div>
    </div>
    <p style="font-size:14px;color:#444;line-height:1.6;">{overall_summary}</p>
  </div>

  <h2>Annotated video</h2>
  <video controls>
    <source src="{video_name}" type="video/mp4">
    Your browser does not support the video tag.
  </video>

  <h2>Joint scores &amp; exercises</h2>
  {joint_cards}

  <p style="font-size:11px;color:#aaa;margin-top:24px;text-align:center;">
    Generated by mobility-analyzer · Assessment by Claude (Anthropic)
  </p>
</div>
</body>
</html>"""

    Path(output_path).write_text(html, encoding="utf-8")
    print(f"[report] HTML report saved → {output_path}")
    return output_path
