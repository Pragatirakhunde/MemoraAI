from typing import Any


class ResponseFormatter:

    @staticmethod
    def format_references(
        fused_context: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:

        references = []
        seen = set()

        for item in fused_context:
            source_type = item.get("source_type")
            score = item.get("score", 0.0)
            reference = item.get("reference") or {}

            if source_type == "vector":

                document_id = reference.get("document_id")
                chunk_id = reference.get("chunk_id")

                key = ("vector", document_id, chunk_id)

                if key in seen:
                    continue

                seen.add(key)

                references.append(
                    {
                        "source_type": "vector",
                        "document_id": document_id,
                        "chunk_id": chunk_id,
                        "title": reference.get("title"),
                        "file_path": reference.get("file_path"),
                        "extension": reference.get("extension"),
                        "chunk_index": reference.get("chunk_index"),
                        "score": round(float(score), 4),
                    }
                )

            elif source_type == "graph":

                content = item.get("content", "")

                key = ("graph", content)

                if key in seen:
                    continue

                seen.add(key)

                references.append(
                    {
                        "source_type": "graph",
                        "content": content,
                        "score": round(float(score), 4),
                    }
                )

        return references