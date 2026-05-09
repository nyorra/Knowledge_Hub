"""
Parser for Microsoft Word documents (.docx).
"""

from pathlib import Path

from docx import Document

from app.core.logger import logger

from .base import BaseParser, ParsedDocument


class DOCXParser(BaseParser):
    """
    Parser for DOCX (Microsoft Word) documents.
    Extracts text from paragraphs and tables.
    """

    SUPPORTED_EXTENSIONS = {".docx"}

    def supports(self, extension: str) -> bool:
        return extension.lower() in self.SUPPORTED_EXTENSIONS

    def parse(self, file_path: Path) -> ParsedDocument:
        """
        Parse DOCX file and extract text content.

        Handles:
        - Paragraphs
        - Tables
        - Headers/footers (optional)
        - Multi-language content
        """
        logger.debug(f"[DOCXParser] Parsing: {file_path.name}")

        try:
            doc = Document(file_path)

            # Extract text from paragraphs
            paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]

            # Extract text from tables
            tables_text = []
            for table in doc.tables:
                for row in table.rows:
                    row_text = " | ".join(cell.text.strip() for cell in row.cells)
                    if row_text.strip():
                        tables_text.append(row_text)

            # Combine all text
            content_parts = paragraphs
            if tables_text:
                content_parts.append("\n--- TABLES ---\n")
                content_parts.extend(tables_text)

            content = "\n\n".join(content_parts)

            if not content.strip():
                logger.warning(f"  No text extracted from {file_path.name}")
                return ParsedDocument(
                    content="", error="DOCX file is empty or contains only images"
                )

            # Detect language
            language = self._detect_language(content)

            # Build metadata
            metadata = {
                "paragraph_count": len(paragraphs),
                "table_count": len(doc.tables),
                "char_count": len(content),
            }

            # Try to extract core properties
            try:
                core_props = doc.core_properties
                metadata.update(
                    {
                        "author": core_props.author or "",
                        "title": core_props.title or "",
                        "created": str(core_props.created)
                        if core_props.created
                        else "",
                        "modified": str(core_props.modified)
                        if core_props.modified
                        else "",
                    }
                )
            except Exception as e:
                logger.debug(f"  Could not extract core properties: {e}")

            logger.debug(
                f"✓ Parsed {file_path.name}: {len(paragraphs)} paragraphs, {len(content)} chars, lang={language}"
            )

            return ParsedDocument(content=content, language=language, metadata=metadata)

        except Exception as e:
            logger.error(f"✗ Failed to parse DOCX {file_path.name}: {e}")
            return ParsedDocument(content="", error=f"DOCX parsing failed: {str(e)}")
