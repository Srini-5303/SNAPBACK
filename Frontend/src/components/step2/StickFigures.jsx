const STROKE = '#00E5CC';
const STROKE_DIM = 'rgba(0,229,204,0.4)';
const HEAD_FILL = 'rgba(0,229,204,0.08)';

export function OverheadReachFigure() {
  return (
    <svg viewBox="0 0 80 120" fill="none" xmlns="http://www.w3.org/2000/svg" aria-label="Overhead reach movement">
      {/* Head */}
      <circle cx="40" cy="14" r="9" stroke={STROKE} strokeWidth="1.5" fill={HEAD_FILL} />
      {/* Torso */}
      <line x1="40" y1="23" x2="40" y2="70" stroke={STROKE} strokeWidth="1.5" />
      {/* Left arm — raised overhead */}
      <line x1="40" y1="35" x2="20" y2="15" stroke={STROKE} strokeWidth="1.5" strokeLinecap="round" />
      <line x1="20" y1="15" x2="12" y2="4" stroke={STROKE} strokeWidth="1.5" strokeLinecap="round" />
      {/* Right arm — raised overhead */}
      <line x1="40" y1="35" x2="60" y2="15" stroke={STROKE} strokeWidth="1.5" strokeLinecap="round" />
      <line x1="60" y1="15" x2="68" y2="4" stroke={STROKE} strokeWidth="1.5" strokeLinecap="round" />
      {/* Left leg */}
      <line x1="40" y1="70" x2="26" y2="95" stroke={STROKE} strokeWidth="1.5" strokeLinecap="round" />
      <line x1="26" y1="95" x2="22" y2="118" stroke={STROKE} strokeWidth="1.5" strokeLinecap="round" />
      {/* Right leg */}
      <line x1="40" y1="70" x2="54" y2="95" stroke={STROKE} strokeWidth="1.5" strokeLinecap="round" />
      <line x1="54" y1="95" x2="58" y2="118" stroke={STROKE} strokeWidth="1.5" strokeLinecap="round" />
      {/* Motion indicators */}
      <line x1="12" y1="4" x2="8" y2="2" stroke={STROKE_DIM} strokeWidth="1" strokeDasharray="2 2" />
      <line x1="68" y1="4" x2="72" y2="2" stroke={STROKE_DIM} strokeWidth="1" strokeDasharray="2 2" />
    </svg>
  );
}

export function DeepSquatFigure() {
  return (
    <svg viewBox="0 0 80 120" fill="none" xmlns="http://www.w3.org/2000/svg" aria-label="Deep squat movement">
      {/* Head */}
      <circle cx="40" cy="14" r="9" stroke={STROKE} strokeWidth="1.5" fill={HEAD_FILL} />
      {/* Torso — slight forward lean */}
      <line x1="40" y1="23" x2="36" y2="58" stroke={STROKE} strokeWidth="1.5" />
      {/* Arms out front for balance */}
      <line x1="38" y1="40" x2="16" y2="50" stroke={STROKE} strokeWidth="1.5" strokeLinecap="round" />
      <line x1="38" y1="40" x2="60" y2="50" stroke={STROKE} strokeWidth="1.5" strokeLinecap="round" />
      {/* Hips at squat depth */}
      <line x1="36" y1="58" x2="20" y2="58" stroke={STROKE} strokeWidth="1.5" strokeLinecap="round" />
      <line x1="36" y1="58" x2="52" y2="58" stroke={STROKE} strokeWidth="1.5" strokeLinecap="round" />
      {/* Left leg — deep bend */}
      <line x1="20" y1="58" x2="18" y2="85" stroke={STROKE} strokeWidth="1.5" strokeLinecap="round" />
      <line x1="18" y1="85" x2="14" y2="112" stroke={STROKE} strokeWidth="1.5" strokeLinecap="round" />
      {/* Right leg — deep bend */}
      <line x1="52" y1="58" x2="54" y2="85" stroke={STROKE} strokeWidth="1.5" strokeLinecap="round" />
      <line x1="54" y1="85" x2="58" y2="112" stroke={STROKE} strokeWidth="1.5" strokeLinecap="round" />
      {/* Depth arrow */}
      <path d="M40 64 L40 76" stroke={STROKE_DIM} strokeWidth="1" strokeDasharray="2 2" markerEnd="url(#arrow)" />
    </svg>
  );
}

export function ForwardLungeFigure() {
  return (
    <svg viewBox="0 0 80 120" fill="none" xmlns="http://www.w3.org/2000/svg" aria-label="Forward lunge movement">
      {/* Head */}
      <circle cx="34" cy="12" r="9" stroke={STROKE} strokeWidth="1.5" fill={HEAD_FILL} />
      {/* Upright torso */}
      <line x1="34" y1="21" x2="34" y2="60" stroke={STROKE} strokeWidth="1.5" />
      {/* Left arm back */}
      <line x1="34" y1="36" x2="18" y2="50" stroke={STROKE} strokeWidth="1.5" strokeLinecap="round" />
      {/* Right arm forward */}
      <line x1="34" y1="36" x2="52" y2="44" stroke={STROKE} strokeWidth="1.5" strokeLinecap="round" />
      {/* Front leg — lunge forward */}
      <line x1="34" y1="60" x2="52" y2="75" stroke={STROKE} strokeWidth="1.5" strokeLinecap="round" />
      <line x1="52" y1="75" x2="56" y2="100" stroke={STROKE} strokeWidth="1.5" strokeLinecap="round" />
      {/* Back leg — trailing */}
      <line x1="34" y1="60" x2="22" y2="80" stroke={STROKE} strokeWidth="1.5" strokeLinecap="round" />
      <line x1="22" y1="80" x2="18" y2="112" stroke={STROKE} strokeWidth="1.5" strokeLinecap="round" />
      {/* Back knee close to ground */}
      <circle cx="22" cy="80" r="3" stroke={STROKE_DIM} strokeWidth="1" fill="none" />
    </svg>
  );
}

export function TrunkRotationFigure() {
  return (
    <svg viewBox="0 0 80 120" fill="none" xmlns="http://www.w3.org/2000/svg" aria-label="Trunk rotation movement">
      {/* Head — rotated slightly */}
      <circle cx="40" cy="14" r="9" stroke={STROKE} strokeWidth="1.5" fill={HEAD_FILL} />
      {/* Torso */}
      <line x1="40" y1="23" x2="40" y2="68" stroke={STROKE} strokeWidth="1.5" />
      {/* Arms spread wide — rotation */}
      <line x1="40" y1="38" x2="10" y2="30" stroke={STROKE} strokeWidth="1.5" strokeLinecap="round" />
      <line x1="40" y1="38" x2="70" y2="46" stroke={STROKE} strokeWidth="1.5" strokeLinecap="round" />
      {/* Hips — stable */}
      <line x1="40" y1="68" x2="28" y2="68" stroke={STROKE} strokeWidth="1.5" />
      <line x1="40" y1="68" x2="52" y2="68" stroke={STROKE} strokeWidth="1.5" />
      {/* Left leg */}
      <line x1="28" y1="68" x2="24" y2="95" stroke={STROKE} strokeWidth="1.5" strokeLinecap="round" />
      <line x1="24" y1="95" x2="22" y2="118" stroke={STROKE} strokeWidth="1.5" strokeLinecap="round" />
      {/* Right leg */}
      <line x1="52" y1="68" x2="56" y2="95" stroke={STROKE} strokeWidth="1.5" strokeLinecap="round" />
      <line x1="56" y1="95" x2="58" y2="118" stroke={STROKE} strokeWidth="1.5" strokeLinecap="round" />
      {/* Rotation arc */}
      <path d="M18 36 Q40 22 62 40" stroke={STROKE_DIM} strokeWidth="1" fill="none" strokeDasharray="3 2" />
    </svg>
  );
}
