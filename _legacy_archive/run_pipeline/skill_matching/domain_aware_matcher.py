#!/usr/bin/env python3
"""
Domain-Aware Matching Algorithm - Uses domain relationships to improve skill matching

This script implements the domain-aware matching algorithm for the SDR framework, 
which reduces false positives by considering domain relationships instead of 
simple semantic matching.
"""

import json
import os
from collections import defaultdict

# Constants
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ENRICHED_SKILLS_PATH = os.path.join(BASE_DIR, 'docs', 'skill_matching', 'enriched_skills.json')
SKILL_RELATIONSHIPS_PATH = os.path.join(BASE_DIR, 'docs', 'skill_matching', 'skill_relationships.json')
OUTPUT_DIR = os.path.join(BASE_DIR, 'docs', 'skill_matching')

class DomainAwareMatchingAlgorithm:
    """Implements domain-aware matching for skills between job requirements and candidate profiles"""
    
    def __init__(self):
        self.enriched_skills = []
        self.skill_map = {}  # Maps skill names to their enriched definitions
        self.relationships = {}  # Relationship matrix
        self.skill_synonyms = {}  # Maps standard skill names to their synonyms
        
    def load_data(self):
        """Load the enriched skill definitions and relationships"""
        print("Loading skill data...")
        
        # Load enriched skills
        try:
            with open(ENRICHED_SKILLS_PATH, 'r') as f:
                self.enriched_skills = json.load(f)
            
            # Create a map of skill names to their definitions for easy lookup
            for skill in self.enriched_skills:
                self.skill_map[skill['name']] = skill
        except Exception as e:
            print(f"Error loading enriched skills: {e}")
        
        # Load relationship matrix
        try:
            with open(SKILL_RELATIONSHIPS_PATH, 'r') as f:
                self.relationships = json.load(f)
        except Exception as e:
            print(f"Error loading skill relationships: {e}")
        
        # Build skill synonyms (placeholder - in a real implementation, this would be more sophisticated)
        # This helps map different terms to standardized skill names
        self._build_skill_synonyms()
        
        print(f"Loaded {len(self.enriched_skills)} skills and {len(self.relationships)} relationship entries")
    
    def _build_skill_synonyms(self):
        """Build a map of skill synonyms to standardized skill names"""
        # In a real implementation, this would use NLP or a curated list
        # For demonstration, we'll just create some simple variants
        for skill_name in self.skill_map:
            # Add the original name
            self.skill_synonyms[skill_name.lower()] = skill_name
            
            # Add common variants
            variants = []
            
            # Remove spaces
            no_spaces = skill_name.replace(' ', '')
            variants.append(no_spaces.lower())
            
            # Change order of words
            words = skill_name.split()
            if len(words) > 1:
                reversed_words = ' '.join(reversed(words))
                variants.append(reversed_words.lower())
            
            # Add 'ing' form for verbs if doesn't already end with 'ing'
            if len(words) > 0 and not words[0].lower().endswith('ing'):
                gerund = words[0] + 'ing'
                gerund_variant = ' '.join([gerund] + words[1:])
                variants.append(gerund_variant.lower())
            
            # Map all variants to the original skill name
            for variant in variants:
                self.skill_synonyms[variant] = skill_name
    
    def standardize_skill(self, skill_text):
        """Map a skill text to a standardized skill name if possible"""
        # Clean and standardize the skill text
        cleaned_text = skill_text.lower().strip()
        
        # Check if it's in our synonym dictionary
        if cleaned_text in self.skill_synonyms:
            return self.skill_synonyms[cleaned_text]
        
        # Check for partial matches
        for synonym, standard_name in self.skill_synonyms.items():
            if synonym in cleaned_text or cleaned_text in synonym:
                return standard_name
        
        # If no match, return the original (could be a new skill)
        return skill_text
    
    def get_relationship(self, skill1, skill2):
        """Get the relationship between two skills"""
        # Standardize skill names
        std_skill1 = self.standardize_skill(skill1)
        std_skill2 = self.standardize_skill(skill2)
        
        # Check if we have a relationship defined
        if std_skill1 in self.relationships and std_skill2 in self.relationships[std_skill1]:
            return self.relationships[std_skill1][std_skill2]
        
        # If no relationship is defined, default to unrelated
        return {'relationship': 'Unrelated', 'similarity': 0.0}
    
    def calculate_match_score(self, job_skills, candidate_skills):
        """Calculate the match score between job skills and candidate skills"""
        if not job_skills or not candidate_skills:
            return 0.0
        
        total_score = 0.0
        matched_skills = []
        
        # For each job skill, find the best matching candidate skill
        for job_skill in job_skills:
            best_match = None
            best_score = 0.0
            
            for candidate_skill in candidate_skills:
                relationship = self.get_relationship(job_skill, candidate_skill)
                similarity = relationship.get('similarity', 0.0)
                
                # Apply relationship-based scoring
                if relationship.get('relationship') == 'Exact match':
                    score = 1.0
                elif relationship.get('relationship') == 'Subset':
                    score = 0.8
                elif relationship.get('relationship') == 'Superset':
                    score = 0.7
                elif relationship.get('relationship') == 'Neighboring':
                    score = 0.5
                elif relationship.get('relationship') == 'Hybrid':
                    score = 0.4
                else:  # Unrelated
                    score = max(0.1, similarity)  # Allow some minimal score for semantic relevance
                
                if score > best_score:
                    best_score = score
                    best_match = candidate_skill
            
            if best_match:
                total_score += best_score
                matched_skills.append({
                    'job_skill': job_skill,
                    'candidate_skill': best_match,
                    'match_score': best_score,
                    'relationship': self.get_relationship(job_skill, best_match).get('relationship', 'Unknown')
                })
        
        # Normalize score to be between 0 and 1
        max_possible_score = len(job_skills)
        normalized_score = total_score / max_possible_score if max_possible_score > 0 else 0.0
        
        return {
            'overall_score': normalized_score,
            'matched_skills': matched_skills,
            'unmatched_job_skills': [js for js in job_skills if not any(m['job_skill'] == js for m in matched_skills)]
        }
    
    def compare_job_and_candidate(self, job_id, candidate_id):
        """Compare a job posting with a candidate profile"""
        # In a real implementation, this would load actual job and candidate data
        # For demonstration, we'll use mock data
        
        job_skills = self._get_mock_job_skills(job_id)
        candidate_skills = self._get_mock_candidate_skills(candidate_id)
        
        # Calculate match using domain-aware algorithm
        domain_match = self.calculate_match_score(job_skills, candidate_skills)
        
        # For comparison, also calculate a simple semantic match (without domain awareness)
        semantic_match = self._calculate_simple_semantic_match(job_skills, candidate_skills)
        
        results = {
            'job_id': job_id,
            'candidate_id': candidate_id,
            'domain_aware_match': domain_match,
            'semantic_match': semantic_match,
            'improvement': domain_match['overall_score'] - semantic_match['overall_score'],
            'false_positives_reduced': len(semantic_match.get('false_positives', [])),
            'job_skills': job_skills,
            'candidate_skills': candidate_skills
        }
        
        return results
    
    def _calculate_simple_semantic_match(self, job_skills, candidate_skills):
        """Calculate a simple semantic match without domain awareness"""
        # This is a simplified version for comparison
        # In a real implementation, this would use actual semantic similarity
        
        matches = []
        false_positives = []
        
        for job_skill in job_skills:
            job_words = set(job_skill.lower().split())
            
            for candidate_skill in candidate_skills:
                candidate_words = set(candidate_skill.lower().split())
                
                # Simple word overlap
                overlap = len(job_words.intersection(candidate_words))
                
                if overlap > 0:
                    # This is a naive match that might include false positives
                    similarity = overlap / max(len(job_words), len(candidate_words))
                    
                    # Consider it a match if there's any word overlap
                    matches.append({
                        'job_skill': job_skill,
                        'candidate_skill': candidate_skill,
                        'score': similarity
                    })
                    
                    # Check if this would be a false positive (different domains)
                    std_job_skill = self.standardize_skill(job_skill)
                    std_candidate_skill = self.standardize_skill(candidate_skill)
                    
                    if (std_job_skill in self.skill_map and 
                        std_candidate_skill in self.skill_map and
                        self.skill_map[std_job_skill]['category'] != self.skill_map[std_candidate_skill]['category']):
                        false_positives.append({
                            'job_skill': job_skill,
                            'candidate_skill': candidate_skill,
                            'job_domain': self.skill_map[std_job_skill]['category'],
                            'candidate_domain': self.skill_map[std_candidate_skill]['category']
                        })
                        
        # Calculate overall score
        total_score = sum(match['score'] for match in matches)
        max_possible_score = len(job_skills)
        normalized_score = total_score / max_possible_score if max_possible_score > 0 else 0.0
        
        return {
            'overall_score': normalized_score,
            'matches': matches,
            'false_positives': false_positives,
            'unmatched_job_skills': [js for js in job_skills if not any(m['job_skill'] == js for m in matches)]
        }
    
    def _get_mock_job_skills(self, job_id):
        """Get mock job skills for testing"""
        # In a real implementation, this would load from the job database
        mock_jobs = {
            'job1': [
                'Python Programming', 
                'Data Analysis', 
                'Project Management', 
                'Communication Skills'
            ],
            'job2': [
                'Java Development',
                'Software Architecture',
                'Team Leadership',
                'Agile Methodologies'
            ],
            'job3': [
                'Strategic Sourcing',
                'Vendor Management',
                'Contract Negotiation',
                'Risk Assessment'
            ]
        }
        
        return mock_jobs.get(job_id, [])
    
    def _get_mock_candidate_skills(self, candidate_id):
        """Get mock candidate skills for testing"""
        # In a real implementation, this would load from the candidate database
        mock_candidates = {
            'candidate1': [
                'Python Development',
                'Statistical Analysis',
                'Team Coordination',
                'Technical Writing'
            ],
            'candidate2': [
                'Java Programming',
                'Solution Architecture',
                'Team Management',
                'Scrum Master'
            ],
            'candidate3': [
                'Procurement Strategy',
                'Supplier Relationship Management',
                'Negotiation',
                'Business Risk Management'
            ]
        }
        
        return mock_candidates.get(candidate_id, [])
    
    def run_test_comparisons(self):
        """Run test comparisons to demonstrate the algorithm"""
        print("Running test comparisons...")
        
        test_cases = [
            ('job1', 'candidate1'),  # Good match
            ('job2', 'candidate2'),  # Good match
            ('job3', 'candidate3'),  # Good match
            ('job1', 'candidate3'),  # Poor match (different domains)
            ('job2', 'candidate1'),  # Partial match
        ]
        
        results = []
        for job_id, candidate_id in test_cases:
            print(f"Comparing {job_id} with {candidate_id}...")
            comparison = self.compare_job_and_candidate(job_id, candidate_id)
            results.append(comparison)
        
        # Save results
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        output_file = os.path.join(OUTPUT_DIR, 'matching_test_results.json')
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"Test results saved to {output_file}")
        
        # Print summary
        print("\nSummary of results:")
        for result in results:
            print(f"Job {result['job_id']} and Candidate {result['candidate_id']}:")
            print(f"  Domain-aware match score: {result['domain_aware_match']['overall_score']:.2f}")
            print(f"  Semantic match score: {result['semantic_match']['overall_score']:.2f}")
            print(f"  Improvement: {result['improvement']:.2f}")
            print(f"  False positives reduced: {result['false_positives_reduced']}")
        
        return results


if __name__ == "__main__":
    matcher = DomainAwareMatchingAlgorithm()
    matcher.load_data()
    matcher.run_test_comparisons()
