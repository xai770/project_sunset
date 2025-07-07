#!/usr/bin/env python3
"""
Utility functions for bucketed skill matching
"""

import re
import logging
from typing import Dict, List, Any, Optional, Set
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("bucket_utils")

# Get paths from the main config
try:
    from run_pipeline.config.paths import PROJECT_ROOT, JOB_DATA_DIR
except ImportError:
    # Fallback if imported outside the pipeline
    PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
    JOB_DATA_DIR = PROJECT_ROOT / "data" / "postings"

# Define paths
YOUR_SKILLS_FILE = PROJECT_ROOT / "profile" / "skills" / "skill_decompositions.json"

# Define skill buckets - simplified categories
SKILL_BUCKETS = {
    "Technical": [
        "programming", "software", "development", "engineering", "code", "coding", 
        "database", "cloud", "devops", "system", "infrastructure", "technology",
        "technical", "it", "computer", "machine learning", "ai", "algorithm",
        "architecture", "backend", "frontend", "web", "mobile", "network",
        "security", "cybersecurity", "hardware", "automation", "qa", "testing"
    ],
    "Management": [
        "leadership", "management", "project", "team", "strategic", "planning", 
        "program", "portfolio", "executive", "change", "organizational", "resource",
        "supervisor", "director", "manager", "lead", "coordinator", "administration"
    ],
    "Domain_Knowledge": [
        "finance", "banking", "insurance", "healthcare", "manufacturing", "retail", 
        "telecom", "energy", "legal", "education", "government", "pharmaceutical",
        "biotech", "real estate", "hospitality", "transportation", "logistics",
        "agriculture", "media", "entertainment", "industry", "domain", "sector",
        "field", "specialization", "expertise", "knowledge"
    ],
    "Soft_Skills": [
        "communication", "teamwork", "problem solving", "critical thinking", 
        "adaptability", "time management", "collaboration", "interpersonal",
        "negotiation", "conflict resolution", "emotional intelligence", "leadership",
        "decision making", "creativity", "innovation", "motivation", "flexibility",
        "presentation", "persuasion", "empathy", "ethic", "social", "personal"
    ],
    "Analytics": [
        "data analysis", "business intelligence", "reporting", "statistics",
        "forecasting", "analytics", "visualization", "sql", "quantitative",
        "market research", "competitive analysis", "metrics", "kpi", "insight",
        "trend", "pattern", "predictive", "descriptive", "diagnostic", "dashboard"
    ]
}

def categorize_skill(skill_name: str, skill_description: str = "") -> str:
    """
    Categorize a skill into one of the predefined buckets
    
    Args:
        skill_name: The name of the skill
        skill_description: Optional description of the skill
    
    Returns:
        str: The bucket name (or 'Other' if no match)
    """
    # Combine name and description for better categorization
    text = f"{skill_name} {skill_description}".lower()
    
    # Check each bucket's keywords
    for bucket, keywords in SKILL_BUCKETS.items():
        for keyword in keywords:
            if keyword.lower() in text:
                return bucket
    
    # Default bucket for uncategorized skills
    return "Other"

def extract_cv_skills(cv_skills_data: Dict[str, Any]) -> Dict[str, List[str]]:
    """
    Extract skills from CV data and organize them into buckets
    
    Args:
        cv_skills_data: The CV skills data structure
    
    Returns:
        Dict[str, List[str]]: Skills organized by bucket
    """
    bucketed_skills: Dict[str, List[str]] = {bucket: [] for bucket in SKILL_BUCKETS.keys()}
    bucketed_skills["Other"] = []  # For skills that don't match any bucket
    
    # Process complex skills
    complex_skills = cv_skills_data.get("complex_skills", [])
    for skill in complex_skills:
        name = skill.get("name", "")
        description = skill.get("description", "")
        
        if name:
            bucket = categorize_skill(name, description)
            bucketed_skills[bucket].append(name)
    
    # Process elementary skills if they exist separately
    elementary_skills = cv_skills_data.get("elementary_skills", [])
    for skill in elementary_skills:
        if isinstance(skill, dict):
            name = skill.get("name", "")
            description = skill.get("description", "")
        else:
            name = skill
            description = ""
        
        if name and name not in [s for skills in bucketed_skills.values() for s in skills]:
            bucket = categorize_skill(name, description)
            bucketed_skills[bucket].append(name)
    
    return bucketed_skills

def extract_job_skills(job_data: Dict[str, Any]) -> Dict[str, List[str]]:
    """
    Extract skills from job data and organize them into buckets
    
    Args:
        job_data: The job data structure
    
    Returns:
        Dict[str, List[str]]: Skills organized by bucket
    """
    bucketed_skills: Dict[str, List[str]] = {bucket: [] for bucket in SKILL_BUCKETS.keys()}
    bucketed_skills["Other"] = []  # For skills that don't match any bucket
    all_skills: Set[str] = set()  # Track all skills to avoid duplicates
    skills_found = False
    
    # Process SDR skills if available (highest priority source)
    sdr_skills = job_data.get("sdr_skills", {}).get("enriched", {})
    
    if sdr_skills:
        for skill_name, skill_info in sdr_skills.items():
            if isinstance(skill_info, dict):
                description = skill_info.get("description", "")
            else:
                description = ""
            
            if skill_name.lower() not in all_skills:
                bucket = categorize_skill(skill_name, description)
                bucketed_skills[bucket].append(skill_name)
                all_skills.add(skill_name.lower())
                skills_found = True
    
    # Check for standard skills as a simple list
    standard_skills = job_data.get("skills", [])
    if standard_skills and isinstance(standard_skills, list):
        for skill in standard_skills:
            if isinstance(skill, str) and skill.lower() not in all_skills:
                bucket = categorize_skill(skill)
                bucketed_skills[bucket].append(skill)
                all_skills.add(skill.lower())
                skills_found = True
    
    # Check for skill matches that might contain skill information
    skill_matches = job_data.get("skill_matches", {}).get("matches", [])
    if skill_matches:
        for match_entry in skill_matches:
            if isinstance(match_entry, dict):
                skill = match_entry.get("job_skill", "")
                if skill and skill.lower() not in all_skills:
                    bucket = categorize_skill(skill)
                    bucketed_skills[bucket].append(skill)
                    all_skills.add(skill.lower())
                    skills_found = True
    
    # Check for structured description requirements
    structured_requirements = job_data.get("web_details", {}).get("structured_description", {}).get("requirements", [])
    if structured_requirements and isinstance(structured_requirements, list):
        for requirement in structured_requirements:
            if isinstance(requirement, str):
                # Extract potential skills from each requirement
                skill_parts = re.split(r',|;|and', requirement)
                for part in skill_parts:
                    skill = part.strip()
                    if len(skill) > 3 and skill.lower() not in all_skills:
                        bucket = categorize_skill(skill)
                        bucketed_skills[bucket].append(skill)
                        all_skills.add(skill.lower())
                        skills_found = True
    
    # Also check responsibilities for skillset requirements
    structured_responsibilities = job_data.get("web_details", {}).get("structured_description", {}).get("responsibilities", [])
    if structured_responsibilities and isinstance(structured_responsibilities, list):
        for responsibility in structured_responsibilities:
            if isinstance(responsibility, str):
                # Look for phrases indicating skills in responsibilities
                if any(keyword in responsibility.lower() for keyword in [
                    "using", "with", "skills", "ability", "knowledge", "experience", "proficient"
                ]):
                    skill_parts = re.split(r',|;|and', responsibility)
                    for part in skill_parts:
                        skill = part.strip()
                        if len(skill) > 3 and skill.lower() not in all_skills:
                            bucket = categorize_skill(skill)
                            bucketed_skills[bucket].append(skill)
                            all_skills.add(skill.lower())
                            skills_found = True
    
    # Check for concise description - often contains key skills
    concise_description = job_data.get("web_details", {}).get("concise_description", "")
    if isinstance(concise_description, str) and concise_description:
        # Extract requirements section from concise description
        requirements_match = re.search(r'Requirements:(.*?)(?:\n\n|\Z)', concise_description, re.DOTALL)
        if requirements_match:
            requirements_text = requirements_match.group(1)
            requirements_items = re.findall(r'-\s*(.*?)(?:\n|$)', requirements_text)
            for item in requirements_items:
                skill = item.strip()
                if len(skill) > 3 and skill.lower() not in all_skills:
                    bucket = categorize_skill(skill)
                    bucketed_skills[bucket].append(skill)
                    all_skills.add(skill.lower())
                    skills_found = True
    
    # If still no skills found, try to extract from job description
    if not skills_found or sum(len(skills) for skills in bucketed_skills.values()) < 3:
        job_description = job_data.get("job_description", "")
        if job_description:
            # Extract potential skills from job description
            extracted_skills = extract_skills_from_text(job_description)
            for skill in extracted_skills:
                if skill.lower() not in all_skills:
                    bucket = categorize_skill(skill)
                    bucketed_skills[bucket].append(skill)
                    all_skills.add(skill.lower())
    
    return bucketed_skills

def extract_skills_from_text(text: str) -> List[str]:
    """
    Extract potential skills from text using improved heuristics and NLP techniques
    
    Args:
        text: Text to extract skills from
    
    Returns:
        List[str]: List of potential skills
    """
    if not text:
        return []
        
    # Normalize text for better extraction
    normalized_text = text.replace('\r', '\n').replace('\t', ' ')
    skills = []
    
    # Common technical skills to look for directly
    common_technical_skills = [
        # Programming languages
        "Python", "Java", "JavaScript", "TypeScript", "C++", "C#", "Ruby", "Go", "PHP",
        "Swift", "Kotlin", "Rust", "Scala", "R", "MATLAB", "Perl", "Shell", "PowerShell",
        "Bash", "Objective-C", "SQL", "PL/SQL", "T-SQL", "Dart", "Groovy", "F#", "Lua",
        "COBOL", "Fortran", "Haskell", "Julia", "Clojure", "Erlang", "Elixir", "VBA",
        
        # Frameworks & libraries
        "React", "Angular", "Vue", "Node.js", "Express", "Django", "Flask", "Spring",
        "ASP.NET", "Laravel", "Rails", "FastAPI", "Symfony", "TensorFlow", "PyTorch",
        "Keras", "scikit-learn", "pandas", "NumPy", "jQuery", "Bootstrap", "NextJS",
        "Redux", "Svelte", "Ember.js", "Backbone.js", "RxJS", "NestJS", "Pandas",
        
        # Infrastructure & DevOps
        "AWS", "Azure", "Google Cloud", "Docker", "Kubernetes", "Git", "CI/CD",
        "Jenkins", "GitHub Actions", "Terraform", "Ansible", "Puppet", "Chef",
        "Prometheus", "Grafana", "ELK Stack", "Heroku", "DigitalOcean", "Nginx",
        "Apache", "Serverless", "Kafka", "RabbitMQ", "Redis", "Memcached", "Linux",
        
        # Databases
        "SQL", "NoSQL", "MongoDB", "PostgreSQL", "MySQL", "Oracle", "SQLite", 
        "Redis", "Elasticsearch", "Cassandra", "DynamoDB", "CosmosDB", "Firebase",
        "MariaDB", "Neo4j", "CouchDB", "InfluxDB", "TimeScale", "GraphQL",
        
        # Web & Mobile
        "HTML", "CSS", "SASS", "LESS", "REST API", "GraphQL", "OAuth", "JWT",
        "SOAP", "XML", "JSON", "WebSockets", "PWA", "SPA", "SEO", "Responsive Design",
        "Material UI", "Tailwind CSS", "iOS", "Android", "React Native", "Flutter",
        "Xamarin", "Cordova", "Ionic", "Unity", "WebGL",
        
        # Methodologies & Practices
        "Agile", "Scrum", "Kanban", "Waterfall", "TDD", "BDD", "DDD", "CI/CD",
        "DevOps", "GitOps", "Microservices", "Serverless", "OOP", "Functional Programming",
        "Design Patterns", "MVC", "MVVM", "Clean Architecture", "SOLID", "Twelve-Factor App"
    ]
    
    # Extract common skills directly with word boundary checks to avoid partial matches
    for skill in common_technical_skills:
        if re.search(r'\b' + re.escape(skill) + r'\b', text, re.IGNORECASE):
            skills.append(skill)
    
    # Look for "skills" sections with comprehensive section headers
    section_headers = [
        "skills", "requirements", "qualifications", "experience", "preferred", 
        "required", "responsibilities", "what you'll need", "what you need",
        "key skills", "key requirements", "technical skills", "essential skills",
        "competencies", "core competencies", "desired qualifications", "job requirements",
        "must-have", "skill set", "abilities", "technical requirements", "proficiency", 
        "capabilities", "expertise", "basic qualifications", "minimum requirements"
    ]
    
    # Create a pattern that accounts for various section header formats
    section_pattern = r'(?:^|\n)(?:' + '|'.join(section_headers) + r')(?:[^\n]*):?\s*(?:\n|$)((?:.*\n)+?)(?:\n\n|\n(?:[A-Z][a-z]+|\d+\.|\Z))'
    skill_sections = re.findall(section_pattern, normalized_text, re.IGNORECASE)
    
    for section in skill_sections:
        # Extract bullet points
        bullet_pattern = r"(?:^|\n)(?:\s*[-•*+]\s*|\d+\.\s*)([^\n]+)"
        bullets = re.findall(bullet_pattern, section)
        
        # Process each bullet point
        for bullet in bullets:
            # Clean up bullet text
            cleaned = bullet.strip()
            if len(cleaned) <= 3:
                continue
            
            # Look for specific skill phrases within bullets
            skill_indicators = [
                r"(?:proficient in|experience with|knowledge of|expertise in|skilled in|familiar with|background in)\s+([^,.;]+)",
                r"(?:\d+\+?\s+years?(?:\s+of)?\s+experience\s+(?:in|with))\s+([^,.;]+)",
                r"(?:strong|advanced|intermediate|basic)\s+([^,.;]+?)(?:\s+skills)",
                r"(?:ability to|able to)\s+([^,.;]+)"
            ]
            
            for pattern in skill_indicators:
                skill_phrases = re.findall(pattern, cleaned.lower())
                for phrase in skill_phrases:
                    clean_phrase = phrase.strip()
                    if 3 < len(clean_phrase) < 50:  # Reasonable skill length
                        skills.append(clean_phrase.capitalize())
            
            # Extract terms that appear to be technologies or methodologies
            # Look for capitalized terms that might be technologies or methods
            tech_terms = re.findall(r'\b([A-Z][a-zA-Z0-9]*(?:\.[a-zA-Z0-9]+)?)\b', cleaned)
            for term in tech_terms:
                if len(term) >= 2 and term not in ["I", "A", "The", "This", "That", "We", "You"]:
                    skills.append(term)
                    
            # Extract terms with unconventional capitalization (typical for tech)
            mixed_case_terms = re.findall(r'\b([a-z]+[A-Z][a-zA-Z0-9]*)\b', cleaned)
            skills.extend(mixed_case_terms)
                    
            # Extract skills from lists within bullets
            if "," in cleaned or ";" in cleaned:
                separators = r'[,;]'
                parts = re.split(separators, cleaned)
                for part in parts:
                    clean_part = part.strip()
                    # Check if it could be a skill (not too long, has a keyword or is capitalized)
                    if 3 < len(clean_part) < 30 and (
                        any(kw in clean_part.lower() for kw in ["experience", "skill", "knowledge", "proficient"]) or
                        any(c.isupper() for c in clean_part) or
                        re.search(r'\b[A-Z][a-z]+', clean_part)
                    ):
                        skills.append(clean_part)
    
    # Try alternative approach if few skills found
    if len(skills) < 5:
        # Extract sentences likely to contain skills
        sentences = re.split(r'[.!?]\s+', normalized_text)
        for sentence in sentences:
            if any(kw in sentence.lower() for kw in [
                "skill", "experience", "knowledge", "proficiency", "familiar", 
                "proficient", "competent", "ability", "expertise", "background"
            ]):
                # Extract potential technologies (often capitalized)
                tech_candidates = re.findall(r'\b([A-Z][a-zA-Z0-9]*(?:\.[a-zA-Z0-9]+)?)\b', sentence)
                skills.extend([t for t in tech_candidates if t not in ["I", "A", "The"]])
                
                # Look for phrases after skill indicators
                skill_parts = re.split(r'(?:including|such as|like|e\.g\.|i\.e\.|specifically|particularly)', sentence, flags=re.IGNORECASE)
                if len(skill_parts) > 1:
                    potential_skills = re.split(r'[,;]|\s+and\s+', skill_parts[1])
                    skills.extend([s.strip() for s in potential_skills if 3 < len(s.strip()) < 40])
    
    # Clean up skills
    cleaned_skills = []
    seen = set()
    for skill in skills:
        # Normalize the skill
        skill = skill.strip().rstrip(".,;:()").strip()
        
        # Skip if empty or too short or too long
        if not skill or len(skill) <= 2 or len(skill) > 50:
            continue
            
        # Skip if it's an article or common word
        if skill.lower() in ["the", "and", "for", "with", "what", "when", "where", "how", "why"]:
            continue
            
        # If hasn't been seen, add to cleaned skills
        if skill.lower() not in seen:
            seen.add(skill.lower())
            cleaned_skills.append(skill)
    
    return cleaned_skills

def calculate_bucket_weights(job_skills_buckets: Dict[str, List[str]]) -> Dict[str, float]:
    """
    Calculate weights for each skill bucket based on job requirements
    
    Args:
        job_skills_buckets: Job skills organized by bucket
    
    Returns:
        Dict[str, float]: Weight for each bucket (0.0-1.0)
    """
    # Count skills in each bucket
    bucket_counts = {bucket: len(skills) for bucket, skills in job_skills_buckets.items()}
    total_skills = sum(bucket_counts.values())
    
    if total_skills == 0:
        # Equal weight if no skills
        return {bucket: 1.0 / len(job_skills_buckets) for bucket in job_skills_buckets}
    
    # Calculate weights based on proportion of skills
    weights = {bucket: count / total_skills for bucket, count in bucket_counts.items()}
    
    # Ensure minimum weight for each bucket with at least one skill
    min_weight = 0.1
    for bucket, count in bucket_counts.items():
        if count > 0 and weights[bucket] < min_weight:
            weights[bucket] = min_weight
    
    # Normalize weights to sum to 1.0
    weight_sum = sum(weights.values())
    if weight_sum > 0:
        normalized_weights = {bucket: weight / weight_sum for bucket, weight in weights.items()}
    else:
        # Fallback if all weights are 0
        normalized_weights = {bucket: 1.0 / len(job_skills_buckets) for bucket in job_skills_buckets}
    
    return normalized_weights

def extract_percentage(text: str) -> float:
    """
    Extract a percentage from text
    
    Args:
        text: Text to extract percentage from
    
    Returns:
        float: Extracted percentage (0-1.0)
    """
    # Try to find a percentage (X%) pattern
    percentage_match = re.search(r'(\d{1,3})%', text)
    if percentage_match:
        try:
            percentage = int(percentage_match.group(1))
            return min(percentage, 100) / 100.0
        except ValueError:
            pass
    
    # Try to find a decimal (0.X) pattern
    decimal_match = re.search(r'(0\.\d+)', text)
    if decimal_match:
        try:
            decimal = float(decimal_match.group(1))
            return min(decimal, 1.0)
        except ValueError:
            pass
    
    # Try to find a fraction (X/10 or X out of 10) pattern
    fraction_match = re.search(r'(\d+)\s*(?:\/|out of)\s*10', text)
    if fraction_match:
        try:
            fraction = int(fraction_match.group(1))
            return min(fraction, 10) / 10.0
        except ValueError:
            pass
    
    # Default to 0 if no percentage found
    return 0.0
