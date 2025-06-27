# Domain Enhanced Matcher

This document provides information about the Domain Enhanced Matcher module, which improves skill matching by incorporating domain context alongside semantic similarity.

## Module Organization

The Domain Enhanced Matcher consists of the following components:

1. **Domain Matcher Integration** (`run_pipeline/skill_matching/domain_matcher_integration.py`)
   - Provides a unified interface to different domain matching implementations
   - Handles graceful fallbacks between basic and advanced matchers
   - Caches domain lookups for improved performance

2. **Enhanced Domain Skill Matcher** (`run_pipeline/skill_matching/enhanced_domain_skill_matcher.py`)
   - Implements domain-aware skill similarity calculations
   - Provides enhanced scoring with domain context weights
   - Supports analyzing domain relationships between skills

3. **Domain Enhanced Matcher Runner** (`run_pipeline/run_domain_enhanced_matcher.py`)
   - Command-line interface for batch processing jobs with the domain matcher
   - Supports parallel processing for improved performance
   - Manages caching of match results

## Usage

To use the Domain Enhanced Matcher:

```bash
# Process a single job
python run_pipeline/run_domain_enhanced_matcher.py 12345

# Process all jobs
python run_pipeline/run_domain_enhanced_matcher.py --all

# Process multiple specific jobs
python run_pipeline/run_domain_enhanced_matcher.py --jobs 12345,12346,12347

# Force reprocessing of already processed jobs
python run_pipeline/run_domain_enhanced_matcher.py --all --force

# Configure batch size and workers for parallel processing
python run_pipeline/run_domain_enhanced_matcher.py --all --workers 4 --batch-size 10

# Export results to a specific CSV file
python run_pipeline/run_domain_enhanced_matcher.py --all --csv-path data/custom_report.csv

# Skip CSV export
python run_pipeline/run_domain_enhanced_matcher.py --all --no-csv
```

## Integration with Pipeline

The Domain Enhanced Matcher can be run independently using the runner script. It's not currently integrated with the main pipeline flow (`run_pipeline/run.py`), but can be used as a supplemental matching tool.

To integrate it with the main pipeline in the future, the `run_pipeline/core/skill_matching_orchestrator.py` would need to be updated to call the Enhanced Domain Skill Matcher alongside or as an alternative to the bucketed matcher.

## Output

The matcher now produces domain-enhanced match results directly in each job file in:
```
data/postings/{job_id}.json
```

These results are stored in a "domain_enhanced_match" property within each job file, and include:
- Match coverage percentage
- Average match score
- Domain relationship analysis
- Quality assessments for each match (High/Medium/Low)

Additionally, the matcher can export a CSV report summarizing the results for all jobs to:
```
data/reports/domain_enhanced_matches_YYYYMMDD_HHMMSS.csv
```

This CSV includes:
- Job ID and title
- Match coverage percentage 
- Average match score
- Counts of high/medium/low quality matches
- Primary domains
- Number of matched skills
