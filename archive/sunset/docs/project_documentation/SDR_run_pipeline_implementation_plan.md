# SDR Run Pipeline Implementation Plan

*Date: May 19, 2025*

## Overview

This document outlines the implementation plan for integrating the Skill Domain Relationship (SDR) framework into the `run_pipeline` module. The SDR framework addresses the critical issue of false positive matches in job skill matching by providing domain-aware skill matching instead of purely semantic matching.

## Current State Analysis

The `run_pipeline` module currently has:
- A well-structured pipeline with 5 stages
- Basic skill extraction from job descriptions
- Skill categorization and importance analysis
- Elementary skill decomposition

The existing functionality in other modules that needs to be ported:
- CV skill extraction from `profile/profile/cv/Gershon Pollatschek CV 2025.md`
- Domain-aware skill matching from the SDR framework
- LLM integration for domain analysis and relationship classification

## Implementation Plan

### Phase 1: Set up Core Components (Estimated: 3 days)

1. **Create CV Skills Extractor Module**
   - Create `run_pipeline/core/cv_skill_extractor.py` 
   - Implement Markdown parsing for CV
   - Extract both explicit and implicit skills
   - Store extracted skills in a structured format with professional context
   - Add experience timeline for skill acquisition time weighting

2. **Port Domain Overlap Components**
   - Create `run_pipeline/core/domain_overlap/` directory structure
   - Port `domain_overlap_rater.py` and related utilities
   - Port the SDR framework implementation
   - Implement Jaccard similarity and other distance metrics
   - Create skill domain component extraction functions

3. **Set up LLM Integration**
   - Create `run_pipeline/core/llm_integration.py`
   - Implement multi-model approach with fallback chain
   - Primary model: phi4-mini-reasoning
   - Fallbacks: llama3.2, mistral
   - Implement exponential backoff for timeouts
   - Set up caching mechanisms for LLM responses
   - Create model-specific prompt templates

### Phase 2: Enhance Skills Module (Estimated: 2 days)

1. **Update `skills_module.py` for Domain-Aware Matching**
   - Add domain analysis functions for job skills
   - Add domain analysis for CV skills
   - Implement domain-aware matching algorithms
   - Update the requirement decomposition with domain context
   - Implement relationship classification
   - Add domain compatibility scoring

2. **Create Enhanced Matching Report Generation**
   - Implement detailed domain analysis reports
   - Create visual representations of domain matching
   - Generate feedback on skill gaps with domain context
   - Add skill transition suggestions
   - Include proficiency level analysis

### Phase 3: Integration and Enhancements (Estimated: 2 days)

1. **Update Pipeline Entry Points**
   - Update `pipeline.py` to include domain-aware steps
   - Add command-line arguments for SDR options
   - Implement pipeline entry points for individual operations
   - Add configuration options for model selection

2. **Add Efficient Caching System**
   - Implement caching for domain relationships
   - Add caching for decomposed job requirements
   - Set up LLM response caching for performance
   - Create cache invalidation strategies

### Phase 4: Testing and Optimization (Estimated: 3 days)

1. **Create Test Suite**
   - Create unit tests for all SDR components
   - Set up integration tests for the complete pipeline
   - Create benchmark tests for performance
   - Test with known problematic skills (like "automation")

2. **Optimize Performance**
   - Analyze and improve LLM response times
   - Implement parallel processing where possible
   - Enhance caching strategies
   - Optimize prompts for quick responses

## Implementation Details

### File Structure

```
run_pipeline/
├── core/
│   ├── pipeline.py (Update)
│   ├── skills_module.py (Update)
│   ├── cv_skill_extractor.py (New)
│   ├── llm_integration.py (New)
│   └── domain_overlap/ (New)
│       ├── __init__.py
│       ├── domain_overlap_rater.py
│       ├── domain_overlap_utils.py
│       └── skill_domain_relationship.py
├── utils/
│   ├── logging_utils.py (Existing)
│   └── caching_utils.py (New)
└── config/
    ├── paths.py (Update)
    └── llm_models.py (New)
```

### Key Code Implementations

#### 1. CV Skill Extractor

```python
# cv_skill_extractor.py

def extract_skills_from_cv(cv_path):
    """Extract skills from CV document"""
    skills = []
    experience_timeline = {}
    
    # Parse Markdown CV
    with open(cv_path, 'r') as f:
        cv_content = f.read()
    
    # Extract core competencies section
    core_competencies = extract_section(cv_content, "Core Competencies")
    
    # Extract skills lists
    for competency_area in parse_competency_areas(core_competencies):
        area_name = competency_area['name']
        area_skills = parse_bullet_points(competency_area['content'])
        
        for skill in area_skills:
            skills.append({
                'name': skill,
                'category': area_name,
                'source': 'cv_core_competency',
                'confidence': 0.9
            })
    
    # Extract skills from experience sections
    experience_sections = extract_section(cv_content, "Professional Experience")
    job_experiences = parse_experiences(experience_sections)
    
    for job in job_experiences:
        period = job.get('period', '')
        start_year = extract_start_year(period)
        
        job_skills = extract_skills_from_description(job.get('description', ''))
        for skill in job_skills:
            if skill not in [s['name'] for s in skills]:
                skills.append({
                    'name': skill,
                    'category': job.get('title', 'Unknown'),
                    'source': 'cv_job_experience',
                    'confidence': 0.7
                })
            
            # Add to experience timeline
            if skill not in experience_timeline or start_year < experience_timeline[skill]:
                experience_timeline[skill] = start_year
    
    return skills, experience_timeline
```

#### 2. Domain Overlap Rater

```python
# domain_overlap_rater.py

def calculate_domain_overlap(skill1, skill2):
    """Calculate domain overlap between two skills (0-1 scale)"""
    # Check cache first
    cache_key = f"{skill1}|{skill2}"
    reverse_key = f"{skill2}|{skill1}"
    
    cache = _load_cache()
    if cache_key in cache: return cache[cache_key]
    if reverse_key in cache: return cache[reverse_key]
    
    # Try multiple strategies with fallbacks
    overlap = None
    
    # 1. Try SDR framework (preferred)
    try:
        relationship = classify_relationship(skill1, skill2)
        if relationship and "compatibility_percentage" in relationship:
            overlap = relationship["compatibility_percentage"] / 100.0
    except Exception as e:
        logger.debug(f"SDR calculation failed: {e}")
    
    # 2. Try LLM-based calculation
    if overlap is None:
        try:
            overlap = calculate_llm_overlap(skill1, skill2)
        except Exception as e:
            logger.debug(f"LLM calculation failed: {e}")
    
    # 3. Fallback to heuristic approach
    if overlap is None:
        overlap = calculate_heuristic_overlap(skill1, skill2)
    
    # Cache the result
    _update_cache(cache_key, overlap)
    return overlap
```

#### 3. Skills Module Update for Domain-Aware Matching

```python
# skills_module.py

def match_skills_using_domain(profile_skills, job_requirements):
    """
    Match profile skills against job requirements using domain awareness
    
    Args:
        profile_skills: List of skills from the profile
        job_requirements: List of job requirements
        
    Returns:
        List of match results with domain context
    """
    matches = []
    
    for req in job_requirements:
        req_name = req.get('name', '')
        best_match = None
        best_score = 0
        
        for skill in profile_skills:
            skill_name = skill.get('name', '')
            
            # Calculate domain overlap
            domain_overlap = calculate_domain_overlap(skill_name, req_name)
            
            # Only consider matches with sufficient domain overlap
            if domain_overlap >= 0.3:  # Minimum threshold
                # Calculate total score (weighted combination)
                score = domain_overlap * 0.7  # Prioritize domain
                
                if score > best_score:
                    best_score = score
                    best_match = {
                        'skill': skill_name,
                        'requirement': req_name,
                        'match_strength': score,
                        'domain_overlap': domain_overlap,
                        'match_type': 'domain_match'
                    }
        
        if best_match:
            matches.append(best_match)
        else:
            # No match found
            matches.append({
                'requirement': req_name,
                'match_strength': 0,
                'match_type': 'no_match'
            })
    
    return matches
```

#### 4. LLM Integration with Model Fallback

```python
# llm_integration.py

def extract_domain_with_llm(skill_name):
    """
    Extract domain information for a skill using LLM with fallback chain
    
    Args:
        skill_name: Name of the skill to analyze
        
    Returns:
        Dictionary with domain information
    """
    # Define models in preference order
    models = [
        {"name": "phi4-mini-reasoning", "timeout": 30},
        {"name": "llama3.2", "timeout": 45},
        {"name": "mistral", "timeout": 35}
    ]
    
    prompt = create_domain_extraction_prompt(skill_name)
    
    # Try each model in sequence
    for model_config in models:
        model_name = model_config["name"]
        timeout = model_config["timeout"]
        
        try:
            logger.debug(f"Trying domain extraction with model: {model_name}")
            response = call_llm(prompt, model_name, timeout)
            
            if response:
                # Parse JSON from response
                domain_info = extract_json_from_response(response)
                
                # Validate response structure
                if validate_domain_info_structure(domain_info):
                    logger.info(f"Successfully extracted domain info using {model_name}")
                    return domain_info
                else:
                    logger.warning(f"Invalid domain info structure from {model_name}")
        except Exception as e:
            logger.warning(f"Error with model {model_name}: {str(e)}")
    
    # If all models fail, return basic info
    return {
        "domain": "unknown",
        "knowledge_components": [],
        "context": [],
        "functions": []
    }
```

#### 5. Main Pipeline Updates for SDR Integration

```python
# pipeline.py

def process_skills(max_jobs=None, job_ids=None, log_dir=None, use_domain_aware=True, 
                 primary_model="phi4-mini-reasoning", use_model_fallback=True):
    """
    Process skills for job postings with domain awareness
    
    Args:
        max_jobs: Maximum number of jobs to process
        job_ids: Specific job IDs to process
        log_dir: Directory for log files
        use_domain_aware: Whether to use domain-aware matching
        primary_model: Primary LLM model to use
        use_model_fallback: Whether to use fallback models on failure
        
    Returns:
        bool: Success status
    """
    logger.info(f"Processing job skills with domain-aware matching: {use_domain_aware}")
    
    try:
        # Load CV skills - new step
        cv_path = Path(CV_FILE_PATH)
        if cv_path.exists():
            profile_skills, skill_timeline = extract_skills_from_cv(cv_path)
            logger.info(f"Extracted {len(profile_skills)} skills from CV")
        else:
            logger.error(f"CV file not found: {cv_path}")
            return False
        
        # Process job files
        processed, success, error = process_job_files(
            job_dir=JOB_DATA_DIR,
            max_jobs=max_jobs,
            specific_job_ids=job_ids,
            profile_skills=profile_skills,
            skill_timeline=skill_timeline,
            use_domain_aware=use_domain_aware,
            primary_model=primary_model,
            use_model_fallback=use_model_fallback
        )
        
        # Generate summary report
        logger.info("=" * 50)
        logger.info("Job Skills Processing Summary")
        logger.info("=" * 50)
        logger.info(f"Total jobs processed: {processed}")
        logger.info(f"Successfully processed: {success}")
        logger.info(f"Errors: {error}")
        logger.info(f"Using domain-aware matching: {use_domain_aware}")
        logger.info(f"Primary LLM model: {primary_model}")
        logger.info("=" * 50)
        
        return processed > 0
        
    except Exception as e:
        logger.error(f"Critical error in job skills processing: {str(e)}")
        return False
```

## Required Dependencies

1. **LLM Model Integration**
   - Set up access to phi4-mini-reasoning (primary)
   - Configure fallbacks to llama3.2 and mistral
   - Implement timeout handling and exponential backoff
   - Configure model-specific prompts

2. **Data Storage**
   - Set up storage for domain relationship cache
   - Configure paths for skill decompositions
   - Set up efficient storage for LLM responses
   - Create cache invalidation mechanisms

## Testing Strategy

1. **Unit Testing**
   - Test each SDR component independently
   - Test CV skill extraction with sample CV
   - Test domain overlap calculation with known skills
   - Test LLM fallback chain

2. **Integration Testing**
   - Test complete pipeline workflow
   - Verify domain-aware matching produces better results than semantic
   - Test with known problematic skills like "automation"
   - Validate improved match scores

3. **Performance Benchmarking**
   - Measure LLM response times across models
   - Compare matching accuracy with and without domain awareness
   - Evaluate impact of caching on performance
   - Monitor memory usage for large job batches

## Next Steps

1. Set up project structure and implement CV skill extractor
2. Port domain overlap modules from existing codebase
3. Set up LLM integration with model fallback chain
4. Update skills module with domain-aware matching
5. Update pipeline entry points and add CLI options
6. Implement comprehensive test suite
7. Optimize for performance

## Timeline

| Task | Start Date | End Date | Duration |
|------|------------|----------|----------|
| Set up Core Components | May 20, 2025 | May 22, 2025 | 3 days |
| Enhance Skills Module | May 23, 2025 | May 24, 2025 | 2 days |
| Integration and Enhancements | May 25, 2025 | May 26, 2025 | 2 days |
| Testing and Optimization | May 27, 2025 | May 29, 2025 | 3 days |

Total implementation time: **10 days**

## Task Assignments

To be determined based on team availability and expertise.

## Success Metrics

1. **Reduction in false positives** - Goal: Reduce false positives by 80%+
2. **More accurate match percentages** - Goal: Match scores reflect actual domain compatibility
3. **Improved resilience** - Goal: 99%+ success rate for LLM calls with fallback
4. **Better performance** - Goal: Process 50+ jobs in under 10 minutes 
5. **Better skill gap analysis** - Goal: Provide actionable insights for skill development

## Conclusion

This implementation plan provides a structured approach to integrating the SDR framework into the run_pipeline module. By following this plan, we will significantly improve job matching accuracy by differentiating between skills with similar names but different domain contexts. The domain-aware matching will reduce false positives and provide more accurate compatibility scores.
