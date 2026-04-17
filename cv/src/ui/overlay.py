"""
HUD panel renderer.
Draws onto the LEFT portion of a composite canvas (panel | video).
The panel has its own solid background — it is NOT overlaid on the video.
"""

from __future__ import annotations

from typing import Optional

import cv2
import numpy as np

from ..analysis.angles import JointAngles
from ..analysis.mobility import MobilityStatus

FONT      = cv2.FONT_HERSHEY_SIMPLEX
FONT_BOLD = cv2.FONT_HERSHEY_DUPLEX

# Panel layout
PANEL_WIDTH = 300
MARGIN      = 12
LINE_HEIGHT = 22

# Button
BTN_HEIGHT     = 28
BTN_BOTTOM_PAD = 12
BTN_X1         = MARGIN
BTN_X2         = PANEL_WIDTH - MARGIN

# Colors (BGR)
_BG     = ( 18,  18,  18)
_WHITE  = (255, 255, 255)
_GREY   = (160, 160, 160)
_GREEN  = (  0, 210,   0)
_YELLOW = (  0, 200, 220)
_RED    = (  0,   0, 210)
_CYAN   = (200, 200,   0)
_BTN_BG = ( 55,  55,  55)
_BTN_HL = ( 90,  90,  90)
_DIV    = ( 60,  60,  60)


def _score_color(score: float) -> tuple:
    if score >= 80: return _GREEN
    if score >= 50: return _YELLOW
    return _RED


class OverlayRenderer:
    """
    Call render(canvas, ...) each frame.
    canvas must be shape (h, PANEL_WIDTH + video_w, 3) — the panel occupies
    canvas[:, :PANEL_WIDTH] and is filled here with a solid background.

    self.cam_btn_rect is always in canvas (panel) coordinates — no flip math needed.
    """

    def __init__(self) -> None:
        self.cam_btn_rect:   Optional[tuple[int, int, int, int]] = None
        self.pause_btn_rect: Optional[tuple[int, int, int, int]] = None

    def render(
        self,
        canvas: np.ndarray,
        angles: Optional[JointAngles],
        status: Optional[MobilityStatus],
        fps: float,
        camera_label: str = "Cam 0",
        btn_hover: bool = False,
        paused: bool = False,
        pause_btn_hover: bool = False,
    ) -> None:
        """Draw the panel onto canvas[:, :PANEL_WIDTH] in-place."""
        h = canvas.shape[0]

        # Solid panel background
        canvas[:, :PANEL_WIDTH] = _BG

        y = MARGIN + 16

        # --- Title + FPS ---
        cv2.putText(canvas, "Mobility Analysis", (MARGIN, y),
                    FONT_BOLD, 0.55, _WHITE, 1, cv2.LINE_AA)
        y += LINE_HEIGHT - 2
        cv2.putText(canvas, f"FPS: {fps:.0f}", (MARGIN, y),
                    FONT, 0.4, _GREY, 1, cv2.LINE_AA)
        y += LINE_HEIGHT + 2
        self._div(canvas, y); y += 8

        if status is None or angles is None:
            cv2.putText(canvas, "No person detected", (MARGIN, y + 20),
                        FONT, 0.46, _RED, 1, cv2.LINE_AA)
        else:
            if status.calibrating:
                cv2.putText(canvas, "Calibrating...", (MARGIN, y + 16),
                            FONT, 0.46, _YELLOW, 1, cv2.LINE_AA)
                y += LINE_HEIGHT * 2
            else:
                y += 2

            # --- Joint table ---
            # Fixed x positions for each column (proportional font needs abs coords)
            X_LABEL = MARGIN
            X_CUR   = 130
            X_MIN   = 185
            X_MAX   = 240

            for hdr, x in [("Cur", X_CUR), ("Min", X_MIN), ("Max", X_MAX)]:
                cv2.putText(canvas, hdr, (x, y), FONT, 0.35, _GREY, 1, cv2.LINE_AA)
            y += LINE_HEIGHT

            def fv(d, k): return f"{d[k]:.0f}" if k in d else "---"
            def sc(v): return (  _GREEN  if v >= 80
                               else _YELLOW if v >= 50
                               else _RED)

            for label, pk, lk, rk in [
                ("Elbow",    "elbow",    "elbow_left",    "elbow_right"),
                ("Knee",     "knee",     "knee_left",     "knee_right"),
                ("Hip",      "hip",      "hip_left",      "hip_right"),
                ("Shoulder", "shoulder", "shoulder_left", "shoulder_right"),
            ]:
                asym = status.asymmetry_scores.get(pk, 0.0)
                col  = _RED if asym >= 30 else (_YELLOW if asym >= 15 else _WHITE)
                js   = status.joint_scores.get(pk)

                # Left row
                cv2.putText(canvas, label + " L", (X_LABEL, y), FONT, 0.37, col, 1, cv2.LINE_AA)
                cv2.putText(canvas, fv(status.cur_angles, lk), (X_CUR, y), FONT, 0.37, col, 1, cv2.LINE_AA)
                cv2.putText(canvas, fv(status.min_angles, lk), (X_MIN, y), FONT, 0.37, col, 1, cv2.LINE_AA)
                cv2.putText(canvas, fv(status.max_angles, lk), (X_MAX, y), FONT, 0.37, col, 1, cv2.LINE_AA)
                y += LINE_HEIGHT - 5

                # Right row
                cv2.putText(canvas, "  R", (X_LABEL, y), FONT, 0.37, col, 1, cv2.LINE_AA)
                cv2.putText(canvas, fv(status.cur_angles, rk), (X_CUR, y), FONT, 0.37, col, 1, cv2.LINE_AA)
                cv2.putText(canvas, fv(status.min_angles, rk), (X_MIN, y), FONT, 0.37, col, 1, cv2.LINE_AA)
                cv2.putText(canvas, fv(status.max_angles, rk), (X_MAX, y), FONT, 0.37, col, 1, cv2.LINE_AA)
                y += LINE_HEIGHT - 2

                # Score row
                if js and not status.calibrating:
                    cv2.putText(canvas, "Score", (X_LABEL + 6, y), FONT, 0.33, _GREY, 1, cv2.LINE_AA)
                    cv2.putText(canvas, f"L:{js.left:.0f}", (X_CUR,       y), FONT, 0.33, sc(js.left),     1, cv2.LINE_AA)
                    cv2.putText(canvas, f"R:{js.right:.0f}",(X_MIN,       y), FONT, 0.33, sc(js.right),    1, cv2.LINE_AA)
                    cv2.putText(canvas, f"Jt:{js.combined:.0f}", (X_MAX - 10, y), FONT, 0.33, sc(js.combined), 1, cv2.LINE_AA)
                y += LINE_HEIGHT

            self._div(canvas, y); y += 10

            # --- Mobility score ---
            sc = status.overall_score
            cv2.putText(canvas, "Mobility Score", (MARGIN, y),
                        FONT, 0.44, _GREY, 1, cv2.LINE_AA)
            y += LINE_HEIGHT + 2
            cv2.putText(canvas, f"{sc:.0f} / 100", (MARGIN + 8, y),
                        FONT_BOLD, 0.88, _score_color(sc), 2, cv2.LINE_AA)
            y += LINE_HEIGHT + 8
            self._div(canvas, y); y += 8

        # --- Key hints ---
        hints_y = h - BTN_BOTTOM_PAD - 14
        cv2.putText(canvas, "[Q] Quit  [R] Reset  [C] Cam  [Space] Pause",
                    (MARGIN, hints_y), FONT, 0.30, _GREY, 1, cv2.LINE_AA)

    def _div(self, canvas: np.ndarray, y: int) -> None:
        cv2.line(canvas, (MARGIN, y), (PANEL_WIDTH - MARGIN, y), _DIV, 1)
