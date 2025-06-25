# Job Acquisition Process Test Plan

## 1. Overview

This test plan focuses specifically on the job profile acquisition process, which is the core functionality of Project Sunset. It ensures that the process of retrieving job postings from Deutsche Bank, extracting their details, and storing the results works correctly.

## 2. Test Scope

The test plan covers the complete job acquisition flow:

1. **API Access Tests** - Verifying connectivity to Deutsche Bank careers API
2. **Job Filtering Tests** - Ensuring Frankfurt jobs are correctly identified
3. **Browser Scraping Tests** - Testing the Firefox-based scraping functionality
4. **TLM Extraction Tests** - Verifying the TLM-based content extraction
5. **End-to-End Flow Tests** - Testing the complete acquisition pipeline

## 3. Test Approach

### 3.1 API Access Testing

| Test ID | Test Name | Description | Expected Result |
|---------|-----------|-------------|----------------|
| API-01 | Basic API Connectivity | Test connection to Deutsche Bank careers API | Successful connection, jobs retrieved |
| API-02 | API Response Structure | Verify structure of API response | JSON format with expected fields |
| API-03 | Frankfurt Job Filtering | Test filtering for Frankfurt jobs | Only Frankfurt jobs returned |
| API-04 | API Error Handling | Test handling of API errors | Graceful handling, appropriate retries |

### 3.2 Browser Scraping Testing

| Test ID | Test Name | Description | Expected Result |
|---------|-----------|-------------|----------------|
| SCR-01 | Firefox Initialization | Test browser initialization | Browser launched successfully |
| SCR-02 | Content Loading | Test loading job detail pages | Page loads with complete content |
| SCR-03 | HTML Extraction | Test extraction of HTML content | Complete HTML retrieved |
| SCR-04 | Anti-Scraping Measures | Test handling of anti-scraping protections | Content retrieved despite protections |

### 3.3 TLM Extraction Testing

| Test ID | Test Name | Description | Expected Result |
|---------|-----------|-------------|----------------|
| TLM-01 | Basic Extraction | Test TLM extraction from HTML | Structured content extracted |
| TLM-02 | Field Validation | Verify required fields are extracted | All required fields present |
| TLM-03 | Content Quality | Verify quality of extracted content | Clean, relevant content extracted |
| TLM-04 | Error Handling | Test handling of extraction failures | Graceful error handling |
| TLM-05 | Storage Optimization | Test removal of full_description field | Space saved, clean_description preserved |

### 3.4 End-to-End Testing

| Test ID | Test Name | Description | Expected Result |
|---------|-----------|-------------|----------------|
| E2E-01 | Complete Acquisition Flow | Test full job acquisition process | Jobs successfully acquired and stored |
| E2E-02 | File Storage Verification | Verify JSON files are correctly stored | Files created with proper structure |
| E2E-03 | Multiple Jobs Processing | Test processing multiple jobs | All jobs processed correctly |

## 4. Test Implementation Plan

### 4.1 Test File Structure

```
tests/
├── job_acquisition/              # New dedicated test directory
│   ├── test_api_access.py        # API access tests
│   ├── test_job_filtering.py     # Job filtering tests
│   ├── test_browser_scraping.py  # Browser scraping tests
│   ├── test_tlm_extraction.py    # TLM extraction tests
│   └── test_e2e_acquisition.py   # End-to-end acquisition tests
│
└── fixtures/
    └── job_acquisition/
        ├── api_responses/        # Sample API responses
        ├── html_content/         # Sample HTML content
        └── expected_results/     # Expected extraction results
```

### 4.2 Implementation Phases

#### 4.2.1 Phase 1: Unit Tests (1 week)
1. Create API access tests
2. Develop browser scraping tests
3. Implement TLM extraction tests

#### 4.2.2 Phase 2: Integration Tests (1 week)
1. Create tests for API-to-scraper flow
2. Develop tests for scraper-to-TLM flow
3. Implement tests for TLM-to-storage flow

#### 4.2.3 Phase 3: End-to-End Tests (1 week)
1. Create complete acquisition flow tests
2. Develop multi-job processing tests
3. Implement error recovery tests

## 5. Test Execution Strategy

### 5.1 Test Environment

1. **Development Environment**
   - Local Firefox instance
   - Local TLM with Ollama
   - Access to DB careers API
   - Limited to 1-2 job acquisitions per run

2. **Testing Schedule**
   - API tests: Daily
   - Browser tests: Weekly
   - TLM tests: Daily
   - End-to-end tests: Weekly

### 5.2 Test Data

1. **Real API Data**
   - Use actual Deutsche Bank API for testing
   - Cache responses for test consistency

2. **Sample HTML Content**
   - Store representative HTML samples
   - Include various job detail formats

3. **Expected Extraction Results**
   - Define expected TLM extraction outputs
   - Use for comparison in tests

## 6. Success Criteria

1. **API Access**
   - 100% success rate connecting to API
   - All required fields present in responses

2. **Browser Scraping**
   - >95% success rate retrieving HTML content
   - All dynamic content properly loaded

3. **TLM Extraction**
   - >90% success rate extracting structured content
   - All required fields correctly extracted

4. **End-to-End Flow**
   - >95% success rate for complete acquisition
   - Correct file storage and structure

## 7. Test Maintenance

1. Update tests when DB careers website changes
2. Keep sample HTML content up to date
3. Adjust expected results as needed
4. Document any persistent issues or limitations
