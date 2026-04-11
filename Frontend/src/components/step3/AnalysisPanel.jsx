import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useApp } from '../../context/AppContext.jsx';
import JointAssessmentRow from './JointAssessmentRow.jsx';
import ReadinessRing from './ReadinessRing.jsx';
import './AnalysisPanel.css';

const WEEKS_OPTIONS = [2, 4, 6, 8, 12, 16];

export default function AnalysisPanel({ gapAnalysis }) {
  const navigate = useNavigate();
  const { generatePlan, planLoading } = useApp();

  const [showForm, setShowForm]           = useState(false);
  const [dominantHand, setDominantHand]   = useState(null);     // 'left' | 'right'
  const [weeksToReturn, setWeeksToReturn] = useState(null);     // number
  const [weightKg, setWeightKg]           = useState('');       // string input

  if (!gapAnalysis) return null;
  const { sportName, readinessScore, joints } = gapAnalysis;

  async function handleSubmit() {
    if (!dominantHand || !weeksToReturn) return;
    const weightNum = parseFloat(weightKg);
    await generatePlan({
      dominantHand,
      weeksToReturn,
      weightKg: !isNaN(weightNum) && weightNum > 0 ? weightNum : null,
    });
    navigate('/plan');
  }

  const formReady = dominantHand && weeksToReturn;

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
        {!showForm ? (
          <button className="btn-generate" onClick={() => setShowForm(true)}>
            Generate My Return Plan
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <path d="M5 12h14M12 5l7 7-7 7" />
            </svg>
          </button>
        ) : (
          <div className="plan-form">
            <p className="plan-form-title">Personalise your plan</p>

            <div className="plan-form-group">
              <span className="plan-form-label">Dominant hand</span>
              <div className="plan-form-pills">
                {['left', 'right'].map((h) => (
                  <button
                    key={h}
                    className={`pill ${dominantHand === h ? 'pill-active' : ''}`}
                    onClick={() => setDominantHand(h)}
                  >
                    {h.charAt(0).toUpperCase() + h.slice(1)}
                  </button>
                ))}
              </div>
            </div>

            <div className="plan-form-group">
              <span className="plan-form-label">Weeks until return to sport</span>
              <div className="plan-form-pills">
                {WEEKS_OPTIONS.map((w) => (
                  <button
                    key={w}
                    className={`pill ${weeksToReturn === w ? 'pill-active' : ''}`}
                    onClick={() => setWeeksToReturn(w)}
                  >
                    {w}w
                  </button>
                ))}
              </div>
            </div>

            <div className="plan-form-group">
              <span className="plan-form-label">Body weight (kg) <span className="plan-form-optional">optional</span></span>
              <input
                className="plan-form-input"
                type="number"
                min="30"
                max="250"
                step="1"
                placeholder="e.g. 75"
                value={weightKg}
                onChange={(e) => setWeightKg(e.target.value)}
              />
            </div>

            <button
              className={`btn-generate ${!formReady || planLoading ? 'btn-generate-disabled' : ''}`}
              onClick={handleSubmit}
              disabled={!formReady || planLoading}
            >
              {planLoading ? 'Building plan…' : 'Build My Plan'}
              {!planLoading && (
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M5 12h14M12 5l7 7-7 7" />
                </svg>
              )}
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
