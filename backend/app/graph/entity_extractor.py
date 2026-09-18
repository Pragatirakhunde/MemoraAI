import re

from app.graph.entities import ExtractedEntity


class EntityExtractor:

    TECHNOLOGIES = {
        "python",
        "fastapi",
        "flask",
        "react",
        "typescript",
        "javascript",
        "java",
        "c++",
        "docker",
        "kubernetes",
        "redis",
        "git",
        "github",
        "neo4j",
        "qdrant",
        "nginx",
        "celery",
    }

    DATABASES = {
        "postgresql",
        "mysql",
        "mongodb",
        "sqlite",
        "oracle",
        "sql server",
        "neo4j",
        "qdrant",
    }

    IGNORED_HEADINGS = {
        "projects",
        "project",
        "technology",
        "technologies",
        "architecture",
        "engineering",
        "overview",
        "introduction",
        "documentation",
        "backend",
        "frontend",
        "database",
        "databases",
        "features",
        "requirements",
    }

    def extract(
        self,
        text: str,
        document_title: str,
        file_path: str,
    ) -> list[ExtractedEntity]:

        entities = []

        entities.extend(
            self._extract_technologies(text)
        )

        entities.extend(
            self._extract_databases(text)
        )

        entities.extend(
            self._extract_projects(text)
        )

        entities.extend(
            self._extract_modules(text)
        )

        entities.extend(
            self._extract_apis(text)
        )

        return self._deduplicate(entities)

    def _extract_technologies(
        self,
        text: str,
    ) -> list[ExtractedEntity]:

        entities = []

        for technology in self.TECHNOLOGIES:

            if technology in self.DATABASES:
                continue

            pattern = re.compile(
                rf"(?<!\w)"
                rf"{re.escape(technology)}"
                rf"(?!\w)",
                re.IGNORECASE,
            )

            match = pattern.search(text)

            if match:
                entities.append(
                    ExtractedEntity(
                        name=technology,
                        entity_type="TECHNOLOGY",
                        confidence=0.95,
                        source_text=match.group(0),
                    )
                )

        return entities

    def _extract_databases(
        self,
        text: str,
    ) -> list[ExtractedEntity]:

        entities = []

        for database in self.DATABASES:

            pattern = re.compile(
                rf"(?<!\w)"
                rf"{re.escape(database)}"
                rf"(?!\w)",
                re.IGNORECASE,
            )

            match = pattern.search(text)

            if match:
                entities.append(
                    ExtractedEntity(
                        name=database,
                        entity_type="DATABASE",
                        confidence=0.98,
                        source_text=match.group(0),
                    )
                )

        return entities

    def _extract_projects(
        self,
        text: str,
    ) -> list[ExtractedEntity]:

        entities = []

        lines = text.splitlines()

        inside_project_section = False

        for line in lines:

            stripped = line.strip()

            # Detect a Projects section
            heading_match = re.match(
                r"^#{1,6}\s+(.+)$",
                stripped,
            )

            if heading_match:

                heading = (
                    heading_match.group(1)
                    .strip()
                    .lower()
                )

                if heading in {
                    "projects",
                    "project",
                }:
                    inside_project_section = True
                    continue

                # Stop when the next heading starts
                if inside_project_section:
                    inside_project_section = False

            # Extract bullet-style project names
            if inside_project_section:

                bullet_match = re.match(
                    r"^[-*]\s+(.+)$",
                    stripped,
                )

                if bullet_match:

                    name = (
                        bullet_match.group(1)
                        .strip()
                    )

                    if (
                        len(name) >= 3
                        and name.lower()
                        not in self.IGNORED_HEADINGS
                    ):
                        entities.append(
                            ExtractedEntity(
                                name=name,
                                entity_type="PROJECT",
                                confidence=0.95,
                                source_text=name,
                            )
                        )

        # Explicit "X project" patterns
        explicit_pattern = re.compile(
            r"\b([A-Z][A-Za-z0-9 &-]{2,60})"
            r"\s+project\b",
            re.IGNORECASE,
        )

        for match in explicit_pattern.finditer(text):

            name = match.group(1).strip()

            if (
                name.lower()
                not in self.IGNORED_HEADINGS
            ):
                entities.append(
                    ExtractedEntity(
                        name=name,
                        entity_type="PROJECT",
                        confidence=0.90,
                        source_text=name,
                    )
                )

        return entities

    def _extract_modules(
        self,
        text: str,
    ) -> list[ExtractedEntity]:

        entities = []

        pattern = re.compile(
            r"\b([A-Z][A-Za-z0-9 &-]{2,50})"
            r"\s+(?:module|service)\b",
            re.IGNORECASE,
        )

        for match in pattern.finditer(text):

            name = match.group(1).strip()

            if (
                name.lower()
                not in self.IGNORED_HEADINGS
            ):
                entities.append(
                    ExtractedEntity(
                        name=name,
                        entity_type="MODULE",
                        confidence=0.80,
                        source_text=match.group(0),
                    )
                )

        return entities

    def _extract_apis(
        self,
        text: str,
    ) -> list[ExtractedEntity]:

        entities = []

        paths = re.findall(
            r"(?<!\w)(/api/[A-Za-z0-9_./{}-]+)",
            text,
        )

        for path in paths:
            entities.append(
                ExtractedEntity(
                    name=path,
                    entity_type="API",
                    confidence=0.98,
                    source_text=path,
                )
            )

        api_names = re.findall(
            r"\b([A-Z][A-Za-z0-9 &-]{2,50})\s+API\b",
            text,
            flags=re.IGNORECASE,
        )

        for api_name in api_names:

            name = api_name.strip()

            entities.append(
                ExtractedEntity(
                    name=name,
                    entity_type="API",
                    confidence=0.85,
                    source_text=f"{name} API",
                )
            )

        return entities

    @staticmethod
    def _deduplicate(
        entities: list[ExtractedEntity],
    ) -> list[ExtractedEntity]:

        unique = {}

        for entity in entities:

            key = (
                entity.entity_type,
                entity.name.lower().strip(),
            )

            if key not in unique:
                unique[key] = entity

        return list(unique.values())