import os

import streamlit as st
import requests


BACKEND_URL = os.environ.get("BACKEND_API_URL", "http://localhost:7071/api/indexer")

st.set_page_config(page_title="Document Indexer", layout="wide")
st.title("📄 Document Indexer for RAG Applications")
st.markdown("---")

st.subheader("Upload a file to be indexed")
uploaded_file = st.file_uploader("Choose a file", type=["pdf", "docx", "txt"])

if uploaded_file is not None:
    st.markdown("---")
    st.write("File Details:")
    st.json(
        {
            "File Name": uploaded_file.name,
            "File Size": f"{uploaded_file.size / 1024:.2f} KB",
            "File Type": uploaded_file.type,
        }
    )

    if st.button("Index This File", type="primary"):
        with st.spinner("Indexing the document..."):
            try:
                files_to_send = {
                    "file": (
                        uploaded_file.name,
                        uploaded_file.getvalue(),
                        uploaded_file.type,
                    )
                }

                response = requests.post(BACKEND_URL, files=files_to_send, timeout=300)

                if response.status_code == 200:
                    st.success("Successfully indexed the document!")
                    st.text_area("API Response", value=response.text, height=150)
                else:
                    st.error(f"Error from API(Status {response.status_code}):")
                    st.text_area("Error Details", value=response.text, height=150)

            except requests.exceptions.RequestException as e:
                st.error(f"Failed to connect to the backend API at {BACKEND_URL}")
                st.exception(e)
