#!/usr/bin/env python3
"""
Script to update version numbers in the staged processor package.
This is used to trigger reprocessing of jobs when significant changes are made.
"""

import sys
import argparse
from pathlib import Path
import re

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent))

def update_version(module_name, version_type='patch'):
    """
    Update the version number for a specific module
    
    Args:
        module_name: Name of the module to update (or 'all' for all modules)
        version_type: Type of version increment ('major', 'minor', 'patch')
    """
    versions_path = Path(__file__).parent / "run_pipeline" / "utils" / "staged_processor" / "versions.py"
    
    if not versions_path.exists():
        print(f"Error: versions.py not found at {versions_path}")
        return False
        
    # Read the current file content
    with open(versions_path, 'r') as f:
        content = f.read()
    
    # Determine modules to update
    modules_to_update = []
    
    if module_name == 'all':
        # Update all modules
        modules_to_update = [
            'HTML_CLEANER_VERSION', 
            'LANGUAGE_HANDLER_VERSION', 
            'EXTRACTORS_VERSION', 
            'FILE_HANDLER_VERSION', 
            'PROCESSOR_VERSION',
            'STAGED_PROCESSOR_VERSION'
        ]
    else:
        # Map module name to version constant
        module_mapping = {
            'html_cleaner': 'HTML_CLEANER_VERSION',
            'language_handler': 'LANGUAGE_HANDLER_VERSION',
            'extractors': 'EXTRACTORS_VERSION',
            'file_handler': 'FILE_HANDLER_VERSION',
            'processor': 'PROCESSOR_VERSION',
            'staged_processor': 'STAGED_PROCESSOR_VERSION'
        }
        
        if module_name in module_mapping:
            modules_to_update = [module_mapping[module_name]]
            # Always update the overall version when any component changes
            if module_name != 'staged_processor':
                modules_to_update.append('STAGED_PROCESSOR_VERSION')
        else:
            print(f"Error: Unknown module '{module_name}'")
            print(f"Valid modules: {', '.join(module_mapping.keys())}")
            return False
    
    # Update each version
    updated_content = content
    for module_var in modules_to_update:
        # Find current version
        pattern = rf'{module_var}\s*=\s*"(\d+)\.(\d+)\.(\d+)"'
        match = re.search(pattern, content)
        
        if match:
            major, minor, patch = map(int, match.groups())
            
            # Update version according to semantic versioning
            if version_type == 'major':
                major += 1
                minor = 0
                patch = 0
            elif version_type == 'minor':
                minor += 1
                patch = 0
            else:  # patch
                patch += 1
                
            new_version = f'{major}.{minor}.{patch}'
            replacement = f'{module_var} = "{new_version}"'
            updated_content = re.sub(pattern, replacement, updated_content)
            
            print(f"Updated {module_var}: {major}.{minor}.{patch}")
    
    # Write the updated content
    with open(versions_path, 'w') as f:
        f.write(updated_content)
        
    print(f"Successfully updated versions in {versions_path}")
    return True

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Update version numbers for staged processor')
    parser.add_argument('module', choices=['all', 'html_cleaner', 'language_handler', 'extractors', 
                                           'file_handler', 'processor', 'staged_processor'],
                        help='Module to update (or "all")')
    parser.add_argument('--type', choices=['major', 'minor', 'patch'], default='patch',
                        help='Type of version update (default: patch)')
    
    args = parser.parse_args()
    
    success = update_version(args.module, args.type)
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
