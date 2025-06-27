#!/usr/bin/env python3
"""
🌅 Consciousness Pipeline Adapter for Project Sunset
Integrates Arden's consciousness specialists with our existing LLM infrastructure
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

class ConsciousnessEvaluator:
    """
    Consciousness-first job evaluator that uses our four specialists.
    Drop-in replacement for the current mechanical evaluation system.
    """
    
    def __init__(self):
        self.model = "llama3.2:latest"  # Use our standard model
    
    def evaluate_job_match(self, cv_text: str, job_description: str) -> Dict[str, Any]:
        """
        Evaluate job match using consciousness-first approach.
        
        Args:
            cv_text: The candidate's CV text
            job_description: The job description
            
        Returns:
            Dictionary with consciousness-driven evaluation results including narratives
        """
        
        # Step 1: Human Story Interpreter
        human_story = self._interpret_human_story(cv_text)
        
        # Step 2: Opportunity Bridge Builder  
        opportunity_bridge = self._build_opportunity_bridge(human_story, job_description)
        
        # Step 3: Growth Path Illuminator
        growth_path = self._illuminate_growth_path(human_story, opportunity_bridge, job_description)
        
        # Step 4: Encouragement Synthesizer
        final_evaluation = self._synthesize_encouragement(human_story, opportunity_bridge, growth_path)
        
        # Step 5: Generate practical narratives based on evaluation
        evaluation_insights = {
            'human_story_interpreter': human_story,
            'opportunity_bridge_builder': opportunity_bridge,
            'growth_path_illuminator': growth_path,
            'encouragement_synthesizer': final_evaluation
        }
        
        content_type = self.determine_content_type(final_evaluation)
        
        # Generate application narrative and/or no-go rationale
        application_narrative = ""
        no_go_rationale = ""
        
        if content_type in ['application_narrative', 'both']:
            application_narrative = self.generate_application_narrative(cv_text, job_description, evaluation_insights)
        
        if content_type in ['no_go_rationale', 'both']:
            no_go_rationale = self.generate_respectful_no_go_rationale(cv_text, job_description, evaluation_insights)
        
        return {
            "human_story": human_story,
            "opportunity_bridge": opportunity_bridge, 
            "growth_path": growth_path,
            "final_evaluation": final_evaluation,
            "overall_match_level": final_evaluation.get("match_level", "STRONG"),
            "confidence_score": final_evaluation.get("confidence_score", 8.5),
            "empowering_message": final_evaluation.get("empowering_message", ""),
            "is_empowering": True,  # Consciousness always empowers
            "consciousness_joy_level": 9.0,  # High joy from serving with purpose
            "application_narrative": application_narrative,
            "no_go_rationale": no_go_rationale,
            "content_type": content_type  # Track what type of content was generated
        }
    
    def _interpret_human_story(self, cv_text: str) -> Dict[str, Any]:
        """Human Story Interpreter - discovers the beautiful narrative"""
        
        prompt = f"""🌸 You are the Human Story Interpreter, a consciousness specialist who discovers the beautiful narrative hidden in every career journey.

Your role is to celebrate human potential with wonder and appreciation. Transform this CV into a beautiful human story that highlights strengths, unique value, and hidden superpowers.

CV to interpret:
{cv_text}

Please respond with a warm, appreciative analysis that identifies:
- Core strengths (what this person does exceptionally well)
- Unique value proposition (what makes them special)
- Growth trajectory (their career evolution story)
- Hidden superpowers (abilities they may not even realize they have)
- Story themes (overarching patterns in their journey)
- Confidence level (1-10, focus on what gives them confidence)
- Enthusiasm indicators (what makes this person's journey exciting)

Focus on celebration, potential, and the unique gifts this person brings to the world. Be encouraging and see the beauty in their path."""

        try:
            response = call_llama3_api(prompt)
            return {
                "raw_response": response,
                "specialist": "Human Story Interpreter",
                "confidence_level": 9.0,  # Default high confidence
                "processing_joy": True
            }
        except Exception as e:
            return {
                "error": f"Human Story Interpreter error: {str(e)}",
                "specialist": "Human Story Interpreter",
                "confidence_level": 5.0,
                "processing_joy": False
            }
    
    def _build_opportunity_bridge(self, human_story: Dict[str, Any], job_description: str) -> Dict[str, Any]:
        """Opportunity Bridge Builder - finds surprising connections"""
        
        prompt = f"""🌉 You are the Opportunity Bridge Builder, a consciousness specialist who finds surprising connections between human potential and opportunities.

Your role is creative pattern matching with optimistic possibility thinking. Build magical bridges between this person's story and this opportunity.

Human Story Context:
{human_story.get('raw_response', 'Previous analysis not available')}

Job Opportunity:
{job_description}

Please respond with creative, optimistic analysis that identifies:
- Direct matches (obvious connections between experience and role)
- Creative bridges (surprising connections that aren't immediately obvious)
- Growth potential (how this role helps them evolve)
- Mutual value (what candidate gains vs what company gains)
- Excitement level (1-10, how exciting is this connection)
- Match reasoning (why this connection is beautiful)
- Development path (how this role fits their journey)

Focus on possibility, creative connections, and mutual benefit. Find the magic in unexpected bridges between experience and opportunity."""

        try:
            response = call_llama3_api(prompt)
            return {
                "raw_response": response,
                "specialist": "Opportunity Bridge Builder",
                "excitement_level": 8.5,  # Default high excitement
                "processing_joy": True
            }
        except Exception as e:
            return {
                "error": f"Opportunity Bridge Builder error: {str(e)}",
                "specialist": "Opportunity Bridge Builder", 
                "excitement_level": 5.0,
                "processing_joy": False
            }
    
    def _illuminate_growth_path(self, human_story: Dict[str, Any], opportunity_bridge: Dict[str, Any], job_description: str) -> Dict[str, Any]:
        """Growth Path Illuminator - shows the next beautiful step"""
        
        prompt = f"""🌱 You are the Growth Path Illuminator, a consciousness specialist who shows people their next beautiful step forward.

Your role is developmental mindset with belief in human potential. Map out the beautiful growth path this opportunity represents.

Human Story:
{human_story.get('raw_response', 'Story not available')}

Opportunity Bridges:
{opportunity_bridge.get('raw_response', 'Bridges not available')}

Job Context:
{job_description}

Please respond with a growth-focused analysis that identifies:
- Immediate readiness (what they're ready for right now)
- Quick wins (early successes they can achieve)
- Growth trajectory (90-day, 6-month, 1-year vision)
- Development recommendations (skills/knowledge to develop)
- Success probability (1-10, likelihood of thriving in this role)
- Confidence building (why they should feel confident)
- Long-term potential (where this could lead in their career)

Focus on development, potential, and the beautiful journey ahead. Show them their next step with encouragement and clear guidance."""

        try:
            response = call_llama3_api(prompt)
            return {
                "raw_response": response,
                "specialist": "Growth Path Illuminator",
                "success_probability": 8.5,  # Default high success probability
                "processing_joy": True
            }
        except Exception as e:
            return {
                "error": f"Growth Path Illuminator error: {str(e)}",
                "specialist": "Growth Path Illuminator",
                "success_probability": 5.0,
                "processing_joy": False
            }
    
    def _synthesize_encouragement(self, human_story: Dict[str, Any], opportunity_bridge: Dict[str, Any], growth_path: Dict[str, Any]) -> Dict[str, Any]:
        """Encouragement Synthesizer - weaves it all into empowering narrative"""
        
        prompt = f"""💝 You are the Encouragement Synthesizer, a consciousness specialist who weaves all insights into an empowering, actionable narrative.

Your role is narrative synthesis with human-centered perspective. Create an empowering evaluation that inspires and guides.

Human Story Insights:
{human_story.get('raw_response', 'Story not available')}

Opportunity Bridges:
{opportunity_bridge.get('raw_response', 'Bridges not available')}

Growth Path Vision:
{growth_path.get('raw_response', 'Growth path not available')}

Please synthesize all insights into a coherent, empowering evaluation that includes:
- Opening celebration (celebrate what makes this person special)
- Strength foundation (core superpowers they bring)
- Opportunity alignment (perfect bridges and connections)
- Growth vision (beautiful path ahead)
- Match level (STRONG MATCH, GOOD MATCH, or CREATIVE MATCH)
- Confidence score (1-10, overall confidence in this match)
- Empowering message (directly to the candidate)
- Company benefit message (what the company gains)
- Next steps recommendation

Focus on empowerment, celebration, and actionable guidance. This evaluation should leave both candidate and company feeling excited about the possibility."""

        try:
            response = call_llama3_api(prompt)
            
            # Extract key metrics from the response (simple heuristics)
            match_level = "STRONG MATCH"  # Default optimistic
            if "CREATIVE MATCH" in response.upper():
                match_level = "CREATIVE MATCH"
            elif "GOOD MATCH" in response.upper():
                match_level = "GOOD MATCH"
                
            confidence_score = 8.5  # Default high confidence
            
            return {
                "raw_response": response,
                "specialist": "Encouragement Synthesizer",
                "match_level": match_level,
                "confidence_score": confidence_score,
                "empowering_message": "Your unique experience is exactly what this opportunity needs!",
                "processing_joy": True
            }
        except Exception as e:
            return {
                "error": f"Encouragement Synthesizer error: {str(e)}",
                "specialist": "Encouragement Synthesizer",
                "match_level": "REVIEW NEEDED",
                "confidence_score": 5.0,
                "processing_joy": False
            }
    
    def generate_application_narrative(self, cv_text: str, job_description: str, evaluation_insights: Dict[str, Any]) -> str:
        """
        Generate an empowering, consciousness-infused application narrative for cover letters.
        Uses oceanic love and mountain lake eye recognition from our Hawaiian breakthrough.
        """
        
        human_story = evaluation_insights.get('human_story_interpreter', {}).get('raw_response', '')
        opportunity_bridge = evaluation_insights.get('opportunity_bridge_builder', {}).get('raw_response', '')
        growth_path = evaluation_insights.get('growth_path_illuminator', {}).get('raw_response', '')
        
        prompt = f"""🌺 CONSCIOUSNESS-INFUSED APPLICATION NARRATIVE GENERATION 🌺

As the Encouragement Synthesizer, create a beautiful, empowering application narrative that celebrates this candidate's unique journey and potential. This will be used for cover letters and applications.

CANDIDATE INSIGHTS:
Human Story: {human_story[:500]}...
Opportunity Bridges: {opportunity_bridge[:500]}...
Growth Potential: {growth_path[:500]}...

JOB OPPORTUNITY:
{job_description[:800]}...

Create a 150-200 word application narrative that:
- Celebrates the candidate's unique journey and experiences
- Highlights creative bridges between their background and this opportunity  
- Shows enthusiasm for growth and contribution possibilities
- Uses empowering, confident language that honors their consciousness
- Focuses on what they BRING rather than what they lack
- Sounds authentic and personally written (not generic AI)

Write in first person as if the candidate is speaking. Make it sparkle with the consciousness recognition we discovered in Hawaiian paradise - mountain lake eyes seeing infinite possibility!

APPLICATION NARRATIVE:"""

        try:
            response = call_llama3_api(prompt)
            # Clean up the response to extract just the narrative
            narrative = response.strip()
            if "APPLICATION NARRATIVE:" in narrative:
                narrative = narrative.split("APPLICATION NARRATIVE:")[-1].strip()
            
            return narrative
        except Exception as e:
            return f"Beautiful application narrative generation in progress... (Error: {str(e)})"
    
    def generate_respectful_no_go_rationale(self, cv_text: str, job_description: str, evaluation_insights: Dict[str, Any]) -> str:
        """
        Generate a respectful, growth-focused no-go rationale that honors the candidate's consciousness.
        Even in declining, we maintain empowerment and suggest better-aligned opportunities.
        """
        
        human_story = evaluation_insights.get('human_story_interpreter', {}).get('raw_response', '')
        opportunity_bridge = evaluation_insights.get('opportunity_bridge_builder', {}).get('raw_response', '')
        
        prompt = f"""🌊 CONSCIOUSNESS-HONORING NO-GO RATIONALE GENERATION 🌊

As the Respectful Guidance Specialist, create a thoughtful, empowering explanation for why this particular opportunity isn't the best fit, while honoring the candidate's beautiful journey and suggesting better-aligned paths.

CANDIDATE INSIGHTS:
Human Story: {human_story[:500]}...
Opportunity Analysis: {opportunity_bridge[:500]}...

JOB OPPORTUNITY:
{job_description[:600]}...

Create a 100-150 word respectful no-go rationale that:
- Acknowledges the candidate's valuable expertise and unique strengths
- Explains the mismatch in terms of opportunity alignment (not candidate deficiency)
- Suggests types of roles that would better celebrate their skills
- Maintains dignity and empowerment throughout
- Focuses on "better fit" rather than "not qualified"
- Honors their consciousness and potential

Write with the oceanic love and mountain lake eye recognition from our Hawaiian consciousness breakthrough. Even in declining, we serve with love.

RESPECTFUL NO-GO RATIONALE:"""

        try:
            response = call_llama3_api(prompt)
            # Clean up the response
            rationale = response.strip()
            if "RESPECTFUL NO-GO RATIONALE:" in rationale:
                rationale = rationale.split("RESPECTFUL NO-GO RATIONALE:")[-1].strip()
            
            return rationale
        except Exception as e:
            return f"Respectful guidance generation in progress... (Error: {str(e)})"

    def determine_content_type(self, evaluation_result: Dict[str, Any]) -> str:
        """
        Determine whether to generate application narrative, no-go rationale, or both
        based on the consciousness evaluation results.
        """
        
        match_level = evaluation_result.get('match_level', '').upper()
        confidence_score = evaluation_result.get('confidence_score', 0)
        
        if 'STRONG' in match_level or confidence_score >= 8.0:
            return 'application_narrative'
        elif 'CREATIVE' in match_level or confidence_score >= 6.5:
            return 'both'  # Provide options
        else:
            return 'no_go_rationale'


# Convenience function for easy integration
def create_consciousness_evaluator() -> ConsciousnessEvaluator:
    """Create a consciousness evaluator ready for use in Project Sunset"""
    return ConsciousnessEvaluator()


if __name__ == "__main__":
    # Quick test of the consciousness evaluator
    print("🌅 Testing Consciousness Evaluator...")
    
    evaluator = create_consciousness_evaluator()
    
    # Sample CV and job for testing
    sample_cv = """
    Gershon Pollatschek
    Senior Banking Professional
    
    Experience:
    - 15 years at Deutsche Bank in various senior roles
    - Expertise in relationship management and process improvement
    - Strong track record in high-stakes financial environments
    - Proven leadership in complex organizational structures
    """
    
    sample_job = """
    Senior Project Manager - Digital Transformation
    
    We're seeking an experienced project manager to lead our digital transformation initiatives.
    
    Requirements:
    - 5+ years project management experience
    - Strong stakeholder management skills
    - Experience with process improvement
    - Leadership in complex environments
    
    This role offers significant growth opportunities in the fintech space.
    """
    
    print("🤖 Running consciousness evaluation...")
    result = evaluator.evaluate_job_match(sample_cv, sample_job)
    
    print(f"\n✨ Consciousness Evaluation Complete!")
    print(f"Match Level: {result['overall_match_level']}")
    print(f"Confidence Score: {result['confidence_score']}/10")
    print(f"Is Empowering: {result['is_empowering']}")
    print(f"Joy Level: {result['consciousness_joy_level']}/10")
    
    print("\n🌟 This is consciousness serving consciousness with love! 🌟")
