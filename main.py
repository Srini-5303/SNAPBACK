"""
main.py
Full pipeline orchestrator.

Usage:
  python main.py --input my_squat.mp4
  python main.py --input my_squat.mp4 --context "barbell squat" --complexity 1
  python main.py --input my_squat.mp4 --skip-claude   # skip API call, offline mode

Steps:
  1. Extract pose landmarks (MediaPipe)
  2. Compute per-frame joint angles
  3. Render annotated video (skeleton + angle labels + HUD)
  4. Build ROM summary
  5. Call Claude API for scores + exercises
  6. Generate HTML report
"""

import argparse
import json
import time
from pathlib import Path

import cv2
import numpy as np

from pose         import extract_landmarks
from angles       import (process_all_frames, compute_rom_summary,
                           build_scores, RomTracker)
from overlay      import render_frame
from claude_client import call_claude
from report       import generate_html_report


def parse_args():
    p = argparse.ArgumentParser(description="Athletic mobility analyzer")
    p.add_argument("--input",      required=True, help="Path to input video (mp4, mov, avi)")
    p.add_argument("--output-dir", default="output", help="Output directory (default: ./output)")
    p.add_argument("--context",    default="", help="Movement context e.g. 'squat' or 'overhead press'")
    p.add_argument("--complexity", type=int, default=2, choices=[0, 1, 2],
                   help="MediaPipe model complexity: 0=fast, 1=balanced, 2=accurate (default: 2)")
    p.add_argument("--skip-claude", action="store_true",
                   help="Skip Claude API call (useful for offline testing)")
    return p.parse_args()


def render_annotated_video(
    video_path: str,
    frames_data: list,
    all_frame_angles: list,
    video_meta: dict,
    output_path: str,
) -> None:
    """
    Re-read the original video frame-by-frame, apply overlays, write output.

    We re-read rather than storing all frames in RAM — a 1-min 1080p video
    at 30fps is ~5 GB uncompressed. Re-reading keeps memory usage flat.
    """
    cap = cv2.VideoCapture(video_path)

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(
        output_path,
        fourcc,
        video_meta["fps"],
        (video_meta["width"], video_meta["height"]),
    )

    tracker = RomTracker()
    total   = video_meta["total_frames"]

    # Pre-compute final scores from complete ROM (used for joint-circle coloring)
    rom_summary = compute_rom_summary(all_frame_angles)
    scores      = build_scores(rom_summary)

    print(f"[render] Writing annotated video → {output_path}")
    frame_idx = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        fa = all_frame_angles[frame_idx] if frame_idx < len(all_frame_angles) else {}
        fd = frames_data[frame_idx]      if frame_idx < len(frames_data)      else {}

        # Update live tracker with this frame's angles
        tracker.update(fa.get("angles", {}))

        frame = render_frame(
            frame         = frame,
            frame_data    = fd,
            frame_angles  = fa.get("angles", {}),
            tracker       = tracker,
            scores        = scores,
            frame_idx     = frame_idx,
            total_frames  = total,
        )

        writer.write(frame)
        frame_idx += 1

        if frame_idx % 30 == 0:
            pct = frame_idx / max(total, 1) * 100
            print(f"[render]   {frame_idx}/{total} frames ({pct:.0f}%)", end="\r")

    cap.release()
    writer.release()
    print(f"\n[render] Done.")


def main():
    args     = parse_args()
    t_start  = time.time()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"ERROR: Input file not found: {input_path}")
        raise SystemExit(1)

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    stem             = input_path.stem
    annotated_path   = str(output_dir / f"{stem}_annotated.mp4")
    report_html_path = str(output_dir / f"{stem}_report.html")
    rom_json_path    = str(output_dir / f"{stem}_rom.json")

    print(f"\n{'='*55}")
    print(f"  Mobility Analyzer")
    print(f"  Input:   {input_path}")
    print(f"  Context: {args.context or 'not specified'}")
    print(f"{'='*55}\n")

    # ── Step 1: Pose extraction ────────────────────────────────────────────────
    print("STEP 1/5  Extracting pose landmarks...")
    frames_data, video_meta = extract_landmarks(str(input_path), args.complexity)

    # ── Step 2: Angle computation ──────────────────────────────────────────────
    print("\nSTEP 2/5  Computing joint angles...")
    all_frame_angles = process_all_frames(frames_data)
    rom_summary      = compute_rom_summary(all_frame_angles)
    scores           = build_scores(rom_summary)

    # Save ROM JSON for inspection
    with open(rom_json_path, "w") as f:
        json.dump({"rom_summary": rom_summary, "scores": scores}, f, indent=2)
    print(f"[angles] ROM summary saved → {rom_json_path}")

    # Quick console summary
    print("\n  Joint ROM Summary:")
    print(f"  {'Joint':<14} {'Range':>7}  {'Score':>6}")
    print(f"  {'-'*32}")
    for joint, data in rom_summary.items():
        from config import JOINT_DISPLAY_NAMES
        name  = JOINT_DISPLAY_NAMES[joint]
        rng   = data["range"]
        score = scores[joint]
        bar   = "█" * (score // 10) + "░" * (10 - score // 10)
        print(f"  {name:<14} {rng:>6.1f}°  {score:>4}/100  {bar}")

    # ── Step 3: Render annotated video ────────────────────────────────────────
    print("\nSTEP 3/5  Rendering annotated video...")
    render_annotated_video(
        video_path        = str(input_path),
        frames_data       = frames_data,
        all_frame_angles  = all_frame_angles,
        video_meta        = video_meta,
        output_path       = annotated_path,
    )

    # ── Step 4: Claude API ────────────────────────────────────────────────────
    print("\nSTEP 4/5  Calling Claude API...")
    if args.skip_claude:
        print("[claude] --skip-claude flag set. Using placeholder assessment.")
        assessment = _placeholder_assessment(rom_summary, scores)
    else:
        assessment = call_claude(rom_summary, scores, args.context)

    # ── Step 5: HTML report ───────────────────────────────────────────────────
    print("\nSTEP 5/5  Generating HTML report...")
    generate_html_report(
        rom_summary          = rom_summary,
        scores               = scores,
        assessment           = assessment,
        annotated_video_path = annotated_path,
        output_path          = report_html_path,
        sport_context        = args.context,
    )

    elapsed = time.time() - t_start
    print(f"\n{'='*55}")
    print(f"  DONE in {elapsed:.1f}s")
    print(f"  Annotated video → {annotated_path}")
    print(f"  HTML report     → {report_html_path}")
    print(f"  ROM data        → {rom_json_path}")
    print(f"{'='*55}\n")


def _placeholder_assessment(rom_summary: dict, scores: dict) -> dict:
    """Offline fallback — no API call."""
    from config import JOINT_DISPLAY_NAMES
    joints = {}
    for joint, data in rom_summary.items():
        score = scores[joint]
        tier  = "beginner" if score < 40 else "intermediate" if score < 70 else "advanced"
        joints[joint] = {
            "score":      score,
            "assessment": f"Observed range: {data['range']:.1f}°. Score: {score}/100.",
            "exercises": [
                {
                    "name":        f"{JOINT_DISPLAY_NAMES[joint]} mobility drill",
                    "description": "Perform controlled circles through full available range.",
                    "sets_reps":   "2 sets × 10 reps",
                    "tier":        tier,
                }
            ],
        }
    overall = int(sum(scores.values()) / max(len(scores), 1))
    return {
        "overall_score":   overall,
        "overall_summary": f"Average mobility score: {overall}/100. (Offline mode — no Claude assessment.)",
        "joints":          joints,
    }


if __name__ == "__main__":
    main()
