"""
Gap analysis — compares user ROM against sport blueprint and assigns status colors.
"""

from typing import Dict, Tuple, List
from config import SPORT_BLUEPRINTS, GREEN_THRESHOLD, YELLOW_THRESHOLD
from models import JointGap, JointStatus


def compute_gaps(
    sport: str,
    user_mobility: Dict[str, float],
) -> Tuple[List[JointGap], Dict[str, str], float]:
    """
    Compare user_mobility against the sport's ROM blueprint.

    Returns:
        gaps          — list of JointGap sorted worst → best
        body_map      — joint_key → color string for the frontend SVG
        readiness_score — 0–100 overall sport readiness percentage
    """
    blueprint = SPORT_BLUEPRINTS[sport]["joints"]
    gaps: List[JointGap] = []
    body_map: Dict[str, str] = {}

    for joint_key, spec in blueprint.items():
        required = spec["required"]
        current  = user_mobility.get(joint_key, 0.0)
        gap      = max(0.0, required - current)
        percent  = round(min(100.0, (current / required) * 100), 1)

        if percent >= GREEN_THRESHOLD:
            status = JointStatus.GREEN
        elif percent >= YELLOW_THRESHOLD:
            status = JointStatus.YELLOW
        else:
            status = JointStatus.RED

        gaps.append(JointGap(
            joint_key=joint_key,
            label=spec["label"],
            current_rom=current,
            required_rom=required,
            gap=round(gap, 1),
            percent_achieved=percent,
            status=status,
        ))
        body_map[joint_key] = status.value

    # Sort worst → best so the UI can render priority items at the top
    gaps.sort(key=lambda g: g.percent_achieved)

    readiness_score = round(
        sum(g.percent_achieved for g in gaps) / len(gaps), 1
    ) if gaps else 0.0

    return gaps, body_map, readiness_score
