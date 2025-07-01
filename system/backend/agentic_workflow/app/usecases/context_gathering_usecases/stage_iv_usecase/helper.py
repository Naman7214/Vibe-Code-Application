import json
import os
from typing import Any, Dict, List

from system.backend.agentic_workflow.app.utils.logger import loggers


class StageIVHelper:
    def __init__(self):
        self.logger = loggers["stage_iv"]

    def extract_screen_requirements(
        self, stage_ii_data: Dict[str, Any], screen_names: List[str]
    ) -> Dict[str, Any]:
        """
        Extract screen requirements for specified screens from stage_ii data
        """
        screen_requirements = {}

        for screen_name in screen_names:
            if screen_name in stage_ii_data:
                screen_requirements[screen_name] = stage_ii_data[screen_name]

        return screen_requirements

    def extract_screen_specific_components(
        self, stage_iiib_data: Dict[str, Any], screen_names: List[str]
    ) -> Dict[str, Any]:
        """
        Extract screen-specific components for specified screens from stage_iiib data
        """
        screen_specific_components = {}
        stage_iiib_screen_components = stage_iiib_data.get(
            "screen-specific-components", {}
        )

        for screen_name in screen_names:
            if screen_name in stage_iiib_screen_components:
                screen_specific_components[screen_name] = (
                    stage_iiib_screen_components[screen_name]
                )

        return screen_specific_components

    async def read_json_file(self, file_path: str) -> Dict[str, Any]:
        """
        Read and parse JSON file
        """
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                return json.load(file)
        except FileNotFoundError:
            self.logger.error(f"File not found: {file_path}")
            return {}
        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON in file {file_path}: {e}")
            return {}

    async def save_json_file(
        self, file_path: str, data: Dict[str, Any]
    ) -> None:
        """
        Save data to JSON file
        """
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            with open(file_path, "w", encoding="utf-8") as file:
                json.dump(data, file, indent=2, ensure_ascii=False)

        except Exception as e:
            self.logger.error(f"Failed to save file {file_path}: {e}")
            raise

    async def merge_and_save_json_file(
        self, file_path: str, new_data: Dict[str, Any]
    ) -> None:
        """
        Merge new data with existing JSON file and save
        - If screen doesn't exist: append it
        - If screen exists: replace it
        - Preserve other existing screens
        """
        try:
            # Read existing data if file exists
            existing_data = {}
            if os.path.exists(file_path):
                existing_data = await self.read_json_file(file_path)

            # Merge new data with existing data
            # New data will overwrite existing keys, preserve others
            merged_data = {**existing_data, **new_data}

            # Save merged data
            await self.save_json_file(file_path, merged_data)

            self.logger.info(
                f"Successfully merged and saved data to {file_path}"
            )

        except Exception as e:
            self.logger.error(f"Failed to merge and save file {file_path}: {e}")
            raise
