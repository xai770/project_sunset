# Job Processing Issues (May 13, 2025)

## Current Issues

### Issue #1: Incomplete Job Acquisition
**Priority: High**

**Description:**  
The current job acquisition process retrieves only 7-10 jobs, while Deutsche Bank's website shows approximately 75+ positions for the Frankfurt location alone.

**Symptoms:**
- Running `fetch_and_save_jobs.py` with `--max-jobs 100` still results in only 7-10 jobs
- Job counts are consistently low across multiple runs

**Potential Root Causes:**
- API pagination parameters not properly implemented
- Request parameters may be limiting results
- API endpoint might have changed behavior

**Investigation Steps:**
1. Analyze the API request parameters in `career_pipeline/fetch_and_save_jobs.py`
2. Test direct API calls with different pagination parameters
3. Verify if the API has rate limiting or other restrictions

### Issue #2: LLM Output Artifacts
**Priority: Critical**

**Description:**  
Clean job descriptions extracted by LLMs contain model artifacts and instruction fragments that should not be part of the final output.

**Symptoms:**
- Output in `job63239.json` begins with "Here is the extracted job information in the requested format:"
- Similar artifacts may exist in other job files
- These artifacts affect downstream processing and data quality

**Potential Root Causes:**
- Prompt design allows instruction leakage
- LLM (llama3.2:latest) may be prone to including instructions in output
- No post-processing to clean up model artifacts

**Investigation Steps:**
1. Review prompt design in `job_description_cleaner.py`
2. Test alternative models (phi3, mistral) to compare output quality
3. Implement post-processing to detect and remove standard model artifacts
4. Consider prompt engineering techniques to prevent instruction leakage

### Issue #3: Workflow Reliability
**Priority: Medium**

**Description:**  
The end-to-end job processing workflow cannot currently run reliably without manual intervention.

**Symptoms:**
- Failures in one component require manual restart
- Error handling is inconsistent across components
- Documentation for complete process is fragmented

**Potential Root Causes:**
- Insufficient error handling in component scripts
- No retry mechanisms for transient failures
- Lack of comprehensive logging for troubleshooting
- Dependencies between components not properly managed

**Investigation Steps:**
1. Analyze failure points in the current workflow
2. Implement robust error handling in all component scripts
3. Add retry mechanisms for common failure points
4. Enhance logging for better visibility into process status

## Next Steps

1. **API Investigation (Owner: TBD)**
   - Deadline: [TBD]
   - Review API interaction code in `fetch_and_save_jobs.py`
   - Test direct API calls with different parameters
   - Implement pagination if necessary

2. **LLM Quality Enhancement (Owner: TBD)**
   - Deadline: [TBD]
   - Refine prompts to prevent instruction leakage
   - Test alternative models (phi3, mistral)
   - Implement post-processing cleanup
   - Add validation for extraction results

3. **Workflow Reliability (Owner: TBD)**
   - Deadline: [TBD]
   - Add error handling to all components
   - Implement retry mechanisms
   - Enhance logging
   - Create comprehensive documentation
