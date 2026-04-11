import * as THREE from 'three';

export const SEVERITY_COLOR = {
  priority: '#FF4757',
  moderate: '#FFBE0B',
  good:     '#00E5CC',
};

// ── Vertex-based joint position computation ────────────────────
// After HologramBody normalises the loaded GLB to 1.8 units tall
// (feet ≈ −0.9, head ≈ +0.9, centred at origin), this function
// does a single pass over all mesh vertices, buckets them into
// anatomical Y-slices, and returns centroids.  No hardcoded Z —
// the centroid Z naturally equals the geometric centre of the
// body cross-section at that height.

const STRIDE = 12; // sample every 12th vertex — fast enough on 34 MB models

// Anatomical Y targets for a 1.8-unit model centred at y=0
// Formula: y = −0.9 + fraction_from_sole × 1.8
const SY = {                // [targetY, yTolerance]
  shoulder : [ 0.57, 0.11 ], // 82 % from sole
  thoracic : [ 0.27, 0.09 ], // 65 % from sole
  hip      : [-0.04, 0.10 ], // 48 % from sole
  elbow    : [ 0.22, 0.11 ], // 63 % from sole  (arms-down pose)
  wrist    : [-0.06, 0.10 ], // 47 % from sole  (arms-down pose)
  knee     : [-0.41, 0.09 ], // 27 % from sole
  ankle    : [-0.77, 0.09 ], //  7 % from sole
};

/**
 * Compute world-space joint positions by sampling actual mesh vertices.
 * Call this AFTER the scene has been normalised (scale + position applied)
 * and after updateWorldMatrix(true,true) has been called.
 *
 * Returns a map: jointKey → [x, y, z]
 */
export function computeJointPositions(normalizedScene) {
  normalizedScene.updateWorldMatrix(true, true);

  // ── Single pass: collect all sampled vertices ──────────────────
  const buf = []; // flat [x,y,z, x,y,z, …]
  const tmp = new THREE.Vector3();

  normalizedScene.traverse((child) => {
    if (!child.isMesh) return;
    const attr = child.geometry.attributes.position;
    if (!attr) return;
    child.updateWorldMatrix(true, false);
    const mat = child.matrixWorld;
    for (let i = 0; i < attr.count; i += STRIDE) {
      tmp.fromBufferAttribute(attr, i).applyMatrix4(mat);
      buf.push(tmp.x, tmp.y, tmp.z);
    }
  });

  if (buf.length === 0) return {};

  // ── Centroid helper ─────────────────────────────────────────────
  // Returns [x,y,z] centroid of all buffered vertices that satisfy
  // the Y-slice and X-window filters, or null if < minCount points.
  function centroid(yTarget, yTol, xMin, xMax, minCount = 8) {
    let sx = 0, sy = 0, sz = 0, n = 0;
    for (let i = 0; i < buf.length; i += 3) {
      const x = buf[i], y = buf[i + 1], z = buf[i + 2];
      if (y < yTarget - yTol || y > yTarget + yTol) continue;
      if (x < xMin || x > xMax) continue;
      sx += x; sy += y; sz += z; n++;
    }
    return n >= minCount ? [sx / n, sy / n, sz / n] : null;
  }

  // ── Detect arm pose at shoulder height ─────────────────────────
  // If max |x| at shoulder level > 0.42 → T-pose (arms out)
  let maxAbsX = 0;
  const [sY, sTol] = SY.shoulder;
  for (let i = 0; i < buf.length; i += 3) {
    const y = buf[i + 1];
    if (y < sY - sTol || y > sY + sTol) continue;
    const ax = Math.abs(buf[i]);
    if (ax > maxAbsX) maxAbsX = ax;
  }
  const isTPose = maxAbsX > 0.42;

  const R = {}; // region positions

  // ── Shoulders ──────────────────────────────────────────────────
  // x window [-0.40, -0.05] / [0.05, 0.40] captures the shoulder
  // joint zone for both T-pose and arms-down without including the
  // full arm extension.
  R.shoulder_left  = centroid(sY, sTol, -0.40, -0.05);
  R.shoulder_right = centroid(sY, sTol,  0.05,  0.40);

  // ── Elbows & wrists ────────────────────────────────────────────
  if (isTPose) {
    const h = maxAbsX; // half-arm span
    R.elbow_left   = centroid(sY, sTol + 0.04, -(h * 0.90), -(h * 0.52));
    R.elbow_right  = centroid(sY, sTol + 0.04,  (h * 0.52),  (h * 0.90));
    R.wrist_left   = centroid(sY, sTol + 0.04, -(h + 0.06), -(h * 0.88));
    R.wrist_right  = centroid(sY, sTol + 0.04,  (h * 0.88),  (h + 0.06));
  } else {
    // Arms hanging — sample at elbow & wrist Y levels
    const [eY, eTol] = SY.elbow;
    const [wY, wTol] = SY.wrist;
    R.elbow_left   = centroid(eY, eTol, -0.42, -0.05);
    R.elbow_right  = centroid(eY, eTol,  0.05,  0.42);
    R.wrist_left   = centroid(wY, wTol, -0.42, -0.04);
    R.wrist_right  = centroid(wY, wTol,  0.04,  0.42);
  }

  // ── Thoracic spine (narrow centre band) ───────────────────────
  const [tY, tTol] = SY.thoracic;
  R.thoracic_center = centroid(tY, tTol, -0.14, 0.14);

  // ── Hips ───────────────────────────────────────────────────────
  const [hY, hTol] = SY.hip;
  R.hip_left  = centroid(hY, hTol, -0.30, -0.04);
  R.hip_right = centroid(hY, hTol,  0.04,  0.30);
  if (R.hip_left && R.hip_right) {
    R.hip_center = [
      (R.hip_left[0] + R.hip_right[0]) / 2,
      (R.hip_left[1] + R.hip_right[1]) / 2,
      (R.hip_left[2] + R.hip_right[2]) / 2,
    ];
  }

  // ── Knees ──────────────────────────────────────────────────────
  const [kY, kTol] = SY.knee;
  R.knee_left  = centroid(kY, kTol, -0.26, -0.02);
  R.knee_right = centroid(kY, kTol,  0.02,  0.26);

  // ── Ankles ─────────────────────────────────────────────────────
  const [aY, aTol] = SY.ankle;
  R.ankle_left  = centroid(aY, aTol, -0.24, -0.01);
  R.ankle_right = centroid(aY, aTol,  0.01,  0.24);

  // ── Map region → joint keys ────────────────────────────────────
  const REGION_TO_KEYS = {
    shoulder_left  : ['shoulder_flexion', 'shoulder_internal_rotation'],
    shoulder_right : ['shoulder_extension', 'shoulder_external_rotation'],
    elbow_left     : ['elbow_flexion'],
    wrist_left     : ['wrist_extension'],
    thoracic_center: ['thoracic_rotation', 'thoracic_extension'],
    hip_left       : ['hip_flexion', 'hip_internal_rotation'],
    hip_right      : ['hip_extension', 'hip_external_rotation'],
    hip_center     : ['hip_rotation'],
    knee_left      : ['knee_flexion'],
    ankle_left     : ['ankle_dorsiflexion'],
    ankle_right    : ['ankle_plantarflexion'],
  };

  const jointMap = {};
  for (const [region, keys] of Object.entries(REGION_TO_KEYS)) {
    const pos = R[region];
    if (!pos) continue;
    for (const key of keys) jointMap[key] = pos;
  }
  return jointMap;
}

// ── Proportional fallback positions ───────────────────────────
// Used when vertex sampling returns null for a region (e.g. model
// has no vertices in that slice).  Calibrated for a 1.8-unit model.
const JOINT_POSITIONS_FALLBACK = {
  shoulder_flexion:           [-0.22,  0.57, 0.00],
  shoulder_extension:         [ 0.22,  0.57, 0.00],
  shoulder_external_rotation: [ 0.22,  0.57, 0.00],
  shoulder_internal_rotation: [ 0.22,  0.57, 0.00],
  elbow_flexion:              [-0.28,  0.22, 0.00],
  wrist_extension:            [-0.26, -0.06, 0.00],
  thoracic_rotation:          [ 0.00,  0.27, 0.00],
  thoracic_extension:         [ 0.00,  0.27, 0.00],
  hip_flexion:                [-0.12, -0.04, 0.00],
  hip_extension:              [ 0.12, -0.04, 0.00],
  hip_internal_rotation:      [-0.12, -0.04, 0.00],
  hip_external_rotation:      [ 0.12, -0.04, 0.00],
  hip_rotation:               [ 0.00, -0.04, 0.00],
  knee_flexion:               [-0.11, -0.41, 0.00],
  ankle_dorsiflexion:         [-0.10, -0.77, 0.00],
  ankle_plantarflexion:       [ 0.10, -0.77, 0.00],
};

const SEVERITY_RANK = { priority: 3, moderate: 2, good: 1 };

/**
 * Merge gap-analysis joint data with 3D positions.
 * Prefers computed positions from actual mesh vertices; falls back
 * to proportional constants when a region wasn't sampled.
 * Deduplicates overlapping markers (same rounded position) keeping
 * the worst severity.
 *
 * @param {Array}  gapJoints        – joints[] from computeGapAnalysis()
 * @param {Object} computedPositions – jointKey → [x,y,z] from computeJointPositions()
 */
export function mergeJoints3D(gapJoints, computedPositions = {}) {
  const byKey = new Map(gapJoints.map((j) => [j.key, j]));
  const seen  = new Map();

  for (const [key, fallbackPos] of Object.entries(JOINT_POSITIONS_FALLBACK)) {
    const joint = byKey.get(key);
    if (!joint) continue;

    // Prefer vertex-derived position; fall back to proportional constant
    const pos = computedPositions[key] ?? fallbackPos;

    // Dedup: round to nearest 0.05 to merge joints at the same anatomical site
    const dedupId = pos.map((v) => Math.round(v * 20) / 20).join(',');

    const existing = seen.get(dedupId);
    if (!existing || SEVERITY_RANK[joint.severity] > SEVERITY_RANK[existing.joint.severity]) {
      const hudSide = pos[0] <= 0 ? 'left' : 'right';
      seen.set(dedupId, { key, position: pos, joint, hudSide });
    }
  }

  return Array.from(seen.values());
}
