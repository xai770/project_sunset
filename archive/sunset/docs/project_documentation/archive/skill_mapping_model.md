# Elementary Skill Decomposition Model

This document outlines a class design for implementing the elementary skill decomposition approach to matching your skills with job requirements.

## Conceptual Framework

The elementary skill decomposition approach works by breaking down complex skills into more fundamental components, facilitating indirect mapping between your experience and job requirements.

```
+-----------------+          +------------------+
| Your Experience |          | Job Requirements |
+-----------------+          +------------------+
        |                            |
        v                            v
+------------------+         +-------------------+
| Complex Skills   |         | Complex Job Reqs  |
+------------------+         +-------------------+
        |                            |
        v                            v
+------------------+         +-------------------+
| Elementary       |<------->| Elementary        |
| Skills           |  Match  | Requirements      |
+------------------+         +-------------------+
```

## Class Structure

```
+-------------------+     +-------------------+     +-------------------+
| ElementarySkill   |<----| ComplexSkill      |     | ComplexRequirement|
+-------------------+     +-------------------+     +-------------------+
| - id              |     | - id              |     | - id              |
| - name            |     | - name            |     | - name            |
| - description     |     | - description     |     | - description     |
| - domain          |     | - proficiency     |     | - importance      |
| - synonyms[]      |     | - elementarySkills|---->| - elementaryReqs  |---->+
+-------------------+     +-------------------+     +-------------------+     |
                                   ^                                          |
                                   |                                          |
+-------------------+              |              +-------------------+       |
| PersonalSkill     |--------------+              | ElementaryRequirement|<---+
+-------------------+                             +-------------------+
| - examples[]      |                             | - id              |
| - years_experience|                             | - name            |
| - demonstrations[]|                             | - description     |
+-------------------+                             | - domain          |
                                                  | - synonyms[]      |
                                                  +-------------------+
```

## Key Components

### 1. ElementarySkill
Represents a fundamental skill or knowledge area that can't be meaningfully decomposed further. Examples: "SQL", "stakeholder communication", "requirement analysis".

### 2. ComplexSkill
Represents a high-level skill from your CV that is composed of multiple elementary skills. Example: "Software License Management" is composed of ["contract analysis", "negotiation", "compliance", "vendor management"].

### 3. PersonalSkill
Extends ComplexSkill to include your personal proficiency, examples, and years of experience with this skill.

### 4. ElementaryRequirement
Similar to ElementarySkill, but represents a fundamental requirement from a job description.

### 5. ComplexRequirement
Represents a high-level requirement from a job description, composed of multiple elementary requirements.

## Mapping Process

The skill mapping algorithm would:

1. **Decompose your skills** into elementary components
2. **Decompose job requirements** into elementary components
3. **Create a similarity matrix** between elementary skills and requirements
   - Using exact matches
   - Using synonym matching
   - Using semantic similarity (via embeddings)
4. **Calculate match scores** for each complex skill to complex requirement
5. **Rank matches** by strength and relevance
6. **Generate recommendations** for which experiences to highlight

## Example

```json
{
  "personalSkill": {
    "id": "software_license_mgmt",
    "name": "Software License Management",
    "description": "Managing software licensing across enterprise environments",
    "proficiency": "Expert",
    "years_experience": 12,
    "elementarySkills": [
      "contract_analysis",
      "vendor_management",
      "compliance_monitoring",
      "negotiation",
      "asset_tracking"
    ],
    "examples": [
      "Managed software compliance challenges from first contact to settlement"
    ]
  },
  
  "jobRequirement": {
    "id": "vendor_governance",
    "name": "Vendor Governance",
    "description": "Managing vendor relationships and ensuring contractual compliance",
    "importance": "Essential",
    "elementaryRequirements": [
      "relationship_management",
      "contract_analysis",
      "performance_monitoring",
      "risk_assessment",
      "negotiation"
    ]
  },
  
  "matches": [
    {"elementary": "contract_analysis", "strength": 1.0},
    {"elementary": "negotiation", "strength": 1.0},
    {"elementary": "vendor_management", "similarity": "relationship_management", "strength": 0.8}
  ],
  
  "matchScore": 0.6,  // 3 matches out of 5 requirements
  "relevanceScore": 0.75  // Weighted by importance of matched elements
}
```

## Next Steps for Implementation

1. **Create an ontology** of elementary skills organized by domain
2. **Define decomposition rules** for complex skills
3. **Build a matching engine** to compare skill sets
4. **Develop a recommendation system** that suggests which experiences to highlight
5. **Integrate with content generation** to create targeted cover letter sections

This approach provides a systematic way to discover non-obvious connections between our experience and job requirements, enabling more targeted and effective cover letters.
