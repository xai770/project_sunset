#!/usr/bin/env python3
"""
Test migration of job_matcher to run_pipeline.
"""
import sys
import traceback
from pathlib import Path

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
print(f"PROJECT_ROOT: {PROJECT_ROOT}")
print(f"sys.path: {sys.path}")

def test_imports():
    """Test that imports work correctly after migration."""
    try:
        # Import modules from run_pipeline.job_matcher
        from run_pipeline.job_matcher.job_processor import process_job
        from run_pipeline.job_matcher.cv_utils import get_cv_markdown_text
        from run_pipeline.job_matcher.feedback_handler import save_feedback, analyze_feedback
        from run_pipeline.job_matcher.prompt_adapter import get_formatted_prompt
        
        print("✅ All imports successful!")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_prompt_loading():
    """Test that prompts can be loaded correctly."""
    try:
        from run_pipeline.job_matcher.prompt_adapter import get_formatted_prompt
        
        # Try to get a prompt
        prompt = get_formatted_prompt('llama3_cv_match', category='job_matching', 
                                     cv="Sample CV", job="Sample job description")
        
        if prompt and "Sample CV" in prompt and "Sample job description" in prompt:
            print("✅ Prompt loaded successfully!")
            return True
        else:
            print("❌ Prompt loading failed: Prompt does not contain placeholders")
            return False
    except Exception as e:
        print(f"❌ Prompt loading error: {e}")
        return False

if __name__ == "__main__":
    print("Testing migration of job_matcher to run_pipeline...")
    
    # Test imports
    imports_ok = test_imports()
    
    # Test prompt loading
    prompt_ok = test_prompt_loading()
    
    # Overall status
    if imports_ok and prompt_ok:
        print("\n✅ Migration successful!")
        sys.exit(0)
    else:
        print("\n❌ Migration has issues that need to be fixed.")
        sys.exit(1)
