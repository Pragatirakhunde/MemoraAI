from app.database.qdrant import qdrant_client


collections = qdrant_client.get_collections()

print("Qdrant connected successfully")
print("Collections:")

for collection in collections.collections:
    print("-", collection.name)