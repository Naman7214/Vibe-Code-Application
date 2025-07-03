import json
import logging
import os
from typing import Any, Dict

from system.backend.agentic_workflow.app.utils.file_structure import (
    generate_directory_structure,
)
from system.backend.agentic_workflow.app.utils.xml_parser import (
    parse_xml_to_dict,
)


class FlutterStageIHelper:
    def __init__(self):
        # Set up a simple logger for Flutter code generation
        self.logger = logging.getLogger("flutter_code_generation_stage_i")
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

    async def prepare_input_context(self, session_id: str) -> Dict[str, Any]:
        """
        Prepare input context by reading required files for Flutter project

        Args:
            session_id: The session ID for file paths

        Returns:
            Dict containing all required context data
        """
        # Define file paths for Flutter project
        stage_iii_a_path = (
            f"artifacts/{session_id}/project_context/stage_iii_a.json"
        )
        stage_iv_path = f"artifacts/{session_id}/project_context/stage_iv.json"
        pubspec_yaml_path = f"artifacts/{session_id}/codebase/pubspec.yaml"
        codebase_path = f"artifacts/{session_id}/codebase"

        context_data = {"codebase_path": codebase_path}

        # Read stage_iii_a.json (entire file)
        try:
            with open(stage_iii_a_path, "r", encoding="utf-8") as f:
                context_data["stage_iii_a"] = json.load(f)
            self.logger.info(f"Successfully read stage_iii_a.json")
        except FileNotFoundError:
            self.logger.error(
                f"stage_iii_a.json not found at {stage_iii_a_path}"
            )
            context_data["stage_iii_a"] = {}
        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON in stage_iii_a.json: {e}")
            context_data["stage_iii_a"] = {}

        # Read stage_iv.json and extract specific keys for Flutter theming
        try:
            with open(stage_iv_path, "r", encoding="utf-8") as f:
                stage_iv_data = json.load(f)

            # Extract specific keys for each screen (exclude content key)
            filtered_stage_iv = {}
            for screen_name, screen_data in stage_iv_data.items():
                if isinstance(screen_data, dict):
                    # Check if it's the nested structure (screen_name -> screen_name -> data)
                    if screen_name in screen_data and isinstance(
                        screen_data[screen_name], dict
                    ):
                        nested_screen_data = screen_data[screen_name]
                        filtered_screen_data = {}
                        for key in [
                            "description",
                            "components",
                            "interactions",
                            "responsive",
                            "design",
                            "theme_colors",
                            "typography",
                        ]:
                            if key in nested_screen_data:
                                filtered_screen_data[key] = nested_screen_data[
                                    key
                                ]
                        if filtered_screen_data:
                            filtered_stage_iv[screen_name] = (
                                filtered_screen_data
                            )
                    else:
                        # Handle direct structure (screen_name -> data)
                        filtered_screen_data = {}
                        for key in [
                            "description",
                            "components",
                            "interactions",
                            "responsive",
                            "design",
                            "theme_colors",
                            "typography",
                        ]:
                            if key in screen_data:
                                filtered_screen_data[key] = screen_data[key]
                        if filtered_screen_data:
                            filtered_stage_iv[screen_name] = (
                                filtered_screen_data
                            )

            context_data["stage_iv_a"] = filtered_stage_iv
            self.logger.info(
                f"Successfully read and filtered stage_iv.json for Flutter"
            )
        except FileNotFoundError:
            self.logger.error(f"stage_iv.json not found at {stage_iv_path}")
            context_data["stage_iv_a"] = {}
        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON in stage_iv.json: {e}")
            context_data["stage_iv_a"] = {}

        # Read pubspec.yaml
        try:
            with open(pubspec_yaml_path, "r", encoding="utf-8") as f:
                context_data["pubspec_yaml"] = f.read()
            self.logger.info(f"Successfully read pubspec.yaml")
        except FileNotFoundError:
            self.logger.error(f"pubspec.yaml not found at {pubspec_yaml_path}")
            context_data["pubspec_yaml"] = ""

        return context_data

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

        # Generate and write file structure with full absolute path
        absolute_codebase_path = os.path.abspath(codebase_path)
        file_structure = generate_directory_structure(absolute_codebase_path)
        file_structure_path = os.path.join(
            scratchpads_dir, "flutter_file_structure.txt"
        )

        with open(file_structure_path, "w", encoding="utf-8") as f:
            f.write(file_structure)

        self.logger.info(
            f"Updated flutter_file_structure.txt at {file_structure_path}"
        )

        # Parse XML response to get structured output
        try:
            file_data = parse_xml_to_dict(llm_output)

            # Format parsed output for scratchpad
            formatted_output = f"""
<FLUTTER_STAGE_I_CODE_GENERATION>
<TIMESTAMP>{self._get_timestamp()}</TIMESTAMP>
<GENERATED_THEME_FILES>
"""

            for file_info in file_data:
                formatted_output += f"""
<FILE>
<FILE_PATH>{file_info['file_path']}</FILE_PATH>
<CODE_CONTENT>
{file_info['code_snippet']}
</CODE_CONTENT>
</FILE>
"""

            formatted_output += """
</GENERATED_THEME_FILES>
</FLUTTER_STAGE_I_CODE_GENERATION>

"""

        except Exception as e:
            # Fallback to raw output if parsing fails
            self.logger.warning(f"Failed to parse XML output: {e}")
            formatted_output = f"""
<FLUTTER_STAGE_I_CODE_GENERATION>
<TIMESTAMP>{self._get_timestamp()}</TIMESTAMP>
<RAW_LLM_OUTPUT>
{llm_output}
</RAW_LLM_OUTPUT>
</FLUTTER_STAGE_I_CODE_GENERATION>

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
