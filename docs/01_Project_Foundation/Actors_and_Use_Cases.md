1. System Context

Let's first define what is inside our system and what is outside.

                  OUTSIDE THE SYSTEM

  Git Repository
  Documentation
  PDFs
  Meeting Notes
  Wiki
  API Docs

           │
           ▼

-----------------------------------------------
 Enterprise Knowledge Graph &
 Organizational Memory Platform
-----------------------------------------------

           ▲
           │

        Employee
        Admin

Everything outside provides knowledge.

Everything inside processes knowledge.

2. Identify Actors

An actor is anything that interacts with the system.

For Version 1 we have 4 actors.

Actor 1 — Administrator

This is the person who configures and manages the platform.

Responsibilities:

Login
Configure connectors
Add users
Remove users
Monitor synchronization
View analytics
Check logs
Trigger manual synchronization

Admin is not responsible for asking AI questions daily.

Actor 2 — Employee

This is the primary user.

Responsibilities:

Login
Ask AI questions
View references
Search documentation
Explore Knowledge Graph
View conversation history

Employee never changes system settings.

Actor 3 — Scheduler (System Actor)

This isn't a human.

It's an automated background process.

Responsibilities:

Run every few minutes
Check connected sources
Detect changes
Trigger processing pipeline
Update databases

The Scheduler is invisible to users.

Actor 4 — External Data Sources

These are systems connected to our platform.

Examples:

Git Repository

Documentation Folder

Meeting Notes

PDFs

Markdown Files

These systems never call the AI.

They only provide knowledge.

Actor Summary
Actor	Type	Purpose
Admin	Human	Manage the platform
Employee	Human	Consume knowledge
Scheduler	System	Automate updates
Data Sources	External System	Provide organizational data
3. Use Cases

Now we define everything users can do.

UC-1 User Login

Actor:

Employee/Admin

Flow

User

↓

Login Page

↓

Enter Credentials

↓

Authentication Service

↓

JWT Generated

↓

Dashboard

Success:

User reaches dashboard.

Failure:

Invalid credentials.

UC-2 Configure Connectors

Actor

Admin

Flow

Admin

↓

Settings

↓

Add Repository

↓

Validate

↓

Save

↓

Ready for Sync

Result

System knows where organizational knowledge is stored.

UC-3 Automatic Synchronization

Actor

Scheduler

Flow

Every 10 Minutes

↓

Check Git

↓

New Commit?

↓

Yes

↓

Processing Pipeline

No user interaction.

UC-4 Process Documents

Actor

Synchronization Service

Flow

Changed File

↓

Parser

↓

Metadata

↓

Chunking

↓

Entity Extraction

↓

Embedding

↓

Storage
UC-5 Ask AI Question

Actor

Employee

Flow

Employee

↓

Ask Question

↓

AI Agent

↓

Retrieval

↓

LLM

↓

Answer

↓

References

This is the primary use case.

UC-6 Search Knowledge

Actor

Employee

Flow

Employee

↓

Search

↓

Retrieval Service

↓

Matching Documents

No AI generation required.

UC-7 View Knowledge Graph

Actor

Employee

Flow

Employee

↓

Graph Viewer

↓

Neo4j

↓

Relationships

↓

Visualization
UC-8 Monitor Synchronization

Actor

Admin

Flow

Admin

↓

Dashboard

↓

Synchronization Status

↓

Connector Health

↓

Logs
UC-9 Manage Users

Actor

Admin

Flow

Admin

↓

Users

↓

Create

↓

Update

↓

Deactivate
UC-10 View Analytics

Actor

Admin

Flow

Dashboard

↓

Statistics

↓

Search Trends

↓

Document Count

↓

System Health
4. Main Business Workflow

This is the heart of the system.

Admin

↓

Configure Connectors

↓

Scheduler Starts

↓

Detect Changes

↓

Process Files

↓

Generate Embeddings

↓

Update Knowledge Graph

↓

Employee Logs In

↓

Ask Question

↓

AI Retrieves Knowledge

↓

Generate Answer

↓

Show References

Everything revolves around this workflow.

5. Daily Operational Workflow

This is what happens every day.

08:00

Employee Login

↓

Ask Question

↓

Receive Answer

--------------------------

Meanwhile

Scheduler

↓

Git Changed?

↓

Update Knowledge

↓

Employee Never Notices

This is exactly how enterprise software behaves.

6. Use Case Relationships
Employee

│

├── Login

├── Ask Question

├── Search

├── View Sources

└── View Knowledge Graph



Admin

│

├── Login

├── Configure Connectors

├── Manage Users

├── Trigger Sync

├── View Analytics

└── Monitor Logs



Scheduler

│

├── Detect Changes

├── Process Files

└── Update Knowledge
7. Exception Scenarios

Good architects think about failures too.

Git Repository Unavailable

Expected behavior:

Log error
Retry later
Continue processing other sources
PDF Parsing Failure

Expected behavior:

Skip corrupted file
Log issue
Continue remaining pipeline
LLM Unavailable

Expected behavior:

Return retrieval results
Show friendly error
Do not crash system
No Relevant Knowledge Found

Expected behavior:

"I couldn't find enough organizational knowledge
to answer this question."

Not a hallucinated answer.

8. Permissions Matrix
Feature	Admin	Employee
Login	✅	✅
Ask AI Questions	✅	✅
Search Knowledge	✅	✅
View Knowledge Graph	✅	✅
Configure Connectors	✅	❌
Manage Users	✅	❌
Trigger Synchronization	✅	❌
View Analytics	✅	Limited
View Logs	✅	❌
9. Use Case Priority
Must Have (Version 1)
Login
Configure Connectors
Automatic Synchronization
Processing Pipeline
AI Questions
Hybrid Retrieval
Dashboard
Nice to Have
Conversation History
Saved Searches
Advanced Graph Explorer
Future
Voice Queries
Slack Bot
Teams Integration
Jira Assistant
10. Final Use Case Diagram (Text)
                     Administrator
                           │
      ┌────────────────────┼────────────────────┐
      │                    │                    │
      ▼                    ▼                    ▼
 Configure Sources     Manage Users     Monitor System
      │                    │                    │
      └────────────────────┴───────────────┐
                                            │
                                            ▼
              Enterprise Knowledge Platform
                                            ▲
                                            │
      ┌────────────────────┬────────────────┘
      │                    │
      ▼                    ▼
 Ask AI Questions    Search Knowledge
      │                    │
      └──────────────┬─────┘
                     ▼
                  Employee


        External Sources ─────► Synchronization
                                   │
                                   ▼
                           Knowledge Update
🎯 Architect Review

This document is in good shape, but I want to make one important improvement before we move on.

Earlier, we introduced 10 logical services. We should start mapping every use case to the service responsible for it. For example:

Use Case	Primary Service
Login	Authentication Service
Configure Connectors	Connector Management Service
Automatic Synchronization	Synchronization Service
Process Documents	Document Processing Service
Ask AI Question	AI Agent + Retrieval Service
View Knowledge Graph	Knowledge Graph Service
View Analytics	Dashboard & Analytics Service

This mapping will make the next phases (High-Level and Low-Level Design) much easier because we'll already know which service owns which functionality.