from sqlalchemy.orm import Session
from sqlalchemy import select
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
from app.models.project import Project


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

        if document.project_id is not None:

            project = db.get(
                Project,
                document.project_id,
            )

            if project is None:
                raise ValueError(
                    "Project not found"
                )

            GraphIndexer.create_project(
                project_id=project.id,
                organization_id=project.organization_id,
                name=project.name,
                slug=project.slug,
            )

            GraphIndexer.link_project_to_document(
                project_id=project.id,
                organization_id=project.organization_id,
                document_id=document.id,
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

    @staticmethod
    def index_all_documents(
        db: Session,
    ) -> int:

        documents = db.scalars(
            select(Document).order_by(Document.id)
        ).all()

        print(
            f"Starting Neo4j reindex for "
            f"{len(documents)} documents..."
        )

        for document in documents:
            print(
                f"Indexing document "
                f"{document.id}: {document.title}"
            )

            GraphIndexingService.index_document(
                db=db,
                document=document,
            )

        print(
            f"Neo4j reindex completed: "
            f"{len(documents)} documents"
        )

        return len(documents)