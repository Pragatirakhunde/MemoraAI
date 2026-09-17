from qdrant_client.models import PointStruct

from app.database.qdrant import (
    COLLECTION_NAME,
    qdrant_client,
)
from app.embeddings.payload import build_chunk_payload
from app.embeddings.service import EmbeddingService
from app.models.document import Document
from app.models.document_chunk import DocumentChunk


class VectorService:

    def __init__(self):
        self.embedding_service = EmbeddingService()

    def upsert_chunk(
        self,
        document: Document,
        chunk: DocumentChunk,
    ) -> None:

        vector = self.embedding_service.embed_text(
            chunk.content
        )

        payload = build_chunk_payload(
            document=document,
            chunk=chunk,
        )

        point = PointStruct(
            id=chunk.id,
            vector=vector,
            payload=payload,
        )

        qdrant_client.upsert(
            collection_name=COLLECTION_NAME,
            points=[point],
        )

    def upsert_chunks(
        self,
        document: Document,
        chunks: list[DocumentChunk],
    ) -> None:

        if not chunks:
            return

        texts = [
            chunk.content
            for chunk in chunks
        ]

        vectors = self.embedding_service.embed_texts(
            texts
        )

        points = []

        for chunk, vector in zip(
            chunks,
            vectors,
        ):

            payload = build_chunk_payload(
                document=document,
                chunk=chunk,
            )

            points.append(
                PointStruct(
                    id=chunk.id,
                    vector=vector,
                    payload=payload,
                )
            )

        qdrant_client.upsert(
            collection_name=COLLECTION_NAME,
            points=points,
        )

    def delete_document_chunks(
        self,
        chunk_ids: list[int],
    ) -> None:

        if not chunk_ids:
            return

        qdrant_client.delete(
            collection_name=COLLECTION_NAME,
            points_selector=chunk_ids,
        )
        