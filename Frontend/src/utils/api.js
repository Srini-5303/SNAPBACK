/**
 * API utility — all calls to the SNAPBACK Python backend.
 *
 * Transforms backend response shapes to match what the frontend
 * components already expect (HologramBodyMap, AnalysisPanel, ExerciseCard).
 */

const BASE_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000';

// ── Transformers ──────────────────────────────────────────────────────────────

/**
 * Backend status (red/yellow/green) → frontend severity (priority/moderate/good)
 * Used by HologramJoints for coloring and sonar rings.
 */
const STATUS_TO_SEVERITY = { red: 'priority', yellow: 'moderate', green: 'good' };

/**
 * Transform backend /api/analyze gaps array → frontend joints array
 * (shape expected by computeGapAnalysis consumers: HologramBodyMap, AnalysisPanel)
 */
function sideSeverity(romDeg, required) {
  if (!required || required === 0) return 'good';
  const pct = romDeg / required;
  if (pct >= 0.80) return 'good';
  if (pct >= 0.60) return 'moderate';
  return 'priority';
}

function transformGapAnalysis(data) {
  const joints = data.gaps.map((g) => ({
    key:           g.joint_key,
    label:         g.label,
    current:       g.current_rom,
    currentLeft:   g.current_left,
    currentRight:  g.current_right,
    required:      g.required_rom,
    gap:           g.gap,
    gapPercent:    g.required_rom > 0 ? g.gap / g.required_rom : 0,
    asymmetry:     g.asymmetry,
    severity:      STATUS_TO_SEVERITY[g.status] ?? 'good',
    severityLeft:  sideSeverity(g.current_left,  g.required_rom),
    severityRight: sideSeverity(g.current_right, g.required_rom),
    score:         g.percent_achieved,
  }));

  return {
    sportName:      data.sport_name,
    overallScore:   data.overall_score,
    readinessScore: data.readiness_score,
    joints,
  };
}

/**
 * Transform backend plan weeks → frontend exercisePlan
 * (shape expected by ExercisePlan / ExerciseCard)
 */
function transformPlan(data) {
  return {
    weeks: data.plan.map((w) => ({
      weekNumber: w.week,
      focus:      w.focus ?? `Week ${w.week}`,
      avoid:      w.avoid ?? [],
      exercises:  w.exercises.map((ex) => ({
        name:        ex.name,
        targetJoint: ex.target_label,
        targetColor: ex.status,          // red | yellow | green — same values
        sets:        null,
        reps:        null,
        holdTime:    ex.sets_reps,       // full string e.g. "3 × 30 sec each side"
        description: ex.description,
        rationale:   ex.why,
      })),
    })),
  };
}

// ── API calls ─────────────────────────────────────────────────────────────────

/**
 * Fetch 4 sport-specific exercises from Claude.
 * Called right after sport selection so exercises are ready on Step 2.
 *
 * Returns raw exercise objects:
 *   { name, target_label, sets_reps, description, why }
 */
export async function fetchSportPreview(sport) {
  const res = await fetch(`${BASE_URL}/api/sport-preview/${sport}`);
  if (!res.ok) throw new Error(`Sport preview failed: ${res.status}`);
  const data = await res.json();
  return data.exercises;
}

/**
 * Run full mobility analysis pipeline:
 *   pose stub (simulated OpenCV) → gap analysis → Claude plan
 *
 * Returns { gapAnalysis, exercisePlan } in the frontend's expected shape.
 */
/**
 * Run full mobility analysis pipeline.
 * Pass cvResult (from CV server JSON) to use real recorded data.
 * Omit cvResult to use demo data.
 *
 * Returns { gapAnalysis, exercisePlan } in the frontend's expected shape.
 */
/**
 * Run gap analysis only (no plan). Called when the user finishes recording.
 */
export async function analyzeMovement(sport, cvResult = null) {
  const body = { sport, use_demo: !cvResult, skip_plan: true };
  if (cvResult) body.cv_result = cvResult;

  const res = await fetch(`${BASE_URL}/api/analyze`, {
    method:  'POST',
    headers: { 'Content-Type': 'application/json' },
    body:    JSON.stringify(body),
  });
  if (!res.ok) throw new Error(`Analysis failed: ${res.status}`);
  const data = await res.json();

  return { gapAnalysis: transformGapAnalysis(data) };
}

/**
 * Generate the personalised plan. Called after the user answers the profile
 * questions (dominant hand + weeks to return).
 */
export async function generatePlanRequest(sport, cvResult = null, userProfile = null) {
  const body = { sport, use_demo: !cvResult };
  if (cvResult) body.cv_result = cvResult;
  if (userProfile) {
    // Convert camelCase frontend keys → snake_case backend Pydantic model
    body.user_profile = {
      dominant_hand:   userProfile.dominantHand,
      weeks_to_return: userProfile.weeksToReturn,
      weight_kg:       userProfile.weightKg ?? null,
    };
  }

  const res = await fetch(`${BASE_URL}/api/plan`, {
    method:  'POST',
    headers: { 'Content-Type': 'application/json' },
    body:    JSON.stringify(body),
  });
  if (!res.ok) throw new Error(`Plan generation failed: ${res.status}`);
  const data = await res.json();

  return { exercisePlan: transformPlan(data) };
}
