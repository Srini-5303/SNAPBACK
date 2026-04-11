import { useRef, useMemo, useEffect } from 'react';
import { useFrame } from '@react-three/fiber';
import { Html } from '@react-three/drei';
import * as THREE from 'three';
import { SEVERITY_COLOR } from './HologramScene.constants.js';
import JointHUD from './JointHUD.jsx';

// Shared diamond geometry — created once, reused across all markers
const diamondGeo = new THREE.OctahedronGeometry(0.048, 0);
const ringGeo    = new THREE.RingGeometry(0.055, 0.075, 32);

// ── Sonar ring for priority joints ────────────────────────────
function SonarRing({ color }) {
  const meshRef = useRef();
  const timeRef = useRef(Math.random() * 2); // stagger rings

  useFrame((_, delta) => {
    timeRef.current = (timeRef.current + delta) % 2.2;
    const t = timeRef.current / 2.2;
    const scale   = 1 + t * 2.2;
    const opacity = Math.max(0, 0.85 * (1 - t));
    meshRef.current.scale.setScalar(scale);
    meshRef.current.material.opacity = opacity;
  });

  return (
    <mesh ref={meshRef} geometry={ringGeo} rotation={[-Math.PI / 2, 0, 0]}>
      <meshBasicMaterial
        color={color}
        transparent
        opacity={0.85}
        side={THREE.DoubleSide}
        depthWrite={false}
        blending={THREE.AdditiveBlending}
      />
    </mesh>
  );
}

// ── Single joint marker ────────────────────────────────────────
function JointMarker({ markerData, isHovered, onHover, scaleRef }) {
  const { key, position, joint, hudSide } = markerData;
  const color      = SEVERITY_COLOR[joint.severity];
  const isPriority = joint.severity === 'priority';
  const threeColor = useMemo(() => new THREE.Color(color), [color]);

  const groupRef   = useRef();
  const targetScale= isHovered ? 1.5 : 1.0;

  // Smooth scale lerp
  useFrame((_, delta) => {
    if (!groupRef.current) return;
    const current = groupRef.current.scale.x;
    const next    = THREE.MathUtils.lerp(current, targetScale, Math.min(1, delta * 10));
    groupRef.current.scale.setScalar(next);
  });

  return (
    <group ref={groupRef} position={position}>
      {/* Outer glow halo */}
      <mesh>
        <sphereGeometry args={[0.075, 8, 4]} />
        <meshBasicMaterial
          color={threeColor}
          transparent
          opacity={isHovered ? 0.22 : 0.10}
          blending={THREE.AdditiveBlending}
          depthWrite={false}
        />
      </mesh>

      {/* Diamond marker — responds to pointer events */}
      <mesh
        geometry={diamondGeo}
        onPointerEnter={(e) => { e.stopPropagation(); onHover(key); }}
        onPointerLeave={() => onHover(null)}
      >
        <meshBasicMaterial
          color={threeColor}
          transparent
          opacity={0.9}
        />
      </mesh>

      {/* Sonar pulse ring for priority joints */}
      {isPriority && <SonarRing color={color} />}

      {/* Html HUD — appears on hover, positioned in 3D space */}
      {isHovered && (
        <Html
          center={false}
          zIndexRange={[100, 0]}
          style={{ pointerEvents: 'none' }}
          position={[hudSide === 'left' ? -0.05 : 0.05, 0, 0]}
        >
          <div className={`hud-scene-wrapper hud-scene-${hudSide}`}>
            <JointHUD joint={joint} side={hudSide} inScene />
          </div>
        </Html>
      )}
    </group>
  );
}

// ── All joints ─────────────────────────────────────────────────
export default function HologramJoints({ mergedJoints, hoveredKey, onHover }) {
  // Clean up shared geometries on unmount
  useEffect(() => {
    return () => {
      diamondGeo.dispose();
      ringGeo.dispose();
    };
  }, []);

  return (
    <group>
      {mergedJoints.map((markerData) => (
        <JointMarker
          key={markerData.key}
          markerData={markerData}
          isHovered={hoveredKey === markerData.key}
          onHover={onHover}
        />
      ))}
    </group>
  );
}
