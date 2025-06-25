# Enhanced Skill Domain Relationship (SDR) Framework

This document outlines the integration of the Enhanced Skill Domain Relationship (SDR) framework into the job expansion pipeline. The SDR framework provides a rich, contextual understanding of skills and their relationships, enabling improved job matching, career progression planning, and skill-based recommendations.

## Overview

The Enhanced SDR framework extends traditional skill extraction by:

1. **Enriching skill definitions** with detailed information about:
   - Knowledge components
   - Functional contexts
   - Proficiency levels with acquisition time estimates
   - Domain-specific applications

2. **Analyzing relationships between skills** to identify:
   - Skill dependencies
   - Complementary skills
   - Domain-specific variations

3. **Providing domain-aware skill matching** for improved job recommendations and skills analysis

## Integration with Job Pipeline

The SDR framework is integrated into the main job pipeline (`run_pipeline/core/pipeline.py`) with the following features:

### Command Line Options

| Option | Description |
|--------|-------------|
| `--use-sdr` | Enable the SDR pipeline for skill processing |
| `--sdr-use-llm` | Use LLM for higher quality skill enrichment (slower) |
| `--sdr-max-skills` | Maximum skills to analyze (default: 50) |
| `--sdr-validate` | Validate enrichment quality |
| `--sdr-test-matching` | Test domain-aware matching with sample data |
| `--sdr-apply-feedback` | Apply expert feedback to improve definitions |
| `--sdr-generate-visualizations` | Generate skill relationship visualizations |

### Example Usage

```bash
# Basic SDR pipeline run
python run_pipeline/core/pipeline.py --use-sdr

# Full SDR pipeline with all features
python run_pipeline/core/pipeline.py --use-sdr --sdr-use-llm --sdr-validate \
    --sdr-test-matching --sdr-apply-feedback --sdr-generate-visualizations

# Process specific jobs with SDR
python run_pipeline/core/pipeline.py --use-sdr --job-ids 12345,67890
```

## Job File Updates

When the SDR pipeline runs, it automatically updates each job file with enriched skill information under a new `sdr_skills` section containing:

```json
"sdr_skills": {
  "enriched": {
    "Skill Name": {
      "category": "Skill Category",
      "description": "Context and function description",
      "domains": ["Domain1", "Domain2"],
      "knowledge_components": ["Component1", "Component2"],
      "proficiency_levels": {
        "beginner": {
          "description": "Beginner level description",
          "estimated_acquisition_time": "time estimate"
        },
        "intermediate": {...},
        "advanced": {...}
      },
      "contexts": ["Context1", "Context2"],
      "functions": ["Function1", "Function2"]
    }
  },
  "relationships": {
    "Skill Name": {
      "Related Skill": {
        "relationship": "Relationship Type",
        "similarity": 0.75
      }
    }
  },
  "metadata": {
    "timestamp": "2025-05-20T19:10:11.267",
    "enriched_skill_count": 2,
    "source": "sdr_pipeline"
  }
}
```

## Output Files

The SDR pipeline generates the following output files:

1. **`docs/skill_matching/enriched_skills.json`**: Complete set of enriched skill definitions
2. **`docs/skill_matching/skill_relationships.json`**: Skill relationship classifications
3. **`docs/skill_matching/matching_results.json`**: Results of domain-aware matching tests (optional)
4. **`docs/skill_matching/enrichment_validation.json`**: Validation metrics (optional)
5. **`docs/skill_matching/visualizations/`**: Skill relationship visualizations (optional)

## Benefits

The SDR framework provides several advantages over traditional skill extraction:

1. **Deeper Skill Understanding**: Detailed knowledge components and proficiency levels
2. **Domain-Specific Context**: How skills are applied across different domains
3. **Relationship Analysis**: Understanding how skills relate to each other
4. **Improved Matching**: More accurate job to candidate skill matching
5. **Career Development**: Better understanding of skill progression paths
6. **Data-Driven Insights**: Visualizations and metrics for skill landscape analysis

## Technical Implementation

The SDR framework implementation is spread across several modules:

- `run_pipeline/skill_matching/run_enhanced_sdr.py`: Main orchestration
- `run_pipeline/skill_matching/sdr_pipeline.py`: Core pipeline implementation
- `run_pipeline/skill_matching/skill_analyzer.py`: Skill analysis and enrichment
- `run_pipeline/skill_matching/domain_relationship_classifier.py`: Relationship classification
- `run_pipeline/skill_matching/visualize_relationships.py`: Visualization generation
- `run_pipeline/skill_matching/continuous_learning.py`: Feedback integration

## Future Enhancements

Planned enhancements for the SDR framework include:

1. **Real-time skill enrichment**: Enriching skills on-demand as they are extracted
2. **User feedback loop**: Incorporating user feedback to improve skill definitions
3. **Industry-specific skill models**: Customized skill models for different industries
4. **Temporal skill analysis**: Tracking how skills evolve over time
5. **Predictive skill recommendations**: Suggesting skills to learn based on career goals
