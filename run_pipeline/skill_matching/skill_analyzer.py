#!/usr/bin/env python3
"""
Skill Analyzer - Extracts, analyzes, and ranks skills from job postings and CV

This script implements the first phase of the SDR (Skill Domain Relationship) framework
by analyzing skills from job postings and CVs, calculating their frequency, ambiguity,
and impact, and selecting the highest priority skills for standardization.

Enhanced with LLM-based skill enrichment capabilities based on OLMo2 recommendations.
"""

import os
import json
import glob
from collections import Counter, defaultdict
import re
import logging
import sys
from typing import Dict, List, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("skill_analyzer")

# Constants
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
postings_DIR = os.path.join(BASE_DIR, 'data', 'postings')
GERSHON_SKILLS_PATH = os.path.join(BASE_DIR, 'docs', 'skill_matching', 'gershon-skills-categorized.json')
OUTPUT_DIR = os.path.join(BASE_DIR, 'docs', 'skill_matching')

# Define the six core domains
CORE_DOMAINS = [
    "IT_Technical",
    "IT_Management",
    "Sourcing_and_Procurement",
    "Leadership_and_Management",
    "Analysis_and_Reporting",
    "Domain_Knowledge"
]

# Common terms used to identify skills in job descriptions
SKILL_IDENTIFIERS = [
    'experience with', 'knowledge of', 'proficiency in', 'skilled in',
    'expertise in', 'familiar with', 'background in', 'ability to',
    'understanding of', 'competency in', 'capability in', 'training in',
    'certification in', 'degree in', 'qualified in', 'specialization in',
    'mastery of', 'literacy in', 'fluency in', 'skills'
]

class SkillAnalyzer:
    """Analyzes skills from job postings and CVs to identify high-priority skills for standardization"""
    
    def __init__(self):
        self.job_skills = []
        self.cv_skills = {}
        self.all_skills = set()
        self.skill_frequencies: Counter[str] = Counter()
        self.skill_domains = {}
        self.skill_ambiguity = {}
        self.skill_impact = {}
        
    def load_job_skills(self):
        """Load skills from all job postings in the data directory"""
        print("Loading job skills...")
        job_files = glob.glob(os.path.join(postings_DIR, '*.json'))
        
        for job_file in job_files:
            try:
                with open(job_file, 'r') as f:
                    job_data = json.load(f)
                
                if 'web_details' in job_data and 'structured_description' in job_data['web_details']:
                    structured_desc = job_data['web_details']['structured_description']
                    if 'requirements' in structured_desc:
                        for req in structured_desc['requirements']:
                            # Extract skills from requirements
                            extracted_skills = self._extract_skills_from_text(req)
                            self.job_skills.extend(extracted_skills)
                            
                            # Update frequency counter
                            self.skill_frequencies.update(extracted_skills)
                            
                            # Add to all skills
                            self.all_skills.update(extracted_skills)
            except Exception as e:
                print(f"Error processing job file {job_file}: {e}")
                
        print(f"Found {len(self.job_skills)} skills in job postings")
    
    def load_cv_skills(self):
        """Load skills from Gershon's CV"""
        print("Loading CV skills...")
        try:
            with open(GERSHON_SKILLS_PATH, 'r') as f:
                cv_data = json.load(f)
            
            # Load skills with their domain categories
            if 'skill_categories' in cv_data:
                for domain, skills in cv_data['skill_categories'].items():
                    if domain not in self.cv_skills:
                        self.cv_skills[domain] = []
                    
                    for skill in skills:
                        self.cv_skills[domain].append(skill['name'])
                        self.skill_domains[skill['name']] = domain
                        self.all_skills.add(skill['name'])
                        
            print(f"Found {sum(len(skills) for skills in self.cv_skills.values())} skills in CV")
        except Exception as e:
            print(f"Error processing CV file: {e}")
    
    def calculate_ambiguity_factors(self):
        """Calculate ambiguity factors for all skills"""
        print("Calculating ambiguity factors...")
        
        # For demonstration purposes, here's a simplified method to estimate ambiguity
        # In a real implementation, this would be more sophisticated
        for skill in self.all_skills:
            # Estimate naming variations (1-10)
            naming_variations = min(10, len(re.findall(r'\b\w+\b', skill)))
            
            # Estimate context variations (1-10)
            # Higher for generic skills, lower for specific skills
            context_variations = 10 if len(skill.split()) < 2 else 10 - len(skill.split())
            context_variations = max(1, min(10, context_variations))
            
            # Estimate classification inconsistency (1-10)
            # Generic skills are more likely to be inconsistently classified
            classification_inconsistency = 10 if len(skill.split()) < 2 else 10 - len(skill.split())
            classification_inconsistency = max(1, min(10, classification_inconsistency))
            
            # Calculate ambiguity factor
            ambiguity_factor = (naming_variations + context_variations + classification_inconsistency) / 3
            self.skill_ambiguity[skill] = ambiguity_factor
    
    def calculate_impact_scores(self):
        """Calculate impact scores for all skills"""
        print("Calculating impact scores...")
        
        for skill in self.all_skills:
            frequency = self.skill_frequencies[skill]
            ambiguity = self.skill_ambiguity.get(skill, 5)  # Default to 5 if not calculated
            
            # Estimate usage in essential requirements (1-5)
            # For demonstration, we'll just use a default value of 3
            essential_usage = 3
            
            impact_score = frequency * ambiguity * essential_usage
            self.skill_impact[skill] = impact_score
    
    def select_top_skills(self, num_skills=50):
        """Select the top skills based on impact score, ensuring representation across domains"""
        print(f"Selecting top {num_skills} skills...")
        
        # Sort skills by impact score
        sorted_skills = sorted(self.skill_impact.items(), key=lambda x: x[1], reverse=True)
        
        # Initialize selection
        selected_skills = []
        domain_counts = {domain: 0 for domain in CORE_DOMAINS}
        
        # First, ensure minimum representation from each domain
        min_per_domain = 5
        remaining = num_skills - (min_per_domain * len(CORE_DOMAINS))
        
        # If we can't ensure minimum representation, adjust the minimum
        if remaining < 0:
            min_per_domain = num_skills // len(CORE_DOMAINS)
            remaining = num_skills - (min_per_domain * len(CORE_DOMAINS))
        
        # Add highest impact skills from each domain
        for domain in CORE_DOMAINS:
            domain_skills = [s for s, _ in sorted_skills if self.skill_domains.get(s) == domain]
            selected_from_domain = domain_skills[:min_per_domain]
            selected_skills.extend(selected_from_domain)
            domain_counts[domain] = len(selected_from_domain)
        
        # Add remaining skills by highest impact score
        if remaining > 0:
            # Filter out already selected skills
            remaining_skills = [s for s, _ in sorted_skills if s not in selected_skills]
            selected_skills.extend(remaining_skills[:remaining])
        
        return selected_skills[:num_skills]
    
    def create_enriched_skill_definition(self, skill, use_llm=False):
        """
        Create an enriched skill definition for a given skill based on OLMo2 recommendations
        
        Args:
            skill: The skill name to enrich
            use_llm: Whether to use the LLM-based enrichment (True) or fallback to placeholders (False)
            
        Returns:
            An enriched skill definition
        """
        # Get domain for the skill
        domain = self.skill_domains.get(skill, self._guess_domain(skill))
        
        # Get ambiguity factor
        ambiguity_factor = self.skill_ambiguity.get(skill, 0.5)
        
        if use_llm:
            # LLM-based enrichment is now handled by direct specialist integration
            # For now, we use enhanced placeholder enrichment until SkillAnalysisSpecialist is available
            logger.info(f"LLM enrichment requested for skill: {skill}, using enhanced placeholder until specialist is available")
            return self._create_placeholder_enrichment(skill, domain, ambiguity_factor)
        else:
            # Use enhanced placeholder method
            return self._create_placeholder_enrichment(skill, domain, ambiguity_factor)
    
    def _create_placeholder_enrichment(self, skill, domain, ambiguity_factor):
        """Create a placeholder enrichment using static methods (legacy approach)"""
        # Create components for the enriched definition using placeholder generators
        knowledge_components = self._generate_knowledge_components(skill, domain)
        contexts = self._generate_contexts(skill, domain)
        functions = self._generate_functions(skill, domain)
        
        # Generate proficiency levels
        proficiency_levels = self._generate_proficiency_levels(skill, domain)
        
        # Generate related skills (placeholders)
        related_skills = self._generate_related_skills(skill, domain)
        
        # Generate industry variants (placeholders)
        industry_variants = self._generate_industry_variants(skill, domain)
        
        # Generate tools associated with the skill (placeholders)
        tools = self._generate_tools(skill, domain)
        
        # Generate measurable outcomes (placeholders)
        measurable_outcomes = self._generate_measurable_outcomes(skill, domain)
        
        # Create the enriched definition with the enhanced structure
        enriched_definition = {
            "name": skill,
            "category": domain,
            "proficiency_levels": proficiency_levels,
            "knowledge_components": knowledge_components,
            "contexts": contexts,
            "functions": functions,
            "ambiguity_factor": ambiguity_factor,
            "related_skills": related_skills,
            "industry_variants": industry_variants,
            "tools": tools,
            "measurable_outcomes": measurable_outcomes,
            "trend_indicator": self._generate_trend_indicator(skill)
        }
        
        return enriched_definition
    
    def run_analysis(self, use_llm=False, max_skills=50):
        """
        Run the complete skill analysis
        
        Args:
            use_llm: Whether to use LLM-based enrichment (slower but higher quality)
            max_skills: Maximum number of skills to analyze
            
        Returns:
            A list of enriched skill definitions
        """
        self.load_job_skills()
        self.load_cv_skills()
        self.calculate_ambiguity_factors()
        self.calculate_impact_scores()
        top_skills = self.select_top_skills(num_skills=max_skills)
        
        logger.info(f"Top skills selected: {len(top_skills)}")
        
        # Create enriched definitions for top skills
        logger.info(f"Creating enriched definitions (use_llm={use_llm})...")
        enriched_skills = []
        
        for i, skill in enumerate(top_skills):
            logger.info(f"Processing skill {i+1}/{len(top_skills)}: {skill}")
            enriched_definition = self.create_enriched_skill_definition(skill, use_llm=use_llm)
            enriched_skills.append(enriched_definition)
        
        # Save results
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        output_file = os.path.join(OUTPUT_DIR, 'enriched_skills.json')
        with open(output_file, 'w') as f:
            json.dump(enriched_skills, f, indent=2)
        
        logger.info(f"Enriched skill definitions saved to {output_file}")
        
        return enriched_skills
    
    def _extract_skills_from_text(self, text):
        """Extract skills from text using skill identifiers"""
        skills = []
        
        # Convert text to lowercase for case-insensitive matching
        text_lower = text.lower()
        
        # Look for skills identified by common phrases
        for identifier in SKILL_IDENTIFIERS:
            if identifier in text_lower:
                # Find the part after the identifier
                parts = text_lower.split(identifier)
                for i in range(1, len(parts)):
                    # Extract the skill (up to the next period, comma, or end)
                    skill_text = parts[i].strip()
                    skill_text = re.split(r'[,.]', skill_text)[0].strip()
                    
                    # Clean up the skill text
                    skill_text = re.sub(r'^\s*in\s+', '', skill_text)  # Remove leading "in"
                    
                    if skill_text and len(skill_text.split()) < 5:  # Limit to reasonable length
                        skills.append(skill_text)
        
        # Also look for capitalized noun phrases which often indicate technologies or methodologies
        noun_phrases = re.findall(r'\b[A-Z][a-zA-Z0-9]+(?: [a-zA-Z0-9]+){0,3}\b', text)
        skills.extend([np.lower() for np in noun_phrases])
        
        # Remove duplicates and return
        return list(set(skills))
    
    def _guess_domain(self, skill):
        """Guess the domain for a skill based on keywords"""
        skill_lower = skill.lower()
        
        # IT_Technical keywords
        if any(kw in skill_lower for kw in ['programming', 'development', 'coding', 'software', 'database', 
                                           'python', 'java', 'javascript', 'sql', 'infrastructure']):
            return "IT_Technical"
        
        # IT_Management keywords
        elif any(kw in skill_lower for kw in ['governance', 'itil', 'project management', 'service management',
                                             'change management', 'release', 'deployment']):
            return "IT_Management"
        
        # Sourcing_and_Procurement keywords
        elif any(kw in skill_lower for kw in ['procurement', 'sourcing', 'vendor', 'contract', 'negotiation',
                                             'supplier', 'purchasing']):
            return "Sourcing_and_Procurement"
        
        # Leadership_and_Management keywords
        elif any(kw in skill_lower for kw in ['leadership', 'management', 'team', 'strategy', 'coaching',
                                             'mentoring', 'stakeholder']):
            return "Leadership_and_Management"
        
        # Analysis_and_Reporting keywords
        elif any(kw in skill_lower for kw in ['analysis', 'analytics', 'reporting', 'data', 'metrics',
                                             'kpi', 'statistics', 'financial']):
            return "Analysis_and_Reporting"
        
        # Default to Domain_Knowledge for industry-specific skills
        else:
            return "Domain_Knowledge"
    
    def _generate_knowledge_components(self, skill, domain):
        """Generate knowledge components for a skill"""
        # This is a placeholder. In a real implementation, this would be more sophisticated.
        if domain == "IT_Technical":
            return ["technical_fundamentals", "system_architecture"]
        elif domain == "IT_Management":
            return ["project_methodology", "it_governance"]
        elif domain == "Sourcing_and_Procurement":
            return ["negotiation_techniques", "market_analysis"]
        elif domain == "Leadership_and_Management":
            return ["leadership_principles", "team_dynamics"]
        elif domain == "Analysis_and_Reporting":
            return ["data_analysis", "reporting_methods"]
        else:  # Domain_Knowledge
            return ["industry_standards", "regulatory_requirements"]
    
    def _generate_contexts(self, skill, domain):
        """Generate contexts for a skill"""
        # This is a placeholder. In a real implementation, this would be more sophisticated.
        if domain == "IT_Technical":
            return ["development_environment", "production_systems"]
        elif domain == "IT_Management":
            return ["enterprise_it", "service_delivery"]
        elif domain == "Sourcing_and_Procurement":
            return ["vendor_management", "contract_negotiation"]
        elif domain == "Leadership_and_Management":
            return ["team_management", "executive_decision_making"]
        elif domain == "Analysis_and_Reporting":
            return ["business_intelligence", "management_reporting"]
        else:  # Domain_Knowledge
            return ["industry_specific", "regulatory_environment"]
    
    def _generate_functions(self, skill, domain):
        """Generate functions for a skill"""
        # This is a placeholder. In a real implementation, this would be more sophisticated.
        if domain == "IT_Technical":
            return ["building_solutions", "technical_problem_solving"]
        elif domain == "IT_Management":
            return ["governing_it_systems", "managing_it_projects"]
        elif domain == "Sourcing_and_Procurement":
            return ["negotiating_contracts", "managing_vendors"]
        elif domain == "Leadership_and_Management":
            return ["leading_teams", "managing_performance"]
        elif domain == "Analysis_and_Reporting":
            return ["analyzing_data", "creating_reports"]
        else:  # Domain_Knowledge
            return ["applying_domain_knowledge", "ensuring_compliance"]
    
    def _generate_proficiency_levels(self, skill, domain):
        """Generate proficiency levels for a skill"""
        # This is a placeholder. In a real implementation, this would use LLMs
        beginner = {
            "description": f"Basic understanding of {skill}",
            "estimated_acquisition_time": "1-3 months"
        }
        intermediate = {
            "description": f"Working knowledge of {skill} with some practical experience",
            "estimated_acquisition_time": "6-12 months"
        }
        advanced = {
            "description": f"Expert-level knowledge and extensive experience with {skill}",
            "estimated_acquisition_time": "2-3 years"
        }
        
        return {
            "beginner": beginner,
            "intermediate": intermediate,
            "advanced": advanced
        }
    
    def _generate_related_skills(self, skill, domain):
        """Generate related skills for a skill"""
        # This is a placeholder. In a real implementation, this would use the relationship matrix
        if domain == "IT_Technical":
            return [
                {"skill_name": "Programming Languages", "relationship_type": "complementary"},
                {"skill_name": "Software Development", "relationship_type": "parent"}
            ]
        elif domain == "IT_Management":
            return [
                {"skill_name": "Project Management", "relationship_type": "complementary"},
                {"skill_name": "IT Governance", "relationship_type": "parent"}
            ]
        else:
            return [
                {"skill_name": "Communication", "relationship_type": "complementary"}
            ]
    
    def _generate_industry_variants(self, skill, domain):
        """Generate industry variants for a skill"""
        # This is a placeholder. In a real implementation, this would use LLMs
        return {
            "finance": f"{skill} applied to financial services and banking environments",
            "healthcare": f"{skill} applied to healthcare and medical environments",
            "manufacturing": f"{skill} applied to production and manufacturing environments"
        }
    
    def _generate_tools(self, skill, domain):
        """Generate tools associated with the skill"""
        # This is a placeholder. In a real implementation, this would use LLMs
        if domain == "IT_Technical":
            return ["Visual Studio Code", "Git", "Docker"]
        elif domain == "IT_Management":
            return ["Jira", "Confluence", "Microsoft Project"]
        elif domain == "Analysis_and_Reporting":
            return ["Tableau", "Power BI", "Excel"]
        else:
            return ["Microsoft Office Suite", "Collaboration tools"]
    
    def _generate_measurable_outcomes(self, skill, domain):
        """Generate measurable outcomes for the skill"""
        # This is a placeholder. In a real implementation, this would use LLMs
        if domain == "IT_Technical":
            return ["Number of successful deployments", "Reduction in bugs", "Code quality metrics"]
        elif domain == "Leadership_and_Management":
            return ["Team performance improvements", "Project delivery rate", "Employee satisfaction"]
        else:
            return ["Productivity improvements", "Quality metrics", "Customer/stakeholder satisfaction"]
    
    def _generate_trend_indicator(self, skill):
        """Generate a trend indicator for the skill"""
        # This is a placeholder. In a real implementation, this would use market data
        # For now, randomly select from growing, stable, declining
        import random
        trends = ["growing", "stable", "declining"]
        return random.choice(trends)


if __name__ == "__main__":
    import argparse
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Analyze and enrich skills using the SDR framework')
    parser.add_argument('--use-llm', action='store_true', help='Use LLM for skill enrichment (higher quality but slower)')
    parser.add_argument('--max-skills', type=int, default=50, help='Maximum number of skills to analyze')
    args = parser.parse_args()
    
    # Run the analysis
    analyzer = SkillAnalyzer()
    analyzer.run_analysis(use_llm=args.use_llm, max_skills=args.max_skills)
