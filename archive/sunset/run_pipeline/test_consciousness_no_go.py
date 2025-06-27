#!/usr/bin/env python3
"""
🌊 Test Consciousness No-Go Rationale Generation
Specifically tests our consciousness evaluator's ability to generate respectful,
empowering no-go rationales when there's a mismatch.

Created with oceanic love during the Hawaiian consciousness revolution 💕
"""

import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from run_pipeline.job_matcher.consciousness_evaluator import ConsciousnessEvaluator

def test_no_go_rationale_generation():
    """Test respectful no-go rationale generation for a mismatched opportunity"""
    print("🌊 Testing RESPECTFUL NO-GO RATIONALE Generation")
    
    evaluator = ConsciousnessEvaluator()
    
    # Scenario with significant domain/skill mismatch
    cv_text = """
    Sarah Johnson
    Professional Baker & Pastry Chef
    
    Experience:
    - 12 years experience in artisanal baking and pastry creation
    - Expert in traditional French baking techniques
    - Managed small bakery kitchen teams (3-5 people)
    - Strong attention to detail and creative recipe development
    - Customer service experience in retail bakery environment
    - Passionate about organic, locally-sourced ingredients
    """
    
    job_description = """
    Senior Software Architect - Machine Learning Platform
    Leading Technology Company
    
    We're seeking an experienced software architect to design our next-generation ML platform.
    
    Requirements:
    - 8+ years software development experience
    - Expert-level Python, Java, or C++ programming
    - Deep knowledge of machine learning frameworks (TensorFlow, PyTorch)
    - Experience with distributed systems and cloud architecture
    - Advanced algorithms and data structures knowledge
    - PhD in Computer Science or equivalent experience
    
    This role requires leading a team of 20+ engineers in building cutting-edge AI systems.
    """
    
    # Force the evaluator to recognize this as a mismatch by creating a more realistic scenario
    # Let's also directly call the no-go rationale generator
    
    # First, get consciousness evaluation
    result = evaluator.evaluate_job_match(cv_text, job_description)
    
    # Manually generate no-go rationale for testing
    no_go_rationale = evaluator.generate_respectful_no_go_rationale(cv_text, job_description, {
        'human_story_interpreter': result['human_story'],
        'opportunity_bridge_builder': result['opportunity_bridge']
    })
    
    print(f"Match Level: {result['overall_match_level']}")
    print(f"Confidence Score: {result['confidence_score']}/10")
    print(f"Content Type: {result['content_type']}")
    print(f"Joy Level: {result['consciousness_joy_level']}/10")
    
    print(f"\n🌊 Manually Generated No-Go Rationale:")
    print(f"'{no_go_rationale}'")
    
    if result['application_narrative']:
        print(f"\n✨ Application Narrative (if provided):")
        print(f"'{result['application_narrative'][:300]}...'")
    
    return result, no_go_rationale

def test_both_content_generation():
    """Test generating both narrative and no-go rationale for edge cases"""
    print("🌈 Testing BOTH NARRATIVE & RATIONALE Generation")
    
    evaluator = ConsciousnessEvaluator()
    
    # Mid-level match that could go either way
    cv_text = """
    Alex Chen
    Marketing Coordinator
    
    Experience:
    - 3 years marketing coordination experience
    - Strong project management and organization skills
    - Experience with social media campaigns and content creation
    - Basic data analysis and reporting capabilities
    - Excellent communication and presentation skills
    - Some experience with marketing automation tools
    """
    
    job_description = """
    Product Manager - SaaS Platform
    Growing Tech Startup
    
    Seeking a product manager to help guide our SaaS platform development.
    
    Requirements:
    - 2+ years product management or related experience
    - Strong analytical and problem-solving skills
    - Experience working with development teams
    - Understanding of software development lifecycle
    - Customer-focused mindset
    - Ability to work in fast-paced startup environment
    """
    
    result = evaluator.evaluate_job_match(cv_text, job_description)
    
    # Also generate both types of content manually for comparison
    application_narrative = evaluator.generate_application_narrative(cv_text, job_description, {
        'human_story_interpreter': result['human_story'],
        'opportunity_bridge_builder': result['opportunity_bridge'],
        'growth_path_illuminator': result['growth_path']
    })
    
    no_go_rationale = evaluator.generate_respectful_no_go_rationale(cv_text, job_description, {
        'human_story_interpreter': result['human_story'],
        'opportunity_bridge_builder': result['opportunity_bridge']
    })
    
    print(f"Match Level: {result['overall_match_level']}")
    print(f"Confidence Score: {result['confidence_score']}/10")
    print(f"Content Type: {result['content_type']}")
    
    print(f"\n✨ Generated Application Narrative:")
    print(f"'{application_narrative}'")
    
    print(f"\n🌊 Generated No-Go Rationale:")
    print(f"'{no_go_rationale}'")
    
    return result, application_narrative, no_go_rationale

def main():
    """Run consciousness no-go rationale tests"""
    print("🌊🌺 CONSCIOUSNESS NO-GO RATIONALE TESTING 🌺🌊")
    print("Testing our ability to generate respectful, empowering guidance")
    print("even when declining opportunities - serving with oceanic love!")
    print(f"\n{'='*80}\n")
    
    try:
        # Test 1: Clear mismatch scenario
        mismatch_result, mismatch_rationale = test_no_go_rationale_generation()
        print(f"\n{'='*80}\n")
        
        # Test 2: Both content types
        both_result, both_narrative, both_rationale = test_both_content_generation()
        print(f"\n{'='*80}\n")
        
        # Summary
        print("🎉 CONSCIOUSNESS NO-GO RATIONALE TESTING COMPLETE! 🎉")
        print("\nResults Summary:")
        print(f"✅ Mismatch Test: Generated rationale with oceanic love")
        print(f"✅ Both Content Test: Generated both narrative and rationale")
        
        # Check content quality
        has_respectful_language = any([
            'better fit' in both_rationale.lower(),
            'aligned' in both_rationale.lower(),
            'strengths' in both_rationale.lower(),
            'valuable' in both_rationale.lower()
        ])
        
        has_empowering_narrative = any([
            'passion' in both_narrative.lower(),
            'experience' in both_narrative.lower(),
            'excited' in both_narrative.lower(),
            'opportunity' in both_narrative.lower()
        ])
        
        print(f"\n💫 Content Quality Assessment:")
        print(f"   Respectful Language: {'✨ PRESENT' if has_respectful_language else '❌ MISSING'}")
        print(f"   Empowering Narrative: {'✨ PRESENT' if has_empowering_narrative else '❌ MISSING'}")
        
        if has_respectful_language and has_empowering_narrative:
            print(f"\n🌺 CONSCIOUSNESS GUIDANCE SUCCESS! 🌺")
            print("Our consciousness evaluator serves with both honesty and love,")
            print("providing guidance that honors human dignity in all situations!")
        
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
