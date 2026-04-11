"""
Pose analysis stub — returns joint angles from video.

Currently hardcoded with demo data from FRONTEND_SPEC.md.
Replace get_joint_angles() body with real MediaPipe extraction when ready.
"""

from typing import Optional, Dict
from config import DEMO_USER_MOBILITY


def get_joint_angles(
    video_path: Optional[str] = None,
    use_demo: bool = True,
    provided: Optional[Dict[str, float]] = None,
) -> Dict[str, float]:
    """
    Return a dict of joint_key → measured ROM in degrees.

    Priority order:
      1. `provided` dict (caller passed explicit values, e.g. from real MediaPipe output)
      2. Demo data (DEMO_USER_MOBILITY from config) when use_demo=True
      3. Demo data as fallback even if use_demo=False (until real MediaPipe is wired)
    """
    if provided:
        return provided

    # TODO: replace with real MediaPipe extraction once pose.py is integrated
    # Real implementation will look roughly like:
    #   cap = cv2.VideoCapture(video_path)
    #   with mp.solutions.pose.Pose(...) as pose:
    #       angles = extract_angles_across_frames(cap, pose)
    #   return compute_rom(angles)

    return dict(DEMO_USER_MOBILITY)
