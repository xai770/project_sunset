#!/usr/bin/env python3
"""
Script to register the llama3_cv_match prompt with the prompt manager system.
"""
import sys
from pathlib import Path

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Import prompt manager functions
from run_pipeline.utils.prompt_manager import add_prompt_version

# Read prompt from file
prompt_path = PROJECT_ROOT / "run_pipeline" / "prompts" / "job_matching" / "v1" / "llama3_cv_match.txt"
if not prompt_path.exists():
    prompt_path = PROJECT_ROOT / "prompts" / "job_matching" / "v1" / "llama3_cv_match.txt"

if not prompt_path.exists():
    print(f"Error: Prompt file not found at {prompt_path}")
    sys.exit(1)

with open(prompt_path, 'r', encoding='utf-8') as f:
    prompt_text = f.read()

# Register the prompt
prompt_type = "job_matching_llama3_cv_match"
version = add_prompt_version(
    prompt_type,
    prompt_text,
    description="CV to job matching prompt for Llama 3.2",
    author="MigratedSystem",
    set_active=True
)

if version:
    print(f"✅ Successfully registered prompt '{prompt_type}' with version {version}")
    sys.exit(0)
else:
    print(f"❌ Failed to register prompt '{prompt_type}'")
    sys.exit(1)
