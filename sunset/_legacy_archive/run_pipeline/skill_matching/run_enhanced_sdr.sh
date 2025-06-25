#!/bin/bash
# Run Enhanced SDR Implementation with LLM-based Skill Enrichment
#
# This script runs the enhanced SDR implementation with options to use
# LLM-powered skill enrichment based on OLMo2's recommendations.

set -e  # Exit on error

# Set working directory to the script's directory
cd "$(dirname "$0")"

# Define the project root
PROJECT_ROOT="$(cd ../.. && pwd)"

# Create logs directory if it doesn't exist
mkdir -p "$PROJECT_ROOT/logs"

# Log file prefix
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
LOG_FILE="$PROJECT_ROOT/logs/enhanced_sdr_${TIMESTAMP}.log"

# Default options
USE_LLM=false
MAX_SKILLS=50
SKIP_VALIDATION=false

# Print usage
print_usage() {
  echo "Usage: $0 [options]"
  echo "Options:"
  echo "  --use-llm            Use LLM for skill enrichment (higher quality but slower)"
  echo "  --max-skills <num>   Maximum number of skills to analyze (default: 50)"
  echo "  --skip-validation    Skip validation of enriched skills"
  echo "  --help               Show this help message"
}

# Parse command-line arguments
while [[ $# -gt 0 ]]; do
  key="$1"
  case $key in
    --use-llm)
      USE_LLM=true
      shift
      ;;
    --max-skills)
      MAX_SKILLS="$2"
      shift
      shift
      ;;
    --skip-validation)
      SKIP_VALIDATION=true
      shift
      ;;
    --help)
      print_usage
      exit 0
      ;;
    *)
      echo "Unknown option: $1"
      print_usage
      exit 1
      ;;
  esac
done

# Build the command
CMD="python3 run_enhanced_sdr.py"

if [ "$USE_LLM" = true ]; then
  CMD="$CMD --use-llm"
fi

if [ "$SKIP_VALIDATION" = true ]; then
  CMD="$CMD --skip-validation"
fi

CMD="$CMD --max-skills $MAX_SKILLS"

# Run the command
echo "Starting Enhanced SDR implementation with the following options:"
echo "  Use LLM: $USE_LLM"
echo "  Max Skills: $MAX_SKILLS"
echo "  Skip Validation: $SKIP_VALIDATION"
echo "Log file: $LOG_FILE"
echo ""
echo "Running: $CMD"

# Execute the command and log output
$CMD 2>&1 | tee "$LOG_FILE"

# Check execution status
if [ ${PIPESTATUS[0]} -eq 0 ]; then
  echo ""
  echo "Enhanced SDR implementation completed successfully."
  echo "Full log available in: $LOG_FILE"
  echo ""
  echo "Output files in: $PROJECT_ROOT/docs/skill_matching/"
  echo "  - enriched_skills.json"
  echo "  - skill_relationships.json"
  if [ "$SKIP_VALIDATION" = false ]; then
    echo "  - enrichment_validation.json"
  fi
else
  echo ""
  echo "ERROR: Enhanced SDR implementation failed."
  echo "Check the log file for details: $LOG_FILE"
  exit 1
fi
