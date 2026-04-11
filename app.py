"""
app.py
Gradio web interface for the mobility analyzer.
Wraps the full pipeline in a drag-and-drop upload UI.

Run:
  python app.py
  python app.py --share    ← get a public URL
"""

import argparse
import json
import os
import shutil
import tempfile
import time
from pathlib import Path

import gradio as gr

from pose         import extract_landmarks
from angles       import process_all_frames, compute_rom_summary, build_scores
from claude_client import call_claude
from report       import generate_html_report

# Import render function from main.py
from main import render_annotated_video, _placeholder_assessment


def analyze_video(video_file, sport_context: str, model_complexity: int, skip_claude: bool):
    """
    Gradio callback. Takes an uploaded video file path and returns:
      (annotated_video_path, report_html_string, rom_json_string, status_string)
    """
    if video_file is None:
        return None, "<p>Please upload a video first.</p>", "", "No video uploaded."

    t_start = time.time()
    logs    = []

    def log(msg):
        logs.append(msg)
        return "\n".join(logs)

    try:
        # Work in a temp directory
        tmpdir  = tempfile.mkdtemp(prefix="mobility_")
        stem    = Path(video_file).stem
        in_path = str(Path(tmpdir) / Path(video_file).name)
        shutil.copy(video_file, in_path)

        annotated_path   = str(Path(tmpdir) / f"{stem}_annotated.mp4")
        report_html_path = str(Path(tmpdir) / f"{stem}_report.html")

        # Step 1
        status = log("Extracting pose landmarks...")
        yield None, "<p>Processing…</p>", "", status

        frames_data, video_meta = extract_landmarks(in_path, model_complexity)
        status = log(f"  {len(frames_data)} frames extracted.")
        yield None, "<p>Processing…</p>", "", status

        # Step 2
        status = log("Computing joint angles...")
        yield None, "<p>Processing…</p>", "", status

        all_frame_angles = process_all_frames(frames_data)
        rom_summary      = compute_rom_summary(all_frame_angles)
        scores           = build_scores(rom_summary)

        rom_json_str = json.dumps({"rom_summary": rom_summary, "scores": scores}, indent=2)
        status = log("  Angles computed.")
        yield None, "<p>Processing…</p>", rom_json_str, status

        # Step 3
        status = log("Rendering annotated video...")
        yield None, "<p>Processing…</p>", rom_json_str, status

        render_annotated_video(
            video_path       = in_path,
            frames_data      = frames_data,
            all_frame_angles = all_frame_angles,
            video_meta       = video_meta,
            output_path      = annotated_path,
        )
        status = log("  Video rendered.")
        yield annotated_path, "<p>Processing…</p>", rom_json_str, status

        # Step 4
        if skip_claude:
            assessment = _placeholder_assessment(rom_summary, scores)
            status = log("  Skipped Claude API (offline mode).")
        else:
            status = log("Calling Claude API for assessment...")
            yield annotated_path, "<p>Processing…</p>", rom_json_str, status
            assessment = call_claude(rom_summary, scores, sport_context)
            status = log(f"  Overall score: {assessment.get('overall_score', '?')}/100")

        yield annotated_path, "<p>Processing…</p>", rom_json_str, status

        # Step 5
        status = log("Generating HTML report...")
        generate_html_report(
            rom_summary          = rom_summary,
            scores               = scores,
            assessment           = assessment,
            annotated_video_path = annotated_path,
            output_path          = report_html_path,
            sport_context        = sport_context,
        )

        html_content = Path(report_html_path).read_text(encoding="utf-8")

        elapsed = time.time() - t_start
        status = log(f"\nDone in {elapsed:.1f}s.")

        yield annotated_path, html_content, rom_json_str, status

    except Exception as e:
        import traceback
        err = traceback.format_exc()
        yield None, f"<pre style='color:red'>{err}</pre>", "", f"ERROR: {e}"


def build_ui():
    with gr.Blocks(title="Mobility Analyzer", theme=gr.themes.Soft()) as demo:

        gr.Markdown("## Athletic Mobility Analyzer")
        gr.Markdown(
            "Upload a video of yourself performing an athletic movement. "
            "The pipeline extracts your pose, measures joint angles across every frame, "
            "computes range-of-motion, and uses Claude to score your mobility and suggest exercises."
        )

        with gr.Row():
            with gr.Column(scale=1):
                video_input = gr.Video(label="Upload video (mp4, mov, avi)")
                context_box = gr.Textbox(
                    label="Movement context (optional)",
                    placeholder="e.g. squat, overhead press, running, lunge",
                )
                complexity_slider = gr.Slider(
                    minimum=0, maximum=2, step=1, value=2,
                    label="Model complexity (0=fast, 2=accurate)",
                )
                skip_claude_toggle = gr.Checkbox(
                    label="Skip Claude API (offline / no API key)",
                    value=False,
                )
                run_btn = gr.Button("Analyze", variant="primary")

            with gr.Column(scale=2):
                status_box  = gr.Textbox(label="Progress log", lines=8, interactive=False)
                video_out   = gr.Video(label="Annotated video")

        with gr.Accordion("HTML Report", open=True):
            report_html = gr.HTML(label="Mobility report")

        with gr.Accordion("Raw ROM JSON", open=False):
            rom_json_out = gr.Code(language="json", label="ROM data")

        run_btn.click(
            fn=analyze_video,
            inputs=[video_input, context_box, complexity_slider, skip_claude_toggle],
            outputs=[video_out, report_html, rom_json_out, status_box],
        )

    return demo


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--share", action="store_true", help="Generate public Gradio link")
    args = parser.parse_args()

    demo = build_ui()
    demo.launch(share=args.share)
