from app.codemind.graph.service import CodeGraphService
from app.codemind.retrieval.vector_store import CodeVectorStore
from app.services.llm_service import LLMService
from app.services.search_service import SearchService


class CodeMindQueryService:
    def __init__(self):
        self.vector = CodeVectorStore()

    def search(self, query: str, organization_id: int, project_id: int, limit: int = 10):
        return self.vector.search(query, organization_id, project_id, limit)

    def ask(self, query: str, organization_id: int, project_id: int, limit: int = 8):
        results = self.search(query, organization_id, project_id, limit)
        architecture = CodeGraphService.architecture(organization_id, project_id)
        context = []
        for item in results:
            context.append(
                f"FILE: {item.get('file_path')}\n"
                f"SYMBOL: {item.get('symbol_name')}\n"
                f"LINES: {item.get('start_line')}-{item.get('end_line')}\n"
                f"CODE:\n{item.get('content', '')}"
            )
        prompt = f"""
You are CodeMind inside Memora AI.
Use only the retrieved code context for the authorized project below.
Do not invent files, functions, APIs, architecture, or behavior.
When evidence is insufficient, say so explicitly.

PROJECT_ID: {project_id}
ARCHITECTURE: {architecture}

RETRIEVED CODE:
{chr(10).join(context) if context else 'No matching code was retrieved.'}

QUESTION:
{query}

Give a direct technical answer. Mention exact file paths and symbols when present.
""".strip()
        answer = LLMService().generate(prompt)
        references = [
            {
                "file_path": item.get("file_path"),
                "symbol_name": item.get("symbol_name"),
                "start_line": item.get("start_line"),
                "end_line": item.get("end_line"),
                "score": item.get("score"),
            }
            for item in results
        ]
        return {"answer": answer, "references": references, "related_symbols": references}

    def similar(self, query: str, organization_id: int, project_id: int, limit: int = 10):
        return self.search(query, organization_id, project_id, limit)

    @staticmethod
    def architecture(organization_id: int, project_id: int):
        return CodeGraphService.architecture(organization_id, project_id)

    @staticmethod
    def dependencies(organization_id: int, project_id: int, symbol_id: int):
        return CodeGraphService.dependencies(organization_id, project_id, symbol_id)

    @staticmethod
    def impact(organization_id: int, project_id: int, symbol_id: int):
        return CodeGraphService.impact(organization_id, project_id, symbol_id)

    @staticmethod
    def business_rule(db, rule: str, organization_id: int, project_id: int, limit: int = 8):
        code_matches = CodeVectorStore().search(rule, organization_id, project_id, limit)
        memory_matches = SearchService().search(
            db=db,
            query=rule,
            organization_id=organization_id,
            project_ids=[project_id],
            limit=limit,
        )
        return {"rule": rule, "code_matches": code_matches, "memory_matches": memory_matches}
