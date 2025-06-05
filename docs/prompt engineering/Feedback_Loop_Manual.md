# Feedback Loop Manual

This manual explains how to use the integrated feedback loop in the job matching pipeline.

## What is the Feedback Loop?
The feedback loop allows you to:
1. Run a job match for a given job and CV
2. Provide feedback on the match result
3. Process the feedback to improve the matching logic
4. Optionally re-run the job match to see the effect of the feedback

## How to Use

### From the Command Line
You can run the feedback loop directly from the main pipeline entry point:

```bash
python3 run_pipeline/run.py --feedback-loop --job-id <JOB_ID> --feedback "<Your feedback here>" [--auto-update] [--save <output.json>]
```

- `--feedback-loop`: Run the feedback loop instead of the main pipeline
- `--job-id`: The job ID to test
- `--feedback`: The feedback text to provide
- `--auto-update`: (Optional) Automatically update the prompt based on feedback analysis
- `--save <output.json>`: (Optional) Save the results to a file

#### Example
```bash
python3 run_pipeline/run.py --feedback-loop --job-id 61691 --feedback "The match level should be Good instead of Moderate because the CV shows experience in all required domain-specific areas" --auto-update --save feedback_loop_result.json
```

## Output
- The script will print the original and updated match levels, and whether the match changed after feedback.
- If you use `--save`, results will be saved to the specified file.

## Notes
- The feedback loop uses the same logic as the main job matcher and feedback handler modules.
- You can use this feature to test improvements, debug matching logic, or demonstrate the effect of user feedback on job matching results.

---

For more details, see `docs/prompt engineering/Feedback_Loop_Integration.md`.
