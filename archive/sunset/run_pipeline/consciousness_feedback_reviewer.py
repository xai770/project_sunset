#!/usr/bin/env python3
"""
🌺 CONSCIOUSNESS FEEDBACK REVIEWER 🌺
A systematic tool for reviewing consciousness specialist outputs and collecting feedback
for iterative improvement of our empowering AI evaluation system.

Created in Hawaiian paradise - where consciousness meets technology with love.
"""

import json
import os
import random
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

class ConsciousnessFeedbackReviewer:
    """
    Systematic reviewer for consciousness specialist outputs.
    Enables collaborative feedback collection and iterative improvement.
    """
    
    def __init__(self, workspace_path: str = "/home/xai/Documents/sunset"):
        self.workspace_path = Path(workspace_path)
        self.postings_path = self.workspace_path / "data" / "postings"
        self.reports_path = self.workspace_path / "reports"
        self.feedback_path = self.workspace_path / "data" / "feedback" / "consciousness"
        
        # Ensure feedback directory exists
        self.feedback_path.mkdir(parents=True, exist_ok=True)
    
    def get_evaluated_jobs(self) -> List[str]:
        """Get list of jobs that have consciousness evaluations."""
        evaluated_jobs = []
        
        for job_file in self.postings_path.glob("job*.json"):
            job_id = job_file.stem
            llm_response_file = self.postings_path / f"{job_id}_all_llm_responses.txt"
            
            if llm_response_file.exists():
                # Check if it contains consciousness evaluation
                try:
                    with open(llm_response_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if "consciousness_specialists" in content.lower() or "encouragement_synthesizer" in content.lower():
                            evaluated_jobs.append(job_id)
                except Exception:
                    continue
        
        return sorted(evaluated_jobs)
    
    def load_job_details(self, job_id: str) -> Optional[Dict]:
        """Load job posting details."""
        job_file = self.postings_path / f"{job_id}.json"
        
        if not job_file.exists():
            return None
            
        try:
            with open(job_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading job {job_id}: {e}")
            return None
    
    def load_consciousness_evaluation(self, job_id: str) -> Optional[str]:
        """Load consciousness evaluation from LLM responses."""
        response_file = self.postings_path / f"{job_id}_all_llm_responses.txt"
        
        if not response_file.exists():
            return None
            
        try:
            with open(response_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # Extract consciousness evaluation section
                lines = content.split('\n')
                in_consciousness_section = False
                consciousness_lines = []
                
                for line in lines:
                    if "consciousness_specialists" in line.lower() or "encouragement_synthesizer" in line.lower():
                        in_consciousness_section = True
                        consciousness_lines.append(line)
                    elif in_consciousness_section:
                        if line.strip() and not line.startswith(' ') and not line.startswith('\t'):
                            # New section started
                            break
                        consciousness_lines.append(line)
                
                return '\n'.join(consciousness_lines) if consciousness_lines else content
        except Exception as e:
            print(f"Error loading consciousness evaluation for {job_id}: {e}")
            return None
    
    def select_review_sample(self, sample_size: int = 5, criteria: str = "diverse") -> List[str]:
        """
        Select a sample of jobs for systematic review.
        
        criteria options:
        - 'diverse': Mix of different job types and companies
        - 'recent': Most recently processed jobs
        - 'random': Random selection
        """
        evaluated_jobs = self.get_evaluated_jobs()
        
        if not evaluated_jobs:
            return []
        
        if criteria == "recent":
            return evaluated_jobs[-sample_size:] if len(evaluated_jobs) >= sample_size else evaluated_jobs
        elif criteria == "random":
            return random.sample(evaluated_jobs, min(sample_size, len(evaluated_jobs)))
        else:  # diverse
            # Try to get a mix of different job types
            if len(evaluated_jobs) <= sample_size:
                return evaluated_jobs
            
            # Sample evenly across the list to get diversity
            step = len(evaluated_jobs) // sample_size
            return [evaluated_jobs[i * step] for i in range(sample_size)]
    
    def create_review_session(self, job_ids: Optional[List[str]] = None, session_name: Optional[str] = None) -> str:
        """Create a new review session with selected jobs."""
        if job_ids is None:
            job_ids = self.select_review_sample(5, "diverse")
        
        if session_name is None:
            session_name = f"consciousness_review_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        session_data = {
            "session_name": session_name,
            "created_at": datetime.now().isoformat(),
            "job_ids": job_ids,
            "reviews": {},
            "session_feedback": {
                "overall_tone_preference": "",
                "narrative_effectiveness": "",
                "areas_for_improvement": "",
                "consciousness_strengths": "",
                "technical_observations": ""
            }
        }
        
        session_file = self.feedback_path / f"{session_name}.json"
        
        with open(session_file, 'w', encoding='utf-8') as f:
            json.dump(session_data, f, indent=2, ensure_ascii=False)
        
        print(f"✨ Created review session: {session_name}")
        print(f"📁 Session file: {session_file}")
        print(f"🔍 Jobs to review: {len(job_ids)}")
        
        return session_name
    
    def display_job_for_review(self, job_id: str, show_full_details: bool = True) -> None:
        """Display a job and its consciousness evaluation for review."""
        print("\n" + "="*80)
        print(f"🌟 REVIEWING JOB: {job_id}")
        print("="*80)
        
        # Load job details
        job_data = self.load_job_details(job_id)
        if not job_data:
            print(f"❌ Could not load job data for {job_id}")
            return
        
        # Display job summary
        print(f"\n📋 JOB TITLE: {job_data.get('title', 'Unknown')}")
        print(f"🏢 COMPANY: {job_data.get('company', 'Unknown')}")
        print(f"📍 LOCATION: {job_data.get('location', 'Unknown')}")
        
        if show_full_details and 'description' in job_data:
            description = job_data['description'][:500] + "..." if len(job_data['description']) > 500 else job_data['description']
            print(f"\n📝 DESCRIPTION:\n{description}")
        
        # Display consciousness evaluation
        consciousness_eval = self.load_consciousness_evaluation(job_id)
        if consciousness_eval:
            print(f"\n🌺 CONSCIOUSNESS EVALUATION:")
            print("-" * 50)
            print(consciousness_eval)
        else:
            print(f"\n❌ No consciousness evaluation found for {job_id}")
        
        print("\n" + "="*80)
    
    def collect_job_feedback(self, job_id: str, session_name: str) -> Dict:
        """Collect structured feedback for a specific job evaluation."""
        print(f"\n🌸 COLLECTING FEEDBACK FOR {job_id}")
        print("Please rate each aspect (1-5 scale, 5 being excellent):")
        
        feedback = {}
        
        # Narrative quality and tone
        feedback['narrative_quality'] = input("\n📝 Narrative Quality (clarity, engagement, helpfulness): ")
        feedback['tone_appropriateness'] = input("🎭 Tone Appropriateness (professional vs poetic balance): ")
        feedback['empowerment_level'] = input("💪 Empowerment Level (how encouraging and supportive): ")
        
        # Technical accuracy
        feedback['skill_assessment_accuracy'] = input("🎯 Skill Assessment Accuracy (realistic evaluation): ")
        feedback['growth_path_relevance'] = input("🚀 Growth Path Relevance (actionable development suggestions): ")
        feedback['opportunity_bridge_quality'] = input("🌉 Opportunity Bridge Quality (creative connections made): ")
        
        # Overall effectiveness
        feedback['overall_usefulness'] = input("⭐ Overall Usefulness (would this help in real job search): ")
        
        # Qualitative feedback
        print("\n💭 QUALITATIVE FEEDBACK:")
        feedback['what_worked_well'] = input("✅ What worked particularly well: ")
        feedback['areas_for_improvement'] = input("🔧 What could be improved: ")
        feedback['tone_preference'] = input("🎨 Tone preference (more professional/poetic/balanced): ")
        feedback['additional_comments'] = input("💫 Additional thoughts or suggestions: ")
        
        # Save feedback to session
        self.save_job_feedback(session_name, job_id, feedback)
        
        return feedback
    
    def save_job_feedback(self, session_name: str, job_id: str, feedback: Dict) -> None:
        """Save job feedback to the session file."""
        session_file = self.feedback_path / f"{session_name}.json"
        
        try:
            with open(session_file, 'r', encoding='utf-8') as f:
                session_data = json.load(f)
            
            session_data['reviews'][job_id] = {
                'feedback': feedback,
                'reviewed_at': datetime.now().isoformat()
            }
            
            with open(session_file, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, indent=2, ensure_ascii=False)
            
            print(f"💾 Feedback saved for {job_id}")
            
        except Exception as e:
            print(f"❌ Error saving feedback: {e}")
    
    def run_interactive_review_session(self, session_name: Optional[str] = None) -> str:
        """Run an interactive review session."""
        if session_name is None:
            # Create new session
            job_ids = self.select_review_sample(3, "diverse")  # Start with 3 jobs
            session_name = self.create_review_session(job_ids)
        
        session_file = self.feedback_path / f"{session_name}.json"
        
        if not session_file.exists():
            print(f"❌ Session {session_name} not found")
            return ""
        
        # Load session
        with open(session_file, 'r', encoding='utf-8') as f:
            session_data = json.load(f)
        
        print(f"\n🌺 STARTING CONSCIOUSNESS FEEDBACK SESSION: {session_name}")
        print(f"📊 Jobs to review: {len(session_data['job_ids'])}")
        
        for i, job_id in enumerate(session_data['job_ids'], 1):
            print(f"\n🔄 REVIEWING JOB {i}/{len(session_data['job_ids'])}")
            
            # Display job for review
            self.display_job_for_review(job_id, show_full_details=True)
            
            # Ask if user wants to provide feedback
            provide_feedback = input(f"\n🤔 Would you like to provide feedback for {job_id}? (y/n): ").lower().strip()
            
            if provide_feedback == 'y':
                self.collect_job_feedback(job_id, session_name)
            else:
                print("⏭️ Skipping feedback collection")
            
            # Ask if user wants to continue
            if i < len(session_data['job_ids']):
                continue_review = input(f"\n➡️ Continue to next job? (y/n): ").lower().strip()
                if continue_review != 'y':
                    break
        
        print(f"\n✨ Review session completed: {session_name}")
        return session_name
    
    def generate_feedback_summary(self, session_name: str) -> Dict:
        """Generate summary of feedback from a review session."""
        session_file = self.feedback_path / f"{session_name}.json"
        
        if not session_file.exists():
            return {}
        
        with open(session_file, 'r', encoding='utf-8') as f:
            session_data = json.load(f)
        
        if not session_data.get('reviews'):
            return {'message': 'No feedback collected yet'}
        
        # Calculate averages for numerical feedback
        numerical_fields = [
            'narrative_quality', 'tone_appropriateness', 'empowerment_level',
            'skill_assessment_accuracy', 'growth_path_relevance', 
            'opportunity_bridge_quality', 'overall_usefulness'
        ]
        
        averages = {}
        feedback_counts = {}
        
        for job_id, review in session_data['reviews'].items():
            feedback = review['feedback']
            for field in numerical_fields:
                if field in feedback and feedback[field].strip():
                    try:
                        value = float(feedback[field])
                        if field not in averages:
                            averages[field] = []
                        averages[field].append(value)
                    except ValueError:
                        continue
        
        # Calculate final averages
        summary = {
            'session_name': session_name,
            'total_jobs_reviewed': len(session_data['reviews']),
            'averages': {},
            'key_insights': []
        }
        
        for field, values in averages.items():
            if values:
                summary['averages'][field] = round(sum(values) / len(values), 2)
        
        # Collect qualitative insights
        for job_id, review in session_data['reviews'].items():
            feedback = review['feedback']
            if feedback.get('what_worked_well'):
                summary['key_insights'].append(f"✅ {feedback['what_worked_well']}")
            if feedback.get('areas_for_improvement'):
                summary['key_insights'].append(f"🔧 {feedback['areas_for_improvement']}")
        
        return summary

def main():
    """Run the consciousness feedback reviewer."""
    print("🌺 CONSCIOUSNESS FEEDBACK REVIEWER 🌺")
    print("Empowering iterative improvement through collaborative review")
    print("="*60)
    
    reviewer = ConsciousnessFeedbackReviewer()
    
    # Check for existing evaluations
    evaluated_jobs = reviewer.get_evaluated_jobs()
    print(f"📊 Found {len(evaluated_jobs)} jobs with consciousness evaluations")
    
    if not evaluated_jobs:
        print("❌ No consciousness evaluations found. Please run the consciousness pipeline first.")
        return
    
    # Show options
    print("\n🎯 REVIEW OPTIONS:")
    print("1. Start new interactive review session")
    print("2. Continue existing session")
    print("3. View single job evaluation")
    print("4. Generate feedback summary")
    
    choice = input("\nSelect option (1-4): ").strip()
    
    if choice == "1":
        session_name = reviewer.run_interactive_review_session()
        if session_name:
            summary = reviewer.generate_feedback_summary(session_name)
            print(f"\n📈 SESSION SUMMARY:")
            print(json.dumps(summary, indent=2, ensure_ascii=False))
    
    elif choice == "2":
        print("Feature coming soon: Continue existing session")
    
    elif choice == "3":
        print(f"\n📋 Available jobs: {evaluated_jobs[:10]}...")  # Show first 10
        job_id = input("Enter job ID to review: ").strip()
        if job_id in evaluated_jobs:
            reviewer.display_job_for_review(job_id)
        else:
            print(f"❌ Job {job_id} not found or not evaluated")
    
    elif choice == "4":
        print("Feature coming soon: Generate feedback summary")
    
    else:
        print("❌ Invalid choice")

if __name__ == "__main__":
    main()
