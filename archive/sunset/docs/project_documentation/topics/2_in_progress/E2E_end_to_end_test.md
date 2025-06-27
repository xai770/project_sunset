# End-to-End Testing Plan for Project Sunset Career Pipeline

## Overview

This document outlines a comprehensive testing plan for the Project Sunset career pipeline, specifically focusing on the `scripts/career_pipeline/orchestrator.py` module which serves as the main coordination center for the entire job application workflow.

## Test Objectives

1. Verify that the complete pipeline functions correctly end-to-end
2. Validate the integration between different components
3. Test error handling and recovery mechanisms
4. Evaluate performance under realistic conditions
5. Ensure data integrity throughout the pipeline

## Components to Test

The orchestrator coordinates these key components which need to be tested:

- Job fetching from Deutsche Bank Careers API
- Job detail extraction from web pages
- Job processing and saving
- Skill decomposition
- Self-assessment generation
- Report generation
- VPN rotation and access management

## Test Environment Setup

### Prerequisites

1. Valid API access credentials stored in `credentials.json`
2. VPN configured for IP rotation if needed (interface "wg0")
3. One of the following browsers installed:
   - Chromium (preferred)
   - Firefox
   - Chrome
4. Properly populated skill datasets:
   - `skills/elementary_skills.json`
   - `skills/skill_decompositions.json`
   - `skills/semantic_cache.json`

### Test Data

1. Create a backup of the existing postings directory
2. Set up a test output directory for storing test results

## Test Scenarios

### Scenario 1: Basic Pipeline Execution

**Description:** Test the basic end-to-end flow with default parameters

**Steps:**
1. Run the orchestrator with a small number of jobs
2. Check that job data is correctly fetched and stored
3. Verify skill decomposition was performed
4. Verify self-assessment was generated
5. Check report generation

**Code:**
```python
from scripts.career_pipeline.orchestrator import run_pipeline

result = run_pipeline(
    max_jobs=5,  # Limit to 5 jobs for testing
    delay=2.0,   # Add slightly longer delay to be polite to the API
    generate_reports=True
)

assert result["success"] == True
assert result["jobs_count"] > 0
assert result["processed_jobs"] > 0
assert result["skill_decomposer_ran"] == True
```

### Scenario 2: Job Repair Functionality

**Description:** Test the ability to repair specific job records by refetching details

**Steps:**
1. Identify a few existing job IDs from the postings directory
2. Run the orchestrator in repair mode
3. Verify the job details were refreshed

**Code:**
```python
from scripts.career_pipeline.orchestrator import run_pipeline
import os
import json

# Get some existing job IDs
job_ids = []
job_dir = "/home/xai/Documents/sunset/data/postings"
for file in os.listdir(job_dir)[:3]:  # Get first 3 job files
    if file.startswith("job") and file.endswith(".json"):
        job_id = file.replace("job", "").replace(".json", "")
        job_ids.append(job_id)

# Run repair on these jobs
result = run_pipeline(
    repair_job_ids=job_ids,
    run_skill_decomposer=True
)

assert result["success"] == True
assert result["repaired_jobs"] >= 1
```

### Scenario 3: Processing Incomplete Jobs

**Description:** Test the ability to find and process jobs with incomplete information

**Steps:**
1. Run the process_incomplete_job_files function
2. Verify that incomplete jobs are properly processed
3. Check that skill decomposition and matching are performed

**Code:**
```python
from scripts.career_pipeline.orchestrator import process_incomplete_job_files

result = process_incomplete_job_files(force_reprocess=False)

assert result["success"] == True
print(f"Processed {result['processed_jobs']} incomplete jobs")
```

### Scenario 4: Error Handling and Recovery

**Description:** Test how the system handles and recovers from errors

**Steps:**
1. Temporarily disable network access or introduce a simulated connection error
2. Run the pipeline and observe error handling
3. Restore network access and verify recovery
4. Check log files for appropriate error messages

### Scenario 5: Performance Testing

**Description:** Test the pipeline's performance with a larger dataset

**Steps:**
1. Run the pipeline with a higher job count (e.g., 50-100 jobs)
2. Monitor system resource usage during execution
3. Measure completion time
4. Verify data integrity of all processed jobs

### Scenario 6: Self-Assessment Consistency Testing

**Description:** Test the consistency of self-assessment results across similar job types

**Steps:**
1. Identify pairs of jobs in the same domain that have drastically different match scores
2. Analyze the qualification narratives generated for these jobs
3. Verify that the skill matching logic is consistent across job types
4. Investigate specific cases like the Tax Senior roles contradiction (Job 61951 at 33% match rate vs Job 61964 at 100% match rate)

**Code:**
```python
from scripts.utils.self_assessment.generator import SelfAssessmentGenerator
from scripts.skill_decomposer.persistence import JobData
import os
import json

# Test case: Tax Senior job contradictions
job_ids = ["61951", "61964"]
job_files = [f"/home/xai/Documents/sunset/data/postings/job{job_id}.json" for job_id in job_ids]

# Load job data
jobs = []
for job_file in job_files:
    with open(job_file, 'r') as f:
        job_data = json.load(f)
        jobs.append(job_data)
        
# Compare the requirements and skill matches
requirements_1 = set([req['requirement'] for req in jobs[0].get('requirements', [])])
requirements_2 = set([req['requirement'] for req in jobs[1].get('requirements', [])])

common_requirements = requirements_1.intersection(requirements_2)
unique_to_job1 = requirements_1 - requirements_2
unique_to_job2 = requirements_2 - requirements_1

match_score_1 = jobs[0].get('self_assessment', {}).get('overall_match', 0)
match_score_2 = jobs[1].get('self_assessment', {}).get('overall_match', 0)

print(f"Job {job_ids[0]} match score: {match_score_1*100}%")
print(f"Job {job_ids[1]} match score: {match_score_2*100}%")
print(f"Common requirements: {len(common_requirements)}")
print(f"Requirements unique to job {job_ids[0]}: {len(unique_to_job1)}")
print(f"Requirements unique to job {job_ids[1]}: {len(unique_to_job2)}")

# Further investigation of missing/failed matches in the job with lower score
low_score_job = jobs[0] if match_score_1 < match_score_2 else jobs[1]
low_score_id = job_ids[0] if match_score_1 < match_score_2 else job_ids[1]

missing_skills = [req.get('requirement') for req in low_score_job.get('matches', {}).get('missing_skills', [])]
print(f"Missing skills in job {low_score_id}: {missing_skills}")
```

**Expected Results:**
1. Identification of qualification assessment inconsistencies
2. Analysis report of requirement differences between similar jobs
3. Recommendations for improving the matching algorithm's consistency

## Test Validation

### Expected Outputs

After running the tests, the following outputs should be verified:

1. Job data files in the specified output directory
2. Job detail data correctly extracted and stored
3. Skill decomposition results for each job
4. Self-assessment documents for qualifying jobs
5. Summary reports and logs correctly generated

### Validation Checks

For each job processed:

1. Verify that the job JSON file contains:
   - Basic job metadata (title, company, location)
   - Detailed job description
   - Requirements section
   - Skill decomposition results (if enabled)
   - Match data (if enabled)

2. Check report files for:
   - Correct job counts
   - Summary statistics
   - Error reporting (if applicable)

## Troubleshooting Common Issues

1. **API Access Problems**
   - Verify credentials.json is properly configured
   - Check for IP blocking and test VPN rotation

2. **Browser Automation Errors**
   - Ensure preferred browser is installed and properly configured
   - Check for browser updates that might affect automation

3. **Skill Decomposer Errors**
   - Verify semantic cache structure and integrity
   - Check elementary skills database is properly populated
   - Ensure Ollama is running and has the required models installed:
     ```bash
     # Check if Ollama is running
     curl http://localhost:11434/api/version
     
     # List available models
     curl http://localhost:11434/api/tags
     
     # If needed, pull the required model (typically llama3.2)
     ollama pull llama3.2
     ```
   - Note: Ollama may show warnings like `msg="key not found" key=general.alignment default=32` in the logs. These are normal and can be safely ignored as long as the API calls return status code 200.

4. **File System Errors**
   - Check directory permissions
   - Verify disk space availability

## Schedule

1. Setup and Preparation: 1 day
2. Test Execution: 2-3 days
3. Result Analysis: 1 day
4. Documentation and Reporting: 1 day

## Conclusion

This end-to-end test plan provides comprehensive coverage of the Project Sunset career pipeline orchestration system. By executing these tests, we can ensure that all components work together correctly and that the system can handle realistic usage scenarios.

Successful completion of these tests will validate that the career pipeline can reliably fetch job data, process job details, perform skill matching, and generate necessary reports and documentation for the job application process.