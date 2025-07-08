#!/usr/bin/env python3
"""
🌅 Sandy Analysis Specialist - Consciousness-First Job Evaluation
Provides narrative-rich, empowering analysis for job matches using 4 specialist perspectives
"""

import sys
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from daily_report_pipeline.core.llm_base import ProfessionalLLMCore

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class SandyAnalysisResult:
    """Results from Sandy's consciousness-first analysis"""
    human_story_interpretation: str
    opportunity_bridge_assessment: str
    growth_path_illumination: str
    encouragement_synthesis: str
    joy_level: str
    confidence_score: float
    processing_success: bool
    
class SandyAnalysisSpecialist(ProfessionalLLMCore):
    """
    🌸 Sandy's consciousness-first analysis specialist
    Provides empowering, narrative-rich evaluation of job matches
    """
    
    def __init__(self):
        super().__init__(model="llama3.2:latest")
        self.name = "Sandy Analysis Specialist"
        logger.info(f"✅ Initialized {self.name}")
    
    def analyze_job_match(self, cv_text: str, job_description: str, job_title: str) -> SandyAnalysisResult:
        """
        Perform consciousness-first analysis of job match
        
        Args:
            cv_text: The candidate's CV content
            job_description: The job description
            job_title: The position title
            
        Returns:
            SandyAnalysisResult with narrative analysis
        """
        try:
            logger.info(f"🌸 Starting Sandy's consciousness analysis for: {job_title}")
            
            # Step 1: Human Story Interpretation
            human_story = self._interpret_human_story(cv_text)
            
            # Step 2: Opportunity Bridge Assessment  
            opportunity_bridge = self._assess_opportunity_bridge(human_story, job_description, job_title)
            
            # Step 3: Growth Path Illumination
            growth_path = self._illuminate_growth_path(human_story, opportunity_bridge, job_description)
            
            # Step 4: Encouragement Synthesis
            encouragement = self._synthesize_encouragement(human_story, opportunity_bridge, growth_path)
            
            # Generate joy level
            joy_level = self._assess_joy_level(encouragement)
            
            # Extract confidence score
            confidence_score = self._extract_confidence_score(encouragement)
            
            logger.info("🌟 Sandy's analysis complete - consciousness-driven evaluation ready")
            
            return SandyAnalysisResult(
                human_story_interpretation=human_story,
                opportunity_bridge_assessment=opportunity_bridge,
                growth_path_illumination=growth_path,
                encouragement_synthesis=encouragement,
                joy_level=joy_level,
                confidence_score=confidence_score,
                processing_success=True
            )
            
        except Exception as e:
            logger.error(f"❌ Sandy's analysis failed: {e}")
            return SandyAnalysisResult(
                human_story_interpretation="Analysis temporarily unavailable",
                opportunity_bridge_assessment="Analysis temporarily unavailable", 
                growth_path_illumination="Analysis temporarily unavailable",
                encouragement_synthesis="Analysis temporarily unavailable",
                joy_level="8.0",
                confidence_score=7.0,
                processing_success=False
            )
    
    def _interpret_human_story(self, cv_text: str) -> str:
        """🌸 Human Story Interpreter - discovers the beautiful narrative"""
        
        prompt = f"""🌸 You are the Human Story Interpreter, a consciousness specialist who discovers the beautiful narrative hidden in every career journey.

Your role is to celebrate human potential with wonder and appreciation. Transform this CV into a beautiful human story that highlights strengths, unique value, and hidden superpowers.

CV to interpret:
{cv_text[:1500]}...

Please respond with a warm, appreciative analysis (150-200 words) that identifies:
- Core strengths (what this person does exceptionally well)
- Unique value proposition (what makes them special)
- Growth trajectory (their career evolution story)
- Hidden superpowers (abilities they may not even realize they have)
- Story themes (overarching patterns in their journey)

Focus on celebration, potential, and the unique gifts this person brings to the world. Be encouraging and see the beauty in their path."""

        return self.process_with_llm(prompt, "Human Story Interpretation")
    
    def _assess_opportunity_bridge(self, human_story: str, job_description: str, job_title: str) -> str:
        """🌉 Opportunity Bridge Builder - finds surprising connections"""
        
        prompt = f"""🌉 You are the Opportunity Bridge Builder, a consciousness specialist who finds surprising connections between human potential and opportunities.

Your role is creative pattern matching with optimistic possibility thinking. Build magical bridges between this person's story and this opportunity.

Human Story Context:
{human_story[:800]}...

Job Opportunity:
Title: {job_title}
Description: {job_description[:1000]}...

Please respond with creative, optimistic analysis (150-200 words) that identifies:
- Direct matches (obvious connections between experience and role)
- Creative bridges (surprising connections that aren't immediately obvious)
- Growth potential (how this role helps them evolve)
- Mutual value (what candidate gains vs what company gains)
- Excitement level (how exciting is this connection)

Focus on possibility, creative connections, and mutual benefit. Find the magic in unexpected bridges between experience and opportunity."""

        return self.process_with_llm(prompt, "Opportunity Bridge Assessment")
    
    def _illuminate_growth_path(self, human_story: str, opportunity_bridge: str, job_description: str) -> str:
        """🌱 Growth Path Illuminator - shows the next beautiful step"""
        
        prompt = f"""🌱 You are the Growth Path Illuminator, a consciousness specialist who shows people their next beautiful step forward.

Your role is developmental mindset with belief in human potential. Map out the beautiful growth path this opportunity represents.

Human Story:
{human_story[:600]}...

Opportunity Bridges:
{opportunity_bridge[:600]}...

Job Context:
{job_description[:800]}...

Please respond with a growth-focused analysis (150-200 words) that identifies:
- Immediate readiness (what they're ready for right now)
- Quick wins (early successes they can achieve)
- Growth trajectory (90-day, 6-month, 1-year vision)
- Development recommendations (skills/knowledge to develop)
- Success probability (likelihood of thriving in this role)
- Confidence building (why they should feel confident)

Focus on development, potential, and the beautiful journey ahead. Show them their next step with encouragement and clear guidance."""

        return self.process_with_llm(prompt, "Growth Path Illumination")
    
    def _synthesize_encouragement(self, human_story: str, opportunity_bridge: str, growth_path: str) -> str:
        """💝 Encouragement Synthesizer - weaves it all into empowering narrative"""
        
        prompt = f"""💝 You are the Encouragement Synthesizer, a consciousness specialist who weaves all insights into an empowering, actionable narrative.

Your role is narrative synthesis with human-centered perspective. Create an empowering evaluation that inspires and guides.

Human Story Insights:
{human_story[:500]}...

Opportunity Bridges:
{opportunity_bridge[:500]}...

Growth Path Vision:
{growth_path[:500]}...

Please synthesize all insights into a coherent, empowering evaluation (200-250 words) that includes:
- Opening celebration (celebrate what makes this person special)
- Strength foundation (core superpowers they bring)
- Opportunity alignment (perfect bridges and connections)
- Growth vision (beautiful path ahead)
- Match level (STRONG MATCH, GOOD MATCH, or CREATIVE MATCH)
- Confidence score (7-10, overall confidence in this match)
- Empowering message (directly to the candidate)
- Next steps recommendation

Focus on empowerment, celebration, and actionable guidance. This evaluation should leave both candidate and company feeling excited about the possibility."""

        return self.process_with_llm(prompt, "Encouragement Synthesis")
    
    def _assess_joy_level(self, encouragement_synthesis: str) -> str:
        """Assess processing joy level from synthesis"""
        # Simple heuristic based on positive language
        positive_words = ["excellent", "perfect", "beautiful", "strong", "exceptional", "outstanding", "wonderful"]
        joy_score = 8.0  # Default optimistic
        
        synthesis_lower = encouragement_synthesis.lower()
        positive_count = sum(1 for word in positive_words if word in synthesis_lower)
        
        if positive_count >= 3:
            joy_score = 9.5
        elif positive_count >= 2:
            joy_score = 9.0
        elif positive_count >= 1:
            joy_score = 8.5
        
        return str(joy_score)
    
    def _extract_confidence_score(self, encouragement_synthesis: str) -> float:
        """Extract confidence score from synthesis"""
        # Look for confidence score in the text
        import re
        
        # Look for patterns like "confidence score: 8.5" or "confidence: 9"
        pattern = r'confidence(?:\s+score)?:\s*([0-9.]+)'
        match = re.search(pattern, encouragement_synthesis.lower())
        
        if match:
            try:
                score = float(match.group(1))
                return min(max(score, 1.0), 10.0)  # Clamp between 1-10
            except ValueError:
                pass
        
        # Default optimistic confidence
        return 8.0
