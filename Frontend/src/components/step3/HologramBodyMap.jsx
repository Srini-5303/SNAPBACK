import { useMemo, useState, Suspense } from 'react';
import { Canvas } from '@react-three/fiber';
import { OrbitControls } from '@react-three/drei';
import { EffectComposer, Bloom } from '@react-three/postprocessing';
import * as THREE from 'three';
import HologramGrid from './HologramGrid.jsx';
import HologramBody from './HologramBody.jsx';
import HologramJoints from './HologramJoints.jsx';
import HologramScanLine from './HologramScanLine.jsx';
import { mergeJoints3D } from './HologramScene.constants.js';
import './HologramBodyMap.css';

// Simple placeholder rendered via Suspense fallback while model loads
function LoadingPlaceholder() {
  return (
    <mesh position={[0, 0.3, 0]}>
      <capsuleGeometry args={[0.15, 1.4, 8, 16]} />
      <meshBasicMaterial color="#00E5CC" transparent opacity={0.08} wireframe />
    </mesh>
  );
}

function HologramScene({ mergedJoints, hoveredKey, onHover }) {
  return (
    <>
      <ambientLight intensity={0.05} />
      <pointLight position={[0,  2,  2]} color="#00E5CC" intensity={0.5} />
      <pointLight position={[0, -1,  1]} color="#00E5CC" intensity={0.2} />

      {/* Model — Suspense shows placeholder until the GLB is parsed */}
      <Suspense fallback={<LoadingPlaceholder />}>
        <HologramBody />
      </Suspense>

      <HologramJoints
        mergedJoints={mergedJoints}
        hoveredKey={hoveredKey}
        onHover={onHover}
      />
      <HologramScanLine />

      <EffectComposer>
        <Bloom
          luminanceThreshold={0.08}
          luminanceSmoothing={0.9}
          intensity={1.8}
          height={300}
        />
      </EffectComposer>

      <OrbitControls
        autoRotate
        autoRotateSpeed={0.7}
        enableZoom={false}
        enablePan={false}
        minPolarAngle={Math.PI * 0.25}
        maxPolarAngle={Math.PI * 0.75}
      />
    </>
  );
}

export default function HologramBodyMap({ gapAnalysis }) {
  const [hoveredKey, setHoveredKey] = useState(null);

  const mergedJoints = useMemo(
    () => (gapAnalysis ? mergeJoints3D(gapAnalysis.joints) : []),
    [gapAnalysis]
  );

  return (
    <div className="hologram-body-map hologram-body-map-3d">
      <HologramGrid />
      <Canvas
        camera={{ position: [0, 0.35, 3.4], fov: 38 }}
        gl={{ antialias: true, alpha: true }}
        style={{ background: 'transparent', position: 'relative', zIndex: 1 }}
      >
        <HologramScene
          mergedJoints={mergedJoints}
          hoveredKey={hoveredKey}
          onHover={setHoveredKey}
        />
      </Canvas>
    </div>
  );
}
