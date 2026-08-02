Perfect. Now we're entering what I consider the **most important phase of the entire project**.

# 🚨 P0.6 — Low-Level Design (LLD)

Until now we've looked at the city from an airplane.

Now we're going inside every building.

This is where we decide:

* Which services exist?
* What does each service do?
* Which APIs does it expose?
* Which database can it access?
* Which service can call another service?

**This document will literally become our coding roadmap.**

---

# Before We Start: One Important Improvement

I want to improve something from our previous discussions.

Earlier we said:

> "Instead of writing one huge backend, we'll build independent services."

Technically, that's correct—but for **Version 1** we'll implement them as **modules inside one FastAPI application**, not as independently deployed microservices.

So think of them as:

```text
FastAPI Application

├── Authentication Module
├── User Module
├── Connector Module
├── Sync Module
├── Processing Module
├── Retrieval Module
├── AI Module
├── Dashboard Module
```

This gives us the benefits of clean architecture without the complexity of distributed systems.

---

# Backend Architecture

```text
backend/

├── auth/
├── users/
├── connectors/
├── sync/
├── processing/
├── storage/
├── retrieval/
├── ai/
├── dashboard/
├── common/
└── api/
```

Each folder is one logical service.

---

# Service 1 — Authentication Service

## Purpose

Identify who is using the system.

Nothing more.

---

## Responsibilities

* Login
* Logout
* JWT generation
* JWT verification
* Password hashing
* Authorization

---

## Inputs

```text
Email

Password
```

---

## Outputs

```text
JWT Token
```

---

## Database

PostgreSQL

---

## APIs

```text
POST /login

POST /logout

GET /me
```

---

## Used By

Every module.

---

# Service 2 — User Service

Purpose

Manage users.

---

Responsibilities

* Create employee
* Update profile
* Deactivate account
* List users

---

Database

PostgreSQL

---

APIs

```text
GET /users

POST /users

PUT /users/{id}

DELETE /users/{id}
```

---

# Service 3 — Connector Management Service

This is one of the most important services.

---

Purpose

Know where organizational knowledge exists.

---

Responsibilities

* Register Git repository
* Register documentation folder
* Enable connector
* Disable connector
* Validate connector

---

Database

PostgreSQL

---

APIs

```text
POST /connectors

GET /connectors

PUT /connectors/{id}

DELETE /connectors/{id}
```

---

Output

```text
Connector Configuration
```

---

# Service 4 — Synchronization Service

Purpose

Detect changes.

Notice:

It does NOT process files.

---

Responsibilities

* Poll repositories
* Detect changes
* Detect deletions
* Detect updates
* Schedule processing jobs

---

Input

```text
Connector Configuration
```

---

Output

```text
Processing Tasks
```

---

Database

PostgreSQL

(sync history)

---

Future

Uses

Celery

---

# Service 5 — Document Processing Service

One of the biggest services.

---

Purpose

Transform raw files into structured knowledge.

---

Pipeline

```text
File

↓

Parser

↓

Cleaner

↓

Metadata

↓

Chunking

↓

Entities

↓

Relations
```

---

Responsibilities

* Parse PDF
* Parse Markdown
* Parse source code
* Extract metadata
* Chunk text
* Extract entities
* Extract relationships

---

Output

```text
Knowledge Object
```

---

# Service 6 — Embedding Service

Purpose

Generate embeddings.

---

Responsibilities

* Receive chunks
* Generate vectors
* Store vectors

---

Uses

```text
BGE-M3
```

---

Database

Qdrant

---

Output

```text
Vector IDs
```

---

# Service 7 — Knowledge Graph Service

Purpose

Maintain Neo4j.

---

Responsibilities

* Create nodes
* Create relationships
* Update graph
* Delete outdated relationships

---

Example

```text
Employee

↓

WORKED_ON

↓

Project
```

---

Database

Neo4j

---

Output

Updated graph.

---

# Service 8 — Retrieval Service

One of the most intelligent services.

---

Purpose

Find knowledge.

---

Responsibilities

Vector Search

Graph Search

Metadata Search

Hybrid Ranking

---

Input

```text
Question
```

---

Output

```text
Relevant Context
```

---

Uses

```text
PostgreSQL

Neo4j

Qdrant
```

---

# Service 9 — AI Agent Service

Purpose

Reason.

Not search.

---

Responsibilities

Receive question

↓

Choose retrieval

↓

Combine context

↓

Call LLM

↓

Return answer

---

Uses

LangGraph

---

Input

Question

---

Output

Final Answer

---

# Service 10 — Dashboard Service

Purpose

Provide statistics.

---

Responsibilities

* Analytics
* Query history
* Sync history
* User activity
* System status

---

Database

PostgreSQL

---

# Service Dependencies

This is extremely important.

```text
Authentication
        │
        ▼
Every Service


Connector

↓

Synchronization

↓

Processing

↓

Embedding

↓

Knowledge Graph

↓

Retrieval

↓

AI Agent

↓

Frontend
```

Notice

Everything moves downward.

No circular dependencies.

---

# Database Ownership

Professional systems avoid multiple services writing to the same data without ownership.

| Service         | Owns                        |
| --------------- | --------------------------- |
| Authentication  | Users, Sessions             |
| User            | User Profiles               |
| Connector       | Connector Configurations    |
| Sync            | Sync History                |
| Processing      | Processing Status           |
| Embedding       | Vector Storage              |
| Knowledge Graph | Graph Nodes                 |
| Retrieval       | No ownership (reads only)   |
| AI              | No ownership (orchestrates) |
| Dashboard       | Analytics Views             |

This is a very important architectural principle.

---

# Internal Request Flow

When an employee asks:

> Explain authentication.

Flow

```text
Frontend

↓

AI Service

↓

Retrieval

↓

Qdrant

Neo4j

PostgreSQL

↓

Relevant Context

↓

LLM

↓

Answer

↓

Frontend
```

---

# Background Flow

No users involved.

```text
Scheduler

↓

Connector

↓

Synchronization

↓

Processing

↓

Embedding

↓

Knowledge Graph

↓

Finished
```

---

# Error Handling Strategy

Every service returns:

```json
{
  "success": true,
  "message": "...",
  "data": {}
}
```

or

```json
{
  "success": false,
  "error": "...",
  "details": {}
}
```

This keeps APIs consistent.

---

# Logging Strategy

Every service logs:

* Start
* Success
* Failure
* Duration
* Error

This will help when we add monitoring later.

---

# Configuration Strategy

Every service reads configuration from `.env`.

Examples:

```text
DATABASE_URL=

NEO4J_URL=

QDRANT_URL=

JWT_SECRET=

LLM_PROVIDER=

SYNC_INTERVAL=
```

No secrets in source code.

---

# Final LLD Diagram

```text
                    React Frontend
                          │
                          ▼
                    FastAPI Backend
                          │
 ┌──────────────────────────────────────────────────────┐
 │ Authentication │ Users │ Dashboard │ API │ Common   │
 └──────────────────────────────────────────────────────┘
                          │
                 AI Agent Service
                          │
                  Retrieval Service
         ┌────────────────┼────────────────┐
         ▼                ▼                ▼
     PostgreSQL        Neo4j           Qdrant
                          ▲
                          │
               Knowledge Graph Service
                          ▲
                    Embedding Service
                          ▲
              Document Processing Service
                          ▲
               Synchronization Service
                          ▲
            Connector Management Service
                          ▲
                  Git / Docs / PDFs
```

---

# 🚨 Architect Review (Important)

I want to make one architectural improvement before we move on.

Earlier, we treated the **Document Processing Service** as a single large unit. As the project grows, that's likely to become the biggest and hardest-to-maintain module.

So internally, we'll design it as a **pipeline** made of smaller components:

```text
Document Processing Service
│
├── Parser
├── Cleaner
├── Metadata Extractor
├── Chunker
├── Entity Extractor
└── Relation Extractor
```

To the rest of the system, it's still one service. Internally, it's modular and easy to extend (for example, adding HTML parsing later without changing the rest of the code).

This is a common enterprise design pattern that gives us flexibility without exposing unnecessary complexity.

---

# 📊 Phase Progress

* ✅ P0.1 – Project Vision
* ✅ P0.2 – Functional Requirements
* ✅ P0.3 – Non-Functional Requirements
* ✅ P0.4 – Actors & Use Cases
* ✅ P0.5 – High-Level Design
* ✅ P0.6 – Low-Level Design

At this point, we have a complete architectural blueprint.

The next milestone, **P0.7 – Database Design**, is where we'll design the schemas for **PostgreSQL**, the node and relationship model for **Neo4j**, the collection structure for **Qdrant**, and—most importantly—how a single document flows through all three databases while remaining linked together. That cross-database design is what will make this project feel like a real enterprise AI platform rather than three disconnected databases.
