from app.services.graph_query_service import (
    GraphQueryService,
)


print("\n=== Projects ===")

projects = (
    GraphQueryService.list_projects(
        organization_id=1,
    )
)

for project in projects:
    print(project)


print("\n=== Project Context ===")

context = (
    GraphQueryService.get_project_context(
        organization_id=1,
        project_name="Inventory Management",
    )
)

print(context)


print("\n=== Projects using PostgreSQL ===")

database_projects = (
    GraphQueryService.get_projects_using_database(
        organization_id=1,
        database_name="postgresql",
    )
)

for project in database_projects:
    print(project)


print("\n=== Documents mentioning React ===")

documents = (
    GraphQueryService.get_documents_for_entity(
        organization_id=1,
        entity_name="react",
    )
)

for document in documents:
    print(document)