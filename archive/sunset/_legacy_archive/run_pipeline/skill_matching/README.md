# Skill Domain Relationship (SDR) Framework

This module provides advanced skill matching for job and CV analysis in Project Sunset. It standardizes skill definitions, classifies domain relationships, and enables more accurate, context-aware matching between job requirements and candidate profiles.

## Intended Workflow

1. **Skill Extraction & Enrichment**
   - Extracts skills from job postings and CVs using LLMs (e.g., Ollama).
   - Enriches each skill with metadata: category (technical, domain, social, etc.), knowledge components, proficiency levels, and context.

2. **Domain Relationship Classification**
   - Builds a relationship matrix between skills (e.g., exact match, subset, superset, neighboring, unrelated) using semantic similarity and domain knowledge.
   - Classifies relationships to reduce false positives in matching.

3. **Skill Bucketing**
   - Groups skills into broad, meaningful buckets (e.g., technical, domain, social) based on their category.
   - Summarizes each job and CV by these buckets for efficient comparison.

4. **Domain-Aware Matching**
   - Compares skill buckets between jobs and CVs, focusing on overlap within each category.
   - Uses LLMs to assess domain overlap and relevance, rather than comparing every skill individually.
   - Produces a match score and interpretable summary for each job-CV pair.

5. **Output & Integration**
   - Stores enriched skills and relationship data in job JSONs for traceability.
   - Generates summary structures (skill buckets) for fast, efficient matching.
   - Designed for integration into the main pipeline for daily automated execution.

## Usage

Run the full SDR implementation with:

```bash
cd /home/xai/Documents/sunset
bash ./run_pipeline/skill_matching/run_sdr.sh
```

## Output Files

- `enriched_skills.json`: Standardized skill definitions with metadata.
- `skill_relationships.json`: Relationship matrix between analyzed skills.
- `matching_test_results.json`: Results of test comparisons using the matching algorithm.
- `sdr_implementation_results.json`: Summary of the implementation process.

## Next Steps

- Enhance skill enrichment with more meaningful LLM-generated metadata.
- Integrate LLMs for advanced semantic analysis and relationship classification.
- Improve matching performance by refining skill bucketing and leveraging weighted matching.

## Migration Notes

This module was migrated from `/scripts` to align with project structure standards. All new SDR-related development should occur here.
