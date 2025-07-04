import React, { useState } from 'react';
import { Play, Plus, FileText } from 'lucide-react';

const Step1FollowUpSession = ({ 
  sessionId,
  setSessionId,
  dictOfScreens,
  setDictOfScreens,
  platformType, 
  setPlatformType, 
  onNext, 
  loading, 
  error 
}) => {
  const [screensText, setScreensText] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    
    // Parse the screens input
    try {
      let parsedScreens = {};
      
      if (screensText.trim()) {
        // Try to parse as JSON first
        try {
          parsedScreens = JSON.parse(screensText);
        } catch {
          // If not JSON, treat as line-separated screen names
          const lines = screensText.split('\n').filter(line => line.trim());
          lines.forEach(line => {
            const [name, description] = line.split(':').map(s => s.trim());
            if (name) {
              parsedScreens[name] = description || `${name} screen`;
            }
          });
        }
      }
      
      setDictOfScreens(parsedScreens);
      onNext();
    } catch (error) {
      console.error('Error parsing screens:', error);
    }
  };

  const handleScreensChange = (e) => {
    setScreensText(e.target.value);
  };

  return (
    <div className="max-w-2xl mx-auto p-6">
      <div className="text-center mb-8">
        <div className="inline-flex items-center justify-center w-16 h-16 bg-blue-100 rounded-full mb-4">
          <Plus className="w-8 h-8 text-blue-600" />
        </div>
        <h2 className="text-3xl font-bold text-gray-900 mb-2">Project Context Setup</h2>
        <p className="text-gray-600">
          Provide your project details to begin context gathering
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Session ID Input */}
        <div>
          <label htmlFor="sessionId" className="block text-sm font-medium text-gray-700 mb-2">
            Session ID
          </label>
          <input
            id="sessionId"
            type="text"
            value={sessionId}
            onChange={(e) => setSessionId(e.target.value)}
            placeholder="Enter your existing session ID (e.g., a353764f-a5d7-46db-b8d1-e6d073eb5bb3)"
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            required
          />
          <p className="text-xs text-gray-500 mt-1">
            Find this in your previous generation results or artifacts folder
          </p>
        </div>

        {/* Platform Type Selection */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-3">
            Platform Type
          </label>
          <div className="grid grid-cols-2 gap-4">
            <button
              type="button"
              onClick={() => setPlatformType('web')}
              className={`p-4 border-2 rounded-lg text-left transition-all ${
                platformType === 'web'
                  ? 'border-primary-500 bg-primary-50 text-primary-700'
                  : 'border-gray-200 hover:border-gray-300'
              }`}
            >
              <div className="font-semibold">Web Application</div>
              <div className="text-sm text-gray-500 mt-1">
                React-based web application
              </div>
            </button>
            
            <button
              type="button"
              onClick={() => setPlatformType('mobile')}
              className={`p-4 border-2 rounded-lg text-left transition-all ${
                platformType === 'mobile'
                  ? 'border-primary-500 bg-primary-50 text-primary-700'
                  : 'border-gray-200 hover:border-gray-300'
              }`}
            >
              <div className="font-semibold">Mobile Application</div>
              <div className="text-sm text-gray-500 mt-1">
                Flutter-based mobile app
              </div>
            </button>
          </div>
        </div>

        {/* Screens Input */}
        <div>
          <label htmlFor="screens" className="block text-sm font-medium text-gray-700 mb-2">
            Screens to Add
          </label>
          <textarea
            id="screens"
            value={screensText}
            onChange={handleScreensChange}
            placeholder={`Enter screens in one of these formats:

JSON format:
{
  "settings_page": "User settings and preferences screen",
  "notifications": "Push notifications management screen"
}

Line format:
settings_page: User settings and preferences screen
notifications: Push notifications management screen

Simple format:
settings_page
notifications`}
            rows={8}
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent resize-none font-mono text-sm"
            required
          />
          <p className="text-xs text-gray-500 mt-1">
            Supports JSON format, line format (name: description), or simple screen names
          </p>
        </div>

        {/* Info Box */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex items-start">
            <FileText className="w-5 h-5 text-blue-600 mt-0.5 mr-3 flex-shrink-0" />
            <div className="text-sm">
              <h3 className="font-semibold text-blue-900 mb-1">Context Gathering Process</h3>
              <p className="text-blue-800">
                This will start the context gathering process for your existing project. We will:
              </p>
              <ul className="list-disc list-inside text-blue-700 mt-2 space-y-1">
                <li>Load your existing project context</li>
                <li>Analyze requirements for the new screens</li>
                <li>Gather context for seamless integration</li>
                <li>Prepare for code generation</li>
              </ul>
            </div>
          </div>
        </div>

        {/* Error Display */}
        {error && (
          <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-red-600 text-sm">{error}</p>
          </div>
        )}

        {/* Submit Button */}
        <button
          type="submit"
          disabled={loading || !sessionId.trim() || !screensText.trim()}
          className="w-full flex items-center justify-center px-6 py-3 bg-primary-600 text-white font-semibold rounded-lg hover:bg-primary-700 focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {loading ? (
            <>
              <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
              Processing...
            </>
          ) : (
            <>
              <Play className="w-5 h-5 mr-2" />
              Start Context Gathering
            </>
          )}
        </button>
      </form>
    </div>
  );
};

export default Step1FollowUpSession; 