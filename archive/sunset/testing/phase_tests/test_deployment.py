#!/usr/bin/env python3
"""
Quick test to verify LLM Factory deployment is working.
"""

import sys
sys.path.insert(0, '/home/xai/Documents/sunset')

from run_pipeline.core.phi3_match_and_cover import get_match_and_cover_letter

def test_deployment():
    """Test the deployed LLM Factory integration."""
    print("🧪 Testing Deployed LLM Factory Integration")
    print("=" * 50)
    
    # Sample data
    cv = """John Smith
Software Engineer with 3 years of Python experience.
Skills: Python, Machine Learning, Docker, Git
Education: BS Computer Science
Experience: Built web applications and ML models."""
    
    job_description = """Python Developer position requiring:
- 3+ years Python experience
- Knowledge of ML frameworks
- Experience with Docker and deployment
- Strong problem-solving skills"""
    
    print("📋 Testing job matching and cover letter generation...")
    
    try:
        result = get_match_and_cover_letter(cv, job_description)
        
        print(f"\n✅ Success! Match: {result['match_percentage']}%")
        print(f"📝 Cover letter length: {len(result['cover_letter'])} characters")
        print(f"🔍 Assessment method: {result['fitness_assessment']['assessment_method']}")
        print(f"⭐ Confidence: {result['fitness_assessment']['confidence']}")
        
        print("\n🎉 LLM Factory deployment successful!")
        return True
        
    except Exception as e:
        print(f"\n❌ Deployment test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_deployment()
    sys.exit(0 if success else 1)
