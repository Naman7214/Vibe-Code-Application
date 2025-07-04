import React from 'react';
import { CheckCircle, Folder, RotateCcw, Copy } from 'lucide-react';

const Step5Completion = ({ 
  codebasePath, 
  sessionId, 
  selectedScreens, 
  platformType, 
  onReset 
}) => {
  const selectedScreenList = Object.keys(selectedScreens);

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    // You could add a toast notification here
  };

  return (
    <div className="max-w-3xl mx-auto p-6">
      <div className="text-center mb-8">
        <div className="inline-flex items-center justify-center w-16 h-16 bg-green-100 rounded-full mb-4">
          <CheckCircle className="w-8 h-8 text-green-600" />
        </div>
        <h2 className="text-3xl font-bold text-gray-900 mb-2">Code Generation Complete!</h2>
        <p className="text-gray-600">
          Your {platformType} application has been successfully generated and is ready to use.
        </p>
      </div>

      {/* Success Summary */}
      <div className="bg-green-50 border border-green-200 rounded-lg p-6 mb-6">
        <h3 className="text-lg font-semibold text-green-900 mb-4">Generation Summary</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-green-700">{selectedScreenList.length}</div>
            <div className="text-sm text-green-600">Screens Generated</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-green-700 capitalize">{platformType}</div>
            <div className="text-sm text-green-600">Platform</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-green-700">✓</div>
            <div className="text-sm text-green-600">Build Verified</div>
          </div>
        </div>

        <div className="border-t border-green-200 pt-4">
          <h4 className="font-medium text-green-800 mb-2">Generated Screens:</h4>
          <div className="flex flex-wrap gap-2">
            {selectedScreenList.map((screenName) => (
              <span
                key={screenName}
                className="px-3 py-1 bg-green-100 text-green-800 text-sm rounded-full"
              >
                {screenName.replace(/_/g, ' ')}
              </span>
            ))}
          </div>
        </div>
      </div>

      {/* Codebase Path */}
      <div className="bg-gray-50 border border-gray-200 rounded-lg p-6 mb-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
          <Folder className="w-5 h-5 mr-2" />
          Codebase Location
        </h3>
        
        <div className="bg-white border border-gray-300 rounded-lg p-4">
          <div className="flex items-center justify-between">
            <code className="text-sm text-gray-800 font-mono break-all">
              {codebasePath}
            </code>
            <button
              onClick={() => copyToClipboard(codebasePath)}
              className="ml-3 p-2 text-gray-500 hover:text-gray-700 transition-colors"
              title="Copy path"
            >
              <Copy className="w-4 h-4" />
            </button>
          </div>
        </div>

        <div className="mt-4 text-sm text-gray-600">
          <p><strong>Session ID:</strong> {sessionId}</p>
          <p className="mt-1">Navigate to the path above to find your generated {platformType} application files.</p>
        </div>
      </div>

      {/* Next Steps */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
        <h3 className="font-semibold text-blue-900 mb-2">Next Steps</h3>
        <ul className="space-y-1 text-sm text-blue-800">
          {platformType === 'web' ? (
            <>
              <li>• Navigate to the codebase directory</li>
              <li>• Run <code className="bg-blue-100 px-1 rounded">npm install</code> to install dependencies</li>
              <li>• Run <code className="bg-blue-100 px-1 rounded">npm start</code> to start the development server</li>
              <li>• Open your browser to view the application</li>
            </>
          ) : (
            <>
              <li>• Navigate to the codebase directory</li>
              <li>• Run <code className="bg-blue-100 px-1 rounded">flutter pub get</code> to install dependencies</li>
              <li>• Connect your device or start an emulator</li>
              <li>• Run <code className="bg-blue-100 px-1 rounded">flutter run</code> to launch the app</li>
            </>
          )}
        </ul>
      </div>

      {/* Actions */}
      <div className="flex gap-4">
        <button
          onClick={onReset}
          className="flex-1 flex items-center justify-center px-6 py-3 bg-white border border-gray-300 text-gray-700 font-semibold rounded-lg hover:bg-gray-50 focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 transition-colors"
        >
          <RotateCcw className="w-5 h-5 mr-2" />
          Create Another Project
        </button>
        
        <button
          onClick={() => window.open(`file://${codebasePath}`, '_blank')}
          className="flex-1 flex items-center justify-center px-6 py-3 bg-primary-600 text-white font-semibold rounded-lg hover:bg-primary-700 focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 transition-colors"
        >
          <Folder className="w-5 h-5 mr-2" />
          Open Codebase Folder
        </button>
      </div>
    </div>
  );
};

export default Step5Completion; 