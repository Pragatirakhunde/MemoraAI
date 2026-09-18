from app.database.postgres import SessionLocal

from app.repositories.document_repository import (
    DocumentRepository,
)

from app.processors.parsers.factory import parse_document
from app.processors.cleaners.text_cleaner import (
    TextCleaner,
)

from app.graph.entity_extractor import (
    EntityExtractor,
)


db = SessionLocal()

try:

    documents = DocumentRepository.get_all(
        db,
        organization_id=1,
    )

    if not documents:
        print("No documents found.")
    else:

        document = documents[0]

        raw_text = parse_document(
            document
        )

        cleaned_text = TextCleaner.clean(
            raw_text
        )

        extractor = EntityExtractor()

        entities = extractor.extract(
            text=cleaned_text,
            document_title=document.title,
            file_path=document.file_path,
        )

        print(
            f"Document: {document.title}"
        )

        print("\nEntities:")

        for entity in entities:

            print(
                f"- {entity.entity_type}: "
                f"{entity.name} "
                f"(confidence="
                f"{entity.confidence})"
            )

finally:
    db.close()