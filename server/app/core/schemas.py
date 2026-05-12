from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator

# ============================================================================
# REQUEST SCHEMAS
# ============================================================================


class AiData(BaseModel):
    question: str = Field(
        ..., min_length=1, max_length=2000, description="User question"
    )


class FileData(BaseModel):
    filename: str = Field(..., min_length=1, max_length=255)
    content: str = Field(..., min_length=1)


class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)


class UserLogin(BaseModel):
    username: str
    password: str


class QueryFeedback(BaseModel):
    query_id: int
    rating: int = Field(..., ge=1, le=5, description="Rating from 1 to 5")
    feedback: Optional[str] = Field(None, max_length=1000)


# ============================================================================
# RESPONSE SCHEMAS
# ============================================================================


class FilesResponse(BaseModel):
    files: list[str]


class FileMetadataResponse(BaseModel):
    """Detailed file information."""

    id: int
    filename: str
    original_filename: str
    file_size: int
    file_type: str
    language: Optional[str]
    char_count: Optional[int]
    page_count: Optional[int]
    chunk_count: int
    is_indexed: bool
    version: int
    created_at: datetime
    updated_at: datetime
    owner_id: Optional[int]

    class Config:
        from_attributes = True


class QueryResponse(BaseModel):
    """AI answer with metadata."""

    id: int
    question: str
    answer: str
    response_time_ms: Optional[float]
    chunks_retrieved: int
    source_files: list[str]
    created_at: datetime

    class Config:
        from_attributes = True


class UserResponse(BaseModel):
    """User profile information."""

    id: int
    username: str
    email: str
    is_active: bool
    is_admin: bool
    created_at: datetime
    last_login: Optional[datetime]

    class Config:
        from_attributes = True


class AnalyticsResponse(BaseModel):
    """System analytics and statistics."""

    total_files: int
    total_queries: int
    total_chunks: int
    avg_response_time_ms: Optional[float]
    most_queried_files: list[dict]
    queries_per_day: list[dict]


# ============================================================================
# VALIDATORS
# ============================================================================


class FileUploadValidator(BaseModel):
    """Validation for file uploads."""

    max_size_mb: int = 50
    allowed_extensions: list[str] = [".txt", ".md", ".pdf", ".docx", ".markdown"]

    @field_validator("allowed_extensions")
    @classmethod
    def validate_extensions(cls, v):
        return [ext.lower() if ext.startswith(".") else f".{ext.lower()}" for ext in v]
