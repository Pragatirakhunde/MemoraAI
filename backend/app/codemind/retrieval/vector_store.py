from qdrant_client.models import Distance, FieldCondition, Filter, MatchValue, PointIdsList, PointStruct, VectorParams

from app.core.config import settings
from app.database.qdrant import qdrant_client, VECTOR_SIZE
from app.embeddings.service import EmbeddingService


class CodeVectorStore:
    collection = settings.CODEMIND_QDRANT_COLLECTION

    def __init__(self):
        self.embedder = EmbeddingService()

    def ensure_collection(self) -> None:
        existing = {c.name for c in qdrant_client.get_collections().collections}
        if self.collection not in existing:
            qdrant_client.create_collection(
                collection_name=self.collection,
                vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
            )

    def upsert_many(self, rows: list[tuple[int, str, dict]]) -> None:
        if not rows:
            return
        self.ensure_collection()
        vectors = self.embedder.embed_texts([content for _, content, _ in rows])
        qdrant_client.upsert(
            collection_name=self.collection,
            points=[
                PointStruct(id=chunk_id, vector=vector, payload=payload)
                for (chunk_id, _, payload), vector in zip(rows, vectors)
            ],
        )

    def delete_ids(self, ids: list[int]) -> None:
        if ids:
            self.ensure_collection()
            qdrant_client.delete(
                collection_name=self.collection,
                points_selector=PointIdsList(points=ids),
            )

    def search(self, query: str, organization_id: int, project_id: int, limit: int = 8) -> list[dict]:
        self.ensure_collection()
        vector = self.embedder.embed_text(query)
        response = qdrant_client.query_points(
            collection_name=self.collection,
            query=vector,
            query_filter=Filter(must=[
                FieldCondition(key="organization_id", match=MatchValue(value=organization_id)),
                FieldCondition(key="project_id", match=MatchValue(value=project_id)),
            ]),
            limit=limit,
            with_payload=True,
        )
        return [{"score": item.score, **(item.payload or {})} for item in response.points]
