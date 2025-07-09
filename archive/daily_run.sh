#!/bin/bash
# Daily Job Pipeline Runner
# Usage: ./daily_run.sh [options]

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🌅 Daily Job Pipeline Starting...${NC}"
echo "📅 Date: $(date)"
echo "📂 Working directory: $(pwd)"
echo

# Change to the script directory
cd "$(dirname "$0")"

# Check if virtual environment exists and activate it
if [ -d "venv" ]; then
    echo -e "${YELLOW}🐍 Activating virtual environment...${NC}"
    source venv/bin/activate
elif [ -d ".venv" ]; then
    echo -e "${YELLOW}🐍 Activating virtual environment...${NC}"
    source .venv/bin/activate
fi

# Run the Python pipeline with all arguments passed through
echo -e "${GREEN}🚀 Running daily pipeline...${NC}"
python run_daily_pipeline.py "$@"

# Check exit code
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Daily pipeline completed successfully!${NC}"
    echo "📊 Check the output/excel/ directory for your job matches report"
    echo "📧 Check your email for the daily summary"
else
    echo -e "${RED}❌ Daily pipeline failed!${NC}"
    echo "📋 Check the logs/daily_pipeline/ directory for error details"
    exit 1
fi
