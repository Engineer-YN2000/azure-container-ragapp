import azure.functions as func
import logging
import tempfile
import os

from .clients import AzureSearchClient
from .func import chunk_text, extract_text_from_file
from .core.config import Settings

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)


@app.route(route="indexer")
def indexer(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Python HTTP trigger function processed a request.")

    try:
        settings = Settings()

        # 1. Get file from request
        file = req.files.get("file")
        if not file:
            return func.HttpResponse("Please provide a file to index.", status_code=400)

        file_bytes = file.read()
        file_name = file.filename
        if not file_name:
            return func.HttpResponse(
                "File name could not be determined.", status_code=400
            )

        logging.info(f"Received file: {file_name}. Creating temporary file.")

        # 2. Extract text from file
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_file_path = os.path.join(temp_dir, file_name)

            with open(temp_file_path, "wb") as f:
                f.write(file_bytes)

            logging.info(
                f"Temporary file created at {temp_file_path}. Extracting text."
            )

            text = extract_text_from_file(temp_file_path)

        if not text:
            logging.warning(f"No text could be extracted from {file_name}.")
            return func.HttpResponse(
                f"Could not extract text from '{file_name}'. This may be an unsupported file format or the file may be empty.",
                status_code=400,
            )

        # 3. Chunk text
        logging.info(f"Extracted text from {file_name}. Chunking text.")
        chunks = chunk_text(text)

        # 4. Index chunks to Azure Search
        logging.info(
            f"Chunking complete. Indexing {len(chunks)} chunks to Azure Search."
        )
        search_client = AzureSearchClient(settings)
        search_client.index_chunks(chunks)

        success_message = (
            f"Finished all processes for {file_name} and indexed {len(chunks)} chunks ."
        )
        logging.info(success_message)

        return func.HttpResponse(success_message, status_code=200)

    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}", exc_info=True)
        return func.HttpResponse("An unexpected error occurred.", status_code=500)
