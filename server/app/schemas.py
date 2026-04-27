from pydantic import BaseModel

class AskRequest(BaseModel):
    text: str

class AskResponse(BaseModel):
    status: str
    answer: str

class FileData(BaseModel):
    filename: str
    content: str

class FilesResponse(BaseModel):
    files: list[str]    
