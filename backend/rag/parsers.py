from pathlib import Path

from docx import Document as DocxDocument
from pypdf import PdfReader


class DocumentParsingError(Exception):
    """Raised when document text cannot be extracted."""


def parse_pdf(file_path: str) -> str:
    try:
        reader = PdfReader(file_path)
        text = "\n".join(page.extract_text() or "" for page in reader.pages)
    except Exception as exc:
        raise DocumentParsingError("Failed to parse PDF document.") from exc

    if not text.strip():
        raise DocumentParsingError("PDF contains no extractable text.")

    return text


def parse_txt(file_path: str) -> str:
    try:
        return Path(file_path).read_text(encoding="utf-8")
    except Exception as exc:
        raise DocumentParsingError("Failed to read text document.") from exc


def parse_docx(file_path: str) -> str:
    try:
        document = DocxDocument(file_path)
        text = "\n".join(paragraph.text for paragraph in document.paragraphs)
    except Exception as exc:
        raise DocumentParsingError("Failed to parse DOCX document.") from exc

    if not text.strip():
        raise DocumentParsingError("DOCX contains no extractable text.")

    return text


def parse_document(file_path: str) -> str:
    extension = Path(file_path).suffix.lower()

    if extension == ".pdf":
        return parse_pdf(file_path)

    if extension == ".txt":
        return parse_txt(file_path)

    if extension == ".docx":
        return parse_docx(file_path)

    raise DocumentParsingError(f"Unsupported document type: {extension or 'unknown'}")
