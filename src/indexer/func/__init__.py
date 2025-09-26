from .chunker import DocChunker
from .extractor_factory import extract_text_from_file

_default_chunker = DocChunker(chunk_size=1000, overlap=200)
chunk_text = _default_chunker.chunk_text


__all__ = [
    "DocChunker",
    "chunk_text",
    "extract_text_from_file",
]
