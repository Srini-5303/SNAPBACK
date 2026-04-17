import './SportPreviewExercises.css';

/**
 * Shows 4 Claude-generated sport-specific exercises on the Movement Recording screen.
 * Exercises are fetched immediately after sport selection (no user data yet).
 *
 * Props:
 *   exercises  — array of { name, target_label, sets_reps, description, why }
 *   loading    — boolean, show skeleton while fetching
 */
export default function SportPreviewExercises({ exercises, loading }) {
  if (!loading && !exercises) return null;

  return (
    <div className="sport-preview-section">
      <div className="sport-preview-header">
        <span className="sport-preview-label">Recommended warm-up</span>
        <h2 className="sport-preview-title">Key mobility exercises for your sport</h2>
      </div>

      <div className="sport-preview-grid">
        {loading
          ? Array.from({ length: 4 }).map((_, i) => (
              <div key={i} className="sport-preview-card skeleton">
                <div className="skeleton-line skeleton-title" />
                <div className="skeleton-line skeleton-sub" />
                <div className="skeleton-line skeleton-sub short" />
              </div>
            ))
          : exercises.map((ex, i) => (
              <div key={i} className="sport-preview-card">
                <div className="sport-preview-card-top">
                  <span className="sport-preview-index">{String(i + 1).padStart(2, '0')}</span>
                  <span className="sport-preview-target">{ex.target_label}</span>
                </div>
                <h3 className="sport-preview-name">{ex.name}</h3>
                <p className="sport-preview-sets">{ex.sets_reps}</p>
                <p className="sport-preview-desc">{ex.description}</p>
                <p className="sport-preview-why">{ex.why}</p>
              </div>
            ))}
      </div>
    </div>
  );
}
