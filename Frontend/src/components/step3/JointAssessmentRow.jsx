import './JointAssessmentRow.css';

const SEVERITY_LABEL = {
  priority: 'Priority',
  moderate: 'Moderate',
  good:     'Good',
};

function SideBar({ rom, required, severity, label }) {
  const pct = required > 0 ? Math.min(100, Math.round((rom / required) * 100)) : 100;
  return (
    <div className="side-bar-group">
      <div className="side-bar-header">
        <span className="side-bar-label">{label}</span>
        <span className={`side-bar-value side-bar-value-${severity}`}>{Math.round(rom)}°</span>
      </div>
      <div className="bar-track">
        <div className={`bar-fill bar-fill-${severity}`} style={{ width: `${pct}%` }} />
      </div>
    </div>
  );
}

export default function JointAssessmentRow({ joint }) {
  const { label, current, currentLeft, currentRight, required, severity, gap } = joint;
  const hasLR  = currentLeft != null && currentRight != null;
  const fillPct = required > 0 ? Math.min(100, Math.round((current / required) * 100)) : 100;

  return (
    <div className={`joint-row joint-row-${severity}`}>
      <div className="joint-row-header">
        <span className="joint-row-name">{label}</span>
        <div className="joint-row-header-right">
          {gap > 0 && (
            <span className={`gap-chip gap-chip-${severity}`}>−{Math.round(gap)}°</span>
          )}
          <span className={`joint-row-badge badge-${severity}`}>
            {SEVERITY_LABEL[severity]}
          </span>
        </div>
      </div>

      <div className="joint-row-required">
        <span className="angle-label">Required</span>
        <span className="angle-value">{required}°</span>
      </div>

      {hasLR ? (
        <div className="joint-lr-bars">
          <SideBar
            rom={currentLeft}
            required={required}
            severity={joint.severityLeft ?? severity}
            label="Left"
          />
          <SideBar
            rom={currentRight}
            required={required}
            severity={joint.severityRight ?? severity}
            label="Right"
          />
        </div>
      ) : (
        <>
          <div className="joint-row-bar">
            <div className="bar-track">
              <div className={`bar-fill bar-fill-${severity}`} style={{ width: `${fillPct}%` }} />
            </div>
          </div>
          <div className="joint-row-angles">
            <span className="joint-row-angle">
              <span className="angle-label">You</span>
              <span className="angle-value">{Math.round(current)}°</span>
            </span>
          </div>
        </>
      )}
    </div>
  );
}
