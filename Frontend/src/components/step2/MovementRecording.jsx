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

const SPORT_MOVEMENTS = {
  tennis: [
    { number: '01', title: 'Overhead Serve Reach', instruction: 'Extend both arms overhead as if tossing and striking a serve', figure: OverheadReachFigure },
    { number: '02', title: 'Split Step Squat', instruction: 'Feet wide, sink into a low ready-position crouch', figure: DeepSquatFigure },
    { number: '03', title: 'Forehand Lunge', instruction: 'Step out into a deep lunge reaching your arm across your body', figure: ForwardLungeFigure },
    { number: '04', title: 'Groundstroke Rotation', instruction: 'Arms out, rotate your hips and torso as if swinging through a shot', figure: TrunkRotationFigure },
  ],
  soccer: [
    { number: '01', title: 'Aerial Header Reach', instruction: 'Jump and extend both arms up as if meeting a high ball with your head', figure: OverheadReachFigure },
    { number: '02', title: 'Goalkeeper Crouch', instruction: 'Wide stance, sink low into a goalkeeper ready position', figure: DeepSquatFigure },
    { number: '03', title: 'Lateral Cut Lunge', instruction: 'Step wide to the side into a deep lunge, each direction', figure: ForwardLungeFigure },
    { number: '04', title: 'Hip Rotation for Kicking', instruction: 'Hands on hips, rotate through your full hip range each side', figure: TrunkRotationFigure },
  ],
  basketball: [
    { number: '01', title: 'Jump Shot Reach', instruction: 'Extend both arms overhead as if releasing a jump shot at full extension', figure: OverheadReachFigure },
    { number: '02', title: 'Defensive Stance Squat', instruction: 'Feet wide, drop into a low defensive stance and hold', figure: DeepSquatFigure },
    { number: '03', title: 'Drive Lane Lunge', instruction: 'Step forward into a deep lunge simulating a drive to the basket', figure: ForwardLungeFigure },
    { number: '04', title: 'Pivot Rotation', instruction: 'Plant one foot and rotate your torso fully each direction', figure: TrunkRotationFigure },
  ],
  swimming: [
    { number: '01', title: 'Catch Phase Reach', instruction: 'Extend both arms fully overhead like the catch position in freestyle', figure: OverheadReachFigure },
    { number: '02', title: 'Push-Off Streamline Squat', instruction: 'Squat to wall push-off depth with arms pressed together overhead', figure: DeepSquatFigure },
    { number: '03', title: 'Kick Extension Lunge', instruction: 'Step into a long lunge and extend the back leg fully like a kick', figure: ForwardLungeFigure },
    { number: '04', title: 'Body Roll Rotation', instruction: 'Arms extended, rotate your torso side to side mimicking freestyle body roll', figure: TrunkRotationFigure },
  ],
  running: [
    { number: '01', title: 'Arm Drive Reach', instruction: 'Drive both arms overhead in an exaggerated running arm swing', figure: OverheadReachFigure },
    { number: '02', title: 'Single-Leg Squat', instruction: 'Balance on one leg, squat as low as comfortable, then switch', figure: DeepSquatFigure },
    { number: '03', title: 'Hip Flexor Lunge', instruction: 'Step into the deepest lunge you can, feeling the hip flexor stretch', figure: ForwardLungeFigure },
    { number: '04', title: 'Running Torso Rotation', instruction: 'Elbows bent at 90°, rotate your torso as in a sprint arm swing', figure: TrunkRotationFigure },
  ],
  crossfit: [
    { number: '01', title: 'Overhead Squat Reach', instruction: 'Extend arms fully overhead with thumbs back, as in an overhead squat', figure: OverheadReachFigure },
    { number: '02', title: 'Deep Squat Hold', instruction: 'Feet shoulder-width, squat to full depth and hold at the bottom', figure: DeepSquatFigure },
    { number: '03', title: 'Lunge & Overhead Reach', instruction: 'Step into a lunge and reach the opposite arm up and across', figure: ForwardLungeFigure },
    { number: '04', title: 'Thoracic Rotation', instruction: 'Hands behind head, rotate your upper back fully each direction', figure: TrunkRotationFigure },
  ],
  golf: [
    { number: '01', title: 'Address Position Reach', instruction: 'Hinge at the hips into golf address and extend arms down as if holding a club', figure: OverheadReachFigure },
    { number: '02', title: 'Impact Squat', instruction: 'Feet shoulder-width, sink into the low impact position of a golf swing', figure: DeepSquatFigure },
    { number: '03', title: 'Follow-Through Lunge', instruction: 'Step forward into a lunge reaching the trail arm through like a follow-through', figure: ForwardLungeFigure },
    { number: '04', title: 'Full Backswing Rotation', instruction: 'Arms across chest, rotate into a full backswing and follow-through each way', figure: TrunkRotationFigure },
  ],
  volleyball: [
    { number: '01', title: 'Spike Approach Reach', instruction: 'Jump and fully extend one arm overhead as if spiking a ball at the net', figure: OverheadReachFigure },
    { number: '02', title: 'Digging Crouch', instruction: 'Feet wide, arms low, drop into a deep defensive digging position', figure: DeepSquatFigure },
    { number: '03', title: 'Serving Lunge', instruction: 'Step into a lunge and reach the hitting arm back as if in a serving motion', figure: ForwardLungeFigure },
    { number: '04', title: 'Setting Rotation', instruction: 'Arms overhead in setting position, rotate your torso each direction', figure: TrunkRotationFigure },
  ],
  baseball: [
    { number: '01', title: 'Wind-Up Reach', instruction: 'Lift your lead knee and reach the throwing arm overhead like a pitching wind-up', figure: OverheadReachFigure },
    { number: '02', title: 'Fielding Ready Stance', instruction: 'Sink into a low fielding crouch with weight on the balls of your feet', figure: DeepSquatFigure },
    { number: '03', title: 'Stride & Lunge', instruction: 'Step into a long stride lunge like planting on a pitch or swing', figure: ForwardLungeFigure },
    { number: '04', title: 'Batting Hip Rotation', instruction: 'Load hips back then drive them through fully as in a batting swing', figure: TrunkRotationFigure },
  ],
  boxing: [
    { number: '01', title: 'Guard Reach', instruction: 'Raise both arms into a high guard and extend fully overhead', figure: OverheadReachFigure },
    { number: '02', title: 'Slip & Crouch', instruction: 'Drop into a deep defensive slip crouch, hands up, weight centred', figure: DeepSquatFigure },
    { number: '03', title: 'Cross Step Lunge', instruction: 'Step forward into a lunge as if throwing a cross with full extension', figure: ForwardLungeFigure },
    { number: '04', title: 'Pivot & Rotate', instruction: 'Plant the lead foot and rotate your hips and torso through a full punch arc', figure: TrunkRotationFigure },
  ],
};

const DEFAULT_MOVEMENTS = [
  { number: '01', title: 'Overhead Reach', instruction: 'Stand tall, raise both arms as high as you can', figure: OverheadReachFigure },
  { number: '02', title: 'Deep Squat', instruction: 'Feet shoulder-width, squat as deep as comfortable', figure: DeepSquatFigure },
  { number: '03', title: 'Forward Lunge', instruction: 'Step forward into your deepest lunge, each side', figure: ForwardLungeFigure },
  { number: '04', title: 'Trunk Rotation', instruction: 'Arms out, rotate your torso fully left and right', figure: TrunkRotationFigure },
];

const STREAM_URL = 'http://localhost:5001';

export default function MovementRecording() {
  const { selectedSport, runAnalysis } = useApp();
  const movements = SPORT_MOVEMENTS[selectedSport] ?? DEFAULT_MOVEMENTS;
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

  async function handleAnalyze() {
    if (!videoReady) return;
    setIsAnalyzing(true);
    await runAnalysis(selectedSport);
    navigate('/analysis');
  }

  return (
    <div className="movement-recording fade-in">
      <div className="page-container">
        <div className="movement-recording-header">
          <h1>Show us how you move</h1>
          <p>Record or upload a video of yourself doing these 4 test movements. We'll handle the rest.</p>
        </div>

        <div className="movement-grid">
          {movements.map((m) => (
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
