from pydantic import BaseModel


class IDEAgentRequest(BaseModel):
    user_query: str
