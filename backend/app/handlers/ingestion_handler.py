# handlers/ingestion_handler.py

from fastapi import APIRouter, UploadFile, File, Form
from typing import List, Optional
from prepdocslib.blobmanager import BlobManager
from prepdocslib.searchmanager import SearchManager
from prepdocslib.fileprocessor import FileProcessor
from prepdocslib.embeddings import EmbeddingService
import tempfile
import os

router = APIRouter(prefix="/ingest", tags=["Ingestion"])

@router.post("/")
async def ingest_documents(
    files: List[UploadFile] = File(...),
    index_name: str = Form(...),
    connection_string: str = Form(...),
    container: str = Form(...),
    use_acls: Optional[bool] = Form(False),
    embedding_model: Optional[str] = Form("azureopenai:gpt-4"),
    schema_config: Optional[str] = Form(None),
    doc_type: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),  # comma-separated
    domain: Optional[str] = Form(None)
):
    """
    Ingest uploaded documents into Azure Cognitive Search with optional ACL tagging and domain metadata.
    """
    print(f"[INFO] Ingesting to index: {index_name}, ACLs: {use_acls}, doc_type: {doc_type}, domain: {domain}")

    with tempfile.TemporaryDirectory() as tmpdir:
        local_paths = []
        for f in files:
            dest_path = os.path.join(tmpdir, f.filename)
            with open(dest_path, "wb") as out_file:
                out_file.write(await f.read())
            local_paths.append(dest_path)

        # Upload to blob
        blob_manager = BlobManager(connection_string, container)
        uploaded_files = blob_manager.upload_documents(local_paths)

        # Process files into pages
        processor = FileProcessor(use_acls=use_acls)
        pages = processor.extract_pages(uploaded_files)

        # Apply domain metadata
        for page in pages:
            page.doc_type = doc_type
            page.tags = tags.split(",") if tags else []
            page.domain = domain

        # Embed content
        embedder = EmbeddingService(model=embedding_model)
        for page in pages:
            page.embedding = embedder.embed_text(page.content)

        # Index
        search = SearchManager(index_name=index_name)
        if schema_config:
            search.setup_index(schema_path=schema_config)
        search.index_documents(pages)

    return {"message": "Ingestion completed successfully.", "indexed_count": len(pages)}
