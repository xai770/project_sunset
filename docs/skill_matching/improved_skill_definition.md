# Final Skill Definition Standardization Framework

## Core Principles

1. **Consistency**: Use standardized keywords and phrases across all skill definitions
2. **Hierarchy**: Implement clear skill levels (Base, Intermediate, Advanced)
3. **Specificity**: Prefer specific skill definitions over generic terms
4. **Component-Based**: Classify skills by knowledge, context, and function
5. **Domain-Aware**: Consider skill relationships across domains to reduce false positives

## Standardized Structure

### Terminology Standards
- Maintain consistent verb forms (e.g., "Developing" not "Development")
- Use established naming patterns (e.g., "[Technology] Development")
- Define clear boundaries between related skills

### Hierarchical Classification
- **Level 1 (Base)**: Foundational knowledge and basic application
  - Example: "SQL Basics" - Simple queries, understanding tables
  - Indicators: "Basic understanding", "Fundamental concepts", "Entry-level proficiency"
- **Level 2 (Intermediate)**: Practical application in standard situations
  - Example: "SQL Development" - Complex queries, joins, procedures
  - Indicators: "Working knowledge", "Practical application", "Independent performance"
- **Level 3 (Advanced)**: Expert application, optimization, innovation
  - Example: "SQL Performance Optimization" - Query tuning, indexing
  - Indicators: "Expert-level", "Strategic implementation", "Leadership capability"

### Specificity Requirements
- Replace generic terms with specific skills:
  - "Programming" → "Java Development", "Python Scripting"
  - "Communication" → "Technical Documentation", "Executive Presentation"
  - "Analysis" → "Business Process Analysis", "Requirements Analysis"
- Add qualifiers when needed (e.g., "Cloud Architecture, AWS")

### Skill Requirement Classification
- **Required Skills**: Essential for job performance; absence would significantly impair ability to perform role
  - Identified by terms like "must have", "required", "essential"
  - Example: "Required: Experience with SQL database design"
- **Desired Skills**: Beneficial but not essential; enhances performance but absence doesn't prevent basic job functions
  - Identified by terms like "preferred", "desired", "nice to have"
  - Example: "Preferred: Experience with PostgreSQL performance tuning"

## Component Classification

### Knowledge Components
- Definition: Theoretical understanding or factual information
- Examples: "Understanding of database normalization", "Knowledge of ITIL"

### Context Components
- Definition: Environments or situations where skills are applied
- Examples: "Enterprise software development", "Financial services environment"

### Function Components
- Definition: Practical application of knowledge
- Examples: "Developing software applications", "Analyzing business requirements"

## Implementation Format

```json
{
  "name": "Basic Process Automation",
  "category": "IT_Technical",
  "level": 2,
  "requirement_type": "required",
  "knowledge_components": ["workflow_analysis", "scripting"],
  "contexts": ["office", "business_process"],
  "functions": ["efficiency_improvement", "task_simplification"],
  "ambiguity_factor": 4.5,  // Optional: Score from 1-10 indicating potential for misclassification
  "related_skills": [       // Optional: Skills with meaningful relationships
    {
      "skill_name": "Workflow Optimization",
      "relationship_type": "Neighboring",
      "similarity_score": 0.65
    }
  ]
}
```

## Example Implementations

```json
{
  "name": "IT troubleshooting",
  "category": "Technology",
  "level": 2,
  "requirement_type": "required",
  "knowledge_components": ["common_computer_problems", "basic_network_concepts"],
  "contexts": ["remote_support", "personal_computer"],
  "functions": ["diagnose_problem", "suggest_solutions"]
}

{
  "name": "Healthcare appointment scheduling",
  "category": "Healthcare",
  "level": 2,
  "requirement_type": "desired",
  "knowledge_components": ["common_health_services", "available_doctors"],
  "contexts": ["in_person_conversation", "telehealth_session"],
  "functions": ["suggest_appointment_time", "confirm_schedule"]
}

{
  "name": "Personal finance management",
  "category": "Finance",
  "level": 2,
  "requirement_type": "required",
  "knowledge_components": ["budget_calculation", "monthly_expenses"],
  "contexts": ["daily_usage", "yearly_financial_plan"],
  "functions": ["suggest_budget", "track_expenses"]
}
```

These examples illustrate how skills can be standardized across different domains with specific attributes tailored to common tasks within those domains. Each skill is clearly defined with levels indicating its complexity, requirement type showing its importance, knowledge components highlighting the foundational information required, contexts specifying when each skill might be used, and functions outlining the specific tasks that can be performed.
