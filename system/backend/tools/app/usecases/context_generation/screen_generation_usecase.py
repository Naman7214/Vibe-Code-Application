import json
import os
import sys
from typing import Any, Dict

from fastapi import Depends, HTTPException

project_root = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../../../../..")
)
sys.path.insert(0, project_root)

from system.backend.tools.app.models.schemas.context_generation_schema import (
    ScreenGenerationRequest,
)
from system.backend.tools.app.prompts.context_generation_prompt import (
    SCREEN_PROMPT,
)
from system.backend.tools.app.references.screen_schema_reference import (
    SCREEN_REFERENCE_JSON,
)
from system.backend.tools.app.repositories.error_repo import Error, ErrorRepo
from system.backend.tools.app.services.anthropic_service.llm_service import (
    AnthropicService,
)
from system.backend.tools.app.utils.context_generation_helper import (
    save_individual_screens,
)
from system.backend.tools.app.utils.logger import loggers
from system.backend.tools.app.utils.parser import extract_json_content


class ScreenGenerationUsecase:
    def __init__(
        self,
        anthropic_service: AnthropicService = Depends(),
        error_repo: ErrorRepo = Depends(),
    ):
        self.anthropic_service = anthropic_service
        self.error_repo = error_repo

    async def execute(self, request: ScreenGenerationRequest) -> Dict[str, Any]:
        """
        Generate screens using Anthropic service and save each screen individually

        :param request: ScreenGenerationRequest containing user query and options
        :return: ScreenGenerationResponse with generated screens and file paths
        """
        try:
            formatted_prompt = SCREEN_PROMPT.format(
                REFERENCE_JSON=json.dumps(SCREEN_REFERENCE_JSON, indent=2),
                USER_QUERY=request.user_query,
            )

            loggers["screen_generation"].info(
                f"🤖 Generating screens using Anthropic streaming service..."
            )
            loggers["screen_generation"].info(
                f"🔍 Generating screens for query: {request.user_query}"
            )

            response = self.anthropic_service.anthropic_client_request(
                formatted_prompt
            )

            json_content = extract_json_content(response)

            loggers["screen_generation"].info(
                "🎉 Response received from Anthropic API"
            )

            try:
                parsed_json = json.loads(json_content)
                screen_count = (
                    len(parsed_json) if isinstance(parsed_json, list) else 0
                )
                loggers["screen_generation"].info(
                    f"📊 Generated {len(parsed_json) if isinstance(parsed_json, list) else 'N/A'} screens"
                )
            except json.JSONDecodeError as e:
                self.error_repo.insert_error(
                    Error(
                        tool_name="screen_generation",
                        error_message=f"Generated content may not be valid JSON: {e}",
                    )
                )
                loggers["screen_generation"].warning(
                    f"Generated content may not be valid JSON: {e}"
                )
                parsed_json = []

            if not isinstance(parsed_json, list):
                parsed_json = []

            file_paths = []
            if parsed_json:
                try:
                    screens_dir_path = os.path.join(
                        project_root, request.dir_path
                    )
                    print(f"Saving screens to {screens_dir_path}")
                    file_paths = save_individual_screens(
                        parsed_json, screens_dir_path, request.base_file_name
                    )
                    file_saved = len(file_paths) > 0

                    if file_saved:
                        loggers["screen_generation"].info(
                            f"Successfully saved {len(file_paths)} screen files"
                        )
                    else:
                        loggers["screen_generation"].warning(
                            "No screens were saved to files"
                        )

                except Exception as e:
                    self.error_repo.insert_error(
                        Error(
                            tool_name="screen_generation",
                            error_message=f"Failed to save screens: {str(e)}",
                        )
                    )
                    loggers["screen_generation"].error(
                        f"Failed to save screens: {str(e)}"
                    )
                    file_paths = []

            return {
                "status": "success",
                "number_of_screens": screen_count,
                "file_paths": file_paths,
            }

        except HTTPException as e:
            self.error_repo.insert_error(
                Error(
                    tool_name="screen_generation",
                    error_message=f"Error generating screens: {str(e.detail)}",
                )
            )
            loggers["screen_generation"].error(
                f"Error generating screens: {str(e.detail)}"
            )
            raise HTTPException(
                status_code=500,
                detail="Error generating screens: " + str(e.detail),
            )
