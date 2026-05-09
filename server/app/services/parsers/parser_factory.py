"""
Factory for selecting appropriate parser based on file extension.
"""

from pathlib import Path
from typing import Optional

from app.core.logger import logger

from .base import BaseParser
from .docx_parser import DOCXParser
from .pdf_parser import PDFParser
from .text_parser import TextParser


class ParserFactory:
    """
    Factory for creating appropriate parser based on file type.
    Automatically selects parser based on file extension.
    """

    def __init__(self):
        # Register all available parsers
        self.parsers: list[BaseParser] = [
            TextParser(),
            PDFParser(),
            DOCXParser(),
        ]
        logger.debug(f"✓ ParserFactory initialized with {len(self.parsers)} parsers")

    def get_parser(self, file_path: Path) -> Optional[BaseParser]:
        """
        Get appropriate parser for given file.

        Args:
            file_path: Path to the file

        Returns:
            Parser instance or None if format not supported
        """
        extension = file_path.suffix.lower()

        for parser in self.parsers:
            if parser.supports(extension):
                logger.debug(
                    f"Selected parser: {parser.__class__.__name__} for {extension}"
                )
                return parser

        logger.warning(f"No parser found for extension: {extension}")
        return None

    def register_parser(self, parser: BaseParser):
        """
        Register custom parser (for extensibility).

        Args:
            parser: Custom parser instance
        """
        self.parsers.append(parser)
        logger.info(f"✓ Registered custom parser: {parser.__class__.__name__}")
