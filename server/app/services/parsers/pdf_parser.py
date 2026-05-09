"""
Parser for PDF files.
Uses pypdf as primary parser, pdfplumber as fallback.
"""

from pathlib import Path

from pypdf import PdfReader

from app.core.logger import logger

from .base import BaseParser, ParsedDocument


class PDFParser(BaseParser):
    """
    Parser for PDF documents.
    Extracts text from all pages, handles multi-language PDFs.
    """

    SUPPORTED_EXTENSIONS = {".pdf"}

    def supports(self, extension: str) -> bool:
        return extension.lower() in self.SUPPORTED_EXTENSIONS

    def parse(self, file_path: Path) -> ParsedDocument:
        """
        Parse PDF file and extract text from all pages.

        Handles:
        - Multi-page documents
        - Unicode text (Cyrillic, Chinese, Arabic, etc.)
        - Encrypted PDFs (if no password required)
        """
        logger.debug(f"[PDFParser] Parsing: {file_path.name}")

        try:
            reader = PdfReader(file_path)

            # Extract metadata
            metadata = {
                "page_count": len(reader.pages),
                "is_encrypted": reader.is_encrypted,
            }

            # Try to extract PDF metadata
            if reader.metadata:
                metadata.update(
                    {
                        "author": reader.metadata.get("/Author", ""),
                        "title": reader.metadata.get("/Title", ""),
                        "creator": reader.metadata.get("/Creator", ""),
                    }
                )

            # Extract text from all pages
            pages_text = []
            for i, page in enumerate(reader.pages):
                try:
                    text = page.extract_text()
                    if text.strip():
                        pages_text.append(text)
                except Exception as e:
                    logger.warning(f"  Failed to extract page {i + 1}: {e}")

            content = "\n\n".join(pages_text)

            if not content.strip():
                logger.warning(
                    f"  No text extracted from {file_path.name} (scanned PDF?)"
                )
                return ParsedDocument(
                    content="",
                    metadata=metadata,
                    error="PDF contains no extractable text (possibly scanned image)",
                )

            # Detect language
            language = self._detect_language(content)
            metadata["char_count"] = len(content)

            logger.debug(
                f"✓ Parsed {file_path.name}: {len(reader.pages)} pages, {len(content)} chars, lang={language}"
            )

            return ParsedDocument(content=content, language=language, metadata=metadata)

        except Exception as e:
            logger.error(f"✗ Failed to parse PDF {file_path.name}: {e}")

            # Try fallback with pdfplumber
            return self._parse_with_fallback(file_path, str(e))

    def _parse_with_fallback(
        self, file_path: Path, original_error: str
    ) -> ParsedDocument:
        """
        Fallback parser using pdfplumber for complex PDFs.
        """
        try:
            import pdfplumber

            logger.debug("  Trying fallback parser (pdfplumber)...")

            with pdfplumber.open(file_path) as pdf:
                pages_text = []
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        pages_text.append(text)

                content = "\n\n".join(pages_text)

                if content.strip():
                    logger.info(f"✓ Fallback parser succeeded for {file_path.name}")
                    return ParsedDocument(
                        content=content,
                        language=self._detect_language(content),
                        metadata={"page_count": len(pdf.pages), "parser": "pdfplumber"},
                    )

        except ImportError:
            logger.warning("pdfplumber not installed, cannot use fallback")
        except Exception as e:
            logger.error(f"  Fallback parser also failed: {e}")

        return ParsedDocument(content="", error=f"PDF parsing failed: {original_error}")
