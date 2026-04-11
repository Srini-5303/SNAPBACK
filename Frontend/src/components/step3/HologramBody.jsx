import { useEffect, useRef, useMemo } from 'react';
import { useGLTF } from '@react-three/drei';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';
import { computeJointPositions } from './HologramScene.constants.js';

const TEAL       = new THREE.Color('#00E5CC');
const EDGE_ANGLE = 20; // degrees — only show edges sharper than this
const TARGET_HEIGHT = 1.8; // normalised model height in world units

/**
 * Loads a GLB human model, normalises it to TARGET_HEIGHT centred at
 * the world origin, renders it as a teal hologram wireframe, and fires
 * onPositionsComputed(jointMap) with vertex-derived joint positions so
 * the parent can place markers on the actual body surface.
 */
export default function HologramBody({ url = '/models/male_body.glb', onPositionsComputed }) {
  const { scene } = useGLTF(url);
  const groupRef  = useRef();
  const linesRef  = useRef([]);
  const fillsRef  = useRef([]);
  const timeRef   = useRef(0);

  // Clone so we never mutate the useGLTF cache
  const clonedScene = useMemo(() => scene.clone(true), [scene]);

  useEffect(() => {
    linesRef.current = [];
    fillsRef.current = [];

    // ── Normalise: scale to TARGET_HEIGHT, centre at origin ───────
    const box    = new THREE.Box3().setFromObject(scene); // measure original
    const size   = new THREE.Vector3();
    const center = new THREE.Vector3();
    box.getSize(size);
    box.getCenter(center);

    const s = size.y > 0 ? TARGET_HEIGHT / size.y : 1;
    clonedScene.scale.setScalar(s);
    clonedScene.position.set(-center.x * s, -center.y * s, -center.z * s);

    // Flush matrices so computeJointPositions sees the right world coords
    clonedScene.updateWorldMatrix(true, true);

    // ── Compute joint positions from actual mesh vertices ─────────
    if (onPositionsComputed) {
      const jointMap = computeJointPositions(clonedScene);
      onPositionsComputed(jointMap);
    }

    // ── Hologram materials ─────────────────────────────────────────
    clonedScene.traverse((child) => {
      if (!child.isMesh) return;

      // Wireframe edges
      const edges   = new THREE.EdgesGeometry(child.geometry, EDGE_ANGLE);
      const lineMat = new THREE.LineBasicMaterial({
        color:       TEAL,
        transparent: true,
        opacity:     0.92,
        linewidth:   1,
      });
      const lines = new THREE.LineSegments(edges, lineMat);
      lines.renderOrder = 1;
      child.parent.add(lines);
      linesRef.current.push(lineMat);

      // Semi-transparent fill for holographic depth
      const fillMat = new THREE.MeshBasicMaterial({
        color:      TEAL,
        transparent: true,
        opacity:    0.04,
        side:       THREE.DoubleSide,
        depthWrite: false,
      });
      child.material = fillMat;
      fillsRef.current.push(fillMat);
    });

    return () => {
      linesRef.current.forEach((m) => m.dispose());
      fillsRef.current.forEach((m) => m.dispose());
    };
  }, [clonedScene, scene, onPositionsComputed]);

  // Breathing glow — sine-modulate edge opacity
  useFrame((_, delta) => {
    timeRef.current += delta;
    const t = Math.sin((timeRef.current / 3.5) * Math.PI) * 0.5 + 0.5;
    linesRef.current.forEach((m) => { m.opacity = 0.65 + t * 0.35; });
  });

  return (
    <group ref={groupRef}>
      <primitive object={clonedScene} />
    </group>
  );
}

// Preload both models so gender switching is instant
useGLTF.preload('/models/male_body.glb');
useGLTF.preload('/models/female_muscle_human_body.glb');
