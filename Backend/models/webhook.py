from pydantic import BaseModel, Field


class WAHAUser(BaseModel):
    id: str
    pushName: str

    class Config:
        extra = 'allow'


class MessagePayload(BaseModel):
    id: str
    timestamp: int
    from_number: str = Field(..., alias='from')
    to: str
    body: str = Field(default='')
    fromMe: bool

    class Config:
        extra = 'allow'
        populate_by_name = True


class WAHAWebhook(BaseModel):
    id: str
    timestamp: int
    event: str
    session: str
    me: WAHAUser
    payload: MessagePayload

    def is_valid_message(self) -> bool:
        return (
            self.event == 'message'
            and not self.payload.fromMe
            and bool(self.payload.body.strip())
        )

    class Config:
        extra = 'allow'
