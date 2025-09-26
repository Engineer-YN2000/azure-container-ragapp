import logging

import unittest

from src.indexer.func import DocChunker

logging.basicConfig(
    filename="test.log",
    filemode="a",
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


class TestDocChunker(unittest.TestCase):
    def test_chunking_splits_long_text(self):
        chunker = DocChunker(chunk_size=10, overlap=2)
        long_text = "qazwsxedcrfvtgbyhnujmikolp"

        chunks = chunker.chunk_text(long_text)

        self.assertEqual(len(chunks), 3)
        self.assertEqual(chunks[0], "qazwsxedcr")
        self.assertEqual(chunks[1], "crfvtgbyhn")
        self.assertEqual(chunks[2], "hnujmikolp")
