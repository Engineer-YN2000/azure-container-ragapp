import logging
import tempfile
import os

import azure.functions as func

from clients import AzureSearchClient, AzureEmbeddingClient
from func import chunk_text, extract_text_from_file
from core.config import Settings
from utilities.utils import save_chunks_to_file

logger = logging.getLogger(__name__)

if os.environ.get("ENVIRONMENT") == "test":
    search_client = None
    logger.info("Running in TEST environment. Dependencies will be mocked.")
else:
    try:
        settings = Settings()
        embedding_client = AzureEmbeddingClient(settings)
        search_client = AzureSearchClient(settings, embedding_client)
        logger.info("Clients initialized successfully.")
    except Exception as e:
        logger.critical(f"Fatal error during client initialization: {e}", exc_info=True)
        search_client = None

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)


@app.route(route="indexer")
def indexer(req: func.HttpRequest) -> func.HttpResponse:
    logger.info("Python HTTP trigger function processed a request.")

    if not search_client:
        logger.error("Search client is not initialized due to a startup error.")
        return func.HttpResponse(
            "Internal Server Error: Service is not available.", status_code=500
        )

    try:
        # 1. Get file from request
        file = req.files.get("file")
        if not file:
            return func.HttpResponse("Please provide a file to index.", status_code=400)

        file_bytes: bytes = file.read()
        file_name = file.filename
        if not file_name:
            return func.HttpResponse(
                "File name could not be determined.", status_code=400
            )

        logger.info(f"Received file: {file_name}. Creating temporary file.")

        # 2. Extract text from file
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_file_path = os.path.join(temp_dir, file_name)

            with open(temp_file_path, "wb") as f:
                f.write(file_bytes)

            logger.info(f"Temporary file created at {temp_file_path}. Extracting text.")

            text = extract_text_from_file(temp_file_path)

        if not text:
            logger.warning(f"No text could be extracted from {file_name}.")
            return func.HttpResponse(
                f"Could not extract text from '{file_name}'. This may be an unsupported file format or the file may be empty.",
                status_code=400,
            )

        # 3. Chunk text
        logger.info(f"Extracted text from {file_name}. Chunking text.")
        chunks = chunk_text(text)

        save_chunks_to_file(chunks, file_name)

        # 4. Index chunks to Azure Search
        if settings.PERFORM_INDEXING.lower() != "false":
            logger.info(
                f"Chunking complete. Indexing {len(chunks)} chunks to Azure Search."
            )

            search_client.index_chunks(chunks)

            success_message = f"Finished all processes for {file_name} and indexed {len(chunks)} chunks ."
            logger.info(success_message)
        else:
            success_message = f"DRY RUN: Finished all processes for {file_name}. Indexing was skipped."
            logger.info(success_message)

        return func.HttpResponse(success_message, status_code=200)

    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}", exc_info=True)
        return func.HttpResponse("An unexpected error occurred.", status_code=500)
