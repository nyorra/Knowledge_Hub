from pydantic import BaseModel

"""
Pydantic schemas for request/response validation.
These models ensure type safety and automatic validation for API endpoints.
"""


class AiData(BaseModel):
    question: str


class FileData(BaseModel):
    filename: str
    content: str


class FilesResponse(BaseModel):
    files: list[str]
