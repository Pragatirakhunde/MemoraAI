from qdrant_client import QdrantClient

from app.core.config import settings

if settings.QDRANT_URL:
    qdrant_client = QdrantClient(
        url=settings.QDRANT_URL,
        api_key=settings.QDRANT_API_KEY or None,
    )
else:
    qdrant_client = QdrantClient(
        host=settings.QDRANT_HOST,
        port=settings.QDRANT_PORT,
    )

COLLECTION_NAME = "enterprise_memory_chunks"
VECTOR_SIZE = 1024
