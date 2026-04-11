# ReMotion — Frontend Specification for Claude Code

## What to Build
A single-page React web app (`.jsx` artifact) called **ReMotion** — an AI-powered sport-specific mobility gap analyzer. The user selects their sport, uploads/records a video of themselves moving, and gets a visual body map showing which joints need work for their specific sport, plus a personalized return-to-sport plan.

## Design Direction
**Aesthetic: Athletic-Premium meets Medical Precision.** Think Nike Training Club's confidence crossed with a sports science lab. Dark theme with high-contrast accent colors. Clean, commanding, trustworthy. NOT generic fitness app pastel gradients. NOT clinical/sterile hospital UI.

- **Primary background**: Deep charcoal/near-black (`#0A0A0F`)
- **Surface cards**: Dark slate (`#14141F`) with subtle 1px borders (`rgba(255,255,255,0.06)`)
- **Primary accent**: Electric teal/cyan (`#00E5CC`) — used sparingly for active states, highlights, progress
- **Danger/Red zones**: Warm red (`#FF4757`) for body map "needs work" areas
- **Warning/Yellow zones**: Amber (`#FFBE0B`) for moderate gaps
- **Success/Green zones**: Bright green (`#06D6A0`) for "sport-ready" areas
- **Text**: White (`#F8F8F2`) for headings, muted gray (`#8B8B9E`) for secondary text
- **Typography**: Use `'Outfit'` from Google Fonts for headings (bold, geometric, athletic feel), `'DM Sans'` for body text (clean, readable). Import from Google Fonts CDN.

## App Flow — 4 Steps (use a stepper/progress bar at top)

### Step 1: Sport Selection
- Heading: "What sport are you returning to?"
- Subtext: "We'll analyze your mobility against the exact demands of your sport."
- Grid of sport cards (3 columns on desktop, 2 on mobile): Tennis, Soccer, Basketball, Swimming, Running, CrossFit, Golf, Volleyball, Baseball, Boxing
- Each card has: a relevant emoji or lucide-react icon, sport name, brief tag like "Upper body dominant" or "Full body explosive"
- Cards have a hover lift effect and glow border in the accent color when selected
- "Continue" button at bottom, disabled until a sport is selected

### Step 2: Movement Recording / Upload
- Heading: "Show us how you move"
- Subtext: "Record or upload a video of yourself doing these 4 test movements. We'll handle the rest."
- Show 4 test movement cards in a row:
  1. **Overhead Reach** — "Stand tall, raise both arms as high as you can"
  2. **Deep Squat** — "Feet shoulder-width, squat as deep as comfortable"
  3. **Forward Lunge** — "Step forward into your deepest lunge, each side"
  4. **Trunk Rotation** — "Arms out, rotate your torso fully left and right"
- Each card has a small stick-figure SVG illustration of the movement
- Below the cards: two buttons side by side
  - "Record Video" (primary accent button with camera icon) — for hackathon demo, this can just trigger a file input or show a simulated recording state
  - "Upload Video" (outlined button with upload icon) — accepts .mp4/.mov/.webm
- After upload: show a video thumbnail preview with a checkmark and "Video received" confirmation
- For the HACKATHON DEMO: have a "Use Demo Video" button that simulates the upload with pre-loaded data so you don't need a real video during the pitch
- "Analyze My Movement" button (large, accent color, slight pulse animation)

### Step 3: Body Map Results (THIS IS THE HERO SCREEN — make it stunning)
- Split layout: Left 55% = interactive body map, Right 45% = analysis details
- **Left side — SVG Body Map:**
  - Front-facing human body outline in SVG, clean anatomical style (not cartoonish)
  - Body divided into tappable/hoverable zones: shoulders (L/R), elbows (L/R), wrists (L/R), thoracic spine, lumbar spine, hips (L/R), knees (L/R), ankles (L/R)
  - Each zone is color-coded: green (#06D6A0), yellow (#FFBE0B), or red (#FF4757) based on the gap analysis
  - Zones pulse/glow gently when they're red (needs attention)
  - When you hover/tap a zone, it expands slightly and shows a tooltip: "Left Hip — Current: 95° | Required for Soccer: 130° | Gap: 35°"
  - Below the body map: a legend showing green = Sport Ready, yellow = Needs Work, red = Priority Focus
  - Also below: the selected sport badge and an overall "Sport Readiness Score" as a large circular progress ring (e.g., "67% Ready for Tennis")

- **Right side — Analysis Panel:**
  - Heading: "Your [Sport] Mobility Gap Analysis"
  - A scrollable list of joint assessments, sorted worst-to-best:
    - Each item shows: Joint name, current ROM vs required ROM, a mini horizontal bar comparing the two, and a severity badge (Priority / Moderate / Good)
    - Example: "Right Shoulder External Rotation — You: 42° | Tennis Requires: 90° | Gap: 48°" with a red "Priority" badge
  - At the bottom of the panel: "Generate My Return Plan →" button

### Step 4: Personalized Plan
- Heading: "Your 4-Week Return to [Sport] Plan"
- Subtext: "Targeting your specific gaps. 15-20 minutes per day."
- Week selector tabs (Week 1 / Week 2 / Week 3 / Week 4) — show Week 1 by default
- Each week shows 4-5 exercise cards:
  - Exercise name (e.g., "90/90 Hip Switch")
  - Target area with color dot matching body map (e.g., 🔴 Left Hip)
  - Sets × Reps or Hold time (e.g., "3 × 30 seconds each side")
  - Brief description of the exercise
  - A "Why this exercise" expandable section that explains: "Your left hip internal rotation is 25° below what soccer demands for cutting and change of direction. This exercise directly targets hip IR."
- At the bottom:
  - "Download Plan as PDF" button (can be non-functional for hackathon)
  - "Re-assess in 2 Weeks" button
  - Small disclaimer text: "ReMotion is a mobility training tool, not medical advice. Consult a healthcare professional for injuries or pain."

## Key UI Components Needed

### Progress Stepper (top of page)
- 4 steps: Select Sport → Record Movement → View Analysis → Get Plan
- Current step highlighted in accent color, completed steps have checkmarks
- Thin horizontal line connecting the steps

### Sport Readiness Score Ring
- Circular SVG progress ring, large (180px diameter)
- Animated fill on load (count up from 0 to the score)
- Score number in the center in large bold font
- Sport name below

### Body Map SVG
- This is the most important visual element. It should be:
  - Clean, anatomical front-facing human silhouette
  - Semi-transparent base body in a neutral gray
  - Overlay circles/regions on each joint that can be independently colored
  - Smooth color transitions when data loads
  - Hover states that show the angle data

## Interaction & Animation Notes
- Page transitions between steps: smooth fade/slide (use CSS transitions, not heavy libraries)
- Body map zones: CSS transition on color changes, subtle scale on hover
- Score ring: animated stroke-dasharray on mount
- Cards: translateY(-4px) + box-shadow increase on hover
- "Analyze" button: subtle pulse animation (scale 1.0 → 1.02 → 1.0 loop) to draw attention
- Loading state during "analysis": show a skeleton/shimmer version of the body map with a scanning line animation moving top-to-bottom, text says "Analyzing your movement patterns..."
- All transitions should feel snappy and athletic, not floaty — use `cubic-bezier(0.16, 1, 0.3, 1)` easing

## Data Structure (hardcode for hackathon)

```javascript
// Sport movement blueprints — ROM requirements per joint
const sportBlueprints = {
  tennis: {
    name: "Tennis",
    joints: {
      shoulder_external_rotation: { required: 90, label: "Shoulder External Rotation" },
      shoulder_flexion: { required: 170, label: "Shoulder Flexion" },
      thoracic_rotation: { required: 45, label: "Thoracic Rotation" },
      hip_flexion: { required: 120, label: "Hip Flexion" },
      hip_internal_rotation: { required: 35, label: "Hip Internal Rotation" },
      knee_flexion: { required: 130, label: "Knee Flexion" },
      ankle_dorsiflexion: { required: 20, label: "Ankle Dorsiflexion" },
      wrist_extension: { required: 70, label: "Wrist Extension" }
    }
  },
  soccer: {
    name: "Soccer",
    joints: {
      hip_flexion: { required: 130, label: "Hip Flexion" },
      hip_extension: { required: 30, label: "Hip Extension" },
      hip_internal_rotation: { required: 40, label: "Hip Internal Rotation" },
      hip_external_rotation: { required: 45, label: "Hip External Rotation" },
      knee_flexion: { required: 140, label: "Knee Flexion" },
      ankle_dorsiflexion: { required: 25, label: "Ankle Dorsiflexion" },
      ankle_plantarflexion: { required: 50, label: "Ankle Plantarflexion" },
      thoracic_rotation: { required: 40, label: "Thoracic Rotation" }
    }
  },
  basketball: {
    name: "Basketball",
    joints: {
      shoulder_flexion: { required: 170, label: "Shoulder Flexion" },
      shoulder_external_rotation: { required: 80, label: "Shoulder External Rotation" },
      hip_flexion: { required: 125, label: "Hip Flexion" },
      hip_extension: { required: 25, label: "Hip Extension" },
      knee_flexion: { required: 135, label: "Knee Flexion" },
      ankle_dorsiflexion: { required: 25, label: "Ankle Dorsiflexion" },
      thoracic_rotation: { required: 40, label: "Thoracic Rotation" },
      wrist_extension: { required: 65, label: "Wrist Extension" }
    }
  },
  swimming: {
    name: "Swimming",
    joints: {
      shoulder_flexion: { required: 180, label: "Shoulder Flexion" },
      shoulder_extension: { required: 60, label: "Shoulder Extension" },
      shoulder_external_rotation: { required: 95, label: "Shoulder External Rotation" },
      shoulder_internal_rotation: { required: 70, label: "Shoulder Internal Rotation" },
      thoracic_extension: { required: 25, label: "Thoracic Extension" },
      hip_flexion: { required: 120, label: "Hip Flexion" },
      ankle_plantarflexion: { required: 55, label: "Ankle Plantarflexion" },
      ankle_dorsiflexion: { required: 15, label: "Ankle Dorsiflexion" }
    }
  },
  running: {
    name: "Running",
    joints: {
      hip_flexion: { required: 120, label: "Hip Flexion" },
      hip_extension: { required: 20, label: "Hip Extension" },
      knee_flexion: { required: 130, label: "Knee Flexion" },
      ankle_dorsiflexion: { required: 20, label: "Ankle Dorsiflexion" },
      ankle_plantarflexion: { required: 50, label: "Ankle Plantarflexion" },
      hip_internal_rotation: { required: 30, label: "Hip Internal Rotation" },
      thoracic_rotation: { required: 35, label: "Thoracic Rotation" },
      hip_external_rotation: { required: 35, label: "Hip External Rotation" }
    }
  },
  crossfit: {
    name: "CrossFit",
    joints: {
      shoulder_flexion: { required: 180, label: "Shoulder Flexion" },
      shoulder_external_rotation: { required: 90, label: "Shoulder External Rotation" },
      hip_flexion: { required: 135, label: "Hip Flexion" },
      hip_external_rotation: { required: 45, label: "Hip External Rotation" },
      knee_flexion: { required: 140, label: "Knee Flexion" },
      ankle_dorsiflexion: { required: 30, label: "Ankle Dorsiflexion" },
      thoracic_extension: { required: 25, label: "Thoracic Extension" },
      wrist_extension: { required: 75, label: "Wrist Extension" }
    }
  }
};

// Simulated user assessment results (what MediaPipe would return)
// Use this for demo mode
const demoUserMobility = {
  shoulder_flexion: 148,
  shoulder_extension: 42,
  shoulder_external_rotation: 52,
  shoulder_internal_rotation: 55,
  thoracic_rotation: 28,
  thoracic_extension: 15,
  hip_flexion: 98,
  hip_extension: 12,
  hip_internal_rotation: 22,
  hip_external_rotation: 30,
  knee_flexion: 118,
  ankle_dorsiflexion: 12,
  ankle_plantarflexion: 38,
  wrist_extension: 50
};
```

## Claude API Integration (Step 3 → Step 4)

After computing the gap analysis (user angles vs sport blueprint), send the gap data to Claude API (Sonnet) to generate the exercise plan. The prompt should include:
- The sport
- Each joint's current ROM, required ROM, and gap
- Ask for a 4-week progressive plan with specific exercises, sets, reps, and reasoning

For the hackathon demo: you can pre-generate this plan and hardcode it, OR make a real API call. Real call is more impressive if it works reliably.

## Mobile Responsiveness
- Steps 1, 2, 4: stack naturally on mobile
- Step 3 (body map): stack vertically — body map on top (full width), analysis panel below
- Minimum supported width: 375px (iPhone SE)

## What NOT to Build
- No user authentication/login
- No database or persistence
- No real MediaPipe integration in the UI (that's a separate backend concern — the frontend just receives the angle data)
- No payment/subscription UI
- No social sharing

## Final Notes
- The body map is the HERO of the entire app. Spend the most design energy here.
- The "same person, different sports, different maps" concept should be demonstrable — consider adding a sport switcher on the results page that re-colors the body map when you change sports (this is the hackathon wow moment)
- Add a small "ReMotion" logo/wordmark in the top left. Style it with the accent color on "Re" and white on "Motion"
- Footer disclaimer: "ReMotion is a mobility training tool for athletic performance. Not a substitute for medical advice."
