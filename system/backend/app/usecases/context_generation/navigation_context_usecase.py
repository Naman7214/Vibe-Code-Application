import json
import os
import sys
from typing import Dict, Any
from fastapi import Depends, HTTPException

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../.."))
sys.path.insert(0, project_root)

from backend.app.models.domain.error import Error
from backend.app.models.schemas.context_generation_schema import NavigationContextGenerationRequest
from backend.app.prompts.context_generation_prompt import NAVIGATION_PROMPT
from backend.app.references.navigation_context_reference import NAVIGATION_REFERENCE_JSON
from backend.app.repositories.error_repo import ErrorRepo
from backend.app.services.anthropic_service.llm_service import AnthropicService
from backend.app.utils.context_generation_helper import load_screens_from_directory
from backend.app.utils.logger import loggers
from backend.app.utils.parser import extract_json_content


class NavigationContextUsecase:
    def __init__(
        self,
        anthropic_service: AnthropicService = Depends(),
        error_repo: ErrorRepo = Depends(),                 
    ):
        self.anthropic_service = anthropic_service
        self.error_repo = error_repo

    async def execute(self, request: NavigationContextGenerationRequest) -> Dict[str, Any]:
        """Generate navigation context using Anthropic service and save to JSON file"""
        
        try:
            loggers["navigation_context"].info(f"🧭 Starting navigation context generation using screens from directory: {request.screens_dir}")
            
            try:
                screens_dir_path = os.path.join(project_root, request.screens_dir)
                screens_json = load_screens_from_directory(screens_dir_path)
                loggers["navigation_context"].info(f"📁 Successfully loaded {len(screens_json)} screens from directory.")
            except FileNotFoundError:
                error_msg = f"Screens directory not found: {request.screens_dir}"
                loggers["navigation_context"].error(error_msg)
                raise HTTPException(status_code=404, detail=error_msg)
            except json.JSONDecodeError as e:
                error_msg = f"Invalid JSON in one of the screen files: {str(e)}"
                loggers["navigation_context"].error(error_msg)
                raise HTTPException(status_code=400, detail=error_msg)
            except Exception as e:
                error_msg = f"Error reading screens directory: {str(e)}"
                loggers["navigation_context"].error(error_msg)
                raise HTTPException(status_code=500, detail=error_msg)
            
            formatted_prompt = NAVIGATION_PROMPT.format(
                REFERENCE_JSON=json.dumps(NAVIGATION_REFERENCE_JSON, indent=2),
                SCREENS_JSON=json.dumps(screens_json, indent=2)
            )
            
            loggers["navigation_context"].info("📝 Prompt formatted with navigation reference JSON")
            
            response = self.anthropic_service.anthropic_client_request(formatted_prompt)
            
            loggers["navigation_context"].info("🔍 Response received from Anthropic API")
            
            json_content = extract_json_content(response)
            
            loggers["navigation_context"].info("✅ Response received from Anthropic API")
        
            try:
                parsed_json = json.loads(json_content)
                loggers["navigation_context"].info("📊 Generated navigation context successfully")
                
                if isinstance(parsed_json, dict) and 'navigationContext' in parsed_json:
                    nav_items_count = len(parsed_json['navigationContext'].get('navigationItems', []))
                    loggers["navigation_context"].info(f"📊 Generated {nav_items_count} navigation items")
                    
            except json.JSONDecodeError as e:
                self.error_repo.insert_error(
                    Error(
                        tool_name="navigation_context_generation",
                        error_message=f"Generated content may not be valid JSON: {e}",
                    )
                )
                loggers["navigation_context"].warning(f"⚠️  Warning: Generated content may not be valid JSON: {e}")
                loggers["navigation_context"].info("💾 Saving raw content anyway...")
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
            
            loggers["navigation_context"].info(f"💾 Successfully saved generated navigation context to {file_path}")
            
            return {
                "status": "success",
                "navigation_context_file_path": file_path,
            }
            
        except HTTPException as e:
            loggers["navigation_context"].error(f"Error generating navigation context: {str(e.detail)}")
            await self.error_repo.insert_error(
                Error(
                    tool_name="navigation_context_generation",
                    error_message=f"Error generating navigation context: {str(e.detail)}",
                )
            )
            raise HTTPException(status_code=500, detail="Error generating navigation context: " + str(e.detail))