from qdrant_client.models import (
    FieldCondition,
    Filter,
    MatchValue,
)
from sqlalchemy.orm import Session

from app.database.qdrant import (
    COLLECTION_NAME,
    qdrant_client,
)
from app.embeddings.service import EmbeddingService
from app.repositories.document_repository import (
    DocumentRepository,
)


class SearchService:

    def __init__(self):
        self.embedding_service = EmbeddingService()

    def search(
        self,
        db: Session,
        query: str,
        organization_id: int,
        limit: int = 5,
        document_type: str | None = None,
        language: str | None = None,
        data_source_id: int | None = None,
        extension: str | None = None,
    ) -> list[dict]:

        query_vector = (
            self.embedding_service.embed_text(
                query
            )
        )

        conditions = [
            FieldCondition(
                key="organization_id",
                match=MatchValue(
                    value=organization_id
                ),
            )
        ]

        if document_type:
            conditions.append(
                FieldCondition(
                    key="document_type",
                    match=MatchValue(
                        value=document_type
                    ),
                )
            )

        if language:
            conditions.append(
                FieldCondition(
                    key="language",
                    match=MatchValue(
                        value=language
                    ),
                )
            )

        if data_source_id is not None:
            conditions.append(
                FieldCondition(
                    key="data_source_id",
                    match=MatchValue(
                        value=data_source_id
                    ),
                )
            )

        if extension:
            conditions.append(
                FieldCondition(
                    key="extension",
                    match=MatchValue(
                        value=extension
                    ),
                )
            )

        query_filter = Filter(
            must=conditions
        )

        response = qdrant_client.query_points(
            collection_name=COLLECTION_NAME,
            query=query_vector,
            query_filter=query_filter,
            limit=limit,
            with_payload=True,
        )

        qdrant_results = response.points

        document_ids = []

        for result in qdrant_results:

            document_id = result.payload.get(
                "document_id"
            )

            if document_id is not None:
                document_ids.append(
                    document_id
                )

        documents = (
            DocumentRepository.get_by_ids(
                db=db,
                document_ids=document_ids,
                organization_id=organization_id,
            )
        )

        enriched_results = []

        for result in qdrant_results:

            payload = result.payload

            document_id = payload.get(
                "document_id"
            )

            chunk_id = payload.get(
                "chunk_id"
            )

            document = documents.get(
                document_id
            )

            # Ignore stale Qdrant references.
            if document is None:
                continue

            enriched_results.append(
                {
                    "score": result.score,
                    "document_id": document.id,
                    "chunk_id": chunk_id,
                    "title": document.title,
                    "content": payload.get(
                        "content",
                        "",
                    ),
                    "reference": {
                        "document_id": document.id,
                        "chunk_id": chunk_id,
                        "title": document.title,
                        "file_path": document.file_path,
                        "extension": document.extension,
                        "document_type": (
                            payload.get(
                                "document_type"
                            )
                        ),
                        "language": (
                            payload.get(
                                "language"
                            )
                        ),
                        "chunk_index": payload.get(
                            "chunk_index",
                            0,
                        ),
                        "score": result.score,
                    },
                }
            )

        return enriched_results