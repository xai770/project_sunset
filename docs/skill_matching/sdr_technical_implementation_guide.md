# SDR Framework Technical Implementation Guide

## Overview

The Skill Domain Relationship (SDR) Framework is a comprehensive solution for standardizing skill definitions, identifying skill relationships, and improving skill matching by considering domain contexts. This technical guide provides details on the implementation of the enhanced SDR framework based on OLMo2 recommendations.

## Architecture

The SDR framework consists of the following key components:

1. **Skill Analyzer**: Extracts, analyzes, and ranks skills from job postings and CVs, then enriches them with domain-specific information.
2. **Domain Relationship Classifier**: Identifies relationships between skills based on domain components.
3. **Domain-Aware Matcher**: Matches job requirements to candidate skills considering domain relationships.
4. **Skill Validation System**: Validates the quality and completeness of skill definitions.
5. **Continuous Learning System**: Incorporates expert feedback and improves skill definitions over time.
6. **Visualization Tools**: Provides visual insights into skill relationships across domains.

### Component Interaction Diagram

```
                                   +-------------------+
                                   |                   |
                                   | Expert Feedback   |
                                   |                   |
                                   +--------+----------+
                                            |
                                            v
+---------------+        +-----------------+        +-------------------+
|               |        |                 |        |                   |
| Skill Analyzer+------->+ Domain Relation +------->+ Domain-Aware      |
|               |        | Classifier      |        | Matcher           |
+-------+-------+        +-----------------+        +-------------------+
        |                                                    |
        v                                                    v
+-------+-------+        +-----------------+        +-------------------+
|               |        |                 |        |                   |
| Continuous    +<-------+ Skill Validation+<-------+ Matching Results  |
| Learning      |        | System          |        |                   |
+-------+-------+        +-----------------+        +-------------------+
        |
        v
+-------+-------+
|               |
| Visualization |
| Tools         |
|               |
+---------------+
```

## Implementation Details

### 1. Skill Analyzer

The Skill Analyzer extracts and analyzes skills from job postings and CVs, calculating their frequency, ambiguity, and impact. It then selects high-priority skills for enrichment, which can be done using either placeholder data or LLM-based enrichment via OLMo2.

**Key Methods:**
- `load_job_skills()`: Loads skills from job postings
- `load_cv_skills()`: Loads skills from CVs
- `calculate_ambiguity_factors()`: Calculates ambiguity for each skill
- `calculate_impact_scores()`: Calculates impact scores based on frequency and ambiguity
- `select_top_skills()`: Selects high-priority skills for enrichment
- `create_enriched_skill_definition()`: Enriches a skill definition

### 2. Domain Relationship Classifier

The Domain Relationship Classifier calculates similarity between skills based on their knowledge components, contexts, and functions. It then classifies relationships based on similarity thresholds.

**Relationship Types:**
- Exact Match: Very high similarity (≥ 0.9)
- Subset: High similarity within the same domain, with fewer components
- Superset: High similarity within the same domain, with more components
- Neighboring: Moderate similarity within the same domain
- Hybrid: Moderate similarity across different domains
- Unrelated: Low similarity

**Key Methods:**
- `calculate_jaccard_similarity()`: Calculates Jaccard similarity between component sets
- `calculate_domain_similarity()`: Calculates weighted similarity across component types
- `classify_relationship()`: Determines the relationship between two skills
- `classify_relationships()`: Processes all skill pairs to build a relationship matrix

### 3. Domain-Aware Matcher

The Domain-Aware Matcher improves skill matching by considering domain relationships rather than just keyword matches. This reduces false positives in skill matching.

**Key Methods:**
- `calculate_match_score()`: Calculates a match score between job skill and candidate skill
- `check_domain_match()`: Checks if skills are in the same domain
- `check_relationship_match()`: Checks for a relationship in the matrix
- `check_component_overlap()`: Checks for overlapping knowledge components

### 4. Skill Validation System

The Skill Validation System checks the quality and completeness of skill definitions, identifying issues and suggesting improvements.

**Validation Criteria:**
- Completeness: All required fields are present
- Consistency: Terms are used consistently across similar skills
- Specificity: Definitions are specific rather than generic
- Domain Alignment: Components align with the skill's domain

**Key Methods:**
- `validate_skills()`: Validates a set of skill definitions
- `check_completeness()`: Ensures all required fields are present
- `check_consistency()`: Checks for consistency across definitions
- `generate_quality_report()`: Creates a comprehensive quality report

### 5. Continuous Learning System

The Continuous Learning System incorporates expert feedback to improve skill definitions over time, ensuring they remain accurate and relevant.

**Key Methods:**
- `load_expert_feedback()`: Loads feedback from expert reviewers
- `apply_expert_feedback()`: Updates skill definitions based on feedback
- `calculate_quality_scores()`: Calculates quality scores for skill definitions
- `check_consistency()`: Identifies consistency issues across definitions

### 6. Visualization Tools

The Visualization Tools provide insights into skill relationships through various graph types, helping identify patterns and connections across domains.

**Visualization Types:**
- Network Graph: Shows connections between skills
- Domain Heatmap: Shows relationship density between domains
- Chord Diagram: Shows relationships across domains

**Key Methods:**
- `create_relationship_graph()`: Creates a NetworkX graph of relationships
- `visualize_network_graph()`: Visualizes the network of skills
- `visualize_domain_heatmap()`: Creates a heatmap of domain relationships
- `visualize_relationship_chord_diagram()`: Creates a chord diagram

## Enhanced Skill Definition Structure

Based on OLMo2 recommendations, the enhanced skill definition includes:

```json
{
  "name": "Basic Process Automation",
  "category": "IT_Technical",
  "proficiency_levels": {
    "beginner": {
      "description": "Can automate simple, repetitive tasks with guidance",
      "estimated_acquisition_time": "1-2 months"
    },
    "intermediate": {
      "description": "Can design and implement automated workflows independently",
      "estimated_acquisition_time": "3-6 months" 
    },
    "advanced": {
      "description": "Can create complex enterprise automation solutions and optimize existing processes",
      "estimated_acquisition_time": "1-2 years"
    }
  },
  "knowledge_components": ["workflow_analysis", "scripting", "process_improvement"],
  "contexts": ["office", "business_process"],
  "functions": ["efficiency_improvement", "task_simplification"],
  "related_skills": [
    {
      "skill_name": "Scripting",
      "relationship_type": "prerequisite"
    },
    {
      "skill_name": "Business Process Management",
      "relationship_type": "complementary"
    }
  ],
  "industry_variants": {
    "finance": "Focus on regulatory compliance and data security",
    "healthcare": "Focus on patient data workflows and HIPAA compliance",
    "manufacturing": "Focus on production and supply chain automation"
  },
  "trend_indicator": "growing",
  "tools": ["UiPath", "Power Automate", "Python", "Bash scripting"],
  "measurable_outcomes": ["Number of processes automated", "Time saved per week", "Error reduction percentage"]
}
```

## LLM-Based Enrichment Pipeline

The LLM-based enrichment pipeline follows OLMo2's recommendations for a multi-stage approach:

1. **Stage 1: Core Definition Generation**
   - Use OLMo2 to generate core skill components
   - Define basic knowledge components, contexts, and functions

2. **Stage 2: Domain-Specific Enrichment**
   - Use CodeGemma for technical skills
   - Use Qwen3 for leadership and soft skills
   - Use standard models for other domains

3. **Stage 3: Cross-Industry Information**
   - Add industry variants
   - Add trend indicators
   - Add tool associations

4. **Stage 4: Validation and Finalization**
   - Ensure completeness of all required fields
   - Check consistency and quality
   - Apply expert feedback if available

## Continuous Learning Process

The continuous learning process follows these steps:

1. **Feedback Collection**
   - Expert reviews of skill definitions
   - Quality assessments and ratings
   - Suggested corrections and improvements

2. **Feedback Processing**
   - Load and organize feedback
   - Identify common issues
   - Prioritize corrections

3. **Definition Improvement**
   - Apply corrections to skill components
   - Enhance incomplete definitions
   - Update relationships based on feedback

4. **Quality Assessment**
   - Calculate updated quality scores
   - Check consistency across definitions
   - Generate quality reports

5. **Visualization**
   - Generate updated visualizations
   - Highlight improvements and changes
   - Identify patterns in relationship updates

## Usage Instructions

### Running the Enhanced SDR Implementation

```bash
python run_pipeline/skill_matching/run_enhanced_sdr.py [options]
```

Options:
- `--use-llm`: Use LLM for skill enrichment
- `--max-skills`: Maximum number of skills to analyze
- `--skip-validation`: Skip validation of enriched skills
- `--test-matching`: Test domain-aware matching
- `--load-existing`: Load existing enriched skills
- `--apply-feedback`: Apply expert feedback
- `--generate-visualizations`: Generate visualizations

### Running the Continuous Learning System

```bash
python run_pipeline/skill_matching/sdr_continuous_learning.py [options]
```

Options:
- `--skills`: Path to enriched skills file
- `--relationships`: Path to relationships file
- `--no-save`: Do not save updated definitions
- `--no-report`: Do not generate quality report
- `--no-visualizations`: Do not create visualizations

### Testing the Framework

```bash
python run_pipeline/skill_matching/test_enhanced_sdr.py [options]
```

Options:
- `--component`: Component to test (all, analyzer, classifier, matcher, validation)
- `--use-llm`: Use LLM for testing
- `--max-skills`: Maximum skills for testing

For continuous learning tests:
```bash
python run_pipeline/skill_matching/test_continuous_learning.py [options]
```

Options:
- `--component`: Component to test (all, cl_system, integration)

## Best Practices for Extension

1. **Custom Enrichment Models**
   - Implement custom LLM client classes
   - Define specialized prompts for different skill types
   - Ensure consistent JSON output format

2. **Additional Validation Rules**
   - Create new validation methods in SkillValidationSystem
   - Define new quality metrics
   - Implement automated consistency checks

3. **New Visualization Types**
   - Add methods to SkillRelationshipVisualizer
   - Ensure proper data preparation
   - Include legends and explanatory text

4. **Domain-Specific Extensions**
   - Create domain-specific enrichment templates
   - Define domain-specific validation rules
   - Implement specialized relationship classifications

5. **Continuous Learning Enhancements**
   - Implement feedback prioritization logic
   - Create feedback collection interfaces
   - Develop automated quality improvement suggestions
