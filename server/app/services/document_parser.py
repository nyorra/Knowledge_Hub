"""
Document Parser Service - main facade.
Provides simple interface for parsing various document formats.
"""

from pathlib import Path

from app.core.logger import logger
from app.services.parsers.base import ParsedDocument
from app.services.parsers.parser_factory import ParserFactory


class DocumentParserService:
    """
    Main service for parsing documents of various formats.

    Supported formats:
    - Text: .txt, .md, .markdown
    - PDF: .pdf
    - Word: .docx

    Features:
    - Automatic encoding detection (UTF-8, Windows-1251, etc.)
    - Language detection (English, Russian, Chinese, etc.)
    - Metadata extraction (author, title, page count, etc.)
    - Graceful error handling (returns partial results)
    """

    def __init__(self):
        self.factory = ParserFactory()
        logger.info("✓ DocumentParserService initialized")

    def parse_file(self, file_path: Path) -> ParsedDocument:
        """
        Parse document and extract text content.

        Args:
            file_path: Path to the document file

        Returns:
            ParsedDocument with extracted content and metadata

        Example:
            >>> parser = DocumentParserService()
            >>> result = parser.parse_file(Path("document.pdf"))
            >>> print(result.content)
            >>> print(result.language)  # 'en', 'ru', etc.
            >>> print(result.metadata)  # {'page_count': 10, ...}
        """
        logger.info(f"[PARSE] Processing file: {file_path.name}")

        if not file_path.exists():
            logger.error(f"✗ File not found: {file_path}")
            return ParsedDocument(content="", error=f"File not found: {file_path}")

        # Get appropriate parser
        parser = self.factory.get_parser(file_path)

        if parser is None:
            extension = file_path.suffix
            logger.warning(f"⚠ Unsupported file format: {extension}")
            return ParsedDocument(
                content="", error=f"Unsupported file format: {extension}"
            )

        # Parse document
        result = parser.parse(file_path)

        if result.error:
            logger.warning(f"⚠ Parsing completed with errors: {result.error}")
        else:
            logger.info(
                f"✓ Successfully parsed {file_path.name}: {len(result.content)} chars, lang={result.language}"
            )

        return result

    def get_supported_extensions(self) -> set[str]:
        """
        Get list of all supported file extensions.

        Returns:
            Set of supported extensions (e.g., {'.txt', '.pdf', '.docx'})
        """
        extensions = set()
        for parser in self.factory.parsers:
            # Get supported extensions from each parser
            if hasattr(parser, "SUPPORTED_EXTENSIONS"):
                extensions.update(parser.SUPPORTED_EXTENSIONS)
        return extensions


# Global instance
document_parser_service = DocumentParserService()
