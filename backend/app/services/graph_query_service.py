from app.database.neo4j import driver


class GraphQueryService:

    @staticmethod
    def list_projects(
        organization_id: int,
    ) -> list[dict]:

        query = """
        MATCH (p:Project)
        WHERE p.organization_id = $organization_id
        RETURN
            p.name AS name,
            p.key AS key,
            p.confidence AS confidence
        ORDER BY p.name
        """

        with driver.session() as session:
            result = session.run(
                query,
                organization_id=organization_id,
            )

            return result.data()

    @staticmethod
    def get_project_context(
        organization_id: int,
        project_name: str,
    ) -> dict:

        project_query = """
        MATCH (p:Project)
        WHERE p.organization_id = $organization_id
          AND toLower(p.name) = toLower($project_name)

        OPTIONAL MATCH (p)-[:USES]->(t:Technology)
        OPTIONAL MATCH (p)-[:USES_DATABASE]->(db:Database)
        OPTIONAL MATCH (d:Document)-[:DOCUMENTS]->(p)

        RETURN
            p.name AS project,
            collect(DISTINCT t.name) AS technologies,
            collect(DISTINCT db.name) AS databases,
            collect(DISTINCT m.name) AS modules,
            collect(DISTINCT {
                id: d.id,
                title: d.title,
                path: d.file_path
            }) AS documents
        """

        document_query = """
        MATCH (d:Document)-[:DOCUMENTS]->(p:Project)
        WHERE p.organization_id = $organization_id
          AND toLower(p.name) = toLower($project_name)

        RETURN
            d.id AS document_id,
            d.title AS title,
            d.file_path AS file_path
        ORDER BY d.title
        """

        with driver.session() as session:

            project_result = session.run(
                project_query,
                organization_id=organization_id,
                project_name=project_name,
            ).single()

            if project_result is None:
                return {
                    "project": None,
                    "technologies": [],
                    "databases": [],
                    "modules": [],
                    "documents": [],
                }

            document_result = session.run(
                document_query,
                organization_id=organization_id,
                project_name=project_name,
            )

            return {
                "project": project_result["project"],
                "technologies": (
                    project_result["technologies"]
                ),
                "databases": (
                    project_result["databases"]
                ),
                "modules": (
                    project_result["modules"]
                ),
                "documents": document_result.data(),
            }

    @staticmethod
    def get_projects_using_technology(
        organization_id: int,
        technology_name: str,
    ) -> list[dict]:

        query = """
        MATCH (p:Project)-[:USES]->(t:Technology)
        WHERE p.organization_id = $organization_id
          AND t.organization_id = $organization_id
          AND toLower(t.name) = toLower($technology_name)

        RETURN
            p.name AS project,
            t.name AS technology
        ORDER BY p.name
        """

        with driver.session() as session:
            result = session.run(
                query,
                organization_id=organization_id,
                technology_name=technology_name,
            )

            return result.data()

    @staticmethod
    def get_projects_using_database(
        organization_id: int,
        database_name: str,
    ) -> list[dict]:

        query = """
        MATCH (p:Project)-[:USES_DATABASE]->(db:Database)
        WHERE p.organization_id = $organization_id
          AND db.organization_id = $organization_id
          AND toLower(db.name) = toLower($database_name)

        RETURN
            p.name AS project,
            db.name AS database
        ORDER BY p.name
        """

        with driver.session() as session:
            result = session.run(
                query,
                organization_id=organization_id,
                database_name=database_name,
            )

            return result.data()

    @staticmethod
    def get_documents_for_entity(
        organization_id: int,
        entity_name: str,
    ) -> list[dict]:

        query = """
        MATCH (d:Document)-[r:MENTIONS]->(n)
        WHERE d.organization_id = $organization_id
          AND toLower(n.name) = toLower($entity_name)

        RETURN
            d.id AS document_id,
            d.title AS title,
            d.file_path AS file_path,
            type(r) AS relationship,
            labels(n) AS entity_type,
            n.name AS entity_name
        ORDER BY d.title
        """

        with driver.session() as session:
            result = session.run(
                query,
                organization_id=organization_id,
                entity_name=entity_name,
            )

            return result.data()

    @staticmethod
    def get_project_knowledge(
        organization_id: int,
        project_name: str,
    ) -> dict:

        query = """
        MATCH (p:Project)
        WHERE p.organization_id = $organization_id
        AND toLower(p.name) = toLower($project_name)

        OPTIONAL MATCH (p)-[:USES]->(t:Technology)
        OPTIONAL MATCH (p)-[:USES_DATABASE]->(db:Database)
        OPTIONAL MATCH (p)-[:HAS_MODULE]->(m:Module)

        OPTIONAL MATCH (d:Document)-[
            :DOCUMENTS
        ]->(p)

        RETURN
            p.name AS project,

            collect(DISTINCT {
                name: t.name,
                type: 'Technology'
            }) AS technologies,

            collect(DISTINCT {
                name: db.name,
                type: 'Database'
            }) AS databases,

            collect(DISTINCT {
                name: m.name,
                type: 'Module'
            }) AS modules,

            collect(DISTINCT {
                id: d.id,
                title: d.title,
                path: d.file_path
            }) AS documents
        """

        with driver.session() as session:

            result = session.run(
                query,
                organization_id=organization_id,
                project_name=project_name,
            )

            record = result.single()

            if record is None:
                return {
                    "project": None,
                    "technologies": [],
                    "databases": [],
                    "modules": [],
                    "documents": [],
                }

            return {
                "project": record["project"],
                "technologies": [
                    item
                    for item in record["technologies"]
                    if item["name"] is not None
                ],
                "databases": [
                    item
                    for item in record["databases"]
                    if item["name"] is not None
                ],
                "modules": [
                    item
                    for item in record["modules"]
                    if item["name"] is not None
                ],
                "documents": [
                    item
                    for item in record["documents"]
                    if item["id"] is not None
                ],
            }

    @staticmethod
    def get_entity_neighborhood(
        organization_id: int,
        entity_name: str,
    ) -> list[dict]:

        query = """
        MATCH (n)
        WHERE
            toLower(coalesce(n.name, ''))
                = toLower($entity_name)
            AND n.organization_id
                = $organization_id

        OPTIONAL MATCH (n)-[r]-(related)

        WHERE
            related.organization_id
                = $organization_id

        RETURN
            labels(n) AS source_type,
            n.name AS source_name,
            type(r) AS relationship,
            labels(related) AS target_type,
            related.name AS target_name
        ORDER BY relationship, target_name
        """

        with driver.session() as session:

            result = session.run(
                query,
                organization_id=organization_id,
                entity_name=entity_name,
            )

            return result.data()

    @staticmethod
    def get_project_documents(
        organization_id: int,
        project_name: str,
    ) -> list[dict]:

        query = """
        MATCH (d:Document)-[:DOCUMENTS]->(p:Project)
        WHERE p.organization_id = $organization_id
        AND toLower(p.name)
            = toLower($project_name)

        RETURN
            d.id AS document_id,
            d.title AS title,
            d.file_path AS file_path
        ORDER BY d.title
        """

        with driver.session() as session:

            result = session.run(
                query,
                organization_id=organization_id,
                project_name=project_name,
            )

            return result.data()

    @staticmethod
    def expand_entity(
        organization_id: int,
        entity_name: str,
        max_hops: int = 2,
        limit: int = 20,
    ) -> list[dict]:

        max_hops = max(
            1,
            min(max_hops, 2),
        )

        query = f"""
        MATCH (start)
        WHERE
            toLower(coalesce(start.name, ''))
                = toLower($entity_name)
            AND (
                start.organization_id = $organization_id
                OR (
                    start:Organization
                    AND start.id = $organization_id
                )
            )

        MATCH path =
            (start)-[*1..{max_hops}]-(related)

        WHERE
            related <> start
            AND (
                related.organization_id = $organization_id
                OR (
                    related:Organization
                    AND related.id = $organization_id
                )
            )

        RETURN
            start.name AS source_name,
            labels(start) AS source_type,

            [
                node IN nodes(path) |
                coalesce(node.name, toString(node.id))
            ] AS path_nodes,

            [
                relationship IN relationships(path) |
                type(relationship)
            ] AS path_relationships,

            related.name AS target_name,
            labels(related) AS target_type,
            length(path) AS hops

        ORDER BY hops ASC
        LIMIT $limit
        """

        with driver.session() as session:

            result = session.run(
                query,
                organization_id=organization_id,
                entity_name=entity_name,
                limit=limit,
            )

            return result.data()

    @staticmethod
    def resolve_entities_from_query(
        organization_id: int,
        query_text: str,
        limit: int = 20,
    ) -> list[dict]:

        cypher = """
        MATCH (n)
        WHERE
            n.name IS NOT NULL
            AND (
                n.organization_id = $organization_id
                OR (
                    n:Organization
                    AND n.id = $organization_id
                )
            )
            AND toLower($query_text)
                CONTAINS toLower(n.name)

        RETURN
            n.name AS name,
            labels(n) AS labels
        ORDER BY size(n.name) DESC
        LIMIT $limit
        """

        with driver.session() as session:

            result = session.run(
                cypher,
                organization_id=organization_id,
                query_text=query_text,
                limit=limit,
            )

            return result.data()

    @staticmethod
    def get_project_graph(
        organization_id: int,
        project_name: str,
    ) -> dict:
        """
        Return a frontend-friendly one-hop graph
        centered around a project.
        """

        query = """
        MATCH (p:Project)
        WHERE p.organization_id = $organization_id
          AND toLower(p.name) = toLower($project_name)

        OPTIONAL MATCH (p)-[r]-(n)

        WHERE
            n.organization_id = $organization_id

        RETURN
            p.name AS project_name,
            labels(p) AS project_type,
            elementId(p) AS project_id,

            type(r) AS relationship,

            n.name AS target_name,
            labels(n) AS target_type,
            elementId(n) AS target_id
        ORDER BY relationship, target_name
        """

        with driver.session() as session:

            result = session.run(
                query,
                organization_id=organization_id,
                project_name=project_name,
            )

            records = result.data()

        if not records:
            return {
                "nodes": [],
                "edges": [],
            }

        nodes = {}
        edges = set()

        first = records[0]

        project_id = first.get("project_id")
        project_name_value = first.get("project_name")
        project_type = first.get("project_type") or ["Project"]

        if project_id:
            nodes[str(project_id)] = {
                "id": str(project_id),
                "label": project_name_value,
                "type": project_type[0],
            }

        for record in records:

            target_id = record.get("target_id")
            target_name = record.get("target_name")
            target_type = record.get("target_type") or []
            relationship = record.get("relationship")

            if not target_id or not target_name:
                continue

            target_id = str(target_id)

            nodes[target_id] = {
                "id": target_id,
                "label": target_name,
                "type": target_type[0] if target_type else "Entity",
            }

            if relationship and project_id:

                edge_key = (
                    str(project_id),
                    target_id,
                    relationship,
                )

                if edge_key not in edges:
                    edges.add(edge_key)

        return {
            "nodes": list(nodes.values()),
            "edges": [
                {
                    "source": source,
                    "target": target,
                    "relationship": relationship,
                }
                for source, target, relationship in edges
            ],
        }

    @staticmethod
    def get_graph_stats(
        organization_id: int,
    ) -> dict:

        node_query = """
        MATCH (n)
        WHERE n.organization_id = $organization_id

        RETURN
            count(n) AS total_nodes,
            count(CASE WHEN n:Project
                THEN 1 END) AS projects,
            count(CASE WHEN n:Technology
                THEN 1 END) AS technologies,
            count(CASE WHEN n:Database
                THEN 1 END) AS databases,
            count(CASE WHEN n:Document
                THEN 1 END) AS documents
        """

        relationship_query = """
        MATCH (a)-[r]-(b)
        WHERE
            a.organization_id = $organization_id
            AND b.organization_id = $organization_id

        RETURN count(r) AS total_relationships
        """

        with driver.session() as session:

            node_result = session.run(
                node_query,
                organization_id=organization_id,
            ).single()

            relationship_result = session.run(
                relationship_query,
                organization_id=organization_id,
            ).single()

        return {
            "total_nodes": (
                node_result["total_nodes"]
                if node_result
                else 0
            ),
            "projects": (
                node_result["projects"]
                if node_result
                else 0
            ),
            "technologies": (
                node_result["technologies"]
                if node_result
                else 0
            ),
            "databases": (
                node_result["databases"]
                if node_result
                else 0
            ),
            "documents": (
                node_result["documents"]
                if node_result
                else 0
            ),
            "total_relationships": (
                relationship_result[
                    "total_relationships"
                ]
                if relationship_result
                else 0
            ),
        }