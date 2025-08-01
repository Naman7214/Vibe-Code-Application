import logging
import os
from typing import Any, Dict

from system.backend.agentic_workflow.app.utils.file_structure import (
    generate_directory_structure,
)
from system.backend.agentic_workflow.app.utils.xml_parser import (
    parse_xml_to_dict,
)


class StageIVHelper:
    def __init__(self):
        # Set up a simple logger for code generation
        self.logger = logging.getLogger("code_generation_stage_iv")
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

    async def prepare_input_context(
        self, session_id: str, screen_dict: Dict[str, str], is_follow_up: bool
    ) -> Dict[str, Any]:
        """
        Prepare input context by reading screen scratchpads and global scratchpad

        Args:
            session_id: The session ID for file paths
            screen_dict: Dictionary with screen names as keys and descriptions as values
            is_follow_up: Flag indicating if this is a follow-up request

        Returns:
            Dict containing all required context data
        """
        # Define paths
        screen_scratchpads_dir = (
            f"artifacts/{session_id}/scratchpads/screen_scratchpads"
        )
        global_scratchpad_path = (
            f"artifacts/{session_id}/scratchpads/global_scratchpad.txt"
        )
        file_structure_path = (
            f"artifacts/{session_id}/scratchpads/file_structure.txt"
        )
        routes_file_path = f"artifacts/{session_id}/codebase/src/Routes.jsx"
        codebase_path = f"artifacts/{session_id}/codebase"

        context_data = {
            "codebase_path": codebase_path,
            "screen_scratchpads": {},
            "global_scratchpad": "",
            "file_structure": "",
            "existing_routes": "",
        }

        # Read screen scratchpads based on is_follow_up flag
        if is_follow_up:
            # Read only screens specified in the input dict
            screen_names = list(screen_dict.keys())
            self.logger.info(
                f"Follow-up mode: Reading scratchpads for screens: {screen_names}"
            )
        else:
            # Read all available screen scratchpads
            screen_names = await self._get_all_screen_names(
                screen_scratchpads_dir
            )
            self.logger.info(
                f"Initial mode: Reading all available screen scratchpads: {screen_names}"
            )

        # Read screen scratchpad files
        for screen_name in screen_names:
            scratchpad_file = os.path.join(
                screen_scratchpads_dir, f"{screen_name}.txt"
            )
            try:
                with open(scratchpad_file, "r", encoding="utf-8") as f:
                    content = f.read()
                    context_data["screen_scratchpads"][screen_name] = content
                self.logger.info(
                    f"Successfully read scratchpad for {screen_name}"
                )
            except FileNotFoundError:
                self.logger.warning(
                    f"Scratchpad not found for {screen_name} at {scratchpad_file}"
                )
                context_data["screen_scratchpads"][
                    screen_name
                ] = f"No scratchpad available for {screen_name}"
            except Exception as e:
                self.logger.error(
                    f"Error reading scratchpad for {screen_name}: {e}"
                )
                context_data["screen_scratchpads"][
                    screen_name
                ] = f"Error reading scratchpad for {screen_name}"

        # Read global scratchpad
        try:
            with open(global_scratchpad_path, "r", encoding="utf-8") as f:
                context_data["global_scratchpad"] = f.read()
            self.logger.info("Successfully read global_scratchpad.txt")
        except FileNotFoundError:
            self.logger.warning(
                f"global_scratchpad.txt not found at {global_scratchpad_path}"
            )
            context_data["global_scratchpad"] = "No global scratchpad available"
        except Exception as e:
            self.logger.error(f"Error reading global_scratchpad.txt: {e}")
            context_data["global_scratchpad"] = (
                "Error reading global scratchpad"
            )

        # Read file structure
        try:
            with open(file_structure_path, "r", encoding="utf-8") as f:
                context_data["file_structure"] = f.read()
            self.logger.info("Successfully read file_structure.txt")
        except FileNotFoundError:
            self.logger.warning(
                f"file_structure.txt not found at {file_structure_path}"
            )
            context_data["file_structure"] = "No file structure available"
        except Exception as e:
            self.logger.error(f"Error reading file_structure.txt: {e}")
            context_data["file_structure"] = "Error reading file structure"

        # Read existing Routes.jsx if this is a follow-up
        if is_follow_up:
            try:
                with open(routes_file_path, "r", encoding="utf-8") as f:
                    context_data["existing_routes"] = f.read()
                self.logger.info("Successfully read existing Routes.jsx")
            except FileNotFoundError:
                self.logger.warning(
                    f"Routes.jsx not found at {routes_file_path}"
                )
                context_data["existing_routes"] = "No existing Routes.jsx file"
            except Exception as e:
                self.logger.error(f"Error reading Routes.jsx: {e}")
                context_data["existing_routes"] = (
                    "Error reading existing Routes.jsx"
                )

        return context_data

    async def _get_all_screen_names(self, screen_scratchpads_dir: str) -> list:
        """
        Get all available screen names from the screen_scratchpads directory

        Args:
            screen_scratchpads_dir: Path to the screen scratchpads directory

        Returns:
            List of screen names (without .txt extension)
        """
        screen_names = []
        try:
            if os.path.exists(screen_scratchpads_dir):
                for filename in os.listdir(screen_scratchpads_dir):
                    if filename.endswith(".txt"):
                        screen_name = filename[:-4]  # Remove .txt extension
                        screen_names.append(screen_name)
                self.logger.info(
                    f"Found {len(screen_names)} screen scratchpads"
                )
            else:
                self.logger.warning(
                    f"Screen scratchpads directory not found: {screen_scratchpads_dir}"
                )
        except Exception as e:
            self.logger.error(
                f"Error reading screen scratchpads directory: {e}"
            )

        return screen_names

    async def update_file_structure(self, session_id: str, codebase_path: str):
        """
        Update file_structure.txt with current codebase directory structure

        Args:
            session_id: The session ID for file paths
            codebase_path: Path to the codebase directory
        """
        scratchpads_dir = f"artifacts/{session_id}/scratchpads"
        os.makedirs(scratchpads_dir, exist_ok=True)

        # Generate and write updated file structure with full absolute path
        absolute_codebase_path = os.path.abspath(codebase_path)
        file_structure = generate_directory_structure(absolute_codebase_path)
        file_structure_path = os.path.join(
            scratchpads_dir, "file_structure.txt"
        )

        with open(file_structure_path, "w", encoding="utf-8") as f:
            f.write(file_structure)

        self.logger.info(
            f"Updated file_structure.txt with current codebase state at {file_structure_path}"
        )

    async def update_scratchpads(
        self, session_id: str, llm_output: str, codebase_path: str
    ):
        """
        Update scratchpad files with directory structure and parsed LLM output

        Args:
            session_id: The session ID for file paths
            llm_output: The raw LLM output containing XML
            codebase_path: Path to the codebase directory
        """
        scratchpads_dir = f"artifacts/{session_id}/scratchpads"
        os.makedirs(scratchpads_dir, exist_ok=True)

        # Parse XML response to get structured output
        try:
            file_data = parse_xml_to_dict(llm_output)

            # Separate CONTEXT_REGISTRY from regular files
            context_registry_content = ""
            actual_files = []

            for file_info in file_data:
                if file_info["file_path"] == "CONTEXT_REGISTRY":
                    context_registry_content = file_info["code_snippet"]
                else:
                    actual_files.append(file_info)

            # Format parsed output for scratchpad (only CONTEXT_REGISTRY, no actual code files)
            formatted_output = f"""
<STAGE_IV_CODE_GENERATION>
<TIMESTAMP>{self._get_timestamp()}</TIMESTAMP>
<ROUTES_CONTEXT_REGISTRY>
{context_registry_content}
</ROUTES_CONTEXT_REGISTRY>
</STAGE_IV_CODE_GENERATION>

"""

        except Exception as e:
            # Fallback to raw output if parsing fails
            self.logger.warning(f"Failed to parse XML output: {e}")
            formatted_output = f"""
<STAGE_IV_CODE_GENERATION>
<TIMESTAMP>{self._get_timestamp()}</TIMESTAMP>
<RAW_LLM_OUTPUT>
{llm_output}
</RAW_LLM_OUTPUT>
</STAGE_IV_CODE_GENERATION>

"""

        # Append to global scratchpad
        global_scratchpad_path = os.path.join(
            scratchpads_dir, "global_scratchpad.txt"
        )

        with open(global_scratchpad_path, "a", encoding="utf-8") as f:
            f.write(formatted_output)

        self.logger.info(
            f"Updated global_scratchpad.txt at {global_scratchpad_path}"
        )

    async def update_scratchpads_with_routes_generation(
        self,
        session_id: str,
        routes_content: str,
        context_registry_content: str,
        codebase_path: str,
    ):
        """
        Update scratchpad files with routes generation content and analysis.

        Args:
            session_id: The session ID for file paths
            routes_content: Generated Routes.jsx content
            context_registry_content: Context registry content with analysis
            codebase_path: Path to the codebase directory
        """
        scratchpads_dir = f"artifacts/{session_id}/scratchpads"
        os.makedirs(scratchpads_dir, exist_ok=True)

        # Format output for scratchpad with routes generation details
        formatted_output = f"""
<STAGE_IV_ROUTES_GENERATION>
<TIMESTAMP>{self._get_timestamp()}</TIMESTAMP>
<ROUTES_CONTEXT_REGISTRY>
{context_registry_content}
</ROUTES_CONTEXT_REGISTRY>
<GENERATED_ROUTES_FILE>
File: src/Routes.jsx
Content Length: {len(routes_content)} characters
Generated using heuristic analysis of pages directory structure
</GENERATED_ROUTES_FILE>
</STAGE_IV_ROUTES_GENERATION>

"""

        # Append to global scratchpad
        global_scratchpad_path = os.path.join(
            scratchpads_dir, "global_scratchpad.txt"
        )

        with open(global_scratchpad_path, "a", encoding="utf-8") as f:
            f.write(formatted_output)

        self.logger.info(
            f"Updated global_scratchpad.txt with routes generation summary at {global_scratchpad_path}"
        )

        # Also create a dedicated routes analysis file
        routes_analysis_path = os.path.join(
            scratchpads_dir, "routes_analysis.txt"
        )

        with open(routes_analysis_path, "w", encoding="utf-8") as f:
            f.write(f"ROUTES GENERATION ANALYSIS\n")
            f.write(f"Generated at: {self._get_timestamp()}\n")
            f.write(f"{'='*50}\n\n")
            f.write(context_registry_content)

        self.logger.info(
            f"Created routes analysis file at {routes_analysis_path}"
        )

    def generate_context_registry(self, analysis: Dict) -> str:
        """
        Generate context registry content based on routes analysis.

        Args:
            analysis: Analysis results from the routes generator

        Returns:
            Formatted context registry content
        """
        pages = analysis.get("pages", [])
        components = analysis.get("components", {})

        # Build route list
        route_list = []
        for page in pages:
            routes_str = ", ".join(page.get("routes", []))
            route_list.append(
                f"• {page['component_name']} → {routes_str} {'(HOME)' if page.get('is_home') else ''}"
            )

        # Build components summary
        components_summary = []
        if components.get("scroll_to_top"):
            components_summary.append("• ScrollToTop component")
        if components.get("error_boundary"):
            components_summary.append("• ErrorBoundary component")
        if components.get("has_ui_components"):
            components_summary.append("• UI components directory")

        return f"""REACT STAGE IV - ROUTES GENERATION SUMMARY
=========================================

ROUTES CREATED:
{chr(10).join(route_list)}

ARCHITECTURE:
• Router: React Router v6 with BrowserRouter
• Route Structure: <Routes> with <Route> elements
• Import Pattern: ./pages/[page_name]
• Navigation: Navigate programmatically with useNavigate()

SUMMARY:
• Total Routes: {len(pages)}
• Page Components: {len(pages)}
• Component Imports: {len(pages)} page imports
• Home Page: {next((p['component_name'] for p in pages if p.get('is_home')), 'Not determined')}

FEATURES:
{chr(10).join(components_summary) if components_summary else '• No additional components detected'}

ANALYSIS DETAILS:
• Pages Found: {analysis.get('pages_found', 0)}
• Has Routing Structure: {analysis.get('has_routing_structure', False)}
• Generation Method: Heuristic analysis of src/pages directory
• Component Names: Extracted from directory names (converted to PascalCase)
• Route Paths: Generated from directory names (converted to kebab-case)
• Home Page Detection: Based on common naming patterns (main_menu, home, etc.)
"""

    def _get_timestamp(self) -> str:
        """Get current timestamp as string"""
        from datetime import datetime

        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
