import { createContext, useContext, useState } from 'react';
import { demoUserMobility } from '../data/demoUserMobility.js';
import { demoExercisePlan } from '../data/demoExercisePlan.js';
import { computeGapAnalysis } from '../utils/gapAnalysis.js';

const AppContext = createContext(null);

export function AppProvider({ children }) {
  const [selectedSport, setSelectedSport] = useState(null);
  const [gapAnalysis, setGapAnalysis]     = useState(null);
  const [exercisePlan, setExercisePlan]   = useState(null);

  function selectSport(sportKey) {
    setSelectedSport(sportKey);
  }

  function runAnalysis(sportKey) {
    const analysis = computeGapAnalysis(sportKey, demoUserMobility);
    setGapAnalysis(analysis);
    const plan = demoExercisePlan[sportKey] ?? demoExercisePlan.tennis;
    setExercisePlan(plan);
  }

  function switchSport(sportKey) {
    setSelectedSport(sportKey);
    runAnalysis(sportKey);
  }

  return (
    <AppContext.Provider value={{
      selectedSport,
      gapAnalysis,
      exercisePlan,
      selectSport,
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
