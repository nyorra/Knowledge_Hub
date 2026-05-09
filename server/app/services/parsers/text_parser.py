"""
Parser for plain text files (.txt, .md).
Handles encoding detection for multi-language support.
"""

from pathlib import Path

import chardet

from app.core.logger import logger

from .base import BaseParser, ParsedDocument


class TextParser(BaseParser):
    """
    Parser for plain text and Markdown files.
    Automatically detects encoding (UTF-8, Windows-1251, etc.).
    """

    SUPPORTED_EXTENSIONS = {".txt", ".md", ".markdown", ".text"}

    def supports(self, extension: str) -> bool:
        return extension.lower() in self.SUPPORTED_EXTENSIONS

    def parse(self, file_path: Path) -> ParsedDocument:
        """
        Parse text file with automatic encoding detection.

        Handles:
        - UTF-8 (English, Russian, Chinese, etc.)
        - Windows-1251 (Russian legacy)
        - ISO-8859-1 (Latin)
        - And 30+ other encodings via chardet
        """
        logger.debug(f"[TextParser] Parsing: {file_path.name}")

        try:
            # Step 1: Detect encoding
            with open(file_path, "rb") as f:
                raw_data = f.read()

            detected = chardet.detect(raw_data)
            encoding = detected["encoding"] or "utf-8"
            confidence = detected["confidence"]

            logger.debug(
                f"  Detected encoding: {encoding} (confidence: {confidence:.2f})"
            )

            # Step 2: Decode with detected encoding
            try:
                content = raw_data.decode(encoding)
            except (UnicodeDecodeError, LookupError):
                # Fallback to UTF-8 with error handling
                logger.warning(
                    f"  Failed to decode with {encoding}, falling back to UTF-8"
                )
                content = raw_data.decode("utf-8", errors="replace")

            # Step 3: Detect language
            language = self._detect_language(content)

            # Step 4: Build metadata
            metadata = {
                "encoding": encoding,
                "encoding_confidence": confidence,
                "file_size": len(raw_data),
                "char_count": len(content),
            }

            logger.debug(
                f"✓ Parsed {file_path.name}: {len(content)} chars, lang={language}"
            )

            return ParsedDocument(content=content, language=language, metadata=metadata)

        except Exception as e:
            logger.error(f"✗ Failed to parse {file_path.name}: {e}")
            return ParsedDocument(content="", error=f"Text parsing failed: {str(e)}")
