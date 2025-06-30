from fastapi import Depends

from system.backend.agentic_workflow.app.config.database import mongodb_database


class LLMUsageRepository:
    def __init__(
        self, collection=Depends(mongodb_database.get_llm_usage_collection)
    ):
        self.collection = collection

    async def add_llm_usage(self, llm_usage: dict):
        try:
            await self.collection.insert_one(llm_usage)
        except Exception as e:
            pass