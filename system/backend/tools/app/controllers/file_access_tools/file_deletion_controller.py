from fastapi import Depends, status
from fastapi.responses import JSONResponse

from system.backend.tools.app.models.schemas.file_access_schemas import (
    FilesDeleteRequest,
)
from system.backend.tools.app.usecases.file_access_tools.file_deletion_usecase import (
    FileDeletionUseCase,
)


class FileDeletionController:
    def __init__(self, file_deletion_usecase: FileDeletionUseCase = Depends()):
        self.file_deletion_usecase = file_deletion_usecase

    async def execute(self, request: FilesDeleteRequest):
        response = await self.file_deletion_usecase.execute(
            request.path
        )

        return JSONResponse(
            content={
                "data": response,
                "message": "File deleted successfully",
                "error": None,
            },
            status_code=status.HTTP_200_OK,
        )
