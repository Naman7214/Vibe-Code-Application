from typing import Any, Dict
import os

from fastapi import Depends, HTTPException

from system.backend.agentic_workflow.app.models.domain.error import Error
from system.backend.agentic_workflow.app.repositories.error_repo import (
    ErrorRepo,
)
from system.backend.agentic_workflow.app.utils.session_context import (
    session_state,
)
from system.backend.agentic_workflow.app.utils.flutter_routes_generator import (
    generate_flutter_routes_for_project,
)

from .helper import FlutterStageIIIHelper


class FlutterStageIIIUsecase:
    def __init__(
        self,
        error_repo: ErrorRepo = Depends(),
    ):
        self.error_repo = error_repo
        self.helper = FlutterStageIIIHelper()

    async def execute(
        self, screen_dict: Dict[str, str], is_follow_up: bool = False
    ) -> Dict[str, Any]:
        """
        Execute Flutter Stage III processing for code generation
        Generates routes/app_routes.dart file using heuristic analysis of the presentation structure

        Args:
            screen_dict: Dictionary with screen names as keys and descriptions as values
            is_follow_up: Flag indicating if this is a follow-up request

        Returns:
            Dict with success status and message
        """
        try:
            # Get session ID from context variable
            session_id = session_state.get()
            if not session_id:
                raise ValueError("Session ID not found in context")

            # Use heuristic Flutter routes generator
            codebase_path = f"artifacts/{session_id}/codebase"
            lib_path = f"{codebase_path}/lib"
            routes_dir = f"{lib_path}/routes"
            routes_file_path = f"{routes_dir}/app_routes.dart"

            # Ensure routes directory exists
            os.makedirs(routes_dir, exist_ok=True)

            # Generate routes using the heuristic generator
            routes_content, analysis = generate_flutter_routes_for_project(
                lib_path=lib_path,
                output_path=routes_file_path
            )

            # Create context registry content
            context_registry_content = self._generate_context_registry(analysis)

            # Update file structure to reflect newly generated files
            await self.helper.update_file_structure(session_id, codebase_path)

            # Update scratchpad files with the generated content
            await self.helper.update_scratchpads_with_generated_content(
                session_id, routes_content, context_registry_content, codebase_path
            )

            return {
                "success": True,
                "message": "Flutter Stage III code generation completed successfully using heuristic routes generator",
                "error": None,
                "generated_files": ["lib/routes/app_routes.dart"],
                "analysis": analysis,
            }

        except HTTPException as e:
            await self.error_repo.insert_error(
                Error(
                    phase="flutter_code_generation_stage_iii",
                    error_message="Error in Flutter Stage III code generation usecase: "
                    + str(e.detail),
                    stack_trace=e.with_traceback(),
                )
            )
            return {
                "success": False,
                "message": "Error in Flutter Stage III code generation usecase: "
                + str(e.detail),
                "error": e.detail,
            }
        except Exception as e:
            await self.error_repo.insert_error(
                Error(
                    phase="flutter_code_generation_stage_iii",
                    error_message="Unexpected error in Flutter Stage III code generation usecase: "
                    + str(e),
                    stack_trace=str(e),
                )
            )
            return {
                "success": False,
                "message": "Unexpected error in Flutter Stage III code generation usecase: "
                + str(e),
                "error": str(e),
            }

    def _generate_context_registry(self, analysis: Dict) -> str:
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
