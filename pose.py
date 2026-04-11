"""
pose.py
Wraps MediaPipe BlazePose. Extracts per-frame landmark pixel coordinates
and per-landmark visibility scores from a video file.
"""

import cv2
import numpy as np
import mediapipe as mp
from pathlib import Path

from config import MIN_VISIBILITY


def extract_landmarks(video_path: str, model_complexity: int = 2) -> tuple[list[dict], dict]:
    """
    Process every frame of a video and return:
      - frames_data: list of per-frame dicts
            {
              "frame_idx": int,
              "landmarks": { landmark_idx: (px, py, visibility) },
              "width": int,
              "height": int,
            }
      - video_meta: { fps, width, height, total_frames }

    model_complexity: 0 (fast), 1 (balanced), 2 (accurate — recommended)
    """
    path = Path(video_path)
    if not path.exists():
        raise FileNotFoundError(f"Video not found: {video_path}")

    cap = cv2.VideoCapture(str(path))
    if not cap.isOpened():
        raise RuntimeError(f"Cannot open video: {video_path}")

    fps          = cap.get(cv2.CAP_PROP_FPS) or 30.0
    width        = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height       = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    video_meta = {
        "fps": fps,
        "width": width,
        "height": height,
        "total_frames": total_frames,
        "source_path": str(path),
    }

    mp_pose = mp.solutions.pose
    frames_data = []
    frame_idx = 0

    print(f"[pose] Processing {total_frames} frames at {fps:.1f} fps  ({width}x{height})")
    print(f"[pose] Model complexity: {model_complexity}  (2 = most accurate, slowest)")

    with mp_pose.Pose(
        static_image_mode=False,
        model_complexity=model_complexity,
        smooth_landmarks=True,
        enable_segmentation=False,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5,
    ) as pose:

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # MediaPipe needs RGB
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            rgb.flags.writeable = False
            results = pose.process(rgb)

            landmarks = {}
            if results.pose_landmarks:
                for idx, lm in enumerate(results.pose_landmarks.landmark):
                    px = int(lm.x * width)
                    py = int(lm.y * height)
                    landmarks[idx] = (px, py, lm.visibility)

            frames_data.append({
                "frame_idx": frame_idx,
                "landmarks": landmarks,
                "width": width,
                "height": height,
            })

            frame_idx += 1
            if frame_idx % 60 == 0:
                pct = frame_idx / max(total_frames, 1) * 100
                print(f"[pose]   {frame_idx}/{total_frames} frames ({pct:.0f}%)", end="\r")

    cap.release()
    print(f"\n[pose] Done. Extracted {len(frames_data)} frames.")
    return frames_data, video_meta
