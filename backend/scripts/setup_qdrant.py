from app.services.qdrant_service import QdrantService


QdrantService.create_collection()

print(
    "Collection exists:",
    QdrantService.collection_exists(),
)

info = QdrantService.get_collection_info()

print("Vector size:", info.config.params.vectors.size)
print("Distance:", info.config.params.vectors.distance)