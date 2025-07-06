import logging
import os
from typing import Any, Dict

from system.backend.agentic_workflow.app.utils.file_structure import (
    generate_directory_structure,
)
from system.backend.agentic_workflow.app.utils.xml_parser import (
    parse_xml_to_dict,
)


class FlutterStageIIIHelper:
    def __init__(self):
        # Set up a simple logger for Flutter code generation
        self.logger = logging.getLogger("flutter_code_generation_stage_iii")
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
        Prepare input context by reading screen scratchpads and existing routes
        Only includes: screen_scratchpads, is_follow_up, existing_routes, codebase_path

        Args:
            session_id: The session ID for file paths
            screen_dict: Dictionary with screen names as keys and descriptions as values
            is_follow_up: Flag indicating if this is a follow-up request

        Returns:
            Dict containing all required context data
        """
        # Define paths for Flutter project
        screen_scratchpads_dir = (
            f"artifacts/{session_id}/scratchpads/screen_scratchpads"
        )
        routes_file_path = (
            f"artifacts/{session_id}/codebase/lib/routes/app_routes.dart"
        )
        codebase_path = f"artifacts/{session_id}/codebase"

        context_data = {
            "codebase_path": codebase_path,
            "screen_scratchpads": {},
            "existing_routes": "",
        }

        # Read screen scratchpads
        screen_scratchpads = {}
        if os.path.exists(screen_scratchpads_dir):
            for screen_name in screen_dict.keys():
                scratchpad_path = os.path.join(
                    screen_scratchpads_dir, f"{screen_name}.json"
                )
                if os.path.exists(scratchpad_path):
                    try:
                        with open(scratchpad_path, "r", encoding="utf-8") as f:
                            screen_scratchpads[screen_name] = f.read()
                        self.logger.info(
                            f"Successfully read scratchpad for {screen_name}"
                        )
                    except Exception as e:
                        self.logger.error(
                            f"Error reading scratchpad for {screen_name}: {e}"
                        )
                        screen_scratchpads[screen_name] = (
                            f"Error reading scratchpad: {e}"
                        )
                else:
                    self.logger.warning(
                        f"Scratchpad not found for {screen_name}"
                    )
                    screen_scratchpads[screen_name] = (
                        f"Scratchpad not found for {screen_name}"
                    )

        # Format screen scratchpads as JSON string
        import json

        context_data["screen_scratchpads"] = json.dumps(
            screen_scratchpads, indent=2
        )

        # Read existing app_routes.dart if this is a follow-up
        if is_follow_up:
            try:
                with open(routes_file_path, "r", encoding="utf-8") as f:
                    context_data["existing_routes"] = f.read()
                self.logger.info("Successfully read existing app_routes.dart")
            except FileNotFoundError:
                self.logger.warning(
                    f"app_routes.dart not found at {routes_file_path}"
                )
                context_data["existing_routes"] = (
                    "No existing app_routes.dart file"
                )
            except Exception as e:
                self.logger.error(f"Error reading app_routes.dart: {e}")
                context_data["existing_routes"] = (
                    "Error reading existing app_routes.dart"
                )

        return context_data

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
<FLUTTER_STAGE_III_CODE_GENERATION>
<TIMESTAMP>{self._get_timestamp()}</TIMESTAMP>
<ROUTES_CONTEXT_REGISTRY>
{context_registry_content}
</ROUTES_CONTEXT_REGISTRY>
</FLUTTER_STAGE_III_CODE_GENERATION>

"""

        except Exception as e:
            # Fallback to raw output if parsing fails
            self.logger.warning(f"Failed to parse XML output: {e}")
            formatted_output = f"""
<FLUTTER_STAGE_III_CODE_GENERATION>
<TIMESTAMP>{self._get_timestamp()}</TIMESTAMP>
<RAW_LLM_OUTPUT>
{llm_output}
</RAW_LLM_OUTPUT>
</FLUTTER_STAGE_III_CODE_GENERATION>

"""

        # Append to Flutter-specific scratchpad
        flutter_scratchpad_path = os.path.join(
            scratchpads_dir, "global_scratchpad.txt"
        )

        with open(flutter_scratchpad_path, "a", encoding="utf-8") as f:
            f.write(formatted_output)

        self.logger.info(
            f"Updated global_scratchpad.txt at {flutter_scratchpad_path}"
        )

    async def update_scratchpads_with_generated_content(
        self, session_id: str, routes_content: str, context_registry_content: str, codebase_path: str
    ):
        """
        Update scratchpad files with the generated routes content and context registry

        Args:
            session_id: The session ID for file paths
            routes_content: The generated routes file content
            context_registry_content: The context registry content
            codebase_path: Path to the codebase directory
        """
        scratchpads_dir = f"artifacts/{session_id}/scratchpads"
        os.makedirs(scratchpads_dir, exist_ok=True)

        # Format output for scratchpad
        formatted_output = f"""
<FLUTTER_STAGE_III_CODE_GENERATION>
<TIMESTAMP>{self._get_timestamp()}</TIMESTAMP>
<ROUTES_CONTEXT_REGISTRY>
{context_registry_content}
</ROUTES_CONTEXT_REGISTRY>
<GENERATED_ROUTES_FILE>
{routes_content}
</GENERATED_ROUTES_FILE>
</FLUTTER_STAGE_III_CODE_GENERATION>

"""

        # Append to Flutter-specific scratchpad
        flutter_scratchpad_path = os.path.join(
            scratchpads_dir, "global_scratchpad.txt"
        )

        with open(flutter_scratchpad_path, "a", encoding="utf-8") as f:
            f.write(formatted_output)

        self.logger.info(
            f"Updated global_scratchpad.txt with generated routes content at {flutter_scratchpad_path}"
        )

    def generate_context_registry(self, analysis: Dict) -> str:
        """
        Generate context registry content based on routes analysis.
        
        Args:
            analysis: Analysis results from the routes generator
            
        Returns:
            Formatted context registry content
        """
        screens = analysis.get("screens", [])
        initial_screen = analysis.get("initial_screen", {})
        
        # Build route list
        route_list = []
        for screen in screens:
            route_list.append(
                f"• {screen['route_constant']} → {screen['class_name']} (path: /{screen['route_path']})"
            )
        
        return f"""FLUTTER STAGE III - ROUTES GENERATION SUMMARY
=============================================

📍 ROUTES CREATED:
{chr(10).join(route_list)}

🏗️ ARCHITECTURE:
• Router: Traditional Flutter Navigator with named routes
• Route Structure: Map<String, WidgetBuilder> routes
• Import Pattern: ../presentation/[screen_name]/[screen_name].dart
• Navigation: Navigator.pushNamed() approach

📊 SUMMARY:
• Total Routes: {len(screens)}
• Screen Widgets: {len(screens)}
• Route Constants: {len(screens)} static constants defined
• Import Pattern: Consistent presentation layer imports
• Initial Screen: {initial_screen.get('name', 'Not determined') if initial_screen else 'Not determined'}

🚀 FEATURES:
• Static route constants with kebab-case naming
• Centralized route management with AppRoutes class
• Traditional Flutter navigation patterns
• Consistent screen import structure
• TODO comments for extensibility
• Heuristic analysis of presentation structure

🔍 ANALYSIS DETAILS:
• Screens Found: {analysis.get('screens_found', 0)}
• Has Routing Structure: {analysis.get('has_routing_structure', False)}
• Generation Method: Heuristic analysis of lib/presentation directory
• Class Names: Extracted from actual screen files
• Route Paths: Generated from directory names (snake_case → kebab-case)
• Route Constants: Generated from directory names (snake_case → camelCase)
"""

    def _get_timestamp(self) -> str:
        """Get current timestamp as string"""
        from datetime import datetime

        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
