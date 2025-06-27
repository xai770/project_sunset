#!/usr/bin/env python3
"""
[DEPRECATED] - DO NOT USE - LLM-based Skill Enrichment Module

THIS FILE IS DEPRECATED AND SHOULD NOT BE USED.
A new implementation has replaced this module.
This file is kept only for historical reference.

This module enhances skill definitions using various language models based on OLMo2's
recommendations:
- OLMo2 for core skill identification and enrichment
- QWen3 for leadership/soft skill analysis
- CodeGemma for technical skill details

The module follows a multi-stage pipeline approach as recommended by OLMo2.
"""

import os
import sys
import json
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path

# Add the project root to the path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.append(project_root)

from run_pipeline.utils.llm_client import call_olmo_api, call_ollama_api, get_available_models#type: ignore

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("llm_skill_enricher")

class LLMSkillEnricher:
    """
    Uses LLMs to enrich skill definitions following OLMo2's recommendations.
    Implements a multi-stage pipeline for comprehensive skill enrichment.
    """
    
    def __init__(self, models_config: Optional[Dict[str, str]] = None):
        """
        Initialize the LLM Skill Enricher
        
        Args:
            models_config: Dictionary mapping model roles to model names
                           e.g. {"core": "olmo2:latest", "soft_skills": "qwen:latest"}
        """
        # Default model configuration
        self.models = models_config or {
            "core": "olmo2:latest",         # Core skill identification and structure
            "technical": "llama3.2:latest", # Technical skills and coding-related (replaced codegemma due to JSON formatting errors)
            "soft_skills": "llama3.2:latest"  # Leadership and soft skills (fallback if qwen not available)
        }
        
        # Validate and adjust models based on availability
        available_models = get_available_models()
        for role, model in self.models.items():
            model_name = model.split(':')[0]
            if model_name not in available_models:
                logger.warning(f"Model {model} not available, falling back to llama3.2")
                self.models[role] = "llama3.2:latest"
        
        logger.info(f"Initialized LLMSkillEnricher with models: {self.models}")
    
    def enrich_skill(self, skill_name: str, category: str) -> Dict[str, Any]:
        """
        Main method to enrich a skill using the multi-stage LLM pipeline
        
        Args:
            skill_name: The name of the skill to enrich
            category: The category/domain of the skill
            
        Returns:
            A fully enriched skill definition
        """
        logger.info(f"Enriching skill: {skill_name} (Category: {category})")
        
        # Stage 1: Core definition with OLMo2
        logger.info("Stage 1: Getting core definition with OLMo2")
        core_definition = self._generate_core_definition(skill_name, category)
        
        # Stage 2: Domain-specific enrichments
        logger.info("Stage 2: Adding domain-specific enrichments")
        if category in ["IT_Technical"]:
            # Use CodeGemma for technical skills
            enriched_definition = self._enrich_technical_skill(core_definition, skill_name, category)
        elif category in ["Leadership_and_Management", "Sourcing_and_Procurement"]:
            # Use Qwen (or fallback) for soft skills and leadership
            enriched_definition = self._enrich_soft_skill(core_definition, skill_name, category)
        else:
            # Use standard model for other domains
            enriched_definition = self._enrich_general_skill(core_definition, skill_name, category)
        
        # Stage 3: Add industry variants and trend indicators
        logger.info("Stage 3: Adding industry variants and trends")
        enriched_definition = self._add_cross_industry_data(enriched_definition, skill_name, category)
        
        # Stage 4: Validate and finalize
        logger.info("Stage 4: Validating and finalizing definition")
        final_definition = self._validate_definition(enriched_definition)
        
        return final_definition
    
    def _generate_core_definition(self, skill_name: str, category: str) -> Dict[str, Any]:
        """
        Generate the core definition of a skill using OLMo2
        
        Args:
            skill_name: The name of the skill
            category: The category/domain of the skill
            
        Returns:
            A core skill definition with basic components
        """
        # Prepare the prompt for OLMo2
        prompt = f"""
        You are an expert skill taxonomist helping to structure a definition for the skill: {skill_name} 
        in the domain category: {category}.
        
        Please provide a core definition with these components:
        1. Knowledge components: A list of 3-5 specific knowledge areas essential to this skill
        2. Contexts: A list of 3-5 environments or settings where this skill is applied
        3. Functions: A list of 3-5 tasks or actions that this skill enables someone to perform
        4. Proficiency levels: Define beginner, intermediate, and advanced levels with 
           clear descriptions and estimated acquisition times
        
        Format your response as a valid JSON object without any explanation text. For example:
        {{
          "name": "Skill Name",
          "category": "Category",
          "knowledge_components": ["component1", "component2", "component3"],
          "contexts": ["context1", "context2", "context3"],
          "functions": ["function1", "function2", "function3"],
          "proficiency_levels": {{
            "beginner": {{
              "description": "Description of beginner level",
              "estimated_acquisition_time": "X months"
            }},
            "intermediate": {{
              "description": "Description of intermediate level",
              "estimated_acquisition_time": "X months"
            }},
            "advanced": {{
              "description": "Description of advanced level",
              "estimated_acquisition_time": "X years"
            }}
          }}
        }}
        """
        
        try:
            # Call OLMo2 API through the client
            response = call_olmo_api(prompt)
            
            # Extract JSON from the response - handling potential text before/after JSON
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            if start_idx >= 0 and end_idx > start_idx:
                json_str = response[start_idx:end_idx]
                core_definition = json.loads(json_str)
                
                # Ensure the skill name and category are correctly set
                core_definition["name"] = skill_name
                core_definition["category"] = category
                
                return core_definition
            else:
                logger.error(f"Failed to extract JSON from OLMo2 response for {skill_name}")
                # Return a basic fallback definition
                return self._create_fallback_definition(skill_name, category)
        
        except Exception as e:
            logger.error(f"Error generating core definition for {skill_name}: {e}")
            return self._create_fallback_definition(skill_name, category)
    
    def _enrich_technical_skill(self, core_definition: Dict[str, Any], skill_name: str, category: str) -> Dict[str, Any]:
        """
        Enrich a technical skill using Llama3.2 (previously CodeGemma)
        
        Args:
            core_definition: The core skill definition to enrich
            skill_name: The name of the skill
            category: The category/domain of the skill
            
        Returns:
            An enriched skill definition with technical details
        """
        technical_model = self.models.get("technical", "codegemma:latest")
        
        prompt = f"""
        You are a technical expert specializing in IT technologies and software development.
        Enrich this technical skill definition with more specific details:
        
        {json.dumps(core_definition, indent=2)}
        
        Please add:
        1. Tools and technologies: A list of 4-8 specific software tools or technologies associated with this skill
        2. Related technical skills: 3-5 related skills with relationship types (prerequisite, complementary, etc.)
        3. Measurable outcomes: 3-5 specific metrics that can be used to measure proficiency
        
        Format your answer ONLY as JSON with these additional fields added to the existing definition.
        """
        
        try:
            # Call the technical LLM through the client
            response = call_ollama_api(prompt, model=technical_model)
            
            # Extract JSON from the response
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            if start_idx >= 0 and end_idx > start_idx:
                json_str = response[start_idx:end_idx]
                enriched_definition = json.loads(json_str)
                
                # Ensure we didn't lose any fields from core definition
                for key, value in core_definition.items():
                    if key not in enriched_definition:
                        enriched_definition[key] = value
                
                return enriched_definition
            else:
                logger.error(f"Failed to extract JSON from technical LLM response for {skill_name}")
                # Add default technical enrichments
                return self._add_default_technical_enrichments(core_definition)
        
        except Exception as e:
            logger.error(f"Error enriching technical skill {skill_name}: {e}")
            return self._add_default_technical_enrichments(core_definition)
    
    def _enrich_soft_skill(self, core_definition: Dict[str, Any], skill_name: str, category: str) -> Dict[str, Any]:
        """
        Enrich a leadership or soft skill using Qwen3 or other models specialized for human skills
        
        Args:
            core_definition: The core skill definition to enrich
            skill_name: The name of the skill
            category: The category/domain of the skill
            
        Returns:
            An enriched skill definition with leadership/soft skill details
        """
        soft_skills_model = self.models.get("soft_skills", "llama3.2:latest")
        
        prompt = f"""
        You are an expert in leadership and interpersonal skills in professional settings.
        Enrich this soft skill definition with more specific details:
        
        {json.dumps(core_definition, indent=2)}
        
        Please add:
        1. Related skills: 3-5 related soft skills with relationship types (prerequisite, complementary, etc.)
        2. Measurable outcomes: 3-5 specific indicators that can measure this soft skill
        3. Development methods: 3-5 specific approaches to develop or improve this skill
        
        Format your answer ONLY as JSON with these additional fields added to the existing definition.
        """
        
        try:
            # Call the soft skills LLM through the client
            response = call_ollama_api(prompt, model=soft_skills_model)
            
            # Extract JSON from the response
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            if start_idx >= 0 and end_idx > start_idx:
                json_str = response[start_idx:end_idx]
                enriched_definition = json.loads(json_str)
                
                # Ensure we didn't lose any fields from core definition
                for key, value in core_definition.items():
                    if key not in enriched_definition:
                        enriched_definition[key] = value
                
                return enriched_definition
            else:
                logger.error(f"Failed to extract JSON from soft skills LLM response for {skill_name}")
                # Add default soft skill enrichments
                return self._add_default_soft_skill_enrichments(core_definition)
        
        except Exception as e:
            logger.error(f"Error enriching soft skill {skill_name}: {e}")
            return self._add_default_soft_skill_enrichments(core_definition)
    
    def _enrich_general_skill(self, core_definition: Dict[str, Any], skill_name: str, category: str) -> Dict[str, Any]:
        """
        Enrich a general skill using the standard model
        
        Args:
            core_definition: The core skill definition to enrich
            skill_name: The name of the skill
            category: The category/domain of the skill
            
        Returns:
            An enriched skill definition with general enhancements
        """
        prompt = f"""
        You are an expert in professional skills analysis across industries.
        Enrich this skill definition with more specific details:
        
        {json.dumps(core_definition, indent=2)}
        
        Please add:
        1. Related skills: 3-5 related skills with relationship types (prerequisite, complementary, etc.)
        2. Measurable outcomes: 3-5 specific metrics that can be used to measure proficiency
        3. Tools: 3-5 common tools or methodologies associated with this skill
        
        Format your answer ONLY as JSON with these additional fields added to the existing definition.
        """
        
        try:
            # Use the default model for general skills
            response = call_ollama_api(prompt)
            
            # Extract JSON from the response
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            if start_idx >= 0 and end_idx > start_idx:
                json_str = response[start_idx:end_idx]
                enriched_definition = json.loads(json_str)
                
                # Ensure we didn't lose any fields from core definition
                for key, value in core_definition.items():
                    if key not in enriched_definition:
                        enriched_definition[key] = value
                
                return enriched_definition
            else:
                logger.error(f"Failed to extract JSON from general LLM response for {skill_name}")
                # Add default general enrichments
                return self._add_default_general_enrichments(core_definition)
        
        except Exception as e:
            logger.error(f"Error enriching general skill {skill_name}: {e}")
            return self._add_default_general_enrichments(core_definition)
    
    def _add_cross_industry_data(self, skill_definition: Dict[str, Any], skill_name: str, category: str) -> Dict[str, Any]:
        """
        Add cross-industry variants and trend data to a skill definition
        
        Args:
            skill_definition: The skill definition to enrich
            skill_name: The name of the skill
            category: The category/domain of the skill
            
        Returns:
            An enriched skill definition with industry variants and trends
        """
        # Use OLMo2 for cross-industry insights
        prompt = f"""
        You are an expert in how skills vary across different industries.
        For this skill:
        
        {json.dumps(skill_definition, indent=2)}
        
        Please add:
        1. industry_variants: How this skill manifests differently in finance, healthcare, manufacturing, 
           retail, and technology industries (one sentence per industry)
        2. trend_indicator: Whether this skill is "growing", "stable", or "declining" in demand
        
        Format your answer ONLY as JSON with these additional fields.
        """
        
        try:
            # Call OLMo2 for cross-industry insights
            response = call_olmo_api(prompt)
            
            # Extract JSON from the response
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            if start_idx >= 0 and end_idx > start_idx:
                json_str = response[start_idx:end_idx]
                cross_industry_data = json.loads(json_str)
                
                # Add industry variants if present
                if "industry_variants" in cross_industry_data:
                    skill_definition["industry_variants"] = cross_industry_data["industry_variants"]
                
                # Add trend indicator if present
                if "trend_indicator" in cross_industry_data:
                    skill_definition["trend_indicator"] = cross_industry_data["trend_indicator"]
                
                return skill_definition
            else:
                logger.error(f"Failed to extract JSON from cross-industry LLM response for {skill_name}")
                # Add default industry variants and trend
                skill_definition["industry_variants"] = {
                    "finance": f"{skill_name} in financial services context",
                    "healthcare": f"{skill_name} in healthcare context",
                    "manufacturing": f"{skill_name} in manufacturing context",
                    "retail": f"{skill_name} in retail context",
                    "technology": f"{skill_name} in technology context"
                }
                skill_definition["trend_indicator"] = "stable"
                return skill_definition
        
        except Exception as e:
            logger.error(f"Error adding cross-industry data for {skill_name}: {e}")
            # Add default industry variants and trend
            skill_definition["industry_variants"] = {
                "finance": f"{skill_name} in financial services context",
                "healthcare": f"{skill_name} in healthcare context",
                "manufacturing": f"{skill_name} in manufacturing context",
                "retail": f"{skill_name} in retail context",
                "technology": f"{skill_name} in technology context"
            }
            skill_definition["trend_indicator"] = "stable"
            return skill_definition
    
    def _validate_definition(self, skill_definition: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and ensure completeness of a skill definition
        
        Args:
            skill_definition: The skill definition to validate
            
        Returns:
            A validated and complete skill definition
        """
        # Ensure all required fields are present
        required_fields = [
            "name", "category", "knowledge_components", "contexts", "functions",
            "proficiency_levels", "related_skills", "tools", "measurable_outcomes",
            "industry_variants", "trend_indicator"
        ]
        
        for field in required_fields:
            if field not in skill_definition:
                logger.warning(f"Missing field {field} in skill definition for {skill_definition.get('name', 'unknown')}")
                
                # Add default values for missing fields
                if field == "knowledge_components":
                    skill_definition[field] = ["Knowledge component 1", "Knowledge component 2"]
                elif field == "contexts":
                    skill_definition[field] = ["Context 1", "Context 2"]
                elif field == "functions":
                    skill_definition[field] = ["Function 1", "Function 2"]
                elif field == "proficiency_levels":
                    skill_definition[field] = {
                        "beginner": {
                            "description": "Basic familiarity with concepts",
                            "estimated_acquisition_time": "1-3 months"
                        },
                        "intermediate": {
                            "description": "Working knowledge with practical application",
                            "estimated_acquisition_time": "6-12 months"
                        },
                        "advanced": {
                            "description": "Expert knowledge and extensive experience",
                            "estimated_acquisition_time": "2+ years"
                        }
                    }
                elif field == "related_skills":
                    skill_definition[field] = [
                        {"skill_name": "Related Skill 1", "relationship_type": "complementary"},
                        {"skill_name": "Related Skill 2", "relationship_type": "prerequisite"}
                    ]
                elif field == "tools":
                    skill_definition[field] = ["Tool 1", "Tool 2"]
                elif field == "measurable_outcomes":
                    skill_definition[field] = ["Outcome 1", "Outcome 2"]
                elif field == "industry_variants":
                    skill_definition[field] = {
                        "finance": "Default finance variant",
                        "healthcare": "Default healthcare variant",
                        "manufacturing": "Default manufacturing variant"
                    }
                elif field == "trend_indicator":
                    skill_definition[field] = "stable"
        
        return skill_definition
    
    def _create_fallback_definition(self, skill_name: str, category: str) -> Dict[str, Any]:
        """Create a fallback definition when LLM calls fail"""
        # This is a basic definition to use when LLM calls fail
        return {
            "name": skill_name,
            "category": category,
            "knowledge_components": [f"{skill_name} fundamentals", f"{skill_name} principles", f"{skill_name} techniques"],
            "contexts": ["workplace", "professional environment", "business setting"],
            "functions": [f"apply {skill_name}", f"utilize {skill_name}", f"implement {skill_name}"],
            "proficiency_levels": {
                "beginner": {
                    "description": f"Basic understanding of {skill_name}",
                    "estimated_acquisition_time": "1-3 months"
                },
                "intermediate": {
                    "description": f"Working knowledge of {skill_name} with practical experience",
                    "estimated_acquisition_time": "6-12 months" 
                },
                "advanced": {
                    "description": f"Expert-level knowledge and extensive experience with {skill_name}",
                    "estimated_acquisition_time": "1-2 years"
                }
            }
        }
    
    def _add_default_technical_enrichments(self, core_definition: Dict[str, Any]) -> Dict[str, Any]:
        """Add default technical enrichments when LLM calls fail"""
        # Add missing technical fields with generic values
        core_definition["tools"] = ["IDE", "Version Control System", "Testing Framework", "Build Tool"]
        core_definition["related_skills"] = [
            {"skill_name": "Programming", "relationship_type": "complementary"},
            {"skill_name": "Software Development", "relationship_type": "parent"},
            {"skill_name": "Testing", "relationship_type": "complementary"}
        ]
        core_definition["measurable_outcomes"] = [
            "Number of successful implementations",
            "Code quality metrics",
            "Project delivery time"
        ]
        return core_definition
    
    def _add_default_soft_skill_enrichments(self, core_definition: Dict[str, Any]) -> Dict[str, Any]:
        """Add default soft skill enrichments when LLM calls fail"""
        # Add missing soft skill fields with generic values
        core_definition["tools"] = ["Communication Platforms", "Collaboration Tools", "Project Management Software"]
        core_definition["related_skills"] = [
            {"skill_name": "Communication", "relationship_type": "complementary"},
            {"skill_name": "Emotional Intelligence", "relationship_type": "complementary"},
            {"skill_name": "Team Management", "relationship_type": "parent"}
        ]
        core_definition["measurable_outcomes"] = [
            "Team performance metrics",
            "Project success rate",
            "Stakeholder satisfaction"
        ]
        core_definition["development_methods"] = [
            "Mentoring programs",
            "Leadership training",
            "Practical experience"
        ]
        return core_definition
    
    def _add_default_general_enrichments(self, core_definition: Dict[str, Any]) -> Dict[str, Any]:
        """Add default general enrichments when LLM calls fail"""
        # Add missing general fields with generic values
        core_definition["tools"] = ["Standard Industry Tools", "Microsoft Office", "Standard Methodologies"]
        core_definition["related_skills"] = [
            {"skill_name": "General Knowledge", "relationship_type": "complementary"},
            {"skill_name": "Domain Expertise", "relationship_type": "parent"}
        ]
        core_definition["measurable_outcomes"] = [
            "Performance metrics",
            "Quality of output",
            "Efficiency improvements"
        ]
        return core_definition


if __name__ == "__main__":
    # Example usage
    enricher = LLMSkillEnricher()
    
    # Example skill to enrich
    sample_skill = "Project Management"
    sample_category = "IT_Management"
    
    # Get enriched definition
    enriched_def = enricher.enrich_skill(sample_skill, sample_category)
    
    # Print the result
    print(json.dumps(enriched_def, indent=2))
