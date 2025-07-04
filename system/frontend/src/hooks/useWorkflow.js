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

  // Utility function to parse build errors from validation results
  const parseBuildErrorsFromResponse = (response) => {
    if (!response || !response.message) return null;
    
    // Check if the message contains "Code validation failed with errors"
    if (response.message.includes('Code validation failed with errors')) {
      // Try to extract validation results if they exist
      try {
        // Look for validation_results in the response
        if (response.validation_results) {
          const validationResults = response.validation_results;
          
          if (validationResults.validation_results && Array.isArray(validationResults.validation_results)) {
            let errorMessages = [];
            
            validationResults.validation_results.forEach(result => {
              if (result.has_errors && result.error_details) {
                // Add command and description context
                errorMessages.push(`Command: ${result.command}`);
                if (result.description) {
                  errorMessages.push(`Description: ${result.description}`);
                }
                
                // Add the raw output which contains the actual error
                if (result.error_details.raw_output) {
                  errorMessages.push('Build Error Output:');
                  errorMessages.push(result.error_details.raw_output);
                }
                
                // Add parsed errors if available
                if (result.error_details.parsed_errors && Array.isArray(result.error_details.parsed_errors)) {
                  result.error_details.parsed_errors.forEach(error => {
                    if (error.error_line) {
                      errorMessages.push(`\nError: ${error.error_line}`);
                      if (error.file_path) {
                        errorMessages.push(`File: ${error.file_path}`);
                      }
                    }
                  });
                }
              }
            });
            
            return errorMessages.length > 0 ? errorMessages.join('\n') : null;
          }
        }
      } catch (e) {
        console.warn('Failed to parse validation results:', e);
      }
      
      // Fallback: return the error message as is
      return response.message;
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
      
      // Check for build errors in the response
      const buildErrors = parseBuildErrorsFromResponse(response);
      
      if (buildErrors) {
        console.log('Build errors detected, automatically triggering IDE agent...');
        
        // Automatically trigger IDE agent to fix the build errors
        setLoading(true); // Keep loading state for seamless transition
        
        try {
          const errorMessage = `The build failed with the following errors. Please analyze and fix them:\n\n${buildErrors}`;
          const ideResponse = await apiService.ideAgent(sessionId, errorMessage, platformType);
          
          if (ideResponse.success) {
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
      } else if (response.error) {
        // Other types of errors (not build errors)
        throw new Error(response.error);
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