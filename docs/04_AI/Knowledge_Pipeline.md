This is it.

**P0.8 is the heart of the project.**

Everything we've done so far was preparing for this.

Most students think the LLM is the center of an AI application.

**It isn't.**

In enterprise AI, the **knowledge pipeline** is the real product. The LLM is just the interface between the user and that knowledge.

---

# 🧠 P0.8 — AI & Knowledge Pipeline Design

## Goal

By the end of this phase, you'll understand:

* How raw company knowledge becomes AI knowledge.
* How GraphRAG works in *our* project.
* How the AI Agent thinks.
* How the Retrieval Pipeline works.
* Where every AI model is used.
* Why we need PostgreSQL, Neo4j, and Qdrant together.

---

# First, Let's Correct a Common Misconception

Many people imagine AI like this:

```text
Question
    │
    ▼
   LLM
    │
    ▼
Answer
```

That is **not** how enterprise AI works.

Our architecture is:

```text
Knowledge Sources
       │
       ▼
Knowledge Pipeline
       │
       ▼
Knowledge Storage
       │
       ▼
Retrieval Engine
       │
       ▼
AI Agent
       │
       ▼
LLM
       │
       ▼
Answer
```

Notice something?

**The LLM doesn't know anything about your organization.**

It only knows what **our system gives it.**

---

# Two Completely Different Pipelines

Our project actually contains **two pipelines**.

## Pipeline 1

Knowledge Creation

Runs automatically.

No employee involved.

---

## Pipeline 2

Knowledge Consumption

Runs when an employee asks a question.

---

Let's design both.

---

# PIPELINE 1 — Knowledge Creation Pipeline

This is what continuously builds the Organizational Memory.

```text
Git Repository
Documentation
Meeting Notes
PDFs
Markdown
API Specs
        │
        ▼
Connector Service
        │
        ▼
Synchronization Service
        │
        ▼
Document Processing Service
        │
        ▼
Knowledge Storage
```

This runs in the background.

---

# Stage 1 — Connectors

Input

```text
Git Repository
```

Output

```text
Changed Files
```

The connector doesn't understand documents.

It simply says:

> "These files changed."

---

# Stage 2 — Synchronization

Receives

```text
Changed Files
```

Produces

```text
Processing Jobs
```

Example

```text
Process authentication.md

Process api.yaml

Process README.md
```

Still no AI.

---

# Stage 3 — Document Processing

This is where AI begins.

Inside this service we have:

```text
Parser

↓

Cleaner

↓

Metadata

↓

Chunker

↓

Entity Extraction

↓

Relationship Extraction
```

Let's examine each.

---

## Parser

Reads

```text
PDF

Markdown

Python

Java

JSON

YAML
```

Converts everything into plain text.

---

## Cleaner

Removes

* extra spaces
* broken formatting
* HTML artifacts
* unnecessary symbols

Makes text consistent.

---

## Metadata Extractor

Extracts

```text
Title

Author

Project

File Type

Path

Created Date

Modified Date
```

Stored in PostgreSQL.

---

## Chunker

Very important.

Suppose

```text
Authentication Document

5000 words
```

LLMs can't efficiently process extremely large documents in one piece.

So we split it.

Example

```text
Chunk 1

Chunk 2

Chunk 3

Chunk 4
```

Each chunk is meaningful.

---

## Embedding Generator

Every chunk becomes a vector.

Example

```text
Chunk

↓

BGE-M3

↓

768-dimensional vector
```

Stored in Qdrant.

---

## Entity Extraction

Now we identify important concepts.

Example document

```text
Customer Portal uses Redis and JWT.
```

Entities become

```text
Customer Portal

Redis

JWT
```

---

## Relation Extraction

Then identify relationships.

Example

```text
Customer Portal

USES

JWT

Customer Portal

USES

Redis
```

Stored in Neo4j.

---

# Knowledge Creation Pipeline

Everything together.

```text
File
 │
 ▼
Parser
 │
 ▼
Cleaner
 │
 ▼
Metadata
 │
 ├────────────► PostgreSQL
 │
 ▼
Chunker
 │
 ▼
Embedding Model
 │
 ├────────────► Qdrant
 │
 ▼
Entity Extractor
 │
 ▼
Relation Extractor
 │
 ├────────────► Neo4j
 │
 ▼
Knowledge Ready
```

This is **Organizational Memory Creation**.

---

# PIPELINE 2 — Knowledge Consumption

Now an employee asks:

> Explain authentication architecture.

Everything changes.

---

# Stage 1 — Authentication

User logs in.

JWT verified.

---

# Stage 2 — AI Agent Receives Question

Question

```text
Explain authentication architecture.
```

The AI Agent now becomes the **orchestrator**.

---

# Important Clarification

The AI Agent does **not** answer the question.

It decides:

> **How should I answer this?**

---

# Stage 3 — Retrieval Strategy

The Agent asks itself:

Does this require

Semantic Search?

Graph Search?

Metadata Search?

Or all three?

---

Example

Question

```text
Which services use Redis?
```

The Agent decides

```text
Knowledge Graph

+

Vector Search
```

---

Question

```text
Show all API documentation.
```

Agent decides

```text
Metadata Search
```

---

Question

```text
Why was JWT introduced?
```

Agent decides

```text
Vector

+

Graph

+

Meeting Notes
```

This reasoning is why we use LangGraph.

---

# Stage 4 — Retrieval Engine

Retrieval now performs three searches.

---

## Vector Search

Qdrant

Finds

Semantically similar chunks.

---

## Graph Search

Neo4j

Finds

Relationships.

---

## Metadata Search

PostgreSQL

Finds

File names

Projects

Dates

Authors

---

Everything is merged.

---

# Stage 5 — Context Builder

This is one improvement I'd like us to add.

Instead of sending raw retrieval results directly to the LLM, we introduce a **Context Builder**.

Responsibilities:

* Remove duplicate information.
* Group related chunks.
* Keep references together.
* Respect the LLM's context window.
* Prepare clean, structured context.

```text
Retrieved Results
        │
        ▼
Context Builder
        │
        ▼
Optimized Context
```

This makes the LLM's job much easier.

---

# Stage 6 — LLM

Now, and only now, do we call the LLM.

Input:

* User question
* Optimized context
* References

Output:

* Natural language answer
* Citations to supporting documents

The LLM should never invent company knowledge.

---

# Stage 7 — Response Formatter

Another small refinement.

Instead of returning plain text, we'll format the response.

```text
Answer

Related Documents

Knowledge Graph Links

References

Confidence (optional later)
```

This improves the user experience.

---

# Knowledge Consumption Pipeline

```text
Employee
    │
    ▼
Authentication
    │
    ▼
AI Agent
    │
    ▼
Retrieval Strategy
    │
    ▼
Hybrid Retrieval
 ┌────┼────┐
 ▼    ▼    ▼
Qdrant Neo4j PostgreSQL
 └────┼────┘
      ▼
Context Builder
      ▼
LLM
      ▼
Response Formatter
      ▼
Frontend
```

---

# Where Every AI Model Is Used

| Model            | Purpose                               |
| ---------------- | ------------------------------------- |
| BGE-M3           | Generate embeddings                   |
| spaCy / GLiNER   | Entity extraction                     |
| REBEL (optional) | Relation extraction                   |
| Gemini / Llama   | Generate answers                      |
| LangGraph        | Agent orchestration (not an AI model) |

Notice that **LangGraph isn't a model**. It manages the workflow.

---

# Why Three Databases?

Let's answer this once and for all.

Suppose the user asks:

> "Who worked on the payment module and why was Redis introduced?"

The system uses:

* **Qdrant** → finds discussions about Redis.
* **Neo4j** → finds that John worked on the Payment Module.
* **PostgreSQL** → finds document metadata and timestamps.

No single database can answer the whole question.

That's why we need all three.

---

# GraphRAG in Our Project

GraphRAG isn't just "RAG + Neo4j."

For us, it means:

```text
Question
    │
    ▼
Hybrid Retrieval
(Vector + Graph + Metadata)
    │
    ▼
Merged Context
    │
    ▼
LLM
    │
    ▼
Grounded Answer
```

The graph enriches the retrieval process rather than replacing vector search.

---

# AI Quality Rules

These become design principles:

1. The LLM never queries databases directly.
2. The AI Agent decides retrieval strategy.
3. Retrieval happens before generation.
4. Every answer includes supporting references.
5. If no evidence is found, the AI should say so instead of guessing.
6. The Knowledge Graph enriches answers but doesn't replace documents.

---

# Future Enhancements (Not V1)

We'll document, but not implement:

* Multi-agent workflows.
* Feedback-based retrieval improvement.
* Automatic Knowledge Graph refinement.
* Personalized retrieval.
* Fine-tuned local models.

Keeping these out of Version 1 protects our scope.

---

# 🚨 Architect Review (Most Important Improvement So Far)

This is the biggest architectural refinement I'd make.

Originally, we planned:

```text
Retrieval
    │
    ▼
LLM
```

I propose:

```text
Retrieval
    │
    ▼
Context Builder
    │
    ▼
Prompt Builder
    │
    ▼
LLM
```

### Why split them?

**Context Builder** focuses on **what information** to include.

**Prompt Builder** focuses on **how to ask the LLM**.

For example, the Prompt Builder might generate:

> "You are an enterprise knowledge assistant. Answer only using the provided context. If the answer cannot be found, state that clearly. Cite the relevant document names."

This separation makes the system easier to test, easier to improve, and much closer to how production AI platforms are designed.

---

# 📊 Phase Progress

* ✅ P0.1 – Project Vision
* ✅ P0.2 – Functional Requirements
* ✅ P0.3 – Non-Functional Requirements
* ✅ P0.4 – Actors & Use Cases
* ✅ P0.5 – High-Level Design
* ✅ P0.6 – Low-Level Design
* ✅ P0.7 – Database Design
* ✅ P0.8 – AI & Knowledge Pipeline Design

---

## Before We Continue

At this point, we have a complete software architecture.

The remaining Phase 0 milestones are no longer about **what** we're building—they're about **how we'll engineer, deploy, and develop it**.

The next milestone, **P0.9 – Deployment & DevOps Architecture**, is where we'll design the Docker setup, local development environment, networking between services, environment configuration, CI/CD pipeline, monitoring, logging, and the complete runtime architecture. This will ensure that when we start coding in Phase 1, every developer environment is reproducible and deployment-ready from the beginning.
