"""
MediaPipe Pose wrapper — uses the Tasks API (mediapipe >= 0.10).
Converts BGR frames to RGB, runs inference, and returns a clean PoseResult.
"""

from __future__ import annotations

import os
import time
from dataclasses import dataclass
from typing import Optional

import cv2
import mediapipe as mp
import numpy as np
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision as mp_vision

# Default model path (sits next to main.py at project root)
_DEFAULT_MODEL = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "pose_landmarker_full.task",
)


@dataclass
class PoseResult:
    """Pose landmarks for a single frame."""
    landmarks: np.ndarray    # shape (33, 3): normalised x, y, z
    visibility: np.ndarray   # shape (33,):   per-landmark presence score [0,1]
    raw_result: object       # original PoseLandmarkerResult


class PoseEstimator:
    """
    Wraps mediapipe PoseLandmarker (Tasks API) for per-frame inference.

    Usage:
        with PoseEstimator() as est:
            result = est.process(bgr_frame)
    """

    def __init__(
        self,
        model_complexity: int = 1,          # 0=lite, 1=full, 2=heavy → model file
        min_detection_confidence: float = 0.5,
        min_tracking_confidence: float = 0.5,
        model_path: Optional[str] = None,
    ) -> None:
        if model_path is None:
            model_path = _DEFAULT_MODEL

        if not os.path.exists(model_path):
            raise FileNotFoundError(
                f"MediaPipe model not found at: {model_path}\n"
                "Run the download snippet in the README to fetch it."
            )

        base_options = mp_python.BaseOptions(model_asset_path=model_path)
        options = mp_vision.PoseLandmarkerOptions(
            base_options=base_options,
            running_mode=mp_vision.RunningMode.VIDEO,
            num_poses=1,
            min_pose_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence,
        )
        self._landmarker = mp_vision.PoseLandmarker.create_from_options(options)
        self._start_ms = int(time.perf_counter() * 1000)

    def process(self, bgr_frame: np.ndarray) -> Optional[PoseResult]:
        """
        Run pose estimation on a BGR frame.
        Returns None if no person is detected.
        """
        # Convert BGR → RGB
        rgb = cv2.cvtColor(bgr_frame, cv2.COLOR_BGR2RGB)

        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)

        # VIDEO mode requires a monotonically increasing timestamp in ms
        timestamp_ms = int(time.perf_counter() * 1000) - self._start_ms
        mp_result = self._landmarker.detect_for_video(mp_image, timestamp_ms)

        if not mp_result.pose_landmarks:
            return None

        # Use first detected person
        lms = mp_result.pose_landmarks[0]      # list of NormalizedLandmark
        world = mp_result.pose_world_landmarks  # 3-D world coords (metres)

        landmarks  = np.array([[lm.x, lm.y, lm.z] for lm in lms],   dtype=np.float32)

        # presence is the Tasks-API equivalent of visibility
        visibility = np.array([lm.presence if lm.presence is not None else lm.visibility
                                for lm in lms], dtype=np.float32)

        return PoseResult(
            landmarks=landmarks,
            visibility=visibility,
            raw_result=mp_result,
        )

    def close(self) -> None:
        self._landmarker.close()

    def __enter__(self) -> "PoseEstimator":
        return self

    def __exit__(self, *args) -> None:
        self.close()
