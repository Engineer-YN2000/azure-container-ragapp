import os
import json
import sys
from typing import Dict, Any

from azure.core.credentials import AzureKeyCredential
from azure.search.documents.indexes import SearchIndexClient

from src.indexer.core.config import Settings
from src.indexer.clients import AzureSearchClient, AzureEmbeddingClient


def load_local_settings():
    """
    Mimics the Azure Functions runtime by loading settings from
    local.settings.json into the environment variables.
    """
    settings_path = os.path.join("src", "indexer", "local.settings.json")

    print(f"Attempting to load settings from: {settings_path}")

    if not os.path.exists(settings_path):
        print(f"❌ Critical Error: '{settings_path}' not found.")
        print(
            "   Please ensure you are running this script from the project root directory."
        )
        sys.exit(1)

    with open(settings_path, "r") as f:
        settings = json.load(f)

    # "Values"セクションのキーと値を環境変数に設定
    for key, value in settings.get("Values", {}).items():
        os.environ[key] = value

    print("✅ Settings loaded into environment variables.")


def test_azure_openai_connection(
    settings: Settings,
    embedding_client: AzureEmbeddingClient,
    search_client: AzureSearchClient,
):
    """Tests connection to Azure OpenAI Embedding model."""
    print("\n--- Testing Azure OpenAI Connection ---")
    try:
        _ = embedding_client.get_embedding("test")
        print(
            f"✅ Success: Correctly assembled endpoint '{settings.aoai_endpoint}' and got a response. Vector dimensions: {len(embedding_client.get_embedding('test'))}."
        )

    except Exception as e:
        print("❌ Failed: Could not connect to Azure OpenAI.")
        print(f"   Error: {e}")


def test_azure_search_connection(settings: Settings):
    """Tests connection to Azure AI Search."""
    print("\n--- Testing Azure AI Search Connection ---")
    try:
        credential = AzureKeyCredential(settings.search_service_api_key)
        search_index_client = SearchIndexClient(
            endpoint=settings.search_service_endpoint, credential=credential
        )
        stats: Dict[str, Any] = search_index_client.get_index_statistics(
            index_name=settings.search_service_index_name
        )  # type: ignore

        print(
            f"✅ Success: Correctly assembled endpoint '{settings.search_service_endpoint}' and connected to index '{settings.search_service_index_name}'."
        )
        print(f"Index currently has {stats['document_count']} documents.")

    except Exception as e:
        print("❌ Failed: Could not connect to Azure AI Search.")
        print(f"   Error: {e}")


if __name__ == "__main__":
    print("Running Azure Service Connectivity Test...")

    # 1. local.settings.jsonから環境変数をロード
    load_local_settings()

    # 2. ロードされた環境変数を使ってSettingsクラスを初期化
    try:
        app_settings = Settings()
        embedding_client = AzureEmbeddingClient(app_settings)
        search_client = AzureSearchClient(app_settings, embedding_client)
        print("✅ All clients initialized successfully.")
    except SystemExit:
        print(
            "\n❌ Critical Error: Settings class failed to initialize. Check if all required keys are in local.settings.json."
        )
        sys.exit(1)

    # 3. 接続テストを実行
    test_azure_openai_connection(app_settings, embedding_client, search_client)
    test_azure_search_connection(app_settings)
