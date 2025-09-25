import fitz  # type: ignore


class PdfExtractor:
    def __init__(self):
        pass

    def extract(self, filepath: str) -> str:
        try:
            document = fitz.open(filepath)
            all_text = ""
            for page_num in range(len(document)):
                page = document.load_page(page_num)  # type: ignore
                all_text += page.get_text()  # type: ignore
            return all_text  # type: ignore

        except Exception as e:
            print(f"Error extracting text from {filepath}: {e}")
            return ""
