"""
Gap analysis — compares CV session_rom against sport blueprint baselines.

Input:  cv_data  — dict matching CVResult shape (session_rom, asymmetry_scores, overall_score)
Output: gaps, body_map, readiness_score
"""

from typing import Dict, Tuple, List, Any
from config import SPORT_BLUEPRINTS, GREEN_THRESHOLD, YELLOW_THRESHOLD
from models import JointGap, JointStatus


def compute_gaps(
    sport: str,
    cv_data: Dict[str, Any],
) -> Tuple[List[JointGap], Dict[str, str], float]:
    """
    Compare session_rom from the CV result against the sport's ROM blueprint.

    Returns:
        gaps            — list of JointGap sorted worst → best
        body_map        — joint_key → color string for the frontend
        readiness_score — 0–100 overall sport readiness percentage
    """
    blueprint        = SPORT_BLUEPRINTS[sport]["joints"]
    session_rom      = cv_data.get("session_rom", {})
    asymmetry_scores = cv_data.get("asymmetry_scores", {})

    gaps: List[JointGap] = []
    body_map: Dict[str, str] = {}

    for joint_key, spec in blueprint.items():
        left_rom  = session_rom.get(f"{joint_key}_left",  0.0)
        right_rom = session_rom.get(f"{joint_key}_right", 0.0)
        combined  = (left_rom + right_rom) / 2 if (left_rom or right_rom) else 0.0

        required  = spec["required_combined"]
        gap       = max(0.0, required - combined)
        percent   = round(min(100.0, (combined / required) * 100), 1) if required > 0 else 100.0
        asymmetry = asymmetry_scores.get(joint_key, 0.0)

        if percent >= GREEN_THRESHOLD:
            status = JointStatus.GREEN
        elif percent >= YELLOW_THRESHOLD:
            status = JointStatus.YELLOW
        else:
            status = JointStatus.RED

        gaps.append(JointGap(
            joint_key=joint_key,
            label=spec["label"],
            current_rom=round(combined, 1),
            current_left=round(left_rom, 1),
            current_right=round(right_rom, 1),
            required_rom=required,
            gap=round(gap, 1),
            percent_achieved=percent,
            asymmetry=asymmetry,
            status=status,
        ))
        body_map[joint_key] = status.value

    # Sort worst → best so Claude and the UI see priority items first
    gaps.sort(key=lambda g: g.percent_achieved)

    readiness_score = round(
        sum(g.percent_achieved for g in gaps) / len(gaps), 1
    ) if gaps else 0.0

    return gaps, body_map, readiness_score
