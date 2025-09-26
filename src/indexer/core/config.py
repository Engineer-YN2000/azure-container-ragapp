import os
import httpx
import logging

logger = logging.getLogger(__name__)


class Settings:
    """Mnages this application's settings."""

    def __init__(self):
        try:
            self.search_service_endpoint = (
                f"https://{os.environ['SEARCH_SERVICE_ENDPOINT']}.search.windows.net"
            )
            self.search_service_api_key = os.environ["SEARCH_SERVICE_API_KEY"]
            self.search_service_index_name = os.environ["SEARCH_SERVICE_INDEX_NAME"]

            self.aoai_endpoint = (
                f"https://{os.environ['AOAI_ENDPOINT']}.openai.azure.com/"
            )
            self.aoai_api_version = os.environ["AOAI_API_VERSION"]
            self.aoai_api_key = os.environ["AOAI_API_KEY"]
            self.aoai_embedding_model_name = os.environ["AOAI_EMBEDDING_MODEL_NAME"]
        except KeyError as e:
            logger.critical(f"Missing environment variable {e}", exc_info=True)
            raise e

        self.global_http_client = httpx.Client()
        self.async_http_client = httpx.AsyncClient()
