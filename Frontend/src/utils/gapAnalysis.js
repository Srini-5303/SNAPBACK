import { sportBlueprints } from '../data/sportBlueprints.js';

/**
 * Compute mobility gap analysis for a given sport and user mobility data.
 *
 * @param {string} sportKey - key from sportBlueprints (e.g. 'tennis')
 * @param {Object} userMobility - joint name → measured angle in degrees
 * @returns {{ readinessScore: number, joints: Array, sportName: string }}
 */
export function computeGapAnalysis(sportKey, userMobility) {
  const blueprint = sportBlueprints[sportKey];
  if (!blueprint) return null;

  const jointEntries = Object.entries(blueprint.joints);

  const joints = jointEntries.map(([key, { required, label }]) => {
    const current = userMobility[key] ?? 0;
    const gap = Math.max(0, required - current);
    const gapPercent = required > 0 ? gap / required : 0;

    let severity;
    if (gapPercent > 0.30) {
      severity = 'priority';   // red
    } else if (gapPercent > 0.10) {
      severity = 'moderate';   // yellow
    } else {
      severity = 'good';       // teal
    }

    // Score for this joint: 0–100, capped at 100 for surpluses
    const score = Math.min(100, Math.round((current / required) * 100));

    return { key, label, current, required, gap: Math.round(gap), gapPercent, severity, score };
  });

  // Sort worst-to-best by gap percentage
  joints.sort((a, b) => b.gapPercent - a.gapPercent);

  // Overall readiness = average of all joint scores
  const readinessScore = Math.round(
    joints.reduce((sum, j) => sum + j.score, 0) / joints.length
  );

  return {
    sportName: blueprint.name,
    readinessScore,
    joints,
  };
}

/**
 * Map a joint key to its body map region for coloring the SVG.
 * Returns 'left', 'right', or 'center'.
 */
export const JOINT_SIDE_MAP = {
  shoulder_external_rotation: 'both',
  shoulder_internal_rotation: 'both',
  shoulder_flexion:           'both',
  shoulder_extension:         'both',
  thoracic_rotation:          'center',
  thoracic_extension:         'center',
  hip_flexion:                'both',
  hip_extension:              'both',
  hip_internal_rotation:      'both',
  hip_external_rotation:      'both',
  hip_rotation:               'both',
  knee_flexion:               'both',
  ankle_dorsiflexion:         'both',
  ankle_plantarflexion:       'both',
  wrist_extension:            'both',
  elbow_flexion:              'both',
};

export const SEVERITY_COLORS = {
  priority: 'var(--color-red)',
  moderate: 'var(--color-yellow)',
  good:     'var(--color-accent)',
};
