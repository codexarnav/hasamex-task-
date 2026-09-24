"""Interview guide text extractor.

Extracts readable text from uploaded guide files.
Supports .txt and .pdf formats.
"""
from pathlib import Path

from app.core.exceptions import ParsingError
from app.core.logging import get_logger

logger = get_logger("parsers.guide")


def extract_guide_text(file_content: bytes, filename: str) -> str:
    """Extract readable text from an interview guide file.

    Args:
        file_content: Raw file bytes
        filename: Original filename (used to determine format)

    Returns:
        Extracted text content
    """
    suffix = Path(filename).suffix.lower()

    if suffix == ".txt":
        return _extract_text(file_content)
    elif suffix == ".pdf":
        from app.parsers.pdf_extractor import extract_pdf_text
        return extract_pdf_text(file_content)
    elif suffix in (".md", ".markdown"):
        return _extract_text(file_content)
    else:
        # Try text extraction as fallback
        logger.warning(
            f"Unknown guide format '{suffix}', attempting text extraction",
            extra={"operation": "guide_parse"},
        )
        return _extract_text(file_content)


def _extract_text(content: bytes) -> str:
    """Extract text from a text file."""
    try:
        return content.decode("utf-8")
    except UnicodeDecodeError:
        try:
            return content.decode("latin-1")
        except UnicodeDecodeError:
            raise ParsingError(
                message="Failed to decode guide file",
                detail="File encoding not supported (tried UTF-8, Latin-1)",
            )


def _extract_pdf(content: bytes) -> str:
    """Extract text from a PDF file using PyPDF2 or pdfplumber."""
    try:
        import pdfplumber
        import io

        text_parts = []
        with pdfplumber.open(io.BytesIO(content)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)

        if not text_parts:
            raise ParsingError(
                message="Could not extract text from PDF",
                detail="PDF appears to contain no readable text",
            )
        return "\n\n".join(text_parts)

    except ImportError:
        raise ParsingError(
            message="PDF support requires pdfplumber",
            detail="Install pdfplumber to parse PDF files",
        )
    except ParsingError:
        raise
    except Exception as e:
        raise ParsingError(
            message="Failed to parse PDF guide",
            detail=str(e),
        )
