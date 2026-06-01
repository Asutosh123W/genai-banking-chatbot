from pydantic import BaseModel


class ChatRequest(BaseModel):

    message: str

    knowledge_base: str = "general"

    session_id: int