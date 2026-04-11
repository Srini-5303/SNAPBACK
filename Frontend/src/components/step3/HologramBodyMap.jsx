import { useMemo, useState, useCallback, Suspense } from 'react';
import { Canvas } from '@react-three/fiber';
import { OrbitControls } from '@react-three/drei';
import { EffectComposer, Bloom } from '@react-three/postprocessing';
import HologramGrid from './HologramGrid.jsx';
import HologramBody from './HologramBody.jsx';
import HologramJoints from './HologramJoints.jsx';
import HologramScanLine from './HologramScanLine.jsx';
import { mergeJoints3D } from './HologramScene.constants.js';
import './HologramBodyMap.css';

function LoadingPlaceholder() {
  return (
    <mesh position={[0, 0, 0]}>
      <capsuleGeometry args={[0.15, 1.4, 8, 16]} />
      <meshBasicMaterial color="#00E5CC" transparent opacity={0.08} wireframe />
    </mesh>
  );
}

// ── Inner R3F scene ────────────────────────────────────────────
// Lives inside <Canvas> so it has access to the GL context.
// Receives onPositionsComputed as a prop and forwards it to
// HologramBody so the computed joint positions bubble up to the
// parent (HologramBodyMap) which lives outside the Canvas.
function HologramScene({ mergedJoints, hoveredKey, onHover, modelUrl, onPositionsComputed }) {
  return (
    <>
      <ambientLight intensity={0.05} />
      <pointLight position={[0,  2,  2]} color="#00E5CC" intensity={0.5} />
      <pointLight position={[0, -1,  1]} color="#00E5CC" intensity={0.2} />

      <Suspense fallback={<LoadingPlaceholder />}>
        <HologramBody url={modelUrl} onPositionsComputed={onPositionsComputed} />
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
        target={[0, 0, 0]}
        minPolarAngle={Math.PI * 0.25}
        maxPolarAngle={Math.PI * 0.75}
      />
    </>
  );
}

// ── Public component ───────────────────────────────────────────
export default function HologramBodyMap({ gapAnalysis, modelUrl = '/models/male_body.glb' }) {
  const [hoveredKey, setHoveredKey]         = useState(null);
  // computedPositions: { jointKey → [x,y,z] } derived from actual mesh
  const [computedPositions, setComputedPositions] = useState({});

  // Stable callback so it doesn't re-trigger HologramBody's useEffect
  const handlePositionsComputed = useCallback((positions) => {
    setComputedPositions(positions);
  }, []);

  // Reset computed positions when the model URL changes so we don't
  // show stale markers from the previous model while the new one loads
  const [prevUrl, setPrevUrl] = useState(modelUrl);
  if (modelUrl !== prevUrl) {
    setPrevUrl(modelUrl);
    setComputedPositions({});
  }

  const mergedJoints = useMemo(
    () => (gapAnalysis ? mergeJoints3D(gapAnalysis.joints, computedPositions) : []),
    [gapAnalysis, computedPositions]
  );

  return (
    <div className="hologram-body-map hologram-body-map-3d">
      <HologramGrid />
      <Canvas
        camera={{ position: [0, 0.0, 2.6], fov: 42 }}
        gl={{ antialias: true, alpha: true }}
        style={{ background: 'transparent', position: 'relative', zIndex: 1 }}
      >
        <HologramScene
          mergedJoints={mergedJoints}
          hoveredKey={hoveredKey}
          onHover={setHoveredKey}
          modelUrl={modelUrl}
          onPositionsComputed={handlePositionsComputed}
        />
      </Canvas>
    </div>
  );
}
