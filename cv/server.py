"""
Flask MJPEG streaming server for body mobility analysis.

Run:
    python server.py

Endpoints:
    GET  /stream  — MJPEG stream (skeleton overlay + metrics panel)
    POST /start   — start the analysis pipeline
    POST /stop    — stop the pipeline
    POST /pause   — pause the pipeline (freeze last frame)
    POST /resume  — resume the pipeline
    POST /switch  — cycle to the next source (video → cam0 → cam1 → …)
    GET  /status  — {"running", "paused", "source"}
"""

from __future__ import annotations

import json
import threading
import time
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Optional

import cv2
import numpy as np
from flask import Flask, Response, jsonify
from flask_cors import CORS

from src.pose.estimator import PoseEstimator
from src.pose.skeleton import SkeletonRenderer
from src.analysis.angles import extract_angles
from src.analysis.mobility import MobilityAnalyzer, MobilityStatus, build_joint_colors
from src.ui.overlay import OverlayRenderer, PANEL_WIDTH

RESULTS_DIR = Path(__file__).parent / "results"

VIDEO_PATH  = None  # set to a file path to use a video instead of live camera
PHONE_URL   = None  # e.g. "http://192.168.1.42:8080/video" for IP Webcam app
MAX_CAM_PROBE = 4

app = Flask(__name__)
CORS(app)

# ---------------------------------------------------------------------------
# Shared state
# ---------------------------------------------------------------------------

_frame_lock    = threading.Lock()
_latest_frame: bytes | None = None

_running  = False
_paused   = False

_status_lock  = threading.Lock()
_last_status: Optional[MobilityStatus] = None
_session_start: Optional[float] = None

_source_lock      = threading.Lock()
_source_pos       = 0          # index into _sources list
_sources: list    = []         # built once when pipeline starts
_switch_requested = False
_current_label    = "—"

_pipeline_thread: threading.Thread | None = None


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _probe_sources() -> list:
    """Return ordered list of available sources.
    Priority: phone URL > cam 1 > cam 0 > … > video file."""
    available: set[int] = set()
    for i in range(MAX_CAM_PROBE):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            available.add(i)
        cap.release()
    # Fixed preferred order: 1, 0, then any remaining cams ascending
    ordered = [i for i in [1, 0] if i in available]
    ordered += sorted(i for i in available if i not in [1, 0])
    if VIDEO_PATH:
        ordered.append("video")
    if PHONE_URL:
        ordered.insert(0, "phone")   # phone takes priority when configured
    return ordered


def _open_source(src) -> tuple[cv2.VideoCapture, bool, str]:
    """Open a source, return (cap, is_video_mode, label)."""
    if src == "video":
        return cv2.VideoCapture(VIDEO_PATH), True, "Video"
    if src == "phone":
        cap = cv2.VideoCapture(PHONE_URL)
        return cap, False, f"Phone ({PHONE_URL})"
    cap = cv2.VideoCapture(src)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH,  1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    cap.set(cv2.CAP_PROP_FPS,          30)
    return cap, False, f"Cam {src}"


# ---------------------------------------------------------------------------
# Analysis pipeline
# ---------------------------------------------------------------------------

def _analysis_loop() -> None:
    global _latest_frame, _running, _paused
    global _sources, _source_pos, _switch_requested, _current_label
    global _last_status, _session_start

    _session_start = time.time()
    _sources = _probe_sources()
    if not _sources:
        print("[server] ERROR: no video source found")
        _running = False
        return

    print(f"[server] sources: {_sources}")

    with PoseEstimator() as estimator:
        skeleton = SkeletonRenderer()
        overlay  = OverlayRenderer()

        while _running:
            # --- Open current source ---
            with _source_lock:
                src = _sources[_source_pos % len(_sources)]
                _switch_requested = False

            cap, video_mode, label = _open_source(src)
            _current_label = label

            if not cap.isOpened():
                print(f"[server] could not open source: {src}")
                cap.release()
                time.sleep(0.5)
                continue

            print(f"[server] opened: {label}")
            analyzer    = MobilityAnalyzer()   # reset ROM tracking on switch
            prev_time   = time.perf_counter()
            last_angles = None
            last_status = None

            # --- Inner loop for this source ---
            while _running and not _switch_requested:
                if _paused:
                    time.sleep(0.033)
                    continue

                ret, frame = cap.read()
                if not ret:
                    if video_mode:
                        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                        continue
                    else:
                        break   # camera read failed; fall through to reopen

                h, w = frame.shape[:2]

                pose_result = estimator.process(frame)
                if pose_result:
                    angles      = extract_angles(pose_result)
                    status      = analyzer.update(angles)
                    last_angles = angles
                    last_status = status
                    with _status_lock:
                        _last_status = status
                    joint_colors = build_joint_colors(status) if status else {}
                    frame = skeleton.render(
                        frame, pose_result, joint_colors, frame_shape=(h, w))

                now      = time.perf_counter()
                fps      = 1.0 / max(now - prev_time, 1e-9)
                prev_time = now

                canvas = np.zeros((h, PANEL_WIDTH + w, 3), dtype=np.uint8)
                canvas[:, PANEL_WIDTH:] = frame
                overlay.render(canvas, last_angles, last_status, fps,
                               camera_label=label)

                _, jpeg = cv2.imencode('.jpg', canvas,
                                       [cv2.IMWRITE_JPEG_QUALITY, 80])
                with _frame_lock:
                    _latest_frame = jpeg.tobytes()

            cap.release()

    print("[server] pipeline stopped")


# ---------------------------------------------------------------------------
# MJPEG generator
# ---------------------------------------------------------------------------

def _generate_stream():
    while True:
        with _frame_lock:
            frame = _latest_frame
        if frame is not None:
            yield (
                b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n'
            )
        time.sleep(0.033)


# ---------------------------------------------------------------------------
# Session save
# ---------------------------------------------------------------------------

def _save_session() -> Optional[dict]:
    """Serialize the last MobilityStatus to a timestamped JSON file.
    Returns the saved data dict, or None if there's nothing to save."""
    with _status_lock:
        status = _last_status

    if status is None:
        return None

    duration = round(time.time() - _session_start, 1) if _session_start else 0

    # dataclasses.asdict handles nested dataclasses (JointScore, JointStatus)
    data = {
        "timestamp":    datetime.now().isoformat(timespec="seconds"),
        "duration_sec": duration,
        "overall_score": round(status.overall_score, 1),
        "joint_scores": {
            pair: {
                "left":     round(js.left, 1),
                "right":    round(js.right, 1),
                "combined": round(js.combined, 1),
            }
            for pair, js in status.joint_scores.items()
        },
        "min_angles":       {k: round(v, 1) for k, v in status.min_angles.items()},
        "max_angles":       {k: round(v, 1) for k, v in status.max_angles.items()},
        "session_rom":      {k: round(v, 1) for k, v in status.session_rom.items()},
        "asymmetry_scores": {k: round(v, 1) for k, v in status.asymmetry_scores.items()},
    }

    RESULTS_DIR.mkdir(exist_ok=True)
    filename = RESULTS_DIR / f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    filename.write_text(json.dumps(data, indent=2))
    print(f"[server] session saved → {filename}")
    return data


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route('/stream')
def stream():
    return Response(_generate_stream(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/start', methods=['POST'])
def start():
    global _running, _pipeline_thread
    if not _running:
        _running = True
        _pipeline_thread = threading.Thread(target=_analysis_loop, daemon=True)
        _pipeline_thread.start()
        print("[server] pipeline started")
    return jsonify({'status': 'running'})


@app.route('/stop', methods=['POST'])
def stop():
    global _running
    _running = False
    saved = _save_session()
    return jsonify({'status': 'stopped', 'session': saved})


@app.route('/pause', methods=['POST'])
def pause():
    global _paused
    _paused = True
    return jsonify({'status': 'paused'})


@app.route('/resume', methods=['POST'])
def resume():
    global _paused
    _paused = False
    return jsonify({'status': 'running'})


@app.route('/switch', methods=['POST'])
def switch():
    global _source_pos, _switch_requested
    with _source_lock:
        _source_pos += 1
        _switch_requested = True
    print(f"[server] switching to source index {_source_pos}")
    return jsonify({'status': 'switching'})


@app.route('/set-source', methods=['POST'])
def set_source():
    """Set a custom URL source (e.g. phone IP Webcam stream).

    Body: { "url": "http://192.168.1.42:8080/video" }
    Clears the URL if body is {} or {"url": null}.
    """
    from flask import request as req
    global PHONE_URL, _source_pos, _switch_requested, _sources
    data = req.get_json(silent=True) or {}
    PHONE_URL = data.get('url') or None
    # Rebuild source list so new source takes effect on next /start or switch
    with _source_lock:
        _sources = _probe_sources()
        _source_pos = 0
        _switch_requested = True
    label = PHONE_URL or "cleared"
    print(f"[server] phone URL set to: {label}")
    return jsonify({'status': 'ok', 'phone_url': PHONE_URL, 'sources': _sources})


@app.route('/status')
def status():
    return jsonify({
        'running': _running,
        'paused':  _paused,
        'source':  _current_label,
    })


# ---------------------------------------------------------------------------

if __name__ == '__main__':
    print("[server] starting on http://localhost:5001")
    app.run(host='0.0.0.0', port=5001, threaded=True)
