import json
import os
from datetime import datetime
from typing import Any, Dict

from fastapi import Depends

from system.backend.agentic_workflow.app.prompts.code_generation_prompts.stage_ii_prompt import (
    SYSTEM_PROMPT,
    USER_PROMPT,
)
from system.backend.agentic_workflow.app.services.anthropic_services.llm_service import (
    AnthropicService,
)
from system.backend.agentic_workflow.app.utils.file_structure import (
    generate_directory_structure,
    get_project_root,
)
from system.backend.agentic_workflow.app.utils.write_file import (
    write_code_files,
)
from system.backend.agentic_workflow.app.utils.xml_parser import (
    parse_xml_to_dict,
)


class StageIIHelper:
    def __init__(self, anthropic_service: AnthropicService = Depends()):
        self.anthropic_service = anthropic_service

    async def read_json_file(self, file_path: str) -> Dict[str, Any]:
        """
        Read and parse a JSON file

        :param file_path: Path to the JSON file
        :return: Parsed JSON data as dictionary
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    async def read_text_file(self, file_path: str) -> str:
        """
        Read a text file and return its content

        :param file_path: Path to the text file
        :return: File content as string
        """
        if not os.path.exists(file_path):
            return ""  # Return empty string if file doesn't exist

        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()

    async def read_boilerplate_files(self, session_id: str) -> str:
        """
        Read all boilerplate files and format them for the system prompt

        :param session_id: Session identifier
        :return: Formatted boilerplate files content
        """
        base_path = f"artifacts/{session_id}/codebase/src/components"
        boilerplate_files = [
            "AppIcon.jsx",
            "AppImage.jsx",
            "ErrorBoundary.jsx",
            "ScrollToTop.jsx",
        ]

        formatted_content = ""

        for file_name in boilerplate_files:
            file_path = f"{base_path}/{file_name}"
            content = await self.read_text_file(file_path)

            if content:
                formatted_content += f"\n=== {file_name} ===\n"
                formatted_content += content
                formatted_content += "\n"

        return formatted_content

    async def get_global_components_context(
        self, session_id: str
    ) -> Dict[str, Any]:
        """
        Read global components context from stage_iii_b.json

        :param session_id: Session identifier
        :return: Global components data
        """
        file_path = f"artifacts/{session_id}/project_context/stage_iii_b.json"
        try:
            data = await self.read_json_file(file_path)
            return data.get("global_components", {})
        except FileNotFoundError:
            return {}

    async def get_navigation_structure(self, session_id: str) -> Dict[str, Any]:
        """
        Read navigation structure from stage_v.json

        :param session_id: Session identifier
        :return: Navigation structure data
        """
        file_path = f"artifacts/{session_id}/project_context/stage_v.json"
        try:
            data = await self.read_json_file(file_path)
            navigation_structure = data.get("navigation_structure", {})
            return navigation_structure.get("global_navigation", {})
        except FileNotFoundError:
            return {}

    async def get_scratchpads_content(self, session_id: str) -> Dict[str, str]:
        """
        Read scratchpads content from global_scratchpad.txt and file_structure.txt

        :param session_id: Session identifier
        :return: Dictionary with scratchpad contents
        """
        base_path = f"artifacts/{session_id}/scratchpads"

        scratchpads = {}

        # Read global_scratchpad.txt
        global_scratchpads_path = f"{base_path}/global_scratchpad.txt"
        try:
            scratchpads["global_scratchpad"] = await self.read_text_file(
                global_scratchpads_path
            )
        except FileNotFoundError:
            scratchpads["global_scratchpad"] = ""

        # Read file_structure.txt
        file_structure_path = f"{base_path}/file_structure.txt"
        try:
            scratchpads["file_structure"] = await self.read_text_file(
                file_structure_path
            )
        except FileNotFoundError:
            scratchpads["file_structure"] = ""

        return scratchpads

    async def prepare_llm_context(self, session_id: str) -> Dict[str, Any]:
        """
        Prepare all context data for LLM processing

        :param session_id: Session identifier
        :return: Combined context data for LLM
        """
        # Get all context data
        boilerplate_files = await self.read_boilerplate_files(session_id)
        global_components = await self.get_global_components_context(session_id)
        navigation_structure = await self.get_navigation_structure(session_id)
        scratchpads = await self.get_scratchpads_content(session_id)

        return {
            "boilerplate_files": boilerplate_files,
            "global_components": global_components,
            "navigation_structure": navigation_structure,
            "scratchpads_content": scratchpads,
            "file_structure": scratchpads.get("file_structure", ""),
        }

    async def generate_global_components(
        self, context_data: Dict[str, Any]
    ) -> str:
        """
        Generate global components using LLM

        :param context_data: Prepared context data
        :return: LLM response as string
        """
        # Format the system prompt with boilerplate files
        system_prompt = SYSTEM_PROMPT.format(
            boilerplate_files=context_data["boilerplate_files"]
        )

        # Format the user prompt with context data
        user_prompt = USER_PROMPT.format(
            global_components=json.dumps(
                context_data["global_components"], indent=2
            ),
            navigation_structure=json.dumps(
                context_data["navigation_structure"], indent=2
            ),
            scratchpads_content=json.dumps(
                context_data["scratchpads_content"], indent=2
            ),
            file_structure=context_data["file_structure"],
        )

        # Make LLM call using anthropic_client_request
        response = await self.anthropic_service.anthropic_client_request(
            prompt=user_prompt, system_prompt=system_prompt
        )

        return response

    async def append_to_global_scratchpad(
        self, session_id: str, content: str
    ) -> None:
        """
        Append content to the global_scratchpad.txt file

        :param session_id: Session identifier
        :param content: Content to append
        """
        try:
            scratchpad_path = (
                f"artifacts/{session_id}/scratchpads/global_scratchpad.txt"
            )

            # Ensure the scratchpads directory exists
            os.makedirs(os.path.dirname(scratchpad_path), exist_ok=True)

            # Clean and validate content before writing
            if not content or not content.strip():
                print("Warning: Empty context registry content")
                return

            # Append content to the file
            with open(scratchpad_path, "a", encoding="utf-8") as f:
                f.write(f"\n\n<STAGE_II_CODE_GENERATION>\n")
                f.write(
                    f"<TIMESTAMP>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</TIMESTAMP>\n"
                )
                f.write(f"<CONTEXT_REGISTRY>\n")
                f.write(content)
                f.write(f"\n</CONTEXT_REGISTRY>\n")
                f.write(f"</STAGE_II_CODE_GENERATION>\n")

            print(
                f"Successfully appended context registry to {scratchpad_path}"
            )

        except Exception as e:
            print(f"Error appending to global scratchpad: {str(e)}")
            print(
                f"Content that caused error: {repr(content[:200])}"
            )  # Show first 200 chars
            raise

    async def update_file_structure(self, session_id: str) -> None:
        """
        Generate and update the file structure in file_structure.txt

        :param session_id: Session identifier
        """
        codebase_path = f"{get_project_root()}/artifacts/{session_id}/codebase"

        file_structure_path = (
            f"artifacts/{session_id}/scratchpads/file_structure.txt"
        )

        # Generate directory structure
        if os.path.exists(codebase_path):
            structure = generate_directory_structure(
                codebase_path, max_depth=10
            )

            # Ensure scratchpads directory exists
            os.makedirs(os.path.dirname(file_structure_path), exist_ok=True)

            # Write structure to file
            with open(file_structure_path, "w", encoding="utf-8") as f:
                f.write(structure)

    async def process_llm_response_and_write_files(
        self, llm_response: str, session_id: str
    ) -> None:
        """
        Parse LLM response and write generated files to the codebase
        Handle special case for CONTEXT_REGISTRY file

        :param llm_response: Raw LLM response containing XML
        :param session_id: Session identifier to determine base directory
        """
        # Set base directory to the session's codebase
        base_dir = f"artifacts/{session_id}"

        # Parse XML response to get file data
        file_data_list = parse_xml_to_dict(llm_response)

        # Separate regular files from context registry
        regular_files = []
        context_registry_content = None

        for file_data in file_data_list:
            if file_data["file_path"] == "CONTEXT_REGISTRY":
                context_registry_content = file_data["code_snippet"]
            else:
                regular_files.append(file_data)

        # Write regular files to the codebase
        if regular_files:
            write_code_files(regular_files, base_dir)

        # Append context registry to global_scratchpad.txt
        if context_registry_content:
            await self.append_to_global_scratchpad(
                session_id, context_registry_content
            )

    async def execute_stage_ii_pipeline(
        self, session_id: str
    ) -> Dict[str, Any]:
        """
        Execute the complete stage II pipeline for global components generation

        :param session_id: Session identifier
        :return: Result dictionary with success status and message
        """
        try:
            # Prepare context data
            context_data = await self.prepare_llm_context(session_id)

            # Generate components using LLM
            llm_response = await self.generate_global_components(context_data)

            # Process response and write files
            await self.process_llm_response_and_write_files(
                llm_response, session_id
            )

            # Update file structure after all files are written
            await self.update_file_structure(session_id)

            return {
                "success": True,
                "message": "Stage II global components generation completed successfully",
                "error": None,
            }

        except FileNotFoundError as e:
            return {
                "success": False,
                "message": f"Required context file not found: {str(e)}",
                "error": str(e),
            }
        except json.JSONDecodeError as e:
            return {
                "success": False,
                "message": f"Error parsing JSON context file: {str(e)}",
                "error": str(e),
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Unexpected error in stage II pipeline: {str(e)}",
                "error": str(e),
            }
