"""
overlay.py
Draws the stick figure skeleton, joint angle arcs + labels, and the live
HUD panel onto each video frame.

Why Pillow for text?
  cv2.putText() uses a bitmap font — blocky and unreadable below ~18px.
  Pillow's ImageDraw.text() with a TrueType font gives clean, anti-aliased
  labels at any size. We convert BGR→RGB→PIL, draw text, then convert back.
"""

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

from config import (
    SKELETON_CONNECTIONS, JOINT_TRIPLETS, CLINICAL_NORMS,
    JOINT_DISPLAY_NAMES,
    SKELETON_COLOR, SKELETON_THICKNESS, JOINT_RADIUS,
    COLOR_GOOD, COLOR_MODERATE, COLOR_POOR,
    HUD_ALPHA, HUD_BG_COLOR,
    FONT_PATH, FONT_PATH_FALLBACK,
    SCORE_GOOD, SCORE_MODERATE, MIN_VISIBILITY,
)
from angles import compute_angle, score_joint, RomTracker


# ── Font loader ────────────────────────────────────────────────────────────────

def _load_font(size: int) -> ImageFont.FreeTypeFont:
    for path in [FONT_PATH, FONT_PATH_FALLBACK]:
        if Path(path).exists():
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                pass
    return ImageFont.load_default()


_FONT_SMALL  = None
_FONT_MEDIUM = None
_FONT_LARGE  = None

def _get_fonts():
    global _FONT_SMALL, _FONT_MEDIUM, _FONT_LARGE
    if _FONT_SMALL is None:
        _FONT_SMALL  = _load_font(13)
        _FONT_MEDIUM = _load_font(16)
        _FONT_LARGE  = _load_font(20)
    return _FONT_SMALL, _FONT_MEDIUM, _FONT_LARGE


# ── Color helpers ─────────────────────────────────────────────────────────────

def _bgr_to_rgb(bgr: tuple) -> tuple:
    return (bgr[2], bgr[1], bgr[0])

def _score_color_rgb(score: int) -> tuple:
    if score >= SCORE_GOOD:
        return _bgr_to_rgb(COLOR_GOOD)
    elif score >= SCORE_MODERATE:
        return _bgr_to_rgb(COLOR_MODERATE)
    else:
        return _bgr_to_rgb(COLOR_POOR)

def _score_color_bgr(score: int) -> tuple:
    if score >= SCORE_GOOD:
        return COLOR_GOOD
    elif score >= SCORE_MODERATE:
        return COLOR_MODERATE
    else:
        return COLOR_POOR


# ── Skeleton drawing ──────────────────────────────────────────────────────────

def draw_skeleton(frame: np.ndarray, landmarks: dict, scores: dict) -> np.ndarray:
    """
    Draw bone lines + colored joint circles onto frame (in-place, returns frame).
    `scores` maps joint_name → 0–100 score (used to color each joint circle).

    Strategy:
      1. Semi-transparent overlay so original video shows through.
      2. Lines in soft green, circles colored by ROM score.
    """
    overlay = frame.copy()

    # Draw bone lines
    for (idx_a, idx_b) in SKELETON_CONNECTIONS:
        if idx_a not in landmarks or idx_b not in landmarks:
            continue
        if landmarks[idx_a][2] < MIN_VISIBILITY or landmarks[idx_b][2] < MIN_VISIBILITY:
            continue
        pt_a = (landmarks[idx_a][0], landmarks[idx_a][1])
        pt_b = (landmarks[idx_b][0], landmarks[idx_b][1])
        cv2.line(overlay, pt_a, pt_b, SKELETON_COLOR, SKELETON_THICKNESS, cv2.LINE_AA)

    # Draw joint dots — colored by score of nearest tracked joint
    joint_vertex_map = {}
    for joint, (idx_a, idx_v, idx_b) in JOINT_TRIPLETS.items():
        joint_vertex_map[idx_v] = joint

    for idx, (px, py, vis) in landmarks.items():
        if vis < MIN_VISIBILITY:
            continue
        joint = joint_vertex_map.get(idx)
        score = scores.get(joint, 50) if joint else 50
        color = _score_color_bgr(score)
        cv2.circle(overlay, (px, py), JOINT_RADIUS,     color,  -1, cv2.LINE_AA)
        cv2.circle(overlay, (px, py), JOINT_RADIUS + 1, (0,0,0), 1, cv2.LINE_AA)

    cv2.addWeighted(overlay, 0.8, frame, 0.2, 0, frame)
    return frame


# ── Angle arc + label ─────────────────────────────────────────────────────────

def draw_angle_annotation(
    pil_draw: ImageDraw.ImageDraw,
    pt_a: tuple, pt_v: tuple, pt_b: tuple,
    angle: float,
    score: int,
    arc_radius: int = 22,
):
    """
    Draw a small arc between the two bones at `pt_v`, then a label showing
    the angle in degrees. Uses Pillow so text is anti-aliased.

    The arc is drawn as a pie-slice outline between the two bone directions.
    The label is placed 38px from pt_v toward the bisector of the two vectors.
    """
    font_small, font_medium, _ = _get_fonts()
    color = _score_color_rgb(score)

    a  = np.array(pt_a, dtype=float)
    v  = np.array(pt_v, dtype=float)
    b  = np.array(pt_b, dtype=float)

    v1 = a - v
    v2 = b - v

    # Angles of each arm in image space (degrees, 0 = right)
    ang1 = float(np.degrees(np.arctan2(v1[1], v1[0])))
    ang2 = float(np.degrees(np.arctan2(v2[1], v2[0])))

    # Normalise to [0, 360)
    ang1 = ang1 % 360
    ang2 = ang2 % 360

    # Always draw the smaller arc
    start = min(ang1, ang2)
    end   = max(ang1, ang2)
    if end - start > 180:
        start, end = end, start + 360   # go the other way

    box = [
        (pt_v[0] - arc_radius, pt_v[1] - arc_radius),
        (pt_v[0] + arc_radius, pt_v[1] + arc_radius),
    ]
    pil_draw.arc(box, start=start, end=end, fill=color, width=2)

    # Bisector direction for label placement
    n1 = v1 / (np.linalg.norm(v1) + 1e-9)
    n2 = v2 / (np.linalg.norm(v2) + 1e-9)
    bisector = n1 + n2
    bn = np.linalg.norm(bisector)
    if bn > 1e-6:
        bisector /= bn
    else:
        bisector = np.array([1.0, 0.0])

    label_offset = 38
    lx = int(pt_v[0] + bisector[0] * label_offset)
    ly = int(pt_v[1] + bisector[1] * label_offset)

    label = f"{int(round(angle))}°"

    # Background pill
    bbox = pil_draw.textbbox((lx, ly), label, font=font_small, anchor="mm")
    pad = 3
    pil_draw.rounded_rectangle(
        [bbox[0]-pad, bbox[1]-pad, bbox[2]+pad, bbox[3]+pad],
        radius=4, fill=(15, 15, 15, 210)
    )
    pil_draw.text((lx, ly), label, font=font_small, fill=color, anchor="mm")


# ── HUD panel ─────────────────────────────────────────────────────────────────

def draw_hud(frame: np.ndarray, tracker: RomTracker, frame_idx: int, total_frames: int):
    """
    Draw a semi-transparent HUD panel in the top-left corner showing:
      - "LIVE ROM" header
      - Per-joint: display name, running max range, score bar

    Uses OpenCV for the background rect (fast), Pillow for the text.
    """
    font_small, font_medium, _ = _get_fonts()
    joints = list(JOINT_TRIPLETS.keys())

    row_h    = 22
    panel_w  = 195
    panel_h  = 32 + len(joints) * row_h + 10
    margin   = 12

    # Semi-transparent background using OpenCV
    overlay = frame.copy()
    cv2.rectangle(
        overlay,
        (margin, margin),
        (margin + panel_w, margin + panel_h),
        HUD_BG_COLOR, -1
    )
    cv2.addWeighted(overlay, HUD_ALPHA, frame, 1 - HUD_ALPHA, 0, frame)

    # Convert to Pillow for text
    rgb    = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    pil_im = Image.fromarray(rgb)
    draw   = ImageDraw.Draw(pil_im, "RGBA")

    # Header
    hx = margin + 10
    hy = margin + 10
    draw.text((hx, hy), "LIVE ROM", font=font_medium, fill=(200, 200, 200))

    # Progress bar (thin, below header)
    bar_y   = margin + 30
    bar_w   = panel_w - 20
    bar_x   = margin + 10
    draw.rectangle([bar_x, bar_y, bar_x + bar_w, bar_y + 2], fill=(50, 50, 50))
    progress = int(bar_w * (frame_idx / max(total_frames, 1)))
    draw.rectangle([bar_x, bar_y, bar_x + progress, bar_y + 2], fill=(100, 200, 130))

    # Joint rows
    for i, joint in enumerate(joints):
        ry     = margin + 38 + i * row_h
        score  = tracker.get_score(joint)
        rng    = tracker.get_range(joint)
        color  = _score_color_rgb(score)
        name   = JOINT_DISPLAY_NAMES[joint]

        # Name
        draw.text((hx, ry), name, font=font_small, fill=(160, 160, 160))
        # Score value
        score_str = f"{rng:.0f}° / {score}"
        draw.text((margin + panel_w - 14, ry), score_str,
                  font=font_small, fill=color, anchor="ra")

    # Convert back
    result = cv2.cvtColor(np.array(pil_im), cv2.COLOR_RGB2BGR)
    np.copyto(frame, result)


# ── Full frame renderer ───────────────────────────────────────────────────────

def render_frame(
    frame: np.ndarray,
    frame_data: dict,
    frame_angles: dict,
    tracker: RomTracker,
    scores: dict,
    frame_idx: int,
    total_frames: int,
) -> np.ndarray:
    """
    Apply all overlays to a single frame:
      1. Skeleton (OpenCV)
      2. Angle arcs + labels (Pillow)
      3. HUD panel (OpenCV + Pillow)
    """
    landmarks = frame_data["landmarks"]

    # 1 — Skeleton
    draw_skeleton(frame, landmarks, scores)

    # 2 — Angle arcs via Pillow
    rgb    = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    pil_im = Image.fromarray(rgb).convert("RGBA")
    draw   = ImageDraw.Draw(pil_im, "RGBA")

    for joint, (idx_a, idx_v, idx_b) in JOINT_TRIPLETS.items():
        angle = frame_angles.get(joint)
        if angle is None:
            continue
        if not all(idx in landmarks for idx in (idx_a, idx_v, idx_b)):
            continue
        if min(landmarks[i][2] for i in (idx_a, idx_v, idx_b)) < MIN_VISIBILITY:
            continue

        pt_a = landmarks[idx_a][:2]
        pt_v = landmarks[idx_v][:2]
        pt_b = landmarks[idx_b][:2]
        score = tracker.get_score(joint)

        draw_angle_annotation(draw, pt_a, pt_v, pt_b, angle, score)

    # Merge RGBA back to BGR
    rgb_result = np.array(pil_im.convert("RGB"))
    frame = cv2.cvtColor(rgb_result, cv2.COLOR_RGB2BGR)

    # 3 — HUD
    draw_hud(frame, tracker, frame_idx, total_frames)

    return frame
