from typing import Any, Dict, List, Optional

from fastapi import Depends

from system.backend.tools.app.services.file_access_tools.file_search_service import (
    FileSearchService,
)


class FileSearchUseCase:
    def __init__(self, file_search_service: FileSearchService = Depends()):
        self.file_search_service = file_search_service

    async def execute(
        self, pattern: str, default_path: str
    ) -> List[Dict[str, Any]]:

        return await self.file_search_service.search_files(
            pattern, default_path
        )
