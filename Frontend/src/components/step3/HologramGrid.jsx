import './HologramGrid.css';

export default function HologramGrid() {
  const cols = 12;
  const rows = 18;

  return (
    <div className="hologram-grid" aria-hidden="true">
      <svg
        viewBox="0 0 240 440"
        preserveAspectRatio="xMidYMid meet"
        className="hologram-grid-svg"
      >
        <defs>
          <radialGradient id="grid-fade" cx="50%" cy="50%" r="55%">
            <stop offset="0%"   stopColor="rgba(0,229,204,0.12)" />
            <stop offset="70%"  stopColor="rgba(0,229,204,0.05)" />
            <stop offset="100%" stopColor="rgba(0,229,204,0)" />
          </radialGradient>
        </defs>

        {/* Vertical lines */}
        {Array.from({ length: cols + 1 }).map((_, i) => (
          <line
            key={`v${i}`}
            x1={i * (240 / cols)} y1="0"
            x2={i * (240 / cols)} y2="440"
            stroke="url(#grid-fade)"
            strokeWidth="0.5"
          />
        ))}
        {/* Horizontal lines */}
        {Array.from({ length: rows + 1 }).map((_, i) => (
          <line
            key={`h${i}`}
            x1="0" y1={i * (440 / rows)}
            x2="240" y2={i * (440 / rows)}
            stroke="url(#grid-fade)"
            strokeWidth="0.5"
          />
        ))}

        {/* Center crosshair */}
        <line x1="120" y1="0" x2="120" y2="440" stroke="rgba(0,229,204,0.08)" strokeWidth="1" />
        <line x1="0" y1="220" x2="240" y2="220" stroke="rgba(0,229,204,0.08)" strokeWidth="1" />
      </svg>
    </div>
  );
}
