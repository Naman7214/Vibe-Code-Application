import React from 'react';
import { AlertTriangle, Wrench, ArrowRight } from 'lucide-react';

const Step4ErrorFixing = ({ 
  buildErrors, 
  onNext, 
  loading, 
  error 
}) => {
  const handleSubmit = (e) => {
    e.preventDefault();
    onNext(buildErrors);
  };

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="text-center mb-8">
        <div className="inline-flex items-center justify-center w-16 h-16 bg-yellow-100 rounded-full mb-4">
          <AlertTriangle className="w-8 h-8 text-yellow-600" />
        </div>
        <h2 className="text-3xl font-bold text-gray-900 mb-2">Build Errors Detected</h2>
        <p className="text-gray-600">
          Some compilation errors were found. Our IDE agent will fix them automatically.
        </p>
      </div>

      {/* Build Errors Display */}
      <div className="bg-red-50 border border-red-200 rounded-lg p-6 mb-6">
        <h3 className="text-lg font-semibold text-red-900 mb-4 flex items-center">
          <AlertTriangle className="w-5 h-5 mr-2" />
          Build Errors Found
        </h3>
        
        <div className="bg-white border border-red-200 rounded p-4">
          <pre className="text-sm text-red-800 whitespace-pre-wrap overflow-x-auto">
            {buildErrors || 'Error details will be displayed here...'}
          </pre>
        </div>
      </div>

      {/* What's Happening */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
        <h3 className="font-semibold text-blue-900 mb-2 flex items-center">
          <Wrench className="w-5 h-5 mr-2" />
          Automatic Error Resolution
        </h3>
        <ul className="space-y-1 text-sm text-blue-800">
          <li>• Our AI-powered IDE agent will analyze the build errors</li>
          <li>• Common issues like missing imports, syntax errors, and type mismatches will be fixed</li>
          <li>• The codebase will be updated with the corrections</li>
          <li>• Build validation will run again to ensure everything compiles properly</li>
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
          className="w-full flex items-center justify-center px-6 py-3 bg-yellow-600 text-white font-semibold rounded-lg hover:bg-yellow-700 focus:ring-2 focus:ring-yellow-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {loading ? (
            <>
              <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
              Fixing Errors...
            </>
          ) : (
            <>
              <Wrench className="w-5 h-5 mr-2" />
              Fix Errors with IDE Agent
              <ArrowRight className="w-5 h-5 ml-2" />
            </>
          )}
        </button>
      </form>

      {/* Progress Indicator */}
      {loading && (
        <div className="mt-6">
          <div className="bg-gray-200 rounded-full h-2">
            <div className="bg-yellow-600 h-2 rounded-full animate-pulse" style={{width: '75%'}}></div>
          </div>
          <p className="text-center text-sm text-gray-600 mt-2">
            IDE agent is analyzing and fixing the errors...
          </p>
        </div>
      )}
    </div>
  );
};

export default Step4ErrorFixing; 