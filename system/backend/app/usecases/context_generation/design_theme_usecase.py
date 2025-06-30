import json
import os
import sys
from typing import Dict, Any
from fastapi import Depends, HTTPException

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../.."))
sys.path.insert(0, project_root)

from backend.app.models.domain.error import Error
from backend.app.models.schemas.context_generation_schema import DesignThemeGenerationRequest
from backend.app.prompts.context_generation_prompt import DESIGN_PROMPT
from backend.app.references.design_theme_reference import DESIGN_REFERENCE_JSON
from backend.app.repositories.error_repo import ErrorRepo
from backend.app.services.anthropic_service.llm_service import AnthropicService
from backend.app.utils.logger import loggers
from backend.app.utils.parser import extract_json_content


class DesignThemeUsecase:
    def __init__(
        self,
        anthropic_service: AnthropicService = Depends(),
        error_repo: ErrorRepo = Depends(),
    ):
        self.anthropic_service = anthropic_service
        self.error_repo = error_repo

    async def execute(self, request: DesignThemeGenerationRequest) -> Dict[str, Any]:
        """Generate design theme using Anthropic service and save to JSON file"""
        
        try:
            loggers["design_theme"].info(f"Starting design theme generation for query: {request.user_query}")
            
            formatted_prompt = DESIGN_PROMPT.format(
                REFERENCE_JSON=json.dumps(DESIGN_REFERENCE_JSON, indent=2),
                USER_QUERY=request.user_query,
            )
            
            loggers["design_theme"].info("📝 Prompt formatted with reference JSON and user query")
            
            response = self.anthropic_service.anthropic_client_request(formatted_prompt)
            
            loggers["design_theme"].info("🔍 Response received from Anthropic API")
            
            json_content = extract_json_content(response)
            
            loggers["design_theme"].info("✅ Response received from Anthropic API")
        
            try:
                parsed_json = json.loads(json_content)
                loggers["design_theme"].info("📊 Generated design theme successfully")
                
                # Check if it's a design theme structure
                if isinstance(parsed_json, dict) and 'designTheme' in parsed_json:
                    theme_name = parsed_json['designTheme'].get('name', 'Unknown')
                    loggers["design_theme"].info(f"🎨 Theme Name: {theme_name}")
                elif isinstance(parsed_json, dict) and 'name' in parsed_json:
                    theme_name = parsed_json.get('name', 'Unknown')
                    loggers["design_theme"].info(f"🎨 Theme Name: {theme_name}")
                    
            except json.JSONDecodeError as e:
                self.error_repo.insert_error(
                    Error(
                        tool_name="design_theme_generation",
                        error_message=f"Generated content may not be valid JSON: {e}",
                    )
                )
                loggers["design_theme"].warning(f"⚠️  Warning: Generated content may not be valid JSON: {e}")
                loggers["design_theme"].info("💾 Saving raw content anyway...")
                parsed_json = json_content
            
            context_dir_path = os.path.join(project_root, request.dir_path)
            if not os.path.exists(context_dir_path):
                os.makedirs(context_dir_path)
            
            file_path = os.path.join(context_dir_path, request.output_file)
            with open(file_path, "w", encoding="utf-8") as f:
                if isinstance(parsed_json, str):
                    f.write(parsed_json)
                else:
                    json.dump(parsed_json, f, indent=2, ensure_ascii=False)
            
            loggers["design_theme"].info(f"💾 Successfully saved generated design theme to {file_path}")
            
            return {
                "status": "success",
                "design_theme_file_path": file_path,
            }
            
        except HTTPException as e:
            loggers["design_theme"].error(f"Error generating design theme: {str(e.detail)}")
            await self.error_repo.insert_error(
                Error(
                    tool_name="design_theme_generation",
                    error_message=f"Error generating design theme: {str(e.detail)}",
                )
            )
            raise HTTPException(status_code=500, detail="Error generating design theme: " + str(e.detail))