"""
Base class for all document parsers.
Defines common interface and metadata structure.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from app.core.logger import logger


@dataclass
class ParsedDocument:
    """
    Result of document parsing.

    Attributes:
        content: Extracted text content
        language: Detected language code (e.g., 'en', 'ru', 'zh')
        metadata: Additional metadata (author, title, page_count, etc.)
        error: Error message if parsing failed partially
    """

    content: str
    language: Optional[str] = None
    metadata: dict = None
    error: Optional[str] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class BaseParser(ABC):
    """
    Abstract base class for document parsers.
    All format-specific parsers must inherit from this.
    """

    @abstractmethod
    def parse(self, file_path: Path) -> ParsedDocument:
        """
        Parse document and extract text content.

        Args:
            file_path: Path to the document file

        Returns:
            ParsedDocument with extracted content and metadata
        """
        pass

    @abstractmethod
    def supports(self, extension: str) -> bool:
        """
        Check if this parser supports given file extension.

        Args:
            extension: File extension (e.g., '.pdf', '.docx')

        Returns:
            True if parser can handle this format
        """
        pass

    def _detect_language(self, text: str) -> Optional[str]:
        """
        Detect language of the text content.

        Args:
            text: Text content to analyze

        Returns:
            ISO 639-1 language code (e.g., 'en', 'ru') or None
        """
        if not text or len(text.strip()) < 50:
            return None

        try:
            from langdetect import detect

            return detect(text[:1000])  # Analyze first 1000 chars
        except Exception as e:
            logger.warning(f"Language detection failed: {e}")
            return None
