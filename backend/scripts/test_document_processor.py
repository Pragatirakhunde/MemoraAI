from app.database.postgres import SessionLocal
from app.repositories.document_repository import (
    DocumentRepository,
)
from app.processors.document_processor import (
    DocumentProcessor,
)


db = SessionLocal()

try:
    documents = DocumentRepository.get_all(
        db,
        organization_id=1,
    )

    if not documents:
        print("No documents found for organization 1.")
    else:
        document = documents[0]

        print(
            f"Processing document: "
            f"{document.id} - {document.title}"
        )

        processor = DocumentProcessor()

        result = processor.process(document)

        print("\n--- Cleaned Text ---")
        print(result.cleaned_text)

        print("\n--- Metadata ---")
        print(result.metadata)

        print("\n--- Chunks ---")

        for index, chunk in enumerate(
            result.chunks,
            start=1,
        ):
            print(f"\nChunk {index}:")
            print(chunk)

finally:
    db.close()