# Feedback Loop Integration Plan

## Goal
Integrate the feedback loop (job match, feedback, re-match) into `run_pipeline/run.py` for unified pipeline execution and easier testing.

## Steps & Progress

### 1. Planning and Documentation
- [x] Define integration steps and requirements
- [ ] Track progress in this file

### 2. Code Integration
- [x] Import feedback loop functions from `run_pipeline.job_matcher`
- [x] Add CLI/function options to trigger feedback loop in `run.py`
- [x] Implement feedback loop function in `run.py`:
    - [x] Run job match
    - [x] Accept/simulate feedback
    - [x] Process feedback
    - [x] Optionally re-run job match
- [ ] Add output/logging for results and changes
- [ ] Test with sample job and feedback

### 3. Documentation
- [ ] Update this file with progress and code snippets
- [ ] Create `Feedback_Loop_Manual.md` with user instructions

---

## Notes
- Use `run_pipeline/test_feedback_loop.py` as a reference for the feedback loop logic.
- Ensure all imports use the new `run_pipeline.job_matcher` structure.
- CLI should allow specifying job ID, feedback, and options for auto-update and saving results.

### [2025-05-25] Integration Progress
- [x] Added feedback loop imports and function to `run_pipeline/run.py`
- [x] Added CLI options: `--feedback-loop`, `--job-id`, `--feedback`, `--auto-update`, `--save`
- [x] Feedback loop can now be run from the main entry point
- [x] Tested feedback loop integration via run.py CLI. Results saved to feedback_loop_result.json. Integration is working as expected.
