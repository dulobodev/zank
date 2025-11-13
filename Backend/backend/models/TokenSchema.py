from pydantic import BaseModel


class Token(BaseModel):
    """Schema para retornar token (OUTPUT)"""

    access_token: str
    token_type: str
