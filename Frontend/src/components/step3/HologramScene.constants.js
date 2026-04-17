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
// anatomical Y-slices, and returns centroids.
//
// Camera is at z=2.6 looking toward origin (positive-Z = front).
// We use the mean-Z of the sampled vertices + a small forward nudge
// (Z_NUDGE) so markers sit at the joint-centre depth rather than
// floating in front of the body surface.

const STRIDE = 8; // sample every 8th vertex

// Anatomical Y targets for a 1.8-unit model centred at y=0
// Formula: y = −0.9 + fraction_from_sole × 1.8
const SY = {              // [targetY, yTolerance]
  shoulder: [ 0.54, 0.10 ], // 80% from sole (glenohumeral joint centre)
  elbow:    [ 0.22, 0.10 ], // 62% from sole — arms hanging naturally
  hip:      [ 0.00, 0.09 ], // 50% from sole (greater trochanter level)
  knee:     [-0.42, 0.09 ], // 27% from sole
};

// Small forward nudge added to mean-Z so markers sit on the visible
// front half of the body (joint centres are near the midplane).
const Z_NUDGE = 0.03;

export function computeJointPositions(normalizedScene) {
  normalizedScene.updateWorldMatrix(true, true);

  const buf = [];
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

  /**
   * Centroid X/Y of the slice + mean-Z + Z_NUDGE.
   * Using mean-Z (not max-Z) keeps the marker at the joint-centre
   * depth rather than on the skin surface.
   */
  function centroid(yTarget, yTol, xMin, xMax, minCount = 8) {
    let sx = 0, sy = 0, sz = 0, n = 0;
    for (let i = 0; i < buf.length; i += 3) {
      const x = buf[i], y = buf[i + 1], z = buf[i + 2];
      if (y < yTarget - yTol || y > yTarget + yTol) continue;
      if (x < xMin || x > xMax) continue;
      sx += x; sy += y; sz += z; n++;
    }
    if (n < minCount) return null;
    return [sx / n, sy / n, sz / n + Z_NUDGE];
  }

  // Detect T-pose at shoulder level
  let maxAbsX = 0;
  const [sY, sTol] = SY.shoulder;
  for (let i = 0; i < buf.length; i += 3) {
    const y = buf[i + 1];
    if (y < sY - sTol || y > sY + sTol) continue;
    const ax = Math.abs(buf[i]);
    if (ax > maxAbsX) maxAbsX = ax;
  }
  const isTPose = maxAbsX > 0.42;

  const R = {};

  // Shoulders — exclude neck/spine centre (x within ±0.07 of origin)
  R.shoulder_left  = centroid(sY, sTol, -0.42, -0.07);
  R.shoulder_right = centroid(sY, sTol,  0.07,  0.42);

  // Elbows
  const [eY, eTol] = SY.elbow;
  if (isTPose) {
    const h = maxAbsX;
    R.elbow_left  = centroid(sY, sTol + 0.05, -(h * 0.92), -(h * 0.50));
    R.elbow_right = centroid(sY, sTol + 0.05,  (h * 0.50),  (h * 0.92));
  } else {
    // Arms at side — exclude inner torso
    R.elbow_left  = centroid(eY, eTol, -0.38, -0.12);
    R.elbow_right = centroid(eY, eTol,  0.12,  0.38);
  }

  // Hips — pelvic girdle / greater trochanter
  const [hY, hTol] = SY.hip;
  R.hip_left  = centroid(hY, hTol, -0.25, -0.05);
  R.hip_right = centroid(hY, hTol,  0.05,  0.25);

  // Knees
  const [kY, kTol] = SY.knee;
  R.knee_left  = centroid(kY, kTol, -0.22, -0.02);
  R.knee_right = centroid(kY, kTol,  0.02,  0.22);

  const jointMap = {};
  for (const [key, pos] of Object.entries(R)) {
    if (pos) jointMap[key] = pos;
  }
  return jointMap;
}

// ── Proportional fallback positions ───────────────────────────
// Used when vertex sampling returns null for a region.
// Calibrated for a 1.8-unit model centred at origin.
//   Shoulder: 80% height, ±21% width
//   Elbow:    62% height, ±23% width (arms hang at ~shoulder width)
//   Hip:      50% height, ±13% width
//   Knee:     27% height, ±10% width
// Z values = joint-centre depth (near body midplane, slightly forward)
const JOINT_POSITIONS_FALLBACK = {
  shoulder_left:  [-0.21,  0.54, 0.04],
  shoulder_right: [ 0.21,  0.54, 0.04],
  elbow_left:     [-0.23,  0.22, 0.03],
  elbow_right:    [ 0.23,  0.22, 0.03],
  hip_left:       [-0.13,  0.00, 0.04],
  hip_right:      [ 0.13,  0.00, 0.04],
  knee_left:      [-0.10, -0.42, 0.05],
  knee_right:     [ 0.10, -0.42, 0.05],
};

const SEVERITY_RANK = { priority: 3, moderate: 2, good: 1 };

// Backend returns simple keys ("shoulder", "elbow", "hip", "knee").
// Expand each to left + right markers with independent per-side severity.
const SIMPLE_KEY_SIDES = ['shoulder', 'elbow', 'hip', 'knee'];

/**
 * Merge gap-analysis joint data with 3D positions.
 *
 * Handles two input shapes:
 *  - Backend API:  joint.key = "shoulder"  (with severityLeft / severityRight)
 *  - Local fallback: joint.key = "shoulder_left" / "shoulder_right" already split
 *
 * Returns array of markerData: { key, position, joint, hudSide }
 */
export function mergeJoints3D(gapJoints, computedPositions = {}) {
  // Build a lookup keyed by the 8 positional keys
  const byKey = new Map();

  for (const joint of gapJoints) {
    if (SIMPLE_KEY_SIDES.includes(joint.key)) {
      // Backend simple key → split into left and right with per-side severity
      for (const side of ['left', 'right']) {
        const detailKey = `${joint.key}_${side}`;
        const severity  = side === 'left'
          ? (joint.severityLeft  ?? joint.severity)
          : (joint.severityRight ?? joint.severity);
        const currentRom = side === 'left'
          ? (joint.currentLeft  ?? joint.current)
          : (joint.currentRight ?? joint.current);
        byKey.set(detailKey, { ...joint, key: detailKey, severity, current: currentRom });
      }
    } else {
      // Already a positional key (shoulder_left etc.) from local fallback
      byKey.set(joint.key, joint);
    }
  }

  const seen = new Map();

  for (const [key, fallbackPos] of Object.entries(JOINT_POSITIONS_FALLBACK)) {
    const joint = byKey.get(key);
    if (!joint) continue;

    const pos = computedPositions[key] ?? fallbackPos;
    const dedupId = pos.map((v) => Math.round(v * 20) / 20).join(',');

    const existing = seen.get(dedupId);
    if (!existing || SEVERITY_RANK[joint.severity] > SEVERITY_RANK[existing.joint.severity]) {
      const hudSide = pos[0] <= 0 ? 'left' : 'right';
      seen.set(dedupId, { key, position: pos, joint, hudSide });
    }
  }

  return Array.from(seen.values());
}
