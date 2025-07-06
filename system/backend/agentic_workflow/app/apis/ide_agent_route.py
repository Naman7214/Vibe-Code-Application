from fastapi import APIRouter, Depends

from system.backend.agentic_workflow.app.controllers.ide_agent_controller import (
    IDEAgentController,
)
from system.backend.agentic_workflow.app.models.schemas.ide_agent_schema import (
    IDEAgentRequest,
)
from system.backend.agentic_workflow.app.utils.error_handler import (
    handle_exceptions,
)

router = APIRouter()


@router.post("/ide-agent")
@handle_exceptions
async def ide_agent(
    request: IDEAgentRequest,
    ide_agent_controller: IDEAgentController = Depends(),
):
    """
    IDE Agent Endpoint

    This endpoint provides an intelligent coding assistant that can debug, modify, and solve errors
    in the generated codebase. The IDE agent has access to various tools including:

    - File operations (read, edit, search, delete)
    - Terminal command execution
    - Code search and analysis
    - Web search for documentation and solutions
    - Directory operations

    The agent operates within the context of a specific session and works on the codebase
    generated for that session (located at artifacts/{session_id}/codebase).

    Key Features:
    - Tool calling loop with maximum 25 tool calls per request
    - Intelligent error handling and debugging
    - Context-aware code modifications
    - Comprehensive logging and conversation history
    - Session-based operation with X-Session-ID header

    Args:
        request: IDEAgentRequest containing:
            - user_query: Natural language description of what you want to accomplish
                         (e.g., "Fix the authentication bug", "Add error handling",
                          "Optimize the database queries")

    Headers:
        X-Session-ID: Required session identifier to locate the codebase

    Returns:
        JSONResponse with:
            - message: Final agent response or summary
            - tool_calls_used: Number of tool calls executed
            - completion_reason: How the agent completed ("natural_completion", "exit_tool", "max_tool_calls", "error")
            - session_id: Session identifier
            - error: Error details if any issues occurred

    Example Usage:
        POST /api/v1/ide-agent
        Headers: X-Session-ID: your-session-id
        Body: {
            "user_query": "The app crashes when I click the submit button. Can you find and fix the issue?"
        }
    """
    return await ide_agent_controller.execute(request)
