What are Non-Functional Requirements?

If Functional Requirements answer:

"What should the system do?"

Then Non-Functional Requirements answer:

"How well should the system do it?"

Example

Functional Requirement:

The system shall answer user questions.

Non-Functional Requirement:

The system shall answer user questions within 5 seconds for a knowledge base of up to 10,000 indexed documents.

See the difference?

Why are NFRs important?

Imagine two systems.

Both answer questions.

System A

Takes 30 seconds
Crashes often
Gives random answers
Hard to maintain

System B

Answers in 3 seconds
Stable
Modular
Secure

Both satisfy the functional requirement.

Only one is enterprise-ready.

Our NFR Categories

We'll define 12 categories.

NFR-1 Performance
NFR-2 Scalability
NFR-3 Reliability
NFR-4 Security
NFR-5 Maintainability
NFR-6 Modularity
NFR-7 Availability
NFR-8 Usability
NFR-9 Observability
NFR-10 Data Quality
NFR-11 AI Quality
NFR-12 Deployment
NFR-1 Performance

The system should feel responsive.

Requirements
NFR-1.1

Average AI response time should be

≤ 5 seconds

for a normal query.

NFR-1.2

Connector synchronization shall process only changed files.

Not the whole repository.

NFR-1.3

System shall support incremental indexing.

NFR-1.4

Knowledge retrieval should complete before LLM generation.

Meaning

Retrieve

↓

Then

↓

Generate

Never the opposite.

NFR-1.5

Background synchronization should not interrupt users.

NFR-2 Scalability

Although Version 1 supports one organization,

architecture should support future growth.

NFR-2.1

Support multiple repositories.

NFR-2.2

Support multiple document folders.

NFR-2.3

Support future connector additions.

Example

Git

↓

GitHub

↓

Jira

↓

Slack

without redesign.

NFR-2.4

Every service should be independently replaceable.

NFR-3 Reliability

The platform should not lose knowledge.

NFR-3.1

Failed synchronization should not corrupt existing knowledge.

NFR-3.2

System should retry temporary failures.

NFR-3.3

Partial failures should not stop the entire pipeline.

Example

PDF parser fails.

Git processing continues.

NFR-3.4

Knowledge should remain searchable even during synchronization.

NFR-4 Security

Enterprise software must be secure.

NFR-4.1

JWT authentication.

NFR-4.2

Passwords shall be hashed.

Never stored in plain text.

NFR-4.3

Admin and Employee permissions shall be separated.

NFR-4.4

Only authorized users can access organizational knowledge.

NFR-4.5

Sensitive configuration values shall be stored in environment variables.

Not inside source code.

NFR-5 Maintainability

Future developers should understand the project.

NFR-5.1

Every module should have one responsibility.

NFR-5.2

Business logic should be separated from APIs.

NFR-5.3

Reusable services should be preferred.

NFR-5.4

Documentation shall be maintained.

NFR-5.5

Meaningful logging shall be implemented.

NFR-6 Modularity

One of our biggest design principles.

NFR-6.1

LLM should be replaceable.

Example

Gemini

↓

Llama

↓

OpenAI

without major changes.

NFR-6.2

Vector database should be replaceable.

NFR-6.3

Connector implementations should be independent.

NFR-6.4

Document parsers should be independent.

NFR-6.5

Services should communicate through interfaces rather than direct dependencies where practical.

NFR-7 Availability

The system should continue working.

NFR-7.1

Background tasks shall not block users.

NFR-7.2

Search should remain available during synchronization.

NFR-7.3

System startup should automatically initialize required services.

NFR-8 Usability

Remember

Employees are not AI engineers.

NFR-8.1

Simple interface.

NFR-8.2

Minimal configuration.

NFR-8.3

Natural language interaction.

NFR-8.4

Referenced documents should be easy to access.

NFR-8.5

Error messages should clearly explain problems.

NFR-9 Observability

Very important.

NFR-9.1

Synchronization logs.

NFR-9.2

Connector logs.

NFR-9.3

AI query logs.

NFR-9.4

System health monitoring.

NFR-9.5

Dashboard statistics.

NFR-10 Data Quality

Garbage in.

Garbage out.

NFR-10.1

Duplicate documents should be avoided.

NFR-10.2

Metadata should remain consistent.

NFR-10.3

Synchronization should preserve document versions.

(For Version 1, we can simplify this to tracking the latest processed version or timestamp rather than implementing full document version history.)

NFR-10.4

Knowledge Graph relationships should remain consistent.

NFR-11 AI Quality

This is unique to AI systems.

NFR-11.1

LLM should answer only using retrieved organizational knowledge.

No unsupported assumptions.

NFR-11.2

Answers should include references.

NFR-11.3

AI should acknowledge when information is unavailable.

NFR-11.4

Retrieved context should be ranked before generation.

NFR-11.5

Knowledge Graph should improve retrieval quality.

NFR-12 Deployment
NFR-12.1

Entire system should run using Docker Compose.

NFR-12.2

Configuration should use .env.

NFR-12.3

Deployment should support local development.

NFR-12.4

Persistent data should survive container restart.

Quality Attribute Matrix
Attribute	Target
Response Time	≤ 5 seconds for typical queries
Authentication	JWT
Password Storage	Hashed
Background Processing	Non-blocking
Search	Hybrid (Vector + Graph + Metadata)
Deployment	Docker Compose
Configuration	Environment Variables
Logging	Structured
Scalability	Modular Architecture
AI	Explainable Answers
Maintainability	Single Responsibility
Extensibility	Replaceable Components
Engineering Principles (Our Rules)

These are not just NFRs—they're the design philosophy we'll follow.

Automation over manual work.
Single Responsibility Principle.
Loose coupling and replaceable components.
Explainability before intelligence.
Ground answers in retrieved knowledge.
Design for future expansion without building it today.
Fail gracefully whenever possible.
Build observability into the system from the start.
Mapping NFRs to Architecture
Service	Most Important NFRs
Authentication	Security, Reliability
Connector Management	Scalability, Reliability
Synchronization	Performance, Availability
Document Processing	Data Quality, Maintainability
Embedding Service	Modularity, Performance
Knowledge Graph Service	Data Quality, Scalability
Retrieval Service	Performance, AI Quality
AI Agent Service	AI Quality, Explainability
Dashboard	Usability, Observability
Logging	Observability, Reliability

This helps ensure every service is designed with the right quality goals in mind.