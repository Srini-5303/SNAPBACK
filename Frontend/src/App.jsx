import { Routes, Route, Navigate, useLocation } from 'react-router-dom';
import { useApp } from './context/AppContext.jsx';
import Header from './components/layout/Header.jsx';
import ProgressStepper from './components/layout/ProgressStepper.jsx';
import SportSelection from './components/step1/SportSelection.jsx';
import MovementRecording from './components/step2/MovementRecording.jsx';
import BodyMapResults from './components/step3/BodyMapResults.jsx';
import ExercisePlan from './components/step4/ExercisePlan.jsx';

function RequireSport({ children }) {
  const { selectedSport } = useApp();
  return selectedSport ? children : <Navigate to="/" replace />;
}

function RequirePlan({ children }) {
  const { exercisePlan } = useApp();
  return exercisePlan ? children : <Navigate to="/analysis" replace />;
}

export default function App() {
  const location = useLocation();

  return (
    <div className="app">
      <Header />
      <ProgressStepper currentPath={location.pathname} />
      <main className="app-content">
        <Routes>
          <Route path="/" element={<SportSelection />} />
          <Route path="/record" element={
            <RequireSport><MovementRecording /></RequireSport>
          } />
          <Route path="/analysis" element={
            <RequireSport><BodyMapResults /></RequireSport>
          } />
          <Route path="/plan" element={
            <RequirePlan><ExercisePlan /></RequirePlan>
          } />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </main>
    </div>
  );
}
