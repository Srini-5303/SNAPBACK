"""
Pose analysis — returns a CVResult-shaped dict from a recording session.

Currently returns demo data matching the exact output of cv/server.py.
Replace get_cv_result() with a call to the live CV server when available.
"""

from typing import Optional, Dict, Any
from config import DEMO_CV_RESULT


def get_cv_result(
    use_demo: bool = True,
    provided: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Return a dict matching the CVResult shape (cv/server.py output).

    Priority:
      1. `provided` — caller passed a real CV result (from /api/analyze request body)
      2. Demo data from config when use_demo=True or no real data available
    """
    if provided:
        return provided

    # TODO: call the live CV server (http://localhost:5001) once it's running
    # and capture its saved JSON result from the cv/results/ directory.
    return dict(DEMO_CV_RESULT)
