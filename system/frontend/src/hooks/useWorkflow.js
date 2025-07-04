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
    // Remove auto-trigger for follow-up workflow since form submission now handles it directly
    // This effect is no longer needed for the follow-up workflow
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
    setCurrentStep(3);
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

  // Step 1: Initial Processing (New Workflow)
  const runInitialProcessing = async () => {
    if (!userQuery.trim()) {
      setError('Please enter a query');
      return false;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await apiService.initialProcessing(userQuery, platformType);
      
      if (response.success === false) {
        throw new Error(response.error || response.message || 'Initial processing failed');
      }

      setSessionId(response.session_id);
      // Extract the actual data from the nested structure
      setInitialData(response.data || response);
      setCurrentStep(2);
      return true;
    } catch (error) {
      handleError(error);
      return false;
    } finally {
      setLoading(false);
    }
  };

  // Step 1: Follow-up Processing (Follow-up Workflow)
  const runFollowUpProcessing = async () => {
    if (!sessionId.trim()) {
      setError('Please enter a session ID');
      return false;
    }

    if (Object.keys(dictOfScreens).length === 0) {
      setError('Please specify at least one screen');
      return false;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await apiService.contextGathering(sessionId, 'Follow-up session', dictOfScreens, platformType, true);
      
      if (response.success === false) {
        throw new Error(response.error || response.message || 'Follow-up processing failed');
      }

      setCurrentStep(4); // Move to code generation step
      return true;
    } catch (error) {
      handleError(error);
      return false;
    } finally {
      setLoading(false);
    }
  };

  // Step 1: IDE Agent Processing (IDE Workflow)
  const runIdeAgentProcessing = async () => {
    if (!userQuery.trim()) {
      setError('Please enter a query');
      return false;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await apiService.ideAgent(sessionId, userQuery, platformType);
      
      // Check if IDE agent succeeded based on the actual response format
      // IDE agent controller returns { data: {...}, message: "...", error: null } on success
      const ideAgentSucceeded = response.error === null || response.error === undefined;
      
      if (!ideAgentSucceeded) {
        throw new Error(response.error || response.message || 'IDE agent processing failed');
      }

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
      
      if (response.success === false) {
        throw new Error(response.error || response.message || 'Context gathering failed');
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

  // Utility function to parse build errors from validation results
  const parseBuildErrorsFromResponse = (response) => {
    if (!response) return null;
    
    // Check if the response indicates a failure
    if (response.success === false) {
      // Check if this is a validation error (build error)
      if (response.message && response.message.includes('Code validation failed with errors')) {
        // With the new simplified format, the error details are directly in the error field
        if (response.error && typeof response.error === 'string') {
          return response.error; // This contains "Command: [command]\nError: [detailed error]"
        }
        
        // Fallback to message if error field is not available
        return response.message;
      }
    }
    
    return null;
  };

  // Step 3: Code Generation
  const runCodeGeneration = async () => {
    setLoading(true);
    setError(null);

    try {
      const screensToProcess = workflowMode === 'followup' ? dictOfScreens : selectedScreens;
      const isFollowUp = workflowMode === 'followup';
      
      const response = await apiService.generateCode(sessionId, screensToProcess, platformType, isFollowUp);
      
      // Check if the response was successful
      if (response.success === false) {
        // Check for build/validation errors
        const buildErrors = parseBuildErrorsFromResponse(response);
        
        if (buildErrors) {
          console.log('Build errors detected, automatically triggering IDE agent...');
          
          // Automatically trigger IDE agent to fix the build errors
          setLoading(true); // Keep loading state for seamless transition
          
          try {
            const errorMessage = `The build failed with the following errors. Please analyze and fix them:\n\n${buildErrors}`;
            const ideResponse = await apiService.ideAgent(sessionId, errorMessage, platformType);
            
            // Check if IDE agent succeeded based on the actual response format
            // IDE agent controller returns { data: {...}, message: "...", error: null } on success
            // and { data: {...}, message: "...", error: "..." } on failure
            const ideAgentSucceeded = ideResponse.error === null || ideResponse.error === undefined;
            
            if (ideAgentSucceeded) {
              // IDE agent successfully fixed the errors
              setCodebasePath(`artifacts/${sessionId}/codebase`);
              setCurrentStep(workflowMode === 'followup' ? 6 : 5);
              console.log('Build errors automatically fixed by IDE agent');
            } else {
              // IDE agent failed to fix the errors
              throw new Error(ideResponse.error || 'IDE agent failed to fix the build errors');
            }
          } catch (ideError) {
            console.error('IDE agent failed:', ideError);
            setError(`Code generation failed with build errors, and automatic fix failed: ${ideError.message}`);
            return false;
          }
        } else {
          // Other types of errors (not build errors)
          throw new Error(response.error || response.message || 'Code generation failed');
        }
      } else {
        // Success - show codebase path
        setCodebasePath(`artifacts/${sessionId}/codebase`);
        setCurrentStep(workflowMode === 'followup' ? 6 : 5);
      }
      
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
      
      // Check if IDE agent succeeded based on the actual response format
      // IDE agent controller returns { data: {...}, message: "...", error: null } on success
      const ideAgentSucceeded = response.error === null || response.error === undefined;
      
      if (!ideAgentSucceeded) {
        throw new Error(response.error || response.message || 'IDE agent failed to fix the build errors');
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