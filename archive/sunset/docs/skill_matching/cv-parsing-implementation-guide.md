# CV to Skill Profile Parser Implementation Guide

This document provides a comprehensive implementation plan for parsing a CV into a structured skill profile using LLMs. The approach divides the CV into logical blocks, processes each separately, and merges the results into a comprehensive skill profile.

## System Architecture

```
CV Text → Block Divider → Block Parser → Profile Merger → Comprehensive Skill Profile
```

## 1. File Structure

```
cv-skill-parser/
├── src/
│   ├── __init__.py
│   ├── llm_client.py       # Client for LLM API
│   ├── block_parser.py     # Parse individual CV blocks
│   ├── profile_merger.py   # Merge multiple skill profiles
│   └── utils.py            # Utility functions
├── prompts/
│   └── cv_parser.md        # Prompt template for parsing
├── data/
│   ├── cv_blocks/          # Store CV blocks
│   └── output/             # Store parsing results
├── config.json             # Configuration file
└── main.py                 # Main script
```

## 2. LLM Client Implementation (`llm_client.py`)

```python
import json
import requests
import logging

class LLMClient:
    """Client for interacting with LLM API."""
    
    def __init__(self, endpoint="http://localhost:11434/api/generate"):
        """Initialize the LLM client.
        
        Args:
            endpoint: API endpoint URL
        """
        self.endpoint = endpoint
        self.logger = logging.getLogger(__name__)
    
    def generate(self, model, prompt, temperature=0.7, max_tokens=4000):
        """Send a generation request to the LLM API.
        
        Args:
            model: Model name to use
            prompt: Text prompt
            temperature: Sampling temperature (0.0-1.0)
            max_tokens: Maximum tokens to generate
            
        Returns:
            Generated text response or None if error
        """
        payload = {
            "model": model,
            "prompt": prompt,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        try:
            response = requests.post(self.endpoint, json=payload)
            response.raise_for_status()
            return response.json().get("response", "")
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error calling LLM API: {e}")
            return None
    
    def extract_json(self, text):
        """Extract JSON object from text response.
        
        Args:
            text: Text containing JSON
            
        Returns:
            Parsed JSON object or None if extraction fails
        """
        try:
            # Find JSON object (starting with { and ending with })
            start_idx = text.find('{')
            if start_idx == -1:
                self.logger.error("No JSON object found in response")
                return None
                
            # Track brace nesting to find the end of the JSON object
            brace_count = 0
            for i in range(start_idx, len(text)):
                if text[i] == '{':
                    brace_count += 1
                elif text[i] == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        json_str = text[start_idx:i+1]
                        return json.loads(json_str)
            
            self.logger.error("No matching closing brace found in JSON")
            return None
        except json.JSONDecodeError as e:
            self.logger.error(f"Error decoding JSON: {e}")
            return None
```

## 3. Block Parser Implementation (`block_parser.py`)

```python
import os
import json
import logging

class BlockParser:
    """Parser for extracting skills from CV blocks."""
    
    def __init__(self, llm_client, model="olmo2:latest", prompt_path="prompts/cv_parser.md"):
        """Initialize the block parser.
        
        Args:
            llm_client: LLMClient instance
            model: Model name to use
            prompt_path: Path to the prompt template file
        """
        self.llm_client = llm_client
        self.model = model
        self.logger = logging.getLogger(__name__)
        
        # Load prompt template
        try:
            with open(prompt_path, 'r', encoding='utf-8') as f:
                self.prompt_template = f.read()
        except Exception as e:
            self.logger.error(f"Error loading prompt template: {e}")
            self.prompt_template = "Extract skills from the CV: {cv_text}"
    
    def parse_block(self, cv_block):
        """Parse a CV block and extract skills.
        
        Args:
            cv_block: CV text block
            
        Returns:
            Structured skill profile as JSON object or None if parsing fails
        """
        prompt = self.prompt_template.replace("{cv_text}", cv_block)
        
        # Call LLM API
        response = self.llm_client.generate(self.model, prompt)
        if not response:
            self.logger.error("No response from LLM")
            return None
        
        # Extract JSON from response
        result = self.llm_client.extract_json(response)
        if not result:
            self.logger.error("Failed to extract JSON from LLM response")
            self.logger.debug(f"Raw response: {response[:500]}...")
            return None
        
        return result
    
    def parse_block_file(self, block_file_path, output_path=None):
        """Parse a CV block file and optionally save the result.
        
        Args:
            block_file_path: Path to CV block file
            output_path: Optional path to save the result JSON
            
        Returns:
            Structured skill profile as JSON object or None if parsing fails
        """
        try:
            with open(block_file_path, 'r', encoding='utf-8') as f:
                cv_block = f.read()
        except Exception as e:
            self.logger.error(f"Error reading CV block file: {e}")
            return None
        
        # Parse CV block
        result = self.parse_block(cv_block)
        
        # Save result if output path provided
        if result and output_path:
            try:
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(result, f, indent=2)
                self.logger.info(f"Saved parsed block to {output_path}")
            except Exception as e:
                self.logger.error(f"Error saving result: {e}")
        
        return result
```

## 4. Profile Merger Implementation (`profile_merger.py`)

```python
import logging

class ProfileMerger:
    """Merger for combining multiple skill profiles."""
    
    def __init__(self):
        """Initialize the profile merger."""
        self.logger = logging.getLogger(__name__)
    
    def normalize_skill_name(self, name):
        """Normalize a skill name for comparison.
        
        Args:
            name: Skill name
            
        Returns:
            Normalized skill name
        """
        # Convert to lowercase and remove excess whitespace
        return name.lower().strip()
    
    def merge_profiles(self, profiles):
        """Merge multiple skill profiles into one comprehensive profile.
        
        Args:
            profiles: List of skill profile JSONs
            
        Returns:
            Merged skill profile
        """
        if not profiles:
            self.logger.error("No profiles to merge")
            return None
            
        # Use first profile for name and contact info
        merged_profile = {
            "name": profiles[0]["name"],
            "contact": profiles[0]["contact"],
            "skill_profile": {
                "IT_Technical": [],
                "IT_Management": [],
                "Sourcing_and_Procurement": [],
                "Leadership_and_Management": [],
                "Analysis_and_Reporting": [],
                "Domain_Knowledge": []
            }
        }
        
        # Create skill lookup to track what we've already added
        skill_lookup = {category: {} for category in merged_profile["skill_profile"]}
        
        # Process each profile
        for profile in profiles:
            for category, skills in profile.get("skill_profile", {}).items():
                if category not in merged_profile["skill_profile"]:
                    continue
                    
                for skill in skills:
                    skill_name = skill.get("name", "")
                    if not skill_name:
                        continue
                        
                    # Normalize skill name for comparison
                    normalized_name = self.normalize_skill_name(skill_name)
                    
                    # Get skill properties
                    skill_level = skill.get("level", 3)
                    skill_evidence = skill.get("evidence", "")
                    
                    # Check if skill already exists
                    if normalized_name in skill_lookup[category]:
                        existing_index = skill_lookup[category][normalized_name]
                        existing_skill = merged_profile["skill_profile"][category][existing_index]
                        
                        # Update level (take highest)
                        existing_skill["level"] = max(existing_skill["level"], skill_level)
                        
                        # Add additional evidence if not duplicate
                        if isinstance(existing_skill["evidence"], list):
                            if skill_evidence not in existing_skill["evidence"]:
                                existing_skill["evidence"].append(skill_evidence)
                        else:
                            if skill_evidence != existing_skill["evidence"]:
                                existing_skill["evidence"] = [existing_skill["evidence"], skill_evidence]
                    else:
                        # Add new skill
                        new_skill = {
                            "name": skill_name,
                            "level": skill_level,
                            "evidence": skill_evidence
                        }
                        merged_profile["skill_profile"][category].append(new_skill)
                        skill_lookup[category][normalized_name] = len(merged_profile["skill_profile"][category]) - 1
        
        return merged_profile
```

## 5. Block Divider Function (`utils.py`)

```python
import os
import re
import logging

def divide_cv_into_blocks(cv_text, output_dir=None):
    """Divide a CV into logical blocks based on section headers.
    
    Args:
        cv_text: Full CV text
        output_dir: Optional directory to save blocks as files
        
    Returns:
        List of CV blocks
    """
    logger = logging.getLogger(__name__)
    
    # Find section headers based on markdown-like patterns
    section_patterns = [
        r'^#{1,3}\s+([^\n]+)$',  # Markdown headers (e.g., # Section, ## Section)
        r'^([^\n]+)\n[=\-]+$',    # Underlined headers (e.g., Section\n====)
        r'^([A-Z][A-Z\s]+):$'     # ALL CAPS followed by colon
    ]
    
    # Combine patterns
    combined_pattern = '|'.join(f'({pattern})' for pattern in section_patterns)
    
    # Find all section headers
    matches = list(re.finditer(combined_pattern, cv_text, re.MULTILINE))
    
    if not matches:
        logger.warning("No section headers found, returning CV as single block")
        return [cv_text]
    
    # Extract blocks
    blocks = []
    
    for i, match in enumerate(matches):
        # Section header
        header = match.group(0)
        
        # Section content (from current match to next match or end)
        start = match.start()
        end = matches[i+1].start() if i < len(matches) - 1 else len(cv_text)
        
        # Extract block (header + content)
        block = cv_text[start:end].strip()
        blocks.append(block)
    
    # Save blocks if output directory provided
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        
        for i, block in enumerate(blocks):
            # Extract header text for filename
            header_match = re.search(combined_pattern, block, re.MULTILINE)
            header_text = header_match.group(0) if header_match else f"Block_{i+1}"
            
            # Clean header text for filename
            filename = re.sub(r'[^\w\s-]', '', header_text)
            filename = re.sub(r'[-\s]+', '_', filename).strip('-_')
            
            # Save block to file
            block_path = os.path.join(output_dir, f"{filename}.txt")
            with open(block_path, 'w', encoding='utf-8') as f:
                f.write(block)
            logger.info(f"Saved block to {block_path}")
    
    return blocks

def is_experience_section(text):
    """Check if text is an experience section.
    
    Args:
        text: Text to check
        
    Returns:
        True if experience section, False otherwise
    """
    # Check for common experience section headers
    experience_patterns = [
        r'experience',
        r'employment',
        r'work history',
        r'career',
        r'professional background'
    ]
    
    # Check for company/position patterns
    company_patterns = [
        r'^\s*[A-Z][A-Za-z0-9\s,\.]+\([0-9]{4}.*?[0-9]{4}.*?\)',  # Company (YYYY - YYYY)
        r'^\s*[A-Z][A-Za-z0-9\s,\.]+\s*[0-9]{4}.*?[0-9]{4}',       # Company YYYY - YYYY
        r'^\s*[A-Z][A-Za-z0-9\s,\.]+\s*\|.*?[0-9]{4}'              # Company | Position | YYYY
    ]
    
    # Check for position/role patterns
    position_patterns = [
        r'^\s*\*\*[A-Z][A-Za-z0-9\s,\.]+\*\*',  # **Position**
        r'^\s*[A-Z][A-Za-z0-9\s,\.]+\s*\([A-Za-z]+\)'  # Position (Title)
    ]
    
    # Check for experience section headers
    for pattern in experience_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    
    # Check for company patterns
    for pattern in company_patterns:
        if re.search(pattern, text, re.MULTILINE):
            return True
    
    # Check for position patterns
    for pattern in position_patterns:
        if re.search(pattern, text, re.MULTILINE):
            return True
    
    return False

def further_divide_experience(blocks):
    """Further divide experience blocks by role/position.
    
    Args:
        blocks: List of CV blocks
        
    Returns:
        List of CV blocks with experience sections divided by role
    """
    logger = logging.getLogger(__name__)
    new_blocks = []
    
    for block in blocks:
        # Check if block is an experience section
        if is_experience_section(block):
            # Look for role/position patterns
            role_patterns = [
                r'^\s*\*\*([^\*]+)\*\*\s*\(([^\)]+)\)',  # **Role** (Date range)
                r'^\s*([A-Z][A-Za-z0-9\s,\.]+)\s*\(([0-9]{4}.*?(?:[0-9]{4}|Present))\)'  # Role (YYYY - YYYY)
            ]
            
            # Find role headers
            role_matches = []
            for pattern in role_patterns:
                role_matches.extend(list(re.finditer(pattern, block, re.MULTILINE)))
            
            # Sort matches by position
            role_matches.sort(key=lambda m: m.start())
            
            if role_matches:
                # Extract company/section header
                header_end = role_matches[0].start()
                header = block[:header_end].strip()
                
                # Extract roles
                for i, match in enumerate(role_matches):
                    # Role content (from current match to next match or end)
                    start = match.start()
                    end = role_matches[i+1].start() if i < len(role_matches) - 1 else len(block)
                    
                    # Extract role block (include header for context)
                    role_block = f"{header}\n\n{block[start:end].strip()}"
                    new_blocks.append(role_block)
            else:
                # No roles found, keep block as is
                new_blocks.append(block)
        else:
            # Not an experience section, keep block as is
            new_blocks.append(block)
    
    return new_blocks
```

## 6. Main Script (`main.py`)

```python
import os
import json
import argparse
import logging
from src.llm_client import LLMClient
from src.block_parser import BlockParser
from src.profile_merger import ProfileMerger
from src.utils import divide_cv_into_blocks, further_divide_experience

def setup_logging(log_file=None, level=logging.INFO):
    """Set up logging with console and optional file output.
    
    Args:
        log_file: Optional log file path
        level: Logging level
    
    Returns:
        Configured logger
    """
    # Create logger
    logger = logging.getLogger()
    logger.setLevel(level)
    
    # Create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Create file handler if log file provided
    if log_file:
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger

def main():
    """Main function."""
    # Set up argument parser
    parser = argparse.ArgumentParser(description='CV to Skill Profile Parser')
    parser.add_argument('--cv', required=True, help='Path to CV file')
    parser.add_argument('--output-dir', default='output', help='Output directory')
    parser.add_argument('--blocks-dir', default='data/cv_blocks', help='Directory to save CV blocks')
    parser.add_argument('--model', default='olmo2:latest', help='LLM model to use')
    parser.add_argument('--log-file', default='output/parser.log', help='Log file')
    args = parser.parse_args()
    
    # Set up logging
    logger = setup_logging(args.log_file)
    
    # Create output directories
    os.makedirs(args.output_dir, exist_ok=True)
    os.makedirs(args.blocks_dir, exist_ok=True)
    
    # Initialize components
    llm_client = LLMClient()
    block_parser = BlockParser(llm_client, model=args.model)
    profile_merger = ProfileMerger()
    
    # Load CV
    try:
        with open(args.cv, 'r', encoding='utf-8') as f:
            cv_text = f.read()
    except Exception as e:
        logger.error(f"Error reading CV file: {e}")
        return
    
    # Step 1: Divide CV into blocks
    logger.info("Dividing CV into blocks...")
    blocks = divide_cv_into_blocks(cv_text, output_dir=os.path.join(args.blocks_dir, "initial"))
    logger.info(f"Divided CV into {len(blocks)} initial blocks")
    
    # Step 2: Further divide experience sections by role
    logger.info("Further dividing experience sections...")
    blocks = further_divide_experience(blocks)
    
    # Save final blocks
    blocks_dir = os.path.join(args.blocks_dir, "final")
    os.makedirs(blocks_dir, exist_ok=True)
    for i, block in enumerate(blocks):
        block_path = os.path.join(blocks_dir, f"block_{i+1}.txt")
        with open(block_path, 'w', encoding='utf-8') as f:
            f.write(block)
    
    logger.info(f"Final block count: {len(blocks)}")
    
    # Step 3: Parse each block
    logger.info("Parsing blocks...")
    profiles = []
    
    for i, block in enumerate(blocks):
        logger.info(f"Parsing block {i+1}/{len(blocks)}...")
        block_output_path = os.path.join(args.output_dir, f"block_{i+1}_profile.json")
        
        # Parse block
        profile = block_parser.parse_block(block)
        
        # Save block profile
        if profile:
            with open(block_output_path, 'w', encoding='utf-8') as f:
                json.dump(profile, f, indent=2)
            profiles.append(profile)
            logger.info(f"Saved block {i+1} profile to {block_output_path}")
        else:
            logger.warning(f"Failed to parse block {i+1}")
    
    # Step 4: Merge profiles
    logger.info("Merging profiles...")
    merged_profile = profile_merger.merge_profiles(profiles)
    
    # Save merged profile
    if merged_profile:
        merged_output_path = os.path.join(args.output_dir, "merged_profile.json")
        with open(merged_output_path, 'w', encoding='utf-8') as f:
            json.dump(merged_profile, f, indent=2)
        logger.info(f"Saved merged profile to {merged_output_path}")
        
        # Print summary
        print("\n=== SKILL PROFILE SUMMARY ===")
        print(f"Name: {merged_profile['name']}")
        
        total_skills = 0
        for category, skills in merged_profile["skill_profile"].items():
            category_display = category.replace("_", " ").title()
            print(f"\n{category_display} ({len(skills)} skills):")
            
            for skill in skills:
                print(f"- {skill['name']} (Level {skill['level']})")
                total_skills += 1
        
        print(f"\nTotal Skills: {total_skills}")
    else:
        logger.error("Failed to merge profiles")

if __name__ == "__main__":
    main()
```

## 7. CV Parser Prompt (`prompts/cv_parser.md`)

```markdown
# Prompt for CV Skill Parsing with Olmo

You are a specialized skill extraction system designed to parse CVs/resumes and categorize skills according to predefined categories.

## Task

1. Analyze the provided CV/resume block
2. Extract all skills mentioned or implied in the document
3. Categorize each skill into one of the predefined skill categories
4. Rate the proficiency level for each skill on a scale of 1-5 (1=basic, 5=expert)
5. Format the result as a JSON object

## Skill Categories to Use

Use ONLY these exact skill categories for categorization:
- IT_Technical: Technical IT skills like programming, database development, system architecture
- IT_Management: IT governance, project management, software lifecycle management skills
- Sourcing_and_Procurement: Skills related to vendor management, contracts, procurement
- Leadership_and_Management: Team leadership, process management, stakeholder engagement
- Analysis_and_Reporting: Analytical skills, data processing, reporting, decision frameworks
- Domain_Knowledge: Industry-specific knowledge and expertise

## Output Format

Format your output as a JSON object with the following structure:

```json
{
  "name": "Gershon Urs Pollatschek",
  "contact": {
    "email": "gershon.pollatschek@gmail.com",
    "phone": "+49 1512 5098515"
  },
  "skill_profile": {
    "IT_Technical": [
      {
        "name": "Database Development",
        "level": 4,
        "evidence": "Developed database application for budgeting process"
      }
    ],
    "IT_Management": [
      {
        "name": "Software License Management",
        "level": 5,
        "evidence": "Led Deutsche Bank's Software License Management organization"
      }
    ],
    "Sourcing_and_Procurement": [
      {
        "name": "Strategic Sourcing",
        "level": 5,
        "evidence": "Strategic sourcing and contract negotiation"
      }
    ],
    "Leadership_and_Management": [
      {
        "name": "Team Leadership",
        "level": 4,
        "evidence": "Cross functional team management in IT and sourcing"
      }
    ],
    "Analysis_and_Reporting": [
      {
        "name": "Process Analysis",
        "level": 4,
        "evidence": "Analyze gaps in process and propose new process"
      }
    ],
    "Domain_Knowledge": [
      {
        "name": "Financial Services Industry",
        "level": 4,
        "evidence": "Deutsche Bank, Frankfurt (multiple roles)"
      }
    ]
  }
}
```

Ensure all skill levels are rated on a scale of 1-5 where:
- Level 5: Expert - Advanced mastery with extensive experience
- Level 4: Advanced - Strong proficiency with substantial experience
- Level 3: Intermediate - Competent with moderate experience
- Level 2: Basic - Fundamental understanding with limited experience
- Level 1: Awareness - Basic familiarity or minimal experience

For each skill, include specific evidence from the CV block that demonstrates this skill.

If a category has no skills, include it with an empty array.

Focus only on the skills that are evident in THIS SPECIFIC BLOCK of the CV, not on general assumptions about the person's career.

## CV Block
{cv_text}
```

## 8. Usage Instructions

### Basic Usage:

```bash
# Process a CV and generate a skill profile
python main.py --cv /path/to/your/cv.md --output-dir output
```

### Viewing Results:

1. Check the `output/merged_profile.json` file for the comprehensive skill profile
2. Individual block profiles are in `output/block_X_profile.json`
3. The original blocks are in `data/cv_blocks/final/`

### Customization:

- Modify the CV Parser prompt in `prompts/cv_parser.md`
- Adjust the skill category definitions as needed
- Configure the block division logic in `utils.py`

## 9. Implementation Notes

1. **Block Division**: The system uses both section headers and role patterns to divide the CV. This is configurable to match different CV formats.

2. **Skill Normalization**: Similar skills with slight naming differences are consolidated during merging.

3. **Evidence Collection**: Evidence from multiple occurrences of the same skill is combined.

4. **Error Handling**: The system includes comprehensive error handling for LLM failures, parsing errors, and file I/O issues.

5. **Level Selection**: When the same skill appears in multiple blocks, the highest level is used in the final profile.

This implementation provides a complete pipeline for parsing a CV into a comprehensive skill profile using Olmo. The modular design allows for easy customization and extension to meet specific requirements.
