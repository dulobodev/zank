from pydantic import BaseModel


class Message(BaseModel):
    """Schema para retornar message (OUTPUT)"""

    message: str
