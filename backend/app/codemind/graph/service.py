from app.database.neo4j import driver


class CodeGraphService:
    @staticmethod
    def index_repository(repository_id: int, organization_id: int, project_id: int, name: str, project_name: str | None = None) -> None:
        with driver.session() as session:
            session.run("""
                MERGE (p:Project {organization_id:$organization_id, project_id:$project_id})
                SET p.name = coalesce(p.name, $project_name),
                    p.project_ids = [$project_id]
                WITH p
                MERGE (r:CodeRepository {id:$repository_id})
                SET r.organization_id=$organization_id,
                    r.project_id=$project_id,
                    r.name=$name
                MERGE (p)-[:HAS_CODE_REPOSITORY]->(r)
            """, repository_id=repository_id, organization_id=organization_id,
                 project_id=project_id, name=name, project_name=project_name or name)

    @staticmethod
    def clear_file(file_id: int) -> None:
        with driver.session() as session:
            session.run("""
                MATCH (f:CodeFile {id:$file_id})
                OPTIONAL MATCH (f)-[:CONTAINS_SYMBOL]->(s:CodeSymbol)
                DETACH DELETE s, f
            """, file_id=file_id)

    @staticmethod
    def index_file(repository_id: int, organization_id: int, project_id: int,
                   file_id: int, path: str, language: str | None,
                   symbols: list[dict]) -> None:
        with driver.session() as session:
            session.run("""
                MERGE (f:CodeFile {id:$file_id})
                SET f.organization_id=$organization_id,
                    f.project_id=$project_id,
                    f.repository_id=$repository_id,
                    f.path=$path,
                    f.language=$language
                WITH f
                MATCH (r:CodeRepository {id:$repository_id})
                MERGE (r)-[:CONTAINS]->(f)
            """, repository_id=repository_id, organization_id=organization_id,
                 project_id=project_id, file_id=file_id, path=path, language=language)
            for symbol in symbols:
                session.run("""
                    MERGE (s:CodeSymbol {id:$symbol_id})
                    SET s.organization_id=$organization_id,
                        s.project_id=$project_id,
                        s.repository_id=$repository_id,
                        s.file_id=$file_id,
                        s.name=$name,
                        s.qualified_name=$qualified_name,
                        s.symbol_type=$symbol_type,
                        s.start_line=$start_line,
                        s.end_line=$end_line,
                        s.call_targets=$call_targets
                    WITH s
                    MATCH (f:CodeFile {id:$file_id})
                    MERGE (f)-[:CONTAINS_SYMBOL]->(s)
                """, symbol_id=symbol["id"], organization_id=organization_id,
                     project_id=project_id, repository_id=repository_id, file_id=file_id,
                     name=symbol["name"], qualified_name=symbol["qualified_name"],
                     symbol_type=symbol["symbol_type"], start_line=symbol["start_line"],
                     end_line=symbol["end_line"], call_targets=symbol.get("call_targets", []))

            session.run("""
                MATCH (f:CodeFile {id:$file_id})
                WITH f
                UNWIND $imports AS import_name
                MERGE (m:CodeModule {key: $organization_id + ':' + $project_id + ':' + import_name})
                SET m.organization_id=$organization_id, m.project_id=$project_id, m.name=import_name
                MERGE (f)-[:IMPORTS]->(m)
            """, file_id=file_id, imports=[], organization_id=organization_id, project_id=project_id)

    @staticmethod
    def index_imports(file_id: int, organization_id: int, project_id: int, imports: list[str]) -> None:
        if not imports:
            return
        with driver.session() as session:
            session.run("""
                MATCH (f:CodeFile {id:$file_id})-[r:IMPORTS]->()
                DELETE r
            """, file_id=file_id)
            session.run("""
                MATCH (f:CodeFile {id:$file_id})
                UNWIND $imports AS import_name
                MERGE (m:CodeModule {key: $organization_id + ':' + $project_id + ':' + import_name})
                SET m.organization_id=$organization_id, m.project_id=$project_id, m.name=import_name
                MERGE (f)-[:IMPORTS]->(m)
            """, file_id=file_id, imports=imports,
                 organization_id=organization_id, project_id=project_id)

    @staticmethod
    def rebuild_calls(repository_id: int, organization_id: int, project_id: int) -> None:
        with driver.session() as session:
            session.run("""
                MATCH (s:CodeSymbol {repository_id:$repository_id})-[r:CALLS]->()
                DELETE r
            """, repository_id=repository_id)
            session.run("""
                MATCH (source:CodeSymbol {repository_id:$repository_id})
                WITH source, coalesce(source.call_targets, []) AS calls
                UNWIND calls AS call_name
                MATCH (target:CodeSymbol {repository_id:$repository_id})
                WHERE toLower(target.name)=toLower(call_name)
                  AND target.id <> source.id
                MERGE (source)-[:CALLS]->(target)
            """, repository_id=repository_id)

    @staticmethod
    def architecture(organization_id: int, project_id: int) -> dict:
        with driver.session() as session:
            rows = list(session.run("""
                MATCH (r:CodeRepository {organization_id:$organization_id, project_id:$project_id})
                OPTIONAL MATCH (r)-[:CONTAINS]->(f:CodeFile)
                RETURN r.id AS id, r.name AS name, count(f) AS files,
                       collect(DISTINCT f.language) AS languages
                ORDER BY r.name
            """, organization_id=organization_id, project_id=project_id))
        return {
            "repositories": [
                {"id": row["id"], "name": row["name"], "files": row["files"],
                 "languages": [x for x in (row["languages"] or []) if x]}
                for row in rows
            ]
        }

    @staticmethod
    def dependencies(organization_id: int, project_id: int, symbol_id: int) -> dict:
        with driver.session() as session:
            row = session.run("""
                MATCH (s:CodeSymbol {id:$symbol_id, organization_id:$organization_id, project_id:$project_id})
                OPTIONAL MATCH (s)-[:CALLS]->(callee:CodeSymbol)
                OPTIONAL MATCH (caller:CodeSymbol)-[:CALLS]->(s)
                RETURN s.name AS symbol,
                       collect(DISTINCT {id:callee.id,name:callee.name,qualified_name:callee.qualified_name}) AS callees,
                       collect(DISTINCT {id:caller.id,name:caller.name,qualified_name:caller.qualified_name}) AS callers
            """, organization_id=organization_id, project_id=project_id, symbol_id=symbol_id).single()
        if row is None:
            return {"symbol": None, "callees": [], "callers": []}
        return {
            "symbol": row["symbol"],
            "callees": [x for x in row["callees"] if x.get("id") is not None],
            "callers": [x for x in row["callers"] if x.get("id") is not None],
        }

    @staticmethod
    def impact(organization_id: int, project_id: int, symbol_id: int, depth: int = 2) -> list[dict]:
        depth = max(1, min(depth, 4))
        with driver.session() as session:
            rows = session.run(f"""
                MATCH (s:CodeSymbol {{id:$symbol_id, organization_id:$organization_id, project_id:$project_id}})
                OPTIONAL MATCH p=(s)-[:CALLS*1..{depth}]->(target:CodeSymbol)
                RETURN DISTINCT target.id AS id, target.name AS name,
                                target.qualified_name AS qualified_name, length(p) AS hops
                ORDER BY hops, name
            """, organization_id=organization_id, project_id=project_id, symbol_id=symbol_id)
            return [dict(row) for row in rows if row["id"] is not None]
