import { useRef } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';

const PERIOD = 4;     // seconds per sweep
const TOP    =  1.0;  // just above the head (model normalized to ±0.9)
const BOTTOM = -1.0;  // just below the feet

export default function HologramScanLine() {
  const meshRef = useRef();
  const timeRef = useRef(0);

  useFrame((_, delta) => {
    timeRef.current = (timeRef.current + delta) % PERIOD;
    const t = timeRef.current / PERIOD;              // 0 → 1

    // Move top → bottom
    meshRef.current.position.y = TOP + (BOTTOM - TOP) * t;

    // Fade in/out at edges, brightest mid-body
    meshRef.current.material.opacity = 0.55 * Math.sin(Math.PI * t) + 0.1;
  });

  return (
    <mesh ref={meshRef} rotation={[-Math.PI / 2, 0, 0]} position={[0, TOP, 0]}>
      <planeGeometry args={[0.8, 0.012]} />
      <meshBasicMaterial
        color="#00E5CC"
        transparent
        opacity={0.5}
        blending={THREE.AdditiveBlending}
        depthWrite={false}
        side={THREE.DoubleSide}
      />
    </mesh>
  );
}
