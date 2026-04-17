# SNAPBACK

**AI-powered return-to-sport mobility analyzer.**

SNAPBACK measures your joint range of motion against the specific demands of your sport and generates a personalised, progressive 4-week recovery plan using Claude.

---

## How it works

```
Select sport → Record movements → CV analysis → Gap analysis → Claude plan
```

1. **Sport selection** — choose from 8 sports (tennis, basketball, swimming, CrossFit, golf, volleyball, baseball, boxing)
2. **Movement recording** — perform 4 sport-specific movements on camera; the CV server runs MediaPipe pose estimation in real time and streams the annotated feed back to the browser
3. **Gap analysis** — measured ROM (shoulder, elbow, hip, knee — left/right/combined) is compared against clinical sport-demand thresholds; joints are flagged green / yellow / red
4. **3D hologram** — an interactive Three.js body map renders your joint status with sonar-ring markers and hover HUDs
5. **Claude plan** — Anthropic's Claude generates a 4-week progressive exercise plan personalised to your gaps, dominant hand, and weeks-to-return target; each week includes an "avoid" list

---

## Stack

| Layer | Technology |
|---|---|
| Frontend | React 18, Vite, React Router v6 |
| 3D visualisation | Three.js, @react-three/fiber, @react-three/postprocessing |
| Backend API | FastAPI, Uvicorn, Pydantic |
| CV pipeline | MediaPipe (Tasks API), OpenCV, NumPy |
| CV server | Flask (MJPEG stream) |
| AI | Anthropic Claude (`claude-opus-4-6`) |

---

## Project structure

```
SNAPBACK/
├── backend/                    FastAPI server
│   ├── main.py                 API endpoints (/api/sports, /api/analyze, /api/plan)
│   ├── config.py               Sport blueprints + clinical ROM baselines
│   ├── models.py               Pydantic models (CVResult, JointGap, WeekPlan …)
│   ├── gap_analysis.py         Compare session_rom vs sport requirements
│   ├── claude_client.py        Claude API — exercise plan generation
│   ├── pose.py                 CV result ingestion (real or demo)
│   └── requirements.txt
│
├── cv/                         Computer vision pipeline
│   ├── server.py               Flask MJPEG streaming server (port 5001)
│   ├── main.py                 CLI entry point
│   ├── pose_landmarker_full.task   MediaPipe model (download separately)
│   └── src/
│       ├── pose/               Landmark extraction & skeleton rendering
│       ├── analysis/           Joint angle math, ROM computation, scoring
│       └── ui/                 OpenCV overlay (HUD, metrics panel)
│
└── Frontend/                   React app
    └── src/
        ├── context/AppContext.jsx   Global state (sport, analysis, plan)
        ├── utils/api.js             Backend API calls + response transformers
        ├── components/
        │   ├── step1/              Sport selection
        │   ├── step2/              Movement recording (sport-specific cards + live stream)
        │   ├── step3/              3D hologram body map + analysis panel
        │   └── step4/              4-week exercise plan with week tabs
        └── data/                   Sport blueprints, demo mobility data
```

---

## Setup

### Prerequisites

- Python 3.10+
- Node.js 18+
- An [Anthropic API key](https://console.anthropic.com/)

### 1. Clone

```bash
git clone https://github.com/Srini-5303/SNAPBACK.git
cd SNAPBACK
```

### 2. Backend

```bash
cd backend
pip install -r requirements.txt

# Create .env file
echo "ANTHROPIC_API_KEY=sk-ant-..." > .env

# Verify the key works before starting all three servers
python test_api_key.py
```

### 3. CV server

```bash
cd cv
pip install -r requirements.txt

# Download the MediaPipe pose model (~9 MB)
curl -L -o pose_landmarker_full.task \
  "https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_full/float16/latest/pose_landmarker_full.task"
```

### 4. Frontend

```bash
cd Frontend
npm install

# Create .env.local (optional — defaults to http://localhost:8000)
echo "VITE_API_URL=http://localhost:8000" > .env.local
```

---

## Running

Open three terminals:

```bash
# Terminal 1 — Backend (port 8000)
cd backend
python -m uvicorn main:app --reload --port 8000

# Terminal 2 — CV server (port 5001)
cd cv
python server.py

# Terminal 3 — Frontend (port 5173)
cd Frontend
npm run dev
```

Open **http://localhost:5173**

> **Windows note:** The CV server uses DirectShow (`CAP_DSHOW`) instead of MSMF for camera detection — this prevents the 30-second hang that occurs when probing camera indices with the default Windows backend.

---

## API endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/sports` | List all supported sports |
| `GET` | `/api/sport-preview/{sport}` | 4 Claude-generated warm-up exercises for the sport |
| `POST` | `/api/analyze` | CV result → gap analysis (+ optional plan) |
| `POST` | `/api/plan` | Generate personalised Claude plan with user profile |
| `GET` | `/health` | Health check |

### POST /api/analyze

```json
{
  "sport": "tennis",
  "use_demo": true,
  "skip_plan": false,
  "cv_result": null,
  "user_profile": {
    "dominant_hand": "right",
    "weeks_to_return": 4,
    "weight_kg": 75
  }
}
```

Pass the CV server's `/stop` response as `cv_result` to use real recorded data instead of demo data.

### CV server endpoints (port 5001)

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/start` | Start pose analysis pipeline |
| `POST` | `/stop` | Stop pipeline + save session JSON to `cv/results/` |
| `POST` | `/pause` | Freeze last frame |
| `POST` | `/resume` | Resume pipeline |
| `POST` | `/switch` | Cycle camera source |
| `POST` | `/set-source` | Set phone IP webcam URL `{"url": "http://..."}` |
| `GET` | `/stream` | MJPEG stream (skeleton overlay + metrics panel) |
| `GET` | `/status` | `{running, paused, source}` |

---

## Scoring

ROM measurements are compared against sport-specific clinical thresholds derived from `cv/src/analysis/mobility.py` reference values:

| Joint | Clinical reference ROM |
|---|---|
| Shoulder | 140° |
| Elbow | 145° |
| Hip | 110° |
| Knee | 155° |

| % of required ROM | Status | Label |
|---|---|---|
| ≥ 80% | Green | Sport ready |
| 60–79% | Yellow | Needs work |
| < 60% | Red | Priority focus |

---

## Demo mode

If the CV server isn't running or no camera is available, the backend falls back to `DEMO_CV_RESULT` in `config.py` — a realistic synthetic session matching the `result_format.json` output shape. The Claude plan generation still runs using real API calls, provided `ANTHROPIC_API_KEY` is set. If the key is missing or invalid, the plan also falls back to a hardcoded default via `_fallback_plan()` in `claude_client.py`.

---

## Environment variables

| File | Variable | Description |
|---|---|---|
| `backend/.env` | `ANTHROPIC_API_KEY` | Anthropic API key |
| `Frontend/.env.local` | `VITE_API_URL` | Backend URL (default: `http://localhost:8000`) |
