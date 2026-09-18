# Neo4j Knowledge Graph Design

## Node Types

### Organization
Represents the organization.

Properties:
- id
- name
- slug

### Employee
Represents an employee.

Properties:
- id
- name
- role
- organization_id

### Project
Represents an organizational project.

Properties:
- key
- name
- organization_id

### Module
Represents a project module/service.

Properties:
- key
- name
- organization_id

### API
Represents an API or endpoint.

Properties:
- key
- name
- method
- path
- organization_id

### Technology
Represents a technology used by the organization.

Properties:
- name
- organization_id

### Database
Represents a database technology/system.

Properties:
- name
- organization_id

### Document
Represents an ingested organizational document.

Properties:
- id
- title
- file_path
- organization_id

### Meeting
Represents an organizational meeting.

Properties:
- id
- title
- organization_id

### Decision
Represents an architecture/business decision.

Properties:
- id
- title
- organization_id

## Relationships

- Employee -[:WORKED_ON]-> Project
- Project -[:HAS_MODULE]-> Module
- Project -[:USES]-> Technology
- Project -[:USES_DATABASE]-> Database
- Module -[:CALLS]-> API
- Document -[:DOCUMENTS]-> Project
- Document -[:DOCUMENTS]-> Module
- Document -[:MENTIONS]-> Technology
- Meeting -[:DISCUSSES]-> Project
- Decision -[:RELATES_TO]-> Project
- Decision -[:DOCUMENTED_IN]-> Document