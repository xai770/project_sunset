# Pipeline Workflow Diagram

```mermaid
graph TD
    A[run.py] --> B[pipeline_main.py]
    B --> C[pipeline_orchestrator.py]
    
    subgraph "Core Orchestration"
        C --> D[cli_args.py]
        C --> E[pipeline_utils.py]
    end
    
    subgraph "Configuration"
        C --> F[paths.py]
    end
    
    subgraph "Pipeline Steps"
        C --> G[fetch_module.py]
        C --> H[cleaner_module.py]
        C --> I[status_checker_module.py]
        C --> J[skills_module.py]
        C --> K[skill_matching_orchestrator.py]
        C --> L[auto_fix.py]
    end
    
    subgraph "Fetch Submodules"
        G --> G1[fetch/api.py]
        G --> G2[fetch/job_processing.py]
        G --> G3[fetch/progress.py]
    end
    
    subgraph "Skills Submodules"
        J --> J1[skills_io.py]
        J --> J2[skills_categorization.py]
        J --> J3[skills_decomposition.py]
        J --> J4[skills_importance.py]
    end
    
    subgraph "Skill Matching"
        K --> K1[bucket_matcher.py]
        K1 --> K2[bucketed_skill_matcher.py]
        K1 --> K3[bucket_utils_fixed.py]
        K1 --> K4[embedding_utils.py]
        K1 --> K5[bucket_cache.py]
    end
    
    subgraph "Utilities"
        C --> U1[utils/logging_utils.py]
        H --> U2[utils/llm_client.py]
        G --> U3[utils/common_tools.py]
    end
```

## Pipeline Execution Flow

1. **Entry Point**: `run.py` calls `pipeline_main.py`
2. **Argument Parsing**: `pipeline_main.py` uses `cli_args.py` to parse arguments
3. **Pipeline Orchestration**: `pipeline_orchestrator.py` coordinates all pipeline steps
4. **Step 1 - Fetch Jobs**: `fetch_module.py` retrieves job data from the API
5. **Step 2 - Clean Descriptions**: `cleaner_module.py` cleans and formats job descriptions
6. **Step 3 - Check Status**: `status_checker_module.py` checks if jobs are still available online
7. **Step 4 - Process Skills**: `skills_module.py` extracts and processes skills
8. **Step 5 - Match Skills**: `skill_matching_orchestrator.py` matches skills using the bucketed approach
9. **Step 6 - Auto Fix**: `auto_fix.py` fixes jobs with missing skills or zero matches

Each step has dependencies on various utility modules and submodules as shown in the diagram.
