import './ScanAnimation.css';

export default function ScanAnimation() {
  return (
    <div className="scan-animation">
      <div className="scan-title">
        <span className="scan-dot" />
        Analyzing your movement patterns<span className="scan-cursor">_</span>
      </div>
      <div className="scan-body-skeleton">
        {/* Head */}
        <div className="skel skel-head shimmer" />
        {/* Shoulders */}
        <div className="skel skel-shoulders shimmer" />
        {/* Torso */}
        <div className="skel skel-torso shimmer" />
        {/* Hips */}
        <div className="skel skel-hips shimmer" />
        {/* Legs */}
        <div className="skel-legs">
          <div className="skel skel-leg shimmer" />
          <div className="skel skel-leg shimmer" />
        </div>
        {/* Scan line */}
        <div className="scan-line" />
      </div>
      <p className="scan-subtitle">Measuring range of motion across 16 joint zones…</p>
    </div>
  );
}
