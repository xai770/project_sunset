#!/usr/bin/env python3
"""
Domain Relationship Classifier - Implements domain relationship classification for the SDR framework

This script implements the domain relationship classification component of the SDR framework,
which categorizes the relationship between skills based on their domain components using
Jaccard similarity and thresholds.
"""

import json
import os
import logging
from collections import defaultdict
from typing import Dict, List, Any, Set, Tuple, Optional

# Configure logging
logger = logging.getLogger("domain_relationship_classifier")

# Constants
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ENRICHED_SKILLS_PATH = os.path.join(BASE_DIR, 'docs', 'skill_matching', 'enriched_skills.json')
OUTPUT_DIR = os.path.join(BASE_DIR, 'docs', 'skill_matching')

# Relationship types
RELATIONSHIP_TYPES = {
    'EXACT_MATCH': 'Exact match',
    'SUBSET': 'Subset',
    'SUPERSET': 'Superset',
    'NEIGHBORING': 'Neighboring',
    'UNRELATED': 'Unrelated',
    'HYBRID': 'Hybrid'
}

class DomainRelationshipClassifier:
    """Classifies relationships between skills based on their domain components"""
    
    def __init__(self):
        self.enriched_skills = []
        self.skill_map = {}  # Maps skill names to their enriched definitions
        self.relationship_matrix = defaultdict(dict)
        
    def load_enriched_skills(self):
        """Load the enriched skill definitions"""
        print("Loading enriched skill definitions...")
        
        try:
            with open(ENRICHED_SKILLS_PATH, 'r') as f:
                self.enriched_skills = json.load(f)
            
            # Create a map of skill names to their definitions for easy lookup
            for skill in self.enriched_skills:
                self.skill_map[skill['name']] = skill
                
            print(f"Loaded {len(self.enriched_skills)} enriched skill definitions")
        except Exception as e:
            print(f"Error loading enriched skill definitions: {e}")
            # Create empty file if it doesn't exist
            if not os.path.exists(ENRICHED_SKILLS_PATH):
                os.makedirs(os.path.dirname(ENRICHED_SKILLS_PATH), exist_ok=True)
                with open(ENRICHED_SKILLS_PATH, 'w') as f:
                    json.dump([], f)
    
    def calculate_jaccard_similarity(self, components1: List[str], components2: List[str]) -> float:
        """
        Calculate Jaccard similarity between two sets of components
        
        Args:
            components1: First list of components
            components2: Second list of components
            
        Returns:
            Jaccard similarity score (0.0 to 1.0)
        """
        if not components1 or not components2:
            logger.debug(f"Empty component list detected: {len(components1)} vs {len(components2)} items")
            return 0.0
            
        set1 = set(components1)
        set2 = set(components2)
        
        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))
        
        if union == 0:
            logger.debug("Union of component sets is empty")
            return 0.0
            
        similarity = intersection / union
        logger.debug(f"Jaccard similarity: {similarity:.4f} ({intersection} intersecting items out of {union} total)")
        return similarity
    
    def calculate_domain_similarity(self, skill1: str, skill2: str) -> float:
        """
        Calculate domain similarity between two skills based on their components
        
        Args:
            skill1: Name of the first skill
            skill2: Name of the second skill
            
        Returns:
            Weighted domain similarity score (0.0 to 1.0)
        """
        # Get components for each skill
        skill1_def = self.skill_map.get(skill1)
        skill2_def = self.skill_map.get(skill2)
        
        if not skill1_def or not skill2_def:
            logger.debug(f"Missing skill definition for {skill1 if not skill1_def else skill2}")
            return 0.0
        
        logger.debug(f"Calculating domain similarity between '{skill1}' and '{skill2}'")
        
        # Calculate similarity for each component type
        knowledge_similarity = self.calculate_jaccard_similarity(
            skill1_def.get('knowledge_components', []),
            skill2_def.get('knowledge_components', [])
        )
        
        context_similarity = self.calculate_jaccard_similarity(
            skill1_def.get('contexts', []),
            skill2_def.get('contexts', [])
        )
        
        function_similarity = self.calculate_jaccard_similarity(
            skill1_def.get('functions', []),
            skill2_def.get('functions', [])
        )
        
        # Weighted average (can adjust weights as needed)
        weights = {
            'knowledge': 0.4,
            'context': 0.3,
            'function': 0.3
        }
        
        # Calculate detailed component similarities for logging
        detailed_similarities = {
            'knowledge': knowledge_similarity,
            'context': context_similarity,
            'function': function_similarity
        }
        
        overall_similarity = (
            knowledge_similarity * weights['knowledge'] +
            context_similarity * weights['context'] +
            function_similarity * weights['function']
        )
        
        logger.debug(f"Component similarities: Knowledge={knowledge_similarity:.3f}, "
                    f"Context={context_similarity:.3f}, Function={function_similarity:.3f}")
        logger.debug(f"Overall domain similarity: {overall_similarity:.3f}")
        
        return overall_similarity
    
    def classify_relationship(self, skill1, skill2):
        """Classify the relationship between two skills"""
        # Calculate similarity
        similarity = self.calculate_domain_similarity(skill1, skill2)
        
        # Check if skills are in the same domain
        skill1_def = self.skill_map.get(skill1)
        skill2_def = self.skill_map.get(skill2)
        
        if not skill1_def or not skill2_def:
            return RELATIONSHIP_TYPES['UNRELATED']
        
        same_domain = skill1_def['category'] == skill2_def['category']
        
        # Classify based on thresholds
        if similarity >= 0.9:
            return RELATIONSHIP_TYPES['EXACT_MATCH']
        elif same_domain and similarity >= 0.7:
            # Check for subset/superset
            # If skill1 has more components than skill2, it's a superset
            # Otherwise, it's a subset
            skill1_component_count = sum(len(skill1_def.get(comp_type, [])) for comp_type in ['knowledge_components', 'contexts', 'functions'])
            skill2_component_count = sum(len(skill2_def.get(comp_type, [])) for comp_type in ['knowledge_components', 'contexts', 'functions'])
            
            if skill1_component_count > skill2_component_count:
                return RELATIONSHIP_TYPES['SUPERSET']
            else:
                return RELATIONSHIP_TYPES['SUBSET']
        elif same_domain and similarity >= 0.5:
            return RELATIONSHIP_TYPES['NEIGHBORING']
        elif not same_domain and similarity >= 0.5:
            return RELATIONSHIP_TYPES['HYBRID']
        else:
            return RELATIONSHIP_TYPES['UNRELATED']
    
    def classify_relationships(self, skills: List[Dict[str, Any]]) -> Dict[str, Dict[str, Dict[str, Any]]]:
        """
        Classify relationships between all skills in the provided list
        
        Args:
            skills: List of enriched skill definitions
            
        Returns:
            Dictionary of skill relationships
        """
        logger.info(f"Classifying relationships between {len(skills)} skills")
        
        # First, make sure we have the skill definitions loaded
        for skill in skills:
            self.skill_map[skill['name']] = skill
            
        self.enriched_skills = skills
        
        # Build the relationship matrix for all skills
        skill_names = list(self.skill_map.keys())
        
        # Build matrix of all skill pairs
        total_pairs = len(skill_names) * (len(skill_names) - 1)
        processed = 0
        relationship_counts: Dict[str, int] = defaultdict(int)
        
        logger.info(f"Processing {total_pairs} skill pairs")
        
        for i, skill1 in enumerate(skill_names):
            logger.debug(f"Processing relationships for skill {i+1}/{len(skill_names)}: {skill1}")
            for skill2 in skill_names:
                if skill1 != skill2:
                    relationship = self.classify_relationship(skill1, skill2)
                    similarity = self.calculate_domain_similarity(skill1, skill2)
                    
                    self.relationship_matrix[skill1][skill2] = {
                        'relationship': relationship,
                        'similarity': similarity
                    }
                    
                    relationship_counts[relationship] += 1
                    processed += 1
                    
            # Log progress periodically
            if (i+1) % 10 == 0 or i+1 == len(skill_names):
                progress = (processed / total_pairs) * 100
                logger.info(f"Progress: {progress:.1f}% ({processed}/{total_pairs} pairs)")
        
        # Log relationship distribution
        logger.info("Relationship distribution:")
        for rel_type, count in relationship_counts.items():
            percentage = (count / total_pairs) * 100
            logger.info(f"  - {rel_type}: {count} ({percentage:.1f}%)")
        
        logger.info(f"Relationship classification completed. {len(self.relationship_matrix)} skills in relationship matrix.")
        return dict(self.relationship_matrix)
    
    def build_relationship_matrix(self):
        """Build a matrix of relationships between all skills"""
        print("Building relationship matrix...")
        skill_names = list(self.skill_map.keys())
        
        # Build matrix of all skill pairs
        for i, skill1 in enumerate(skill_names):
            print(f"Processing skill {i+1}/{len(skill_names)}: {skill1}")
            for skill2 in skill_names:
                if skill1 != skill2:
                    relationship = self.classify_relationship(skill1, skill2)
                    similarity = self.calculate_domain_similarity(skill1, skill2)
                    
                    self.relationship_matrix[skill1][skill2] = {
                        'relationship': relationship,
                        'similarity': similarity
                    }
        
        print("Relationship matrix completed")
    
    def save_relationship_matrix(self):
        """Save the relationship matrix to a file"""
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        output_file = os.path.join(OUTPUT_DIR, 'skill_relationships.json')
        
        with open(output_file, 'w') as f:
            json.dump(dict(self.relationship_matrix), f, indent=2)
        
        print(f"Relationship matrix saved to {output_file}")
    
    def run_classification(self):
        """Run the complete domain relationship classification"""
        self.load_enriched_skills()
        self.build_relationship_matrix()
        self.save_relationship_matrix()
        
        return self.relationship_matrix


if __name__ == "__main__":
    classifier = DomainRelationshipClassifier()
    classifier.run_classification()
