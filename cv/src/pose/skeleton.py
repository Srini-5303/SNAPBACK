"""
Skeleton overlay renderer.
Draws numbered joint circles and color-coded limb edges onto a video frame.
"""

from __future__ import annotations

from typing import Optional

import cv2
import numpy as np

from .estimator import PoseResult
from .landmarks import (
    DISPLAY_TO_MP,
    MID_SHOULDER_KEY, MID_HIP_KEY,
    LEFT_SHOULDER, RIGHT_SHOULDER, LEFT_HIP, RIGHT_HIP,
    SKELETON_EDGES, SIDE_COLORS,
    COLOR_GREEN, COLOR_WHITE, COLOR_BLACK,
)

VISIBILITY_THRESHOLD = 0.5


class SkeletonRenderer:
    """
    Draws the stick-figure skeleton on a copy of the frame.

    joint_colors maps display joint index → BGR override color.
    Any joint not in joint_colors defaults to COLOR_GREEN.
    """

    def __init__(
        self,
        line_thickness: int = 3,
        circle_radius: int = 12,
        font_scale: float = 0.38,
    ) -> None:
        self.line_thickness = line_thickness
        self.circle_radius  = circle_radius
        self.font_scale     = font_scale

    # ------------------------------------------------------------------
    def render(
        self,
        frame: np.ndarray,
        pose_result: PoseResult,
        joint_colors: dict[int, tuple],
        frame_shape: tuple[int, int],   # (height, width)
    ) -> np.ndarray:
        """Return an annotated copy of frame; does not modify original."""
        out = frame.copy()
        h, w = frame_shape

        coords = self._get_pixel_coords(pose_result, h, w)
        if not coords:
            return out

        # Draw edges first (behind circles)
        for (j1, j2, side) in SKELETON_EDGES:
            pt1 = coords.get(j1)
            pt2 = coords.get(j2)
            if pt1 is None or pt2 is None:
                continue
            color = SIDE_COLORS[side]
            cv2.line(out, pt1, pt2, color, self.line_thickness, cv2.LINE_AA)

        # Draw joint circles on top
        for display_idx in DISPLAY_TO_MP:
            pt = coords.get(display_idx)
            if pt is None:
                continue
            color = joint_colors.get(display_idx, COLOR_GREEN)
            self._draw_joint(out, pt, display_idx, color)

        return out

    # ------------------------------------------------------------------
    def _get_pixel_coords(
        self,
        pose_result: PoseResult,
        h: int,
        w: int,
    ) -> dict[int | str, tuple[int, int]]:
        """
        Returns pixel (x, y) for each visible display joint and both
        synthetic mid-joints. Joints below VISIBILITY_THRESHOLD are omitted.
        """
        coords: dict[int | str, tuple[int, int]] = {}

        for display_idx, mp_idx in DISPLAY_TO_MP.items():
            if pose_result.visibility[mp_idx] < VISIBILITY_THRESHOLD:
                continue
            x, y, _ = pose_result.landmarks[mp_idx]
            coords[display_idx] = (int(x * w), int(y * h))

        # Synthetic mid-shoulder (requires both shoulders visible)
        ls_vis = pose_result.visibility[LEFT_SHOULDER]
        rs_vis = pose_result.visibility[RIGHT_SHOULDER]
        if ls_vis >= VISIBILITY_THRESHOLD and rs_vis >= VISIBILITY_THRESHOLD:
            lx, ly, _ = pose_result.landmarks[LEFT_SHOULDER]
            rx, ry, _ = pose_result.landmarks[RIGHT_SHOULDER]
            coords[MID_SHOULDER_KEY] = (
                int((lx + rx) / 2 * w),
                int((ly + ry) / 2 * h),
            )

        # Synthetic mid-hip (requires both hips visible)
        lh_vis = pose_result.visibility[LEFT_HIP]
        rh_vis = pose_result.visibility[RIGHT_HIP]
        if lh_vis >= VISIBILITY_THRESHOLD and rh_vis >= VISIBILITY_THRESHOLD:
            lx, ly, _ = pose_result.landmarks[LEFT_HIP]
            rx, ry, _ = pose_result.landmarks[RIGHT_HIP]
            coords[MID_HIP_KEY] = (
                int((lx + rx) / 2 * w),
                int((ly + ry) / 2 * h),
            )

        return coords

    # ------------------------------------------------------------------
    def _draw_joint(
        self,
        frame: np.ndarray,
        center: tuple[int, int],
        joint_index: int,
        color: tuple[int, int, int],
    ) -> None:
        r = self.circle_radius
        # Outer dark ring for contrast
        cv2.circle(frame, center, r + 2, COLOR_BLACK, -1, cv2.LINE_AA)
        # Filled coloured circle
        cv2.circle(frame, center, r, color, -1, cv2.LINE_AA)
        # Joint number label
        label = str(joint_index)
        (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, self.font_scale, 1)
        tx = center[0] - tw // 2
        ty = center[1] + th // 2
        cv2.putText(
            frame, label,
            (tx, ty),
            cv2.FONT_HERSHEY_SIMPLEX,
            self.font_scale,
            COLOR_WHITE,
            1,
            cv2.LINE_AA,
        )
