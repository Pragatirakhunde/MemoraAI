from app.database.neo4j import driver

from app.database.postgres import SessionLocal

from app.repositories.document_repository import (
    DocumentRepository,
)

from app.services.graph_query_service import (
    GraphQueryService,
)


db = SessionLocal()

try:

    print("=" * 60)
    print("PHASE 7 VALIDATION")
    print("=" * 60)

    # ----------------------------------------
    # 1. PostgreSQL documents
    # ----------------------------------------

    documents = DocumentRepository.get_all(
        db,
        organization_id=1,
    )

    print("\n1. PostgreSQL")

    if not documents:
        raise RuntimeError(
            "No documents found."
        )

    print(
        "Documents:",
        len(documents),
    )

    # ----------------------------------------
    # 2. Neo4j node counts
    # ----------------------------------------

    node_query = """
    MATCH (n)
    WHERE n.organization_id = $organization_id
       OR (n:Organization AND n.id = $organization_id)
    RETURN count(n) AS count
    """

    with driver.session() as session:

        result = session.run(
            node_query,
            organization_id=1,
        ).single()

        node_count = result["count"]

    print("\n2. Neo4j")

    print(
        "Graph nodes:",
        node_count,
    )

    if node_count == 0:
        raise RuntimeError(
            "No Neo4j nodes found."
        )

    # ----------------------------------------
    # 3. Relationship count
    # ----------------------------------------

    relationship_query = """
    MATCH (a)-[r]->(b)
    WHERE
        (
            a.organization_id = $organization_id
            OR b.organization_id = $organization_id
        )
    RETURN count(r) AS count
    """

    with driver.session() as session:

        result = session.run(
            relationship_query,
            organization_id=1,
        ).single()

        relationship_count = result["count"]

    print(
        "Graph relationships:",
        relationship_count,
    )

    # ----------------------------------------
    # 4. Project query
    # ----------------------------------------

    projects = (
        GraphQueryService.list_projects(
            organization_id=1,
        )
    )

    print("\n3. Project Query")

    print(
        "Projects found:",
        len(projects),
    )

    if projects:
        for project in projects:
            print(
                "-",
                project.get("name"),
            )

    # ----------------------------------------
    # 5. Graph neighborhood test
    # ----------------------------------------

    neighborhood = (
        GraphQueryService.get_entity_neighborhood(
            organization_id=1,
            entity_name="postgresql",
        )
    )

    print(
        "\n4. Entity Neighborhood"
    )

    print(
        "PostgreSQL relationships:",
        len(neighborhood),
    )

    for item in neighborhood:
        print(
            "-",
            item.get("source_name"),
            "->",
            item.get("relationship"),
            "->",
            item.get("target_name"),
        )

    # ----------------------------------------
    # 6. Project knowledge
    # ----------------------------------------

    if projects:

        project_name = projects[0]["name"]

        knowledge = (
            GraphQueryService.get_project_knowledge(
                organization_id=1,
                project_name=project_name,
            )
        )

        print(
            "\n5. Project Knowledge"
        )

        print(
            "Project:",
            knowledge.get("project"),
        )

        print(
            "Technologies:",
            len(
                knowledge.get(
                    "technologies",
                    [],
                )
            ),
        )

        print(
            "Databases:",
            len(
                knowledge.get(
                    "databases",
                    [],
                )
            ),
        )

        print(
            "Documents:",
            len(
                knowledge.get(
                    "documents",
                    [],
                )
            ),
        )

    # ----------------------------------------
    # SUCCESS
    # ----------------------------------------

    print("\n" + "=" * 60)
    print("PHASE 7 VALIDATION SUCCESSFUL")
    print("=" * 60)

finally:
    db.close()