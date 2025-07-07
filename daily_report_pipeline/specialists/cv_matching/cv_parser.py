"""
CV Parser
=========

Parses markdown CV files into structured CV objects.
"""

import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from .data_models import CV, Education, Experience, Language, LanguageProficiency

class CVParser:
    """Parses markdown CV files into structured CV objects"""
    
    def __init__(self) -> None:
        """Initialize the CV parser"""
        self.current_section = ""
        self.sections: Dict[str, List[str]] = {}
        self.section_markers = {
            "summary": ["## Summary", "## Professional Summary", "## Profile"],
            "experience": ["## Experience", "## Professional Experience", "## Work Experience"],
            "education": ["## Education", "## Academic Background", "## Educational Background"],
            "skills": ["## Skills", "## Technical Skills", "## Core Competencies"],
            "languages": ["## Languages", "## Language Skills"],
            "personal": ["## Personal Information", "## Personal Details"]
        }
    
    def parse_markdown_cv(self, file_path: str | Path) -> CV:
        """Parse a markdown CV file into a structured CV object."""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        sections = self._split_into_sections(content)
        
        contact_info = self._extract_contact_info(sections.get("header", ""))
        languages = self._parse_languages(sections.get("languages", ""))
        experiences = self._parse_experience(sections.get("experience", ""))
        education = self._parse_education(sections.get("education", ""))
        skills = self._parse_skills(sections.get("skills", ""))
        personal_info = self._parse_personal_info(sections.get("personal", ""))

        return CV(
            name=self._extract_name(sections.get("header", "")),
            contact=contact_info,
            summary=self._clean_section(sections.get("summary", "")),
            core_competencies=self._parse_core_competencies(sections.get("skills", "")),
            experience=experiences,
            education=education,
            languages=languages,
            skills=skills,
            personal_info=personal_info
        )

    def _split_into_sections(self, content: str) -> Dict[str, str]:
        """Split the CV content into different sections."""
        lines = content.split('\n')
        sections: Dict[str, List[str]] = {"header": []}
        current_section = "header"

        for line in lines:
            if line.startswith('# '):  # Main header
                sections["header"].append(line)
                continue

            section_found = False
            for section_type, headers in self.section_markers.items():
                if any(line.startswith(header) for header in headers):
                    current_section = section_type
                    sections[current_section] = []
                    section_found = True
                    break
            
            if not section_found:
                if current_section in sections:
                    sections[current_section].append(line)
                else:
                    sections[current_section] = [line]

        return {k: '\n'.join(v).strip() for k, v in sections.items()}

    def _extract_name(self, header: str) -> str:
        """Extract the name from the CV header."""
        if not header:
            return ""
        match = re.search(r'^# (.+)$', header, re.MULTILINE)
        return match.group(1).strip() if match else ""

    def _extract_contact_info(self, header: str) -> Dict[str, str]:
        """Extract contact information from the CV header."""
        contact_info: Dict[str, str] = {}
        
        # Common patterns for contact information
        patterns = {
            'email': r'[\w\.-]+@[\w\.-]+\.\w+',
            'phone': r'[\+\d][\d\s\-\(\)\.]+\d',
            'address': r'^[^#\n]+(?=\n|$)',  # First non-header line
            'linkedin': r'linkedin\.com/\S+'
        }

        for key, pattern in patterns.items():
            match = re.search(pattern, header, re.MULTILINE)
            if match:
                contact_info[key] = match.group(0).strip()

        return contact_info

    def _parse_languages(self, section: str) -> List[Language]:
        """Parse language proficiencies from the language section."""
        languages: List[Language] = []
        if not section:
            return languages

        for line in section.split('\n'):
            if not line.strip() or line.startswith('#'):
                continue

            # Handle different format patterns
            patterns = [
                r'(\w+):\s*(native|fluent|advanced|intermediate|basic)',
                r'(\w+)\s*-\s*(native|fluent|advanced|intermediate|basic)',
                r'(First language|Native):\s*(\w+)',
                r'Fluent in .* (written and spoken|spoken and written) (\w+)'
            ]

            for pattern in patterns:
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    if "First language" in line or "Native" in line:
                        lang_name = match.group(2)
                        proficiency = LanguageProficiency.NATIVE
                    elif "Fluent" in line:
                        lang_name = match.group(2)
                        proficiency = LanguageProficiency.FLUENT
                    else:
                        lang_name = match.group(1)
                        proficiency = LanguageProficiency[match.group(2).upper()]
                    
                    languages.append(Language(
                        name=lang_name,
                        proficiency=proficiency,
                        spoken=True,
                        written=True
                    ))
                    break

        return languages

    def _parse_experience(self, section: str) -> List[Experience]:
        """Parse work experience entries."""
        experiences: List[Experience] = []
        if not section:
            return experiences

        # Split into individual entries
        entries = re.split(r'\n(?=\*\*|###)', section)
        
        for entry in entries:
            if not entry.strip():
                continue

            # Try to extract company and title
            company_match = re.search(r'\*\*(.*?)\*\*', entry)
            if not company_match:
                continue

            company = company_match.group(1).strip()
            
            # Extract dates
            date_match = re.search(r'(\d{2}/\d{4})\s*-\s*(\d{2}/\d{4}|Present)', entry)
            if date_match:
                start_date = datetime.strptime(date_match.group(1), '%m/%Y').date()
                end_date = None if date_match.group(2) == 'Present' else datetime.strptime(date_match.group(2), '%m/%Y').date()
            else:
                continue

            # Extract description and skills
            description_lines = []
            skills = []
            for line in entry.split('\n'):
                line = line.strip()
                if line.startswith('•'):
                    description_lines.append(line[1:].strip())
                    # Extract skills from description (keywords after "using", "with", etc.)
                    skill_match = re.search(r'using|with|including|through|via)\s+([\w\s,]+)', line, re.IGNORECASE)
                    if skill_match:
                        skills.extend([s.strip() for s in skill_match.group(1).split(',')])

            experiences.append(Experience(
                company=company,
                title="",  # Would need more specific parsing based on actual CV format
                start_date=start_date,
                end_date=end_date,
                description=description_lines,
                skills=list(set(skills)),  # Deduplicate skills
                industry="",  # Would need more specific parsing or external data
                is_current=end_date is None
            ))

        return experiences

    def _parse_education(self, section: str) -> List[Education]:
        """Parse education entries."""
        education_list: List[Education] = []
        if not section:
            return education_list

        # Split into individual entries
        entries = re.split(r'\n(?=\*\*|###)', section)
        
        for entry in entries:
            if not entry.strip():
                continue

            # Try to extract institution and degree
            institution_match = re.search(r'\*\*(.*?)\*\*', entry)
            if not institution_match:
                continue

            institution = institution_match.group(1).strip()
            
            # Extract degree and field
            degree_match = re.search(r'(Bachelor|Master|PhD|Diploma|Certificate) (?:of|in) (.*?)(?:\n|$)', entry, re.IGNORECASE)
            if degree_match:
                degree = degree_match.group(1)
                field = degree_match.group(2).strip()
            else:
                degree = ""
                field = ""

            # Extract dates
            date_match = re.search(r'(\d{4})\s*-\s*(\d{4}|Present)', entry)
            if date_match:
                start_date = datetime.strptime(f"01/01/{date_match.group(1)}", '%d/%m/%Y').date()
                end_str = date_match.group(2)
                end_date = None if end_str == 'Present' else datetime.strptime(f"31/12/{end_str}", '%d/%m/%Y').date()
            else:
                continue

            education_list.append(Education(
                institution=institution,
                degree=degree,
                field=field,
                start_date=start_date,
                end_date=end_date
            ))

        return education_list

    def _parse_skills(self, section: str) -> List[str]:
        """Extract skills from the skills/competencies section."""
        skills: List[str] = []
        if not section:
            return skills

        for line in section.split('\n'):
            if line.startswith('•'):
                # Extract individual skills from bullet points
                skill_text = line[1:].strip()
                # Split compound skills if they contain commas or "and"
                sub_skills = re.split(r',|\sand\s', skill_text)
                skills.extend([s.strip() for s in sub_skills if s.strip()])

        return list(set(skills))  # Deduplicate skills

    def _parse_core_competencies(self, section: str) -> Dict[str, List[str]]:
        """Parse core competencies into categories."""
        competencies: Dict[str, List[str]] = {}
        current_category = "General"
        
        if not section:
            return competencies

        for line in section.split('\n'):
            line = line.strip()
            if not line:
                continue
                
            if line.startswith('**'):
                # New category
                current_category = line.strip('*').strip()
                competencies[current_category] = []
            elif line.startswith('•'):
                # Competency item
                if current_category not in competencies:
                    competencies[current_category] = []
                competencies[current_category].append(line[1:].strip())

        return competencies

    def _parse_personal_info(self, section: str) -> Dict[str, str]:
        """Parse personal information section."""
        info: Dict[str, str] = {}
        if not section:
            return info

        for line in section.split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                info[key.strip('* ')] = value.strip()

        return info

    def _clean_section(self, text: str) -> str:
        """Clean up a section of text."""
        if not text:
            return ""
        # Remove section headers and clean up whitespace
        lines = [line for line in text.split('\n') if not line.startswith('#')]
        return '\n'.join(line.strip() for line in lines if line.strip())
