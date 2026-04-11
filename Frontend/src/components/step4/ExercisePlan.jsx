import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useApp } from '../../context/AppContext.jsx';
import WeekTabs from './WeekTabs.jsx';
import ExerciseCard from './ExerciseCard.jsx';
import './ExercisePlan.css';

export default function ExercisePlan() {
  const { selectedSport, exercisePlan, gapAnalysis } = useApp();
  const navigate = useNavigate();
  const [activeWeek, setActiveWeek] = useState(1);

  if (!exercisePlan) return null;

  const { weeks } = exercisePlan;
  const currentWeek = weeks.find((w) => w.weekNumber === activeWeek) ?? weeks[0];
  const sportName = gapAnalysis?.sportName ?? selectedSport;

  return (
    <div className="exercise-plan fade-in">
      <div className="page-container">

        <div className="exercise-plan-header">
          <h1>Your {weeks.length}-Week Return to {sportName} Plan</h1>
          <p>Targeting your specific mobility gaps · 15–20 minutes per day</p>
        </div>

        <WeekTabs weeks={weeks} activeWeek={activeWeek} onSelect={setActiveWeek} />

        {currentWeek.focus && (
          <div className="week-focus-banner">
            <span className="week-focus-label">Week {activeWeek} Focus</span>
            <span className="week-focus-text">{currentWeek.focus}</span>
          </div>
        )}

        <div className="exercise-grid">
          {currentWeek.exercises.map((exercise, i) => (
            <ExerciseCard key={`${activeWeek}-${i}`} exercise={exercise} index={i} />
          ))}
        </div>

        {currentWeek.avoid && currentWeek.avoid.length > 0 && (
          <div className="avoid-section">
            <div className="avoid-header">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                <path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z" />
                <line x1="12" y1="9" x2="12" y2="13" /><line x1="12" y1="17" x2="12.01" y2="17" />
              </svg>
              <span>Things to Avoid — Week {activeWeek}</span>
            </div>
            <ul className="avoid-list">
              {currentWeek.avoid.map((item, i) => (
                <li key={i} className="avoid-item">{item}</li>
              ))}
            </ul>
          </div>
        )}

        <div className="exercise-plan-footer">
          <div className="exercise-plan-actions">
            <button className="btn-pdf" disabled>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4" /><polyline points="7 10 12 15 17 10" /><line x1="12" y1="15" x2="12" y2="3" />
              </svg>
              Download Plan PDF
            </button>
            <button className="btn-reassess" onClick={() => navigate('/analysis')}>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <polyline points="23 4 23 10 17 10" /><path d="M20.49 15a9 9 0 11-2.12-9.36L23 10" />
              </svg>
              Back to Analysis
            </button>
          </div>
          <p className="exercise-disclaimer">
            SNAPBACK is a mobility training tool, not medical advice. Consult a healthcare professional for injuries or pain.
          </p>
        </div>

      </div>
    </div>
  );
}
