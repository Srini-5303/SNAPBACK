# Mobility Analyzer

Analyze athletic movement from video. Extracts joint angles frame-by-frame,
computes range-of-motion (ROM), scores each joint against clinical norms,
and uses Claude to generate targeted mobility exercises.

## Output

- `output/[name]_annotated.mp4` — original video with stick figure, angle arcs, live HUD
- `output/[name]_report.html` — full mobility report with scores and exercises
- `output/[name]_rom.json` — raw ROM data for inspection

## Setup

```bash
# 1. Clone / copy this folder
cd mobility-analyzer

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Download a font (optional but recommended for crisp labels)
mkdir -p assets
curl -L "https://github.com/google/fonts/raw/main/apache/robotomono/RobotoMono%5Bwght%5D.ttf" \
     -o assets/RobotoMono-Regular.ttf

# 5. Set your Anthropic API key
export ANTHROPIC_API_KEY=sk-ant-...
```

## Usage

### Command-line pipeline

```bash
# Basic
python main.py --input my_video.mp4

# With context label (sent to Claude for better exercise targeting)
python main.py --input squat.mp4 --context "barbell back squat"

# Fast mode (less accurate pose, much faster)
python main.py --input squat.mp4 --complexity 0

# Offline mode (no API key needed — uses placeholder exercises)
python main.py --input squat.mp4 --skip-claude
```

### Web UI (Gradio)

```bash
python app.py           # opens at http://localhost:7860
python app.py --share   # generates a public URL
```

## How the overlay works

Each video frame goes through four drawing steps:

**1. Skeleton (OpenCV)**
MediaPipe gives 33 normalized (0–1) landmarks per frame. We scale them to
pixel coordinates and draw lines along `SKELETON_CONNECTIONS` in soft green.
Joint circles are drawn last, colored by ROM score (green/amber/red).

```
draw_skeleton(frame, landmarks, scores)
  → cv2.line() for each bone pair
  → cv2.circle() at each joint vertex
  → blended with cv2.addWeighted(alpha=0.8)
```

**2. Angle arcs (Pillow)**
For each tracked joint, we compute the angle at the vertex between its two
bone arms. `cv2.ellipse()` would work but Pillow gives anti-aliased arcs.

The arc is drawn between the two bone direction angles in image space.
The degree label is placed 38px from the vertex along the bisector of the
two bone vectors, with a dark background pill behind it.

```
draw_angle_annotation(pil_draw, pt_a, pt_v, pt_b, angle, score)
  → PIL arc between ang1 and ang2
  → label at vertex + 38px toward bisector
```

**3. Live HUD panel (OpenCV + Pillow)**
Top-left corner: semi-transparent dark panel with a progress bar and a row
per joint showing its name, running max ROM, and current score. The running
max updates every frame — so the HUD shows "best seen so far", which is the
actual mobility metric.

```
draw_hud(frame, tracker, frame_idx, total_frames)
  → cv2.rectangle() + addWeighted for the panel background
  → Pillow text for labels (anti-aliased at 13px)
```

**4. Why Pillow for text?**
`cv2.putText()` uses a bitmap font — it looks blocky at anything under 24px.
Pillow's `ImageDraw.text()` with a TrueType font gives clean, readable labels
at 13px. The pipeline converts BGR → RGB → PIL → draw → RGB → BGR per frame.

## Camera angle tips

| Movement | Best camera position |
|---|---|
| Squat, lunge, deadlift | Strictly side-on (90° to movement) |
| Overhead press | Side-on or 45° |
| Running gait | Side-on |
| Shoulder circles, arm raises | Frontal (facing camera) |

A side-on view is the single most important setup decision. Frontal views
make hip and knee angles nearly uncomputable from 2D landmarks.

## Scoring

```
score = min(100, int(observed_range / clinical_norm × 100))
```

| Score | Status | Exercise tier |
|---|---|---|
| 0–39 | Restricted | Beginner / therapeutic |
| 40–69 | Moderate | Intermediate |
| 70–100 | Good | Maintenance / advanced |

Clinical norms are defined in `config.py` and can be adjusted.

## Project structure

```
mobility-analyzer/
├── main.py            ← CLI entry point
├── app.py             ← Gradio web UI
├── config.py          ← all constants (joints, norms, colors)
├── pose.py            ← MediaPipe landmark extraction
├── angles.py          ← joint angle math + ROM computation
├── overlay.py         ← OpenCV + Pillow drawing
├── claude_client.py   ← Anthropic API integration
├── report.py          ← HTML report generator
├── requirements.txt
└── assets/
    └── RobotoMono-Regular.ttf   ← optional, improves text quality
```
