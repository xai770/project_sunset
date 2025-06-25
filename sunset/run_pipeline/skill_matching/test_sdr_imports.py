#!/usr/bin/env python3
"""
Test script for the refactored SDR implementation
"""

import os
import sys
import importlib

# Add project root to path if needed
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
if project_root not in sys.path:
    sys.path.append(project_root)

def test_imports():
    """Test that all the refactored modules can be imported correctly"""
    modules = [
        'run_pipeline.skill_matching.sdr_pipeline',
        'run_pipeline.skill_matching.test_utilities',
        'run_pipeline.skill_matching.validation_utilities',
        'run_pipeline.skill_matching.run_enhanced_sdr',
    ]
    
    success = True
    for module in modules:
        try:
            imported_module = importlib.import_module(module)
            print(f"✅ Successfully imported {module}")
            
            # Check if the module has the expected functions
            if module == 'run_pipeline.skill_matching.sdr_pipeline':
                expected_functions = ['run_skill_analysis', 'run_relationship_classification', 
                                     'apply_expert_feedback', 'generate_visualizations', 
                                     'run_complete_pipeline']
                check_functions(imported_module, expected_functions)
                
            elif module == 'run_pipeline.skill_matching.test_utilities':
                expected_functions = ['check_domain_aware_match', 'test_domain_aware_matching', 
                                     'calculate_match_metrics']
                check_functions(imported_module, expected_functions)
                
            elif module == 'run_pipeline.skill_matching.validation_utilities':
                expected_functions = ['validate_skill_enrichment']
                check_functions(imported_module, expected_functions)
                
        except ImportError as e:
            print(f"❌ Failed to import {module}: {e}")
            success = False
    
    return success

def check_functions(module, expected_functions):
    """Check if a module has the expected functions"""
    for func in expected_functions:
        if hasattr(module, func):
            print(f"  - Found function: {func}")
        else:
            print(f"  - ❌ Missing function: {func}")

if __name__ == "__main__":
    print("Testing SDR implementation modules...")
    if test_imports():
        print("\nAll imports successful! The refactoring appears to be working.")
    else:
        print("\nThere were issues with the imports. Please check the error messages above.")
