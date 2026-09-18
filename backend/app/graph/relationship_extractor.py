import re

from app.graph.entities import ExtractedEntity
from app.graph.relationships import ExtractedRelationship


class RelationshipExtractor:

    def extract(
        self,
        text: str,
        entities: list[ExtractedEntity],
    ) -> list[ExtractedRelationship]:

        relationships = []

        projects = [
            entity
            for entity in entities
            if entity.entity_type == "PROJECT"
        ]

        technologies = [
            entity
            for entity in entities
            if entity.entity_type == "TECHNOLOGY"
        ]

        databases = [
            entity
            for entity in entities
            if entity.entity_type == "DATABASE"
        ]

        modules = [
            entity
            for entity in entities
            if entity.entity_type == "MODULE"
        ]

        apis = [
            entity
            for entity in entities
            if entity.entity_type == "API"
        ]

        for project in projects:

            for technology in technologies:

                if self._related_in_same_context(
                    text,
                    project,
                    technology,
                ):
                    relationships.append(
                        ExtractedRelationship(
                            source_name=project.name,
                            source_type="PROJECT",
                            relationship_type="USES",
                            target_name=technology.name,
                            target_type="TECHNOLOGY",
                            confidence=0.80,
                            source_text=(
                                f"{project.name} "
                                f"uses "
                                f"{technology.name}"
                            ),
                        )
                    )

            for database in databases:

                if self._related_in_same_context(
                    text,
                    project,
                    database,
                ):
                    relationships.append(
                        ExtractedRelationship(
                            source_name=project.name,
                            source_type="PROJECT",
                            relationship_type="USES_DATABASE",
                            target_name=database.name,
                            target_type="DATABASE",
                            confidence=0.85,
                            source_text=(
                                f"{project.name} "
                                f"uses "
                                f"{database.name}"
                            ),
                        )
                    )

        for project in projects:

            for module in modules:

                if self._related_in_same_context(
                    text,
                    project,
                    module,
                ):
                    relationships.append(
                        ExtractedRelationship(
                            source_name=project.name,
                            source_type="PROJECT",
                            relationship_type="HAS_MODULE",
                            target_name=module.name,
                            target_type="MODULE",
                            confidence=0.75,
                            source_text=(
                                f"{project.name} "
                                f"has module "
                                f"{module.name}"
                            ),
                        )
                    )

        for module in modules:

            for api in apis:

                if self._related_in_same_context(
                    text,
                    module,
                    api,
                ):
                    relationships.append(
                        ExtractedRelationship(
                            source_name=module.name,
                            source_type="MODULE",
                            relationship_type="CALLS",
                            target_name=api.name,
                            target_type="API",
                            confidence=0.70,
                            source_text=(
                                f"{module.name} "
                                f"calls "
                                f"{api.name}"
                            ),
                        )
                    )

        return self._deduplicate(
            relationships
        )

    @staticmethod
    def _related_in_same_context(
        text: str,
        source: ExtractedEntity,
        target: ExtractedEntity,
    ) -> bool:

        source_match = re.search(
            re.escape(source.source_text),
            text,
            flags=re.IGNORECASE,
        )

        if not source_match:
            return False

        # Only inspect a local context window.
        start = max(
            0,
            source_match.start() - 150,
        )

        end = min(
            len(text),
            source_match.end() + 350,
        )

        context = text[start:end]

        return bool(
            re.search(
                re.escape(target.source_text),
                context,
                flags=re.IGNORECASE,
            )
        )

    @staticmethod
    def _deduplicate(
        relationships: list[ExtractedRelationship],
    ) -> list[ExtractedRelationship]:

        unique = {}

        for relationship in relationships:

            key = (
                relationship.source_type,
                relationship.source_name.lower(),
                relationship.relationship_type,
                relationship.target_type,
                relationship.target_name.lower(),
            )

            if key not in unique:
                unique[key] = relationship

        return list(unique.values())