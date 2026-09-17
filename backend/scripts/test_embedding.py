from app.embeddings.service import EmbeddingService


service = EmbeddingService()

text = """
TechNova Solutions uses Python, React,
PostgreSQL and Redis for enterprise software.
"""

embedding = service.embed_text(text)

print("Embedding generated")
print("Vector length:", len(embedding))
print("First 5 values:", embedding[:5])