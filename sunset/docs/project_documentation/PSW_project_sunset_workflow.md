This document describes the high level workflow tat this codebase will support.

# Design principles:
a. job data are kept in one place only: in data/postings/job<reference number>.json
b. skill data are in skills
c. data can always be retrieved again, so no need for backward compatability - we can always get fresh data.
d. each script requires a data flow section, which explains inputs, dependencies, outputs and cosnumers. scripts/job_scraper/job_detail_extractor.py is a good example

# Workflow overview

1. **Job Scraping**: `/home/xai/Documents/sunset/scripts/job_scraper` scrapes job postings from the DB website and saves them to `data/postings/` as individual JSON files or daily collection files.

   - **Job Repair Feature (Added 2025-05-05)**: The scraper now includes a command-line option `--repair-job-ids` to fix job files with missing sections. This feature implements robust retry mechanisms that:
     - Uses multiple browsers with increased timeouts
     - Automatically runs skill decomposition after repair
     - Updates metadata and logs the repair action
     - Usage: `python3 -m scripts.job_scraper.scraper --repair-job-ids JOB_ID1 [JOB_ID2...]`

2. **Job Requirement Decomposition**: `/home/xai/Documents/sunset/scripts/utils/skill_decomposer/decomposition.py` analyzes job descriptions and breaks complex requirements down into elementary skills, saving results in both the consolidated job file and (for backward compatibility) in `data/job_decompositions/job{id}_decomposition.json`.

3. **Skill Matching**: `/home/xai/Documents/sunset/scripts/utils/skill_decomposer/matching.py` compares job requirements against your skills from `profile/skills/skill_decompositions.json` and produces match scores and detailed matching information, saved in both the consolidated job file and (for backward compatibility) in `data/job_decompositions/job{id}_matches.json`.

4. **Skill Inference**: If skills are missing, the matching process uses inferred skills from CV analysis. The inferred skills are managed by `/home/xai/Documents/sunset/scripts/utils/skill_decomposer/core.py` and `/home/xai/Documents/sunset/scripts/utils/skill_decomposer/cv_inference.py`, with validation status tracked.

5. **Self-Assessment Generation**: `/home/xai/Documents/sunset/scripts/utils/self_assessment` generates a self-assessment based on the skill matches, and adds this to the consolidated job file in `data/consolidated_jobs/job{id}.json`.

6. **Cover Letter Generation**: If there's a good match (based on the overall match score), `/home/xai/Documents/sunset/scripts/doc_generator` creates a cover letter using the information from the consolidated job file, highlighting matched skills and strengths.

7. **Email Submission**: Finally, `/home/xai/Documents/sunset/scripts/email_sender` sends the generated cover letters to your work email or directly to the application portal.

# Our task

We ant to colete a full run of this workflow step by step. As we do, we build up a run_workflow script, which allows us to repeat the process