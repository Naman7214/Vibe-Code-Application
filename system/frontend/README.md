# Velocity.new Frontend

A React-based frontend for the Velocity.new code generation platform.

## Features

- **Step-by-step workflow**: Guided process for code generation
- **Platform selection**: Support for Web (React) and Mobile (Flutter) applications
- **Screen selection**: Choose which screens to generate from AI suggestions
- **Real-time feedback**: Loading states and error handling
- **Automatic error fixing**: Integration with IDE agent for build error resolution
- **Modern UI**: Built with Tailwind CSS for a clean, responsive interface

## Prerequisites

- Node.js (v16 or higher)
- npm or yarn
- Running Velocity.new backend (on http://127.0.0.1:8000)

## Installation

1. Navigate to the frontend directory:
   ```bash
   cd system/frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

## Development

Start the development server:
```bash
npm start
```

The application will open in your browser at `http://localhost:3000`.

## Workflow Steps

1. **Initial Processing**: Enter your app description and select platform type
2. **Screen Selection**: Choose which screens to generate from AI suggestions
3. **Code Generation**: Automatic context gathering and code generation
4. **Error Fixing** (if needed): Automatic error resolution via IDE agent
5. **Completion**: Get the path to your generated codebase

## API Integration

The frontend integrates with these backend endpoints:

- `POST /api/v1/initial-processing` - Process user query and get screen suggestions
- `POST /api/v1/context-gathering` - Gather context for selected screens
- `POST /api/v1/generate-code` - Generate the actual code
- `POST /api/v1/ide-agent` - Fix build errors automatically

## Build

Create a production build:
```bash
npm run build
```

## Technologies Used

- React 18
- Tailwind CSS
- Axios for API calls
- Lucide React for icons
- Custom hooks for state management

## Project Structure

```
src/
├── components/           # React components for each workflow step
├── hooks/               # Custom React hooks
├── services/           # API service layer
└── utils/              # Utility functions
``` 