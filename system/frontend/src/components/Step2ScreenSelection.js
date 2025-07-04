import React from 'react';
import { CheckSquare, Square, ArrowRight, Info } from 'lucide-react';

const Step2ScreenSelection = ({ 
  initialData, 
  selectedScreens, 
  toggleScreenSelection, 
  onNext, 
  loading, 
  error 
}) => {
  const handleSubmit = (e) => {
    e.preventDefault();
    onNext();
  };

  const selectedCount = Object.keys(selectedScreens).length;
  const totalScreens = Object.keys(initialData?.screens || {}).length;

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="text-center mb-8">
        <div className="inline-flex items-center justify-center w-16 h-16 bg-primary-100 rounded-full mb-4">
          <CheckSquare className="w-8 h-8 text-primary-600" />
        </div>
        <h2 className="text-3xl font-bold text-gray-900 mb-2">Select Screens</h2>
        <p className="text-gray-600">
          Choose the screens you want to generate for your {initialData?.domain} application
        </p>
      </div>

      {/* Project Info */}
      {initialData && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
          <div className="flex items-start">
            <Info className="w-5 h-5 text-blue-600 mt-0.5 mr-3 flex-shrink-0" />
            <div>
              <h3 className="font-semibold text-blue-900 mb-2">Project Overview</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="font-medium text-blue-800">Domain:</span>{' '}
                  <span className="text-blue-700 capitalize">{initialData.domain}</span>
                </div>
                <div>
                  <span className="font-medium text-blue-800">Business Type:</span>{' '}
                  <span className="text-blue-700">{initialData.business_type || 'Not specified'}</span>
                </div>
              </div>
              {initialData.project_context && (
                <div className="mt-2 text-sm">
                  <span className="font-medium text-blue-800">Project Description:</span>{' '}
                  <span className="text-blue-700">{initialData.project_context.substring(0, 200)}...</span>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      <form onSubmit={handleSubmit}>
        {/* Screen Selection */}
        <div className="mb-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">
              Available Screens ({selectedCount}/{totalScreens} selected)
            </h3>
            <div className="text-sm text-gray-500">
              Select at least one screen to continue
            </div>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {Object.entries(initialData?.screens || {}).map(([screenName, description]) => {
              const isSelected = selectedScreens[screenName];
              
              return (
                <button
                  key={screenName}
                  type="button"
                  onClick={() => toggleScreenSelection(screenName)}
                  className={`p-4 border-2 rounded-lg text-left transition-all ${
                    isSelected
                      ? 'border-primary-500 bg-primary-50'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                >
                  <div className="flex items-start justify-between mb-2">
                    <h4 className={`font-semibold capitalize ${
                      isSelected ? 'text-primary-700' : 'text-gray-900'
                    }`}>
                      {screenName.replace(/_/g, ' ')}
                    </h4>
                    {isSelected ? (
                      <CheckSquare className="w-5 h-5 text-primary-600 flex-shrink-0" />
                    ) : (
                      <Square className="w-5 h-5 text-gray-400 flex-shrink-0" />
                    )}
                  </div>
                  <p className={`text-sm ${
                    isSelected ? 'text-primary-600' : 'text-gray-600'
                  }`}>
                    {description}
                  </p>
                </button>
              );
            })}
          </div>
        </div>

        {/* Industry Patterns */}
        {initialData?.industry_patterns && initialData.industry_patterns.length > 0 && (
          <div className="mb-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-3">Industry Patterns</h3>
            <div className="bg-gray-50 rounded-lg p-4">
              <ul className="space-y-2">
                {initialData.industry_patterns.map((pattern, index) => (
                  <li key={index} className="flex items-start">
                    <div className="w-2 h-2 bg-primary-500 rounded-full mt-2 mr-3 flex-shrink-0"></div>
                    <span className="text-sm text-gray-700">{pattern}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        )}

        {/* Error Display */}
        {error && (
          <div className="p-4 bg-red-50 border border-red-200 rounded-lg mb-6">
            <p className="text-red-600 text-sm">{error}</p>
          </div>
        )}

        {/* Submit Button */}
        <button
          type="submit"
          disabled={loading || selectedCount === 0}
          className="w-full flex items-center justify-center px-6 py-3 bg-primary-600 text-white font-semibold rounded-lg hover:bg-primary-700 focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {loading ? (
            <>
              <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
              Gathering Context...
            </>
          ) : (
            <>
              Continue to Context Gathering
              <ArrowRight className="w-5 h-5 ml-2" />
            </>
          )}
        </button>
      </form>
    </div>
  );
};

export default Step2ScreenSelection; 