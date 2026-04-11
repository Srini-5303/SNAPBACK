import './JointHUD.css';

export default function JointHUD({ joint, x, y, side = 'right', inScene = false }) {
  if (!joint) return null;

  const statusLabel = {
    priority: 'PRIORITY',
    moderate: 'MODERATE',
    good:     'SPORT READY',
  }[joint.severity];

  return (
    <div
      className={`joint-hud joint-hud-${joint.severity} joint-hud-${side}`}
      style={inScene ? undefined : { '--hud-x': `${x}`, '--hud-y': `${y}` }}
    >
      <div className="hud-connector" aria-hidden="true" />
      <div className="hud-panel">
        <div className="hud-header">
          <span className="hud-joint-name">{joint.label}</span>
          <span className={`hud-badge hud-badge-${joint.severity}`}>{statusLabel}</span>
        </div>
        <div className="hud-data">
          <div className="hud-row">
            <span className="hud-label">CURRENT</span>
            <span className="hud-value">{joint.current}°</span>
          </div>
          <div className="hud-row">
            <span className="hud-label">REQUIRED</span>
            <span className="hud-value">{joint.required}°</span>
          </div>
          {joint.gap > 0 && (
            <div className="hud-row hud-row-gap">
              <span className="hud-label">GAP</span>
              <span className="hud-value hud-gap-value">-{joint.gap}°</span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
