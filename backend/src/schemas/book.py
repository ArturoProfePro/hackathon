from pydantic import BaseModel


class BookSchema(BaseModel):
    filename: str
    content_type: str
    size: int
    location: str


class CreateBookSchema(BaseModel):
    filename: str
