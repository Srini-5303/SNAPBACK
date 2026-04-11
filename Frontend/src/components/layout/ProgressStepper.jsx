import './ProgressStepper.css';

const STEPS = [
  { label: 'Select Sport', path: '/' },
  { label: 'Record Movement', path: '/record' },
  { label: 'View Analysis', path: '/analysis' },
  { label: 'Get Plan', path: '/plan' },
];

function getStepIndex(pathname) {
  if (pathname === '/plan')     return 3;
  if (pathname === '/analysis') return 2;
  if (pathname === '/record')   return 1;
  return 0;
}

export default function ProgressStepper({ currentPath }) {
  const activeIndex = getStepIndex(currentPath);

  return (
    <div className="stepper-wrapper">
      <div className="stepper page-container">
        {STEPS.map((step, i) => {
          const isCompleted = i < activeIndex;
          const isActive    = i === activeIndex;

          return (
            <div key={step.path} className="stepper-item">
              {i > 0 && (
                <div className={`stepper-line ${isCompleted ? 'completed' : ''}`} />
              )}
              <div className={`stepper-node ${isActive ? 'active' : ''} ${isCompleted ? 'completed' : ''}`}>
                {isCompleted ? (
                  <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
                    <path d="M2 6l3 3 5-5" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                  </svg>
                ) : (
                  <span>{i + 1}</span>
                )}
              </div>
              <span className={`stepper-label ${isActive ? 'active' : ''} ${isCompleted ? 'completed' : ''}`}>
                {step.label}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
