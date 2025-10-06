import React, { useState, useEffect } from 'react';
import Joyride, { STATUS } from 'react-joyride';

const steps = [
  {
    target: '.dashboard-header',
    content: 'Welcome to Flowstate-AI! This is your dashboard header where you can access your profile and settings.',
    disableBeacon: true,
  },
  {
    target: '.new-project-button',
    content: 'Click here to create a new project and start your AI workflow.',
  },
  {
    target: '.projects-list',
    content: 'Here you can find all your projects listed with quick access options.',
  },
  {
    target: '.help-menu',
    content: 'Need help? This menu contains guides, FAQs, and support contact.',
  },
  {
    target: '.footer',
    content: 'That’s it for the tour! Remember, you can rerun this onboarding anytime from the Help menu.',
  },
];

function OnboardingTour() {
  const [run, setRun] = useState(false);
  const [stepsState, setStepsState] = useState(steps);

  useEffect(() => {
    const onboardingCompleted = localStorage.getItem('flowstateOnboardingComplete');
    if (!onboardingCompleted) {
      setRun(true);
    }
  }, []);

  const handleJoyrideCallback = (data) => {
    const { status, type } = data;
    const finishedStatuses = [STATUS.FINISHED, STATUS.SKIPPED];

    if (finishedStatuses.includes(status)) {
      setRun(false);
      localStorage.setItem('flowstateOnboardingComplete', 'true');
    }
  };

  return (
    <Joyride
      steps={stepsState}
      run={run}
      continuous={true}
      scrollToFirstStep={true}
      showProgress={true}
      showSkipButton={true}
      styles={{
        options: {
          zIndex: 10000,
        },
      }}
      callback={handleJoyrideCallback}
    />
  );
}

export default OnboardingTour;
