from app.models.document import Document
from app.models.document_chunk import DocumentChunk


def build_chunk_payload(
    document: Document,
    chunk: DocumentChunk,
) -> dict:

    metadata = document.metadata_json or {}

    return {
        "document_id": document.id,
        "chunk_id": chunk.id,
        "organization_id": document.organization_id,
        "data_source_id": document.data_source_id,
        "source_file_id": document.source_file_id,
        "chunk_index": chunk.chunk_index,
        "title": document.title,
        "file_path": document.file_path,
        "extension": document.extension,
        "document_type": metadata.get(
            "document_type"
        ),
        "language": metadata.get(
            "language"
        ),
        "content": chunk.content,
    }