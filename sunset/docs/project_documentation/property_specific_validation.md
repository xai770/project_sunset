# Property-Specific Validation in TLM

## Overview

This document describes the implementation of property-specific validation in the Task-centric LLM Management (TLM) framework.

## Problem

Previously, the TLM framework applied all validations defined in a task definition to all input properties. This led to validation errors when a validation rule meant for one property (like minimum length requirements) was incorrectly applied to other properties.

For example, in the job detail extraction task, we had a validation rule called `min_length_100` that was meant to apply only to the `job_posting` field, but was being applied to all fields including the `job_id` field.

## Solution

We have enhanced the TLM validation mechanism to support property-specific validations. This allows task definitions to specify which validation rules apply to which properties.

### Changes Made

1. Modified `TaskExecutor._validate_input` to support property-specific validations
2. Updated task definitions to use the new `property_validations` field instead of the global `validations` field
3. Added backward compatibility for existing task definitions

### Task Definition Example

```json
"input": {
  "schema": {
    "type": "object",
    "properties": {
      "job_posting": {"type": "string"},
      "job_id": {"type": "string"}
    },
    "required": ["job_posting"]
  },
  "validations": ["non_empty_text"],  // Global validations (applied to required fields)
  "property_validations": {           // Property-specific validations
    "job_posting": ["non_empty_text", "min_length_100"],
    "job_id": ["non_empty_text"]
  }
}
```

### Implementation Details

The `TaskExecutor._validate_input` method now:

1. Checks for a new `property_validations` field in the task definition
2. If present, applies validations according to these property-specific rules
3. If not present, falls back to the previous behavior of applying all validations to required fields

## Impact

This enhancement eliminates false validation errors and improves the flexibility of the TLM framework. It allows for more precise validation rules tailored to each property's requirements.

## Testing

We have verified this enhancement with dedicated test scripts:

1. `test_property_validation.py` - Tests the property-specific validation mechanism directly
2. Integration tests with real job extraction scenarios

All tests confirm that the validation now correctly applies only to the properties it should.
