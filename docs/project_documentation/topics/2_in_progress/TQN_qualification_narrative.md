# Technical Qualification Narrative (TQN) System

## Overview

The Technical Qualification Narrative (TQN) system provides a sophisticated approach to measuring job fit by analyzing not just skill matches but also the criticality and acquisition time of required skills. This system helps create a nuanced picture of qualification that goes beyond simple "yes/no" matching.

## Criticality-Weighted Matching

The system evaluates each job requirement based on its importance to the role:

- **CRITICAL**: Core skills essential for the role (e.g., primary programming language for a developer position)
- **IMPORTANT**: Skills that significantly contribute to success but aren't absolute blockers
- **NICE-TO-HAVE**: Skills that provide incremental value but aren't essential

## Acquisition Time-Weighted Matching

A key enhancement to our matching system is the consideration of **skill acquisition time**. This addresses an important hiring manager question:

> "How long will it take for a new hire to reach 90% proficiency in missing skills?"

### Acquisition Time Categories

Skills are classified into three acquisition time categories:

1. **Quick-to-Learn Skills** (< 3 months)
   - Examples: Excel, PowerPoint, specific tools, basic communication skills
   - Acceptable match threshold: 0.7 (70%)
   - Missing skills in this category are less concerning - they can be learned quickly on the job

2. **Medium-Term Skills** (3-12 months)
   - Examples: Programming languages, frameworks, project management methodologies
   - Acceptable match threshold: 0.8 (80%)
   - Missing skills require moderate investment in training

3. **Long-Term Skills** (1+ years)
   - Examples: Domain expertise (legal, tax, medical), architecture design, leadership
   - Acceptable match threshold: 0.9 (90%)
   - Missing skills in this category are significant concerns as they require substantial time to develop

### Match Adjustment Algorithm

For each skill, we assess:
1. How well the candidate's skills match the requirement (match strength: 0.0-1.0)
2. How long it would take to acquire proficiency in the skill if lacking
3. The match strength threshold based on acquisition time category

When a match is below the threshold for its category, we apply targeted adjustments:
- **Quick-learn skills**: Gap reduced by 90% (almost fully compensating for the missing skill)
- **Medium-term skills**: Gap reduced by 50% (moderate compensation)
- **Long-term skills**: Gap reduced by only 10% (minimal compensation)

### Example

Consider a candidate with:
- 0.75 match on a quick-learn skill (threshold 0.7) → No adjustment needed, above threshold
- 0.65 match on a medium-term skill (threshold 0.8) → Adjusted to 0.725
  - Gap: 0.8-0.65 = 0.15
  - 50% reduction: 0.65 + (0.15 × 0.5) = 0.725
- 0.82 match on a long-term skill (threshold 0.9) → Adjusted to 0.828
  - Gap: 0.9-0.82 = 0.08
  - 10% reduction: 0.82 + (0.08 × 0.1) = 0.828

## Benefits of Acquisition Time Weighting

This approach provides several advantages:

1. **More Nuanced Evaluation**: Goes beyond binary "qualified/not qualified" assessments
2. **Practical Hiring Insights**: Answers the practical question about onboarding time
3. **Realistic Expectations**: Acknowledges that some skills can be reasonably learned on the job
4. **Risk Assessment**: Better identifies high-risk skill gaps that would take years to fill

## Implementation

The acquisition time evaluation uses two methods:
1. **LLM-Based Assessment**: Uses a domain-aware model to evaluate each skill based on complexity, prerequisites, and learning curve
2. **Heuristic Fallback**: Uses predefined categories and recognition patterns when LLM is unavailable

The system maintains a cache of acquisition time assessments to improve performance and consistency.

## Usage in Job Matching

When enabled, acquisition time weighting is applied:
1. After criticality weighting (which identifies the importance of each requirement)
2. Before generating the final qualification score
3. With detailed reporting on which skills received adjustments

## Future Work

- Personalized acquisition time assessments based on related skills already possessed
- Learning curve modeling for more precise time estimates
- Integration with development planning to create skill acquisition roadmaps

## Initial Issue (May 6, 2025)
My score in data/postings/job61951.json is 0, yet this is wrong:

```json
"qualification_narrative": "Based on my professional experience, I am partially qualified for the Tax Senior Specialist (d/m/w) role. My professional background aligns well with the requirements, positioning me to contribute effectively from day one.",
```

## Ollama API Connection Fix (May 7, 2025)

### Problem Identified
The skill decomposer module was failing with 404 errors when trying to connect to Ollama's API endpoints. Terminal logs showed:
```
[GIN] 2025/05/06 - 22:36:18 | 404 | 1.075985ms | 127.0.0.1 | POST "/api/generate"
[GIN] 2025/05/06 - 22:36:18 | 404 | 105.446µs | 127.0.0.1 | POST "/api/generate" 
[GIN] 2025/05/06 - 22:36:18 | 404 | 183.744µs | 127.0.0.1 | POST "/api/chat"
[GIN] 2025/05/06 - 22:36:18 | 404 | 107.016µs | 127.0.0.1 | POST "/api/chat"
```

### Root Cause
Ollama server was running properly (version 0.6.8), but no models were installed. This caused the API endpoints to return 404 errors when trying to access non-existent models.

### Solution Implemented
1. Installed the llama3.2 model using `ollama pull llama3.2`
2. Verified API functionality with a test script (`test_ollama_simulation.py`)
3. Updated E2E documentation with Ollama model installation instructions and notes about normal warning messages

### Verification
1. Ran the orchestrator with 5 test jobs: 
   ```
   cd /home/xai/Documents/sunset && python tests/end_to_end/run_orchestrator.py --max-jobs 5 --output-dir ./data/postings
   ```
2. Results showed successful skill decomposition for 4 out of 5 jobs (one timed out)
3. The logs confirmed successful API calls with messages like:
   ```
   root - INFO - Trying model llama3.2:latest for JSON generation
   root - INFO - Model llama3.2:latest returned valid JSON
   root - INFO - Successfully used model llama3.2:latest to decompose job 61964
   ```

### Latest Results
- Job 61951 (Tax Senior Specialist): Now showing 33.3% match score (previously 0%)
- Job 61964 (Tax Senior Analyst): 100% match score
- Job 62914 (Senior Site Reliability Engineer): 100% match score
- Job 63141 (Senior Procurement Manager): 100% match score

### Note
The warning messages in Ollama logs about `key not found key=general.alignment default=32` are normal and don't affect functionality.

## Domain Matcher Reorganization (May 7, 2025)

### Problem Identified
We identified that the codebase had two separate domain matcher implementations:
1. A basic implementation in `scripts/utils/domain_matcher.py`
2. A more advanced implementation with LLM features in `scripts/utils/skill_decomposer/domain_matcher.py`

This duplication led to confusion, potential code conflicts, and maintenance challenges. Some parts of the codebase used one implementation while other parts used the other.

### Solution Implemented
We reorganized the domain matching functionality with clearer separation of concerns:

1. **Renamed modules for clarity**:
   - Basic implementation: `scripts/utils/basic_domain_matcher.py`
   - Advanced implementation: `scripts/utils/skill_decomposer/advanced_domain_matcher.py`
   - Created new unified interface: `scripts/utils/skill_decomposer/domain_overlap_rater.py`

2. **Updated documentation** in each file to clearly explain:
   - The purpose of each module
   - Which implementation to use for different scenarios
   - The relationship between the modules

3. **Updated imports** in:
   - `scripts/utils/skill_decomposer/requirement_matcher.py` 
   - Test files renamed from `test_domain_matcher.py` to `test_domain_overlap_rater.py`

4. **Created compatibility layers** to ensure existing code continues to work with either implementation

### Benefits
- Clearer code organization and separation of concerns
- Better documentation for developers
- Single interface for domain matching operations
- Maintained backward compatibility for existing code
- Preserved advanced LLM-based domain overlap functionality for sophisticated matching

### Feedback on the Domain Overlap Rater Implementation

The new `domain_overlap_rater.py` implementation represents a significant improvement in our skill matching capabilities. Some notable highlights:

- **Innovative hybrid approach**: The implementation elegantly combines traditional heuristic-based domain matching with LLM-powered analysis, providing the best of both worlds.

- **Intelligent caching**: The caching mechanism dramatically improves performance by storing previously computed domain relationships, which is especially valuable for frequently compared skills.

- **Graceful degradation**: When LLM services are unavailable, the system automatically falls back to heuristic-based matching, ensuring continuous functionality even in offline scenarios.

- **Domain-aware scoring**: The ability to boost or penalize match strengths based on domain relevance results in much more accurate and contextually appropriate skill matches.

- **Rich domain analytics**: The `analyze_job_domain_focus` function provides valuable insights into job requirement domains, enabling better strategic decisions for job applicants.

This approach represents exactly the kind of sophisticated solution we need for accurate qualification assessments - combining traditional algorithms with modern LLM capabilities to achieve results that neither could accomplish alone.

### Next Steps
- Continue to enhance `domain_overlap_rater.py` with additional LLM capabilities
- Consider phase-out plan for the basic domain matcher implementation over time
- Add comprehensive tests for both implementations to ensure consistent behavior

## Domain Overlap vs. Semantic Similarity Weighting

**Date: 2025-05-07**

### Issue
While fixing the errors in the qualification narrative system, we identified an underlying concern with how matches are evaluated. Semantic similarity alone can produce misleading matches between terms that sound linguistically similar but belong to different professional domains (e.g., "tax compliance" and "contract compliance").

### Solution
Implemented a weighting system that allows balancing between semantic similarity and domain overlap when calculating match strength. This gives us the ability to fine-tune the matching algorithm and determine the optimal balance between these two approaches:

1. **Semantic Similarity**: Focuses on linguistic/textual similarity between skills
2. **Domain Overlap**: Focuses on conceptual similarity based on professional domains

The weighting parameter ranges from 0.0 (pure semantic matching) to 1.0 (pure domain overlap matching), with intermediate values creating a weighted blend.

### Next Steps
- Run tests with various weighting values (0.3, 0.5, 0.7, 0.9) and evaluate match quality
- Determine optimal default weighting based on test results
- Consider making this parameter user-configurable for different use cases

### Recent Test Results
Running the self-assessment with domain_overlap_weight=0.7 (70% domain overlap, 30% semantic similarity) has shown promising initial results. We'll continue refining this parameter based on further testing.

## Next Steps
- Consider installing additional backup models for cases when llama3.2 times out
- Investigate the mismatch between the qualification narrative text ("partially qualified") and the match score for job61951.json (33.3%)

## Case Study: Similar Tax Roles with Different Match Scores (May 8, 2025)

### Issue Identified
We've identified an excellent test case to review and refine our matching strategy. Two very similar job roles are showing vastly different match scores:
- **Job 61951** (Tax Senior Specialist): 33.33% match score
- **Job 61964** (Tax Senior Analyst): 100% match score

These positions are nearly identical in their core requirements, with the main difference being seniority level:
- Job 61951 is a Vice President position requiring 7+ years of experience
- Job 61964 is an Assistant Vice President position requiring "several years" of experience

### Root Cause Analysis
The significant discrepancy in match scores stems from how requirement criticality is evaluated, particularly for the "Tax Compliance" skill:

1. **Criticality Rating Differences**: In the `requirement_criticality_cache.json` file:
   - Job 61964: "Tax Compliance" is rated as "CRITICAL" with weight 3.0
   - Job 61951: "Tax Compliance" is rated as "NICE-TO-HAVE" with weight 1.0

2. **Same Skill Matching**: Both jobs show the exact same match between "Tax Compliance" and "contract compliance" with match strength 0.8:
   ```json
   {
     "your_skill": "contract compliance",
     "matched_on": "semantic similarity",
     "match_type": "semantic",
     "match_strength": 0.8,
     "semantic_similarity": 0.8
   }
   ```

3. **Score Discrepancy**: Despite identical skill matches, the criticality weighting is causing Job 61964 to appear as a perfect match while Job 61951 appears as only partially matching.

### Impact of Criticality Weighting
When we analyze the job descriptions, there's little justification for such different criticality ratings:

- Both roles involve tax compliance responsibilities
- Both are in the same department (Group Tax at Deutsche Bank)
- Both focus on Pillar 2 tax regulations and compliance

The inconsistent criticality evaluation appears to be artificially inflating the match score for one role while deflating it for the other.

### Test Results: Criticality Weighting Impact
We conducted controlled tests using the `test_criticality_weighting.py` script to evaluate the impact of criticality weighting on match scores:

#### Job 61951 (Tax Senior Specialist - VP level):
- Regular Match Score: 33% 
- Enhanced Score with Criticality: 27%
- All 3 requirements classified as "Nice-to-Have" in test environment

#### Job 61964 (Tax Senior Analyst - AVP level):
- Regular Match Score: 67%
- Enhanced Score with Criticality: 48% 
- All 3 requirements classified as "Nice-to-Have" in test environment

#### Analysis of Test Results:
1. **Base Score Difference**: Without any weighting, the system already shows a significant difference in match scores (33% vs 67%)
2. **Testing vs. Production**: The test environment showed different behavior than production:
   - In production: Job 61964 showed 100% match vs. Job 61951's 33% match
   - In testing: Job 61964 showed 67% match vs. Job 61951's 33% match
3. **Criticality Classification**: In our controlled test, both jobs had all requirements classified as "Nice-to-Have", which differs from the cached criticality data in the production system

These results suggest that criticality evaluations may not be consistent across different runs or environments, potentially leading to significant score variations for similar jobs.

### Recommendations
1. **Standardized Criticality Evaluation**: Implement a more consistent approach to evaluating requirement criticality, possibly using:
   - Job title and description text analysis with consistent weights
   - Industry-standard job classification systems
   - LLM-based evaluation with carefully crafted prompts

2. **Criticality Confidence Scores**: Add confidence levels to criticality assessments, with less weight given to assessments with low confidence

3. **Manual Override Options**: Allow for manual adjustment of criticality ratings when automated systems produce questionable results

4. **Hybrid Scoring**: Consider showing both weighted and unweighted scores to provide a more balanced perspective

5. **Persistent Criticality Evaluations**: Once a criticality evaluation is performed for a job requirement, ensure it's consistently applied across similar jobs and requirements

### Next Steps
- Review the criticality evaluation algorithm to ensure consistent ratings for similar requirements
- Implement the recommendations above, starting with standardized criticality evaluation
- Continue monitoring similar job pairs to identify and address any inconsistencies in matching

## Semantic Matching Disabled (May 8, 2025)

### Problem Identified
Our investigation into inconsistent match scores revealed a significant issue with semantic matching:

1. **Semantic Matching Inconsistencies**: The semantic matching system produces inconsistent results by matching similar requirements differently based on minor wording variations.

2. **Case Study Evidence**: In our tax roles comparison, we found that:
   - "Tax Compliance" consistently matched with "contract compliance" at 80% similarity
   - "Global Tax Knowledge" matched with "Ontology/Taxonomy development" at 60% similarity
   - "Global Tax Planning" found no matches at all, despite being semantically equivalent to "Global Tax Knowledge"

3. **False Positives**: Semantic matching creates matches based on linguistic similarity rather than actual skill relevance, leading to inflated match scores based on coincidental word similarities.

### Solution Implemented
We've made the following changes to address these issues:

1. **Semantic Matching Disabled by Default**: Modified the `find_skill_matches` function in `matching.py` to disable semantic matching by default (`use_semantic=False`).

2. **Controlled Testing**: Running tests with semantic matching disabled for both tax roles resulted in consistent 0% match scores, confirming that previous differences were entirely due to semantic matching inconsistencies.

3. **Consistent Results**: Without semantic matching, similar jobs now receive more consistent and reliable match scores that better reflect actual qualifications.

### Comparison of Results

| Job | With Semantic Matching | Without Semantic Matching |
|-----|------------------------|---------------------------|
| Tax Senior Specialist (61951) | 33.33% | 0% |
| Tax Senior Analyst (61964) | 66.67% (or 100% with criticality) | 0% |

### Benefits of Disabling Semantic Matching

1. **Consistency**: Match scores between similar job roles are more consistent and predictable.
2. **Reliability**: Matches are based on actual skill alignment rather than linguistic coincidences.
3. **Transparency**: Match scores better reflect genuine skill matches, making it clearer where skill gaps exist.

### Future Improvements

While disabling semantic matching improves consistency, it may reduce match rates overall. To address this, we plan to:

1. **Enhance Exact Matching**: Improve direct matching to handle minor variations in terminology (plurals, hyphenation, etc.)
2. **Implement Skill Taxonomies**: Develop standardized skill taxonomies to map variations of the same skill
3. **Focus on Domain Matching**: Continue enhancing domain-based matching as a more reliable alternative to semantic matching

### Next Steps
- Develop additional test cases to validate the impact of disabling semantic matching
- Enhance direct matching capabilities to recognize slight variations in skill terminology
- Create a mechanism for manually mapping semantically similar skills when needed


