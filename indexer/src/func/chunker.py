from langchain.text_splitter import RecursiveCharacterTextSplitter

class DocChunker:
    def __init__ (self, chunk_size: int = 1000, overlap: int = 200, separators: list[str] = ["\n\n", "\n", " ", ""]):
        """Separate text into chunks of specified size with overlap."""
        self.chunker = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=overlap,
            separators=separators
        )
        
    def chunk_text(self, text: str) -> list[str]:
        """Chunk the provided text and return a list of chunks."""
        return self.chunker.split_text(text)