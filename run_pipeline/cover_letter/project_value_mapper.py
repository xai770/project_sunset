#!/usr/bin/env python3
"""
Project Value Mapper for Cover Letter Generation

This module maps candidate projects and experiences to job requirements and challenges,
highlighting relevant achievements for personalized cover letters.
"""

import os
import json
import logging
import re
from pathlib import Path
from collections import defaultdict

# Configure logging
logger = logging.getLogger(__name__)

class ProjectValueMapper:
    """
    Maps candidate projects and experiences to job requirements and challenges,
    highlighting relevant achievements for cover letter content.
    """
    
    def __init__(self, projects_path=None):
        """
        Initialize the ProjectValueMapper with candidate project data.
        
        Args:
            projects_path (str, optional): Path to the projects JSON file
        """
        self.projects = []
        self.value_categories = {
            "efficiency": ["reduce", "optimize", "streamline", "automate", "improve", "increase", "enhance"],
            "compliance": ["comply", "regulation", "audit", "legal", "standard", "requirement"],
            "innovation": ["new", "innovative", "create", "develop", "design", "novel", "unique"],
            "cost": ["cost", "save", "budget", "expense", "reduce", "roi", "investment"],
            "quality": ["quality", "improve", "enhance", "excellence", "standard", "best practice"]
        }
        
        # Load project data if provided
        if projects_path:
            self.load_projects(projects_path)
        else:
            # Try to find projects in default locations
            self._find_and_load_projects()
    
    def _find_and_load_projects(self):
        """Attempt to find and load project data from common locations."""
        possible_paths = [
            os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "project_impact_data.json"),
            os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data", "project_impact_data.json"),
            os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "profile", "projects", "project_data.json")
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                logger.info(f"Found project data at: {path}")
                self.load_projects(path)
                return
        
        # If no project data found, create default example projects
        logger.warning("Could not find project data. Using default example projects.")
        self._create_default_projects()
    
    def _create_default_projects(self):
        """Create default example projects when no project data is found."""
        self.projects = [
            {
                "title": "Enterprise License Management System",
                "description": "Developed and implemented an enterprise-wide license management system that automated compliance tracking and reporting",
                "achievements": [
                    "Reduced manual audit preparation time by 75%",
                    "Increased compliance rate from 82% to 99.5%",
                    "Saved €2.4M in potential audit penalties"
                ],
                "skills": ["compliance", "automation", "software development", "data analysis"],
                "domain": "financial services"
            },
            {
                "title": "Vendor Management Optimization",
                "description": "Redesigned vendor management processes to improve efficiency and reduce costs while maintaining compliance",
                "achievements": [
                    "Consolidated vendor contracts saving €1.2M annually",
                    "Reduced contract processing time by 40%",
                    "Implemented standardized compliance checks across all vendors"
                ],
                "skills": ["negotiation", "contract management", "process optimization", "vendor relations"],
                "domain": "procurement"
            },
            {
                "title": "Regulatory Compliance Dashboard",
                "description": "Created a real-time dashboard for monitoring regulatory compliance across multiple jurisdictions",
                "achievements": [
                    "Provided early warning system for compliance issues",
                    "Reduced compliance-related incidents by 65%",
                    "Adopted by 4 business units as standard practice"
                ],
                "skills": ["data visualization", "regulatory knowledge", "risk assessment", "reporting"],
                "domain": "regulatory compliance"
            }
        ]
    
    def load_projects(self, file_path):
        """
        Load project data from a JSON file.
        
        Args:
            file_path (str): Path to the projects JSON file
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)  # type: ignore
                
                # Handle different formats of project data
                if isinstance(data, list):
                    self.projects = data
                elif isinstance(data, dict) and "projects" in data:
                    self.projects = data["projects"]
                else:
                    self.projects = [data]  # Single project as dict
                    
            logger.info(f"Successfully loaded {len(self.projects)} projects from {file_path}")
        except Exception as e:
            logger.error(f"Error loading project data: {e}")
            self._create_default_projects()
    
    def extract_job_values(self, job_data):
        """
        Extract key value drivers from job description.
        
        Args:
            job_data (dict): Job data dictionary
            
        Returns:
            dict: Dictionary of job values by category
        """
        job_values = defaultdict(list)
        job_description = ""
        
        # Try different fields where description might be found
        if 'search_details' in job_data and 'JobDescription' in job_data['search_details']:
            job_description = job_data['search_details']['JobDescription']
        elif 'api_details' in job_data and 'description' in job_data['api_details']:
            job_description = job_data['api_details']['description']
        elif 'job_description' in job_data:
            job_description = job_data['job_description']
        
        if not job_description:
            logger.warning("No job description found in job data")
            return job_values
        
        # Extract value drivers using keywords
        for category, keywords in self.value_categories.items():
            for keyword in keywords:
                pattern = r'(?i)\b{}\w*\b'.format(keyword)
                matches = re.findall(pattern, job_description)
                if matches:
                    for match in matches:
                        value = match.lower()
                        if value not in job_values[category]:
                            job_values[category].append(value)
        
        return job_values
    
    def map_projects_to_job(self, job_data):
        """
        Map projects to job requirements and values.
        
        Args:
            job_data (dict): Job data dictionary
            
        Returns:
            dict: Mapping of projects to job requirements with relevance scores
        """
        job_values = self.extract_job_values(job_data)
        
        mapping = {
            "top_projects": [],
            "value_alignments": [],
            "achievement_highlights": [],
            "quantifiable_achievements": []  # New field for achievements with metrics
        }
        
        # Skip if no projects or job values
        if not self.projects or not job_values:
            return mapping
        
        # Score each project for relevance to the job
        project_scores = []
        for project in self.projects:
            score = 0
            project_text = project.get("title", "") + " " + project.get("description", "")
            
            # Check for value category matches
            value_matches = []
            for category, values in job_values.items():
                for value in values:
                    if value.lower() in project_text.lower():
                        score += 2
                        if category not in value_matches:
                            value_matches.append(category)
            
            # Check for achievements that align with job values
            achievement_matches = []
            quantifiable_achievements = []
            for achievement in project.get("achievements", []):
                # Check if achievement contains quantifiable results (numbers, percentages)
                is_quantifiable = any(char.isdigit() for char in achievement)
                has_percentage = '%' in achievement
                has_currency = any(currency in achievement for currency in ['$', '€', '£', 'USD', 'EUR'])
                
                # Enhanced scoring for quantifiable achievements
                achievement_score = 3  # Base score
                if is_quantifiable:
                    achievement_score += 2  # Bonus for containing numbers
                if has_percentage:
                    achievement_score += 1  # Bonus for percentage metrics
                if has_currency:
                    achievement_score += 1  # Bonus for monetary impact
                
                matches_value = False
                matched_category = None
                
                # Check if achievement aligns with job values
                for category, values in job_values.items():
                    for value in values:
                        if value.lower() in achievement.lower():
                            score += achievement_score  # Add weighted score
                            matches_value = True
                            matched_category = category
                            break
                    if matches_value:
                        break
                
                if matches_value:
                    achievement_matches.append((achievement, matched_category))
                
                # Track quantifiable achievements separately
                if is_quantifiable:
                    impact_level = 0
                    if has_percentage or has_currency:
                        impact_level += 1
                    if matches_value:
                        impact_level += 2
                        
                    quantifiable_achievements.append({
                        "text": achievement,
                        "impact_level": impact_level,
                        "matches_job_values": matches_value,
                        "category": matched_category if matches_value else None
                    })
            
            # Check domain relevance
            if "domain" in project and job_data.get("search_details", {}).get("SubCategory", "").lower() in project["domain"].lower():
                score += 5
            
            project_scores.append({
                "project": project,
                "score": score,
                "value_matches": value_matches,
                "achievement_matches": achievement_matches,
                "quantifiable_achievements": quantifiable_achievements
            })
        
        # Sort projects by relevance score
        project_scores.sort(key=lambda x: x["score"], reverse=True)
        
        # Get top 2 most relevant projects
        for project_data in project_scores[:2]:
            project = project_data["project"]
            mapping["top_projects"].append({
                "title": project.get("title", ""),
                "description": project.get("description", ""),
                "relevance_score": project_data["score"]
            })
        
        # Record value alignments
        for category in job_values:
            relevant_projects = [p for p in project_scores if category in p["value_matches"]]
            if relevant_projects:
                top_project = relevant_projects[0]["project"]
                mapping["value_alignments"].append({
                    "value_category": category,
                    "project_title": top_project.get("title", ""),
                    "alignment_description": f"Your {category} focus aligns with my experience in {top_project.get('title', '')}"
                })
        
        # Collect achievement highlights
        all_achievement_matches = []
        for project_data in project_scores:
            all_achievement_matches.extend([
                {
                    "achievement": am[0],
                    "category": am[1],
                    "project_title": project_data["project"].get("title", "")
                }
                for am in project_data["achievement_matches"]
            ])
        
        # Get top 3 achievements
        mapping["achievement_highlights"] = all_achievement_matches[:3]
        
        # Collect all quantifiable achievements and sort by impact level
        all_quantifiable = []
        for project_data in project_scores:
            project_title = project_data["project"].get("title", "")
            all_quantifiable.extend([
                {
                    **qa,
                    "project_title": project_title
                }
                for qa in project_data["quantifiable_achievements"]
            ])
        
        # Sort by impact level and relevance to job
        all_quantifiable.sort(key=lambda x: (x["impact_level"], x["matches_job_values"]), reverse=True)
        mapping["quantifiable_achievements"] = all_quantifiable[:5]  # Top 5 quantifiable achievements
        
        return mapping
    
    def get_project_paragraph(self, job_data, max_length=350):
        """
        Generate a paragraph highlighting relevant project experience for the cover letter.
        
        Args:
            job_data (dict): Job data dictionary
            max_length (int): Maximum length of the paragraph
            
        Returns:
            str: Paragraph for the cover letter
        """
        mapping = self.map_projects_to_job(job_data)
        
        if not mapping["top_projects"]:
            return "Throughout my career, I have led multiple successful projects that demonstrate my ability to deliver results. I approach challenges methodically, consistently achieving targets while maintaining high quality standards."
        
        # Focus on top project
        top_project = mapping["top_projects"][0]
        
        # Include achievements if available
        achievement_text = ""
        if mapping["achievement_highlights"]:
            achievements = [h["achievement"] for h in mapping["achievement_highlights"][:2]]
            achievement_text = f" Some key achievements include {achievements[0].lower()}"
            if len(achievements) > 1:
                achievement_text += f" and {achievements[1].lower()}"
            achievement_text += "."
        
        paragraph = (
            f"My experience leading the {top_project['title']} project is particularly relevant to this position. "
            f"{top_project['description']}. {achievement_text} "
            f"I would bring this same focused approach to delivering value in this role, applying lessons learned "
            f"and proven methodologies to address your organization's challenges."
        )
        
        # Ensure paragraph doesn't exceed max length
        if len(paragraph) > max_length:
            paragraph = paragraph[:max_length-3] + "..."
            
        return paragraph
    
    def get_value_proposition_paragraph(self, job_data, max_length=250):
        """
        Generate a paragraph highlighting value proposition aligned with job needs.
        
        Args:
            job_data (dict): Job data dictionary
            max_length (int): Maximum length of the paragraph
            
        Returns:
            str: Value proposition paragraph for the cover letter
        """
        mapping = self.map_projects_to_job(job_data)
        job_values = self.extract_job_values(job_data)
        
        # Default paragraph if no clear alignments found
        if not job_values:
            return "I am committed to delivering exceptional results through a combination of technical expertise, process optimization, and collaborative leadership. My approach focuses on creating measurable business value while ensuring regulatory compliance and operational excellence."
        
        # Get top 2 value categories
        top_values = list(job_values.keys())[:2]
        value_text = " and ".join([v.capitalize() for v in top_values])
        
        # Reference a relevant achievement if available
        achievement_reference = ""
        if mapping["achievement_highlights"]:
            highlight = mapping["achievement_highlights"][0]
            achievement_reference = f" As demonstrated in my previous work where I {highlight['achievement'].lower()}, I consistently deliver tangible results."
        
        paragraph = (
            f"{value_text} are clearly important to this role, and these are areas where I excel. "
            f"My approach combines practical implementation with strategic thinking to address complex challenges."
            f"{achievement_reference} "
            f"I'm confident I can bring this same value-driven mindset to your team."
        )
        
        # Ensure paragraph doesn't exceed max length
        if len(paragraph) > max_length:
            paragraph = paragraph[:max_length-3] + "..."
            
        return paragraph
    
    def get_quantifiable_achievements_section(self, job_data, max_items=3):
        """
        Generate a section highlighting quantifiable achievements relevant to the job.
        
        Args:
            job_data (dict): Job data dictionary
            max_items (int): Maximum number of achievements to include
            
        Returns:
            str: Formatted section with quantifiable achievements
        """
        mapping = self.map_projects_to_job(job_data)
        
        # Return empty string if no quantifiable achievements
        if not mapping["quantifiable_achievements"]:
            return ""
        
        # Build the section
        section = "\n## Key Quantifiable Achievements\n\n"
        
        # Get top achievements that match job values
        achievements = [a for a in mapping["quantifiable_achievements"] if a["matches_job_values"]]
        # If not enough, add other quantifiable achievements
        if len(achievements) < max_items:
            non_matching = [a for a in mapping["quantifiable_achievements"] if not a["matches_job_values"]]
            achievements.extend(non_matching[:max_items - len(achievements)])
        
        # Format each achievement
        for i, achievement in enumerate(achievements[:max_items]):
            project = achievement["project_title"]
            text = achievement["text"]
            section += f"{i+1}. **{project}**: {text}\n"
        
        return section

# Testing functionality when run directly
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    mapper = ProjectValueMapper()
    
    # Mock job data for testing
    mock_job = {
        "search_details": {
            "JobDescription": "We are looking for a candidate who can improve efficiency and reduce costs in our compliance processes. The ideal candidate will optimize our workflows while ensuring we meet all regulatory requirements.",
            "SubCategory": "financial"
        }
    }
    
    mapping = mapper.map_projects_to_job(mock_job)
    print("Project-Job Mapping:")
    print(json.dumps(mapping, indent=2))
    
    print("\nRecommended Project Paragraph:")
    print(mapper.get_project_paragraph(mock_job))
    
    print("\nRecommended Value Proposition:")
    print(mapper.get_value_proposition_paragraph(mock_job))
    
    print("\nQuantifiable Achievements Section:")
    print(mapper.get_quantifiable_achievements_section(mock_job))
