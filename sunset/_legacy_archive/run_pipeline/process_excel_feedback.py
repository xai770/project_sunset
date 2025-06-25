#!/usr/bin/env python3
"""
Process feedback from an exported Excel file and run the feedback loop for each entry.
"""
import sys
import os
import pandas as pd
from pathlib import Path
from run_pipeline.job_matcher.job_processor import process_feedback

def main(excel_path, job_id_col='job_id', feedback_col='feedback', auto_update=True, save_results=True):
    df = pd.read_excel(excel_path)
    results = []
    for idx, row in df.iterrows():
        job_id = str(row.get(job_id_col, '')).strip()
        feedback = str(row.get(feedback_col, '')).strip()
        if job_id and feedback and feedback.lower() != 'nan':
            print(f"Processing feedback for job {job_id}...")
            result = process_feedback(job_id, feedback, auto_update=auto_update)
            results.append({
                'job_id': job_id,
                'feedback': feedback,
                'result': result
            })
        else:
            print(f"Skipping row {idx}: missing job_id or feedback.")
    if save_results:
        out_path = Path(excel_path).with_name(f"feedback_results_{Path(excel_path).stem}.json")
        import json
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2)
        print(f"Results saved to {out_path}")
    print("Done.")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Process feedback from Excel and run feedback loop.")
    parser.add_argument("excel", help="Path to exported Excel file with feedback column.")
    parser.add_argument("--job-id-col", default="job_id", help="Column name for job ID (default: job_id)")
    parser.add_argument("--feedback-col", default="feedback", help="Column name for feedback (default: feedback)")
    parser.add_argument("--no-auto-update", action="store_true", help="Do not auto-update prompts")
    parser.add_argument("--no-save", action="store_true", help="Do not save results to file")
    args = parser.parse_args()
    main(
        args.excel,
        job_id_col=args.job_id_col,
        feedback_col=args.feedback_col,
        auto_update=not args.no_auto_update,
        save_results=not args.no_save
    )
