import './JointAssessmentRow.css';

const SEVERITY_LABEL = {
  priority: 'Priority',
  moderate: 'Moderate',
  good:     'Good',
};

export default function JointAssessmentRow({ joint }) {
  const { label, current, required, severity } = joint;
  const fillPct = Math.min(100, Math.round((current / required) * 100));

  return (
    <div className={`joint-row joint-row-${severity}`}>
      <div className="joint-row-header">
        <span className="joint-row-name">{label}</span>
        <span className={`joint-row-badge badge-${severity}`}>
          {SEVERITY_LABEL[severity]}
        </span>
      </div>
      <div className="joint-row-angles">
        <span className="joint-row-angle">
          <span className="angle-label">You</span>
          <span className="angle-value">{current}°</span>
        </span>
        <span className="joint-row-angle">
          <span className="angle-label">Required</span>
          <span className="angle-value">{required}°</span>
        </span>
        {joint.gap > 0 && (
          <span className={`joint-row-angle gap-angle gap-${severity}`}>
            <span className="angle-label">Gap</span>
            <span className="angle-value">-{joint.gap}°</span>
          </span>
        )}
      </div>
      <div className="joint-row-bar">
        <div className="bar-track">
          <div
            className={`bar-fill bar-fill-${severity}`}
            style={{ width: `${fillPct}%` }}
          />
          <div className="bar-required-marker" />
        </div>
      </div>
    </div>
  );
}
