from qdrant_client.models import (
    Distance,
    VectorParams,
)

from app.database.qdrant import (
    COLLECTION_NAME,
    VECTOR_SIZE,
    qdrant_client,
)


class QdrantService:

    @staticmethod
    def create_collection() -> None:

        collections = qdrant_client.get_collections()

        existing_names = {
            collection.name
            for collection in collections.collections
        }

        if COLLECTION_NAME in existing_names:
            print(
                f"Collection already exists: "
                f"{COLLECTION_NAME}"
            )
            return

        qdrant_client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(
                size=VECTOR_SIZE,
                distance=Distance.COSINE,
            ),
        )

        print(
            f"Created collection: "
            f"{COLLECTION_NAME}"
        )

    @staticmethod
    def collection_exists() -> bool:

        collections = qdrant_client.get_collections()

        return COLLECTION_NAME in {
            collection.name
            for collection in collections.collections
        }

    @staticmethod
    def get_collection_info():

        return qdrant_client.get_collection(
            collection_name=COLLECTION_NAME,
        )