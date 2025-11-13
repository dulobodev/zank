from pydantic import BaseModel, Field


class FilterPage(BaseModel):
    """Schema para filtrar paginas"""

    limit: int = Field(ge=1, default=10)
    offset: int = Field(ge=0, default=0)
