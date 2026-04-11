import './SportCard.css';

export default function SportCard({ id, name, emoji, tag, selected, onSelect }) {
  return (
    <button
      className={`sport-card ${selected ? 'selected' : ''}`}
      onClick={() => onSelect(id)}
      aria-pressed={selected}
    >
      <span className="sport-card-emoji">{emoji}</span>
      <span className="sport-card-name">{name}</span>
      <span className="sport-card-tag">{tag}</span>
      {selected && <div className="sport-card-check">✓</div>}
    </button>
  );
}
