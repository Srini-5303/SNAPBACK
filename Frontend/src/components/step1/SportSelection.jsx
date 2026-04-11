import { useNavigate } from 'react-router-dom';
import { useApp } from '../../context/AppContext.jsx';
import { sportBlueprints } from '../../data/sportBlueprints.js';
import SportCard from './SportCard.jsx';
import './SportSelection.css';

const SPORTS = Object.entries(sportBlueprints).map(([id, { name, emoji, tag }]) => ({
  id, name, emoji, tag,
}));

export default function SportSelection() {
  const { selectedSport, selectSport } = useApp();
  const navigate = useNavigate();

  function handleContinue() {
    if (selectedSport) navigate('/record');
  }

  return (
    <div className="sport-selection fade-in">
      <div className="page-container">
        <div className="sport-selection-header">
          <h1>What sport are you returning to?</h1>
          <p>We'll analyze your mobility against the exact demands of your sport.</p>
        </div>

        <div className="sport-grid">
          {SPORTS.map((sport) => (
            <SportCard
              key={sport.id}
              {...sport}
              selected={selectedSport === sport.id}
              onSelect={selectSport}
            />
          ))}
        </div>

        <div className="sport-selection-footer">
          <button
            className={`btn-primary btn-large ${!selectedSport ? 'disabled' : ''}`}
            onClick={handleContinue}
            disabled={!selectedSport}
          >
            Continue
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <path d="M5 12h14M12 5l7 7-7 7" />
            </svg>
          </button>
        </div>
      </div>
    </div>
  );
}
