import { createContext, useContext, useRef, useState } from 'react';
import { demoUserMobility } from '../data/demoUserMobility.js';
import { demoExercisePlan } from '../data/demoExercisePlan.js';
import { computeGapAnalysis } from '../utils/gapAnalysis.js';
import { fetchSportPreview, analyzeMovement, generatePlanRequest } from '../utils/api.js';

const AppContext = createContext(null);

export function AppProvider({ children }) {
  const [selectedSport, setSelectedSport]           = useState(null);
  const [gapAnalysis, setGapAnalysis]               = useState(null);
  const [exercisePlan, setExercisePlan]             = useState(null);
  const [sportExercises, setSportExercises]         = useState(null);
  const [sportExercisesLoading, setSportExercisesLoading] = useState(false);
  const [analysisLoading, setAnalysisLoading]       = useState(false);
  const [planLoading, setPlanLoading]               = useState(false);

  // Keep a ref to the latest cvResult so generatePlan can use it
  const lastCvResult = useRef(null);

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

  async function runAnalysis(sportKey, cvResult = null) {
    setAnalysisLoading(true);
    lastCvResult.current = cvResult;
    try {
      // Run analysis without plan (plan is deferred to generatePlan)
      const { gapAnalysis: ga } = await analyzeMovement(sportKey, cvResult);
      setGapAnalysis(ga);
      setExercisePlan(null);  // clear stale plan
    } catch {
      const ga = computeGapAnalysis(sportKey, demoUserMobility);
      setGapAnalysis(ga);
      setExercisePlan(null);
    } finally {
      setAnalysisLoading(false);
    }
  }

  async function generatePlan(userProfile) {
    if (!selectedSport || !gapAnalysis) return;
    setPlanLoading(true);
    try {
      const { exercisePlan: ep } = await generatePlanRequest(
        selectedSport,
        lastCvResult.current,
        userProfile,
      );
      setExercisePlan(ep);
    } catch {
      setExercisePlan(demoExercisePlan[selectedSport] ?? demoExercisePlan.tennis);
    } finally {
      setPlanLoading(false);
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
      planLoading,
      selectSport,
      loadSportPreview,
      runAnalysis,
      generatePlan,
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
