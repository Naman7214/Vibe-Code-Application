import React from 'react';
import { Code, ArrowRight, CheckCircle } from 'lucide-react';

const Step3CodeGeneration = ({ 
  selectedScreens, 
  platformType, 
  onNext, 
  loading, 
  error 
}) => {
  const handleSubmit = (e) => {
    e.preventDefault();
    onNext();
  };

  const selectedScreenList = Object.keys(selectedScreens);

  return (
    <div className="max-w-3xl mx-auto p-6">
      <div className="text-center mb-8">
        <div className="inline-flex items-center justify-center w-16 h-16 bg-primary-100 rounded-full mb-4">
          <Code className="w-8 h-8 text-primary-600" />
        </div>
        <h2 className="text-3xl font-bold text-gray-900 mb-2">Generate Code</h2>
        <p className="text-gray-600">
          Ready to generate your {platformType} application with the selected screens
        </p>
      </div>

      {/* Generation Summary */}
      <div className="bg-gray-50 rounded-lg p-6 mb-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Generation Summary</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h4 className="font-medium text-gray-700 mb-2">Platform</h4>
            <div className="flex items-center">
              <div className="w-3 h-3 bg-green-500 rounded-full mr-2"></div>
              <span className="text-gray-900 capitalize">{platformType} Application</span>
            </div>
          </div>
          
          <div>
            <h4 className="font-medium text-gray-700 mb-2">Selected Screens</h4>
            <div className="text-gray-900">{selectedScreenList.length} screens</div>
          </div>
        </div>

        <div className="mt-4">
          <h4 className="font-medium text-gray-700 mb-2">Screens to Generate</h4>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
            {selectedScreenList.map((screenName) => (
              <div key={screenName} className="flex items-center">
                <CheckCircle className="w-4 h-4 text-green-500 mr-2" />
                <span className="text-sm text-gray-700 capitalize">
                  {screenName.replace(/_/g, ' ')}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* What Happens Next */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
        <h3 className="font-semibold text-blue-900 mb-2">What happens next?</h3>
        <ul className="space-y-1 text-sm text-blue-800">
          <li>• Context gathering will be completed for your selected screens</li>
          <li>• Code generation will begin for your {platformType} application</li>
          <li>• Build validation will check for any compilation errors</li>
          <li>• If errors are found, our IDE agent will automatically fix them</li>
          <li>• You'll get the path to your generated codebase</li>
        </ul>
      </div>

      <form onSubmit={handleSubmit}>
        {/* Error Display */}
        {error && (
          <div className="p-4 bg-red-50 border border-red-200 rounded-lg mb-6">
            <p className="text-red-600 text-sm">{error}</p>
          </div>
        )}

        {/* Submit Button */}
        <button
          type="submit"
          disabled={loading}
          className="w-full flex items-center justify-center px-6 py-3 bg-primary-600 text-white font-semibold rounded-lg hover:bg-primary-700 focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {loading ? (
            <>
              <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
              Generating Code...
            </>
          ) : (
            <>
              Start Code Generation
              <ArrowRight className="w-5 h-5 ml-2" />
            </>
          )}
        </button>
      </form>

      {/* Progress Indicator */}
      {loading && (
        <div className="mt-6">
          <div className="bg-gray-200 rounded-full h-2">
            <div className="bg-primary-600 h-2 rounded-full animate-pulse" style={{width: '45%'}}></div>
          </div>
          <p className="text-center text-sm text-gray-600 mt-2">
            This may take a few minutes...
          </p>
        </div>
      )}
    </div>
  );
};

export default Step3CodeGeneration; 