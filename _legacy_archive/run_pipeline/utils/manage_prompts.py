#!/usr/bin/env python3
"""
Prompt Management Utility

This script provides a command-line interface for managing job description prompts.
It allows you to:
- View the current prompt and version
- Add a new prompt version
- List all available prompt versions
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime

# Add project root directory to path for imports
project_root = str(Path(__file__).resolve().parent.parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

# Add parent directory as well
parent_dir = str(Path(__file__).resolve().parent.parent)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from run_pipeline.config.paths import PROJECT_ROOT

# Define paths
PROMPTS_DIR = PROJECT_ROOT / "run_pipeline" / "config" / "prompts"
JOB_DESCRIPTION_PROMPT_FILE = PROMPTS_DIR / "job_description_prompts.json"

def ensure_prompts_dir():
    """Ensure the prompts directory exists"""
    os.makedirs(PROMPTS_DIR, exist_ok=True)
    return PROMPTS_DIR

def get_default_prompt():
    """Get the default job description prompt"""
    return """Extract ONLY the English version of this job description from Deutsche Bank. 

Please:
1. Remove all German text completely
2. Remove all website navigation elements and menus
3. Remove company marketing content and benefits sections
4. Remove all HTML formatting and unnecessary whitespace
5. Preserve the exact original wording of the job title, location, responsibilities, and requirements
6. Maintain the contact information
7. Keep the original structure (headings, bullet points) of the core job description
8. Double check that you remove all sections and wordings discussing the company culture, benefits, values, and mission statement

The result should be a clean, professional job description in English only, with all the essential information about the position preserved exactly as written."""

def load_prompt_data():
    """Load prompt data from file or create default"""
    ensure_prompts_dir()
    
    if not JOB_DESCRIPTION_PROMPT_FILE.exists():
        # Create default prompt file
        default_version = "1.0"
        data = {
            "version": default_version,
            "updated_at": datetime.now().isoformat(),
            "active_version": default_version,
            "versions": {
                default_version: {
                    "prompt": get_default_prompt(),
                    "created_at": datetime.now().isoformat(),
                    "description": "Default job description prompt",
                    "author": "system"
                }
            }
        }
        
        try:
            with open(JOB_DESCRIPTION_PROMPT_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"Created default prompt file at {JOB_DESCRIPTION_PROMPT_FILE}")
        except Exception as e:
            print(f"Error creating prompt file: {str(e)}")
            return None
    
    # Load existing data
    try:
        with open(JOB_DESCRIPTION_PROMPT_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading prompt file: {str(e)}")
        return None

def save_prompt_data(data):
    """Save prompt data to file"""
    ensure_prompts_dir()
    
    try:
        with open(JOB_DESCRIPTION_PROMPT_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error saving prompt file: {str(e)}")
        return False

def show_current_prompt():
    """Show the current active prompt and version"""
    data = load_prompt_data()
    if not data:
        print("Could not load prompt data.")
        return
    
    active_version = data.get("active_version", "1.0")
    if active_version not in data.get("versions", {}):
        print(f"Error: Active version {active_version} not found in prompt file.")
        return
    
    prompt_info = data["versions"][active_version]
    
    print("=" * 80)
    print(f"Current Job Description Prompt (Version {active_version})")
    print("=" * 80)
    print(f"Created: {prompt_info.get('created_at', 'unknown')}")
    print(f"Author: {prompt_info.get('author', 'system')}")
    print(f"Description: {prompt_info.get('description', 'No description')}")
    print("=" * 80)
    print(prompt_info.get("prompt", "Error: Prompt text not found"))
    print("=" * 80)

def add_new_prompt(prompt_text, description=None, author=None):
    """Add a new prompt version"""
    data = load_prompt_data()
    if not data:
        print("Could not load prompt data.")
        return
    
    # Calculate new version
    versions = data.get("versions", {})
    if not versions:
        new_version = "1.0"
    else:
        # Find highest version
        version_keys = [v.split('.') for v in versions.keys()]
        version_keys.sort(key=lambda x: (int(x[0]), int(x[1])))
        latest = version_keys[-1]
        
        # Increment minor version
        new_version = f"{latest[0]}.{int(latest[1]) + 1}"
    
    # Add new version
    if "versions" not in data:
        data["versions"] = {}
    
    data["versions"][new_version] = {
        "prompt": prompt_text,
        "created_at": datetime.now().isoformat(),
        "description": description or f"Updated prompt version {new_version}",
        "author": author or "system"
    }
    
    # Update file metadata
    data["version"] = new_version
    data["updated_at"] = datetime.now().isoformat()
    data["active_version"] = new_version
    
    # Save to file
    if save_prompt_data(data):
        print(f"Successfully added new prompt version {new_version}")
        return new_version
    else:
        print("Failed to save new prompt version")
        return None

def list_versions():
    """List all available prompt versions"""
    data = load_prompt_data()
    if not data:
        print("Could not load prompt data.")
        return
    
    active_version = data.get("active_version", "1.0")
    versions = data.get("versions", {})
    
    if not versions:
        print("No prompt versions found.")
        return
    
    print("=" * 80)
    print("Job Description Prompt Versions")
    print("=" * 80)
    print(f"{'Version':<10} {'Active':<10} {'Date':<25} {'Author':<15} {'Description'}")
    print("-" * 80)
    
    # Sort versions by number
    sorted_versions = sorted(
        [(k, v) for k, v in versions.items()],
        key=lambda x: [int(i) for i in x[0].split('.')]
    )
    
    for version, info in sorted_versions:
        is_active = "✓" if version == active_version else ""
        created_at = info.get("created_at", "unknown")[:19]  # Truncate time for display
        author = info.get("author", "system")
        description = info.get("description", "No description")
        
        print(f"{version:<10} {is_active:<10} {created_at:<25} {author:<15} {description}")
    
    print("=" * 80)

def set_active_version(version):
    """Set a specific version as active"""
    data = load_prompt_data()
    if not data:
        print("Could not load prompt data.")
        return False
    
    versions = data.get("versions", {})
    if version not in versions:
        print(f"Error: Version {version} not found.")
        return False
    
    data["active_version"] = version
    data["updated_at"] = datetime.now().isoformat()
    
    if save_prompt_data(data):
        print(f"Successfully set version {version} as active.")
        return True
    else:
        print("Failed to set active version.")
        return False

def read_prompt_from_file(file_path):
    """Read prompt text from a file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"Error reading prompt file: {str(e)}")
        return None

def main():
    parser = argparse.ArgumentParser(description="Job Description Prompt Management Utility")
    
    # Create subparsers for different commands
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Show current prompt
    show_parser = subparsers.add_parser("show", help="Show the current active prompt")
    
    # List versions
    list_parser = subparsers.add_parser("list", help="List all prompt versions")
    
    # Add new version
    add_parser = subparsers.add_parser("add", help="Add a new prompt version")
    add_parser.add_argument("--file", type=str, help="File containing the prompt text")
    add_parser.add_argument("--text", type=str, help="Prompt text (use quotes)")
    add_parser.add_argument("--description", type=str, help="Description of the prompt changes")
    add_parser.add_argument("--author", type=str, help="Author of the prompt")
    
    # Set active version
    set_parser = subparsers.add_parser("set-active", help="Set a specific version as active")
    set_parser.add_argument("version", type=str, help="Version number to set as active (e.g., 1.0)")
    
    args = parser.parse_args()
    
    # Handle commands
    if args.command == "show":
        show_current_prompt()
    
    elif args.command == "list":
        list_versions()
    
    elif args.command == "add":
        prompt_text = None
        
        if args.file:
            prompt_text = read_prompt_from_file(args.file)
            if not prompt_text:
                return 1
        elif args.text:
            prompt_text = args.text
        else:
            print("Error: Either --file or --text must be specified.")
            return 1
        
        add_new_prompt(prompt_text, args.description, args.author)
    
    elif args.command == "set-active":
        set_active_version(args.version)
    
    else:
        parser.print_help()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
