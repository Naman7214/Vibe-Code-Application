import React, { useState } from 'react';
import { Wrench, FileText, Zap } from 'lucide-react';

const Step1IdeAgent = ({ 
  sessionId,
  setSessionId,
  userQuery,
  setUserQuery,
  onNext, 
  loading, 
  error 
}) => {
  const handleSubmit = (e) => {
    e.preventDefault();
    onNext();
  };

  return (
    <div className="max-w-2xl mx-auto p-6">
      <div className="text-center mb-8">
        <div className="inline-flex items-center justify-center w-16 h-16 bg-orange-100 rounded-full mb-4">
          <Wrench className="w-8 h-8 text-orange-600" />
        </div>
        <h2 className="text-3xl font-bold text-gray-900 mb-2">IDE Agent Assistant</h2>
        <p className="text-gray-600">
          Get AI assistance for debugging, fixing, or modifying your existing project
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
            The session ID of the project you want to work with
          </p>
        </div>

        {/* User Query Input */}
        <div>
          <label htmlFor="userQuery" className="block text-sm font-medium text-gray-700 mb-2">
            Your Request
          </label>
          <textarea
            id="userQuery"
            value={userQuery}
            onChange={(e) => setUserQuery(e.target.value)}
            placeholder={`Describe what you need help with:

Examples:
• Fix the navigation bug on the homepage
• Add dark mode support to the application
• The build is failing with TypeScript errors
• Update the color scheme to use blue instead of green
• Add a new button to the header component
• The API calls are not working properly`}
            rows={8}
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent resize-none"
            required
          />
          <p className="text-xs text-gray-500 mt-1">
            Be specific about what you need help with for better results
          </p>
        </div>

        {/* Info Boxes */}
        <div className="space-y-4">
          {/* Capabilities */}
          <div className="bg-green-50 border border-green-200 rounded-lg p-4">
            <div className="flex items-start">
              <Zap className="w-5 h-5 text-green-600 mt-0.5 mr-3 flex-shrink-0" />
              <div className="text-sm">
                <h3 className="font-semibold text-green-900 mb-1">IDE Agent Capabilities</h3>
                <ul className="list-disc list-inside text-green-800 space-y-1">
                  <li>Debug and fix code errors</li>
                  <li>Modify existing components and features</li>
                  <li>Add new functionality to your project</li>
                  <li>Update styling and UI elements</li>
                  <li>Fix build and compilation issues</li>
                  <li>Optimize code performance</li>
                </ul>
              </div>
            </div>
          </div>

          {/* How it works */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <div className="flex items-start">
              <FileText className="w-5 h-5 text-blue-600 mt-0.5 mr-3 flex-shrink-0" />
              <div className="text-sm">
                <h3 className="font-semibold text-blue-900 mb-1">How It Works</h3>
                <p className="text-blue-800">
                  The IDE agent will analyze your existing project files, understand your request, 
                  and make the necessary changes using intelligent code analysis and modification tools.
                </p>
              </div>
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
          disabled={loading || !sessionId.trim() || !userQuery.trim()}
          className="w-full flex items-center justify-center px-6 py-3 bg-orange-600 text-white font-semibold rounded-lg hover:bg-orange-700 focus:ring-2 focus:ring-orange-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {loading ? (
            <>
              <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
              Processing...
            </>
          ) : (
            <>
              <Wrench className="w-5 h-5 mr-2" />
              Get AI Assistance
            </>
          )}
        </button>
      </form>
    </div>
  );
};

export default Step1IdeAgent; 