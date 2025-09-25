import unittest
from unittest.mock import patch, MagicMock
import azure.functions as func
import logging

from function_app import indexer

logging.basicConfig(
    filename="test_function.log",
    filemode="w",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


class TestIndexerFunction(unittest.TestCase):
    @patch("function_app.Settings")
    @patch("function_app.AzureSearchClient")
    @patch("function_app.extract_text_from_file")
    @patch("function_app.chunk_text")
    def test_indexer_happy_path(
        self,
        mock_chunk: MagicMock,
        mock_extract: MagicMock,
        mock_search_client: MagicMock,
        mock_settings: MagicMock,
    ):
        # --- 1. dummy data ---
        mock_extract.return_value = "This is some extracted text."
        mock_chunk.return_value = ["Chunk 1", "Chunk 2"]

        mock_search_client_instance = mock_search_client.return_value

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
        mock_search_client.assert_called_once()
        mock_search_client_instance.index_chunks.assert_called_once_with(
            ["Chunk 1", "Chunk 2"]
        )
