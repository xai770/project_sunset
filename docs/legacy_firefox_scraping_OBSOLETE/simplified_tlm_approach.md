# Simplified TLM Extraction Approach

This document describes the simplified approach to TLM-based extraction for the Deutsche Bank careers website job postings, focusing on resolving cookie consent and anti-scraping challenges.

## Background

Our previous approach was encountering issues with cookie consent dialogs and 403 Forbidden errors when attempting to extract job posting data from the Deutsche Bank careers website. The old approach was too complex and tried to do too much at once, making it harder to diagnose and resolve issues.

## Simplified Approach

The new simplified approach focuses on:

1. **HTML Extraction First**: Using Firefox to extract the raw HTML content from job posting pages
2. **TLM Processing Second**: Using TLM to process the raw HTML and extract relevant job information
3. **Basic Schema**: Focusing on essential fields only (job title, location, responsibilities, requirements)

## Implementation Components

### 1. Simple TLM Extractor

The `simple_tlm_extractor.py` module provides a straightforward extraction workflow:

```python
def extract_and_process_job(url, job_id=None):
    # Step 1: Extract HTML with Firefox
    extraction_result = extract_job_with_firefox(url, job_id)
    
    # Step 2: Process with TLM
    executor = TaskExecutor("job_detail_extraction")
    tlm_input = {"job_posting": raw_content}
    tlm_result = executor.execute(tlm_input)
    
    # Step 3: Return structured result
    return {
        "job_title": tlm_output.get("job_title", "Unknown"),
        "location": tlm_output.get("location", "Unknown"),
        "responsibilities": tlm_output.get("responsibilities", []),
        "requirements": tlm_output.get("requirements", []),
        ...
    }
```

### 2. Updated TLM Task Definitions

The job detail extraction task has been simplified to focus on essential fields and specifically handle HTML content:

```json
{
  "prompts": [
    {
      "id": "html_extraction",
      "text": "The following text contains HTML from a job posting page. Extract only the essential job details from this HTML content..."
    }
  ]
}
```

### 3. Integrated Pipeline

The updated `tlm_integrated_pipeline.py` script provides a simple workflow:

1. Extract and process job posting with Firefox + TLM
2. Run skill decomposition on the extracted requirements
3. Save both job details and skill decomposition results

## Benefits of Simplified Approach

1. **Easier Debugging**: Separating HTML extraction from content processing makes it easier to identify where issues occur
2. **More Robust**: Less complex processing means fewer points of failure
3. **Better Error Handling**: Each step can have its own error handling and fallback mechanisms
4. **Progressive Enhancement**: We can start with basic functionality and add more advanced features once the pipeline is stable

## Future Enhancements

Once the simplified approach is working reliably, we plan to:

1. Add more sophisticated field parsing
2. Implement advanced verification methods
3. Enhance skill decomposition with domain-specific knowledge
4. Add performance monitoring and optimization

## Testing

The simplified approach can be tested with:

```bash
python scripts/career_pipeline/tlm_integrated_pipeline.py 63141
```

This will extract the job posting with ID 63141 from the Deutsche Bank careers website and process it with the TLM framework.
