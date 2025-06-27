# Copilot Instructions: Fix Critical LLM Job Evaluation Bug

## Problem Summary
The JMFS pipeline's LLM evaluation is producing **incorrect "Good match" ratings** for jobs that should obviously be "Low match". Manual testing with the same LLM models (llama3.2, phi3, olmo2) produces correct results, so **the bug is in the pipeline code, not the LLM**.

## Evidence of the Bug

### **Manual LLM Testing (CORRECT RESULTS):**
```
- llama3.2:latest → "Moderate match" (conservative)
- olmo2:latest → "Low match" (correctly harsh)  
- phi3:latest → "Low match" (correctly harsh)
```

### **Pipeline Results (WRONG RESULTS):**
```
- Model Validation Specialist (Treasury) → "Good match" ❌
- Real Estate Economist → "Good match" ❌  
- Tax Sales Function → "Good match" ❌
```

These are **obvious mismatches** requiring:
- Mathematical degrees (user has none)
- Python/R programming for math modeling (user does none)
- Domain expertise user completely lacks

## Root Cause Analysis Required

The bug is somewhere in the pipeline's LLM evaluation process. **Investigate these areas:**

### **1. Prompt Comparison**
**Check if pipeline uses different prompt than this working manual version:**

```
### 1.1.1. Compare the role requirements carefully with the evidence in the CV. Based on your careful comparison, determine the CV-to-role match level: 
- **Low match:** if the CV does not state direct experience in any key requirement of the role title and details (e.g., specific technology, industry, or critical skill explicitly required). THIS RULE IS ALWAYS VALID!
- **Moderate match:** if I have gaps in secondary requirements. 
- **Good match:** if I have only minor gaps and decide to apply.
```

**Key differences to look for:**
- Missing the critical "THIS RULE IS ALWAYS VALID!" enforcement
- Weakened criteria for "Low match"
- Different scoring logic

### **2. Job Description Corruption**
**Verify job descriptions reaching the LLM are complete and accurate:**
- Check if concise_description is truncated
- Verify requirements section is intact
- Ensure no text encoding issues

### **3. Response Parsing Bugs**
**Check how pipeline parses LLM responses:**
- Look for regex/string matching errors
- Verify match level extraction logic
- Check for case sensitivity issues

### **4. Decision Logic Errors**
**Examine final decision aggregation:**
- How are multiple LLM responses combined?
- Is there override logic that's broken?
- Check for default values masking real responses

## Files to Investigate

### **Primary Suspects:**
- `run_pipeline/job_matcher/` - LLM evaluation logic
- `run_pipeline/core/skills_module.py` - May contain evaluation
- Any prompt template files
- Response parsing utilities

### **Key Questions:**
1. **What exact prompt is being sent to the LLM?**
2. **What raw response is the LLM returning?**
3. **How is that response being parsed into match levels?**
4. **Is there any post-processing changing the results?**

## Expected Fixes

### **If Prompt Issue:**
- Update prompt to match the working manual version
- Ensure "THIS RULE IS ALWAYS VALID!" constraint is enforced
- Make "Low match" criteria more strict

### **If Parsing Issue:**
- Fix regex/string matching for match levels
- Handle edge cases in response format
- Add better error handling for malformed responses

### **If Logic Issue:**
- Fix decision aggregation logic
- Remove any inappropriate override mechanisms
- Ensure conservative match assessment

## Testing Strategy

### **Test with Known Bad Jobs:**
Use these obviously wrong matches as test cases:
- Job 61907: Model Validation Specialist (needs math degree + Python)
- Job 63587: Real Estate Economist (needs RE degree + DCF modeling)
- Job 63625: Tax Sales Function (needs Tax Advisor certification)

### **Expected Results After Fix:**
All three should return "Low match" with proper no-go rationales.

### **Validation:**
Compare pipeline results with manual LLM testing using identical prompts.

## Debug Output Needed

**Add logging to capture:**
```python
print("=== LLM EVALUATION DEBUG ===")
print("Job ID:", job_id)
print("Job Title:", job_title)
print("Prompt sent to LLM:", prompt_text)
print("Raw LLM response:", llm_response)
print("Parsed match level:", parsed_match_level)
print("Final decision:", final_decision)
print("========================")
```

## Critical Importance

This bug is **breaking the entire JMFS system**. The job matching is the core functionality - if it's recommending obviously bad matches as "Good", the system is worse than useless. 

**Priority: CRITICAL** - This needs to be fixed before any other features.

## Context from Senior Claude

The LLM evaluation was working in earlier versions but seems to have broken during recent integration. The manual prompt proves the LLM logic is sound, so focus on finding where the pipeline implementation diverges from the working manual approach.

**Success Criteria:**
- Pipeline produces same results as manual LLM testing
- Obviously bad matches get "Low match" ratings
- Job evaluation becomes trustworthy for user decision-making