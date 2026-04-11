import { useEffect, useState } from 'react';
import { useApp } from '../../context/AppContext.jsx';
import { sportBlueprints } from '../../data/sportBlueprints.js';
import HologramBodyMap from './HologramBodyMap.jsx';
import AnalysisPanel from './AnalysisPanel.jsx';
import ScanAnimation from './ScanAnimation.jsx';
import './BodyMapResults.css';

const SPORTS = Object.entries(sportBlueprints).map(([id, { name, emoji }]) => ({ id, name, emoji }));

export default function BodyMapResults() {
  const { selectedSport, gapAnalysis, switchSport } = useApp();
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const timer = setTimeout(() => setIsLoading(false), 2500);
    return () => clearTimeout(timer);
  }, []);

  return (
    <div className="body-map-results fade-in">
      <div className="page-container">

        {/* Sport switcher */}
        <div className="sport-switcher">
          <span className="sport-switcher-label">Switch Sport:</span>
          <div className="sport-switcher-pills">
            {SPORTS.map((s) => (
              <button
                key={s.id}
                className={`sport-pill ${selectedSport === s.id ? 'active' : ''}`}
                onClick={() => switchSport(s.id)}
              >
                <span>{s.emoji}</span>
                <span>{s.name}</span>
              </button>
            ))}
          </div>
        </div>

        {/* Main split layout */}
        <div className="body-map-layout">
          {/* Left: Hologram */}
          <div className="body-map-left">
            {isLoading ? (
              <ScanAnimation />
            ) : (
              <>
                <HologramBodyMap gapAnalysis={gapAnalysis} />
                <div className="body-map-legend">
                  <div className="legend-row">
                    <span className="legend-dot legend-teal" />
                    <span>Sport Ready</span>
                  </div>
                  <div className="legend-row">
                    <span className="legend-dot legend-yellow" />
                    <span>Needs Work</span>
                  </div>
                  <div className="legend-row">
                    <span className="legend-dot legend-red" />
                    <span>Priority Focus</span>
                  </div>
                </div>
              </>
            )}
          </div>

          {/* Right: Analysis panel */}
          <div className="body-map-right">
            {isLoading ? (
              <div className="analysis-loading">
                <div className="analysis-loading-title shimmer" />
                <div className="analysis-loading-row shimmer" />
                <div className="analysis-loading-row shimmer" />
                <div className="analysis-loading-row shimmer" />
                <div className="analysis-loading-row shimmer" />
              </div>
            ) : (
              <AnalysisPanel gapAnalysis={gapAnalysis} />
            )}
          </div>
        </div>

      </div>
    </div>
  );
}
