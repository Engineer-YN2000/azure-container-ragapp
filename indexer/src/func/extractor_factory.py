from pathlib import Path
from .pdf_extractor import PdfExtractor

EXTRACTOR_MAP = {
    ".pdf": PdfExtractor(),
}

def extract_text_from_file(filepath: str) -> str:
    """Extract text from a file based on its extension."""
    ext = Path(filepath).suffix.lower()
    extractor = EXTRACTOR_MAP.get(ext)
    if extractor:
        return extractor.extract(filepath)
    else:
        print(f"No extractor available for files with extension: {ext}")
        return ""