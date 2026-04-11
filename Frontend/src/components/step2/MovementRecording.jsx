import { useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useApp } from '../../context/AppContext.jsx';
import MovementCard from './MovementCard.jsx';
import {
  OverheadReachFigure,
  DeepSquatFigure,
  ForwardLungeFigure,
  TrunkRotationFigure,
} from './StickFigures.jsx';
import './MovementRecording.css';

const MOVEMENTS = [
  {
    number: '01',
    title: 'Overhead Reach',
    instruction: 'Stand tall, raise both arms as high as you can',
    figure: OverheadReachFigure,
  },
  {
    number: '02',
    title: 'Deep Squat',
    instruction: 'Feet shoulder-width, squat as deep as comfortable',
    figure: DeepSquatFigure,
  },
  {
    number: '03',
    title: 'Forward Lunge',
    instruction: 'Step forward into your deepest lunge, each side',
    figure: ForwardLungeFigure,
  },
  {
    number: '04',
    title: 'Trunk Rotation',
    instruction: 'Arms out, rotate your torso fully left and right',
    figure: TrunkRotationFigure,
  },
];

export default function MovementRecording() {
  const { selectedSport, runAnalysis } = useApp();
  const navigate = useNavigate();
  const fileInputRef = useRef(null);
  const [videoReady, setVideoReady] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  function handleFileUpload(e) {
    const file = e.target.files?.[0];
    if (file) setVideoReady(true);
  }

  function handleDemoVideo() {
    setVideoReady(true);
  }

  function handleAnalyze() {
    if (!videoReady) return;
    setIsAnalyzing(true);
    runAnalysis(selectedSport);
    setTimeout(() => navigate('/analysis'), 400);
  }

  return (
    <div className="movement-recording fade-in">
      <div className="page-container">
        <div className="movement-recording-header">
          <h1>Show us how you move</h1>
          <p>Record or upload a video of yourself doing these 4 test movements. We'll handle the rest.</p>
        </div>

        <div className="movement-grid">
          {MOVEMENTS.map((m) => (
            <MovementCard key={m.number} {...m} />
          ))}
        </div>

        <div className="upload-section">
          {!videoReady ? (
            <>
              <div className="upload-buttons">
                <button className="btn-record" onClick={() => fileInputRef.current?.click()}>
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M23 7l-7 5 7 5V7z" /><rect x="1" y="5" width="15" height="14" rx="2" ry="2" />
                  </svg>
                  Record Video
                </button>
                <button className="btn-upload" onClick={() => fileInputRef.current?.click()}>
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4" /><polyline points="17 8 12 3 7 8" /><line x1="12" y1="3" x2="12" y2="15" />
                  </svg>
                  Upload Video
                </button>
              </div>
              <input
                ref={fileInputRef}
                type="file"
                accept=".mp4,.mov,.webm"
                style={{ display: 'none' }}
                onChange={handleFileUpload}
              />
              <button className="btn-demo" onClick={handleDemoVideo}>
                Use Demo Video
                <span className="demo-badge">Hackathon Mode</span>
              </button>
            </>
          ) : (
            <div className="video-ready">
              <div className="video-ready-icon">
                <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                  <polyline points="20 6 9 17 4 12" />
                </svg>
              </div>
              <div className="video-ready-text">
                <span className="video-ready-title">Video received</span>
                <span className="video-ready-sub">Ready to analyze your movement patterns</span>
              </div>
            </div>
          )}
        </div>

        <div className="analyze-section">
          <button
            className={`btn-analyze ${videoReady ? 'pulse' : 'disabled'}`}
            onClick={handleAnalyze}
            disabled={!videoReady || isAnalyzing}
          >
            {isAnalyzing ? 'Preparing Analysis…' : 'Analyze My Movement'}
            {!isAnalyzing && (
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                <path d="M5 12h14M12 5l7 7-7 7" />
              </svg>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
