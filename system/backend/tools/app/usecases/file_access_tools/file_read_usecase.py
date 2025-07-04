from typing import Any, Dict

from fastapi import Depends

from system.backend.tools.app.services.file_access_tools.file_read_service import (
    FileReadService,
)


class FileReadUseCase:
    def __init__(self, file_read_service: FileReadService = Depends()):
        self.file_read_service = file_read_service

    async def execute(
        self,
        file_path: str,
        start_line: int = 0,
        end_line: int = 1500,
    ) -> Dict[str, Any]:

        return await self.file_read_service.read_file(
            file_path, start_line, end_line
        )
