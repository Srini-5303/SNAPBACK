import { useNavigate } from 'react-router-dom';
import JointAssessmentRow from './JointAssessmentRow.jsx';
import ReadinessRing from './ReadinessRing.jsx';
import './AnalysisPanel.css';

export default function AnalysisPanel({ gapAnalysis }) {
  const navigate = useNavigate();

  if (!gapAnalysis) return null;
  const { sportName, readinessScore, joints } = gapAnalysis;

  return (
    <div className="analysis-panel">
      <div className="analysis-panel-header">
        <h2>Your {sportName} Mobility Gap Analysis</h2>
        <p className="analysis-panel-sub">
          {joints.filter((j) => j.severity === 'priority').length} priority areas ·{' '}
          {joints.filter((j) => j.severity === 'moderate').length} moderate ·{' '}
          {joints.filter((j) => j.severity === 'good').length} sport-ready
        </p>
      </div>

      <div className="analysis-ring-row">
        <ReadinessRing score={readinessScore} sportName={sportName} />
        <div className="analysis-ring-legend">
          <div className="legend-item">
            <span className="legend-dot legend-dot-good" />
            <span>Sport Ready</span>
          </div>
          <div className="legend-item">
            <span className="legend-dot legend-dot-moderate" />
            <span>Needs Work</span>
          </div>
          <div className="legend-item">
            <span className="legend-dot legend-dot-priority" />
            <span>Priority Focus</span>
          </div>
        </div>
      </div>

      <div className="joint-list">
        {joints.map((joint) => (
          <JointAssessmentRow key={joint.key} joint={joint} />
        ))}
      </div>

      <div className="analysis-panel-footer">
        <button className="btn-generate" onClick={() => navigate('/plan')}>
          Generate My Return Plan
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
            <path d="M5 12h14M12 5l7 7-7 7" />
          </svg>
        </button>
      </div>
    </div>
  );
}
