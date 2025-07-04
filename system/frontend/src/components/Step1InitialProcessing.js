import React from 'react';
import { Play, FileText } from 'lucide-react';

const Step1InitialProcessing = ({ 
  userQuery, 
  setUserQuery, 
  platformType, 
  setPlatformType, 
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
        <div className="inline-flex items-center justify-center w-16 h-16 bg-primary-100 rounded-full mb-4">
          <FileText className="w-8 h-8 text-primary-600" />
        </div>
        <h2 className="text-3xl font-bold text-gray-900 mb-2">Create New Codebase</h2>
        <p className="text-gray-600">
          Describe your application idea and select the platform type to get started
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* User Query Input */}
        <div>
          <label htmlFor="userQuery" className="block text-sm font-medium text-gray-700 mb-2">
            Application Description
          </label>
          <textarea
            id="userQuery"
            value={userQuery}
            onChange={(e) => setUserQuery(e.target.value)}
            placeholder="Describe your application idea (e.g., 'Build a coffee shop app with menu, ordering, and location features')"
            rows={4}
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent resize-none"
            required
          />
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

        {/* Error Display */}
        {error && (
          <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-red-600 text-sm">{error}</p>
          </div>
        )}

        {/* Submit Button */}
        <button
          type="submit"
          disabled={loading || !userQuery.trim()}
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
              Start Processing
            </>
          )}
        </button>
      </form>
    </div>
  );
};

export default Step1InitialProcessing; 