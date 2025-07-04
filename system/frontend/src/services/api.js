import axios from 'axios';

const API_BASE_URL = 'http://127.0.0.1:8000/api/v1';

// Create axios instance with default configuration
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 1200000, // 20 minutes timeout (20 * 60 * 1000)
});

// Request interceptor for logging
api.interceptors.request.use(
  (config) => {
    console.log(`Making ${config.method?.toUpperCase()} request to ${config.url}`);
    return config;
  },
  (error) => {
    console.error('Request error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    console.error('Response error:', error);
    return Promise.reject(error);
  }
);

// API Service functions
export const apiService = {
  // Step 1: Initial Processing
  async initialProcessing(userQuery, platformType) {
    try {
      const response = await api.post('/initial-processing', {
        user_query: userQuery,
        platform_type: platformType
      });
      return response.data;
    } catch (error) {
      throw new Error(`Initial processing failed: ${error.response?.data?.message || error.message}`);
    }
  },

  // Step 2: Context Gathering
  async contextGathering(sessionId, userQuery, selectedScreens, platformType, isFollowUp = false) {
    try {
      const response = await api.post('/context-gathering', {
        user_query: userQuery,
        dict_of_screens: selectedScreens,
        is_follow_up: isFollowUp,
        platform_type: platformType
      }, {
        headers: {
          'X-Session-ID': sessionId
        }
      });
      return response.data;
    } catch (error) {
      throw new Error(`Context gathering failed: ${error.response?.data?.message || error.message}`);
    }
  },

  // Step 3: Code Generation
  async generateCode(sessionId, selectedScreens, platformType, isFollowUp = false) {
    try {
      const response = await api.post('/generate-code', {
        dict_of_screens: selectedScreens,
        is_follow_up: isFollowUp,
        platform_type: platformType
      }, {
        headers: {
          'X-Session-ID': sessionId
        }
      });
      return response.data;
    } catch (error) {
      throw new Error(`Code generation failed: ${error.response?.data?.message || error.message}`);
    }
  },

  // Step 4: IDE Agent (for error fixing and general assistance)
  async ideAgent(sessionId, userQuery, platformType) {
    try {
      const response = await api.post('/ide-agent', {
        user_query: userQuery
      }, {
        headers: {
          'X-Session-ID': sessionId
        }
      });
      
      // Handle the standardized response format
      const data = response.data;
      
      // The response should have this format:
      // {
      //   "success": true,
      //   "message": "Final agent response or summary",
      //   "tool_calls_used": 15,
      //   "completion_reason": "exit_tool|natural_completion|max_tool_calls|error",
      //   "session_id": "session_id",
      //   "error": null
      // }
      
      console.log('IDE Agent Response:', data);
      
      return data;
    } catch (error) {
      // If there's a network or other error, format it to match the expected structure
      const errorResponse = {
        success: false,
        message: `IDE agent request failed: ${error.response?.data?.message || error.message}`,
        tool_calls_used: 0,
        completion_reason: 'error',
        session_id: sessionId,
        error: error.response?.data?.message || error.message
      };
      
      console.error('IDE Agent Error:', errorResponse);
      
      // Return the error response instead of throwing, so the UI can handle it properly
      return errorResponse;
    }
  }
};

export default api; 