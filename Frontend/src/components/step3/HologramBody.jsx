import { useEffect, useRef, useMemo } from 'react';
import { useGLTF } from '@react-three/drei';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';

const TEAL        = new THREE.Color('#00E5CC');
const EDGE_ANGLE  = 20; // degrees — only show edges sharper than this

/**
 * Loads a GLTF/GLB human model and renders it as a teal hologram wireframe.
 * Place your model at public/models/human.glb
 */
export default function HologramBody({ url = '/models/human.glb' }) {
  const { scene } = useGLTF(url);
  const groupRef  = useRef();
  const linesRef  = useRef([]);
  const fillsRef  = useRef([]);
  const timeRef   = useRef(0);

  // Clone the scene so we don't mutate the cached original
  const clonedScene = useMemo(() => scene.clone(true), [scene]);

  useEffect(() => {
    linesRef.current = [];
    fillsRef.current = [];

    clonedScene.traverse((child) => {
      if (!child.isMesh) return;

      // ── Hologram wireframe via EdgesGeometry ──────────────────
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

      // ── Semi-transparent fill for holographic depth ───────────
      const fillMat = new THREE.MeshBasicMaterial({
        color:       TEAL,
        transparent: true,
        opacity:     0.04,
        side:        THREE.DoubleSide,
        depthWrite:  false,
      });
      child.material = fillMat;
      fillsRef.current.push(fillMat);
    });

    return () => {
      // Dispose materials on unmount
      linesRef.current.forEach((m) => m.dispose());
      fillsRef.current.forEach((m) => m.dispose());
    };
  }, [clonedScene]);

  // Breathing glow — sine-modulate line opacity
  useFrame((_, delta) => {
    timeRef.current += delta;
    const t       = Math.sin((timeRef.current / 3.5) * Math.PI) * 0.5 + 0.5;
    const opacity = 0.65 + t * 0.35;
    linesRef.current.forEach((m) => { m.opacity = opacity; });
  });

  return (
    <group ref={groupRef}>
      <primitive object={clonedScene} />
    </group>
  );
}

// Preload so it doesn't block on first render
useGLTF.preload('/models/human.glb');
