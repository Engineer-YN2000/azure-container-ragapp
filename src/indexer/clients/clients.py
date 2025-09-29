from typing import List, Dict, Any
import logging

from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from openai import AzureOpenAI

from core.config import Settings

logger = logging.getLogger(__name__)


class AzureEmbeddingClient:
    def __init__(self, settings: Settings):
        self.client = AzureOpenAI(
            azure_endpoint=settings.aoai_endpoint,
            api_key=settings.aoai_api_key,
            api_version=settings.aoai_api_version,
            http_client=settings.global_http_client,
        )
        self.embedding_model = settings.aoai_embedding_model_name

    def get_embedding(self, text: str) -> list[float]:
        """Get embedding vector for the given text."""
        logger.info(f"Requesting embedding for text (first 30 chars): '{text[:30]}...'")
        response = self.client.embeddings.create(input=text, model=self.embedding_model)
        logger.debug("Embedding received successfully.")
        return response.data[0].embedding


class AzureSearchClient:
    def __init__(self, settings: Settings, embedding_client: AzureEmbeddingClient):
        self.client = SearchClient(
            endpoint=settings.search_service_endpoint,
            index_name=settings.search_service_index_name,
            credential=AzureKeyCredential(settings.search_service_api_key),
            http_client=settings.global_http_client,
        )
        self.embedding_client = embedding_client

    def index_chunks(self, chunks: list[str]):
        """Index a list of text chunks into Azure AI Search."""
        documents: List[Dict[str, Any]] = []

        for i, chunk in enumerate(chunks):
            embedding = self.embedding_client.get_embedding(chunk)
            document: Dict[str, Any] = {
                "id": str(i),
                "content": chunk,
                "contentVector": embedding,
            }
            documents.append(document)

        logger.info(f"Uploading {len(documents)} documents to Azure AI Search.")
        self.client.upload_documents(documents)  # type: ignore
        logger.info("Successfully uploded documents.")

        try:
            # upload_documentsは結果のリストを返す
            results = self.client.upload_documents(documents)  # type: ignore

            # 各ドキュメントの結果をチェック
            successful_uploads = 0
            for result in results:
                if result.succeeded:
                    successful_uploads += 1
                else:
                    # 失敗したドキュメントのキーとエラーをログに出力
                    logger.error(
                        f"Failed to index document with key {result.key}. "
                        f"Error: {result.error_message}, Status Code: {result.status_code}"
                    )

            if successful_uploads == len(documents):
                logger.info("Successfully uploaded all documents.")
            else:
                logger.warning(
                    f"Successfully uploaded {successful_uploads} out of {len(documents)} documents."
                )

        except Exception as e:
            logger.error(
                f"An error occurred during document upload: {e}", exc_info=True
            )
            raise
