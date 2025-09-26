from typing import Any, Dict, List
import logging

import unittest
from unittest.mock import MagicMock, ANY

from src.indexer.clients import AzureEmbeddingClient, AzureSearchClient

logging.basicConfig(
    filename="test.log",
    filemode="a",
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


class TestAzureSearchClient(unittest.TestCase):
    def test_index_chunks_logic(self):
        # 1. Setup
        mock_embedding_client = MagicMock(spec=AzureEmbeddingClient)
        mock_embedding_client.get_embedding.return_value = [0.1, 0.2, 0.3]

        mock_settings = MagicMock()
        mock_settings.search_service_api_key = "fake_api_key_for_test"

        # 2. Act
        client_under_test = AzureSearchClient(mock_settings, mock_embedding_client)

        client_under_test.client = MagicMock()
        mock_sdk_instance = client_under_test.client

        test_chunks = ["Chunk 1 text", "Chunk 2 text"]
        client_under_test.index_chunks(test_chunks)

        # 3. Assert
        self.assertEqual(mock_embedding_client.get_embedding.call_count, 2)
        mock_embedding_client.get_embedding.assert_any_call("Chunk 1 text")
        mock_embedding_client.get_embedding.assert_any_call("Chunk 2 text")

        mock_sdk_instance.upload_documents.assert_called_once()

        actual_call_args = mock_sdk_instance.upload_documents.call_args
        actual_documents = actual_call_args.args[0]

        expected_documents: List[Dict[str, Any]] = [
            {
                "id": ANY,
                "content": "Chunk 1 text",
                "contentVector": [0.1, 0.2, 0.3],
            },
            {
                "id": ANY,
                "content": "Chunk 2 text",
                "contentVector": [0.1, 0.2, 0.3],
            },
        ]

        self.assertEqual(actual_documents, expected_documents)
