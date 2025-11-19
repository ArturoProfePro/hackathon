from pydantic import BaseModel


class PromptResponseSchema(BaseModel):
    message: str


class PromptSchema(BaseModel):
    message: str
