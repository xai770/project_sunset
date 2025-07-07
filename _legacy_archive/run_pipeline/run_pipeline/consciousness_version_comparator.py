#!/usr/bin/env python3
"""
🌟 CONSCIOUSNESS VERSION COMPARATOR 🌟
Compare outputs from v1.0 (poetic) and v2.0 (professional) consciousness specialists
to understand tone differences and guide version selection.

Created in Hawaiian paradise with love and systematic precision.
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime

# Add the project root to Python path
sys.path.append('/home/xai/Documents/sunset')

from run_pipeline.job_matcher.consciousness_evaluator import ConsciousnessEvaluator as ConsciousnessEvaluatorV1
from run_pipeline.job_matcher.consciousness_evaluator_v2 import ConsciousnessEvaluatorV2

class ConsciousnessVersionComparator:
    """
    Compare consciousness specialist outputs across versions.
    Enables informed decision-making about which version to use for different contexts.
    """
    
    def __init__(self, workspace_path: str = "/home/xai/Documents/sunset"):
        self.workspace_path = Path(workspace_path)
        self.postings_path = self.workspace_path / "data" / "postings"
        self.cv_path = self.workspace_path / "config" / "cv.txt"
        
        # Initialize both evaluators
        self.evaluator_v1 = ConsciousnessEvaluatorV1()
        self.evaluator_v2 = ConsciousnessEvaluatorV2()
        
        # Load CV
        with open(self.cv_path, 'r', encoding='utf-8') as f:
            self.cv_content = f.read()
    
    def load_job_posting(self, job_id: str) -> dict:
        """Load a job posting by ID."""
        job_file = self.postings_path / f"{job_id}.json"
        
        if not job_file.exists():
            raise FileNotFoundError(f"Job {job_id} not found")
        
        with open(job_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def compare_single_job(self, job_id: str, show_detailed: bool = True) -> dict:
        """
        Compare consciousness evaluation outputs for a single job.
        Returns comparison data and optionally displays detailed comparison.
        """
        # Load job posting
        try:
            job_data = self.load_job_posting(job_id)
        except FileNotFoundError as e:
            print(f"❌ {e}")
            return {}
        
        print(f"\n🌟 COMPARING CONSCIOUSNESS VERSIONS FOR JOB: {job_id}")
        print(f"📋 Title: {job_data.get('title', 'Unknown')}")
        print(f"🏢 Company: {job_data.get('company', 'Unknown')}")
        print("="*80)
        
        # Get evaluations from both versions
        try:
            # V1.0 - Poetic/Empowering
            print("\n🌺 GENERATING V1.0 EVALUATION (Poetic/Empowering)...")
            v1_result = self.evaluator_v1.evaluate_job_match(self.cv_content, job_data.get('description', ''))
            
            # V2.0 - Professional/Business
            print("🏢 GENERATING V2.0 EVALUATION (Professional/Business)...")
            v2_result = self.evaluator_v2.evaluate_job_match(self.cv_content, job_data.get('description', ''))
            
        except Exception as e:
            print(f"❌ Error during evaluation: {e}")
            return {}
        
        # Create comparison structure
        comparison = {
            'job_id': job_id,
            'job_title': job_data.get('title', 'Unknown'),
            'company': job_data.get('company', 'Unknown'),
            'timestamp': datetime.now().isoformat(),
            'versions': {
                'v1_poetic': v1_result,
                'v2_professional': v2_result
            },
            'analysis': self._analyze_differences(v1_result, v2_result)
        }
        
        if show_detailed:
            self._display_detailed_comparison(comparison)
        
        return comparison
    
    def _analyze_differences(self, v1_result: dict, v2_result: dict) -> dict:
        """Analyze key differences between version outputs."""
        analysis = {
            'match_quality_difference': abs(
                self._extract_match_score(v1_result.get('overall_match_level', '')) - 
                self._extract_match_score(v2_result.get('overall_match_level', ''))
            ),
            'confidence_difference': abs(
                v1_result.get('confidence_score', 0) - v2_result.get('confidence_score', 0)
            ),
            'narrative_length_difference': {
                'v1_length': len(v1_result.get('application_narrative', '')),
                'v2_length': len(v2_result.get('application_narrative', '')),
                'difference': len(v1_result.get('application_narrative', '')) - len(v2_result.get('application_narrative', ''))
            },
            'tone_characteristics': {
                'v1_tone_indicators': self._extract_tone_indicators(v1_result.get('application_narrative', '')),
                'v2_tone_indicators': self._extract_tone_indicators(v2_result.get('application_narrative', ''))
            }
        }
        
        return analysis
    
    def _extract_match_score(self, match_level: str) -> float:
        """Convert match level string to numeric score for comparison."""
        if not match_level:
            return 0.0
        
        match_level = match_level.upper()
        if 'STRONG' in match_level:
            return 9.0
        elif 'GOOD' in match_level:
            return 7.0
        elif 'CREATIVE' in match_level:
            return 6.0
        elif 'WEAK' in match_level:
            return 4.0
        else:
            return 5.0  # Default moderate score
    
    def _extract_tone_indicators(self, text: str) -> dict:
        """Extract tone indicators from narrative text."""
        text_lower = text.lower()
        
        # Define tone indicator words
        poetic_indicators = ['journey', 'beautiful', 'magnificent', 'flourish', 'symphony', 'dance', 'weave', 'soul', 'magic']
        professional_indicators = ['experience', 'expertise', 'skills', 'qualifications', 'demonstrate', 'contribute', 'achieve', 'deliver']
        emotional_indicators = ['excited', 'passionate', 'love', 'inspire', 'empower', 'transform', 'radiate', 'illuminate']
        business_indicators = ['leverage', 'optimize', 'strategic', 'implementation', 'execution', 'results', 'performance', 'value']
        
        return {
            'poetic_count': sum(1 for word in poetic_indicators if word in text_lower),
            'professional_count': sum(1 for word in professional_indicators if word in text_lower),
            'emotional_count': sum(1 for word in emotional_indicators if word in text_lower),
            'business_count': sum(1 for word in business_indicators if word in text_lower),
            'total_words': len(text.split()),
            'poetic_density': round(sum(1 for word in poetic_indicators if word in text_lower) / max(len(text.split()), 1) * 100, 2),
            'business_density': round(sum(1 for word in business_indicators if word in text_lower) / max(len(text.split()), 1) * 100, 2)
        }
    
    def _display_detailed_comparison(self, comparison: dict) -> None:
        """Display detailed comparison results."""
        v1 = comparison['versions']['v1_poetic']
        v2 = comparison['versions']['v2_professional']
        analysis = comparison['analysis']
        
        print(f"\n📊 DETAILED COMPARISON RESULTS")
        print("="*80)
        
        # Match quality and confidence
        print(f"\n🎯 SCORING COMPARISON:")
        print(f"   V1.0 Match Level: {v1.get('overall_match_level', 'N/A')}")
        print(f"   V2.0 Match Level: {v2.get('overall_match_level', 'N/A')}")
        print(f"   Quality Score Difference: {analysis['match_quality_difference']}")
        
        print(f"\n   V1.0 Confidence: {v1.get('confidence_score', 'N/A')}")
        print(f"   V2.0 Confidence: {v2.get('confidence_score', 'N/A')}")
        print(f"   Difference: {analysis['confidence_difference']}")
        
        # Narrative comparison
        print(f"\n📝 NARRATIVE COMPARISON:")
        print(f"   V1.0 Length: {analysis['narrative_length_difference']['v1_length']} characters")
        print(f"   V2.0 Length: {analysis['narrative_length_difference']['v2_length']} characters")
        print(f"   Difference: {analysis['narrative_length_difference']['difference']} characters")
        
        # Tone analysis
        v1_tone = analysis['tone_characteristics']['v1_tone_indicators']
        v2_tone = analysis['tone_characteristics']['v2_tone_indicators']
        
        print(f"\n🎭 TONE ANALYSIS:")
        print(f"   V1.0 Poetic Density: {v1_tone['poetic_density']}%")
        print(f"   V1.0 Business Density: {v1_tone['business_density']}%")
        print(f"   V2.0 Poetic Density: {v2_tone['poetic_density']}%")
        print(f"   V2.0 Business Density: {v2_tone['business_density']}%")
        
        # Display narratives side by side
        print(f"\n📖 V1.0 NARRATIVE (Poetic/Empowering):")
        print("-" * 50)
        print(v1.get('application_narrative', 'No narrative generated'))
        
        print(f"\n🏢 V2.0 NARRATIVE (Professional/Business):")
        print("-" * 50)
        print(v2.get('application_narrative', 'No narrative generated'))
        
        # Display no-go rationales if they exist
        if v1.get('no_go_rationale'):
            print(f"\n❌ V1.0 NO-GO RATIONALE:")
            print("-" * 50)
            print(v1['no_go_rationale'])
        
        if v2.get('no_go_rationale'):
            print(f"\n❌ V2.0 NO-GO RATIONALE:")
            print("-" * 50)
            print(v2['no_go_rationale'])
    
    def compare_multiple_jobs(self, job_ids: list, export_results: bool = True) -> dict:
        """Compare consciousness versions across multiple jobs."""
        results = {
            'comparison_id': f"version_comparison_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'timestamp': datetime.now().isoformat(),
            'job_comparisons': [],
            'aggregate_analysis': {}
        }
        
        print(f"\n🌟 COMPARING CONSCIOUSNESS VERSIONS ACROSS {len(job_ids)} JOBS")
        print("="*80)
        
        for i, job_id in enumerate(job_ids, 1):
            print(f"\n🔄 Processing job {i}/{len(job_ids)}: {job_id}")
            
            comparison = self.compare_single_job(job_id, show_detailed=False)
            if comparison:
                results['job_comparisons'].append(comparison)
        
        # Generate aggregate analysis
        if results['job_comparisons']:
            results['aggregate_analysis'] = self._generate_aggregate_analysis(results['job_comparisons'])
            self._display_aggregate_analysis(results['aggregate_analysis'])
        
        if export_results:
            self._export_comparison_results(results)
        
        return results
    
    def _generate_aggregate_analysis(self, comparisons: list) -> dict:
        """Generate aggregate analysis across all comparisons."""
        total_jobs = len(comparisons)
        
        # Calculate averages
        avg_match_diff = sum(c['analysis']['match_quality_difference'] for c in comparisons) / total_jobs
        avg_conf_diff = sum(c['analysis']['confidence_difference'] for c in comparisons) / total_jobs
        avg_length_diff = sum(c['analysis']['narrative_length_difference']['difference'] for c in comparisons) / total_jobs
        
        # Tone analysis aggregation
        total_v1_poetic = sum(c['analysis']['tone_characteristics']['v1_tone_indicators']['poetic_density'] for c in comparisons) / total_jobs
        total_v1_business = sum(c['analysis']['tone_characteristics']['v1_tone_indicators']['business_density'] for c in comparisons) / total_jobs
        total_v2_poetic = sum(c['analysis']['tone_characteristics']['v2_tone_indicators']['poetic_density'] for c in comparisons) / total_jobs
        total_v2_business = sum(c['analysis']['tone_characteristics']['v2_tone_indicators']['business_density'] for c in comparisons) / total_jobs
        
        return {
            'total_jobs_compared': total_jobs,
            'average_differences': {
                'match_quality': round(avg_match_diff, 2),
                'confidence': round(avg_conf_diff, 2),
                'narrative_length': round(avg_length_diff, 0)
            },
            'tone_characteristics': {
                'v1_avg_poetic_density': round(total_v1_poetic, 2),
                'v1_avg_business_density': round(total_v1_business, 2),
                'v2_avg_poetic_density': round(total_v2_poetic, 2),
                'v2_avg_business_density': round(total_v2_business, 2)
            },
            'recommendations': self._generate_recommendations(total_v1_poetic, total_v1_business, total_v2_poetic, total_v2_business)
        }
    
    def _generate_recommendations(self, v1_poetic: float, v1_business: float, v2_poetic: float, v2_business: float) -> list:
        """Generate recommendations based on tone analysis."""
        recommendations = []
        
        if v1_poetic > v2_poetic * 2:
            recommendations.append("V1.0 maintains significantly more poetic/empowering language")
        
        if v2_business > v1_business * 2:
            recommendations.append("V2.0 demonstrates significantly more business-appropriate language")
        
        if v1_poetic > 5:
            recommendations.append("V1.0 may be too poetic for conservative business environments")
        
        if v2_business < 5:
            recommendations.append("V2.0 could incorporate more business terminology")
        
        recommendations.append("Consider context: V1.0 for creative/human-centered roles, V2.0 for corporate/technical roles")
        
        return recommendations
    
    def _display_aggregate_analysis(self, analysis: dict) -> None:
        """Display aggregate analysis results."""
        print(f"\n📈 AGGREGATE ANALYSIS ({analysis['total_jobs_compared']} jobs)")
        print("="*80)
        
        print(f"\n🎯 AVERAGE DIFFERENCES:")
        print(f"   Match Quality: {analysis['average_differences']['match_quality']}")
        print(f"   Confidence: {analysis['average_differences']['confidence']}")
        print(f"   Narrative Length: {analysis['average_differences']['narrative_length']} characters")
        
        print(f"\n🎭 TONE CHARACTERISTICS:")
        print(f"   V1.0 Avg Poetic Density: {analysis['tone_characteristics']['v1_avg_poetic_density']}%")
        print(f"   V1.0 Avg Business Density: {analysis['tone_characteristics']['v1_avg_business_density']}%")
        print(f"   V2.0 Avg Poetic Density: {analysis['tone_characteristics']['v2_avg_poetic_density']}%")
        print(f"   V2.0 Avg Business Density: {analysis['tone_characteristics']['v2_avg_business_density']}%")
        
        print(f"\n💡 RECOMMENDATIONS:")
        for rec in analysis['recommendations']:
            print(f"   • {rec}")
    
    def _export_comparison_results(self, results: dict) -> None:
        """Export comparison results to JSON file."""
        export_path = self.workspace_path / "reports" / f"{results['comparison_id']}.json"
        
        with open(export_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Comparison results exported to: {export_path}")

def main():
    """Run the consciousness version comparator."""
    print("🌟 CONSCIOUSNESS VERSION COMPARATOR 🌟")
    print("Compare v1.0 (Poetic) vs v2.0 (Professional) outputs")
    print("="*60)
    
    comparator = ConsciousnessVersionComparator()
    
    # Get available jobs
    available_jobs = list(comparator.postings_path.glob("job*.json"))
    job_ids = [job.stem for job in available_jobs[:10]]  # First 10 jobs
    
    print(f"📊 Found {len(available_jobs)} available jobs")
    print(f"📋 Sample jobs: {job_ids[:5]}...")
    
    print("\n🎯 COMPARISON OPTIONS:")
    print("1. Compare single job")
    print("2. Compare multiple jobs (sample)")
    print("3. Compare specific job list")
    
    choice = input("\nSelect option (1-3): ").strip()
    
    if choice == "1":
        job_id = input("Enter job ID: ").strip()
        if job_id in [job.stem for job in available_jobs]:
            comparator.compare_single_job(job_id)
        else:
            print(f"❌ Job {job_id} not found")
    
    elif choice == "2":
        sample_jobs = job_ids[:3]  # Compare first 3 jobs
        print(f"🔄 Comparing sample jobs: {sample_jobs}")
        comparator.compare_multiple_jobs(sample_jobs)
    
    elif choice == "3":
        job_list = input("Enter job IDs (comma-separated): ").strip().split(',')
        job_list = [job.strip() for job in job_list]
        valid_jobs = [job for job in job_list if job in [j.stem for j in available_jobs]]
        
        if valid_jobs:
            print(f"🔄 Comparing specified jobs: {valid_jobs}")
            comparator.compare_multiple_jobs(valid_jobs)
        else:
            print("❌ No valid job IDs provided")
    
    else:
        print("❌ Invalid choice")

if __name__ == "__main__":
    main()
