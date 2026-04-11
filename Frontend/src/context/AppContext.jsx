import { createContext, useContext, useState } from 'react';
import { demoUserMobility } from '../data/demoUserMobility.js';
import { demoExercisePlan } from '../data/demoExercisePlan.js';
import { computeGapAnalysis } from '../utils/gapAnalysis.js';
import { fetchSportPreview, analyzeMovement } from '../utils/api.js';

const AppContext = createContext(null);

export function AppProvider({ children }) {
  const [selectedSport, setSelectedSport]           = useState(null);
  const [gapAnalysis, setGapAnalysis]               = useState(null);
  const [exercisePlan, setExercisePlan]             = useState(null);
  const [sportExercises, setSportExercises]         = useState(null);
  const [sportExercisesLoading, setSportExercisesLoading] = useState(false);
  const [analysisLoading, setAnalysisLoading]       = useState(false);

  function selectSport(sportKey) {
    setSelectedSport(sportKey);
  }

  async function loadSportPreview(sportKey) {
    setSportExercisesLoading(true);
    setSportExercises(null);
    try {
      const exercises = await fetchSportPreview(sportKey);
      setSportExercises(exercises);
    } catch {
      setSportExercises(null);
    } finally {
      setSportExercisesLoading(false);
    }
  }

  async function runAnalysis(sportKey) {
    setAnalysisLoading(true);
    try {
      const { gapAnalysis: ga, exercisePlan: ep } = await analyzeMovement(sportKey);
      setGapAnalysis(ga);
      setExercisePlan(ep);
    } catch {
      // Fallback to local computation if backend is unavailable
      const ga = computeGapAnalysis(sportKey, demoUserMobility);
      setGapAnalysis(ga);
      setExercisePlan(demoExercisePlan[sportKey] ?? demoExercisePlan.tennis);
    } finally {
      setAnalysisLoading(false);
    }
  }

  async function switchSport(sportKey) {
    setSelectedSport(sportKey);
    await runAnalysis(sportKey);
  }

  return (
    <AppContext.Provider value={{
      selectedSport,
      gapAnalysis,
      exercisePlan,
      sportExercises,
      sportExercisesLoading,
      analysisLoading,
      selectSport,
      loadSportPreview,
      runAnalysis,
      switchSport,
    }}>
      {children}
    </AppContext.Provider>
  );
}

export function useApp() {
  const ctx = useContext(AppContext);
  if (!ctx) throw new Error('useApp must be used within AppProvider');
  return ctx;
}
