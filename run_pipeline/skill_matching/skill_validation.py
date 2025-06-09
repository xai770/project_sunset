#!/usr/bin/env python3
"""
[DEPRECATED] - DO NOT USE - Continuous Learning and Validation for Skill Enrichments

THIS FILE IS DEPRECATED AND SHOULD NOT BE USED.
A new implementation has replaced this module.
This file is kept only for historical reference.

This module implements continuous learning and validation for the SDR framework as 
recommended by OLMo2. It includes:
1. Feedback mechanisms for skill enrichments
2. Automated quality testing of skill definitions
3. Enhancement learning from human expert feedback
"""

import os
import sys
import json
import logging
import argparse
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

# Add the project root to the path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.append(project_root)

# Import llm_client for feedback processing and LLM Factory
from run_pipeline.utils.llm_client import call_ollama_api  # Fixed import

# Try to import LLM Factory for quality-controlled processing
try:
    from llm_factory.specialist_registry import SpecialistRegistry
    from llm_factory.quality_control import QualityController
    LLM_FACTORY_AVAILABLE = True
except ImportError:
    LLM_FACTORY_AVAILABLE = False

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join(project_root, 'logs', f'skill_validation_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'))
    ]
)
logger = logging.getLogger("skill_validation")

# Constants
SKILL_DIR = os.path.join(project_root, 'docs', 'skill_matching')
FEEDBACK_DIR = os.path.join(project_root, 'data', 'skill_enrichment_feedback')
os.makedirs(FEEDBACK_DIR, exist_ok=True)

class SkillValidationSystem:
    """
    System for validating and continuously improving skill enrichments
    through feedback mechanisms and quality checks.
    """
    
    def __init__(self):
        """Initialize the validation system"""
        self.quality_thresholds = {
            "completeness": 0.9,  # 90% of fields should be filled
            "consistency": 0.8,   # 80% consistency in terminology
            "specificity": 0.7    # 70% of descriptions should be specific enough
        }
        
        # Load existing feedback if available
        self.feedback_data = self._load_feedback_data()
        
        # Initialize LLM Factory
        self.llm_factory_registry = None
        self.quality_controller = None
        self._init_llm_factory()
    
    def _init_llm_factory(self):
        """Initialize LLM Factory specialists for skill validation."""
        if not LLM_FACTORY_AVAILABLE:
            logger.info("LLM Factory not available, using fallback LLM client")
            return
        
        try:
            # Initialize specialist registry
            self.llm_factory_registry = SpecialistRegistry()
            
            # Register skill analysis specialist
            self.llm_factory_registry.register_specialist(
                "skill_analyzer",
                {
                    "type": "document_analysis",
                    "model": "olmo2:latest", 
                    "temperature": 0.2,
                    "max_tokens": 2000,
                    "system_prompt": "You are a professional skill analysis specialist. Analyze skill definitions and feedback to generate improved prompts with precision and clarity."
                }
            )
            
            # Initialize quality controller
            self.quality_controller = QualityController()
            logger.info("LLM Factory initialized for skill validation")
            
        except Exception as e:
            logger.warning(f"Failed to initialize LLM Factory: {e}")
            self.llm_factory_registry = None
            self.quality_controller = None
    
    def _generate_improvement_prompt_with_llm_factory(self, prompt):
        """Generate improvement prompt using LLM Factory specialist."""
        if not self.llm_factory_registry:
            return None
        
        try:
            specialist = self.llm_factory_registry.get_specialist("skill_analyzer")
            response = specialist.generate(prompt)
            
            # Apply quality control
            if self.quality_controller:
                quality_score = self.quality_controller.evaluate_response(response, prompt)
                logger.info(f"LLM Factory skill analysis quality score: {quality_score}")
            
            return response
            
        except Exception as e:
            logger.error(f"Error in LLM Factory skill analysis: {e}")
            return None
    
    def validate_skills(self, enriched_skills_path: str) -> Dict[str, Any]:
        """
        Validate the quality of enriched skill definitions
        
        Args:
            enriched_skills_path: Path to the enriched skills JSON file
            
        Returns:
            Dictionary with validation results and recommendations
        """
        logger.info(f"Validating skills in {enriched_skills_path}")
        
        try:
            with open(enriched_skills_path, 'r') as f:
                enriched_skills = json.load(f)
        except Exception as e:
            logger.error(f"Error loading skills file: {e}")
            return {"error": str(e)}
        
        # Run the validation checks
        completeness_results = self._check_completeness(enriched_skills)
        consistency_results = self._check_consistency(enriched_skills)
        specificity_results = self._check_specificity(enriched_skills)
        
        # Combine results
        validation_results = {
            "timestamp": datetime.now().isoformat(),
            "total_skills": len(enriched_skills),
            "completeness": completeness_results,
            "consistency": consistency_results,
            "specificity": specificity_results,
            "overall_quality_score": (
                completeness_results["overall_score"] * 0.4 + 
                consistency_results["overall_score"] * 0.3 + 
                specificity_results["overall_score"] * 0.3
            ),
            "recommendations": []
        }
        
        # Generate recommendations
        self._generate_recommendations(validation_results)
        
        # Save validation results
        output_path = os.path.join(SKILL_DIR, f'skill_validation_{datetime.now().strftime("%Y%m%d")}.json')
        with open(output_path, 'w') as f:
            json.dump(validation_results, f, indent=2)
        
        logger.info(f"Validation completed. Results saved to {output_path}")
        return validation_results
    
    def process_expert_feedback(self, feedback_path: str) -> Dict[str, Any]:
        """
        Process human expert feedback to improve skill enrichments
        
        Args:
            feedback_path: Path to the expert feedback file
            
        Returns:
            Dictionary with processed feedback and improvement recommendations
        """
        logger.info(f"Processing expert feedback from {feedback_path}")
        
        try:
            with open(feedback_path, 'r') as f:
                feedback = json.load(f)
        except Exception as e:
            logger.error(f"Error loading feedback file: {e}")
            return {"error": str(e)}
        
        # Update the feedback database
        self._update_feedback_database(feedback)
        
        # Generate improvement prompts based on feedback
        improvement_prompts = self._generate_improvement_prompts(feedback)
        
        # Save the improvement prompts
        prompts_path = os.path.join(FEEDBACK_DIR, f'improvement_prompts_{datetime.now().strftime("%Y%m%d")}.json')
        with open(prompts_path, 'w') as f:
            json.dump(improvement_prompts, f, indent=2)
        
        logger.info(f"Feedback processed. Improvement prompts saved to {prompts_path}")
        return {
            "status": "success",
            "feedback_applied": len(feedback.get("skills", [])),
            "improvement_prompts": prompts_path
        }
    
    def generate_quality_report(self, enriched_skills_path: str) -> str:
        """
        Generate a comprehensive quality report for skill enrichments
        
        Args:
            enriched_skills_path: Path to the enriched skills JSON file
            
        Returns:
            Path to the generated report
        """
        logger.info(f"Generating quality report for {enriched_skills_path}")
        
        try:
            with open(enriched_skills_path, 'r') as f:
                enriched_skills = json.load(f)
        except Exception as e:
            logger.error(f"Error loading skills file: {e}")
            return f"Error: {str(e)}"
        
        # Run validation
        validation_results = self.validate_skills(enriched_skills_path)
        
        # Generate report content
        report_content = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_skills": len(enriched_skills),
                "overall_quality": validation_results.get("overall_quality_score", 0),
                "skills_passing_threshold": sum(1 for skill in enriched_skills if self._calculate_skill_quality(skill) > 0.7)
            },
            "validation_results": validation_results,
            "domain_distribution": self._get_domain_distribution(enriched_skills),
            "historical_comparison": self._get_historical_comparison(),
            "recommendations": validation_results.get("recommendations", [])
        }
        
        # Save report
        report_path = os.path.join(SKILL_DIR, f'quality_report_{datetime.now().strftime("%Y%m%d")}.json')
        with open(report_path, 'w') as f:
            json.dump(report_content, f, indent=2)
        
        # Also generate a markdown version for better readability
        markdown_path = report_path.replace('.json', '.md')
        self._generate_markdown_report(report_content, markdown_path)
        
        logger.info(f"Quality report generated: {markdown_path}")
        return markdown_path
    
    def _check_completeness(self, skills: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Check the completeness of skill definitions
        
        Args:
            skills: List of skill definitions to check
            
        Returns:
            Completeness check results
        """
        required_fields = [
            "name", "category", "knowledge_components", "contexts", "functions",
            "proficiency_levels", "related_skills", "tools", "measurable_outcomes",
            "industry_variants", "trend_indicator"
        ]
        
        field_presence = {field: 0 for field in required_fields}
        skill_scores: Dict[str, float] = {}
        
        for skill in skills:
            skill_name = skill.get("name", "Unknown")
            present_fields: float = 0.0
            
            for field in required_fields:
                if field in skill and skill[field]:  # Check if field exists and is not empty
                    field_presence[field] += 1
                    present_fields += 1.0
                    
                    # For list and dict fields, check if they have content
                    if field in skill:
                        if isinstance(skill[field], list) and len(skill[field]) == 0:
                            present_fields -= 0.5  # Penalize empty lists
                        elif isinstance(skill[field], dict) and len(skill[field]) == 0:
                            present_fields -= 0.5  # Penalize empty dicts
            
            # Calculate completeness score for this skill
            skill_scores[skill_name] = present_fields / len(required_fields)
        
        # Calculate overall completeness score
        overall_score = sum(field_presence.values()) / (len(required_fields) * len(skills)) if skills else 0
        
        return {
            "field_presence": {field: count / len(skills) for field, count in field_presence.items()},
            "skill_scores": skill_scores,
            "overall_score": overall_score,
            "meets_threshold": overall_score >= self.quality_thresholds["completeness"]
        }
    
    def _check_consistency(self, skills: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Check the consistency of terminology and structure across skill definitions
        
        Args:
            skills: List of skill definitions to check
            
        Returns:
            Consistency check results
        """
        # Check consistent use of terminology
        terms_by_domain: Dict[str, List[str]] = {}
        domain_skills: Dict[str, List[str]] = {}
        
        for skill in skills:
            domain = skill.get("category", "Unknown")
            if domain not in terms_by_domain:
                terms_by_domain[domain] = []
                domain_skills[domain] = []
            
            # Extract terms from knowledge components
            if "knowledge_components" in skill and isinstance(skill["knowledge_components"], list):
                terms_by_domain[domain].extend(skill["knowledge_components"])
            
            domain_skills[domain].append(skill.get("name", "Unknown"))
        
        # Analyze consistency within domains
        domain_consistency: Dict[str, float] = {}
        overall_consistency_score: float = 0.0
        
        for domain, skills_list in domain_skills.items():
            if len(skills_list) < 2:
                domain_consistency[domain] = 1.0  # Can't check consistency with just one skill
                continue
            
            # Get unique terms
            if domain in terms_by_domain:
                unique_terms = set(terms_by_domain[domain])
                term_counts = {term: terms_by_domain[domain].count(term) for term in unique_terms}
                
                # Calculate consistency score (higher is better)
                repeated_terms = sum(1 for count in term_counts.values() if count > 1)
                consistency_score: float = repeated_terms / len(unique_terms) if unique_terms else 0.0
                domain_consistency[domain] = consistency_score
                overall_consistency_score += consistency_score
            else:
                domain_consistency[domain] = 0.0
        
        # Normalize the overall score
        if domain_consistency:
            overall_consistency_score = overall_consistency_score / len(domain_consistency)
        
        return {
            "domain_consistency": domain_consistency,
            "overall_score": overall_consistency_score,
            "meets_threshold": overall_consistency_score >= self.quality_thresholds["consistency"]
        }
    
    def _check_specificity(self, skills: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Check the specificity of skill definitions (how detailed and precise they are)
        
        Args:
            skills: List of skill definitions to check
            
        Returns:
            Specificity check results
        """
        specificity_scores = {}
        
        # Generic terms that indicate low specificity
        generic_terms = ["general", "basic", "knowledge", "understanding", "standard"]
        
        for skill in skills:
            skill_name = skill.get("name", "Unknown")
            
            # Start with a base score of 1.0 (perfectly specific)
            spec_score = 1.0
            
            # Check knowledge components specificity
            if "knowledge_components" in skill and isinstance(skill["knowledge_components"], list):
                generic_count = sum(1 for term in skill["knowledge_components"] if any(gen in term.lower() for gen in generic_terms))
                if skill["knowledge_components"]:
                    spec_score -= (generic_count / len(skill["knowledge_components"])) * 0.3
            
            # Check proficiency level descriptions
            if "proficiency_levels" in skill and isinstance(skill["proficiency_levels"], dict):
                for level, data in skill["proficiency_levels"].items():
                    desc = data.get("description", "")
                    if len(desc.split()) < 5:  # Too short to be specific
                        spec_score -= 0.1
                    elif any(gen in desc.lower() for gen in generic_terms):
                        spec_score -= 0.05
            
            # Check functions specificity
            if "functions" in skill and isinstance(skill["functions"], list):
                generic_count = sum(1 for func in skill["functions"] if len(func.split()) < 3 or any(gen in func.lower() for gen in generic_terms))
                if skill["functions"]:
                    spec_score -= (generic_count / len(skill["functions"])) * 0.2
            
            # Ensure score is in the range [0, 1]
            specificity_scores[skill_name] = max(0, min(1, spec_score))
        
        # Calculate overall specificity score
        overall_score = sum(specificity_scores.values()) / len(skills) if skills else 0
        
        return {
            "skill_scores": specificity_scores,
            "overall_score": overall_score,
            "meets_threshold": overall_score >= self.quality_thresholds["specificity"]
        }
    
    def _generate_recommendations(self, validation_results: Dict[str, Any]) -> None:
        """
        Generate recommendations based on validation results
        
        Args:
            validation_results: The validation results to base recommendations on
        """
        recommendations = []
        
        # Check completeness
        completeness = validation_results.get("completeness", {})
        if "field_presence" in completeness:
            for field, presence in completeness["field_presence"].items():
                if presence < 0.8:  # Less than 80% of skills have this field
                    recommendations.append(
                        f"Improve completeness of '{field}' field which is missing in {int((1-presence)*100)}% of skills"
                    )
        
        # Check if overall quality is below threshold
        overall_score = validation_results.get("overall_quality_score", 0)
        if overall_score < 0.7:
            recommendations.append(
                f"Overall quality score ({overall_score:.2f}) is below the recommended threshold (0.7). "
                "Consider regenerating skill definitions with improved prompts."
            )
        
        # Check domain consistency
        consistency = validation_results.get("consistency", {})
        if "domain_consistency" in consistency:
            low_consistency_domains = [
                domain for domain, score in consistency["domain_consistency"].items() 
                if score < 0.6
            ]
            if low_consistency_domains:
                domains_str = ", ".join(low_consistency_domains)
                recommendations.append(
                    f"Improve terminology consistency in the following domains: {domains_str}"
                )
        
        # Add general recommendations based on scores
        if "completeness" in validation_results and not validation_results["completeness"].get("meets_threshold", False):
            recommendations.append(
                "Implement mandatory field validation to ensure all required components are present in each skill"
            )
        
        if "specificity" in validation_results and not validation_results["specificity"].get("meets_threshold", False):
            recommendations.append(
                "Improve specificity of skill definitions by using more precise terms and detailed descriptions"
            )
        
        # Add the recommendations to the validation results
        validation_results["recommendations"] = recommendations
    
    def _load_feedback_data(self) -> Dict[str, Any]:
        """
        Load existing feedback data, if available
        
        Returns:
            Dictionary of feedback data
        """
        feedback_file = os.path.join(FEEDBACK_DIR, 'feedback_database.json')
        if os.path.exists(feedback_file):
            try:
                with open(feedback_file, 'r') as f:
                    return json.load(f)  # type: ignore
            except Exception as e:
                logger.error(f"Error loading feedback database: {e}")
                return {
                    "version": 1.0,
                    "last_updated": datetime.now().isoformat(),
                    "feedback_entries": []
                }
        else:
            return {
                "version": 1.0,
                "last_updated": datetime.now().isoformat(),
                "feedback_entries": []
            }
    
    def _update_feedback_database(self, new_feedback: Dict[str, Any]) -> None:
        """
        Update the feedback database with new feedback
        
        Args:
            new_feedback: Dictionary containing new feedback
        """
        if "skills" not in new_feedback:
            logger.warning("No skills found in feedback data")
            return
        
        # Add new feedback entries
        for skill_feedback in new_feedback["skills"]:
            self.feedback_data["feedback_entries"].append({
                "timestamp": datetime.now().isoformat(),
                "skill": skill_feedback.get("skill_name", "Unknown"),
                "feedback": skill_feedback.get("feedback", {}),
                "suggested_improvements": skill_feedback.get("suggested_improvements", [])
            })
        
        # Update the last updated timestamp
        self.feedback_data["last_updated"] = datetime.now().isoformat()
        
        # Save the updated feedback database
        feedback_file = os.path.join(FEEDBACK_DIR, 'feedback_database.json')
        with open(feedback_file, 'w') as f:
            json.dump(self.feedback_data, f, indent=2)
        
        logger.info(f"Feedback database updated with {len(new_feedback['skills'])} new entries")
    
    def _generate_improvement_prompts(self, feedback: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate improvement prompts based on feedback
        
        Args:
            feedback: Dictionary containing feedback
            
        Returns:
            Dictionary with improvement prompts
        """
        improvement_prompts: Dict[str, Any] = {
            "timestamp": datetime.now().isoformat(),
            "prompts_by_skill": {}
        }
        
        if "skills" not in feedback:
            return improvement_prompts
        
        for skill_feedback in feedback["skills"]:
            skill_name = skill_feedback.get("skill_name", "Unknown")
            
            # Format the feedback as a prompt for OLMo2
            prompt = f"""
            You are helping improve a skill definition for: "{skill_name}"
            
            You've received the following expert feedback:
            {json.dumps(skill_feedback.get('feedback', {}), indent=2)}
            
            Suggested improvements from the expert:
            {json.dumps(skill_feedback.get('suggested_improvements', []), indent=2)}
            
            Please create an improved prompt for generating a better skill definition that addresses this feedback.
            The prompt should be specific and guide the LLM to focus on the areas mentioned in the feedback.
            """
            
            # Try using LLM Factory for quality-controlled improvement prompt generation
            response = self._generate_improvement_prompt_with_llm_factory(prompt.strip())
            
            # Fallback to regular OLMo API if needed
            if response:
                improvement_prompts["prompts_by_skill"][skill_name] = response
            else:
                try:
                    response = call_ollama_api(prompt.strip(), model="olmo2:latest")
                    improvement_prompts["prompts_by_skill"][skill_name] = response
                except Exception as e:
                    logger.error(f"Error generating improvement prompt for {skill_name}: {e}")
                    improvement_prompts["prompts_by_skill"][skill_name] = f"Error generating prompt: {str(e)}"
        
        return improvement_prompts
    
    def _calculate_skill_quality(self, skill: Dict[str, Any]) -> float:
        """Calculate quality score for a single skill"""
        score = 1.0
        
        # Check required fields
        required_fields = [
            "name", "category", "knowledge_components", "contexts", "functions", 
            "proficiency_levels", "related_skills"
        ]
        
        for field in required_fields:
            if field not in skill:
                score -= 0.1
                continue
                
            # Check content of lists and dicts
            if isinstance(skill[field], list) and len(skill[field]) == 0:
                score -= 0.05
            elif isinstance(skill[field], dict) and len(skill[field]) == 0:
                score -= 0.05
        
        return max(0, score)  # Ensure non-negative score
    
    def _get_domain_distribution(self, skills: List[Dict[str, Any]]) -> Dict[str, int]:
        """Get the distribution of skills across domains"""
        distribution: Dict[str, int] = {}
        
        for skill in skills:
            category = skill.get("category", "Unknown")
            distribution[category] = distribution.get(category, 0) + 1
        
        return distribution
    
    def _get_historical_comparison(self) -> Dict[str, Any]:
        """Get a comparison with historical quality data if available"""
        # Look for previous validation files
        validation_files = [
            f for f in os.listdir(SKILL_DIR) 
            if f.startswith('skill_validation_') and f.endswith('.json')
        ]
        
        if not validation_files:
            return {"available": False}
        
        # Sort by date (newest first, excluding today)
        today = datetime.now().strftime("%Y%m%d")
        validation_files = [
            f for f in validation_files
            if f.replace('skill_validation_', '').replace('.json', '') < today
        ]
        
        if not validation_files:
            return {"available": False}
        
        validation_files.sort(reverse=True)
        
        # Get the most recent file
        most_recent = validation_files[0]
        
        try:
            with open(os.path.join(SKILL_DIR, most_recent), 'r') as f:
                previous_validation = json.load(f)
                
                return {
                    "available": True,
                    "previous_date": most_recent.replace('skill_validation_', '').replace('.json', ''),
                    "previous_overall_score": previous_validation.get("overall_quality_score", 0),
                    "trend": "improving" if previous_validation.get("overall_quality_score", 0) < 0.7 else "stable"
                }
        except Exception as e:
            logger.error(f"Error loading previous validation: {e}")
            return {"available": False, "error": str(e)}
    
    def _generate_markdown_report(self, report_data: Dict[str, Any], output_path: str) -> None:
        """Generate a markdown report from the report data"""
        with open(output_path, 'w') as f:
            f.write(f"# Skill Enrichment Quality Report\n\n")
            f.write(f"*Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n")
            
            # Write summary section
            f.write("## Summary\n\n")
            summary = report_data.get("summary", {})
            f.write(f"- Total skills analyzed: {summary.get('total_skills', 0)}\n")
            f.write(f"- Overall quality score: {summary.get('overall_quality', 0):.2f} / 1.0\n")
            f.write(f"- Skills passing quality threshold: {summary.get('skills_passing_threshold', 0)} ")
            f.write(f"({(summary.get('skills_passing_threshold', 0) / summary.get('total_skills', 1) * 100):.1f}%)\n\n")
            
            # Write domain distribution
            f.write("## Domain Distribution\n\n")
            distribution = report_data.get("domain_distribution", {})
            for domain, count in distribution.items():
                f.write(f"- {domain}: {count} skills\n")
            f.write("\n")
            
            # Write validation results
            f.write("## Validation Results\n\n")
            validation = report_data.get("validation_results", {})
            
            f.write("### Completeness\n\n")
            completeness = validation.get("completeness", {})
            f.write(f"Score: {completeness.get('overall_score', 0):.2f} / 1.0 ")
            f.write(f"({'PASS' if completeness.get('meets_threshold', False) else 'FAIL'})\n\n")
            
            f.write("### Consistency\n\n")
            consistency = validation.get("consistency", {})
            f.write(f"Score: {consistency.get('overall_score', 0):.2f} / 1.0 ")
            f.write(f"({'PASS' if consistency.get('meets_threshold', False) else 'FAIL'})\n\n")
            
            f.write("### Specificity\n\n")
            specificity = validation.get("specificity", {})
            f.write(f"Score: {specificity.get('overall_score', 0):.2f} / 1.0 ")
            f.write(f"({'PASS' if specificity.get('meets_threshold', False) else 'FAIL'})\n\n")
            
            # Write historical comparison
            historical = report_data.get("historical_comparison", {})
            if historical.get("available", False):
                f.write("## Historical Comparison\n\n")
                f.write(f"Previous quality score: {historical.get('previous_overall_score', 0):.2f} (from {historical.get('previous_date', 'unknown')})\n")
                f.write(f"Trend: {historical.get('trend', 'unknown')}\n\n")
            
            # Write recommendations
            f.write("## Recommendations\n\n")
            recommendations = report_data.get("recommendations", [])
            for i, rec in enumerate(recommendations, 1):
                f.write(f"{i}. {rec}\n")
            
            if not recommendations:
                f.write("No recommendations at this time. The skill enrichments meet the quality criteria.\n")


def main():
    """Main function for the validation system"""
    parser = argparse.ArgumentParser(description='Validate and improve skill enrichments')
    
    # Command group
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Validate command
    validate_parser = subparsers.add_parser('validate', help='Validate enriched skills')
    validate_parser.add_argument('--file', type=str, default=os.path.join(SKILL_DIR, 'enriched_skills.json'),
                       help='Path to the enriched skills JSON file')
    
    # Process feedback command
    feedback_parser = subparsers.add_parser('process-feedback', help='Process human expert feedback')
    feedback_parser.add_argument('--file', required=True, type=str,
                       help='Path to the feedback JSON file')
    
    # Generate report command
    report_parser = subparsers.add_parser('report', help='Generate quality report')
    report_parser.add_argument('--file', type=str, default=os.path.join(SKILL_DIR, 'enriched_skills.json'),
                       help='Path to the enriched skills JSON file')
    
    args = parser.parse_args()
    
    validation_system = SkillValidationSystem()
    
    if args.command == 'validate':
        results = validation_system.validate_skills(args.file)
        if "error" not in results:
            print(f"\nValidation completed successfully.")
            print(f"Overall quality score: {results.get('overall_quality_score', 0):.2f} / 1.0")
            print("\nTop recommendations:")
            for i, rec in enumerate(results.get("recommendations", []), 1):
                if i > 3:
                    break
                print(f"{i}. {rec}")
            
            # Show full results path
            print(f"\nFull results saved to: {os.path.join(SKILL_DIR, 'skill_validation_' + datetime.now().strftime('%Y%m%d') + '.json')}")
        else:
            print(f"Error during validation: {results['error']}")
    
    elif args.command == 'process-feedback':
        results = validation_system.process_expert_feedback(args.file)
        if "error" not in results:
            print(f"\nFeedback processed successfully.")
            print(f"Feedback applied to {results.get('feedback_applied', 0)} skills.")
            print(f"Improvement prompts saved to: {results.get('improvement_prompts', 'unknown')}")
        else:
            print(f"Error processing feedback: {results['error']}")
    
    elif args.command == 'report':
        report_path = validation_system.generate_quality_report(args.file)
        if not report_path.startswith("Error:"):
            print(f"\nQuality report generated successfully.")
            print(f"Report saved to: {report_path}")
        else:
            print(f"Error generating report: {report_path}")
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
