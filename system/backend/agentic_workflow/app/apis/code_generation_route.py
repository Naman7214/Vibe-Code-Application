from fastapi import APIRouter, Depends

from system.backend.agentic_workflow.app.controllers.code_generation_controller import (
    CodeGenerationController,
)
from system.backend.agentic_workflow.app.models.schemas.code_generation_schema import (
    CodeGenerationStageIRequest,
)

router = APIRouter()


@router.post("/stage-i")
async def code_generation_stage_i(
    request: CodeGenerationStageIRequest,
    code_generation_controller: CodeGenerationController = Depends(),
):
    """
    Execute Stage I code generation to create Tailwind CSS configuration and styles
    
    **Headers Required:**
    - X-Session-ID: Session identifier (e.g., "ae96b6a0-7ce4-4f9e-81e5-22e1998cd547")
    
    **Request Body:** Empty JSON object `{}`
    
    **Generated Files:**
    - tailwind.config.js: Complete Tailwind CSS configuration with custom theme
    - src/styles/tailwind.css: Main CSS file with imports and component classes
    
    **Output Location:** artifacts/{session_id}/codebase/
    
    **Scratchpad Updates:**
    - file_structure.txt: Updated directory structure
    - global_scratch_pad.txt: LLM output and generation details
    """
    return await code_generation_controller.execute_stage_i(request) 