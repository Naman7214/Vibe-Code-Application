import React from 'react';
import { Plus, FileText, ArrowRight, Wrench } from 'lucide-react';
import logo from '../logo.png';

const WorkflowSelection = ({ onSelectWorkflow }) => {
  return (
    <div className="max-w-6xl mx-auto p-6">
      <div className="text-center mb-8">
        <div className="flex items-center justify-center mb-4">
          <div className="logo-container bg-white rounded-xl shadow-sm border border-gray-100 p-3 mr-4">
            <img 
              src={logo} 
              alt="Velocity.new Logo" 
              className="w-10 h-10"
            />
          </div>
          <h2 className="text-3xl font-bold text-gray-900">Choose Workflow</h2>
        </div>
        <p className="text-gray-600">
          Select how you want to proceed with your code generation
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* New Project Workflow */}
        <button
          onClick={() => onSelectWorkflow('new')}
          className="group p-6 border-2 border-gray-200 rounded-lg hover:border-primary-500 hover:bg-primary-50 transition-all text-left"
        >
          <div className="flex items-center justify-between mb-4">
            <div className="inline-flex items-center justify-center w-12 h-12 bg-primary-100 rounded-full group-hover:bg-primary-200 transition-colors">
              <Plus className="w-6 h-6 text-primary-600" />
            </div>
            <ArrowRight className="w-5 h-5 text-gray-400 group-hover:text-primary-500 transition-colors" />
          </div>
          
          <h3 className="text-xl font-semibold text-gray-900 mb-2 group-hover:text-primary-700 transition-colors">
            Create New Project
          </h3>
          
          <p className="text-gray-600 mb-4">
            Start fresh with a new application idea. Get AI-generated screen suggestions and build from scratch.
          </p>
          
          <div className="space-y-2">
            <div className="flex items-center text-sm text-gray-500">
              <div className="w-2 h-2 bg-primary-500 rounded-full mr-2"></div>
              Initial processing & domain analysis
            </div>
            <div className="flex items-center text-sm text-gray-500">
              <div className="w-2 h-2 bg-primary-500 rounded-full mr-2"></div>
              AI-powered screen suggestions
            </div>
            <div className="flex items-center text-sm text-gray-500">
              <div className="w-2 h-2 bg-primary-500 rounded-full mr-2"></div>
              Complete codebase generation
            </div>
            <div className="flex items-center text-sm text-gray-500">
              <div className="w-2 h-2 bg-primary-500 rounded-full mr-2"></div>
              Automatic error fixing
            </div>
          </div>
        </button>

        {/* Follow-up Workflow */}
        <button
          onClick={() => onSelectWorkflow('followup')}
          className="group p-6 border-2 border-gray-200 rounded-lg hover:border-blue-500 hover:bg-blue-50 transition-all text-left"
        >
          <div className="flex items-center justify-between mb-4">
            <div className="inline-flex items-center justify-center w-12 h-12 bg-blue-100 rounded-full group-hover:bg-blue-200 transition-colors">
              <FileText className="w-6 h-6 text-blue-600" />
            </div>
            <ArrowRight className="w-5 h-5 text-gray-400 group-hover:text-blue-500 transition-colors" />
          </div>
          
          <h3 className="text-xl font-semibold text-gray-900 mb-2 group-hover:text-blue-700 transition-colors">
            Add to Existing Project
          </h3>
          
          <p className="text-gray-600 mb-4">
            Continue working on an existing project by adding new screens using your session ID.
          </p>
          
          <div className="space-y-2">
            <div className="flex items-center text-sm text-gray-500">
              <div className="w-2 h-2 bg-blue-500 rounded-full mr-2"></div>
              Use existing project context
            </div>
            <div className="flex items-center text-sm text-gray-500">
              <div className="w-2 h-2 bg-blue-500 rounded-full mr-2"></div>
              Add custom screen specifications
            </div>
            <div className="flex items-center text-sm text-gray-500">
              <div className="w-2 h-2 bg-blue-500 rounded-full mr-2"></div>
              Seamless integration with existing code
            </div>
            <div className="flex items-center text-sm text-gray-500">
              <div className="w-2 h-2 bg-blue-500 rounded-full mr-2"></div>
              Skip initial processing
            </div>
          </div>
        </button>

        {/* IDE Agent Workflow */}
        <button
          onClick={() => onSelectWorkflow('ide')}
          className="group p-6 border-2 border-gray-200 rounded-lg hover:border-orange-500 hover:bg-orange-50 transition-all text-left"
        >
          <div className="flex items-center justify-between mb-4">
            <div className="inline-flex items-center justify-center w-12 h-12 bg-orange-100 rounded-full group-hover:bg-orange-200 transition-colors">
              <Wrench className="w-6 h-6 text-orange-600" />
            </div>
            <ArrowRight className="w-5 h-5 text-gray-400 group-hover:text-orange-500 transition-colors" />
          </div>
          
          <h3 className="text-xl font-semibold text-gray-900 mb-2 group-hover:text-orange-700 transition-colors">
            IDE Agent Assistant
          </h3>
          
          <p className="text-gray-600 mb-4">
            Get AI assistance for debugging, fixing, or modifying your existing project files.
          </p>
          
          <div className="space-y-2">
            <div className="flex items-center text-sm text-gray-500">
              <div className="w-2 h-2 bg-orange-500 rounded-full mr-2"></div>
              Debug and fix code errors
            </div>
            <div className="flex items-center text-sm text-gray-500">
              <div className="w-2 h-2 bg-orange-500 rounded-full mr-2"></div>
              Modify existing features
            </div>
            <div className="flex items-center text-sm text-gray-500">
              <div className="w-2 h-2 bg-orange-500 rounded-full mr-2"></div>
              Add new functionality
            </div>
            <div className="flex items-center text-sm text-gray-500">
              <div className="w-2 h-2 bg-orange-500 rounded-full mr-2"></div>
              Intelligent code analysis
            </div>
          </div>
        </button>
      </div>

      {/* Info Section */}
      <div className="mt-8 p-4 bg-gray-50 rounded-lg">
        <h4 className="font-semibold text-gray-900 mb-2">Need Help Choosing?</h4>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm text-gray-600">
          <div>
            <span className="font-medium">Choose "Create New Project" if:</span>
            <ul className="list-disc list-inside mt-1 space-y-1">
              <li>You're starting a completely new application</li>
              <li>You want AI suggestions for screens and features</li>
              <li>You need domain analysis and industry patterns</li>
            </ul>
          </div>
          <div>
            <span className="font-medium">Choose "Add to Existing Project" if:</span>
            <ul className="list-disc list-inside mt-1 space-y-1">
              <li>You have an existing session ID from a previous generation</li>
              <li>You want to add specific screens to an existing project</li>
              <li>You know exactly what screens you need</li>
            </ul>
          </div>
          <div>
            <span className="font-medium">Choose "IDE Agent Assistant" if:</span>
            <ul className="list-disc list-inside mt-1 space-y-1">
              <li>You need to fix bugs or errors in existing code</li>
              <li>You want to modify or enhance existing features</li>
              <li>You need help with specific development tasks</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default WorkflowSelection; 