from sqlalchemy.orm import Session

from app.graph.entity_extractor import EntityExtractor
from app.retrieval.models import (
    GraphResult,
    HybridRetrievalResult,
    VectorResult,
)
from app.services.graph_query_service import (
    GraphQueryService,
)
from app.services.search_service import (
    SearchService,
)


class HybridRetrievalService:

    def __init__(self):
        self.search_service = SearchService()
        self.entity_extractor = EntityExtractor()

    def retrieve(
        self,
        db: Session,
        query: str,
        organization_id: int,
        limit: int = 5,
    ) -> HybridRetrievalResult:

        # ----------------------------------------
        # 1. VECTOR RETRIEVAL
        # ----------------------------------------

        vector_raw = self.search_service.search(
            db=db,
            query=query,
            organization_id=organization_id,
            limit=limit,
        )

        vector_results = [
            VectorResult(
                document_id=item["document_id"],
                chunk_id=item["chunk_id"],
                title=item["title"],
                content=item["content"],
                score=item["score"],
                file_path=item["reference"]["file_path"],
                reference=item["reference"],
            )
            for item in vector_raw
        ]

        # ----------------------------------------
        # 2. NORMAL ENTITY EXTRACTION
        # ----------------------------------------

        extracted_entities = (
            self.entity_extractor.extract(
                text=query,
                document_title="query",
                file_path="",
            )
        )

        # ----------------------------------------
        # 3. GRAPH ENTITY RESOLUTION
        # ----------------------------------------
        # Find entities that already exist in Neo4j
        # and appear in the user's question.

        resolved_entities = (
            GraphQueryService.resolve_entities_from_query(
                organization_id=organization_id,
                query_text=query,
            )
        )

        # ----------------------------------------
        # 4. MERGE ENTITY SOURCES
        # ----------------------------------------

        entity_map = {}

        for entity in extracted_entities:

            key = (
                entity.entity_type,
                entity.name.lower().strip(),
            )

            entity_map[key] = {
                "name": entity.name,
                "type": entity.entity_type,
                "confidence": entity.confidence,
            }

        for entity in resolved_entities:

            labels = entity.get(
                "labels",
                [],
            )

            entity_type = (
                labels[0]
                if labels
                else "UNKNOWN"
            )

            # Ignore generic infrastructure nodes.
            if entity_type == "Organization":
                continue

            key = (
                entity_type,
                entity["name"].lower().strip(),
            )

            if key not in entity_map:

                entity_map[key] = {
                    "name": entity["name"],
                    "type": entity_type,
                    "confidence": 0.95,
                }

        entity_data = list(
            entity_map.values()
        )

        # ----------------------------------------
        # 5. GRAPH EXPANSION
        # ----------------------------------------

        graph_results = []

        for entity in entity_data:

            expansion = (
                GraphQueryService.expand_entity(
                    organization_id=organization_id,
                    entity_name=entity["name"],
                    max_hops=2,
                    limit=10,
                )
            )

            for item in expansion:

                source_type = item.get(
                    "source_type",
                    [],
                )

                target_type = item.get(
                    "target_type",
                    [],
                )

                source_type_name = (
                    source_type[0]
                    if source_type
                    else "UNKNOWN"
                )

                hops = item.get(
                    "hops",
                    1,
                )

                hop_confidence = (
                    0.90
                    if hops == 1
                    else 0.70
                )

                graph_results.append(
                    GraphResult(
                        entity_name=item.get(
                            "source_name",
                            entity["name"],
                        ),
                        entity_type=source_type_name,
                        relationship=" -> ".join(
                            item.get(
                                "path_relationships",
                                [],
                            )
                        ),
                        related_name=item.get(
                            "target_name"
                        ),
                        related_type=target_type,
                        hops=hops,
                        confidence=(
                            entity["confidence"]
                            * hop_confidence
                        ),
                    )
                )

        # ----------------------------------------
        # 6. PROJECT-SPECIFIC GRAPH CONTEXT
        # ----------------------------------------

        for entity in entity_data:

            if entity["type"] != "Project":
                continue

            context = (
                GraphQueryService
                .get_project_knowledge(
                    organization_id=organization_id,
                    project_name=entity["name"],
                )
            )

            for technology in context.get(
                "technologies",
                [],
            ):

                name = technology.get("name")

                if not name:
                    continue

                graph_results.append(
                    GraphResult(
                        entity_name=entity["name"],
                        entity_type="Project",
                        relationship="USES",
                        related_name=name,
                        related_type=[
                            "Technology"
                        ],
                        hops=1,
                        confidence=entity["confidence"],
                    )
                )

            for database in context.get(
                "databases",
                [],
            ):

                name = database.get("name")

                if not name:
                    continue

                graph_results.append(
                    GraphResult(
                        entity_name=entity["name"],
                        entity_type="Project",
                        relationship="USES_DATABASE",
                        related_name=name,
                        related_type=[
                            "Database"
                        ],
                        hops=1,
                        confidence=entity["confidence"],
                    )
                )

            for module in context.get(
                "modules",
                [],
            ):

                name = module.get("name")

                if not name:
                    continue

                graph_results.append(
                    GraphResult(
                        entity_name=entity["name"],
                        entity_type="Project",
                        relationship="HAS_MODULE",
                        related_name=name,
                        related_type=[
                            "Module"
                        ],
                        hops=1,
                        confidence=entity["confidence"],
                    )
                )

        # ----------------------------------------
        # 7. DEDUPLICATE GRAPH RESULTS
        # ----------------------------------------

        unique_graph_results = []
        seen_graph = set()

        for result in graph_results:

            key = (
                result.entity_name.lower(),
                result.relationship,
                (
                    result.related_name.lower()
                    if result.related_name
                    else None
                ),
            )

            if key in seen_graph:
                continue

            seen_graph.add(key)
            unique_graph_results.append(
                result
            )

        # ----------------------------------------
        # 8. RETURN HYBRID RESULT
        # ----------------------------------------

        return HybridRetrievalResult(
            query=query,
            vector_results=vector_results,
            graph_results=unique_graph_results,
            entities=entity_data,
        )

    def retrieve_fused_context(
        self,
        db: Session,
        query: str,
        organization_id: int,
        limit: int = 5,
        max_context_items: int = 10,
    ):

        from app.services.context_fusion_service import (
            ContextFusionService,
        )

        retrieval = self.retrieve(
            db=db,
            query=query,
            organization_id=organization_id,
            limit=limit,
        )

        return ContextFusionService.fuse(
            retrieval=retrieval,
            max_items=max_context_items,
        )