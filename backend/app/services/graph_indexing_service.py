from sqlalchemy.orm import Session

from app.graph.entity_extractor import EntityExtractor
from app.graph.relationship_extractor import (
    RelationshipExtractor,
)
from app.graph.indexer import GraphIndexer
from app.models.organization import Organization
from app.models.document import Document
from app.processors.cleaners.text_cleaner import (
    TextCleaner,
)
from app.processors.parsers.factory import parse_document


class GraphIndexingService:

    @staticmethod
    def index_document(
        db: Session,
        document: Document,
    ) -> None:

        organization = db.get(
            Organization,
            document.organization_id,
        )

        if organization is None:
            raise ValueError(
                "Organization not found"
            )

        raw_text = parse_document(
            document
        )

        cleaned_text = TextCleaner.clean(
            raw_text
        )

        entity_extractor = EntityExtractor()

        entities = entity_extractor.extract(
            text=cleaned_text,
            document_title=document.title,
            file_path=document.file_path,
        )

        relationship_extractor = (
            RelationshipExtractor()
        )

        relationships = (
            relationship_extractor.extract(
                text=cleaned_text,
                entities=entities,
            )
        )

        GraphIndexer.index_document(
            document=document,
            organization=organization,
            entities=entities,
            relationships=relationships,
        )

        print(
            f"Graph indexed: {document.title}"
        )

        print(
            f"Entities: {len(entities)}"
        )

        print(
            f"Relationships: "
            f"{len(relationships)}"
        )