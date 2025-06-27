#!/bin/bash
# Simple script to get OLMo2 feedback on SDR implementation

# Set working directory
cd "$(dirname "$0")"
PROJECT_ROOT="$(cd ../../.. && pwd)"

# Define paths
PROMPT_FILE="${PROJECT_ROOT}/docs/skill_matching/olmo_simple_prompt.txt"
OUTPUT_FILE="${PROJECT_ROOT}/docs/skill_matching/olmo2_sdr_feedback.md"

# Create a simpler prompt
cat > "${PROMPT_FILE}" << EOF
You are OLMo2, an advanced language model specialized in understanding skill taxonomies.

I'm working on improving the Skill Domain Relationship (SDR) framework which we've implemented to reduce false positives in skill matching. The framework standardizes skill definitions and considers domain relationships.

Currently, each skill is enriched with this structure:
\`\`\`json
{
  "name": "Basic Process Automation",
  "category": "IT_Technical",
  "knowledge_components": ["workflow_analysis", "scripting", "process_improvement"],
  "contexts": ["office", "business_process"],
  "functions": ["efficiency_improvement", "task_simplification"]
}
\`\`\`

Please provide detailed feedback on:

1. How to improve our skill definition structure for better domain-aware matching
2. Additional components we should add to skill definitions beyond knowledge, contexts, and functions
3. Best practices for using LLMs to generate high-quality skill enrichments
4. How to ensure consistency across different domains
5. Common pitfalls to avoid when standardizing skill definitions

Please provide specific, actionable recommendations.
EOF

echo "Getting feedback from OLMo2..."
echo "This may take a minute or two..."

# Create the header for the output file
cat > "${OUTPUT_FILE}" << EOF
# OLMo2 Feedback on SDR Implementation

*Generated on: $(date)*

EOF

# Use ollama directly with the prompt and append the response to the output file
ollama run olmo2:latest < "${PROMPT_FILE}" >> "${OUTPUT_FILE}"

# Check if the file was updated successfully
if [ $? -eq 0 ] && [ -s "${OUTPUT_FILE}" ]; then
  echo "Feedback saved to ${OUTPUT_FILE}"
  echo
  echo "Preview of OLMo2's feedback:"
  echo "----------------------------"
  head -n 15 "${OUTPUT_FILE}"
  echo "..."
else
  echo "Error: Failed to get feedback from OLMo2"
fi
