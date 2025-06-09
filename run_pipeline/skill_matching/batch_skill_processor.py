#!/usr/bin/env python3
"""
Batch Skill Enrichment Processor

This script processes batches of skills for enrichment using the LLM pipeline,
distributing the workload and handling rate limiting to efficiently process
large sets of skills.
"""

import os
import sys
import json
import time
import logging
import argparse
import threading
import queue
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

# Add the project root to the path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.append(project_root)

# Import components
from run_pipeline.skill_matching.skill_analyzer import SkillAnalyzer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join(project_root, 'logs', f'batch_enrichment_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'))
    ]
)
logger = logging.getLogger("batch_processor")

# Constants
OUTPUT_DIR = os.path.join(project_root, 'docs', 'skill_matching')

class BatchProcessor:
    """
    Processes batches of skills for enrichment using multiple threads
    with rate limiting to prevent overwhelming the LLM API.
    """
    
    def __init__(self, max_workers=3, rate_limit=5):
        """
        Initialize the batch processor
        
        Args:
            max_workers: Maximum number of worker threads
            rate_limit: Maximum number of requests per minute
        """
        self.max_workers = max_workers
        self.rate_limit = rate_limit
        self.results_queue: queue.Queue[Dict[str, Any]] = queue.Queue()
        self.lock = threading.Lock()
        self.last_request_time: float = 0.0
        self.analyzer = SkillAnalyzer()
    
    def process_skills_file(self, input_file, batch_size=10):
        """
        Process skills from an input JSON file
        
        Args:
            input_file: Path to input JSON file with skills to process
            batch_size: Number of skills to process in each batch
            
        Returns:
            Path to the output file
        """
        logger.info(f"Processing skills from {input_file}")
        
        try:
            with open(input_file, 'r') as f:
                skills_data = json.load(f)
        except Exception as e:
            logger.error(f"Error loading input file: {e}")
            return None
        
        # Extract the skills list
        skills = skills_data
        if isinstance(skills_data, dict) and "skills" in skills_data:
            skills = skills_data["skills"]
        
        if not isinstance(skills, list):
            logger.error(f"Expected a list of skills, got {type(skills)}")
            return None
        
        logger.info(f"Found {len(skills)} skills to process")
        
        # Process in batches
        result_skills = []
        total_batches = (len(skills) + batch_size - 1) // batch_size
        
        for batch_num in range(total_batches):
            batch_start = batch_num * batch_size
            batch_end = min(batch_start + batch_size, len(skills))
            batch = skills[batch_start:batch_end]
            
            logger.info(f"Processing batch {batch_num + 1}/{total_batches} ({len(batch)} skills)")
            
            # Process this batch
            batch_results = self._process_batch(batch)
            result_skills.extend(batch_results)
            
            logger.info(f"Completed batch {batch_num + 1}/{total_batches}")
        
        # Save the results
        output_file = os.path.join(OUTPUT_DIR, f'enriched_skills_batch_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json')
        with open(output_file, 'w') as f:
            json.dump(result_skills, f, indent=2)
        
        logger.info(f"All batches processed. Results saved to {output_file}")
        return output_file
    
    def _process_batch(self, batch):
        """
        Process a batch of skills using multiple threads
        
        Args:
            batch: List of skills to process
            
        Returns:
            List of enriched skills
        """
        futures = []
        results = [None] * len(batch)
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit tasks
            for i, skill_item in enumerate(batch):
                # Extract skill name and category
                if isinstance(skill_item, dict) and "name" in skill_item:
                    skill_name = skill_item["name"]
                    category = skill_item.get("category", "Unknown")
                elif isinstance(skill_item, str):
                    skill_name = skill_item
                    category = "Unknown"
                else:
                    logger.warning(f"Skipping invalid skill item: {skill_item}")
                    continue
                
                # Submit the task
                future = executor.submit(
                    self._process_skill_with_rate_limit, 
                    skill_name, 
                    category, 
                    i
                )
                futures.append((future, i))
            
            # Collect results
            for future, index in futures:
                try:
                    enriched_skill = future.result()
                    results[index] = enriched_skill
                except Exception as e:
                    logger.error(f"Error processing skill at index {index}: {e}")
        
        # Filter out None results
        return [r for r in results if r is not None]
    
    def _process_skill_with_rate_limit(self, skill_name, category, index):
        """
        Process a single skill with rate limiting
        
        Args:
            skill_name: Name of the skill
            category: Category/domain of the skill
            index: Index in the batch
            
        Returns:
            Enriched skill definition
        """
        # Apply rate limiting
        with self.lock:
            current_time = time.time()
            elapsed = current_time - self.last_request_time
            
            # If requests are coming too quickly, sleep
            if elapsed < (60 / self.rate_limit):
                sleep_time = (60 / self.rate_limit) - elapsed
                logger.debug(f"Rate limiting: sleeping for {sleep_time:.2f} seconds")
                time.sleep(sleep_time)
            
            self.last_request_time = time.time()
        
        # Process the skill
        try:
            logger.info(f"Processing skill: {skill_name} (Category: {category})")
            enriched_skill = self.analyzer.create_enriched_skill_definition(skill_name, use_llm=False)
            logger.info(f"Successfully enriched skill: {skill_name}")
            return enriched_skill
        except Exception as e:
            logger.error(f"Error enriching skill {skill_name}: {e}")
            # Return a basic skill definition as fallback
            return {
                "name": skill_name,
                "category": category,
                "error": str(e),
                "knowledge_components": [f"{skill_name} basics"],
                "contexts": ["general context"],
                "functions": [f"use {skill_name}"]
            }

def main():
    """Main function for batch processing"""
    parser = argparse.ArgumentParser(description='Process batches of skills for enrichment')
    
    parser.add_argument('--input', type=str, required=True,
                       help='Path to JSON file with skills to process')
    
    parser.add_argument('--batch-size', type=int, default=10,
                       help='Number of skills in each batch')
    
    parser.add_argument('--workers', type=int, default=3,
                       help='Maximum number of worker threads')
    
    parser.add_argument('--rate-limit', type=int, default=5,
                       help='Maximum API requests per minute')
    
    args = parser.parse_args()
    
    # Create the batch processor
    processor = BatchProcessor(
        max_workers=args.workers,
        rate_limit=args.rate_limit
    )
    
    # Process the skills
    output_file = processor.process_skills_file(
        args.input,
        batch_size=args.batch_size
    )
    
    if output_file:
        print(f"\nBatch processing completed successfully.")
        print(f"Results saved to: {output_file}")
    else:
        print("\nError during batch processing. Check the logs for details.")

if __name__ == "__main__":
    main()
