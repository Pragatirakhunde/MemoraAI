This is the master blueprint of the entire system.

After this document, we should be able to hand it to another developer, and they should understand how the entire platform works.

First, a Professional Architecture Rule

Before drawing anything, I want to establish one architecture principle that we'll follow throughout the project.

The Rule

Data should always flow in one direction.

Meaning

Source

↓

Collection

↓

Processing

↓

Storage

↓

Retrieval

↓

AI

↓

User

Never

AI

↓

Processing

↓

Storage

This keeps the architecture clean.

The System Layers

Instead of thinking about services, first think about layers.

Our architecture will have 7 layers.

Presentation Layer

↓

Application Layer

↓

Ingestion Layer

↓

Processing Layer

↓

Knowledge Layer

↓

Intelligence Layer

↓

Infrastructure Layer

Every service belongs to one layer.

Layer 1 — Presentation Layer

This is what users see.

React + TypeScript + Tailwind

Contains

Login

Employee Dashboard

Admin Dashboard

AI Chat

Knowledge Graph Viewer

Analytics

Settings

The frontend should never directly talk to databases.

Everything goes through FastAPI.

Layer 2 — Application Layer

This is our FastAPI backend.

Think of it as the brain of the application.

Responsibilities

Authentication

Authorization

Routing

Business Logic

API Endpoints

Nothing AI-related happens here.

It simply coordinates everything.

Layer 3 — Data Ingestion Layer

This layer collects knowledge.

Git Connector

Document Connector

PDF Connector

Markdown Connector

Future Connectors

Responsibilities

Locate data

Read data

Detect changes

Send files for processing

Notice

It does NOT understand AI.

Layer 4 — Knowledge Processing Layer

This is where raw files become structured knowledge.

Pipeline

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

Entity Extraction

↓

Relation Extraction

Output

Knowledge Objects
Layer 5 — Knowledge Storage Layer

Our memory.

Three databases.

PostgreSQL

Stores

Users

Metadata

Connector Configurations

Search History

Logs

Analytics
Qdrant

Stores

Embeddings

Purpose

Semantic search.

Neo4j

Stores

Relationships

Purpose

Reasoning.

Layer 6 — Intelligence Layer

This is where AI starts.

Contains

Retrieval Engine

LangGraph Agent

LLM

Retrieval

Finds

Relevant Information

Agent

Decides

Graph Search?

Vector Search?

Metadata?

Everything?

LLM

Generates

Natural Language Answer

Notice

LLM is not the center.

Retrieval is.

Layer 7 — Infrastructure Layer

Everything supporting the system.

Docker

Redis

Celery

Logging

Monitoring

Nginx
Complete High-Level Architecture

This is our official HLD.

                         EMPLOYEE / ADMIN
                                 │
                                 ▼
                ┌─────────────────────────────────┐
                │        React Frontend           │
                └─────────────────────────────────┘
                                 │
                                 ▼
                ┌─────────────────────────────────┐
                │        FastAPI Backend          │
                │ Authentication • APIs • RBAC   │
                └─────────────────────────────────┘
                                 │
               ┌─────────────────┴─────────────────┐
               │                                   │
               ▼                                   ▼
      Connector Management              Dashboard & Analytics
               │
               ▼
       Synchronization Service
      (Automatic Background Sync)
               │
               ▼
      Document Processing Pipeline
(Parser → Metadata → Chunking → Entities)
               │
      ┌────────┼───────────────┐
      ▼        ▼               ▼
 PostgreSQL  Qdrant         Neo4j
 Metadata   Embeddings   Knowledge Graph
      │        │               │
      └────────┼───────────────┘
               ▼
       Hybrid Retrieval Engine
(Vector + Graph + Metadata Search)
               │
               ▼
         LangGraph AI Agent
               │
               ▼
      Gemini / Future Llama
               │
               ▼
 Explainable Answer + References
               │
               ▼
          React Frontend
Internal Data Flow

Now let's see how information moves.

Step 1

Knowledge enters.

Git

PDF

Markdown

Wiki

↓

Connector

Step 2

Synchronization

Checks

New

Modified

Deleted
Step 3

Processing

Converts

Raw File

↓

Knowledge
Step 4

Storage

Metadata

↓

PostgreSQL

Embeddings

↓

Qdrant

Relationships

↓

Neo4j
Step 5

Question

Employee

↓

AI Question
Step 6

Retrieval

Vector

+

Graph

+

Metadata
Step 7

Agent

Combines everything.

Step 8

LLM

Produces answer.

Step 9

Frontend

Displays

Answer

References

Related Documents

Knowledge Graph
Layer Responsibilities
Layer	Responsibility
Presentation	User interaction
Application	Business logic & APIs
Ingestion	Collect organizational data
Processing	Convert raw data into structured knowledge
Storage	Persist knowledge
Intelligence	Retrieve and generate answers
Infrastructure	Support and operate the platform
One Principle Per Layer
Layer	Principle
Presentation	UI only
Backend	Orchestration only
Connector	Collection only
Processing	Transformation only
Storage	Persistence only
Retrieval	Search only
Agent	Reasoning only
LLM	Generation only

This is Separation of Concerns.

Why This Architecture Is Good

Suppose tomorrow you replace:

Gemini → Llama

Nothing changes in:

Connectors
Processing
Databases
Frontend

Suppose tomorrow you replace:

Qdrant → Weaviate

Nothing changes in:

AI Agent
UI
Authentication

That's called Loose Coupling.

Components We Intentionally Removed

Remember our early discussions?

We removed:

❌ Manual Upload Page

Instead

Automatic Synchronization

Removed

❌ Organization Registration

Instead

One Organization

Removed

❌ Multi-tenant SaaS

Instead

Future Architecture Ready

Removed

❌ LLM-centric architecture

Instead

Knowledge-centric architecture

The AI is built on top of organizational knowledge, not the other way around.

High-Level Sequence

This is how the system behaves during a normal day.

Morning
│
├── Scheduler checks Git
├── Finds 3 modified files
├── Processes only those files
├── Updates PostgreSQL
├── Updates Qdrant
├── Updates Neo4j
└── Waits

Employee logs in
│
├── Authentication
├── Opens AI Chat
├── Asks:
│     "Why was Redis introduced?"
│
├── Retrieval Engine
│
├── Qdrant
├── Neo4j
├── PostgreSQL
│
├── LangGraph Agent
│
├── Gemini
│
└── Answer + References
Architect Review (Important)

I'm going to make one significant refinement before we continue.

In our current HLD, the Synchronization Service is responsible for detecting changes and triggering the processing pipeline. As the project grows, those are two different concerns.

So I'd refine it into:

Connector Management
        │
        ▼
Synchronization Service
(Detect what changed)
        │
        ▼
Job Queue
(Create processing tasks)
        │
        ▼
Document Processing Service
(Process those tasks)

For Version 1, we don't need a full message broker like RabbitMQ. We can implement this using Celery + Redis later in Phase 8, while keeping the architecture ready from day one.

This small refinement gives us a more scalable design without adding unnecessary complexity during development.