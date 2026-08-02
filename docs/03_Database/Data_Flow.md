Excellent. This is one of the most important phases because **bad database design can ruin an otherwise good project**.

Also, I want to improve something from our earlier discussions.

> We originally talked about PostgreSQL, Neo4j, and Qdrant separately.

Professional systems **never** think of databases separately.

They think:

> **"How does one piece of information travel through the entire system?"**

That's exactly how we're going to design it.

---

# 🗄️ P0.7 — Database Design

## Goal

By the end of this phase, we'll know:

* What goes into PostgreSQL?
* What goes into Neo4j?
* What goes into Qdrant?
* How are they connected?
* What are the IDs?
* How does one document move across all databases?

---

# The Golden Rule

Each database has **one responsibility**.

| Database   | Responsibility            |
| ---------- | ------------------------- |
| PostgreSQL | Structured business data  |
| Qdrant     | Semantic understanding    |
| Neo4j      | Relationships & reasoning |

Never store the same thing in all three.

---

# Think About One Document

Imagine a document:

```
authentication_design.md
```

It says:

```
JWT Authentication

Author:
John

Uses:

Redis

OAuth2

Project:
Customer Portal
```

This **one document** will create data in **three databases**.

---

# Step 1 — PostgreSQL

PostgreSQL stores **facts**.

Not vectors.

Not graphs.

---

## Documents Table

| Field         | Type      |
| ------------- | --------- |
| id            | UUID      |
| title         | TEXT      |
| file_name     | TEXT      |
| source        | TEXT      |
| connector_id  | UUID      |
| checksum      | TEXT      |
| last_modified | TIMESTAMP |
| status        | TEXT      |
| created_at    | TIMESTAMP |

Example

| id     | title                 |
| ------ | --------------------- |
| DOC001 | Authentication Design |

---

## Users

| id | name | role |

---

## Connectors

| id | type | path |

---

## Sync History

| id | connector | status | time |

---

## Search History

| id | user | question | timestamp |

---

## Processing Jobs

| id | file | status |

---

## Why PostgreSQL?

Because we ask questions like

```
Who uploaded this?

When?

Which connector?

Last sync?
```

Those are relational questions.

---

# Step 2 — Qdrant

Now the document is chunked.

Example

Chunk 1

```
JWT Authentication
uses Redis
```

Chunk 2

```
OAuth2 flow
```

Each chunk becomes an embedding.

---

Collection

```
documents
```

---

Payload

```json
{
  "chunk_id": "CH001",
  "document_id": "DOC001",
  "project": "Customer Portal",
  "file_name": "authentication_design.md",
  "chunk_number": 1,
  "text": "JWT Authentication uses Redis..."
}
```

Notice

We also store metadata with vectors.

---

Why?

Later we can filter:

```
Only search

Customer Portal
```

---

# Step 3 — Neo4j

Now we store relationships.

Nodes

```
Project

Technology

API

Developer

Database

Document

Module
```

---

Relationships

```
WORKED_ON

USES

CALLS

IMPLEMENTS

DOCUMENTED_IN

OWNS

DEPENDS_ON
```

Example

```text
(Customer Portal)

↓

USES

↓

(JWT)

↓

STORES_SESSION_IN

↓

(Redis)
```

Neo4j never stores full document text.

Only knowledge.

---

# Cross-Database Linking

This is the most important design decision.

Everything revolves around a **Document ID**.

Example

```
DOC001
```

---

In PostgreSQL

```
DOC001
```

stores metadata.

---

In Qdrant

Each chunk stores

```
document_id = DOC001
```

---

In Neo4j

Document node

```
Document

id=DOC001
```

links to

Project

Technology

Developer

---

One ID connects everything.

---

# Entity IDs

Every major object gets a UUID.

```
USR001

User

DOC001

Document

PRJ001

Project

CON001

Connector

JOB001

Processing Job

CH001

Chunk
```

We will actually use UUIDs in code, but this naming helps us think.

---

# Relationship Example

Imagine

```
payment_api.py
```

Processing extracts:

```
Payment API

Stripe

Redis

John

Customer Portal
```

Neo4j creates

```text
John

↓

WORKED_ON

↓

Payment API

↓

USES

↓

Stripe

↓

USES

↓

Redis

↓

BELONGS_TO

↓

Customer Portal
```

---

# Storage Flow

One file.

Three databases.

```text
Git Repository

↓

authentication.md

↓

Processing

↓

Metadata

→ PostgreSQL

↓

Chunking

→ Qdrant

↓

Entities

↓

Relationships

→ Neo4j
```

---

# Query Flow

Employee asks

```
How does authentication work?
```

---

Retrieval

Searches

Qdrant

↓

Relevant chunks

---

Neo4j

↓

Related technologies

↓

Related APIs

↓

Related developers

---

PostgreSQL

↓

Metadata

↓

References

---

AI

↓

Answer

---

# PostgreSQL Schema

Core tables

```
users

roles

connectors

documents

processing_jobs

sync_history

chat_history

search_history

system_logs
```

Simple.

Professional.

---

# Neo4j Schema

Nodes

```
User

Project

Module

API

Document

Technology

Database

Meeting

Decision
```

Relationships

```
WORKED_ON

USES

CALLS

BELONGS_TO

CREATED_BY

DEPENDS_ON

DOCUMENTED_IN

RELATED_TO
```

---

# Qdrant Schema

Collections

```
documents
```

Future

```
meeting_notes

source_code

wiki

apis
```

Version 1

Only one collection.

Keep it simple.

---

# Indexing Strategy

PostgreSQL

Indexes

```
document_id

user_id

connector_id
```

---

Neo4j

Indexes

```
Project

Technology

Document
```

---

Qdrant

Uses

Vector Index

No work needed from us.

---

# Lifecycle of One Document

This is the most important diagram.

```text
1. Git Repository
        │
        ▼
2. Connector detects update
        │
        ▼
3. Sync Service creates job
        │
        ▼
4. Document Processing
        │
        ├─────────────┐
        ▼             ▼
 Metadata         Chunks
        │             │
        ▼             ▼
 PostgreSQL      Embedding
                        │
                        ▼
                     Qdrant
        │
        ▼
 Entity Extraction
        │
        ▼
 Relationship Extraction
        │
        ▼
      Neo4j
        │
        ▼
 Knowledge Ready
```

---

# Database Responsibilities

| Service        | PostgreSQL | Neo4j | Qdrant |
| -------------- | ---------- | ----- | ------ |
| Authentication | ✅          | ❌     | ❌      |
| Connectors     | ✅          | ❌     | ❌      |
| Sync           | ✅          | ❌     | ❌      |
| Processing     | Read/Write | Write | Write  |
| Retrieval      | Read       | Read  | Read   |
| AI             | Read       | Read  | Read   |
| Dashboard      | Read       | Read  | ❌      |

Notice:

The AI never writes.

Only reads.

---

# Future Scalability

Because of this design,

later we can replace

Qdrant

↓

Weaviate

No schema redesign.

---

Neo4j

↓

Amazon Neptune

No redesign.

---

Gemini

↓

Llama

No redesign.

---

# 🚨 Architect Review (One Important Refinement)

There's one architectural change I want to make based on enterprise practice.

Earlier, we planned to store **chat history** in PostgreSQL as simple text. Instead, let's separate two concepts:

* **Conversation**: metadata such as conversation ID, user, timestamps, and title.
* **Messages**: each individual user or AI message linked to a conversation.

That gives us a cleaner model:

```text
Conversation
    │
    ├── Message (User)
    ├── Message (AI)
    ├── Message (User)
    └── Message (AI)
```

This makes features like renaming conversations, deleting a conversation, or exporting chat history much easier later.

---

# 📊 Phase Progress

* ✅ P0.1 – Project Vision
* ✅ P0.2 – Functional Requirements
* ✅ P0.3 – Non-Functional Requirements
* ✅ P0.4 – Actors & Use Cases
* ✅ P0.5 – High-Level Design
* ✅ P0.6 – Low-Level Design
* ✅ P0.7 – Database Design

At this stage, we've designed **the static architecture**—services and databases.

The next milestone, **P0.8 – AI & Knowledge Pipeline Design**, is where we'll design the **dynamic architecture**: exactly how a document is transformed into organizational knowledge, how GraphRAG works in our project, how the LangGraph agent makes decisions, and how the complete end-to-end AI workflow operates. This is where the "intelligence" of the platform is truly defined.
