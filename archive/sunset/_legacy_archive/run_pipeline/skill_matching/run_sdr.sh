#!/bin/bash
# run_sdr.sh - Shell script to run the SDR implementation

# Set working directory to the project root
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"
cd "$PROJECT_ROOT"

# Display start message
echo "Starting SDR Implementation..."
echo "Date: $(date)"
echo

# Run the implementation
python3 -m run_pipeline.skill_matching.run_sdr_implementation

# Check exit status
if [ $? -eq 0 ]; then
  echo -e "\nSDR implementation completed successfully!"
else
  echo -e "\nSDR implementation encountered errors. Check the logs for details."
fi

echo "Completed at: $(date)"
