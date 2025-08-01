import json
import os

from fastapi import Depends

from system.backend.agentic_workflow.app.models.schemas.initial_processing_schema import (
    InitialProcessingRequest,
)
from system.backend.agentic_workflow.app.prompts.context_gathering_prompts.stage_i_prompt import (
    FLUTTER_SYSTEM_PROMPT,
    FLUTTER_USER_PROMPT,
    REACT_SYSTEM_PROMPT,
    REACT_USER_PROMPT,
)
from system.backend.agentic_workflow.app.services.anthropic_services.llm_service import (
    AnthropicService,
)
from system.backend.agentic_workflow.app.utils.parser import parse_model_output
from system.backend.agentic_workflow.app.utils.session_context import (
    session_state,
)


class InitialProcessingUsecase:
    def __init__(self, anthropic_service: AnthropicService = Depends()):
        self.anthropic_service = anthropic_service

    async def execute(self, request: InitialProcessingRequest) -> dict:
        """
        Process initial user query to generate domain analysis, industry patterns,
        screens, and business context, then save to artifacts directory

        :param request: InitialProcessingRequest containing user query and platform type
        :return: Dict with generated context data and metadata
        """
        # Get session_id from context (set by middleware)
        session_id = session_state.get()
        if not session_id:
            raise ValueError("No session_id available in context")
        if request.platform_type == "web":
            system_prompt = REACT_SYSTEM_PROMPT
            user_prompt = REACT_USER_PROMPT
        elif request.platform_type == "mobile":
            system_prompt = FLUTTER_SYSTEM_PROMPT
            user_prompt = FLUTTER_USER_PROMPT
        # Create user prompt
        user_prompt = user_prompt.format(
            user_query=request.user_query, platform_type=request.platform_type
        )

        # Call LLM service
        llm_response = await self.anthropic_service.generate_text(
            prompt=user_prompt,
            system_prompt=system_prompt,
            provider="anthropic",
        )

        # Parse the JSON output from <OUTPUT> tags
        parsed_data = parse_model_output(llm_response)

        # Create artifacts directory structure
        artifacts_dir = f"artifacts/{session_id}/project_context"
        os.makedirs(artifacts_dir, exist_ok=True)

        # Save to stage_i.json file
        stage_file_path = os.path.join(artifacts_dir, "stage_i.json")
        with open(stage_file_path, "w") as f:
            json.dump(parsed_data, f, indent=2)

        # Return result with metadata
        return {
            "data": parsed_data,
            "session_id": session_id,
            "saved_to": stage_file_path,
        }
