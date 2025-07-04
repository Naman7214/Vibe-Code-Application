import React, { useState } from 'react';
import { useWorkflow } from '../hooks/useWorkflow';
import WorkflowSelection from './WorkflowSelection';
import Step1InitialProcessing from './Step1InitialProcessing';
import Step1FollowUpSession from './Step1FollowUpSession';
import Step1IdeAgent from './Step1IdeAgent';
import Step2ScreenSelection from './Step2ScreenSelection';
import Step2IdeAgentCompletion from './Step2IdeAgentCompletion';
import Step3CodeGeneration from './Step3CodeGeneration';
import Step4ErrorFixing from './Step4ErrorFixing';
import Step5Completion from './Step5Completion';
import { Plus } from 'lucide-react';

const WorkflowManager = () => {
  const {
    currentStep,
    loading,
    error,
    workflowMode,
    userQuery,
    platformType,
    sessionId,
    initialData,
    selectedScreens,
    dictOfScreens,
    codebasePath,
    ideAgentResponse,
    setUserQuery,
    setPlatformType,
    setSessionId,
    setDictOfScreens,
    setError,
    resetWorkflow,
    startFollowUpWorkflow,
    startNewWorkflow,
    startIdeWorkflow,
    runInitialProcessing,
    runFollowUpProcessing,
    runIdeAgentProcessing,
    runContextGathering,
    runCodeGeneration,
    runIdeAgent,
    toggleScreenSelection,
  } = useWorkflow();



  // Step handlers
  const handleWorkflowSelection = (mode) => {
    if (mode === 'new') {
      startNewWorkflow();
    } else if (mode === 'followup') {
      startFollowUpWorkflow();
    } else if (mode === 'ide') {
      startIdeWorkflow();
    }
  };

  const handleStep1Next = async () => {
    if (workflowMode === 'new') {
      await runInitialProcessing();
    } else if (workflowMode === 'followup') {
      await runFollowUpProcessing();
    } else if (workflowMode === 'ide') {
      await runIdeAgentProcessing();
    }
  };

  const handleStep2Next = async () => {
    await runContextGathering();
  };

  const handleStep3Next = async () => {
    // Code generation now handles build errors automatically
    // If errors occur, the IDE agent will fix them automatically
    // The step progression is handled within the useWorkflow hook
    await runCodeGeneration();
  };

  const handleReset = () => {
    resetWorkflow();
  };

  const getStepsForWorkflow = () => {
    if (workflowMode === 'new') {
      return [
        { number: 1, label: 'Initial Processing', completed: currentStep > 1 },
        { number: 2, label: 'Screen Selection', completed: currentStep > 2 },
        { number: 3, label: 'Code Generation & Auto-fix', completed: currentStep > 3 },
        { number: 4, label: 'Complete', completed: currentStep >= 5 },
      ];
    } else if (workflowMode === 'followup') {
      return [
        { number: 1, label: 'Context Gathering', completed: currentStep > 3 },
        { number: 2, label: 'Code Generation & Auto-fix', completed: currentStep > 4 },
        { number: 3, label: 'Complete', completed: currentStep >= 6 },
      ];
    } else if (workflowMode === 'ide') {
      return [
        { number: 1, label: 'Request Setup', completed: currentStep > 1 },
        { number: 2, label: 'Complete', completed: currentStep >= 2 },
      ];
    }
    return [];
  };

  const getWorkflowTitle = () => {
    const titles = {
      'new': 'New Project Workflow',
      'followup': 'Follow-up Workflow',
      'ide': 'IDE Agent Workflow'
    };
    return titles[workflowMode] || 'Workflow';
  };

  const renderProgressBar = () => {
    // Step 0 is workflow selection
    if (currentStep === 0) return null;

    const steps = getStepsForWorkflow();

    return (
      <div className="max-w-4xl mx-auto mb-8">
        <div className="mb-4 text-center">
          <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-primary-100 text-primary-800">
            {getWorkflowTitle()}
          </span>
        </div>
        <div className="flex items-center justify-between">
          {steps.map((step, index) => (
            <React.Fragment key={step.number}>
              <div className="flex flex-col items-center">
                <div
                  className={`w-10 h-10 rounded-full flex items-center justify-center text-sm font-semibold ${
                    step.completed
                      ? 'bg-primary-600 text-white'
                      : isCurrentStep(step.number)
                      ? 'bg-primary-100 text-primary-600 border-2 border-primary-600'
                      : 'bg-gray-200 text-gray-500'
                  } ${step.optional && !isCurrentStep(step.number) && !step.completed ? 'opacity-50' : ''}`}
                >
                  {step.completed ? '✓' : step.number}
                </div>
                <span
                  className={`text-xs mt-1 text-center ${
                    step.completed || isCurrentStep(step.number)
                      ? 'text-gray-900'
                      : 'text-gray-500'
                  } ${step.optional && !isCurrentStep(step.number) && !step.completed ? 'opacity-50' : ''}`}
                >
                  {step.label}
                  {step.optional && ' (if needed)'}
                </span>
              </div>
              {index < steps.length - 1 && (
                <div
                  className={`flex-1 h-0.5 mx-4 ${
                    step.completed ? 'bg-primary-600' : 'bg-gray-200'
                  }`}
                />
              )}
            </React.Fragment>
          ))}
        </div>
      </div>
    );
  };

  const isCurrentStep = (stepNumber) => {
    if (workflowMode === 'new') {
      return currentStep === stepNumber;
    } else if (workflowMode === 'followup') {
      // Follow-up workflow mapping
      const stepMapping = {
        1: 3, // Context Gathering (step 3 in hook)
        2: 4, // Code Generation & Auto-fix (step 4 in hook)
        3: 6, // Complete (step 6 in hook)
      };
      return currentStep === stepMapping[stepNumber];
    } else if (workflowMode === 'ide') {
      // IDE workflow mapping
      const stepMapping = {
        1: 1, // Request Setup
        2: 2, // Complete
      };
      return currentStep === stepMapping[stepNumber];
    }
    return false;
  };

  const renderCurrentStep = () => {
    // Step 0: Workflow Selection
    if (currentStep === 0) {
      return <WorkflowSelection onSelectWorkflow={handleWorkflowSelection} />;
    }

    if (workflowMode === 'new') {
      switch (currentStep) {
        case 1:
          return (
            <Step1InitialProcessing
              userQuery={userQuery}
              setUserQuery={setUserQuery}
              platformType={platformType}
              setPlatformType={setPlatformType}
              onNext={handleStep1Next}
              loading={loading}
              error={error}
            />
          );
        case 2:
          return (
            <Step2ScreenSelection
              initialData={initialData}
              selectedScreens={selectedScreens}
              toggleScreenSelection={toggleScreenSelection}
              onNext={handleStep2Next}
              loading={loading}
              error={error}
            />
          );
        case 3:
          return (
            <Step3CodeGeneration
              selectedScreens={selectedScreens}
              platformType={platformType}
              onNext={handleStep3Next}
              loading={loading}
              error={error}
            />
          );
        case 5:
          return (
            <Step5Completion
              codebasePath={codebasePath}
              sessionId={sessionId}
              selectedScreens={selectedScreens}
              platformType={platformType}
              onReset={handleReset}
            />
          );
        default:
          return null;
      }
    } else if (workflowMode === 'followup') {
      // Follow-up workflow
      switch (currentStep) {
        case 1:
          return (
            <Step1FollowUpSession
              sessionId={sessionId}
              setSessionId={setSessionId}
              dictOfScreens={dictOfScreens}
              setDictOfScreens={setDictOfScreens}
              platformType={platformType}
              setPlatformType={setPlatformType}
              onNext={handleStep1Next}
              loading={loading}
              error={error}
            />
          );
        case 3:
          // Context gathering step - show session setup form if data not available
          if (!sessionId.trim() || Object.keys(dictOfScreens).length === 0) {
            return (
              <div className="max-w-2xl mx-auto p-6">
                <div className="text-center mb-8">
                  <div className="inline-flex items-center justify-center w-16 h-16 bg-blue-100 rounded-full mb-4">
                    <Plus className="w-8 h-8 text-blue-600" />
                  </div>
                  <h2 className="text-3xl font-bold text-gray-900 mb-2">Context Gathering Portal</h2>
                  <p className="text-gray-600">
                    Add screens to your existing project by providing session details
                  </p>
                </div>
                
                <Step1FollowUpSession
                  sessionId={sessionId}
                  setSessionId={setSessionId}
                  dictOfScreens={dictOfScreens}
                  setDictOfScreens={setDictOfScreens}
                  platformType={platformType}
                  setPlatformType={setPlatformType}
                  onNext={handleStep1Next}
                  loading={loading}
                  error={error}
                />
              </div>
            );
          }
          
          // Show context gathering loading screen when data is available
          return (
            <div className="max-w-2xl mx-auto p-6 text-center">
              <div className="inline-flex items-center justify-center w-16 h-16 bg-blue-100 rounded-full mb-4">
                <svg className="w-8 h-8 text-blue-600 animate-spin" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
              </div>
              <h2 className="text-2xl font-bold text-gray-900 mb-2">Gathering Context</h2>
              <p className="text-gray-600 mb-4">
                Processing your new screens and gathering context from your existing project...
              </p>
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <div className="text-sm text-blue-800">
                  <p className="font-semibold mb-2">Adding screens to your project:</p>
                  <ul className="list-disc list-inside space-y-1">
                    {Object.keys(dictOfScreens).map(screen => (
                      <li key={screen}>{screen}: {dictOfScreens[screen]}</li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>
          );
        case 4:
          return (
            <Step3CodeGeneration
              selectedScreens={dictOfScreens}
              platformType={platformType}
              onNext={handleStep3Next}
              loading={loading}
              error={error}
            />
          );
        case 6:
          return (
            <Step5Completion
              codebasePath={codebasePath}
              sessionId={sessionId}
              selectedScreens={dictOfScreens}
              platformType={platformType}
              onReset={handleReset}
            />
          );
        default:
          return null;
      }
    } else if (workflowMode === 'ide') {
      // IDE Agent workflow
      switch (currentStep) {
        case 1:
          return (
            <Step1IdeAgent
              sessionId={sessionId}
              setSessionId={setSessionId}
              userQuery={userQuery}
              setUserQuery={setUserQuery}
              onNext={handleStep1Next}
              loading={loading}
              error={error}
            />
          );
        case 2:
          return (
            <Step2IdeAgentCompletion
              response={ideAgentResponse}
              sessionId={sessionId}
              userQuery={userQuery}
              onReset={handleReset}
            />
          );
        default:
          return null;
      }
    }

    return null;
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="container mx-auto px-4">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">Velocity.new</h1>
          <p className="text-gray-600">AI-Powered Code Generation Platform</p>
          {currentStep > 0 && (
            <button
              onClick={handleReset}
              className="mt-4 text-sm text-primary-600 hover:text-primary-700 underline"
            >
              ← Start Over
            </button>
          )}
        </div>

        {/* Progress Bar */}
        {renderProgressBar()}

        {/* Current Step */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200">
          {renderCurrentStep()}
        </div>

        {/* Footer */}
        <div className="text-center mt-8 text-sm text-gray-500">
          <p>
            Having issues? Check the console for detailed error logs or contact support.
          </p>
        </div>
      </div>
    </div>
  );
};

export default WorkflowManager; 