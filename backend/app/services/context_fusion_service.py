from app.retrieval.context import FusedContextItem
from app.retrieval.models import HybridRetrievalResult


class ContextFusionService:

    @staticmethod
    def _vector_score(score: float) -> float:
        """
        Normalize vector similarity score
        to a stable 0..1 range.
        """
        return max(
            0.0,
            min(1.0, float(score)),
        )

    @staticmethod
    def _graph_score(
        confidence: float,
        hops: int,
    ) -> float:
        """
        Calculate graph evidence strength.

        Direct relationships are stronger than
        multi-hop relationships.
        """

        hop_factor = (
            1.0
            if hops == 1
            else 0.75
        )

        return max(
            0.0,
            min(
                1.0,
                confidence * hop_factor,
            ),
        )

    @staticmethod
    def fuse(
        retrieval: HybridRetrievalResult,
        max_items: int = 10,
    ) -> list[FusedContextItem]:

        vector_items: list[FusedContextItem] = []
        graph_items: list[FusedContextItem] = []

        # ==================================================
        # 1. VECTOR EVIDENCE
        # ==================================================

        seen_vector: set[tuple[int, int]] = set()

        for item in retrieval.vector_results:

            key = (
                item.document_id,
                item.chunk_id,
            )

            if key in seen_vector:
                continue

            seen_vector.add(key)

            vector_score = (
                ContextFusionService._vector_score(
                    item.score
                )
            )

            # Semantic relevance gets the main weight.
            # Small base value prevents vector evidence
            # from being completely suppressed by graph items.
            final_score = (
                0.70 * vector_score
                + 0.30
            )

            vector_items.append(
                FusedContextItem(
                    source_type="vector",
                    score=round(
                        final_score,
                        4,
                    ),
                    content=item.content,
                    reference={
                        **item.reference,
                        "source": "qdrant",
                        "retrieval_score": item.score,
                    },
                )
            )

        # ==================================================
        # 2. GRAPH EVIDENCE
        # ==================================================

        seen_graph: set[
            tuple[str, str | None, str | None]
        ] = set()

        for item in retrieval.graph_results:

            key = (
                item.entity_name.lower(),
                item.relationship,
                (
                    item.related_name.lower()
                    if item.related_name
                    else None
                ),
            )

            if key in seen_graph:
                continue

            seen_graph.add(key)

            graph_score = (
                ContextFusionService._graph_score(
                    confidence=item.confidence,
                    hops=item.hops,
                )
            )

            # Graph evidence gets its own scoring scale.
            final_score = (
                0.60 * graph_score
                + 0.20
            )

            graph_items.append(
                FusedContextItem(
                    source_type="graph",
                    score=round(
                        final_score,
                        4,
                    ),
                    content=(
                        f"{item.entity_name} "
                        f"-[:{item.relationship}]-> "
                        f"{item.related_name}"
                    ),
                    reference={
                        "source": "neo4j",
                        "entity": item.entity_name,
                        "entity_type": item.entity_type,
                        "relationship": item.relationship,
                        "related_entity": item.related_name,
                        "related_type": item.related_type,
                        "hops": item.hops,
                        "confidence": item.confidence,
                    },
                )
            )

        # ==================================================
        # 3. EMPTY RESULT HANDLING
        # ==================================================

        if not vector_items and not graph_items:
            return []

        # ==================================================
        # 4. ONLY VECTOR RESULTS
        # ==================================================

        if not graph_items:

            vector_items.sort(
                key=lambda item: item.score,
                reverse=True,
            )

            return vector_items[:max_items]

        # ==================================================
        # 5. ONLY GRAPH RESULTS
        # ==================================================

        if not vector_items:

            graph_items.sort(
                key=lambda item: item.score,
                reverse=True,
            )

            return graph_items[:max_items]

        # ==================================================
        # 6. HYBRID SOURCE-DIVERSITY SELECTION
        # ==================================================
        #
        # Always reserve space for both sources.
        #
        # Example for max_items = 10:
        #
        #   Vector → 6
        #   Graph  → 4
        #

        vector_limit = max(
            1,
            int(max_items * 0.60),
        )

        graph_limit = max_items - vector_limit

        vector_items.sort(
            key=lambda item: item.score,
            reverse=True,
        )

        graph_items.sort(
            key=lambda item: item.score,
            reverse=True,
        )

        selected_vectors = vector_items[
            :vector_limit
        ]

        selected_graph = graph_items[
            :graph_limit
        ]

        selected = (
            selected_vectors
            + selected_graph
        )

        # ==================================================
        # 7. FINAL RANKING
        # ==================================================

        selected.sort(
            key=lambda item: item.score,
            reverse=True,
        )

        return selected[:max_items]