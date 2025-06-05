# Domain-Aware Skill Matching: Implementation Approach

*Date: June 5, 2025*

## Executive Summary

This document outlines the implementation approach for integrating the Skill Domain Relationship (SDR) framework with our existing job parsing and skill categorization solutions. The primary goal is to solve the false positive matching issues identified in our current system by adding domain context to skills, resulting in more accurate skill matching and job recommendations. Additionally, this document describes how the SDR framework will be integrated with the Skill Acquisition Timeline Framework to provide comprehensive skill development planning that accounts for domain relationships when calculating skill acquisition times.

## Problem Statement

Our existing skill matching system has been producing false positives due to:

1. **Over-reliance on semantic matching** - Text similarity alone is insufficient for determining skill compatibility
2. **Missing domain context** - Generic skills like "automation" match across unrelated domains
3. **Lack of knowledge component analysis** - Current system doesn't analyze the underlying knowledge required
4. **Undifferentiated proficiency levels** - General familiarity vs. deep expertise aren't distinguished properly

## Existing System Analysis

### Current Categorization Approach

Our system currently categorizes skills into six core domains:
- IT_Technical
- IT_Management
- Sourcing_and_Procurement
- Leadership_and_Management
- Analysis_and_Reporting
- Domain_Knowledge

This forms a solid foundation but lacks the nuanced context needed for accurate matching.

### Current Job Parsing Process

The job parsing system uses the OLMo LLM to:
1. Extract skills from job descriptions
2. Categorize them into predefined skill categories
3. Rate required levels (1-5 scale)
4. Determine if skills are essential or desirable

## SDR Framework Integration Overview

The Skill Domain Relationship (SDR) framework enhances our existing system by adding domain-awareness and relationship classification. The integration will follow these core principles:

1. **Preserve existing categorization** - Maintain the six domains as the high-level structure
2. **Add domain contextualization** - Enrich skills with knowledge components, contexts, and functions
3. **Implement relationship classification** - Determine how skills relate across domains
4. **Use LLM-powered domain analysis** - Leverage advanced language models for nuanced understanding

## Implementation Architecture

### System Components

![SDR Architecture](../project_documentation/diagrams/sdr_architecture.png)

The domain-aware skill matching system will consist of these key components:

1. **CV Skill Extractor**
   - Analyzes CV documents to extract explicit and implicit skills
   - Associates skills with relevant professional contexts
   - Creates a timeline of skill acquisition and usage

2. **Domain Overlap Analysis**
   - Implements Jaccard similarity for knowledge component comparison
   - Calculates domain distances between skills
   - Classifies relationships between skills (subset, superset, neighboring, etc.)

3. **LLM Integration Layer**
   - Primary model: phi4-mini-reasoning
   - Fallbacks: llama3.2, mistral
   - Implements caching, timeout handling, and validation
   - Extracts domain components and analyzes relationships

4. **Enhanced Matching Engine**
   - Replaces pure semantic matching with domain-aware matching
   - Adjusts match strength based on relationship types
   - Filters out incompatible domain matches

## Implementation Plan

### Phase 1: Skill Enrichment (June 10, 2025)

1. **Domain-Enrich Existing Skills**
   - Add knowledge components, contexts, and functions to each skill
   - Use the following structure:
   ```json
   {
     "name": "Basic Process Automation",
     "category": "IT_Technical",
     "knowledge_components": ["workflow_analysis", "scripting", "process_improvement"],
     "contexts": ["office", "business_process"],
     "functions": ["efficiency_improvement", "task_simplification"],
     "proficiency_level": 6
   }
   ```

2. **Resolve Generic Skills**
   - Split problematic generic skills into domain-specific variants
   - Example: Split "automation" into "Process Automation", "Development Automation", etc.

### Phase 2: Model Integration (June 15, 2025)

1. **Implement Multi-Model Approach**
   - Primary: phi4-mini-reasoning for best balance of speed and accuracy
   - First fallback: llama3.2 for high accuracy on technical domains
   - Second fallback: mistral for general reliability
   - Add exponential backoff and timeout handling

2. **Optimize Prompts**
   - Create specialized prompts for:
     - Domain component extraction
     - Relationship classification
     - Skill gap analysis
   - Include validation logic for LLM outputs

### Phase 3: Matching Algorithm Updates (June 20, 2025)

1. **Replace Semantic Matching**
   - Implement domain-aware matching algorithm
   - Consider relationship types in match scoring
   - Prioritize subset/superset relationships over neighboring

2. **Enhance Job Requirement Parsing**
   - Update job-parser-prompt.md to extract domain components
   - Add domain context to extracted job requirements
   - Implement knowledge component extraction

### Phase 4: UI and Reporting (June 25, 2025)

1. **Enhanced Match Reports**
   - Create visual representations of domain overlap
   - Generate detailed feedback on skill gaps
   - Provide transition pathways for skill development

2. **UI Updates**
   - Add domain filter options
   - Implement relationship type filtering
   - Create visual representations of skill relationships

## Technical Implementation

### Core Function Updates

1. **Update `find_skill_matches` Function**
   ```python
   def find_skill_matches(cv_skills, job_skills):
       matches = []
       
       for job_skill in job_skills:
           best_match = None
           best_score = 0
           relationship_type = None
           
           for cv_skill in cv_skills:
               # Domain-aware matching instead of semantic
               domain_score = calculate_domain_overlap(cv_skill, job_skill)
               relationship = classify_relationship(cv_skill, job_skill)
               
               # Only consider valid relationship types
               if relationship in ['exact', 'subset', 'superset', 'neighboring']:
                   # Calculate relationship-adjusted score
                   adjusted_score = adjust_score_by_relationship(
                       domain_score, 
                       relationship,
                       cv_skill['proficiency_level'],
                       job_skill['level']
                   )
                   
                   if adjusted_score > best_score:
                       best_match = cv_skill
                       best_score = adjusted_score
                       relationship_type = relationship
           
           if best_match and best_score > MATCH_THRESHOLD:
               matches.append({
                   'job_skill': job_skill,
                   'cv_skill': best_match,
                   'score': best_score,
                   'relationship': relationship_type
               })
       
       return matches
   ```

2. **Domain Overlap Calculation**
   ```python
   def calculate_domain_overlap(skill1, skill2):
       # Calculate Jaccard similarity of knowledge components
       kc_similarity = jaccard_similarity(
           skill1['knowledge_components'],
           skill2['knowledge_components']
       )
       
       # Calculate context overlap
       context_similarity = jaccard_similarity(
           skill1['contexts'],
           skill2['contexts']
       )
       
       # Calculate function overlap
       function_similarity = jaccard_similarity(
           skill1['functions'],
           skill2['functions']
       )
       
       # Weighted average based on importance of each factor
       return (kc_similarity * 0.5) + (context_similarity * 0.3) + (function_similarity * 0.2)
   ```

3. **Relationship Classification**
   ```python
   def classify_relationship(skill1, skill2):
       # Calculate set relationships between knowledge components
       kc1 = set(skill1['knowledge_components'])
       kc2 = set(skill2['knowledge_components'])
       
       # Calculate Jaccard similarity
       jaccard = len(kc1.intersection(kc2)) / len(kc1.union(kc2))
       
       # Determine relationship type
       if jaccard > 0.9:
           return 'exact'
       elif kc1.issubset(kc2):
           return 'subset'  # skill1 is a subset of skill2
       elif kc2.issubset(kc1):
           return 'superset'  # skill1 is a superset of skill2
       elif jaccard > 0.3:
           return 'neighboring'
       else:
           return 'unrelated'
   ```

### LLM Integration for Domain Extraction

```python
def extract_domain_components(skill_name):
    prompt = f"""
    Analyze the skill '{skill_name}' and extract its domain components:
    
    1. Knowledge Components: Core knowledge areas required for this skill
    2. Contexts: Situations or environments where this skill is applied
    3. Functions: What this skill accomplishes or enables
    
    Format your response as valid JSON with these three arrays.
    """
    
    # Try primary model first, with fallback chain
    try:
        result = call_llm_with_timeout(
            model="phi4-mini-reasoning", 
            prompt=prompt, 
            timeout=25
        )
        return validate_domain_components(result)
    except TimeoutError:
        try:
            result = call_llm_with_timeout(
                model="llama3.2", 
                prompt=prompt, 
                timeout=40
            )
            return validate_domain_components(result)
        except TimeoutError:
            # Final fallback
            result = call_llm_with_timeout(
                model="mistral", 
                prompt=prompt, 
                timeout=30
            )
            return validate_domain_components(result)
```

## Integration with Existing Skill Categories

The SDR framework will integrate with our existing six-domain categorization as follows:

1. **Maintain High-Level Categories**
   - Keep IT_Technical, IT_Management, etc. as the primary categories
   - Use them for high-level filtering and organization

2. **Add Sub-Domain Categorization**
   - Within each high-level category, add domain-specific context
   - Example: Within IT_Technical, differentiate between "Frontend Development", "Database Management", etc.

3. **Enhanced Matching Logic**
   - Match first on high-level category (ensures domain alignment)
   - Then apply domain-aware matching within categories
   - Adjust match scores based on relationship types

## Testing and Evaluation

1. **Test Cases**
   - Create test cases for known problematic skills (e.g., "automation")
   - Evaluate the new matching against the previous results

2. **Performance Benchmarks**
   - Measure LLM response times and optimize where needed
   - Test batch processing capacity

3. **Match Quality Evaluation**
   - Compare match quality metrics before and after SDR implementation
   - Track false positive reduction rate

## Integration with Skill Acquisition Timeline Framework

The Domain-Aware Skill Matching system will be integrated with the Skill Acquisition Timeline Framework to provide comprehensive skill development planning alongside accurate matching. This integration enables calculating realistic ramp-up times for candidates and enhances decision-making for employers and candidates.

### Synergy Between Domain-Aware Matching and Acquisition Timelines

1. **Enriched Skill Definitions**
   - Domain-aware skills will include acquisition timelines for each proficiency level
   - Example enhanced skill structure:
   ```json
   {
     "name": "Basic Process Automation",
     "category": "IT_Technical",
     "knowledge_components": ["workflow_analysis", "scripting", "process_improvement"],
     "contexts": ["office", "business_process"],
     "functions": ["efficiency_improvement", "task_simplification"],
     "proficiency_level": 6,
     "acquisition_timeline": {
       "level_1": {"base_time": "1 week", "time_in_days": 7},
       "level_2": {"base_time": "2 months", "time_in_days": 60},
       "level_3": {"base_time": "8 months", "time_in_days": 240},
       "level_4": {"base_time": "2.5 years", "time_in_days": 912},
       "level_5": {"base_time": "5 years", "time_in_days": 1825}
     },
     "prerequisites": ["Basic Scripting", "Process Analysis", "Documentation Skills"]
   }
   ```

2. **Domain-Aware Ramp-Up Calculation**
   - Incorporate domain relationships when calculating skill acquisition time
   - Reduce acquisition time for skills with significant knowledge component overlap
   - Consider domain-specific acceleration factors

3. **Enhanced Decision Support**
   - Provide transition pathways based on skill domain relationships
   - Generate realistic skill acquisition roadmaps
   - Support strategic hiring and development decisions

### Implementation Approach

1. **Extend the Domain Overlap Analysis Module**
   ```python
   def calculate_domain_transition_time(source_skill, target_skill, base_acquisition_time):
       """Calculate adjusted acquisition time based on domain relationships."""
       # Get domain relationship between skills
       relationship = classify_relationship(source_skill, target_skill)
       domain_overlap = calculate_domain_overlap(source_skill, target_skill)
       
       # Adjust acquisition time based on relationship and overlap
       if relationship == 'exact':
           # Nearly identical skills require minimal transition time
           return base_acquisition_time * 0.1  # 90% reduction
       elif relationship == 'subset':
           # Target skill builds on existing skill
           return base_acquisition_time * (1 - (domain_overlap * 0.8))
       elif relationship == 'superset':
           # Source skill already contains target skill knowledge
           return base_acquisition_time * 0.3  # 70% reduction
       elif relationship == 'neighboring':
           # Related skills share some knowledge
           return base_acquisition_time * (1 - (domain_overlap * 0.5))
       else:
           # Unrelated skills require full acquisition time
           return base_acquisition_time
   ```

2. **Integrate with Development Planning**
   ```python
   def generate_development_plan(candidate_skills, job_skills, acceleration_factors=None):
       """Generate a comprehensive development plan with domain-aware timelines."""
       # Calculate ramp-up time for each required skill
       skill_development_paths = []
       
       for job_skill in job_skills:
           if job_skill["importance"] != "Essential":
               continue
               
           # Find best matching candidate skill
           best_match = None
           best_score = 0
           for cv_skill in candidate_skills:
               domain_score = calculate_domain_overlap(cv_skill, job_skill)
               if domain_score > best_score:
                   best_score = domain_score
                   best_match = cv_skill
           
           # Calculate acquisition/transition time
           if best_match and best_score > 0.3:
               # Calculate transition time between skills
               transition_time = calculate_skill_transition_time(
                   best_match,
                   job_skill,
                   acceleration_factors
               )
               
               # Generate transition pathway
               transition_path = generate_skill_transition_path(
                   best_match,
                   job_skill
               )
           else:
               # Calculate full acquisition time
               transition_time = calculate_full_acquisition(
                   job_skill,
                   acceleration_factors
               )
               
               transition_path = generate_acquisition_pathway(job_skill)
           
           skill_development_paths.append({
               "job_skill": job_skill,
               "matching_candidate_skill": best_match,
               "domain_overlap_score": best_score if best_match else 0,
               "estimated_time_days": transition_time,
               "estimated_time_description": days_to_time_description(transition_time),
               "development_pathway": transition_path
           })
       
       return {
           "overall_rampup_time": max(path["estimated_time_days"] for path in skill_development_paths),
           "skill_development_paths": skill_development_paths,
           "recommended_learning_sequence": optimize_learning_sequence(skill_development_paths)
       }
   ```

### Enhanced Reporting

The integration will provide enhanced match reports that include:

1. **Skill Gap Analysis with Domain Context**
   - Identify missing knowledge components within domains
   - Calculate acquisition time for each knowledge component
   - Visualize skill gaps with domain-specific context

2. **Development Timelines with Domain Pathways**
   - Present realistic timelines for skill acquisition based on domain relationships
   - Suggest optimal learning sequences that leverage domain overlap
   - Provide detailed transition pathways between related domains

3. **Strategic Development Planning**
   - Provide options for different development scenarios
   - Balance short-term requirements with long-term skill development
   - Prioritize skill acquisition based on domain relationships

### Benefits of Integration

1. **For Candidates**
   - More accurate development planning with domain context
   - Clearer understanding of skill transferability across domains
   - Prioritized learning paths based on existing skill domain foundation

2. **For Employers**
   - Better prediction of time-to-productivity with domain context
   - More strategic hiring decisions based on development timelines
   - Improved resource allocation for training and mentoring

3. **For the System**
   - More accurate match quality assessment
   - Better differentiation between similar candidates
   - Reduced false positives through domain-aware development timelines

## Next Steps

1. Begin implementation of the CV Skill Extractor module
2. Port Domain Overlap components from existing code
3. Set up LLM integration with the multi-model approach
4. Update the matching algorithm to use domain-awareness
5. Integrate the Skill Acquisition Timeline Framework
   - Extend skill definitions with acquisition timeline data
   - Implement domain-aware ramp-up calculations
   - Create enhanced reporting with skill development pathways
6. Implement UI changes to reflect the new matching approach
   - Add visualization of domain relationships
   - Include acquisition timeline projections in the match reports
   - Provide interactive development planning tools

## Conclusion

The implementation of domain-aware skill matching through the SDR framework represents a significant advancement in our job matching capabilities. By moving beyond simple semantic matching to a nuanced understanding of skill relationships across domains, we will provide more accurate, relevant job matches that truly reflect the candidate's capabilities and the job requirements.
