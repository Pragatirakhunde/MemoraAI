from app.database.neo4j import driver


CONSTRAINTS = [

    # Organization
    """
    CREATE CONSTRAINT organization_id_unique IF NOT EXISTS
    FOR (n:Organization)
    REQUIRE n.id IS UNIQUE
    """,

    # Employee
    """
    CREATE CONSTRAINT employee_id_unique IF NOT EXISTS
    FOR (n:Employee)
    REQUIRE n.id IS UNIQUE
    """,

    # Document
    """
    CREATE CONSTRAINT document_id_unique IF NOT EXISTS
    FOR (n:Document)
    REQUIRE n.id IS UNIQUE
    """,

    # Project
    """
    CREATE CONSTRAINT project_key_unique IF NOT EXISTS
    FOR (n:Project)
    REQUIRE n.key IS UNIQUE
    """,

    # Module
    """
    CREATE CONSTRAINT module_key_unique IF NOT EXISTS
    FOR (n:Module)
    REQUIRE n.key IS UNIQUE
    """,

    # API
    """
    CREATE CONSTRAINT api_key_unique IF NOT EXISTS
    FOR (n:API)
    REQUIRE n.key IS UNIQUE
    """,

    # Technology
    """
    CREATE CONSTRAINT technology_org_name_unique IF NOT EXISTS
    FOR (n:Technology)
    REQUIRE (n.organization_id, n.name) IS UNIQUE
    """,

    # Database
    """
    CREATE CONSTRAINT database_org_name_unique IF NOT EXISTS
    FOR (n:Database)
    REQUIRE (n.organization_id, n.name) IS UNIQUE
    """,

    # Meeting
    """
    CREATE CONSTRAINT meeting_id_unique IF NOT EXISTS
    FOR (n:Meeting)
    REQUIRE n.id IS UNIQUE
    """,

    # Decision
    """
    CREATE CONSTRAINT decision_id_unique IF NOT EXISTS
    FOR (n:Decision)
    REQUIRE n.id IS UNIQUE
    """,
]


class GraphSchemaService:

    @staticmethod
    def create_constraints() -> None:

        with driver.session() as session:

            for constraint in CONSTRAINTS:
                session.run(constraint)

    @staticmethod
    def get_constraints():

        with driver.session() as session:

            result = session.run(
                "SHOW CONSTRAINTS"
            )

            return result.data()