from fastapi import Depends, status
from fastapi.responses import JSONResponse

from system.backend.agentic_workflow.app.models.schemas.ide_agent_schema import (
    IDEAgentRequest,
)
from system.backend.agentic_workflow.app.usecases.ide_agent_usecases.ide_agent_usecase import (
    IDEAgentUsecase,
)


class IDEAgentController:
    def __init__(self, ide_agent_usecase: IDEAgentUsecase = Depends()):
        self.ide_agent_usecase = ide_agent_usecase

    async def execute(self, request: IDEAgentRequest) -> JSONResponse:
        """
        Execute IDE agent operations to debug, modify, and solve errors in generated code

        :param request: IDEAgentRequest containing user query for code assistance
        :return: JSONResponse with IDE agent results, conversation history, and metadata
        """
        try:
            result = await self.ide_agent_usecase.execute(request)

            if result["success"]:
                return JSONResponse(
                    content={
                        "success": True,
                        "message": result["message"],
                        "tool_calls_used": result["tool_calls_used"],
                        "completion_reason": result.get(
                            "completion_reason", "completed"
                        ),
                        "session_id": result["session_id"],
                        "error": None,
                    },
                    status_code=status.HTTP_200_OK,
                )
            else:
                return JSONResponse(
                    content={
                        "success": False,
                        "message": result["message"],
                        "tool_calls_used": result.get("tool_calls_used", 0),
                        "completion_reason": result.get(
                            "completion_reason", "error"
                        ),
                        "session_id": result.get("session_id", ""),
                        "error": result["error"],
                    },
                    status_code=status.HTTP_400_BAD_REQUEST,
                )

        except Exception as e:
            return JSONResponse(
                content={
                    "success": False,
                    "message": "IDE agent execution failed",
                    "tool_calls_used": 0,
                    "completion_reason": "error",
                    "session_id": "",
                    "error": str(e),
                },
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
