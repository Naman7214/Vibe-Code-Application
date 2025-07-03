import asyncio
import base64
import json
import os
import shutil
from pathlib import Path

from system.backend.agentic_workflow.app.utils.session_context import (
    session_state,
)


class AIReactBoilerplateSetup:
    """Service to create React boilerplate matching AI-generated code structure"""

    def __init__(self):
        # Don't get session_id here - it's not available at import time
        self.session_id = None
        self.base_path = None

    async def create_react_boilerplate(self) -> str:
        """Create React project boilerplate for AI code generation"""
        
        # Get session_id from context when method is actually called
        self.session_id = session_state.get()
        if not self.session_id:
            raise ValueError("Session ID not found in context")
            
        self.base_path = Path(f"artifacts/{self.session_id}/codebase")

        # Remove existing project if exists
        if self.base_path.exists():
            shutil.rmtree(self.base_path)

        # Ensure base directory exists
        self.base_path.mkdir(parents=True, exist_ok=True)

        try:
            # Step 1: Create Vite React project
            await self._create_vite_project()

            # Step 2: Setup project structure
            await self._create_folder_structure()

            # Step 3: Update package.json with exact dependencies
            await self._update_package_json()

            # Step 4: Create configuration files
            await self._create_config_files()

            # Step 5: Create boilerplate source files
            await self._create_boilerplate_files()

            # Step 6: Create utility components
            await self._create_utility_components()

            # Step 7: Setup assets
            await self._setup_assets()

            # Step 8: Remove default Vite files
            await self._cleanup_default_files()

            # Step 9: Install dependencies
            await self._install_dependencies()

            print(
                f"✅ AI React boilerplate created successfully at: {self.base_path}"
            )
            return str(self.base_path)

        except Exception as e:
            print(f"❌ Error creating boilerplate: {e}")
            raise e

    async def _create_vite_project(self):
        """Create Vite React project"""
        print("📦 Creating Vite React project...")

        cmd = ["npm", "create", "vite@latest", ".", "--", "--template", "react"]

        # Set environment variables for non-interactive mode
        env = {
            **os.environ,
            "CI": "true",  # Tells npm to run in non-interactive mode
            "NPM_CONFIG_YES": "true",  # Auto-confirm npm prompts
        }

        process = await asyncio.create_subprocess_exec(
            *cmd,
            cwd=self.base_path,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            stdin=asyncio.subprocess.PIPE,  # Add stdin pipe for input handling
            env=env,  # Use the environment variables
        )

        # Send 'y' to confirm any prompts and close stdin
        stdout, stderr = await process.communicate(input=b'y\n')

        if process.returncode != 0:
            raise Exception(f"Failed to create Vite project: {stderr.decode()}")

        print("✅ Vite React project created")

    async def _create_folder_structure(self):
        """Create AI-compatible folder structure"""
        print("📁 Creating project folder structure...")

        folders = [
            "src/components",
            "src/components/ui",  # For AI-generated UI components
            "src/pages",  # For AI-generated pages
            "src/styles",
            "public/assets",
            "public/assets/images",
        ]

        for folder in folders:
            folder_path = self.base_path / folder
            folder_path.mkdir(parents=True, exist_ok=True)

        print("✅ Folder structure created")

    async def _update_package_json(self):
        """Update package.json with exact dependencies from AI-generated code"""
        print("📄 Updating package.json...")

        package_json_path = self.base_path / "package.json"

        with open(package_json_path, "r") as f:
            package_data = json.load(f)

        # Update to match AI-generated code exactly
        package_data["name"] = "ai-generated-react-app"
        package_data["dependencies"] = {
            "@dhiwise/component-tagger": "^1.0.1",
            "@reduxjs/toolkit": "^2.6.1",
            "@tailwindcss/forms": "^0.5.7",
            "@testing-library/jest-dom": "^5.15.1",
            "@testing-library/react": "^11.2.7",
            "@testing-library/user-event": "^12.8.3",
            "axios": "^1.8.4",
            "d3": "^7.9.0",
            "date-fns": "^4.1.0",
            "dotenv": "^16.0.1",
            "framer-motion": "^10.16.4",
            "lucide-react": "^0.484.0",
            "react": "^18.2.0",
            "react-dom": "^18.2.0",
            "react-helmet": "^6.1.0",
            "react-hook-form": "^7.55.0",
            "react-router-dom": "6.0.2",
            "react-router-hash-link": "^2.4.3",
            "recharts": "^2.15.2",
            "redux": "^5.0.1",
            "tailwindcss-animate": "^1.0.7",
            "tailwindcss-elevation": "^2.0.0",
            "tailwindcss-fluid-type": "^2.0.7",
        }

        package_data["devDependencies"] = {
            "@tailwindcss/aspect-ratio": "^0.4.2",
            "@tailwindcss/container-queries": "^0.1.1",
            "@tailwindcss/line-clamp": "^0.1.0",
            "@tailwindcss/typography": "^0.5.16",
            "@vitejs/plugin-react": "4.3.4",
            "autoprefixer": "10.4.2",
            "postcss": "8.4.8",
            "tailwindcss": "3.4.6",
            "vite": "5.0.0",
            "vite-tsconfig-paths": "3.6.0",
        }

        package_data["scripts"] = {
            "start": "vite",
            "build": "vite build --sourcemap",
            "serve": "vite preview",
        }

        with open(package_json_path, "w") as f:
            json.dump(package_data, f, indent=2)

        print("✅ package.json updated")

    async def _create_config_files(self):
        """Create configuration files"""
        print("⚙️ Creating configuration files...")

        # vite.config.mjs
        vite_config = """import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    host: true
  },
  build: {
    outDir: 'dist',
    sourcemap: true
  }
})
"""

        # postcss.config.js
        postcss_config = """export default {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
"""

        # jsconfig.json for better import resolution
        jsconfig = """{
  "compilerOptions": {
    "baseUrl": "src",
    "paths": {
      "@/*": ["*"],
      "@/components/*": ["components/*"],
      "@/pages/*": ["pages/*"],
      "@/styles/*": ["styles/*"]
    }
  },
  "include": ["src"]
}
"""

        # Write configuration files
        with open(self.base_path / "vite.config.mjs", "w") as f:
            f.write(vite_config)

        with open(self.base_path / "postcss.config.js", "w") as f:
            f.write(postcss_config)

        with open(self.base_path / "jsconfig.json", "w") as f:
            f.write(jsconfig)

        print("✅ Configuration files created")

    async def _create_boilerplate_files(self):
        """Create boilerplate source files"""
        print("📝 Creating boilerplate source files...")

        # src/index.jsx - React entry point
        index_jsx = """import React from "react";
import { createRoot } from "react-dom/client";
import App from "./App";
import "./styles/tailwind.css";
import "./styles/index.css";

const container = document.getElementById("root");
const root = createRoot(container);

root.render(<App />);
"""

        # src/App.jsx - Simple app that renders Routes
        app_jsx = """import React from "react";
import Routes from "./Routes";

function App() {
  return (
    <Routes />
  );
}

export default App;
"""

        # src/styles/index.css - CSS resets
        index_css = """/* src/styles/index.css - Minimal, Non-Conflicting */

/* Only browser-specific fixes that Tailwind doesn't handle */
*, *::before, *::after {
  -webkit-tap-highlight-color: transparent;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

/* Critical accessibility that LLM might miss */
*:focus {
  outline: 2px solid #3b82f6;
  outline-offset: 2px;
}

*:focus:not(:focus-visible) {
  outline: none;
}

/* Screen reader utility */
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}

/* Performance optimizations */
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}

/* Print styles */
@media print {
  body {
    background: white !important;
    color: black !important;
  }
  
  .no-print {
    display: none !important;
  }
}
"""

        # index.html - Update to match AI-generated structure
        index_html = """<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/favicon.ico" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>AI Generated React App</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/index.jsx"></script>
  </body>
</html>
"""

        # Write boilerplate files
        with open(self.base_path / "src/index.jsx", "w") as f:
            f.write(index_jsx)

        with open(self.base_path / "src/App.jsx", "w") as f:
            f.write(app_jsx)

        with open(self.base_path / "src/styles/index.css", "w") as f:
            f.write(index_css)

        with open(self.base_path / "index.html", "w") as f:
            f.write(index_html)

        print("✅ Boilerplate source files created")

    async def _create_utility_components(self):
        """Create utility components that are standard across AI-generated apps"""
        print("🔧 Creating utility components...")

        # AppImage.jsx - Image wrapper with error handling
        app_image = """import React from 'react';

function Image({
  src,
  alt = "Image Name",
  className = "",
  ...props
}) {

  return (
    <img
      src={src}
      alt={alt}
      className={className}
      onError={(e) => {
        e.target.src = "/assets/images/no_image.png"
      }}
      {...props}
    />
  );
}

export default Image;
"""

        # AppIcon.jsx - Icon system using Lucide React
        app_icon = """import React from 'react';
import * as LucideIcons from 'lucide-react';
import { HelpCircle } from 'lucide-react';

function Icon({
    name,
    size = 24,
    color = "currentColor",
    className = "",
    strokeWidth = 2,
    ...props
}) {
    const IconComponent = LucideIcons[name];

    if (!IconComponent) {
        return <HelpCircle size={size} color="gray" strokeWidth={strokeWidth} className={className} {...props} />;
    }

    return <IconComponent
        size={size}
        color={color}
        strokeWidth={strokeWidth}
        className={className}
        {...props}
    />;
}
export default Icon;
"""

        # ErrorBoundary.jsx - Error boundary component
        error_boundary = """import React from "react";
import Icon from "./AppIcon";

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    console.error("Error caught by ErrorBoundary:", error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen flex items-center justify-center bg-neutral-50">
          <div className="text-center p-8 max-w-md">
            <div className="flex justify-center items-center mb-2">
              <svg xmlns="http://www.w3.org/2000/svg" width="42px" height="42px" viewBox="0 0 32 33" fill="none">
                <path d="M16 28.5C22.6274 28.5 28 23.1274 28 16.5C28 9.87258 22.6274 4.5 16 4.5C9.37258 4.5 4 9.87258 4 16.5C4 23.1274 9.37258 28.5 16 28.5Z" stroke="#343330" strokeWidth="2" strokeMiterlimit="10" />
                <path d="M11.5 15.5C12.3284 15.5 13 14.8284 13 14C13 13.1716 12.3284 12.5 11.5 12.5C10.6716 12.5 10 13.1716 10 14C10 14.8284 10.6716 15.5 11.5 15.5Z" fill="#343330" />
                <path d="M20.5 15.5C21.3284 15.5 22 14.8284 22 14C22 13.1716 21.3284 12.5 20.5 12.5C19.6716 12.5 19 13.1716 19 14C19 14.8284 19.6716 15.5 20.5 15.5Z" fill="#343330" />
                <path d="M21 22.5C19.9625 20.7062 18.2213 19.5 16 19.5C13.7787 19.5 12.0375 20.7062 11 22.5" stroke="#343330" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
            </div>
            <div className="flex flex-col gap-1 text-center">
              <h1 className="text-2xl font-medium text-neutral-800">Something went wrong</h1>
              <p className="text-neutral-600 text-base w-8/12 mx-auto">We encountered an unexpected error while processing your request.</p>
            </div>
            <div className="flex justify-center items-center mt-6">
              <button
                onClick={() => {
                  window.location.href = "/";
                }}
                className="bg-blue-500 hover:bg-blue-600 text-white font-medium py-2 px-4 rounded flex items-center gap-2 transition-colors duration-200 shadow-sm"
              >
                <Icon name="ArrowLeft" size={18} color="#fff" />
                Back
              </button>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
"""

        # ScrollToTop.jsx - Scroll to top utility
        scroll_to_top = """import { useEffect } from "react";
import { useLocation } from "react-router-dom";

const ScrollToTop = () => {
  const { pathname } = useLocation();

  useEffect(() => {
    window.scrollTo(0, 0);
  }, [pathname]);

  return null;
};

export default ScrollToTop;
"""

        # Write utility components
        with open(self.base_path / "src/components/AppImage.jsx", "w") as f:
            f.write(app_image)

        with open(self.base_path / "src/components/AppIcon.jsx", "w") as f:
            f.write(app_icon)

        with open(
            self.base_path / "src/components/ErrorBoundary.jsx", "w"
        ) as f:
            f.write(error_boundary)

        with open(self.base_path / "src/components/ScrollToTop.jsx", "w") as f:
            f.write(scroll_to_top)

        print("✅ Utility components created")

    async def _setup_assets(self):
        """Setup assets directory and placeholder files"""
        print("🖼️ Setting up assets...")

        # Path to the static no_image.png file in backend
        static_no_image_path = Path("system/backend/static/assets/images/no_image.png")
        
        # Copy the actual no_image.png file from backend static assets
        if static_no_image_path.exists():
            shutil.copy2(
                static_no_image_path,
                self.base_path / "public/assets/images/no_image.png"
            )
            print(f"  ✅ Copied no_image.png from backend static assets")
        else:
            # Fallback to base64 if the static file doesn't exist
            print("  ⚠️ Static no_image.png not found, creating base64 placeholder")
            placeholder_png = base64.b64decode(
                "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChAGA6xjzTgAAAABJRU5ErkJggg=="
            )
            with open(
                self.base_path / "public/assets/images/no_image.png", "wb"
            ) as f:
                f.write(placeholder_png)

        # Create favicon.ico (simple 16x16 blue square)
        favicon_data = base64.b64decode(
            "AAABAAEAEBAAAAEACABoBQAAFgAAACgAAAAQAAAAIAAAAAEACAAAAAAAAAEAAAAAAAAAAAAAAAEAAAEAAAAAAAAA"
        )

        # Write favicon file

        with open(self.base_path / "public/favicon.ico", "wb") as f:
            f.write(favicon_data)

        # Create manifest.json for PWA support
        manifest = """{
  "short_name": "AI React App",
  "name": "AI Generated React Application",
  "icons": [
    {
      "src": "favicon.ico",
      "sizes": "64x64 32x32 24x24 16x16",
      "type": "image/x-icon"
    }
  ],
  "start_url": ".",
  "display": "standalone",
  "theme_color": "#000000",
  "background_color": "#ffffff"
}
"""

        # robots.txt
        robots = """User-agent: *
Disallow:
"""

        with open(self.base_path / "public/manifest.json", "w") as f:
            f.write(manifest)

        with open(self.base_path / "public/robots.txt", "w") as f:
            f.write(robots)

        print("✅ Assets setup completed")

    async def _cleanup_default_files(self):
        """Remove default Vite files that we don't need"""
        print("🧹 Cleaning up default files...")

        # Files to remove
        files_to_remove = [
            "src/main.jsx",  # We use index.jsx instead
            "src/App.css",  # We don't use App.css
            "src/index.css",  # We don't use index.css
            "tailwind.config.js",  # AI agents will create this
        ]

        for file_path in files_to_remove:
            full_path = self.base_path / file_path
            if full_path.exists():
                full_path.unlink()
                print(f"  ✅ Removed {file_path}")

        print("✅ Default files cleaned up")

    async def _install_dependencies(self):
        """Install all dependencies"""
        print("📦 Installing dependencies...")

        cmd = ["npm", "install"]

        process = await asyncio.create_subprocess_exec(
            *cmd,
            cwd=self.base_path,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        stdout, stderr = await process.communicate()

        if process.returncode != 0:
            raise Exception(
                f"Failed to install dependencies: {stderr.decode()}"
            )

        print("✅ Dependencies installed successfully")


setup_boilerplate = AIReactBoilerplateSetup()