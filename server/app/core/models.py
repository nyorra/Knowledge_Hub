"""
SQLAlchemy ORM models for Knowledge Hub.
Tracks files, users, queries, and system metadata.
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Base class for all database models."""

    pass


class User(Base):
    """User accounts for authentication and tracking."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False, index=True
    )
    email: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False, index=True
    )
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    files: Mapped[list["File"]] = relationship(
        "File", back_populates="owner", cascade="all, delete-orphan"
    )
    queries: Mapped[list["Query"]] = relationship(
        "Query", back_populates="user", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}')>"


class File(Base):
    """Uploaded files with metadata and versioning."""

    __tablename__ = "files"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    filename: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)
    file_type: Mapped[str] = mapped_column(String(50), nullable=False)
    mime_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    language: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    char_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    page_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    chunk_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_indexed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    indexing_error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    parent_file_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("files.id"), nullable=True
    )

    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    owner_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=True
    )

    owner: Mapped[Optional["User"]] = relationship("User", back_populates="files")
    versions: Mapped[list["File"]] = relationship(
        "File", remote_side=[id], backref="parent"
    )
    queries: Mapped[list["Query"]] = relationship(
        "Query", secondary="query_files", back_populates="source_files"
    )

    def __repr__(self):
        return (
            f"<File(id={self.id}, filename='{self.filename}', version={self.version})>"
        )


class Query(Base):
    """User queries and AI responses for analytics."""

    __tablename__ = "queries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    question: Mapped[str] = mapped_column(Text, nullable=False)
    answer: Mapped[str] = mapped_column(Text, nullable=False)

    response_time_ms: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    chunks_retrieved: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    context_length: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    model_used: Mapped[str] = mapped_column(
        String(100), default="llama-3.1-8b-instruct", nullable=False
    )

    user_rating: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    user_feedback: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )

    user_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=True
    )

    user: Mapped[Optional["User"]] = relationship("User", back_populates="queries")
    source_files: Mapped[list["File"]] = relationship(
        "File", secondary="query_files", back_populates="queries"
    )

    def __repr__(self):
        return f"<Query(id={self.id}, question='{self.question[:50]}...')>"


class QueryFile(Base):
    """Association table linking queries to source files."""

    __tablename__ = "query_files"

    query_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("queries.id"), primary_key=True
    )
    file_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("files.id"), primary_key=True
    )
    relevance_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)


class SystemMetrics(Base):
    """System-wide metrics and health monitoring."""

    __tablename__ = "system_metrics"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    metric_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    metric_value: Mapped[float] = mapped_column(Float, nullable=False)
    metric_unit: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    recorded_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False, index=True
    )

    def __repr__(self):
        return f"<SystemMetrics(metric_name='{self.metric_name}', value={self.metric_value})>"
