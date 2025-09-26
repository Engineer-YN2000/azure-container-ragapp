import logging
from pathlib import Path
from .pdf_extractor import PdfExtractor

logger = logging.getLogger(__name__)

EXTRACTOR_MAP = {
    ".pdf": PdfExtractor(),
}


def extract_text_from_file(filepath: str) -> str:
    """Extract text from a file based on its extension."""
    ext = Path(filepath).suffix.lower()
    extractor = EXTRACTOR_MAP.get(ext)
    if not extractor:
        logger.warning(
            f"No extractor found for file type '{ext}'. Skipping file: {filepath}"
        )
        return ""

    try:
        logger.info(
            f"Extracting text from '{filepath}' using {extractor.__class__.__name__}."
        )
        return extractor.extract(filepath)
    except Exception as e:
        logger.error(
            f"Failed to extract text from '{filepath}' with {extractor.__class__.__name__}: {e}",
            exc_info=True,
        )
        return ""
