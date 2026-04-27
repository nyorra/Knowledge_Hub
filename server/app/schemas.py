from pydantic import BaseModel


class AiData(BaseModel):
    question: str


class FileData(BaseModel):
    filename: str
    content: str


class FilesResponse(BaseModel):
    files: list[str]
