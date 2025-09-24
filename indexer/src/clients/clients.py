from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from openai import AzureOpenAI
from core.config import Settings
from typing import List, Dict, Any

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
        response = self.client.embeddings.create(
            input=text,
            model=self.embedding_model
        )
        return response.data[0].embedding
    
class AzureSearchClient:
    def __init__(self, settings: Settings):
        self.client = SearchClient(
            endpoint=settings.search_service_endpoint,
            index_name=settings.search_service_index_name,
            credential=AzureKeyCredential(settings.search_service_api_key),
            http_client=settings.global_http_client,
        )
        self.embedding_client = AzureEmbeddingClient(settings)
    
    def index_chunks(self, chunks: list[str]):
        """Index a list of text chunks into Azure AI Search."""
        documents: List[Dict[str, Any]] = []
        
        for i, chunk in enumerate(chunks):
            embedding = self.embedding_client.get_embedding(chunk)
            document: Dict[str, Any] = {"id": str(i), "content": chunk, "contentVector": embedding}
            documents.append(document)
            
        self.client.upload_documents(documents) # type: ignore