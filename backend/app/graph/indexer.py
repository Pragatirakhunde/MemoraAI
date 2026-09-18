import re

from app.database.neo4j import driver
from app.graph.entities import ExtractedEntity
from app.graph.relationships import ExtractedRelationship
from app.models.document import Document
from app.models.organization import Organization


class GraphIndexer:

    RELATIONSHIP_TYPES = {
        "USES": "USES",
        "USES_DATABASE": "USES_DATABASE",
        "HAS_MODULE": "HAS_MODULE",
        "CALLS": "CALLS",
    }

    @staticmethod
    def _slug(value: str) -> str:
        value = value.lower().strip()
        value = re.sub(r"[^a-z0-9]+", "-", value)
        return value.strip("-")

    @staticmethod
    def _entity_key(
        organization_id: int,
        name: str,
    ) -> str:
        return f"{organization_id}:{GraphIndexer._slug(name)}"

    @staticmethod
    def create_organization(
        organization: Organization,
    ) -> None:

        query = """
        MERGE (o:Organization {id: $id})
        SET
            o.name = $name,
            o.slug = $slug
        """

        with driver.session() as session:
            session.run(
                query,
                id=organization.id,
                name=organization.name,
                slug=organization.slug,
            )

    @staticmethod
    def create_document(
        document: Document,
    ) -> None:

        query = """
        MERGE (d:Document {id: $id})
        SET
            d.title = $title,
            d.file_path = $file_path,
            d.extension = $extension,
            d.checksum = $checksum,
            d.organization_id = $organization_id
        """

        with driver.session() as session:
            session.run(
                query,
                id=document.id,
                title=document.title,
                file_path=document.file_path,
                extension=document.extension,
                checksum=document.checksum,
                organization_id=document.organization_id,
            )

    @staticmethod
    def link_document_to_organization(
        document: Document,
    ) -> None:

        query = """
        MATCH (d:Document {id: $document_id})
        MATCH (o:Organization {id: $organization_id})
        MERGE (o)-[:HAS_DOCUMENT]->(d)
        """

        with driver.session() as session:
            session.run(
                query,
                document_id=document.id,
                organization_id=document.organization_id,
            )

    @staticmethod
    def create_entity(
        entity: ExtractedEntity,
        organization_id: int,
    ) -> None:

        name = entity.name.strip()
        key = GraphIndexer._entity_key(
            organization_id,
            name,
        )

        if entity.entity_type == "PROJECT":

            query = """
            MERGE (n:Project {key: $key})
            SET
                n.name = $name,
                n.organization_id = $organization_id,
                n.confidence = $confidence
            """

        elif entity.entity_type == "MODULE":

            query = """
            MERGE (n:Module {key: $key})
            SET
                n.name = $name,
                n.organization_id = $organization_id,
                n.confidence = $confidence
            """

        elif entity.entity_type == "API":

            query = """
            MERGE (n:API {key: $key})
            SET
                n.name = $name,
                n.organization_id = $organization_id,
                n.confidence = $confidence
            """

        elif entity.entity_type == "TECHNOLOGY":

            query = """
            MERGE (
                n:Technology {
                    organization_id: $organization_id,
                    name: $name
                }
            )
            SET
                n.confidence = $confidence
            """

        elif entity.entity_type == "DATABASE":

            query = """
            MERGE (
                n:Database {
                    organization_id: $organization_id,
                    name: $name
                }
            )
            SET
                n.confidence = $confidence
            """

        else:
            return

        with driver.session() as session:
            session.run(
                query,
                key=key,
                name=name,
                organization_id=organization_id,
                confidence=entity.confidence,
            )

    @staticmethod
    def link_document_to_entity(
        document: Document,
        entity: ExtractedEntity,
    ) -> None:

        if entity.entity_type == "PROJECT":

            query = """
            MATCH (d:Document {id: $document_id})
            MATCH (
                n:Project {
                    key: $key
                }
            )
            MERGE (d)-[:DOCUMENTS]->(n)
            """

        elif entity.entity_type == "MODULE":

            query = """
            MATCH (d:Document {id: $document_id})
            MATCH (
                n:Module {
                    key: $key
                }
            )
            MERGE (d)-[:DOCUMENTS]->(n)
            """

        elif entity.entity_type == "TECHNOLOGY":

            query = """
            MATCH (d:Document {id: $document_id})
            MATCH (
                n:Technology {
                    organization_id: $organization_id,
                    name: $name
                }
            )
            MERGE (d)-[:MENTIONS]->(n)
            """

        elif entity.entity_type == "DATABASE":

            query = """
            MATCH (d:Document {id: $document_id})
            MATCH (
                n:Database {
                    organization_id: $organization_id,
                    name: $name
                }
            )
            MERGE (d)-[:MENTIONS]->(n)
            """

        elif entity.entity_type == "API":

            query = """
            MATCH (d:Document {id: $document_id})
            MATCH (
                n:API {
                    key: $key
                }
            )
            MERGE (d)-[:MENTIONS]->(n)
            """

        else:
            return

        with driver.session() as session:
            session.run(
                query,
                document_id=document.id,
                organization_id=document.organization_id,
                key=GraphIndexer._entity_key(
                    document.organization_id,
                    entity.name,
                ),
                name=entity.name.strip(),
            )

    @staticmethod
    def create_relationship(
        relationship: ExtractedRelationship,
        organization_id: int,
        source_document_id: int,
    ) -> None:

        relationship_type = (
            GraphIndexer.RELATIONSHIP_TYPES.get(
                relationship.relationship_type
            )
        )

        if relationship_type is None:
            return

        source_key = GraphIndexer._entity_key(
            organization_id,
            relationship.source_name,
        )

        target_key = GraphIndexer._entity_key(
            organization_id,
            relationship.target_name,
        )

        if relationship.source_type == "PROJECT":
            source_match = "(source:Project {key: $source_key})"
        elif relationship.source_type == "MODULE":
            source_match = "(source:Module {key: $source_key})"
        else:
            return

        if relationship.target_type == "TECHNOLOGY":
            target_match = (
                "(target:Technology "
                "{organization_id: $organization_id, "
                "name: $target_name})"
            )

        elif relationship.target_type == "DATABASE":
            target_match = (
                "(target:Database "
                "{organization_id: $organization_id, "
                "name: $target_name})"
            )

        elif relationship.target_type == "MODULE":
            target_match = (
                "(target:Module {key: $target_key})"
            )

        elif relationship.target_type == "API":
            target_match = (
                "(target:API {key: $target_key})"
            )

        else:
            return

        query = f"""
        MATCH {source_match}
        MATCH {target_match}

        MERGE (
            source
        )-[r:{relationship_type}]->(
            target
        )

        SET
            r.confidence = $confidence,
            r.source_document_id = $source_document_id
        """

        with driver.session() as session:
            session.run(
                query,
                source_key=source_key,
                target_key=target_key,
                target_name=relationship.target_name.strip(),
                organization_id=organization_id,
                confidence=relationship.confidence,
                source_document_id=source_document_id,
            )

    @staticmethod
    def remove_document_relationships(
        document_id: int,
    ) -> None:

        query = """
        MATCH ()-[r]->()
        WHERE r.source_document_id = $document_id
        DELETE r
        """

        with driver.session() as session:
            session.run(
                query,
                document_id=document_id,
            )

    @staticmethod
    def index_document(
        document: Document,
        organization: Organization,
        entities: list[ExtractedEntity],
        relationships: list[ExtractedRelationship],
    ) -> None:

        GraphIndexer.remove_document_relationships(
            document.id
        )

        GraphIndexer.create_organization(
            organization
        )

        GraphIndexer.create_document(
            document
        )

        GraphIndexer.link_document_to_organization(
            document
        )

        for entity in entities:

            GraphIndexer.create_entity(
                entity,
                document.organization_id,
            )

            GraphIndexer.link_document_to_entity(
                document,
                entity,
            )

        for relationship in relationships:

            GraphIndexer.create_relationship(
                relationship,
                document.organization_id,
                document.id,
            )