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
            f"artifacts/{session_id}/scratchpads/flutter_screen_scratchpads"
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

        # Read screen scratchpads based on is_follow_up flag
        if is_follow_up:
            # Read only screens specified in the input dict
            screen_names = list(screen_dict.keys())
            self.logger.info(
                f"Follow-up mode: Reading Flutter scratchpads for screens: {screen_names}"
            )
        else:
            # Read all available screen scratchpads
            screen_names = await self._get_all_screen_names(
                screen_scratchpads_dir
            )
            self.logger.info(
                f"Initial mode: Reading all available Flutter screen scratchpads: {screen_names}"
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
                    f"Successfully read Flutter scratchpad for {screen_name}"
                )
            except FileNotFoundError:
                self.logger.warning(
                    f"Flutter scratchpad not found for {screen_name} at {scratchpad_file}"
                )
                context_data["screen_scratchpads"][
                    screen_name
                ] = f"No scratchpad available for {screen_name}"
            except Exception as e:
                self.logger.error(
                    f"Error reading Flutter scratchpad for {screen_name}: {e}"
                )
                context_data["screen_scratchpads"][
                    screen_name
                ] = f"Error reading scratchpad for {screen_name}"

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

    async def _get_all_screen_names(self, screen_scratchpads_dir: str) -> list:
        """
        Get all available screen names from the flutter_screen_scratchpads directory

        Args:
            screen_scratchpads_dir: Path to the Flutter screen scratchpads directory

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
                    f"Found {len(screen_names)} Flutter screen scratchpads"
                )
            else:
                self.logger.warning(
                    f"Flutter screen scratchpads directory not found: {screen_scratchpads_dir}"
                )
        except Exception as e:
            self.logger.error(
                f"Error reading Flutter screen scratchpads directory: {e}"
            )

        return screen_names

    async def update_file_structure(self, session_id: str, codebase_path: str):
        """
        Update flutter_file_structure.txt with current codebase directory structure

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
            scratchpads_dir, "flutter_file_structure.txt"
        )

        with open(file_structure_path, "w", encoding="utf-8") as f:
            f.write(file_structure)

        self.logger.info(
            f"Updated flutter_file_structure.txt with current codebase state at {file_structure_path}"
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
            scratchpads_dir, "flutter_global_scratchpad.txt"
        )

        with open(flutter_scratchpad_path, "a", encoding="utf-8") as f:
            f.write(formatted_output)

        self.logger.info(
            f"Updated flutter_global_scratchpad.txt at {flutter_scratchpad_path}"
        )

    def _get_timestamp(self) -> str:
        """Get current timestamp as string"""
        from datetime import datetime

        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
