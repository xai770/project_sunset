# Enhanced Skill Domain Relationship (SDR) Framework

*Based on OLMo2 Recommendations*

## Overview

The Enhanced SDR Framework is a comprehensive solution for skill enrichment, domain relationship classification, and domain-aware matching. It implements the recommendations provided by OLMo2 to create more meaningful skill definitions with domain-specific terminology and better skill relationship classification to improve skill matching.

## Key Components

### 1. Skill Analyzer

The Skill Analyzer component is responsible for:
- Analyzing skills from job postings and CVs
- Calculating ambiguity factors and impact scores
- Selecting high-priority skills for standardization
- Creating enriched skill definitions with domain-specific components
- Using LLMs (specifically OLMo2) for high-quality skill enrichment

### 2. Domain Relationship Classifier

The Domain Relationship Classifier categorizes relationships between skills based on:
- Knowledge component similarity
- Context similarity
- Function similarity
- Domain categorization

Relationship types include:
- Exact Match
- Subset
- Superset
- Neighboring
- Hybrid
- Unrelated

### 3. Domain-Aware Matching Algorithm

The Domain-Aware Matching Algorithm improves skill matching by:
- Using domain context to avoid false positives
- Considering relationships between skills
- Applying knowledge component overlap detection
- Providing match explanations for better transparency

### 4. Continuous Learning System

The Continuous Learning System enhances the framework through:
- Expert feedback incorporation
- Quality scoring of skill definitions
- Consistency checking across skill definitions
- Iterative improvement of skill definitions

### 5. Visualization Tools

The visualization component provides insights through:
- Network graphs of skill relationships
- Domain relationship heatmaps
- Chord diagrams for cross-domain relationships

## Enhanced Skill Definition Structure

Based on OLMo2 recommendations, the enhanced skill definitions include:

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

## Usage

### Running the Enhanced SDR Implementation

```bash
python run_pipeline/skill_matching/run_enhanced_sdr.py [options]
```

Options:
- `--use-llm`: Use LLM for skill enrichment (higher quality but slower)
- `--max-skills`: Maximum number of skills to analyze (default: 50)
- `--skip-validation`: Skip validation of enriched skills
- `--test-matching`: Test domain-aware matching with sample data
- `--load-existing`: Load existing enriched skills instead of generating new ones
- `--apply-feedback`: Apply expert feedback to improve skill definitions
- `--generate-visualizations`: Generate visualizations for skill relationships

### Testing the Enhanced SDR Implementation

```bash
python run_pipeline/skill_matching/test_enhanced_sdr.py [options]
```

Options:
- `--use-llm`: Use LLM for skill enrichment in tests
- `--max-skills`: Maximum number of skills to analyze in tests (default: 5)
- `--component`: Specific component to test (all, analyzer, classifier, matcher, validation)

### Visualizing Skill Relationships

```bash
python run_pipeline/skill_matching/visualize_relationships.py [options]
```

Options:
- `--all`: Generate all available visualizations
- `--network`: Generate network graph visualization
- `--heatmap`: Generate domain relationship heatmap
- `--chord`: Generate chord diagram (requires holoviews)

## Implementation Process

The enhanced SDR implementation follows a multi-stage pipeline:

1. **Data Collection**: Gather skills from job postings and CVs
2. **Analysis and Selection**: Identify high-priority skills based on impact score
3. **Skill Enrichment**: Generate comprehensive definitions with OLMo2
4. **Relationship Classification**: Determine connections between skills
5. **Quality Assessment**: Validate definitions with consistency checks
6. **Continuous Learning**: Incorporate expert feedback and improve definitions
7. **Visualization**: Generate insights through graphical representations

## Benefits

- Reduced false positives in skill matching
- More comprehensive skill definitions
- Domain-aware relationship classification
- Consistency across skill domains
- Visual insights into skill relationships
- Iterative improvement through continuous learning
- Enhanced understanding of skill transferability

## Future Enhancements

- Integration with job recommendation systems
- Personalized learning path generation
- Industry-specific skill libraries
- Time-based skill trend analysis
- Skills gap analysis for organizations
- Automated skill extraction from resumes and job descriptions

## References

- OLMo2 SDR Recommendations (2025)
- Skill Taxonomy Best Practices
- Domain-Aware Matching Algorithms Literature Review
