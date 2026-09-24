"""Robust multi-tier PDF text extraction engine.

Tier 1: PyMuPDF (fitz) - Native high-speed text extraction
Tier 2: pdfplumber - Layout-based text extraction fallback
Tier 3: Tesseract OCR - Local OCR via pytesseract + PyMuPDF page rendering
Tier 4: Gemini Vision OCR - Multimodal LLM OCR fallback for vector-path/scanned PDFs
"""
import io
import os
from pathlib import Path

from app.core.config import get_settings
from app.core.exceptions import ParsingError
from app.core.logging import get_logger

logger = get_logger("parsers.pdf")


def extract_pdf_text(content: bytes) -> str:
    """Extract text from a PDF file using a resilient multi-tier fallback pipeline.

    Args:
        content: Raw PDF bytes

    Returns:
        Extracted transcript / document text

    Raises:
        ParsingError: If all extraction methods fail to extract readable text
    """
    logger.info(
        f"Starting PDF text extraction ({len(content)} bytes)",
        extra={"operation": "pdf_extract"},
    )

    text = _extract_pymupdf(content)
    if text and text.strip():
        logger.info(
            f"PyMuPDF extracted {len(text)} chars",
            extra={"operation": "pdf_extract", "engine": "pymupdf"},
        )
        return text

    text = _extract_pdfplumber(content)
    if text and text.strip():
        logger.info(
            f"pdfplumber extracted {len(text)} chars",
            extra={"operation": "pdf_extract", "engine": "pdfplumber"},
        )
        return text

    logger.warning(
        "Direct text extraction yielded no characters (likely a scanned or vector-path PDF). Initiating OCR...",
        extra={"operation": "pdf_extract"},
    )

    text = _extract_tesseract_ocr(content)
    if text and text.strip():
        logger.info(
            f"Tesseract OCR extracted {len(text)} chars",
            extra={"operation": "pdf_extract", "engine": "tesseract"},
        )
        return text

    text = _extract_gemini_vision(content)
    if text and text.strip():
        logger.info(
            f"Gemini Vision OCR extracted {len(text)} chars",
            extra={"operation": "pdf_extract", "engine": "gemini_vision"},
        )
        return text

    raise ParsingError(
        message="Could not extract text from PDF",
        detail="All extraction methods (PyMuPDF, pdfplumber, Tesseract, Gemini Vision) failed to extract readable text.",
    )


def _extract_pymupdf(content: bytes) -> str:
    """Extract embedded text using PyMuPDF."""
    try:
        import pymupdf

        doc = pymupdf.open(stream=content, filetype="pdf")
        text_parts = []
        for page in doc:
            page_text = page.get_text("text")
            if page_text and page_text.strip():
                text_parts.append(page_text.strip())
        doc.close()
        return "\n\n".join(text_parts)
    except Exception as e:
        logger.debug(f"PyMuPDF extraction failed: {e}")
        return ""


def _extract_pdfplumber(content: bytes) -> str:
    """Extract embedded text using pdfplumber."""
    try:
        import pdfplumber

        text_parts = []
        with pdfplumber.open(io.BytesIO(content)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text and page_text.strip():
                    text_parts.append(page_text.strip())
        return "\n\n".join(text_parts)
    except Exception as e:
        logger.debug(f"pdfplumber extraction failed: {e}")
        return ""


def _extract_tesseract_ocr(content: bytes) -> str:
    """Extract text by rendering PDF pages and running local Tesseract OCR."""
    try:
        import pymupdf
        import pytesseract
        from PIL import Image

        common_paths = [
            r"C:\Program Files\Tesseract-OCR\tesseract.exe",
            r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
            os.path.expandvars(r"%LOCALAPPDATA%\Programs\Tesseract-OCR\tesseract.exe"),
        ]
        for p in common_paths:
            if Path(p).exists():
                pytesseract.pytesseract.tesseract_cmd = p
                break

        doc = pymupdf.open(stream=content, filetype="pdf")
        text_parts = []
        for page in doc:
            zoom = 300 / 72
            mat = pymupdf.Matrix(zoom, zoom)
            pix = page.get_pixmap(matrix=mat)
            img = Image.open(io.BytesIO(pix.tobytes("png")))
            page_text = pytesseract.image_to_string(img)
            if page_text and page_text.strip():
                text_parts.append(page_text.strip())
        doc.close()
        return "\n\n".join(text_parts)
    except Exception as e:
        logger.debug(f"Tesseract OCR failed: {e}")
        return ""


def _extract_gemini_vision(content: bytes) -> str:
    """Extract text by rendering PDF pages and passing images to Gemini Vision."""
    try:
        import pymupdf
        from google import genai
        from google.genai import types

        settings = get_settings()
        if not settings.GEMINI_API_KEY:
            logger.warning("GEMINI_API_KEY not configured, skipping Gemini Vision OCR")
            return ""

        client = genai.Client(api_key=settings.GEMINI_API_KEY)
        doc = pymupdf.open(stream=content, filetype="pdf")

        image_parts = []
        for page in doc:
            zoom = 2.0
            mat = pymupdf.Matrix(zoom, zoom)
            pix = page.get_pixmap(matrix=mat)
            img_bytes = pix.tobytes("png")
            image_parts.append(types.Part.from_bytes(data=img_bytes, mime_type="image/png"))
        doc.close()

        if not image_parts:
            return ""

        prompt = (
            "You are an expert document transcription engine. Transcribe all text from these document pages verbatim. "
            "Preserve all speaker names, timestamps (e.g. [00:00] or 00:00), questions, answers, and dialogue structure exactly as written. "
            "Do not summarize or omit anything. Output only the verbatim transcription."
        )

        response = client.models.generate_content(
            model=settings.GEMINI_MODEL,
            contents=[prompt] + image_parts,
        )

        return response.text or ""
    except Exception as e:
        logger.warning(f"Gemini Vision OCR failed: {e}")
        return ""
