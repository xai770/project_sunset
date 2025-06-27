# Task-centric LLM Management (TLM) Implementation Plan

## Implementation Status (Updated May 13, 2025)

### Completed
- ✅ Initial TLM framework setup and core components
- ✅ Task definition schema for job detail extraction
- ✅ Integration of TLM with job detail extraction
- ✅ Toggle mechanism in orchestrator for TLM extraction
- ✅ Unit tests for TLM-powered job extractor
- ✅ Integration test script for comparison testing
- ✅ Cookie consent dialog handler implementation
- ✅ Browser automation enhancements for anti-scraping measures
- ✅ Firefox-based job extraction implementation
- ✅ Verification of extraction success with pre-accepted cookies
- ✅ Enhanced TLM framework with property-specific validation
- ✅ Fixed validation issue for job_id field
- ✅ Complete integration of Firefox extractor with TLM framework
- ✅ Updated task definitions to use property-specific validation
- ✅ Addressing web scraping challenges (403 Forbidden errors & cookie consent dialogs)
- ✅ Improved TLM prompts for accurate job title extraction
- ✅ Fixed directory paths for job data storage to use /data/postings/
- ✅ Implemented fallback job title extraction for when LLM returns generic titles
- ✅ Fixed variable naming consistency in skill decomposition function
- ✅ Optimized job data storage by removing redundant full_description field
- ✅ Added full job workflow test with verification and cleanup steps
- ✅ Enhanced job_fetcher.py to properly filter for Frankfurt jobs (client-side filtering)
- ✅ Created verify_and_fix_clean_descriptions.py to ensure all jobs have clean descriptions
- ✅ Implemented reset_and_rebuild_jobs.sh for complete repository rebuilding
- ✅ Fixed pagination in job fetcher to handle large numbers of total jobs (max_total_to_check=1000)
- ✅ Corrected variable inconsistency in job fetcher (frankfurt_jobs_in_batch vs actual_frankfurt_jobs)

### In Progress
- 🔄 Basic Firefox HTML extraction with TLM processing
- 🔄 Simplified pipeline integration with TLM approach
- 🔄 Testing LLM-based extraction with gemma3 and llama3 models
- 🔄 Improving job description quality by addressing LLM artifacts in extracted content

### Next Steps (Revised)
- Test Firefox extraction + TLM processing with Deutsche Bank careers site
- Complete basic integration with skill decomposer
- Stabilize pipeline with error handling and fallback options
- Develop performance monitoring to identify bottlenecks
- Add essential unit tests for key components
- Create basic documentation for team usage

## Cookie Consent & Scraping Challenges Solution (Updated May 11, 2025)

### Problem Statement
- Deutsche Bank careers website presents cookie consent dialogs that block automated content extraction
- After accepting cookies, the site may return 403 Forbidden errors due to anti-scraping measures
- Browser automation needs to appear more human-like to avoid triggering security measures

### Cookie Consent Handler Implementation
- Created a general cookie consent handler (`cookie_handler.py`) with:
  - Text-based button detection
  - Selector-based dialog handling
  - Dialog pattern database for different sites
  - Session caching to avoid repeated handling

- Implemented Deutsche Bank specific handler (`db_cookie_handler.py`) with:
  - Specialized selectors for OneTrust cookie banners
  - Multiple acceptance techniques (button text, selectors, JavaScript)
  - Position-based clicking as a fallback method
  
### Browser Automation Enhancements
- Added anti-detection measures:
  - Disabled automation control features in Chromium (`--disable-blink-features=AutomationControlled`)
  - Custom user agent configuration
  - More natural timing between actions with variable delays
  
- Improved content extraction:
  - Added JavaScript-based extraction as an alternative to clipboard
  - Implemented page refresh after cookie acceptance to ensure proper session setup
  - Added content validation to detect 403 errors in extracted content
  
- Enhanced error handling:
  - Graceful recovery from failed cookie acceptance with multiple techniques
  - Multiple extraction attempts with different methods (keyboard shortcuts, JavaScript)
  - Detailed logging for troubleshooting extraction issues

### Testing and Validation
- Created test scripts to verify cookie handling functionality:
  - `test_cookie_handling.py`: Automated test for cookie handling and content extraction
  - `quick_cookie_test.py`: Visual verification test for cookie acceptance

- Implemented progressive enhancement strategy:
  1. Try specialized DB cookie handler first
  2. Fall back to selector-based approach if needed
  3. Use general cookie handler as last resort
  4. Multiple content extraction techniques with validation

## Code Organization

### Directories and Files Structure
- All TLM framework code is located in `scripts/tlm/`
- Task definitions are stored as JSON in `config/task_definitions/`
- Task execution logs are stored in `data/task_executions/`
- Tests are located in `tests/`
- Browser automation and scraping utilities in `scripts/career_pipeline/utils/`
  - Added cookie handlers: `cookie_handler.py` and `db_cookie_handler.py`
  - Added JavaScript content extraction in `js_content_extractor.py`

### Key Components
- `task_executor.py`: Core execution engine
- `models.py`: Model selection and management
- `template_engine.py`: Prompt template rendering
- `validation.py`: Input/output validation
- `verification/`: Output verification methods
- `execution_logger.py`: Execution logging
- `tlm_cli.py`: Command-line interface for the TLM framework

## Phase 1: Foundation (Week 1-2)

### 1. Task Definition Schema
- Create JSON schema for task definitions
- Develop validation utilities for task definitions
- Set up storage mechanism for task definitions

### 2. Core Task Library
- Convert existing LLM operations to TLM task definitions:
  - Job detail extraction
  - Skill decomposition
  - Self-assessment generation
  - Domain relationship analysis
  - Cover letter generation

### 3. Basic Task Execution Engine
- Create TaskExecutor class to handle:
  - Task loading and validation
  - Model selection
  - Prompt rendering
  - Basic result validation

## Phase 2: Verification Methods (Week 3)

### 1. Verification Framework
- Design extensible verification interface
- Implement verification methods:
  - Consensus verification (using multiple models)
  - Basic output validation (schema checking)
  - Hierarchical verification (LLM reviews output)

### 2. Fallback Strategies
- Implement configurable fallback mechanisms:
  - Use highest-ranked model
  - Human review request
  - Error reporting and logging

### 3. Similarity Metrics
- Implement text similarity metrics:
  - String-based similarity (difflib)
  - Token-based similarity
  - Semantic similarity (embeddings)

## Phase 3: Logging and Analysis (Week 4)

### 1. Execution Logging
- Design and implement TaskExecution schema
- Create storage mechanism for execution logs
- Implement logging throughout task execution flow

### 2. Performance Analysis Tools
- Create tools to analyze execution logs:
  - Model performance by task type
  - Success rates and patterns
  - Execution time and token usage

### 3. Recommendation System
- Develop algorithms to generate:
  - Model selection recommendations
  - Prompt improvement suggestions
  - Verification parameter optimizations

## Phase 4: Integration (Week 5-6)

### 1. Update Existing Systems
- Refactor llm_task_optimizer.py to use TLM
- Update consensus_job_extractor.py to use verification framework
- Modify self-assessment generation to use task definitions

### 2. Advanced Features
- Task dependency management
- Multi-stage task workflows
- Adaptive verification based on task criticality
- Batching and caching optimization

### 3. Documentation and Testing
- Comprehensive documentation of framework
- Unit tests for all components
- Integration tests for end-to-end workflows
- Performance benchmarks

## Key Deliverables

1. **Task Definition Library**
   - JSON schema files
   - Task definition examples
   - Validation utilities

2. **Task Execution Engine**
   - Core execution framework
   - Model selection integration
   - Prompt rendering system

3. **Verification Framework**
   - Verification method implementations
   - Similarity metric utilities
   - Fallback mechanism handlers

4. **Logging and Analysis System**
   - Execution log storage
   - Analysis and visualization tools
   - Recommendation algorithms

5. **Updated Components**
   - Integration with existing systems
   - Refactored implementations using TLM
   - New task definitions for all LLM operations

## Implementation Challenges

### Web Scraping Limitations
During the implementation of the TLM-powered job extractor, we encountered 403 Forbidden errors when attempting to access the Deutsche Bank careers website. This appears to be due to anti-scraping measures that detect and block automated requests.

**Identified Issues:**
1. **403 Forbidden Errors**: Direct HTTP requests to the Deutsche Bank careers website are being blocked with 403 responses.
2. **Browser Dependency Detection**: The browser automation fallback mechanism wasn't correctly detecting installed browsers due to naming differences (`chromium-browser` vs `chromium`).
3. **Missing Dependencies**: The browser automation requires several dependencies: xdotool, xclip/xsel, psutil Python package, and at least one supported browser.

**Applied Solutions:**
1. **Updated Browser Priority**: Modified the browser detection to prioritize `chromium-browser` which is installed on our system.
2. **Installed Dependencies**: Added missing dependencies including psutil Python package.
3. **Fixed Browser Detection**: Updated the browser automation module to correctly identify available browsers.
4. **Enhanced Anti-Scraping Utilities**: 
   - Implemented sophisticated 403 error handling with multiple retry strategies
   - Added modern browser user-agent rotation
   - Implemented adaptive delays between requests
   - Added specialized handler for Deutsche Bank careers site
5. **Request Fingerprinting**: Improved HTTP request headers to better mimic legitimate browsers with proper Sec-Fetch-* headers, referrers, and language settings.
6. **Cookie Management**: Implemented persistent cookie storage and session management to maintain authenticated sessions across runs.
7. **Testing Framework**: Created a comparison script to evaluate traditional vs. TLM extraction methods with metrics on 403 error rates and success rates.

**Findings on 403 Error Handling:**
1. **User-Agent Impact**: Using modern, up-to-date browser User-Agent strings significantly reduced 403 errors.
2. **Referrer Headers**: Adding Google search as a referrer helped bypass many anti-scraping checks.
3. **Session Persistence**: Maintaining cookies across requests improved success rates.
4. **Browser Fingerprinting**: Adding proper Sec-Fetch-* headers made requests appear more legitimate.
5. **Adaptive Delays**: Implementing variable delays between requests reduced detection rates.

**Additional Recommended Solutions:**
1. **Browser Automation**: Continue focusing on the browser automation approach which is more reliable but requires proper setup.
2. **IP Rotation Strategy**: Enhance with proxy rotation if 403 errors persist.
3. **Headless Browser API**: Consider implementing a headless browser API (Puppeteer/Playwright) as a middle ground between direct HTTP requests and full browser automation.

### TLM Framework Integration Challenges
Other challenges encountered during the implementation include:

1. **Dependency Management**: The TLM framework has dependencies that must be properly handled in different environments
2. **Error Handling**: Robust fallback mechanisms are needed when TLM execution fails
3. **Module Organization**: Maintaining consistent code organization across TLM-powered components
4. **Testing Strategy**: Balancing thorough testing with practical limitations of web scraping

## Recent Improvements

### Anti-Scraping Module Refactoring (May 11, 2025)

To address the persistent 403 Forbidden errors encountered during job detail extraction, we've completely refactored the anti-scraping module with the following improvements:

#### Technical Changes
- **Modular Structure**: Split the monolithic anti_scraping.py into smaller, more maintainable modules
  - `base.py`: Core functionality, dependencies and base classes
  - `session.py`: The AntiScrapingSession class
  - `utils.py`: Helper functions for anti-scraping
  - `site_specific.py`: Site-specific handlers like Deutsche Bank careers
  - Compatibility wrapper for backward compatibility

#### Anti-403 Improvements
- **Enhanced User-Agent Rotation**: Updated with latest browser signatures to avoid detection
- **Advanced Retry Logic**: Specialized multi-step retry process for 403 errors
  1. First attempt with standard headers
  2. Second attempt with enhanced browser-like headers
  3. Final attempt with a completely new session and referrer spoofing
- **Site-Specific Handlers**: Created a specialized handler for Deutsche Bank careers that simulates proper browsing behavior

#### Integration with TLM
- Updated the TLM job extractor to use the specialized DB careers handler
- Created a toggle mechanism to use either traditional or TLM extraction methods
- Implemented session persistence to maintain cookies and successful headers

#### Verification and Testing
- Added comprehensive unit tests for the anti-scraping module
- Created integration tests to compare performance between traditional and TLM-powered extractors
- Developed a verification script to ensure backward compatibility

#### Next Steps
- Monitor success rates with the new anti-scraping methods
- Extend the site-specific handlers to other career portals
- Integrate usage metrics to identify which anti-scraping techniques work best

## Job Title Extraction Improvements (May 12, 2025)

In our recent testing, we identified an issue with job title extraction where LLM models were returning generic titles (e.g., "Senior Software Engineer") rather than the actual job titles from the Deutsche Bank careers website. This issue affected the overall quality of extracted job data and downstream skill decomposition.

### Job Title Extraction Challenges

1. **Generic Title Generation**: Models were generating generic job titles rather than extracting actual titles from the HTML
2. **Inconsistent Output Format**: Job details were not being stored consistently across different extraction methods
3. **Directory Structure**: Job files were being saved in multiple locations rather than the standard `/data/postings/` directory

### Applied Solutions

1. **Enhanced TLM Prompts**: Updated all prompts in `job_detail_extraction.json` with explicit instructions to:
   - Extract the exact job title as it appears in the HTML
   - Look for job titles near specific markers (e.g., "Job ID", "Apply for this job")
   - Avoid generating generic job titles

2. **Fallback Extraction**: Implemented regex-based fallback extraction in `simple_tlm_extractor.py` that:
   - Detects when models return generic titles like "Senior Software Engineer"
   - Uses pattern matching to find the actual job title directly in the HTML
   - Prioritizes titles found near key markers like "Apply for this job" or "Position Overview"

3. **File Path Standardization**: Updated all file paths to consistently use `/data/postings/` as the storage location for extracted job data

### Testing & Validation

We're currently testing the improved extraction with Gemma and Llama models to verify that:
- Job titles are correctly extracted from HTML
- Job details are properly stored in JSON format
- All files are saved in the correct directory

## TLM-Powered Job Data Extraction Enhancement Plan (May 11, 2025)

Following our successful implementation of the TLM framework for job detail extraction, we're now focusing on enhancing the quality and structure of the extracted data. We've identified several areas for improvement to make the extracted job details more useful for downstream tasks like skill decomposition, matching, and self-assessment.

### Current Extraction Challenges

1. **Unstructured HTML Content**: The current extraction process captures large chunks of HTML content that include navigation elements, footers, and other non-relevant information.
2. **Inconsistent Field Extraction**: Job responsibilities and requirements aren't consistently identified and separated.
3. **Missing Useful Fields**: Some fields that would be valuable for analysis (e.g., specific qualifications, needed certifications) are not explicitly extracted.
4. **Non-standardized Output**: Output structure varies between traditional and TLM-powered extraction.

### Revised Enhancement Action Plan (May 11, 2025)

#### Phase 1: Immediate Implementation (Current Focus)

- **Simplified Output Schema**: Focus on the key essential fields first:
  - `job_title`: Title of the position
  - `location`: Location of the job
  - `responsibilities`: List of key responsibilities
  - `requirements`: List of main requirements
  - `contact`: Contact information if available

- **Raw Text Processing**: Use TLM to extract relevant text from raw HTML:
  1. Firefox extracts raw HTML content
  2. TLM processes content to extract relevant job information
  3. Simple text-based extraction without complex field parsing

- **Basic Integration**: Complete minimal viable integration with skill decomposer:
  1. Pass job details from Firefox extraction to TLM
  2. Extract basic requirements for skill decomposition
  3. Pass relevant context to skill decomposer

#### 2. Verification Improvements

- **Field-Specific Verification**: Implement specialized verification for critical fields:
  - Responsibilities verification to ensure they are action-oriented statements
  - Requirements verification to confirm they contain measurable skills
  - Location verification to standardize formatting

- **Cross-Field Consistency**: Add verification rules to ensure consistency between:
  - Job title and required skills
  - Career level and years of experience
  - Required skills and expected qualifications

#### 3. Integration with Skill Decomposer

- **Direct TLM-to-Decomposer Pipeline**: Create a seamless pipeline from TLM extraction to skill decomposition
- **Skill Hint Extraction**: Add specialized extraction of potential skill keywords during job extraction
- **Context Preservation**: Ensure job context (industry, company, role level) is passed to the skill decomposer

#### 4. Advanced Features

- **Custom Job Field Extractors**: Develop specialized extractors for important field types:
  - Technical skill extractor with standardized skill taxonomy alignment
  - Experience level normalizer to convert various formats to standard representation
  - Location and remote work policy extractor

- **Sentiment Analysis**: Add sentiment analysis on job descriptions to identify:
  - Company culture indicators
  - Workplace flexibility
  - Growth opportunities
  - Work-life balance mentions

#### Implementation Schedule (Revised)

| Task | Timeline | Priority | Status |
|------|----------|----------|--------|
| Firefox HTML extraction with TLM processing | Immediate | Critical | In Progress |
| Complete basic TLM integration | 2 days | Critical | In Progress |
| Testing with Deutsche Bank careers site | 2 days | High | Not Started |
| Basic skill decomposer integration | 3 days | High | In Progress |
| Pipeline stabilization | 1 week | High | Not Started |
| Advanced field extraction (future phase) | After stable pipeline | Medium | Deferred |

### Expected Benefits

1. **Enhanced Skill Matching**: More precise extraction of requirements will improve skill matching accuracy.
2. **Better Self-Assessment**: Structured field extraction will enable more targeted self-assessment.
3. **Improved Cover Letters**: Detailed job context will allow for more customized cover letter generation.
4. **Data Analytics**: Structured extraction will enable better job market trend analysis.

### Success Metrics

- **Extraction Accuracy**: >90% accuracy in identifying job requirements and responsibilities
- **Field Coverage**: Successfully extract at least 7 structured fields per job
- **Processing Success**: >95% of jobs successfully processed without falling back to traditional extraction
- **Downstream Impact**: 15% improvement in skill matching precision

## Success Criteria

1. **Standardization**: All LLM operations follow the TLM framework
2. **Reliability**: Improved verification reduces output errors
3. **Efficiency**: Optimized model selection reduces costs and improves speed
4. **Learning**: System demonstrably improves over time based on execution data
5. **Maintainability**: New LLM tasks can be added with minimal code changes
6. **Resilience**: Better handling of anti-scraping measures and network failures

## Deutsche Bank Job Repository Improvements (May 13, 2025)

### Job Acquisition Issues Fixed

#### 1. Frankfurt Job Filtering Enhancement

**Problem:** 
- Deutsche Bank API returns jobs from all locations despite explicitly filtering for Frankfurt
- Our repository was only getting 7-10 Frankfurt jobs while the website shows 75+

**Solution:**
- Enhanced job_fetcher.py with client-side filtering:
  ```python
  # Check if this is a Frankfurt job (strict filtering)
  is_frankfurt_job = False
  job_location = "Unknown"
  all_locations = []
                              
  if "PositionLocation" in job_data and job_data["PositionLocation"]:
      for location in job_data["PositionLocation"]:
          city = location.get("CityName", "").strip()
          country = location.get("CountryName", "").strip()
          loc = f"{city}, {country}"
          all_locations.append(loc)
          
          # Check for Frankfurt specifically - must be exact match
          if city.lower() == "frankfurt" and country.lower() in ["deutschland", "germany"]:
              is_frankfurt_job = True
      
      job_location = ", ".join(all_locations)

  # Skip non-Frankfurt jobs
  if not is_frankfurt_job:
      logger.debug(f"Skipping job {job_id} - not in Frankfurt (locations: {job_location})")
      continue
  ```

- Implemented pagination improvements:
  - Increased maximum jobs to check (max_total_to_check=1000)
  - Fixed variable inconsistency (frankfurt_jobs_in_batch vs actual_frankfurt_jobs)
  - Enhanced loop logic to continue until we get all Frankfurt jobs

**Result:**
- Can now retrieve all Frankfurt jobs (expected 75+ based on website)
- Fixed pagination issues when processing large numbers of jobs
- Improved logging shows Frankfurt vs. non-Frankfurt jobs clearly

#### 2. Clean Description Verification

**Problem:**
- Some job files were missing the clean_description field in web_details
- Others had artifacts from LLM extraction in their clean descriptions

**Solution:**
- Created verify_and_fix_clean_descriptions.py script that:
  - Checks all job files for a valid clean_description field
  - If missing, tries to extract one from the full_description
  - Creates a placeholder description as a last resort
  - Logs all changes and maintains data integrity

**Implementation:**
```python
def verify_and_fix_jobs(job_dir, model="phi3"):
    """
    Verify all jobs have clean descriptions and attempt to fix those that don't
    """
    job_files = sorted([f for f in os.listdir(job_dir) 
               if f.startswith('job') and f.endswith('.json')])
    
    # Process each job file
    for job_file in job_files:
        job_id = job_file.replace('job', '').replace('.json', '')
        job_path = os.path.join(job_dir, job_file)
        
        # Read job data
        with open(job_path, 'r', encoding='utf-8') as f:
            job_data = json.load(f)
        
        # Check if job already has a clean_description
        has_clean_desc = False
        if 'web_details' in job_data:
            if isinstance(job_data['web_details'], dict) and 'clean_description' in job_data['web_details']:
                if job_data['web_details']['clean_description'] and len(job_data['web_details']['clean_description']) > 100:
                    has_clean_desc = True
        
        if not has_clean_desc:
            # Try to extract a clean description or create a placeholder
            # ...then update the job file
```

#### 3. Complete Repository Reset and Rebuild

**Problem:**
- Needed a reliable way to rebuild the entire job repository from scratch
- Manual process was error-prone and time-consuming

**Solution:**
- Created reset_and_rebuild_jobs.sh script that:
  - Takes a backup of existing job data
  - Clears the job repository
  - Fetches job metadata from API with improved filtering
  - Scrapes job details with Firefox automation
  - Extracts clean job descriptions
  - Verifies all jobs have clean descriptions
  - Provides a summary of the rebuild results

**Usage:**
```bash
# Full repository reset and rebuild
bash /home/xai/Documents/sunset/scripts/reset_and_rebuild_jobs.sh

# Job metadata fetching only
python /home/xai/Documents/sunset/scripts/career_pipeline/fetch_and_save_jobs.py --max-jobs 100

# Clean description verification only
python /home/xai/Documents/sunset/scripts/verify_and_fix_clean_descriptions.py
```

### Next Steps for Job Repository

1. **Quality Improvement:**
   - Further refinement of job description extraction to remove LLM artifacts
   - Implementation of multi-model consensus for higher quality extraction
   - Advanced validation of job descriptions against known patterns

2. **Performance Optimization:**
   - API parameter optimization to reduce the need for client-side filtering
   - Caching of previously seen jobs to reduce redundant processing
   - Parallel processing for faster end-to-end workflow

3. **Data Analysis:**
   - Implement job trend analysis based on clean job descriptions
   - Create analytics for job requirements and skills in Frankfurt
   - Build visualization tools for job market insights
