import logging

import azure.functions as func
import unittest
from unittest.mock import patch, MagicMock

from src.indexer.function_app import indexer

logging.basicConfig(
    filename="test.log",
    filemode="a",
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


class TestIndexerFunction(unittest.TestCase):
    @patch("src.indexer.function_app.search_client")
    @patch("src.indexer.function_app.extract_text_from_file")
    @patch("src.indexer.function_app.chunk_text")
    def test_indexer_happy_path(
        self,
        mock_chunk: MagicMock,
        mock_extract: MagicMock,
        mock_search_client: MagicMock,
    ):
        # --- 1. dummy data ---
        mock_extract.return_value = "This is some extracted text."
        mock_chunk.return_value = ["Chunk 1", "Chunk 2"]

        # --- 2. create a mock HTTP request ---
        req = MagicMock(spec=func.HttpRequest)
        mock_file = MagicMock(filename="test.pdf", read=lambda: b"fake file content")
        req.files = {"file": mock_file}

        # --- 3. call the indexer function ---
        response = indexer(req)

        # --- 4. assertions ---
        self.assertEqual(response.status_code, 200)

        mock_extract.assert_called_once()
        mock_chunk.assert_called_once_with("This is some extracted text.")
        mock_search_client.index_chunks.assert_called_once_with(["Chunk 1", "Chunk 2"])
