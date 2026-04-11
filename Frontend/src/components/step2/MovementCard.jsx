import './MovementCard.css';

export default function MovementCard({ number, title, instruction, figure: Figure }) {
  return (
    <div className="movement-card">
      <div className="movement-card-number">{number}</div>
      <div className="movement-card-figure">
        <Figure />
      </div>
      <div className="movement-card-info">
        <h3>{title}</h3>
        <p>{instruction}</p>
      </div>
    </div>
  );
}
