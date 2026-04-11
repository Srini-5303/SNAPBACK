import * as THREE from 'three';

export const SEVERITY_COLOR = {
  priority: '#FF4757',
  moderate: '#FFBE0B',
  good:     '#00E5CC',
};

// ── Body parts ────────────────────────────────────────────────
// geo: 'Sphere' | 'Cylinder' | 'Box'
// args: constructor args for that geometry
// position: [x, y, z]  (Y-up, centred at pelvis)
// rotation: [x, y, z]  in radians
export const BODY_PARTS = [
  // Head
  { id: 'head',       geo: 'Sphere',   args: [0.13, 10, 7],               position: [0,     1.60,  0],    rotation: [0, 0, 0] },
  // Neck
  { id: 'neck',       geo: 'Cylinder', args: [0.055, 0.07, 0.18, 6],      position: [0,     1.42,  0],    rotation: [0, 0, 0] },
  // Torso (wider shoulders, narrower waist)
  { id: 'torso',      geo: 'Cylinder', args: [0.17, 0.12, 0.70, 8],       position: [0,     0.95,  0],    rotation: [0, 0, 0] },
  // Pelvis
  { id: 'pelvis',     geo: 'Cylinder', args: [0.13, 0.11, 0.22, 8],       position: [0,     0.18,  0],    rotation: [0, 0, 0] },

  // ── Left arm ─────────────────────────────────────────────────
  { id: 'l_upper_arm', geo: 'Cylinder', args: [0.042, 0.036, 0.38, 6],   position: [-0.28, 0.86,  0],    rotation: [0, 0,  0.30] },
  { id: 'l_forearm',   geo: 'Cylinder', args: [0.034, 0.027, 0.34, 6],   position: [-0.42, 0.52,  0],    rotation: [0, 0,  0.12] },
  { id: 'l_hand',      geo: 'Box',      args: [0.07, 0.09, 0.038],        position: [-0.46, 0.28,  0],    rotation: [0, 0,  0.10] },

  // ── Right arm ─────────────────────────────────────────────────
  { id: 'r_upper_arm', geo: 'Cylinder', args: [0.042, 0.036, 0.38, 6],   position: [ 0.28, 0.86,  0],    rotation: [0, 0, -0.30] },
  { id: 'r_forearm',   geo: 'Cylinder', args: [0.034, 0.027, 0.34, 6],   position: [ 0.42, 0.52,  0],    rotation: [0, 0, -0.12] },
  { id: 'r_hand',      geo: 'Box',      args: [0.07, 0.09, 0.038],        position: [ 0.46, 0.28,  0],    rotation: [0, 0, -0.10] },

  // ── Left leg ──────────────────────────────────────────────────
  { id: 'l_thigh',     geo: 'Cylinder', args: [0.068, 0.052, 0.48, 6],   position: [-0.14, -0.24, 0],    rotation: [0, 0,  0.04] },
  { id: 'l_shin',      geo: 'Cylinder', args: [0.044, 0.036, 0.46, 6],   position: [-0.15, -0.72, 0],    rotation: [0, 0,  0] },
  { id: 'l_foot',      geo: 'Box',      args: [0.10, 0.046, 0.19],        position: [-0.15, -0.99, 0.05], rotation: [0, 0,  0] },

  // ── Right leg ─────────────────────────────────────────────────
  { id: 'r_thigh',     geo: 'Cylinder', args: [0.068, 0.052, 0.48, 6],   position: [ 0.14, -0.24, 0],    rotation: [0, 0, -0.04] },
  { id: 'r_shin',      geo: 'Cylinder', args: [0.044, 0.036, 0.46, 6],   position: [ 0.15, -0.72, 0],    rotation: [0, 0,  0] },
  { id: 'r_foot',      geo: 'Box',      args: [0.10, 0.046, 0.19],        position: [ 0.15, -0.99, 0.05], rotation: [0, 0,  0] },
];

// ── Joint 3D positions ─────────────────────────────────────────
// Keyed by the same joint keys used in gapAnalysis
export const JOINT_POSITIONS_3D = {
  shoulder_flexion:           [-0.26,  1.18,  0],
  shoulder_extension:         [ 0.26,  1.18,  0],
  shoulder_external_rotation: [ 0.26,  1.18,  0],
  shoulder_internal_rotation: [ 0.26,  1.18,  0],
  elbow_flexion:              [-0.40,  0.70,  0],
  wrist_extension:            [-0.46,  0.28,  0],
  thoracic_rotation:          [ 0,     0.92,  0],
  thoracic_extension:         [ 0,     0.85,  0],
  hip_flexion:                [-0.16,  0.12,  0],
  hip_extension:              [ 0.16,  0.12,  0],
  hip_internal_rotation:      [-0.16,  0.12,  0],
  hip_external_rotation:      [ 0.16,  0.12,  0],
  hip_rotation:               [ 0,     0.12,  0],
  knee_flexion:               [-0.16, -0.50,  0],
  ankle_dorsiflexion:         [-0.16, -0.94,  0],
  ankle_plantarflexion:       [ 0.16, -0.94,  0],
};

const SEVERITY_RANK = { priority: 3, moderate: 2, good: 1 };

/**
 * Merge joint data with 3D positions, deduplicating overlapping joints by
 * keeping the worst severity at each coordinate.
 */
export function mergeJoints3D(gapJoints) {
  const byKey = new Map(gapJoints.map((j) => [j.key, j]));
  const seen  = new Map();

  for (const [key, pos] of Object.entries(JOINT_POSITIONS_3D)) {
    const joint = byKey.get(key);
    if (!joint) continue;

    const id = pos.join(',');
    const existing = seen.get(id);
    if (!existing || SEVERITY_RANK[joint.severity] > SEVERITY_RANK[existing.joint.severity]) {
      const hudSide = pos[0] < 0 ? 'left' : 'right';
      seen.set(id, { key, position: pos, joint, hudSide });
    }
  }

  return Array.from(seen.values());
}

// ── Geometry factory ───────────────────────────────────────────
export function buildGeometry({ geo, args }) {
  switch (geo) {
    case 'Sphere':   return new THREE.SphereGeometry(...args);
    case 'Cylinder': return new THREE.CylinderGeometry(...args);
    case 'Box':      return new THREE.BoxGeometry(...args);
    default:         return new THREE.BoxGeometry(0.1, 0.1, 0.1);
  }
}
