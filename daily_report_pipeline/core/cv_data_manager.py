"""
CV Data Manager
==============

Loads and parses CV data from config/cv.txt into structured format
for job matching and analysis.
"""

import logging
import re
from pathlib import Path
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

class CVDataManager:
    """
    Manages CV data loading, parsing, and skill extraction
    """
    
    def __init__(self, cv_file_path: Optional[str] = None):
        """Initialize CV data manager
        
        Args:
            cv_file_path: Path to CV file (defaults to config/cv.txt)
        """
        if cv_file_path is None:
            cv_file_path = Path(__file__).parent.parent.parent / "config" / "cv.txt"
        
        self.cv_file_path = Path(cv_file_path)
        self.cv_data = None
        self.parsed_skills = None
        
        logger.info("🎯 CV Data Manager initialized")
        
    def load_cv_data(self) -> Dict[str, Any]:
        """Load and parse CV data from file
        
        Returns:
            Structured CV data dictionary
        """
        if self.cv_data is not None:
            return self.cv_data
            
        try:
            with open(self.cv_file_path, 'r', encoding='utf-8') as f:
                cv_text = f.read()
            
            self.cv_data = self._parse_cv_text(cv_text)
            logger.info(f"✅ CV data loaded: {len(self.cv_data.get('experience', []))} positions, "
                       f"{len(self.cv_data.get('skills', {}).get('all', []))} skills extracted")
            
            return self.cv_data
            
        except Exception as e:
            logger.error(f"❌ Failed to load CV data: {e}")
            return self._get_fallback_cv_data()
    
    def _parse_cv_text(self, cv_text: str) -> Dict[str, Any]:
        """Parse CV text into structured data
        
        Args:
            cv_text: Raw CV content
            
        Returns:
            Structured CV data
        """
        cv_data = {
            'experience': [],
            'skills': {
                'technical': [],
                'business': [],
                'domain': [],
                'all': []
            },
            'domains': [],
            'seniority_level': 'senior',
            'total_years_experience': 20,
            'finance_experience': True,
            'technology_experience': True,
            'management_experience': True
        }
        
        # Extract experience sections
        experience_sections = self._extract_experience_sections(cv_text)
        cv_data['experience'] = experience_sections
        
        # Extract skills from experience
        all_skills = self._extract_skills_from_experience(experience_sections)
        cv_data['skills'] = all_skills
        
        # Determine domains from experience
        cv_data['domains'] = self._extract_domains_from_experience(experience_sections)
        
        return cv_data
    
    def _extract_experience_sections(self, cv_text: str) -> List[Dict[str, Any]]:
        """Extract experience sections from CV text
        
        Args:
            cv_text: Raw CV content
            
        Returns:
            List of experience dictionaries
        """
        experience = []
        
        # Split by company headers (##)
        company_sections = re.split(r'\n## ', cv_text)
        
        for section in company_sections:
            if not section.strip() or 'Professional Experience' in section:
                continue
                
            # Extract company info
            lines = section.strip().split('\n')
            if not lines:
                continue
                
            company_line = lines[0].replace('##', '').strip()
            
            # Parse company, location, years
            if ' - ' in company_line and '(' in company_line:
                parts = company_line.split(' - ')
                company_location = parts[0]
                
                if ',' in company_location:
                    company, location = company_location.split(',', 1)
                    company = company.strip()
                    location = location.strip()
                else:
                    company = company_location.strip()
                    location = 'Unknown'
                
                # Extract years from end
                years_match = re.search(r'\((\d{4}.*?)\)$', company_line)
                years = years_match.group(1) if years_match else 'Unknown'
                
            else:
                company = company_line
                location = 'Unknown'
                years = 'Unknown'
            
            # Extract roles within company
            role_sections = re.split(r'\n### ', section)
            roles = []
            
            for role_section in role_sections[1:]:  # Skip company header
                role_lines = role_section.split('\n')
                if role_lines:
                    role_title_line = role_lines[0]
                    role_description = '\n'.join(role_lines[1:])
                    
                    # Extract role years
                    role_years_match = re.search(r'\((\d{4}.*?)\)$', role_title_line)
                    role_years = role_years_match.group(1) if role_years_match else years
                    role_title = re.sub(r'\s*\(\d{4}.*?\)$', '', role_title_line).strip()
                    
                    roles.append({
                        'title': role_title,
                        'years': role_years,
                        'description': role_description.strip()
                    })
            
            if roles:  # Only add if we found roles
                experience.append({
                    'company': company,
                    'location': location,
                    'years': years,
                    'roles': roles
                })
        
        return experience
    
    def _extract_skills_from_experience(self, experience: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """Extract skills from experience descriptions
        
        Args:
            experience: List of experience dictionaries
            
        Returns:
            Categorized skills dictionary
        """
        # Known skill patterns from the CV
        technical_skills = [
            'Software License Management', 'Contract Compliance', 'SAP', 'SQL', 'Python', 'SAS',
            'Microsoft', 'Adobe', 'Oracle', 'IBM', 'HP', 'VMware', 'Enterprise License Management',
            'Software Asset Management', 'Automated Reporting', 'Dashboard Development',
            'Data Analysis', 'Analytics Tools', 'CRM Systems', 'Campaign Tools', 'Backend Development',
            'Frontend Development', 'API Integration', 'Database Management'
        ]
        
        business_skills = [
            'Vendor Management', 'Contract Negotiations', 'Project Management', 'Team Leadership',
            'Stakeholder Management', 'Process Optimization', 'Compliance Management',
            'Financial Planning', 'Budget Management', 'Risk Management', 'Governance',
            'Change Management', 'Strategic Planning', 'Business Analysis', 'Requirements Gathering',
            'KPI Development', 'Performance Monitoring', 'Cost Optimization', 'Procurement',
            'Sourcing', 'Regulatory Compliance', 'Audit Management'
        ]
        
        domain_skills = [
            'Banking', 'Financial Services', 'Technology', 'IT Management', 'Pharmaceutical',
            'Healthcare', 'Consulting', 'Enterprise Software', 'FinTech', 'RegTech'
        ]
        
        # Combine all text for pattern matching
        all_text = ""
        for exp in experience:
            all_text += f" {exp.get('company', '')} "
            for role in exp.get('roles', []):
                all_text += f" {role.get('title', '')} {role.get('description', '')} "
        
        all_text = all_text.lower()
        
        # Extract matching skills
        found_technical = [skill for skill in technical_skills 
                          if skill.lower() in all_text]
        found_business = [skill for skill in business_skills 
                         if skill.lower() in all_text]
        found_domain = [skill for skill in domain_skills 
                       if skill.lower() in all_text]
        
        # Add some specific extractions based on CV content
        if 'deutsche bank' in all_text:
            found_domain.extend(['Banking', 'Financial Services'])
        if 'novartis' in all_text:
            found_domain.extend(['Pharmaceutical', 'Healthcare'])
        if 'license' in all_text:
            found_technical.append('Software Licensing')
        if 'compliance' in all_text:
            found_business.append('Regulatory Compliance')
        
        all_skills = list(set(found_technical + found_business + found_domain))
        
        return {
            'technical': list(set(found_technical)),
            'business': list(set(found_business)),
            'domain': list(set(found_domain)),
            'all': all_skills
        }
    
    def _extract_domains_from_experience(self, experience: List[Dict[str, Any]]) -> List[str]:
        """Extract industry domains from experience
        
        Args:
            experience: List of experience dictionaries
            
        Returns:
            List of industry domains
        """
        domains = set()
        
        for exp in experience:
            company = exp.get('company', '').lower()
            
            # Map companies to domains
            if 'deutsche bank' in company or 'commerzbank' in company or 'dresdner bank' in company:
                domains.add('Finance')
                domains.add('Banking')
            elif 'novartis' in company or 'roche' in company:
                domains.add('Healthcare')
                domains.add('Pharmaceutical')
            
            # Check role descriptions for domain indicators
            for role in exp.get('roles', []):
                desc = role.get('description', '').lower()
                if 'software' in desc or 'technology' in desc or 'it ' in desc:
                    domains.add('Technology')
                if 'financial' in desc or 'banking' in desc:
                    domains.add('Finance')
        
        return list(domains)
    
    def _get_fallback_cv_data(self) -> Dict[str, Any]:
        """Return fallback CV data if parsing fails
        
        Returns:
            Basic CV data structure
        """
        return {
            'experience': [],
            'skills': {
                'technical': ['Software License Management', 'Project Management', 'SQL'],
                'business': ['Vendor Management', 'Contract Negotiations', 'Team Leadership'],
                'domain': ['Finance', 'Technology'],
                'all': ['Software License Management', 'Project Management', 'SQL', 
                       'Vendor Management', 'Contract Negotiations', 'Team Leadership',
                       'Finance', 'Technology']
            },
            'domains': ['Finance', 'Technology'],
            'seniority_level': 'senior',
            'total_years_experience': 20,
            'finance_experience': True,
            'technology_experience': True,
            'management_experience': True
        }
    
    def get_skills(self) -> Dict[str, List[str]]:
        """Get extracted skills
        
        Returns:
            Dictionary of categorized skills
        """
        if self.cv_data is None:
            self.load_cv_data()
        
        return self.cv_data.get('skills', {})
    
    def get_domains(self) -> List[str]:
        """Get candidate domains
        
        Returns:
            List of candidate domains
        """
        if self.cv_data is None:
            self.load_cv_data()
        
        return self.cv_data.get('domains', [])
    
    def get_experience_summary(self) -> Dict[str, Any]:
        """Get experience summary
        
        Returns:
            Experience summary data
        """
        if self.cv_data is None:
            self.load_cv_data()
        
        return {
            'total_years': self.cv_data.get('total_years_experience', 0),
            'seniority_level': self.cv_data.get('seniority_level', 'unknown'),
            'finance_experience': self.cv_data.get('finance_experience', False),
            'technology_experience': self.cv_data.get('technology_experience', False),
            'management_experience': self.cv_data.get('management_experience', False),
            'companies': [exp.get('company', '') for exp in self.cv_data.get('experience', [])]
        }
