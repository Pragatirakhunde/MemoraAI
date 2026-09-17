from app.database.postgres import SessionLocal
from app.database.qdrant import (
    COLLECTION_NAME,
    qdrant_client,
)
from app.repositories.document_chunk_repository import (
    DocumentChunkRepository,
)
from app.repositories.document_repository import (
    DocumentRepository,
)
from app.services.search_service import SearchService


db = SessionLocal()

try:
    print("=" * 60)
    print("PHASE 6 VALIDATION")
    print("=" * 60)

    # ----------------------------------------
    # 1. Check documents
    # ----------------------------------------

    documents = DocumentRepository.get_all(
        db,
        organization_id=1,
    )

    print("\n1. Documents")

    if not documents:
        raise RuntimeError(
            "No documents found."
        )

    print(
        "Documents found:",
        len(documents),
    )

    # ----------------------------------------
    # 2. Count chunks
    # ----------------------------------------

    total_chunks = 0

    for document in documents:

        chunks = (
            DocumentChunkRepository.get_by_document(
                db,
                document.id,
            )
        )

        total_chunks += len(chunks)

    print("\n2. PostgreSQL chunks")
    print(
        "Total chunks:",
        total_chunks,
    )

    if total_chunks == 0:
        raise RuntimeError(
            "No document chunks found."
        )

    # ----------------------------------------
    # 3. Check Qdrant
    # ----------------------------------------

    collection_info = (
        qdrant_client.get_collection(
            collection_name=COLLECTION_NAME
        )
    )

    qdrant_points = (
        collection_info.points_count
    )

    print("\n3. Qdrant")
    print(
        "Collection:",
        COLLECTION_NAME,
    )
    print(
        "Qdrant points:",
        qdrant_points,
    )

    if qdrant_points < total_chunks:
        raise RuntimeError(
            "Qdrant contains fewer points "
            "than PostgreSQL chunks."
        )

    # ----------------------------------------
    # 4. Semantic search
    # ----------------------------------------

    service = SearchService()

    query = (
        "Which database is used "
        "for the Inventory Management project?"
    )

    print("\n4. Semantic Search")
    print("Query:", query)

    results = service.search(
        db=db,
        query=query,
        organization_id=1,
        limit=5,
    )

    print(
        "Results returned:",
        len(results),
    )

    if not results:
        raise RuntimeError(
            "Semantic search returned no results."
        )

    first_result = results[0]

    print(
        "Top result:",
        first_result["title"],
    )

    print(
        "Score:",
        first_result["score"],
    )

    # ----------------------------------------
    # 5. Reference verification
    # ----------------------------------------

    print("\n5. Reference verification")

    reference = first_result.get(
        "reference"
    )

    required_fields = [
        "document_id",
        "chunk_id",
        "title",
        "file_path",
        "extension",
        "chunk_index",
        "score",
    ]

    for field in required_fields:

        if field not in reference:
            raise RuntimeError(
                f"Missing reference field: {field}"
            )

    print(
        "Reference verified successfully."
    )

    # ----------------------------------------
    # SUCCESS
    # ----------------------------------------

    print("\n" + "=" * 60)
    print("PHASE 6 VALIDATION SUCCESSFUL")
    print("=" * 60)

finally:
    db.close()