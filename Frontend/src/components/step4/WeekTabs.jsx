import './WeekTabs.css';

export default function WeekTabs({ weeks, activeWeek, onSelect }) {
  return (
    <div className="week-tabs">
      {weeks.map((w) => (
        <button
          key={w.weekNumber}
          className={`week-tab ${activeWeek === w.weekNumber ? 'active' : ''}`}
          onClick={() => onSelect(w.weekNumber)}
        >
          <span className="week-tab-label">Week {w.weekNumber}</span>
          {activeWeek === w.weekNumber && (
            <span className="week-tab-focus">{w.focus.split('—')[0].trim()}</span>
          )}
        </button>
      ))}
    </div>
  );
}
