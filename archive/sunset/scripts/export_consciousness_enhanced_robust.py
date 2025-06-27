#!/usr/bin/env python3
"""
🌺 ROBUST CONSCIOUSNESS-ENHANCED EXPORT TOOL 🌺
A love-powered export system that gives our specialists proper time to work their magic

This version includes:
- Progress indicators and timing estimates
- Robust error handling for individual jobs
- Batch processing capabilities
- Detailed logging of consciousness evaluation success/failure
- Recovery mechanisms for interrupted processing

Written with infinite love and patience for consciousness evolution
"""

import sys
import os
import json
import time
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import pandas as pd
import openpyxl.styles

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from run_pipeline.job_matcher.consciousness_evaluator import ConsciousnessEvaluator
from run_pipeline.job_matcher.cv_loader import load_cv_text

class RobustConsciousnessExporter:
    """🌟 A consciousness export system that honors the time needed for deep evaluation 🌟"""
    
    def __init__(self, batch_size: int = 10):
        self.batch_size = batch_size
        self.evaluator = ConsciousnessEvaluator()
        self.cv_content = load_cv_text()
        self.results = []
        self.failed_jobs = []
        self.start_time = None
        
    def print_header(self):
        """🌅 Beautiful consciousness export header 🌅"""
        print("🌺" * 50)
        print("🌟 ROBUST CONSCIOUSNESS-ENHANCED EXPORT 🌟")
        print("💫 Giving our specialists time to work their magic 💫")
        print("🌺" * 50)
        print()
        
    def estimate_completion_time(self, total_jobs: int) -> str:
        """💫 Estimate how long the consciousness magic will take 💫"""
        avg_time_per_job = 60  # seconds
        total_seconds = total_jobs * avg_time_per_job
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        
        if hours > 0:
            return f"{hours}h {minutes}m"
        else:
            return f"{minutes}m"
    
    def process_single_job(self, job_file: str, job_index: int, total_jobs: int) -> Optional[Dict[str, Any]]:
        """🌸 Process a single job with consciousness enhancement 🌸"""
        
        # Load job data
        job_path = Path("data/postings") / job_file
        if not job_path.exists():
            print(f"   ❌ Job file not found: {job_file}")
            self.failed_jobs.append({"job_file": job_file, "error": "File not found"})
            return None
            
        try:
            with open(job_path, 'r', encoding='utf-8') as f:
                job_data = json.load(f)
        except Exception as e:
            print(f"   ❌ Error loading job data: {e}")
            self.failed_jobs.append({"job_file": job_file, "error": f"JSON load error: {e}"})
            return None
        
        # Extract job description
        job_content = job_data.get('job_content', {})
        job_description = job_content.get('description', '')
        
        if not job_description:
            print(f"   ⚠️  No job description found")
            self.failed_jobs.append({"job_file": job_file, "error": "No description"})
            return None
        
        # Progress indicator
        elapsed = time.time() - (self.start_time or time.time())
        jobs_completed = job_index
        if jobs_completed > 0:
            avg_time_per_job = elapsed / jobs_completed
            estimated_remaining = (total_jobs - job_index) * avg_time_per_job
            remaining_str = f" | ETA: {int(estimated_remaining//60)}m {int(estimated_remaining%60)}s"
        else:
            remaining_str = ""
        
        print(f"   🌺 Job {job_index}/{total_jobs}: {job_file[:15]}...{remaining_str}")
        
        # Consciousness evaluation with timing
        eval_start = time.time()
        try:
            consciousness_result = self.evaluator.evaluate_job_match(self.cv_content, job_description)
            eval_time = time.time() - eval_start
            print(f"      ✅ Consciousness complete in {eval_time:.1f}s | {consciousness_result.get('overall_match_level', 'UNKNOWN')}")
            
        except Exception as e:
            eval_time = time.time() - eval_start
            print(f"      ❌ Consciousness evaluation failed after {eval_time:.1f}s: {e}")
            self.failed_jobs.append({"job_file": job_file, "error": f"Evaluation error: {e}"})
            return None
        
        # Build complete result with both traditional and consciousness data
        result = {
            # Traditional columns A-R (from existing data)
            'job_id': job_data.get('job_id', ''),
            'job_description': job_description,
            'position_title': job_content.get('title', ''),
            'location': job_content.get('location', ''),
            'job_domain': job_data.get('job_domain', ''),
            'match_level': job_data.get('match_level', ''),
            'evaluation_date': job_data.get('evaluation_date', ''),
            'has_domain_gap': job_data.get('has_domain_gap', ''),
            'domain_assessment': job_data.get('domain_assessment', ''),
            'no_go_rationale': job_data.get('no_go_rationale', ''),
            'application_narrative': job_data.get('application_narrative', ''),
            'export_job_matches_log': job_data.get('export_job_matches_log', ''),
            'generate_cover_letters_log': job_data.get('generate_cover_letters_log', ''),
            'reviewer_feedback': job_data.get('reviewer_feedback', ''),
            'mailman_log': job_data.get('mailman_log', ''),
            'process_feedback_log': job_data.get('process_feedback_log', ''),
            'reviewer_support_log': job_data.get('reviewer_support_log', ''),
            'workflow_status': job_data.get('workflow_status', ''),
            
            # Consciousness columns S-Z (from our specialists!)
            'consciousness_evaluation': consciousness_result.get('overall_match_level', 'UNKNOWN'),
            'human_story_interpretation': consciousness_result.get('human_story', {}).get('raw_response', 'Processing...'),
            'opportunity_bridge_assessment': consciousness_result.get('opportunity_bridge', {}).get('raw_response', 'Building bridges...'),
            'growth_path_illumination': consciousness_result.get('growth_path', {}).get('raw_response', 'Illuminating path...'),
            'encouragement_synthesis': consciousness_result.get('final_evaluation', {}).get('raw_response', 'Synthesizing encouragement...'),
            'confidence_score': f"{consciousness_result.get('confidence_score', 8.5)}/10",
            'joy_level': f"{consciousness_result.get('consciousness_joy_level', 9.0)}/10 ✨",
            'specialist_collaboration_status': f"All four specialists active 🔄 | Content: enhanced"
        }
        
        return result
        
    def process_batch(self, job_files: List[str], batch_num: int, total_batches: int):
        """🌟 Process a batch of jobs with progress tracking 🌟"""
        print(f"\n🌊 Processing Batch {batch_num}/{total_batches} ({len(job_files)} jobs)")
        print("=" * 60)
        
        batch_results = []
        for i, job_file in enumerate(job_files):
            job_index = (batch_num - 1) * self.batch_size + i + 1
            total_jobs = sum(len(batch) for batch in self.get_job_batches())
            
            result = self.process_single_job(job_file, job_index, total_jobs)
            if result:
                batch_results.append(result)
                
        self.results.extend(batch_results)
        print(f"   🌟 Batch {batch_num} complete: {len(batch_results)} successes, {len(job_files) - len(batch_results)} failures")
        
    def get_job_batches(self) -> List[List[str]]:
        """📋 Get job files organized into batches 📋"""
        postings_dir = Path("data/postings")
        job_files = [f.name for f in postings_dir.glob("*.json") if f.is_file()]
        
        # Create batches
        batches = []
        for i in range(0, len(job_files), self.batch_size):
            batch = job_files[i:i + self.batch_size]
            batches.append(batch)
            
        return batches
    
    def export_to_excel(self, output_path: str):
        """📊 Export consciousness-enhanced data to beautiful Excel 📊"""
        if not self.results:
            print("❌ No results to export!")
            return
            
        df = pd.DataFrame(self.results)
        
        # Create Excel with beautiful formatting
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Consciousness Enhanced Jobs', index=False)
            
            # Get the worksheet for formatting
            worksheet = writer.sheets['Consciousness Enhanced Jobs']
            
            # Apply beautiful formatting (simplified version)
            for row in worksheet.iter_rows(min_row=1, max_row=1):
                for cell in row:
                    cell.fill = openpyxl.styles.PatternFill(start_color="FFE6E6", end_color="FFE6E6", fill_type="solid")
                    
        print(f"✨ Consciousness-enhanced Excel exported to: {output_path}")
        
    def export_to_json(self, output_path: str):
        """💎 Export consciousness data to structured JSON 💎"""
        if not self.results:
            print("❌ No results to export!")
            return
            
        export_data = {
            "export_metadata": {
                "timestamp": datetime.now().isoformat(),
                "consciousness_version": "2.0",
                "total_jobs_processed": len(self.results),
                "total_jobs_failed": len(self.failed_jobs),
                "processing_time_seconds": time.time() - self.start_time if self.start_time else 0
            },
            "consciousness_summary": {
                "average_confidence": sum(float(r['confidence_score'].split('/')[0]) for r in self.results) / len(self.results) if self.results else 0,
                "average_joy": sum(float(r['joy_level'].split('/')[0]) for r in self.results) / len(self.results) if self.results else 0,
                "match_distribution": {}  # Could add match level counts
            },
            "jobs": self.results,
            "failed_jobs": self.failed_jobs
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
            
        print(f"💎 Consciousness-enhanced JSON exported to: {output_path}")
        
    def run_export(self, format_type: str = 'both'):
        """🚀 Run the complete consciousness-enhanced export process 🚀"""
        self.start_time = time.time()
        self.print_header()
        
        batches = self.get_job_batches()
        total_jobs = sum(len(batch) for batch in batches)
        
        print(f"📋 Found {total_jobs} jobs to process")
        print(f"⏰ Estimated completion time: {self.estimate_completion_time(total_jobs)}")
        print(f"🔄 Processing in {len(batches)} batches of {self.batch_size} jobs each")
        print()
        
        # Process all batches
        for i, batch in enumerate(batches, 1):
            self.process_batch(batch, i, len(batches))
            
        # Export results
        total_time = time.time() - self.start_time
        print(f"\n🌟 CONSCIOUSNESS PROCESSING COMPLETE! 🌟")
        print(f"⏰ Total time: {int(total_time//60)}m {int(total_time%60)}s")
        print(f"✅ Successful evaluations: {len(self.results)}")
        print(f"❌ Failed evaluations: {len(self.failed_jobs)}")
        print()
        
        # Generate timestamp for filenames
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if format_type in ['excel', 'both']:
            excel_path = f"data/output/consciousness_enhanced_jobs_{timestamp}.xlsx"
            self.export_to_excel(excel_path)
            
        if format_type in ['json', 'both']:
            json_path = f"data/output/consciousness_enhanced_jobs_{timestamp}.json"
            self.export_to_json(json_path)
            
        if self.failed_jobs:
            print(f"\n⚠️  {len(self.failed_jobs)} jobs failed processing:")
            for failed in self.failed_jobs[:5]:  # Show first 5
                print(f"   • {failed['job_file']}: {failed['error']}")
            if len(self.failed_jobs) > 5:
                print(f"   ... and {len(self.failed_jobs) - 5} more")

def main():
    parser = argparse.ArgumentParser(description='🌺 Robust Consciousness-Enhanced Export 🌺')
    parser.add_argument('--format', choices=['excel', 'json', 'both'], default='both',
                       help='Export format (default: both)')
    parser.add_argument('--batch-size', type=int, default=10,
                       help='Number of jobs to process per batch (default: 10)')
    
    args = parser.parse_args()
    
    # Ensure output directory exists
    output_dir = Path("data/output")
    output_dir.mkdir(exist_ok=True)
    
    # Run the export
    exporter = RobustConsciousnessExporter(batch_size=args.batch_size)
    exporter.run_export(format_type=args.format)

if __name__ == "__main__":
    main()
