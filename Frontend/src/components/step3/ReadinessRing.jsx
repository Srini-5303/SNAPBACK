import { useEffect, useRef, useState } from 'react';
import './ReadinessRing.css';

const SIZE = 180;
const STROKE = 14;
const R = (SIZE - STROKE) / 2;
const CIRCUMFERENCE = 2 * Math.PI * R;

export default function ReadinessRing({ score, sportName }) {
  const [displayScore, setDisplayScore] = useState(0);
  const rafRef = useRef(null);

  useEffect(() => {
    if (!score) return;
    let start = null;
    const duration = 1400;

    function step(ts) {
      if (!start) start = ts;
      const progress = Math.min((ts - start) / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3); // ease-out-cubic
      setDisplayScore(Math.round(eased * score));
      if (progress < 1) {
        rafRef.current = requestAnimationFrame(step);
      }
    }

    rafRef.current = requestAnimationFrame(step);
    return () => cancelAnimationFrame(rafRef.current);
  }, [score]);

  const dashOffset = CIRCUMFERENCE * (1 - displayScore / 100);

  const ringColor =
    displayScore >= 70 ? 'var(--color-accent)' :
    displayScore >= 45 ? 'var(--color-yellow)' :
    'var(--color-red)';

  return (
    <div className="readiness-ring">
      <svg width={SIZE} height={SIZE} viewBox={`0 0 ${SIZE} ${SIZE}`}>
        {/* Track */}
        <circle
          cx={SIZE / 2} cy={SIZE / 2} r={R}
          fill="none"
          stroke="rgba(255,255,255,0.05)"
          strokeWidth={STROKE}
        />
        {/* Progress arc */}
        <circle
          cx={SIZE / 2} cy={SIZE / 2} r={R}
          fill="none"
          stroke={ringColor}
          strokeWidth={STROKE}
          strokeLinecap="round"
          strokeDasharray={CIRCUMFERENCE}
          strokeDashoffset={dashOffset}
          transform={`rotate(-90 ${SIZE / 2} ${SIZE / 2})`}
          style={{
            transition: 'stroke 0.4s ease',
            filter: `drop-shadow(0 0 6px ${ringColor})`,
          }}
        />
        {/* Score text */}
        <text
          x={SIZE / 2} y={SIZE / 2 - 8}
          textAnchor="middle"
          dominantBaseline="middle"
          fill={ringColor}
          fontSize="38"
          fontFamily="Outfit, sans-serif"
          fontWeight="800"
        >
          {displayScore}
        </text>
        <text
          x={SIZE / 2} y={SIZE / 2 + 22}
          textAnchor="middle"
          dominantBaseline="middle"
          fill="rgba(255,255,255,0.4)"
          fontSize="11"
          fontFamily="DM Sans, sans-serif"
          fontWeight="500"
          letterSpacing="2"
        >
          % READY
        </text>
      </svg>
      {sportName && (
        <p className="readiness-ring-sport">{sportName}</p>
      )}
    </div>
  );
}
