import json
import logging
import os
from typing import Any, Dict

from system.backend.agentic_workflow.app.utils.xml_parser import parse_xml_to_dict


class StageIHelper:
    def __init__(self):
        # Set up a simple logger for code generation
        self.logger = logging.getLogger("code_generation_stage_i")
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

    async def prepare_input_context(self, session_id: str) -> Dict[str, Any]:
        """
        Prepare input context by reading required files
        
        Args:
            session_id: The session ID for file paths
            
        Returns:
            Dict containing all required context data
        """
        # Define file paths
        stage_iii_a_path = f"artifacts/{session_id}/project_context/stage_iii_a.json"
        stage_iv_path = f"artifacts/{session_id}/project_context/stage_iv.json"
        postcss_config_path = f"artifacts/{session_id}/codebase/postcss.config.js"
        package_json_path = f"artifacts/{session_id}/codebase/package.json"
        codebase_path = f"artifacts/{session_id}/codebase"

        context_data = {
            "codebase_path": codebase_path
        }

        # Read stage_iii_a.json (entire file)
        try:
            with open(stage_iii_a_path, "r", encoding="utf-8") as f:
                context_data["stage_iii_a"] = json.load(f)
            self.logger.info(f"Successfully read stage_iii_a.json")
        except FileNotFoundError:
            self.logger.error(f"stage_iii_a.json not found at {stage_iii_a_path}")
            context_data["stage_iii_a"] = {}
        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON in stage_iii_a.json: {e}")
            context_data["stage_iii_a"] = {}

        # Read stage_iv.json and extract specific keys
        try:
            with open(stage_iv_path, "r", encoding="utf-8") as f:
                stage_iv_data = json.load(f)
            
            # Extract specific keys for each page
            filtered_stage_iv = {}
            for page_name, page_data in stage_iv_data.items():
                if isinstance(page_data, dict):
                    filtered_page_data = {}
                    for key in ["screen_design", "component_details", "interactions", "responsive_design"]:
                        if key in page_data:
                            filtered_page_data[key] = page_data[key]
                    if filtered_page_data:
                        filtered_stage_iv[page_name] = filtered_page_data
            
            context_data["stage_iv_a"] = filtered_stage_iv
            self.logger.info(f"Successfully read and filtered stage_iv.json")
        except FileNotFoundError:
            self.logger.error(f"stage_iv.json not found at {stage_iv_path}")
            context_data["stage_iv_a"] = {}
        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON in stage_iv.json: {e}")
            context_data["stage_iv_a"] = {}

        # Read postcss.config.js
        try:
            with open(postcss_config_path, "r", encoding="utf-8") as f:
                context_data["postcss_config"] = f.read()
            self.logger.info(f"Successfully read postcss.config.js")
        except FileNotFoundError:
            self.logger.error(f"postcss.config.js not found at {postcss_config_path}")
            context_data["postcss_config"] = ""

        # Read package.json
        try:
            with open(package_json_path, "r", encoding="utf-8") as f:
                context_data["package_json"] = json.load(f)
            self.logger.info(f"Successfully read package.json")
        except FileNotFoundError:
            self.logger.error(f"package.json not found at {package_json_path}")
            context_data["package_json"] = {}
        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON in package.json: {e}")
            context_data["package_json"] = {}

        return context_data

    async def update_scratchpads(self, session_id: str, llm_output: str, codebase_path: str):
        """
        Update scratchpad files with directory structure and parsed LLM output
        
        Args:
            session_id: The session ID for file paths
            llm_output: The raw LLM output containing XML
            codebase_path: Path to the codebase directory
        """
        scratchpads_dir = f"artifacts/{session_id}/scratchpads"
        os.makedirs(scratchpads_dir, exist_ok=True)

        # Generate and write file structure
        file_structure = self._generate_directory_structure(codebase_path)
        file_structure_path = os.path.join(scratchpads_dir, "file_structure.txt")
        
        with open(file_structure_path, "w", encoding="utf-8") as f:
            f.write(file_structure)
        
        self.logger.info(f"Updated file_structure.txt at {file_structure_path}")

        # Parse XML response to get structured output
        try:
            file_data = parse_xml_to_dict(llm_output)
            
            # Format parsed output for scratchpad
            formatted_output = f"""
<STAGE_I_CODE_GENERATION>
<TIMESTAMP>{self._get_timestamp()}</TIMESTAMP>
<GENERATED_FILES>
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
</GENERATED_FILES>
</STAGE_I_CODE_GENERATION>

"""
            
        except Exception as e:
            # Fallback to raw output if parsing fails
            self.logger.warning(f"Failed to parse XML output: {e}")
            formatted_output = f"""
<STAGE_I_CODE_GENERATION>
<TIMESTAMP>{self._get_timestamp()}</TIMESTAMP>
<RAW_LLM_OUTPUT>
{llm_output}
</RAW_LLM_OUTPUT>
</STAGE_I_CODE_GENERATION>

"""

        # Append to global scratchpad
        global_scratchpad_path = os.path.join(scratchpads_dir, "global_scratch_pad.txt")
        
        with open(global_scratchpad_path, "a", encoding="utf-8") as f:
            f.write(formatted_output)
        
        self.logger.info(f"Updated global_scratch_pad.txt at {global_scratchpad_path}")

    def _generate_directory_structure(self, directory_path: str, prefix: str = "", max_depth: int = 5, current_depth: int = 0) -> str:
        """
        Generate directory structure as a string with absolute path at root
        
        Args:
            directory_path: Path to the directory to analyze
            prefix: Prefix for tree structure display
            max_depth: Maximum depth to traverse
            current_depth: Current depth level
            
        Returns:
            String representation of directory structure with absolute root path
        """
        if current_depth >= max_depth or not os.path.exists(directory_path):
            return ""
        
        # For the root level, show the absolute path
        if current_depth == 0:
            structure = f"{directory_path}/\n"
        else:
            structure = ""
            
        try:
            items = sorted(os.listdir(directory_path))
            for i, item in enumerate(items):
                if item.startswith('.'):
                    continue
                
                item_path = os.path.join(directory_path, item)
                is_last = i == len(items) - 1
                
                current_prefix = "└── " if is_last else "├── "
                structure += f"{prefix}{current_prefix}{item}\n"
                
                if os.path.isdir(item_path) and not item.startswith('.'):
                    next_prefix = prefix + ("    " if is_last else "│   ")
                    structure += self._generate_directory_structure(
                        item_path, next_prefix, max_depth, current_depth + 1
                    )
        except PermissionError:
            pass
        
        return structure

    def _get_timestamp(self) -> str:
        """Get current timestamp as string"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
