"""
Body Mobility Analysis — entry point.

Controls:
  Q / ESC  — quit
  R        — reset session history / ROM tracking
  C        — cycle to next camera
  click    — click the "Switch Camera" button on the HUD panel
"""

from __future__ import annotations

import argparse
import time
from typing import Optional

import cv2
import numpy as np

from src.pose.estimator import PoseEstimator
from src.pose.skeleton import SkeletonRenderer
from src.analysis.angles import extract_angles
from src.analysis.mobility import MobilityAnalyzer, build_joint_colors
from src.ui.overlay import OverlayRenderer, PANEL_WIDTH

WINDOW_NAME    = "Body Mobility Analysis"
DISPLAY_WIDTH  = 1280
DISPLAY_HEIGHT = 720
TARGET_FPS     = 30
MAX_CAM_PROBE  = 6   # how many camera indices to probe at startup

# Set to a file path to use a video instead of a live camera.
# Set to None to use the live camera.
VIDEO_PATH = r"C:\Users\aareg\Downloads\WhatsApp Video 2026-04-11 at 12.02.30 PM.mp4"


# ---------------------------------------------------------------------------
# Camera helpers
# ---------------------------------------------------------------------------

def probe_cameras(max_idx: int = MAX_CAM_PROBE) -> list[int]:
    """Return indices of cameras that can be opened."""
    found = []
    for i in range(max_idx):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            found.append(i)
        cap.release()
    return found if found else [0]   # fallback: assume index 0 exists


def open_camera(idx: int) -> cv2.VideoCapture:
    cap = cv2.VideoCapture(idx)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH,  DISPLAY_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, DISPLAY_HEIGHT)
    cap.set(cv2.CAP_PROP_FPS,          TARGET_FPS)
    return cap


# ---------------------------------------------------------------------------
# Init frame
# ---------------------------------------------------------------------------

def _show_init_frame(window: str, w: int, h: int, msg: str) -> None:
    blank = np.zeros((h, w, 3), dtype="uint8")
    (tw, _), _ = cv2.getTextSize(msg, cv2.FONT_HERSHEY_SIMPLEX, 0.8, 2)
    cv2.putText(blank, msg, (w // 2 - tw // 2, h // 2),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (180, 180, 180), 2, cv2.LINE_AA)
    cv2.imshow(window, blank)
    cv2.waitKey(1)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main(model_complexity: int = 1, start_camera: int = 0) -> None:
    # --- Build unified source list: ["video", 0, 1, 2, ...] ---
    print("Probing cameras...")
    available_cams = probe_cameras()
    print(f"Found cameras: {available_cams}")

    # "video" sentinel is first if a video path is configured
    sources: list = (["video"] if VIDEO_PATH else []) + available_cams
    source_pos = 0   # start on first source (video if configured, else cam 0)

    def open_source(src) -> tuple[cv2.VideoCapture, bool, str]:
        """Open a source. Returns (cap, is_video_mode, label)."""
        if src == "video":
            c = cv2.VideoCapture(VIDEO_PATH)
            return c, True, "Video"
        else:
            c = open_camera(src)
            return c, False, f"Cam {src}"

    cap, video_mode, source_label = open_source(sources[source_pos])

    cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(WINDOW_NAME, PANEL_WIDTH + DISPLAY_WIDTH, DISPLAY_HEIGHT)
    _show_init_frame(WINDOW_NAME, PANEL_WIDTH + DISPLAY_WIDTH, DISPLAY_HEIGHT,
                     "Initialising pose model, please wait...")

    # --- Mouse state shared with callback ---
    mouse_state = {"x": -1, "y": -1, "clicked": False}

    def on_mouse(event, x, y, flags, param):
        mouse_state["x"] = x
        mouse_state["y"] = y
        if event == cv2.EVENT_LBUTTONDOWN:
            mouse_state["clicked"] = True

    cv2.setMouseCallback(WINDOW_NAME, on_mouse)

    with PoseEstimator(model_complexity=model_complexity) as estimator:
        skeleton = SkeletonRenderer()
        analyzer = MobilityAnalyzer()
        overlay  = OverlayRenderer()

        prev_time    = time.perf_counter()
        switch_cam   = False
        paused       = False
        last_frame:  Optional[np.ndarray] = None
        last_angles  = None   # retained across frames when detection is lost
        last_status  = None

        while True:
            if paused and last_frame is not None:
                frame = last_frame.copy()
            else:
                ret, frame = cap.read()
                if not ret:
                    if video_mode:
                        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                        continue
                    else:
                        print(f"Camera {cam_idx} read failed, retrying...")
                        cap.release()
                        cap = open_camera(cam_idx)
                        continue
                last_frame = frame.copy()

            h, w = frame.shape[:2]

            # --- Pose pipeline ---
            pose_result = estimator.process(frame)
            if pose_result:
                angles = extract_angles(pose_result)
                status = analyzer.update(angles)
                last_angles = angles
                last_status = status
                joint_colors = build_joint_colors(status) if status else {}
                frame = skeleton.render(
                    frame, pose_result, joint_colors, frame_shape=(h, w))

            # Use last known values when detection is lost
            angles = last_angles
            status = last_status

            # --- Mirror flip video for live camera only ---
            if not video_mode:
                frame = cv2.flip(frame, 1)

            # --- Composite: [panel | video] side-by-side ---
            canvas = np.zeros((h, PANEL_WIDTH + w, 3), dtype=np.uint8)
            canvas[:, PANEL_WIDTH:] = frame   # video on the right

            # --- Button hover ---
            mx, my = mouse_state["x"], mouse_state["y"]

            btn_hover = False
            if overlay.cam_btn_rect is not None:
                bx1, by1, bx2, by2 = overlay.cam_btn_rect
                if bx1 <= mx <= bx2 and by1 <= my <= by2:
                    btn_hover = True

            pause_btn_hover = False
            if overlay.pause_btn_rect is not None:
                px1, py1, px2, py2 = overlay.pause_btn_rect
                if px1 <= mx <= px2 and py1 <= my <= py2:
                    pause_btn_hover = True

            # --- Draw panel onto canvas[:, :PANEL_WIDTH] ---
            now = time.perf_counter()
            fps = 1.0 / max(now - prev_time, 1e-9)
            prev_time = now

            overlay.render(
                canvas, angles, status, fps,
                camera_label=source_label,
                btn_hover=btn_hover,
                paused=paused,
                pause_btn_hover=pause_btn_hover,
            )
            cv2.imshow(WINDOW_NAME, canvas)

            # --- Input handling ---
            key = cv2.waitKey(1) & 0xFF

            if key in (ord("q"), 27):   # Q or ESC
                break
            elif key == ord("r"):
                analyzer.reset()
                print("Session reset.")
            elif key == ord("c"):
                switch_cam = True
            elif key == ord(" "):
                paused = not paused

            if mouse_state["clicked"]:
                mouse_state["clicked"] = False
                if btn_hover:
                    switch_cam = True
                elif pause_btn_hover:
                    paused = not paused

            # --- Switch source (cycles video → cam0 → cam1 → ...) ---
            if switch_cam:
                switch_cam = False
                source_pos = (source_pos + 1) % len(sources)
                cap.release()
                cap, video_mode, source_label = open_source(sources[source_pos])
                analyzer.reset()
                paused = False
                last_frame = None
                print(f"Switched to: {source_label}")
                _show_init_frame(WINDOW_NAME, PANEL_WIDTH + w, h,
                                 f"Switching to {source_label}...")

    cap.release()
    cv2.destroyAllWindows()


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Body Mobility Analysis")
    parser.add_argument(
        "--complexity", type=int, default=1, choices=[0, 1, 2],
        help="MediaPipe model complexity (0=fast, 1=balanced, 2=accurate)"
    )
    parser.add_argument(
        "--camera", type=int, default=1,
        help="Starting camera device index (default: 1)"
    )
    args = parser.parse_args()
    main(model_complexity=args.complexity, start_camera=args.camera)
