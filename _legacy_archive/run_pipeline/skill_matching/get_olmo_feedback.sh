#!/bin/bash
# Script to get OLMo2's feedback on SDR implementation

# Setting up paths
PROJECT_ROOT="/home/xai/Documents/sunset"
PROMPT_FILE="$PROJECT_ROOT/docs/skill_matching/olmo_prompt_full.txt"
OUTPUT_FILE="$PROJECT_ROOT/docs/skill_matching/olmo2_sdr_feedback.md"

# Ensuring we're in the project root
cd "$PROJECT_ROOT"

# Check if Ollama is installed and running
if ! command -v ollama &> /dev/null; then
    echo "Error: Ollama is not installed"
    exit 1
fi

if ! ollama list | grep -q olmo2; then
    echo "Error: OLMo2 model not found in Ollama"
    exit 1
fi 

echo "# OLMo2 Feedback on SDR Implementation" > "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"
echo "*Generated on: $(date)*" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

echo "Getting feedback from OLMo2..."
echo "This may take a minute or two..."

# Using ollama to get feedback with the API method
echo '# OLMo2 Response on Skill Domain Relationship Framework' >> "$OUTPUT_FILE"
echo '' >> "$OUTPUT_FILE"

# Try using the Ollama API directly
PROMPT_CONTENT=$(cat "$PROMPT_FILE")
curl -s -X POST http://localhost:11434/api/generate -d "{
  \"model\": \"olmo2:latest\",
  \"prompt\": \"$PROMPT_CONTENT\",
  \"stream\": false
}" | jq -r '.response' >> "$OUTPUT_FILE" 2>/dev/null

if [ $? -ne 0 ]; then
    echo "Error using the Ollama API. Trying the command line approach..."
    timeout 300 ollama run olmo2:latest < "$PROMPT_FILE" >> "$OUTPUT_FILE" 2>/dev/null
    
    if [ $? -eq 124 ]; then
        echo "The request timed out after 5 minutes."
        echo "" >> "$OUTPUT_FILE"
        echo "**Note:** The request timed out after 5 minutes." >> "$OUTPUT_FILE"
    fi
fi

echo "Feedback saved to $OUTPUT_FILE"

# Display the first few lines of the feedback
echo ""
echo "Preview of OLMo2's feedback:"
echo "----------------------------"
head -n 10 "$OUTPUT_FILE"
echo "..."
