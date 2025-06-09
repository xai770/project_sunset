#!/usr/bin/env python3
"""
Skills Gap Analyzer for Cover Letter Generation

This module analyzes the gap between job requirements and candidate skills,
providing insights and suggestions for cover letter content to address potential gaps.
"""

import os
import json
import logging
import re
from pathlib import Path
from collections import defaultdict

# Configure logging
logger = logging.getLogger(__name__)

class SkillsGapAnalyzer:
    """
    Analyzes the gap between job requirements and candidate skills,
    providing recommendations for cover letter content.
    """
    
    def __init__(self, cv_skills_path=None):
        """
        Initialize the SkillsGapAnalyzer with CV skills data.
        
        Args:
            cv_skills_path (str, optional): Path to the CV skills JSON file
        """
        self.cv_skills = {}
        self.skill_categories = {
            "technical": {
                "keywords": ["software", "programming", "technical", "technology", "system", 
                            "database", "cloud", "infrastructure", "code", "developer",
                            "engineering", "architecture", "IT", "computer", "network"],
                "transferable_skills": [
                    "Technical problem-solving abilities",
                    "System architecture understanding",
                    "Technology implementation experience"
                ]
            },
            "compliance": {
                "keywords": ["compliance", "regulation", "audit", "legal", "governance", 
                            "policy", "risk", "security", "standard", "requirement",
                            "control", "procedure", "protocol", "guideline", "restriction"],
                "transferable_skills": [
                    "Regulatory awareness and adherence",
                    "Policy development and implementation",
                    "Risk assessment methodology"
                ]
            },
            "management": {
                "keywords": ["management", "leadership", "team", "project", "strategy", 
                            "planning", "coordination", "budget", "resource", "stakeholder",
                            "supervision", "direction", "organization", "delegation", "execution"],
                "transferable_skills": [
                    "Team leadership and coordination",
                    "Strategic planning and execution",
                    "Stakeholder management"
                ]
            },
            "communication": {
                "keywords": ["communication", "presentation", "documentation", "writing", "speaking", 
                            "negotiation", "client", "meeting", "report", "collaboration",
                            "interpersonal", "articulation", "training", "teaching", "explanation"],
                "transferable_skills": [
                    "Clear and concise documentation",
                    "Stakeholder communication",
                    "Technical concept explanation to non-technical audiences"
                ]
            },
            "analysis": {
                "keywords": ["analysis", "research", "data", "evaluation", "assessment", 
                            "investigation", "calculation", "measurement", "testing", "validation",
                            "insight", "analytics", "statistics", "metrics", "indicators"],
                "transferable_skills": [
                    "Data-driven decision making",
                    "Pattern recognition and insight generation",
                    "Critical analysis of complex problems"
                ]
            }
        }
        
        # Load CV skills if provided
        if cv_skills_path:
            self.load_cv_skills(cv_skills_path)
        else:
            # Try to find skills in default locations
            self._find_and_load_cv_skills()
    
    def _find_and_load_cv_skills(self):
        """Attempt to find and load CV skills from common locations."""
        possible_paths = [
            os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "cv_skills.json"),
            os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data", "cv_skills.json"),
            os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "profile", "skills", "technical_skills.json")
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                logger.info(f"Found CV skills data at: {path}")
                self.load_cv_skills(path)
                return
        
        logger.warning("Could not find CV skills data. Using default empty skills.")
    
    def load_cv_skills(self, file_path):
        """
        Load CV skills from a JSON file.
        
        Args:
            file_path (str): Path to the CV skills JSON file
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                self.cv_skills = json.load(f)  # type: ignore
            logger.info(f"Successfully loaded CV skills from {file_path}")
        except Exception as e:
            logger.error(f"Error loading CV skills: {e}")
    
    def extract_job_requirements(self, job_data):
        """
        Extract key job requirements from job data.
        
        Args:
            job_data (dict): Job data dictionary
            
        Returns:
            dict: Dictionary of job requirements by category
        """
        # If job data contains parsed requirements, use those
        if 'parsed_requirements' in job_data:
            return job_data['parsed_requirements']
        
        # Otherwise extract from job description
        requirements = defaultdict(list)
        job_description = ""
        job_title = ""
        
        # Try different fields where description might be found
        if 'search_details' in job_data and 'JobDescription' in job_data['search_details']:
            job_description = job_data['search_details']['JobDescription']
            job_title = job_data['search_details'].get('JobTitle', '')
        elif 'api_details' in job_data and 'description' in job_data['api_details']:
            job_description = job_data['api_details']['description']
            job_title = job_data['api_details'].get('title', '')
        elif 'job_description' in job_data:
            job_description = job_data['job_description']
            job_title = job_data.get('job_title', '')
        
        if not job_description:
            logger.warning("No job description found in job data")
            return requirements
        
        # Comprehensive keyword extraction with weighted scoring
        requirement_scores = defaultdict(float)
        
        # First pass: Check for explicit requirement statements
        requirement_patterns = [
            r"required skills?:?\s*(.*?)(?:\.|;|$)",
            r"requirements?:?\s*(.*?)(?:\.|;|$)",
            r"qualifications?:?\s*(.*?)(?:\.|;|$)",
            r"must have:?\s*(.*?)(?:\.|;|$)",
            r"experience (?:with|in):?\s*(.*?)(?:\.|;|$)"
        ]
        
        for pattern in requirement_patterns:
            matches = re.finditer(pattern, job_description, re.IGNORECASE)
            for match in matches:
                requirement_text = match.group(1).strip()
                # Process each explicit requirement
                for category, data in self.skill_categories.items():
                    for keyword in data["keywords"]:
                        if keyword.lower() in requirement_text.lower():
                            # Higher weight for requirements in explicit sections
                            requirement_scores[(category, keyword)] += 3.0
                            
        # Second pass: Check for keywords throughout the description
        for category, data in self.skill_categories.items():
            for keyword in data["keywords"]:
                # Count occurrences of the keyword
                pattern = r'\b{}\w*\b'.format(re.escape(keyword))
                matches = re.findall(pattern, job_description, re.IGNORECASE)
                
                if matches:
                    # Base score based on number of occurrences
                    base_score = min(len(matches) * 0.5, 3.0)  # Cap at 3.0
                    
                    # Bonus if keyword appears in job title
                    title_bonus = 2.0 if keyword.lower() in job_title.lower() else 0.0
                    
                    # Bonus for keyword appearing early in description
                    position_bonus = 0.0
                    first_pos = job_description.lower().find(keyword.lower())
                    if first_pos >= 0:
                        # Higher bonus for keywords appearing in first 20% of text
                        position_bonus = 1.0 if first_pos < len(job_description) * 0.2 else 0.0
                    
                    # Combined score
                    requirement_scores[(category, keyword)] += base_score + title_bonus + position_bonus
        
        # Convert scored requirements into the required format
        for (category, keyword), score in requirement_scores.items():
            if score > 1.0:  # Only include requirements with significant scores
                requirements[category].append(keyword)
        
        return requirements
    
    def analyze_skills_gap(self, job_data):
        """
        Analyze the gap between job requirements and candidate skills.
        
        Args:
            job_data (dict): Job data dictionary
            
        Returns:
            dict: Analysis of skills match, gaps, and recommendations
        """
        job_requirements = self.extract_job_requirements(job_data)
        
        analysis = {
            "match_areas": [],
            "gap_areas": [],
            "transferable_skills": [],
            "recommended_content": [],
            "critical_requirements": [],  # New field for critical requirements
            "key_strengths": []  # New field for key strengths to highlight
        }
        
        # Identify critical requirements based on frequency and placement
        for category, requirements in job_requirements.items():
            if len(requirements) >= 3:  # Many keywords in one category suggests importance
                analysis["critical_requirements"].append({
                    "category": category,
                    "keywords": requirements[:3]  # List top 3 keywords
                })
        
        # Analyze matches and gaps with improved detail
        for category, requirements in job_requirements.items():
            if not requirements:
                continue
                
            # Check if we have skills in this category
            matching_skills = []
            if category in self.cv_skills:
                cv_skills_in_category = self.cv_skills.get(category, [])
                
                # Check how many skills in this category match the job requirements
                for skill in cv_skills_in_category:
                    for req in requirements:
                        # Check if skill contains the requirement keyword
                        if req.lower() in skill.lower():
                            matching_skills.append(skill)
                            break
                
                # If we have matching skills, this is a strength
                if matching_skills:
                    match_strength = len(matching_skills) / len(cv_skills_in_category)  # Proportion of our skills that match
                    
                    analysis["match_areas"].append({
                        "category": category,
                        "requirement": ", ".join(requirements),
                        "matching_skills": matching_skills,
                        "match_strength": min(match_strength * 100, 100)  # As percentage
                    })
                    
                    # Identify key strengths (high match strength areas)
                    if match_strength > 0.5:  # Over 50% of our skills in this category match
                        analysis["key_strengths"].append({
                            "category": category,
                            "skills": matching_skills
                        })
                else:
                    # We have skills in the category but none directly match requirements
                    analysis["gap_areas"].append({
                        "category": category,
                        "requirement": ", ".join(requirements),
                        "available_skills": cv_skills_in_category,
                        "gap_type": "partial"  # We have skills in category but not matching requirements
                    })
            else:
                # No direct match, suggest transferable skills
                analysis["gap_areas"].append({
                    "category": category,
                    "requirement": ", ".join(requirements),
                    "gap_type": "complete"  # No skills in this category
                })
                
                # Add transferable skills suggestions
                if category in self.skill_categories:
                    transferable = self.skill_categories[category]["transferable_skills"]
                    analysis["transferable_skills"].extend(transferable)
        
        # Generate recommended content for the cover letter
        self._generate_content_recommendations(analysis)
        
        return analysis
    
    def _generate_content_recommendations(self, analysis):
        """
        Generate content recommendations based on the skills analysis.
        
        Args:
            analysis (dict): The skills gap analysis
        """
        # Recommendations for strength areas
        if analysis["match_areas"]:
            for match in analysis["match_areas"][:2]:  # Focus on top 2 match areas
                category = match["category"].capitalize()
                analysis["recommended_content"].append(
                    f"Emphasize your strong {category} background, specifically mentioning your "
                    f"experience with {match['requirement']}"
                )
        
        # Recommendations for addressing gaps
        if analysis["gap_areas"]:
            for gap in analysis["gap_areas"][:2]:  # Focus on top 2 gap areas
                category = gap["category"].capitalize()
                analysis["recommended_content"].append(
                    f"Address the {category} requirements by highlighting transferable skills and relevant experiences"
                )
        
        # Specific transferable skills recommendations
        if analysis["transferable_skills"]:
            skills_str = "; ".join(analysis["transferable_skills"][:3])  # Top 3 transferable skills
            analysis["recommended_content"].append(
                f"Include these transferable skills to address potential gaps: {skills_str}"
            )
    
    def get_gap_paragraph(self, job_data, max_length=250):
        """
        Generate a paragraph addressing skills gaps for the cover letter.
        
        Args:
            job_data (dict): Job data dictionary
            max_length (int): Maximum length of the paragraph
            
        Returns:
            str: Paragraph for the cover letter
        """
        analysis = self.analyze_skills_gap(job_data)
        
        if not analysis["gap_areas"]:
            return "My skills and experience align well with the requirements of this position, allowing me to make an immediate contribution while continuing to develop my capabilities in this role."
        
        # Focus on top gap area
        main_gap = analysis["gap_areas"][0]["category"].capitalize() if analysis["gap_areas"] else "technical"
        
        # Get transferable skills for this gap
        transferable = analysis["transferable_skills"][:2]
        transferable_text = ""
        if transferable:
            transferable_text = f"I would leverage my {transferable[0].lower()} and {transferable[1].lower() if len(transferable) > 1 else 'adaptability'} to quickly close any gaps."
        
        paragraph = (
            f"While my background may not include extensive experience in all aspects of {main_gap.lower()}, "
            f"I am confident in my ability to quickly adapt and learn. {transferable_text} "
            f"I am committed to continuous professional development and would approach this opportunity "
            f"with enthusiasm and dedication to excellence."
        )
        
        # Ensure paragraph doesn't exceed max length
        if len(paragraph) > max_length:
            paragraph = paragraph[:max_length-3] + "..."
            
        return paragraph
    
    def get_strength_paragraph(self, job_data, max_length=250):
        """
        Generate a paragraph highlighting skill strengths for the cover letter.
        
        Args:
            job_data (dict): Job data dictionary
            max_length (int): Maximum length of the paragraph
            
        Returns:
            str: Paragraph for the cover letter
        """
        analysis = self.analyze_skills_gap(job_data)
        
        if not analysis["match_areas"]:
            return "My professional background has equipped me with a diverse skill set that I believe would be valuable in this position. I am particularly skilled at adapting to new environments and quickly learning new technologies and processes."
        
        # Identify the job title if available
        job_title = ""
        if 'search_details' in job_data and 'JobTitle' in job_data['search_details']:
            job_title = job_data['search_details']['JobTitle']
        elif 'api_details' in job_data and 'title' in job_data['api_details']:
            job_title = job_data['api_details']['title']
        
        # Focus on top match area
        main_match = analysis["match_areas"][0]
        category = main_match["category"].capitalize()
        requirement = main_match["requirement"]
        
        # Get specific skills that match
        specific_skills = ", ".join(main_match["matching_skills"][:2])
        
        # Check if we have a second match area to mention
        additional_category = ""
        if len(analysis["match_areas"]) > 1:
            additional_category = analysis["match_areas"][1]["category"].capitalize()
        
        # Create a more tailored strength paragraph
        if job_title:
            paragraph = (
                f"My expertise in {category.lower()} is directly relevant to the {job_title} role. "
                f"Specifically, my experience with {specific_skills} has prepared me to excel with {requirement}. "
            )
        else:
            paragraph = (
                f"My extensive experience in {category.lower()} makes me well-suited for this position. "
                f"Specifically, my work with {specific_skills} has prepared me to excel in this role. "
            )
            
        # Add mention of additional strength area if available
        if additional_category:
            paragraph += f"Additionally, my background in {additional_category.lower()} provides complementary skills that would benefit your team. "
        
        # Add conclusion
        paragraph += (
            f"I have consistently demonstrated the ability to deliver results in challenging environments "
            f"and would bring this same commitment to excellence to your team."
        )
        
        # Ensure paragraph doesn't exceed max length
        if len(paragraph) > max_length:
            paragraph = paragraph[:max_length-3] + "..."
            
        return paragraph

# Testing functionality when run directly
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    analyzer = SkillsGapAnalyzer()
    
    # Mock job data for testing
    mock_job = {
        "search_details": {
            "JobDescription": "We are looking for a skilled professional with experience in data analysis, SQL, and project management. The ideal candidate should have strong communication skills and experience in regulatory compliance within the financial industry."
        }
    }
    
    analysis = analyzer.analyze_skills_gap(mock_job)
    print("Skills Gap Analysis:")
    print(json.dumps(analysis, indent=2))
    
    print("\nRecommended Gap Paragraph:")
    print(analyzer.get_gap_paragraph(mock_job))
    
    print("\nRecommended Strength Paragraph:")
    print(analyzer.get_strength_paragraph(mock_job))
