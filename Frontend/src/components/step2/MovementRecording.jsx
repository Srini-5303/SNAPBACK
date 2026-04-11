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

const STREAM_URL = 'http://localhost:5001';

export default function MovementRecording() {
  const { selectedSport, runAnalysis } = useApp();
  const navigate = useNavigate();
  const fileInputRef = useRef(null);
  const [videoReady, setVideoReady] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isStreaming, setIsStreaming] = useState(false);
  const [isPaused, setIsPaused] = useState(false);

  function handleFileUpload(e) {
    const file = e.target.files?.[0];
    if (file) setVideoReady(true);
  }

  function handleDemoVideo() {
    setVideoReady(true);
  }

  function handleStartStream() {
    // Update UI immediately so the button feels instant
    setIsStreaming(true);
    setVideoReady(true);
    // Start the pipeline in the background (fire and forget)
    fetch(`${STREAM_URL}/start`, { method: 'POST' }).catch(console.error);
  }

  function handlePauseStream() {
    const next = !isPaused;
    setIsPaused(next);
    fetch(`${STREAM_URL}/${next ? 'pause' : 'resume'}`, { method: 'POST' }).catch(console.error);
  }

  function handleStopStream() {
    setIsStreaming(false);
    setIsPaused(false);
    setVideoReady(false);
    fetch(`${STREAM_URL}/stop`, { method: 'POST' }).catch(console.error);
  }

  function handleSwitchCamera() {
    fetch(`${STREAM_URL}/switch`, { method: 'POST' }).catch(console.error);
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
                <button className="btn-record" onClick={handleStartStream}>
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
                <span className="video-ready-title">{isStreaming ? 'Live analysis running' : 'Video received'}</span>
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

        {isStreaming && (
          <div className="stream-container">
            <div className="stream-controls">
              <button className="stream-btn" onClick={handlePauseStream}>
                {isPaused ? (
                  <>
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><polygon points="5 3 19 12 5 21 5 3"/></svg>
                    Resume
                  </>
                ) : (
                  <>
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><rect x="6" y="4" width="4" height="16"/><rect x="14" y="4" width="4" height="16"/></svg>
                    Pause
                  </>
                )}
              </button>
              <button className="stream-btn" onClick={handleSwitchCamera}>
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M23 4v6h-6"/><path d="M1 20v-6h6"/><path d="M3.51 9a9 9 0 0114.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0020.49 15"/></svg>
                Switch Camera
              </button>
              <button className="stream-btn stream-btn-stop" onClick={handleStopStream}>
                <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><rect x="3" y="3" width="18" height="18" rx="2"/></svg>
                Stop
              </button>
            </div>
            <img
              src={`${STREAM_URL}/stream`}
              alt="Live mobility analysis"
              className="stream-img"
            />
          </div>
        )}
      </div>
    </div>
  );
}
