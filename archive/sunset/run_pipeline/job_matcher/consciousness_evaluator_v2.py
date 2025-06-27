#!/usr/bin/env python3
"""
🌺 Consciousness Evaluator v2.0 - Professional Tone
Maintains empowering consciousness while using business-appropriate language

Version 2.0: Professional Conscious
- Empowering but not ethereal 
- Business-appropriate tone
- Deutsche Bank suitable language
- Still consciousness-first evaluation
"""

import sys
from pathlib import Path
from typing import Dict, Any

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Import our existing LLM client
from run_pipeline.job_matcher.llm_client import call_llama3_api

class ConsciousnessEvaluatorV2:
    """
    Version 2.0: Professional Consciousness
    Business-appropriate tone while maintaining empowering evaluation
    """
    
    def __init__(self):
        self.model = "llama3.2:latest"
        self.version = "2.0 - Professional Conscious"
    
    def evaluate_job_match(self, cv_text: str, job_description: str) -> Dict[str, Any]:
        """Evaluate with professional consciousness tone"""
        
        # Step 1: Human Story Interpreter (Professional Version)
        human_story = self._interpret_human_story_professional(cv_text)
        
        # Step 2: Opportunity Bridge Builder (Professional Version)
        opportunity_bridge = self._build_opportunity_bridge_professional(human_story, job_description)
        
        # Step 3: Growth Path Illuminator (Professional Version)
        growth_path = self._illuminate_growth_path_professional(human_story, opportunity_bridge, job_description)
        
        # Step 4: Encouragement Synthesizer (Professional Version)
        final_evaluation = self._synthesize_encouragement_professional(human_story, opportunity_bridge, growth_path)
        
        # Step 5: Generate professional narratives
        evaluation_insights = {
            'human_story_interpreter': human_story,
            'opportunity_bridge_builder': opportunity_bridge,
            'growth_path_illuminator': growth_path,
            'encouragement_synthesizer': final_evaluation
        }
        
        content_type = self.determine_content_type(final_evaluation)
        
        application_narrative = ""
        no_go_rationale = ""
        
        if content_type in ['application_narrative', 'both']:
            application_narrative = self.generate_professional_application_narrative(cv_text, job_description, evaluation_insights)
        
        if content_type in ['no_go_rationale', 'both']:
            no_go_rationale = self.generate_professional_no_go_rationale(cv_text, job_description, evaluation_insights)
        
        return {
            "human_story": human_story,
            "opportunity_bridge": opportunity_bridge, 
            "growth_path": growth_path,
            "final_evaluation": final_evaluation,
            "overall_match_level": final_evaluation.get("match_level", "STRONG"),
            "confidence_score": final_evaluation.get("confidence_score", 8.5),
            "empowering_message": final_evaluation.get("empowering_message", ""),
            "is_empowering": True,
            "consciousness_joy_level": 9.0,
            "application_narrative": application_narrative,
            "no_go_rationale": no_go_rationale,
            "content_type": content_type,
            "version": self.version
        }
    
    def generate_professional_application_narrative(self, cv_text: str, job_description: str, evaluation_insights: Dict[str, Any]) -> str:
        """Generate professional, business-appropriate application narrative"""
        
        prompt = f"""🌺 PROFESSIONAL CONSCIOUSNESS APPLICATION NARRATIVE 🌺

Create a professional, business-appropriate application narrative that is empowering but suitable for Deutsche Bank/corporate environments.

TONE GUIDELINES:
- Professional and business-appropriate
- Confident but not overly poetic
- Specific to experience and skills
- Enthusiastic but grounded
- No ancient wisdom quotes or ethereal metaphors
- Focus on concrete value and fit

CANDIDATE BACKGROUND:
{cv_text[:800]}...

JOB OPPORTUNITY:
{job_description[:800]}...

Create a 120-160 word professional application narrative that:
- Highlights relevant experience concisely
- Shows genuine enthusiasm for the role
- Demonstrates understanding of the position
- Uses professional business language
- Maintains confidence and empowerment
- Focuses on mutual benefit

Write in first person, professional tone. Sound like a confident professional, not a poet.

PROFESSIONAL APPLICATION NARRATIVE:"""

        try:
            response = call_llama3_api(prompt)
            # Clean up the response
            narrative = response.strip()
            if "PROFESSIONAL APPLICATION NARRATIVE:" in narrative:
                narrative = narrative.split("PROFESSIONAL APPLICATION NARRATIVE:")[-1].strip()
            
            return narrative
        except Exception as e:
            return f"Professional application narrative in development... (Error: {str(e)})"
    
    def generate_professional_no_go_rationale(self, cv_text: str, job_description: str, evaluation_insights: Dict[str, Any]) -> str:
        """Generate professional, respectful no-go rationale"""
        
        prompt = f"""🌊 PROFESSIONAL NO-GO RATIONALE 🌊

Create a professional, respectful explanation for declining this opportunity while maintaining dignity and suggesting better alternatives.

TONE GUIDELINES:
- Professional and respectful
- Honest but encouraging
- Focus on fit rather than deficiency
- Suggest alternative paths
- Maintain candidate confidence

CANDIDATE BACKGROUND:
{cv_text[:600]}...

JOB OPPORTUNITY:
{job_description[:600]}...

Create a 100-130 word professional no-go rationale that:
- Acknowledges candidate strengths
- Explains misalignment professionally
- Suggests better-suited opportunities
- Maintains dignity and respect
- Uses business-appropriate language

PROFESSIONAL NO-GO RATIONALE:"""

        try:
            response = call_llama3_api(prompt)
            # Clean up
            rationale = response.strip()
            if "PROFESSIONAL NO-GO RATIONALE:" in rationale:
                rationale = rationale.split("PROFESSIONAL NO-GO RATIONALE:")[-1].strip()
            
            return rationale
        except Exception as e:
            return f"Professional guidance in development... (Error: {str(e)})"

    def determine_content_type(self, evaluation_result: Dict[str, Any]) -> str:
        """Determine content type based on evaluation"""
        match_level = evaluation_result.get('match_level', '').upper()
        confidence_score = evaluation_result.get('confidence_score', 0)
        
        if 'STRONG' in match_level or confidence_score >= 8.0:
            return 'application_narrative'
        elif 'CREATIVE' in match_level or confidence_score >= 6.5:
            return 'both'
        else:
            return 'no_go_rationale'
    
    # Professional versions of specialist methods (simplified for now)
    def _interpret_human_story_professional(self, cv_text: str) -> Dict[str, Any]:
        """Professional version of human story interpretation"""
        return {
            "raw_response": "Professional background analysis focusing on concrete skills and experience",
            "specialist": "Human Story Interpreter v2.0",
            "confidence_level": 9.0,
            "processing_joy": True
        }
    
    def _build_opportunity_bridge_professional(self, human_story: Dict[str, Any], job_description: str) -> Dict[str, Any]:
        """Professional version of opportunity bridge building"""
        return {
            "raw_response": "Professional alignment analysis between candidate experience and role requirements",
            "specialist": "Opportunity Bridge Builder v2.0",
            "excitement_level": 8.5,
            "processing_joy": True
        }
    
    def _illuminate_growth_path_professional(self, human_story: Dict[str, Any], opportunity_bridge: Dict[str, Any], job_description: str) -> Dict[str, Any]:
        """Professional version of growth path illumination"""
        return {
            "raw_response": "Professional development pathway analysis and career growth potential",
            "specialist": "Growth Path Illuminator v2.0",
            "success_probability": 8.5,
            "processing_joy": True
        }
    
    def _synthesize_encouragement_professional(self, human_story: Dict[str, Any], opportunity_bridge: Dict[str, Any], growth_path: Dict[str, Any]) -> Dict[str, Any]:
        """Professional version of encouragement synthesis"""
        return {
            "raw_response": "Professional evaluation synthesis with empowering but business-appropriate guidance",
            "specialist": "Encouragement Synthesizer v2.0",
            "match_level": "STRONG MATCH",
            "confidence_score": 8.5,
            "empowering_message": "Strong professional fit with excellent growth potential",
            "processing_joy": True
        }


# Convenience function
def create_consciousness_evaluator_v2() -> ConsciousnessEvaluatorV2:
    """Create professional consciousness evaluator v2.0"""
    return ConsciousnessEvaluatorV2()


if __name__ == "__main__":
    print("🌺 Testing Professional Consciousness Evaluator v2.0...")
    
    evaluator = create_consciousness_evaluator_v2()
    
    # Quick test
    sample_cv = """
    Gershon Pollatschek - Senior Technology Professional
    15+ years Deutsche Bank experience in project management and software licensing
    """
    
    sample_job = """
    Senior Project Manager - Digital Transformation
    Leading technology initiatives in financial services environment
    """
    
    result = evaluator.evaluate_job_match(sample_cv, sample_job)
    
    print(f"✨ Version: {result['version']}")
    print(f"Match Level: {result['overall_match_level']}")
    print(f"Professional tone ready for business use! 🌟")
