import React from 'react';
import ReactMarkdown from 'react-markdown';
import { CheckCircle, XCircle, Wrench, Clock, Zap, RotateCcw, ExternalLink } from 'lucide-react';

const Step2IdeAgentCompletion = ({ 
  response, 
  sessionId, 
  userQuery,
  onReset 
}) => {
  const getCompletionReasonDisplay = (reason) => {
    const reasons = {
      'exit_tool': { 
        label: 'Tool Exit', 
        bgColor: 'bg-blue-50', 
        borderColor: 'border-blue-200', 
        textColor: 'text-blue-900',
        iconColor: 'text-blue-600',
        badgeColor: 'text-blue-600 bg-blue-100',
        descColor: 'text-blue-700',
        description: 'Agent completed using exit tool' 
      },
      'natural_completion': { 
        label: 'Natural Completion', 
        bgColor: 'bg-green-50', 
        borderColor: 'border-green-200', 
        textColor: 'text-green-900',
        iconColor: 'text-green-600',
        badgeColor: 'text-green-600 bg-green-100',
        descColor: 'text-green-700',
        description: 'Agent completed naturally' 
      },
      'max_tool_calls': { 
        label: 'Max Tool Calls', 
        bgColor: 'bg-orange-50', 
        borderColor: 'border-orange-200', 
        textColor: 'text-orange-900',
        iconColor: 'text-orange-600',
        badgeColor: 'text-orange-600 bg-orange-100',
        descColor: 'text-orange-700',
        description: 'Reached maximum tool usage limit' 
      },
      'error': { 
        label: 'Error', 
        bgColor: 'bg-red-50', 
        borderColor: 'border-red-200', 
        textColor: 'text-red-900',
        iconColor: 'text-red-600',
        badgeColor: 'text-red-600 bg-red-100',
        descColor: 'text-red-700',
        description: 'Completed due to an error' 
      }
    };
    return reasons[reason] || { 
      label: reason, 
      bgColor: 'bg-gray-50', 
      borderColor: 'border-gray-200', 
      textColor: 'text-gray-900',
      iconColor: 'text-gray-600',
      badgeColor: 'text-gray-600 bg-gray-100',
      descColor: 'text-gray-700',
      description: 'Unknown completion reason' 
    };
  };

  const completionInfo = getCompletionReasonDisplay(response?.completion_reason);

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="text-center mb-8">
        <div className={`inline-flex items-center justify-center w-16 h-16 rounded-full mb-4 ${
          response?.success ? 'bg-green-100' : 'bg-red-100'
        }`}>
          {response?.success ? (
            <CheckCircle className="w-8 h-8 text-green-600" />
          ) : (
            <XCircle className="w-8 h-8 text-red-600" />
          )}
        </div>
        <h2 className="text-3xl font-bold text-gray-900 mb-2">
          {response?.success ? 'Task Completed!' : 'Task Failed'}
        </h2>
        <p className="text-gray-600">
          {response?.success 
            ? 'The IDE agent has successfully processed your request'
            : 'The IDE agent encountered an issue while processing your request'
          }
        </p>
      </div>

      <div className="space-y-6">
        {/* Main Response */}
        <div className="bg-white border border-gray-200 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <Wrench className="w-5 h-5 mr-2 text-orange-500" />
            Agent Response
          </h3>
          <div className="prose prose-sm max-w-none">
            <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
              <div className="text-gray-800 leading-relaxed">
                <ReactMarkdown 
                  components={{
                    // Custom styling for code blocks
                    code: ({node, inline, className, children, ...props}) => {
                      return inline ? (
                        <code className="bg-gray-200 px-1 py-0.5 rounded text-sm font-mono" {...props}>
                          {children}
                        </code>
                      ) : (
                        <pre className="bg-gray-800 text-gray-100 p-4 rounded-lg overflow-x-auto">
                          <code className="text-sm font-mono" {...props}>
                            {children}
                          </code>
                        </pre>
                      );
                    },
                    // Custom styling for lists
                    ul: ({children}) => <ul className="list-disc list-inside mb-4 space-y-1">{children}</ul>,
                    ol: ({children}) => <ol className="list-decimal list-inside mb-4 space-y-1">{children}</ol>,
                    // Custom styling for headings
                    h1: ({children}) => <h1 className="text-xl font-bold mb-3 text-gray-900">{children}</h1>,
                    h2: ({children}) => <h2 className="text-lg font-semibold mb-2 text-gray-900">{children}</h2>,
                    h3: ({children}) => <h3 className="text-base font-semibold mb-2 text-gray-900">{children}</h3>,
                    // Custom styling for paragraphs
                    p: ({children}) => <p className="mb-3 leading-relaxed">{children}</p>,
                    // Custom styling for blockquotes
                    blockquote: ({children}) => (
                      <blockquote className="border-l-4 border-blue-500 pl-4 italic text-gray-700 mb-4">
                        {children}
                      </blockquote>
                    ),
                    // Custom styling for links
                    a: ({href, children}) => (
                      <a href={href} className="text-blue-600 hover:text-blue-800 underline" target="_blank" rel="noopener noreferrer">
                        {children}
                      </a>
                    )
                  }}
                >
                  {response?.message || 'No response message available.'}
                </ReactMarkdown>
              </div>
            </div>
          </div>
        </div>

        {/* Stats and Info */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Tool Calls Used */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <Zap className="w-5 h-5 text-blue-600 mr-2" />
                <span className="text-sm font-medium text-blue-900">Tool Calls</span>
              </div>
              <span className="text-lg font-bold text-blue-600">
                {response?.tool_calls_used || 0}
              </span>
            </div>
            <p className="text-xs text-blue-700 mt-1">
              Number of tools executed
            </p>
          </div>

          {/* Completion Reason */}
          <div className={`${completionInfo.bgColor} border ${completionInfo.borderColor} rounded-lg p-4`}>
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <Clock className={`w-5 h-5 ${completionInfo.iconColor} mr-2`} />
                <span className={`text-sm font-medium ${completionInfo.textColor}`}>Status</span>
              </div>
              <span className={`text-xs font-semibold ${completionInfo.badgeColor} px-2 py-1 rounded`}>
                {completionInfo.label}
              </span>
            </div>
            <p className={`text-xs ${completionInfo.descColor} mt-1`}>
              {completionInfo.description}
            </p>
          </div>

          {/* Session Info */}
          <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <ExternalLink className="w-5 h-5 text-gray-600 mr-2" />
                <span className="text-sm font-medium text-gray-900">Session</span>
              </div>
            </div>
            <p className="text-xs text-gray-600 mt-1 font-mono truncate">
              {sessionId}
            </p>
          </div>
        </div>

        {/* Original Request */}
        <div className="bg-gray-50 border border-gray-200 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-3">Your Original Request</h3>
          <div className="bg-white border border-gray-200 rounded-lg p-4">
            <p className="text-gray-700 whitespace-pre-wrap leading-relaxed">
              {userQuery}
            </p>
          </div>
        </div>

        {/* Error Details (if any) */}
        {response?.error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-6">
            <h3 className="text-lg font-semibold text-red-900 mb-3 flex items-center">
              <XCircle className="w-5 h-5 mr-2" />
              Error Details
            </h3>
            <div className="bg-red-100 border border-red-200 rounded-lg p-4">
              <p className="text-red-800 font-mono text-sm">
                {response.error}
              </p>
            </div>
          </div>
        )}

        {/* Project Path */}
        <div className="bg-primary-50 border border-primary-200 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-primary-900 mb-3">Project Location</h3>
          <div className="flex items-center justify-between bg-white border border-primary-200 rounded-lg p-4">
            <div>
              <p className="font-mono text-sm text-gray-800">
                artifacts/{sessionId}/codebase
              </p>
              <p className="text-xs text-gray-500 mt-1">
                Your updated project files are available at this location
              </p>
            </div>
            <ExternalLink className="w-5 h-5 text-primary-600" />
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex flex-col sm:flex-row gap-4 pt-4">
          <button
            onClick={onReset}
            className="flex items-center justify-center px-6 py-3 bg-gray-600 text-white font-semibold rounded-lg hover:bg-gray-700 focus:ring-2 focus:ring-gray-500 focus:ring-offset-2 transition-colors"
          >
            <RotateCcw className="w-5 h-5 mr-2" />
            Start New Task
          </button>
          
          <button
            onClick={() => window.open(`/artifacts/${sessionId}/codebase`, '_blank')}
            className="flex items-center justify-center px-6 py-3 bg-primary-600 text-white font-semibold rounded-lg hover:bg-primary-700 focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 transition-colors"
          >
            <ExternalLink className="w-5 h-5 mr-2" />
            View Project Files
          </button>
        </div>

        {/* Tips */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <h4 className="font-semibold text-blue-900 mb-2">💡 What's Next?</h4>
          <ul className="text-sm text-blue-800 space-y-1">
            <li>• Check your project files for the changes made by the IDE agent</li>
            <li>• Test the modifications to ensure they work as expected</li>
            <li>• Run another IDE agent task if you need additional changes</li>
            <li>• Use the same session ID for follow-up modifications</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default Step2IdeAgentCompletion; 