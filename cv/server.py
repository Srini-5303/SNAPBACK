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

import threading
import time

import cv2
import numpy as np
from flask import Flask, Response, jsonify
from flask_cors import CORS

from src.pose.estimator import PoseEstimator
from src.pose.skeleton import SkeletonRenderer
from src.analysis.angles import extract_angles
from src.analysis.mobility import MobilityAnalyzer, build_joint_colors
from src.ui.overlay import OverlayRenderer, PANEL_WIDTH

VIDEO_PATH = r"C:\Users\aareg\Downloads\WhatsApp Video 2026-04-11 at 12.02.30 PM.mp4"
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
    """Return ["video", 0, 1, …] depending on what's available."""
    cams: list[int] = []
    for i in range(MAX_CAM_PROBE):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            cams.append(i)
        cap.release()
    return (["video"] if VIDEO_PATH else []) + cams


def _open_source(src) -> tuple[cv2.VideoCapture, bool, str]:
    """Open a source, return (cap, is_video_mode, label)."""
    if src == "video":
        return cv2.VideoCapture(VIDEO_PATH), True, "Video"
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
    return jsonify({'status': 'stopped'})


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
