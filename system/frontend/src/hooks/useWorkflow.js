import { useState, useEffect } from 'react';
import { apiService } from '../services/api';

export const useWorkflow = () => {
  const [currentStep, setCurrentStep] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  
  // Workflow mode: 'new', 'followup', or 'ide'
  const [workflowMode, setWorkflowMode] = useState('new');
  
  // Workflow data
  const [userQuery, setUserQuery] = useState('');
  const [platformType, setPlatformType] = useState('web');
  const [sessionId, setSessionId] = useState('');
  const [initialData, setInitialData] = useState(null);
  const [selectedScreens, setSelectedScreens] = useState({});
  const [dictOfScreens, setDictOfScreens] = useState({});
  const [codebasePath, setCodebasePath] = useState('');
  const [ideAgentResponse, setIdeAgentResponse] = useState(null);

  // Auto-trigger context gathering for follow-up workflow
  useEffect(() => {
    if (workflowMode === 'followup' && currentStep === 3 && !loading && Object.keys(dictOfScreens).length > 0) {
      // Auto-run context gathering for follow-up workflow
      const autoRunContextGathering = async () => {
        const screensToProcess = dictOfScreens;
        
        if (Object.keys(screensToProcess).length === 0) {
          setError('Please provide screens to add');
          return false;
        }

        setLoading(true);
        setError(null);

        try {
          const isFollowUp = true;
          const queryToUse = 'Follow-up screen generation';
          
          const response = await apiService.contextGathering(sessionId, queryToUse, screensToProcess, platformType, isFollowUp);
          
          if (response.error) {
            throw new Error(response.error);
          }

          setCurrentStep(4);
          return true;
        } catch (error) {
          setError(error.message || 'An unexpected error occurred');
          setLoading(false);
          return false;
        } finally {
          setLoading(false);
        }
      };
      autoRunContextGathering();
    }
  }, [currentStep, workflowMode, dictOfScreens, loading, sessionId, platformType]);

  const resetWorkflow = () => {
    setCurrentStep(0);
    setLoading(false);
    setError(null);
    setWorkflowMode('new');
    setUserQuery('');
    setPlatformType('web');
    setSessionId('');
    setInitialData(null);
    setSelectedScreens({});
    setDictOfScreens({});
    setCodebasePath('');
    setIdeAgentResponse(null);
  };

  const startFollowUpWorkflow = () => {
    setWorkflowMode('followup');
    setCurrentStep(1);
    setLoading(false);
    setError(null);
    setUserQuery('');
    setPlatformType('web');
    setSessionId('');
    setInitialData(null);
    setSelectedScreens({});
    setDictOfScreens({});
    setCodebasePath('');
    setIdeAgentResponse(null);
  };

  const startNewWorkflow = () => {
    setWorkflowMode('new');
    setCurrentStep(1);
    setLoading(false);
    setError(null);
    setUserQuery('');
    setPlatformType('web');
    setSessionId('');
    setInitialData(null);
    setSelectedScreens({});
    setDictOfScreens({});
    setCodebasePath('');
    setIdeAgentResponse(null);
  };

  const startIdeWorkflow = () => {
    setWorkflowMode('ide');
    setCurrentStep(1);
    setLoading(false);
    setError(null);
    setUserQuery('');
    setPlatformType('web');
    setSessionId('');
    setInitialData(null);
    setSelectedScreens({});
    setDictOfScreens({});
    setCodebasePath('');
    setIdeAgentResponse(null);
  };

  const handleError = (error) => {
    setError(error.message || 'An unexpected error occurred');
    setLoading(false);
  };

  // Step 1: Initial Processing (only for new workflow)
  const runInitialProcessing = async () => {
    if (!userQuery.trim()) {
      setError('Please enter a user query');
      return false;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await apiService.initialProcessing(userQuery, platformType);
      
      if (response.error) {
        throw new Error(response.error);
      }

      setInitialData(response.data);
      setSessionId(response.session_id);
      setCurrentStep(2);
      return true;
    } catch (error) {
      handleError(error);
      return false;
    } finally {
      setLoading(false);
    }
  };

  // Step 1 Follow-up: Process dict of screens input
  const runFollowUpProcessing = async () => {
    if (!sessionId.trim()) {
      setError('Please enter a session ID');
      return false;
    }

    if (Object.keys(dictOfScreens).length === 0) {
      setError('Please provide screens to add');
      return false;
    }

    setLoading(true);
    setError(null);

    try {
      // For follow-up, we use the provided dictOfScreens as selectedScreens
      setSelectedScreens(dictOfScreens);
      // Skip to step 3 (context gathering for follow-up)
      setCurrentStep(3);
      return true;
    } catch (error) {
      handleError(error);
      return false;
    } finally {
      setLoading(false);
    }
  };

  // Step 1 IDE: Process IDE agent request
  const runIdeAgentProcessing = async () => {
    if (!sessionId.trim()) {
      setError('Please enter a session ID');
      return false;
    }

    if (!userQuery.trim()) {
      setError('Please describe what you need help with');
      return false;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await apiService.ideAgent(sessionId, userQuery, platformType);
      
      // Handle the standardized response format
      setIdeAgentResponse(response);
      setCurrentStep(2);
      return true;
    } catch (error) {
      handleError(error);
      return false;
    } finally {
      setLoading(false);
    }
  };

  // Step 2: Context Gathering
  const runContextGathering = async () => {
    const screensToProcess = workflowMode === 'followup' ? dictOfScreens : selectedScreens;
    
    if (Object.keys(screensToProcess).length === 0) {
      setError('Please select at least one screen');
      return false;
    }

    setLoading(true);
    setError(null);

    try {
      const isFollowUp = workflowMode === 'followup';
      const queryToUse = workflowMode === 'followup' ? 'Follow-up screen generation' : userQuery;
      
      const response = await apiService.contextGathering(sessionId, queryToUse, screensToProcess, platformType, isFollowUp);
      
      if (response.error) {
        throw new Error(response.error);
      }

      setCurrentStep(workflowMode === 'followup' ? 4 : 3);
      return true;
    } catch (error) {
      handleError(error);
      return false;
    } finally {
      setLoading(false);
    }
  };

  // Step 3: Code Generation
  const runCodeGeneration = async () => {
    setLoading(true);
    setError(null);

    try {
      const screensToProcess = workflowMode === 'followup' ? dictOfScreens : selectedScreens;
      const isFollowUp = workflowMode === 'followup';
      
      const response = await apiService.generateCode(sessionId, screensToProcess, platformType, isFollowUp);
      
      if (response.error) {
        // If there are build errors, proceed to IDE agent
        setCurrentStep(workflowMode === 'followup' ? 5 : 4);
        return response;
      }

      // Success - show codebase path
      setCodebasePath(`artifacts/${sessionId}/codebase`);
      setCurrentStep(workflowMode === 'followup' ? 6 : 5);
      return response;
    } catch (error) {
      handleError(error);
      return false;
    } finally {
      setLoading(false);
    }
  };

  // Step 4: IDE Agent (Error Fixing)
  const runIdeAgent = async (buildErrors) => {
    setLoading(true);
    setError(null);

    try {
      const errorMessage = `Fix the following build errors:\n${buildErrors}`;
      const response = await apiService.ideAgent(sessionId, errorMessage, platformType);
      
      if (response.error) {
        throw new Error(response.error);
      }

      // After IDE agent fixes, show codebase path
      setCodebasePath(`artifacts/${sessionId}/codebase`);
      setCurrentStep(workflowMode === 'followup' ? 6 : 5);
      return true;
    } catch (error) {
      handleError(error);
      return false;
    } finally {
      setLoading(false);
    }
  };

  const toggleScreenSelection = (screenName) => {
    setSelectedScreens(prev => {
      const newSelection = { ...prev };
      if (newSelection[screenName]) {
        delete newSelection[screenName];
      } else {
        newSelection[screenName] = initialData?.screens[screenName] || '';
      }
      return newSelection;
    });
  };

  return {
    // State
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
    
    // Setters
    setUserQuery,
    setPlatformType,
    setSessionId,
    setDictOfScreens,
    setError,
    
    // Actions
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
  };
}; 