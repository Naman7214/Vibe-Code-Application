from fastapi import Depends, status
from fastapi.responses import JSONResponse

from system.backend.tools.app.models.schemas.file_access_schemas import (
    FileSearchRequest,
)
from system.backend.tools.app.usecases.file_access_tools.file_search_usecase import (
    FileSearchUseCase,
)


class FileSearchController:
    def __init__(self, file_search_usecase: FileSearchUseCase = Depends()):
        self.file_search_usecase = file_search_usecase

    async def execute(self, request: FileSearchRequest):
        response = await self.file_search_usecase.execute(
            request.pattern, request.default_path
        )

        return JSONResponse(
            content={
                "data": response,
                "message": "Files searched successfully",
                "error": None,
            },
            status_code=status.HTTP_200_OK,
        )
