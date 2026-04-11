import { useState } from 'react';
import './ExerciseCard.css';

const COLOR_MAP = {
  red:    { bg: 'var(--color-red-dim)',    dot: 'var(--color-red)' },
  yellow: { bg: 'var(--color-yellow-dim)', dot: 'var(--color-yellow)' },
  green:  { bg: 'var(--color-green-dim)',  dot: 'var(--color-green)' },
};

export default function ExerciseCard({ exercise, index }) {
  const [isExpanded, setIsExpanded] = useState(false);
  const { name, targetJoint, targetColor, sets, reps, holdTime, description, rationale } = exercise;
  const colors = COLOR_MAP[targetColor] ?? COLOR_MAP.green;

  return (
    <div className={`exercise-card exercise-card-${targetColor}`}>
      <div className="exercise-card-header">
        <div className="exercise-card-index">{String(index + 1).padStart(2, '0')}</div>
        <div className="exercise-card-main">
          <h3 className="exercise-card-name">{name}</h3>
          <div className="exercise-card-meta">
            <span
              className="exercise-target"
              style={{ background: colors.bg }}
            >
              <span
                className="exercise-target-dot"
                style={{ background: colors.dot, boxShadow: `0 0 5px ${colors.dot}` }}
              />
              {targetJoint}
            </span>
            <span className="exercise-prescription">
              {sets && `${sets} sets`}
              {reps && ` × ${reps}`}
              {holdTime && ` · ${holdTime}`}
            </span>
          </div>
        </div>
      </div>

      <p className="exercise-description">{description}</p>

      <button
        className={`exercise-why-toggle ${isExpanded ? 'expanded' : ''}`}
        onClick={() => setIsExpanded((v) => !v)}
      >
        <span>Why this exercise?</span>
        <svg
          width="16" height="16" viewBox="0 0 24 24"
          fill="none" stroke="currentColor" strokeWidth="2.5"
          strokeLinecap="round" strokeLinejoin="round"
          style={{ transform: isExpanded ? 'rotate(180deg)' : 'none', transition: 'transform 0.2s' }}
        >
          <polyline points="6 9 12 15 18 9" />
        </svg>
      </button>

      <div className={`exercise-why-panel ${isExpanded ? 'open' : ''}`}>
        <p>{rationale}</p>
      </div>
    </div>
  );
}
