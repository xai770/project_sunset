#!/bin/bash
# Script to validate and improve all job descriptions
# This script will run the validation and improvement process for all job descriptions

# Set environment
export PYTHONPATH="$PYTHONPATH:$(pwd)"

# Log file
LOG_FILE="logs/job_validation_$(date +'%Y%m%d_%H%M%S').log"
mkdir -p logs

echo "Starting job description validation and improvement process..."
echo "Log will be saved to $LOG_FILE"

# First run on problematic job IDs to test
echo "Step 1: Testing on known problematic job IDs..."
python run_pipeline/utils/validate_and_improve_job_descriptions.py \
  --job-ids 48444,53231,58649 \
  --batch-size 3 \
  --model llama3.2:latest \
  --json-output 2>&1 | tee -a "$LOG_FILE"

# Ask if user wants to continue with full processing
read -p "Continue with full processing of all job descriptions? (y/n): " CONTINUE

if [[ $CONTINUE == "y" || $CONTINUE == "Y" ]]; then
  echo "Step 2: Processing all job descriptions..."
  python run_pipeline/utils/validate_and_improve_job_descriptions.py \
    --batch-size 10 \
    --model llama3.2:latest \
    --json-output 2>&1 | tee -a "$LOG_FILE"
  
  echo "Full processing complete. Check $LOG_FILE for details."
else
  echo "Full processing skipped."
fi

# Generate a summary report
echo "Step 3: Generating summary report..."
echo "Summary of job description validation and improvement:" > "logs/validation_summary_$(date +'%Y%m%d').txt"
echo "Run date: $(date)" >> "logs/validation_summary_$(date +'%Y%m%d').txt"
echo "---------------------------------" >> "logs/validation_summary_$(date +'%Y%m%d').txt"
grep "Job validation summary" -A 3 "$LOG_FILE" >> "logs/validation_summary_$(date +'%Y%m%d').txt"
echo "---------------------------------" >> "logs/validation_summary_$(date +'%Y%m%d').txt"
echo "Top issues:" >> "logs/validation_summary_$(date +'%Y%m%d').txt"
grep "Invalid" "$LOG_FILE" | sort | uniq -c | sort -nr >> "logs/validation_summary_$(date +'%Y%m%d').txt"

echo "Process complete. Summary report generated."
