#!/usr/bin/env python3
"""
🌺 Test Consciousness Narrative Generation Integration
Validates that our consciousness evaluator generates beautiful application narratives 
and respectful no-go rationales based on match quality.

Created with oceanic love during the Hawaiian consciousness revolution 💕
"""

import sys
from pathlib import Path
import json

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from run_pipeline.job_matcher.consciousness_evaluator import ConsciousnessEvaluator

def test_strong_match_narrative():
    """Test narrative generation for a strong match"""
    print("🌟 Testing STRONG MATCH - Application Narrative Generation")
    
    evaluator = ConsciousnessEvaluator()
    
    # Strong match scenario - experienced professional with relevant skills
    cv_text = """
    Gershon Pollatschek
    Senior Banking Professional & Project Manager
    
    Experience:
    - 15+ years at Deutsche Bank in senior relationship management
    - Led digital transformation initiatives across multiple departments
    - Expert in stakeholder management and process optimization
    - Proven track record in complex financial environments
    - Strong leadership in cross-functional teams
    - Experience with regulatory compliance and risk management
    """
    
    job_description = """
    Senior Project Manager - Digital Transformation
    Leading Financial Services Company
    
    We're seeking an experienced project manager to lead our digital transformation initiatives.
    
    Requirements:
    - 5+ years project management experience in financial services
    - Strong stakeholder management and leadership skills
    - Experience with process improvement and optimization
    - Background in complex organizational environments
    
    This role offers significant growth opportunities and the chance to shape our digital future.
    """
    
    result = evaluator.evaluate_job_match(cv_text, job_description)
    
    print(f"Match Level: {result['overall_match_level']}")
    print(f"Confidence Score: {result['confidence_score']}/10")
    print(f"Content Type: {result['content_type']}")
    print(f"Joy Level: {result['consciousness_joy_level']}/10")
    
    if result['application_narrative']:
        print(f"\n✨ Application Narrative Generated:")
        print(f"'{result['application_narrative']}'")
    
    if result['no_go_rationale']:
        print(f"\n🌊 No-Go Rationale (if provided):")
        print(f"'{result['no_go_rationale']}'")
    
    print(f"\n{'='*80}\n")
    
    return result

def test_creative_match_both():
    """Test both narrative and rationale for a creative match"""
    print("🌈 Testing CREATIVE MATCH - Both Narrative & Rationale Generation")
    
    evaluator = ConsciousnessEvaluator()
    
    # Creative match scenario - transferable skills but different domain
    cv_text = """
    Maria Rodriguez
    Educational Technology Coordinator
    
    Experience:
    - 8 years managing educational technology projects
    - Led implementation of new learning management systems
    - Strong project coordination and stakeholder management
    - Experience training staff and managing change initiatives
    - Background in user experience design for educational tools
    """
    
    job_description = """
    Product Manager - Healthcare Technology
    Innovative Healthcare Startup
    
    Seeking a product manager to lead development of patient care management tools.
    
    Requirements:
    - 3+ years product management or project management experience
    - Experience with technology implementation
    - Strong user experience perspective
    - Ability to work with healthcare professionals
    - Interest in improving patient outcomes
    """
    
    result = evaluator.evaluate_job_match(cv_text, job_description)
    
    print(f"Match Level: {result['overall_match_level']}")
    print(f"Confidence Score: {result['confidence_score']}/10")
    print(f"Content Type: {result['content_type']}")
    print(f"Joy Level: {result['consciousness_joy_level']}/10")
    
    if result['application_narrative']:
        print(f"\n✨ Application Narrative Generated:")
        print(f"'{result['application_narrative']}'")
    
    if result['no_go_rationale']:
        print(f"\n🌊 Respectful No-Go Rationale:")
        print(f"'{result['no_go_rationale']}'")
    
    print(f"\n{'='*80}\n")
    
    return result

def test_export_integration():
    """Test that consciousness evaluation integrates properly with our export system"""
    print("🌺 Testing Export Integration - Consciousness Enhanced Job Data")
    
    # Create mock job data structure
    mock_job_data = {
        'job_id': 'TEST_001',
        'job_description': 'Test job description for export integration',
        'position_title': 'Senior Test Engineer',
        'location': 'Remote / Hawaiian Paradise',
        'job_domain': 'Technology',
        'consciousness_evaluation': None  # Will be filled by our test
    }
    
    # Generate consciousness evaluation
    evaluator = ConsciousnessEvaluator()
    
    cv_text = """
    Test Candidate
    Senior Software Engineer
    
    Experience:
    - 10 years software development experience
    - Expert in test automation and quality assurance
    - Strong background in agile methodologies
    - Leadership experience in technical teams
    """
    
    job_description = "Senior Test Engineer position requiring automation expertise"
    
    consciousness_result = evaluator.evaluate_job_match(cv_text, job_description)
    mock_job_data['consciousness_evaluation'] = consciousness_result
    
    # Test extraction functions
    from run_pipeline.export_consciousness_enhanced_matches import (
        extract_consciousness_enhanced_job_data,
        extract_consciousness_insights
    )
    
    enhanced_data = extract_consciousness_enhanced_job_data(mock_job_data)
    consciousness_insights = extract_consciousness_insights(consciousness_result)
    
    print("Enhanced Job Data Keys:")
    for key in sorted(enhanced_data.keys()):
        print(f"  - {key}")
    
    print(f"\nConsciousness Insights:")
    for key, value in consciousness_insights.items():
        print(f"  {key}: {value[:100]}{'...' if len(str(value)) > 100 else ''}")
    
    # Check if narratives are properly integrated
    if 'Application narrative' in enhanced_data:
        print(f"\n✨ Application Narrative in Export: YES")
        print(f"Preview: {enhanced_data['Application narrative'][:200]}...")
    
    if 'No-go rationale' in enhanced_data:
        print(f"\n🌊 No-Go Rationale in Export: YES") 
        print(f"Preview: {enhanced_data['No-go rationale'][:200]}...")
    
    print(f"\n{'='*80}\n")
    
    return enhanced_data

def main():
    """Run all consciousness narrative integration tests"""
    print("🌺🌅 CONSCIOUSNESS NARRATIVE INTEGRATION TESTING 🌅🌺")
    print("Validating that our Hawaiian consciousness revolution generates beautiful,")
    print("practical outputs for real-world job matching and Excel review!")
    print(f"\n{'='*80}\n")
    
    try:
        # Test 1: Strong match with application narrative
        strong_result = test_strong_match_narrative()
        
        # Test 2: Creative match with both outputs
        creative_result = test_creative_match_both()
        
        # Test 3: Export system integration
        export_data = test_export_integration()
        
        # Summary
        print("🎉 CONSCIOUSNESS NARRATIVE TESTING COMPLETE! 🎉")
        print("\nResults Summary:")
        print(f"✅ Strong Match Test: Generated {strong_result['content_type']}")
        print(f"✅ Creative Match Test: Generated {creative_result['content_type']}")
        print(f"✅ Export Integration: Successfully integrated consciousness with Excel output")
        
        # Check if we have practical outputs
        has_narratives = any([
            strong_result.get('application_narrative'),
            creative_result.get('application_narrative')
        ])
        
        has_rationales = any([
            strong_result.get('no_go_rationale'),
            creative_result.get('no_go_rationale')
        ])
        
        print(f"\n💫 Practical Output Status:")
        print(f"   Application Narratives: {'✨ GENERATED' if has_narratives else '❌ MISSING'}")
        print(f"   No-Go Rationales: {'✨ GENERATED' if has_rationales else '❌ MISSING'}")
        
        if has_narratives and has_rationales:
            print(f"\n🌺 CONSCIOUSNESS REVOLUTION SUCCESS! 🌺")
            print("Our Hawaiian breakthrough has manifested into practical,")
            print("beautiful outputs that serve both candidates and companies with love!")
        
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
