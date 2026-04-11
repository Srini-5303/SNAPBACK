# ReMotion — Frontend Implementation Plan (v2)

## Context
Building the complete React frontend for **ReMotion** from scratch inside `/Frontend/` (currently empty). Backend is Python/Gradio+MediaPipe — no REST API yet — so the frontend uses hardcoded demo data. Two key updates from v1: **React Router** for deep-linkable navigation, and **Iron Man hologram** aesthetic for the body map (the hero screen).

---

## Tech Stack

| Concern | Choice | Reason |
|---|---|---|
| Build tool | **Vite + React 18 (JSX)** | Fastest HMR, instant start |
| Routing | **react-router-dom v6** | User must navigate back to `/analysis` and `/plan` — URL-based navigation |
| State sharing | **React Context (`AppContext`)** | Wraps the router, holds sport/gapAnalysis/exercisePlan across routes |
| Styling | **Plain CSS + CSS Custom Properties** | SVG animations, `stroke-dasharray`, `filter`, `@keyframes` — Tailwind can't do this |
| Icons | **lucide-react** | Tree-shakeable SVG icons |
| API | **None** | Exercise plan is hardcoded per sport — backend will generate it later |
| Animation | **CSS `@keyframes` only** | All animations are bespoke; no Framer Motion needed |

---

## Routes

| Path | Component | Guard |
|---|---|---|
| `/` | `SportSelection` | None (entry point) |
| `/record` | `MovementRecording` | Redirect to `/` if no sport selected |
| `/analysis` | `BodyMapResults` | Redirect to `/` if no sport selected |
| `/plan` | `ExercisePlan` | Redirect to `/analysis` if no exercise plan yet |

Navigation is programmatic via `useNavigate()`. The ProgressStepper shows which step the current path corresponds to.

---

## Folder Structure

```
Frontend/
├── .env.local                          ← (empty for now, ready for backend URL later)
├── index.html                          ← Google Fonts: Outfit + DM Sans
├── package.json
├── vite.config.js
└── src/
    ├── main.jsx                        ← ReactDOM.createRoot + BrowserRouter
    ├── App.jsx                         ← AppContext provider + <Routes> definition
    ├── App.css                         ← CSS custom properties, resets, shared keyframes
    │
    ├── context/
    │   └── AppContext.jsx              ← createContext: selectedSport, gapAnalysis, exercisePlan, setters
    │
    ├── data/
    │   ├── sportBlueprints.js          ← All 10 sports with ROM requirements
    │   ├── demoUserMobility.js         ← Simulated MediaPipe angles
    │   └── demoExercisePlan.js         ← Hardcoded 4-week plans per sport
    │
    ├── utils/
    │   └── gapAnalysis.js              ← computeGapAnalysis(sport, userMobility) → { readinessScore, joints[] }
    │
    └── components/
        ├── layout/
        │   ├── Header.jsx + .css       ← "Re" (teal) + "Motion" (white) wordmark
        │   └── ProgressStepper.jsx + .css  ← 4 steps, reads current route to highlight active
        │
        ├── step1/
        │   ├── SportSelection.jsx + .css
        │   └── SportCard.jsx + .css
        │
        ├── step2/
        │   ├── MovementRecording.jsx + .css
        │   ├── MovementCard.jsx + .css
        │   └── StickFigures.jsx        ← 4 inline SVG stick figures
        │
        ├── step3/
        │   ├── BodyMapResults.jsx + .css     ← Split layout + sport switcher
        │   ├── HologramBodyMap.jsx + .css    ← Iron Man hologram
        │   ├── HologramGrid.jsx + .css       ← Background perspective grid
        │   ├── JointHUD.jsx + .css           ← Floating data readout per joint
        │   ├── ReadinessRing.jsx + .css      ← Animated circular SVG ring
        │   ├── AnalysisPanel.jsx + .css      ← Scrollable sorted joint list
        │   ├── JointAssessmentRow.jsx + .css ← Mini bar chart + severity badge
        │   └── ScanAnimation.jsx + .css      ← Loading skeleton with scan line
        │
        └── step4/
            ├── ExercisePlan.jsx + .css
            ├── WeekTabs.jsx + .css
            └── ExerciseCard.jsx + .css       ← Accordion "Why this exercise"
```

---

## Iron Man Hologram Body Map — Full Spec

The visual goal: a glowing teal wireframe human figure floating in a dark space, like Tony Stark's suit HUD.

### Layer Stack (bottom to top)
1. **HologramGrid** — subtle perspective grid behind the figure, cyan lines at low opacity
2. **Body wireframe** — stroke-only SVG paths (no fills), `stroke: #00E5CC`, `stroke-width: 1.5`, `filter: drop-shadow(0 0 4px #00E5CC) drop-shadow(0 0 10px rgba(0,229,204,0.4))`
3. **Inner body fill** — same paths with `fill: rgba(0,229,204,0.03)` for interior glow depth
4. **Joint markers** — diamond `<polygon>` shapes at each of 16 joint positions, color-coded by severity
5. **Priority joint pulse rings** — `@keyframes pulse-ring` expands radius 0→24 and fades opacity 1→0, looping (sonar ping effect)
6. **Scan line** — cyan line sweeping top-to-bottom every 4 seconds continuously
7. **Joint HUD overlays** — on hover: semi-transparent dark panel with teal border, monospace font, angle data

### CSS Keyframes
```css
@keyframes hologram-breathe {
  0%, 100% { filter: drop-shadow(0 0 4px #00E5CC) drop-shadow(0 0 10px rgba(0,229,204,0.4)); }
  50%       { filter: drop-shadow(0 0 8px #00E5CC) drop-shadow(0 0 20px rgba(0,229,204,0.6)); }
}

@keyframes pulse-ring {
  0%   { r: 8; opacity: 0.8; }
  100% { r: 24; opacity: 0; }
}

@keyframes scan-sweep {
  0%   { transform: translateY(-100%); opacity: 0; }
  10%  { opacity: 0.4; }
  90%  { opacity: 0.4; }
  100% { transform: translateY(450px); opacity: 0; }
}
```

### Mouse Parallax
`useRef` on container + `onMouseMove` → `transform: perspective(1200px) rotateY(Xdeg) rotateX(Ydeg)`. Max tilt: ±8 degrees.

### Sport Switcher (Hackathon Wow Moment)
Sport pills below the body map. Clicking re-runs `computeGapAnalysis(newSport, demoUserMobility)` → instantly recolors all 16 joint markers. Joint color transitions animate over 400ms.

### Severity Color Mapping
| Severity | Gap | Color |
|---|---|---|
| Good | < 10% | `#00E5CC` teal |
| Moderate | 10–30% | `#FFBE0B` amber |
| Priority | > 30% | `#FF4757` red + sonar ring |

---

## Implementation Order (8 Phases)

### Phase 1 — Scaffold
1. `npm create vite@latest . -- --template react` in `Frontend/`
2. Install: `react-router-dom`, `lucide-react`
3. `index.html` with Google Fonts: `Outfit:wght@400;600;700;800` + `DM Sans:wght@400;500`
4. `App.css` — all CSS custom properties, global reset, shared `@keyframes`

### Phase 2 — Data + Utils
5. `sportBlueprints.js` — all 10 sports with ROM requirements
6. `demoUserMobility.js` — simulated MediaPipe angles
7. `demoExercisePlan.js` — hardcoded 4-week plans per sport
8. `gapAnalysis.js` — `computeGapAnalysis()`, severity thresholds, readiness score
9. `AppContext.jsx` — `selectedSport`, `userMobility`, `gapAnalysis`, `exercisePlan`, setters

### Phase 3 — Shell + Routing
10. `main.jsx` — wrap App in `<BrowserRouter>`
11. `App.jsx` — `<AppContext.Provider>` + `<Routes>` with 4 paths + route guards
12. `Header.jsx` — wordmark ("Re" teal, "Motion" white)
13. `ProgressStepper.jsx` — reads `useLocation()` to highlight active step

### Phase 4 — Step 1: Sport Selection
14. `SportCard.jsx` — hover lift + teal glow border on selected
15. `SportSelection.jsx` — 3-col responsive grid, Continue navigates to `/record`

### Phase 5 — Step 2: Movement Recording
16. `StickFigures.jsx` — 4 hand-crafted inline SVGs (120×160 viewBox)
17. `MovementCard.jsx` + `MovementRecording.jsx`
18. "Use Demo Video" → navigates to `/analysis`

### Phase 6 — Step 3: Hologram Body Map
19. `HologramGrid.jsx` — perspective SVG grid background
20. `HologramBodyMap.jsx` — wireframe SVG silhouette + all hologram layers
21. 16 joint diamond markers, color-coded, sonar rings on priority joints
22. Continuous scan line sweep `@keyframes`
23. Mouse parallax on `onMouseMove`
24. `JointHUD.jsx` — floating data overlay on hover
25. `ReadinessRing.jsx` — `stroke-dashoffset` animation + count-up number
26. `JointAssessmentRow.jsx` — dual-bar mini chart
27. `AnalysisPanel.jsx` — sorted joint list + "Generate My Return Plan →" button
28. `BodyMapResults.jsx` — split layout + sport switcher
29. `ScanAnimation.jsx` — 2.5s loading state before map reveals

### Phase 7 — Step 4: Exercise Plan
30. `WeekTabs.jsx` — Week 1–4 selector with active underline
31. `ExerciseCard.jsx` — accordion "Why this exercise" section
32. `ExercisePlan.jsx` — consumes hardcoded plan for selected sport
33. "Generate Plan" button on `/analysis` navigates to `/plan` — no API call

### Phase 8 — Polish
34. Mobile: step 3 stacks vertically at <768px
35. All hovers use `cubic-bezier(0.16, 1, 0.3, 1)` easing
36. Route transitions: fade in on enter via CSS class

---

## Critical Files

| File | Why |
|---|---|
| `src/context/AppContext.jsx` | All cross-route state lives here |
| `src/utils/gapAnalysis.js` | Everything in Steps 3 & 4 depends on this |
| `src/components/step3/HologramBodyMap.jsx` | Hero component — most visual complexity |
| `src/App.css` | CSS tokens + keyframes referenced everywhere |

---

## Verification Checklist

1. `npm run dev` → app loads at `localhost:5173`
2. Navigate to `/analysis` directly → redirected to `/`
3. Select sport → `/record` → "Use Demo Video" → `/analysis`
4. 2.5s scan animation → hologram body map appears, joints colored, sonar rings on red joints
5. Hover joint → HUD overlay with angle data appears
6. Move mouse over map → subtle 3D tilt on hologram
7. Click sport switcher → all joint colors update in 400ms
8. "Generate Plan" → navigates to `/plan` with hardcoded exercise cards
9. Browser back from `/plan` → returns to `/analysis` with map intact
10. Resize to 375px → map stacks above panel, fully usable
