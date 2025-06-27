# Skill Domain Relationship (SDR) Implementation

This directory contains the implementation of the Skill Domain Relationship (SDR) framework, designed to improve skill matching by standardizing skill definitions and taking domain relationships into account.

## Overview

The SDR framework addresses the false positive problems in skill matching by:

1. Standardizing skill definitions using a consistent format
2. Enriching skills with domain-specific components (knowledge, context, function)
3. Classifying relationships between skills based on domain overlap
4. Replacing semantic matching with domain-aware matching

## Components

### Skill Definition Standardization

We've implemented a standardized structure for skill definitions:

```json
{
  "name": "Strategic Sourcing",
  "category": "Sourcing_and_Procurement",
  "level": 3,
  "knowledge_components": ["negotiation_techniques", "market_analysis"],
  "contexts": ["vendor_management", "contract_negotiation"],
  "functions": ["negotiating_contracts", "managing_vendors"]
}
```

Skills are categorized into six core domains:
- IT_Technical
- IT_Management
- Sourcing_and_Procurement
- Leadership_and_Management
- Analysis_and_Reporting
- Domain_Knowledge

### Domain Relationship Classification

Relationships between skills are classified as:
- Exact match: Nearly identical skills (similarity ≥ 0.9)
- Subset: One skill is contained within another (same domain, similarity ≥ 0.7)
- Superset: One skill contains another (same domain, similarity ≥ 0.7)
- Neighboring: Related skills in the same domain (similarity ≥ 0.5)
- Hybrid: Skills across different domains but with significant overlap (similarity ≥ 0.5)
- Unrelated: Skills with minimal relationship (similarity < 0.5)

### Domain-Aware Matching

The matching algorithm calculates match scores based on domain relationships rather than simple semantic similarity, which reduces false positives and improves match quality.

## Implementation Scripts

- `skill_analyzer.py`: Extracts, analyzes, and ranks skills from job postings and CVs
- `domain_relationship_classifier.py`: Implements domain relationship classification
- `domain_aware_matcher.py`: Implements domain-aware matching algorithm
- `run_sdr_implementation.py`: Orchestrates the complete SDR implementation process
- `run_sdr.sh`: Shell script to run the implementation

## Output Files

The implementation generates the following output files in `docs/skill_matching/`:

- `enriched_skills.json`: Standardized skill definitions with domain components
- `skill_relationships.json`: Matrix of relationships between skills
- `matching_test_results.json`: Results of testing the matching algorithm
- `sdr_implementation_results.json`: Summary of the implementation process

## Running the Implementation

To run the SDR implementation:

1. Ensure Python 3.7+ is installed
2. Navigate to the scripts directory
3. Run the shell script:

```bash
cd scripts
./run_sdr.sh
```

## Next Steps

1. Expand the collection of enriched skills beyond the initial 50
2. Integrate the SDR framework with the existing job matching pipeline
3. Set up automated tests and validation for the matching algorithm
4. Collect feedback on match quality for continuous improvement

## Metrics

The implementation will be evaluated based on:
1. False Positive Reduction (Target: 80% reduction)
2. Match Quality Improvement (Target: 70% user preference)
3. System Performance (Target: < 5 seconds for match analysis)
