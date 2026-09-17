from qdrant_client.models import PayloadSchemaType

from app.database.qdrant import (
    COLLECTION_NAME,
    qdrant_client,
)


FIELDS = [
    ("organization_id", PayloadSchemaType.INTEGER),
    ("document_type", PayloadSchemaType.KEYWORD),
    ("language", PayloadSchemaType.KEYWORD),
    ("data_source_id", PayloadSchemaType.INTEGER),
    ("extension", PayloadSchemaType.KEYWORD),
]


for field_name, field_schema in FIELDS:

    qdrant_client.create_payload_index(
        collection_name=COLLECTION_NAME,
        field_name=field_name,
        field_schema=field_schema,
    )

    print(
        f"Created index: {field_name}"
    )