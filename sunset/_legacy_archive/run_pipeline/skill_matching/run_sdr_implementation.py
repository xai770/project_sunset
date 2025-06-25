#!/usr/bin/env python3
"""
SDR Implementation Runner - Orchestrates the SDR implementation process

This script orchestrates the complete SDR implementation process, including 
skill analysis, domain relationship classification, and matching algorithm testing.
"""

import os
import sys
import json
from datetime import datetime
import subprocess

# Import the component modules
try:
    from run_pipeline.skill_matching.skill_analyzer import SkillAnalyzer
    from run_pipeline.skill_matching.domain_relationship_classifier import DomainRelationshipClassifier
    from run_pipeline.skill_matching.domain_aware_matcher import DomainAwareMatchingAlgorithm
except ImportError as e:
    print(f"Error importing required modules: {e}")
    print("Make sure you're running this script from the correct directory.")
    sys.exit(1)

# Constants
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUTPUT_DIR = os.path.join(BASE_DIR, 'docs', 'skill_matching')

class SDRImplementationRunner:
    """Orchestrates the SDR implementation process"""
    
    def __init__(self):
        self.start_time = datetime.now()
        self.results = {
            'timestamp': self.start_time.isoformat(),
            'phases': {}
        }
    
    def create_output_directory(self):
        """Ensure the output directory exists"""
        os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    def run_skill_analysis(self):
        """Run the skill analysis phase"""
        print("\n=== Phase 1: Skill Analysis ===")
        start_time = datetime.now()
        
        try:
            analyzer = SkillAnalyzer()
            enriched_skills = analyzer.run_analysis()
            
            self.results['phases']['skill_analysis'] = {
                'status': 'success',
                'enriched_skills_count': len(enriched_skills),
                'duration_seconds': (datetime.now() - start_time).total_seconds()
            }
            
            print(f"Skill analysis completed successfully with {len(enriched_skills)} enriched skills")
            return True
        except Exception as e:
            self.results['phases']['skill_analysis'] = {
                'status': 'error',
                'error': str(e),
                'duration_seconds': (datetime.now() - start_time).total_seconds()
            }
            
            print(f"Error in skill analysis phase: {e}")
            return False
    
    def run_domain_relationship_classification(self):
        """Run the domain relationship classification phase"""
        print("\n=== Phase 2: Domain Relationship Classification ===")
        start_time = datetime.now()
        
        try:
            classifier = DomainRelationshipClassifier()
            relationships = classifier.run_classification()
            
            # Count relationship types
            relationship_counts = {}
            for skill1, relations in relationships.items():
                for skill2, relation_data in relations.items():
                    rel_type = relation_data.get('relationship', 'Unknown')
                    relationship_counts[rel_type] = relationship_counts.get(rel_type, 0) + 1
            
            self.results['phases']['domain_relationship_classification'] = {
                'status': 'success',
                'relationship_counts': relationship_counts,
                'duration_seconds': (datetime.now() - start_time).total_seconds()
            }
            
            print(f"Domain relationship classification completed successfully")
            print(f"Relationship counts: {relationship_counts}")
            return True
        except Exception as e:
            self.results['phases']['domain_relationship_classification'] = {
                'status': 'error',
                'error': str(e),
                'duration_seconds': (datetime.now() - start_time).total_seconds()
            }
            
            print(f"Error in domain relationship classification phase: {e}")
            return False
    
    def run_matching_algorithm_testing(self):
        """Run the matching algorithm testing phase"""
        print("\n=== Phase 3: Matching Algorithm Testing ===")
        start_time = datetime.now()
        
        try:
            matcher = DomainAwareMatchingAlgorithm()
            matcher.load_data()
            test_results = matcher.run_test_comparisons()
            
            # Calculate improvement metrics
            overall_improvement = sum(result['improvement'] for result in test_results) / len(test_results)
            false_positives_reduced = sum(result['false_positives_reduced'] for result in test_results)
            
            self.results['phases']['matching_algorithm_testing'] = {
                'status': 'success',
                'test_cases': len(test_results),
                'overall_improvement': overall_improvement,
                'false_positives_reduced': false_positives_reduced,
                'duration_seconds': (datetime.now() - start_time).total_seconds()
            }
            
            print(f"Matching algorithm testing completed successfully")
            print(f"Overall improvement in match quality: {overall_improvement:.2f}")
            print(f"Total false positives reduced: {false_positives_reduced}")
            return True
        except Exception as e:
            self.results['phases']['matching_algorithm_testing'] = {
                'status': 'error',
                'error': str(e),
                'duration_seconds': (datetime.now() - start_time).total_seconds()
            }
            
            print(f"Error in matching algorithm testing phase: {e}")
            return False
    
    def make_scripts_executable(self):
        """Make all Python scripts executable"""
        try:
            scripts_dir = os.path.join(BASE_DIR, 'run_pipeline', 'skill_matching')
            
            subprocess.run(['chmod', '+x', 
                os.path.join(scripts_dir, 'skill_analyzer.py'),
                os.path.join(scripts_dir, 'domain_relationship_classifier.py'),
                os.path.join(scripts_dir, 'domain_aware_matcher.py')
            ])
            return True
        except Exception as e:
            print(f"Error making scripts executable: {e}")
            return False
    
    def save_results(self):
        """Save the implementation results"""
        # Add overall duration
        self.results['overall_duration_seconds'] = (datetime.now() - self.start_time).total_seconds()
        
        # Generate summary
        success_phases = sum(1 for phase_data in self.results['phases'].values() if phase_data.get('status') == 'success')
        total_phases = len(self.results['phases'])
        
        self.results['summary'] = {
            'success_rate': f"{success_phases}/{total_phases} phases completed successfully",
            'overall_status': 'success' if success_phases == total_phases else 'partial_success' if success_phases > 0 else 'failure'
        }
        
        # Save to file
        output_file = os.path.join(OUTPUT_DIR, 'sdr_implementation_results.json')
        with open(output_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\nImplementation results saved to {output_file}")
    
    def run_implementation(self):
        """Run the complete SDR implementation process"""
        print("=== Starting SDR Implementation ===")
        print(f"Timestamp: {self.start_time}")
        
        # Ensure output directory exists
        self.create_output_directory()
        
        # Make scripts executable
        self.make_scripts_executable()
        
        # Run phases
        skill_analysis_success = self.run_skill_analysis()
        domain_classification_success = self.run_domain_relationship_classification() if skill_analysis_success else False
        matching_testing_success = self.run_matching_algorithm_testing() if domain_classification_success else False
        
        # Save results
        self.save_results()
        
        # Print completion message
        success_status = "successfully" if matching_testing_success else "with some errors"
        print(f"\n=== SDR Implementation completed {success_status} ===")
        print(f"Total duration: {datetime.now() - self.start_time}")


if __name__ == "__main__":
    runner = SDRImplementationRunner()
    runner.run_implementation()
