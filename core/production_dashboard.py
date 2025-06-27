#!/usr/bin/env python3
"""
Production Pipeline Dashboard
Real-time visualization of job analysis pipeline status
"""

import json
import time
from datetime import datetime, timedelta
from pathlib import Path
import sys
from typing import Dict, List, Any
import subprocess

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

try:
    from core.status_manager import StatusManager, PIPELINE_STATES
except ImportError:
    print("❌ Could not import StatusManager - please run from project root")
    sys.exit(1)

class BeautifulDashboard:
    """Real-time dashboard for Project Sunset pipeline"""
    
    def __init__(self):
        self.status_manager = StatusManager()
        self.start_time = datetime.now()
        
    def get_system_stats(self) -> Dict[str, Any]:
        """Get beautiful system statistics"""
        jobs_dir = PROJECT_ROOT / "data" / "postings"
        
        # Count different file types
        job_files = list(jobs_dir.glob("job*.json"))
        llm_outputs = list(jobs_dir.glob("job*_llm_output.txt"))
        llm_responses = list(jobs_dir.glob("job*_all_llm_responses.txt"))
        
        # Get export files
        output_dir = PROJECT_ROOT / "output"
        exports = list(output_dir.glob("*.xlsx")) if output_dir.exists() else []
        
        return {
            'total_jobs': len(job_files),
            'llm_evaluations': len(llm_outputs),
            'detailed_responses': len(llm_responses),
            'excel_exports': len(exports),
            'uptime': datetime.now() - self.start_time,
            'last_updated': datetime.now().strftime("%H:%M:%S")
        }
    
    def get_pipeline_flow(self) -> List[Dict[str, Any]]:
        """Get beautiful pipeline flow visualization"""
        flow_data = []
        
        # Calculate total jobs by scanning all job files
        job_files = list(self.status_manager.job_data_dir.glob("job*.json"))
        total_jobs = len(job_files)
        
        for code, info in PIPELINE_STATES.items():
            jobs = self.status_manager.get_jobs_by_status(code)
            
            # Calculate flow metrics
            percentage = (len(jobs) / total_jobs * 100) if total_jobs > 0 else 0
            
            # Visual representation
            bar_length = int(percentage / 5)  # Scale for display
            bar = "█" * bar_length
            
            flow_data.append({
                'code': code,
                'state': info['state'],
                'emoji': info.get('emoji', '⚡'),
                'count': len(jobs),
                'percentage': percentage,
                'bar': bar,
                'jobs': [f"Job {job.get('job_metadata', {}).get('job_id', job.get('job_id', 'unknown'))}: {job.get('job_content', {}).get('title', job.get('title', 'Unknown'))[:30]}..." 
                        for job in jobs[:3]]  # Show first 3 jobs
            })
        
        return flow_data
    
    def get_recent_activity(self) -> List[Dict[str, Any]]:
        """Get recent pipeline activity"""
        activity = []
        
        # Get all jobs by scanning all status codes
        for code in PIPELINE_STATES.keys():
            jobs = self.status_manager.get_jobs_by_status(code)
            
            for job in jobs:
                processing_log = job.get('processing_log', [])
                for log_entry in processing_log[-3:]:  # Last 3 entries
                    activity.append({
                        'job_id': job.get('job_metadata', {}).get('job_id', job.get('job_id', 'unknown')),
                        'action': log_entry.get('action', 'unknown'),
                        'timestamp': log_entry.get('timestamp', ''),
                        'processor': log_entry.get('processor', 'unknown'),
                        'status': log_entry.get('status', 'unknown')
                    })
        
        # Sort by timestamp (most recent first)
        activity.sort(key=lambda x: x['timestamp'], reverse=True)
        return activity[:10]  # Return last 10 activities
    
    def display_header(self):
        """Display beautiful dashboard header"""
        print("\033[2J\033[H")  # Clear screen and move cursor to top
        print("🌅" + "=" * 78 + "🌅")
        print("     PROJECT SUNSET - REAL-TIME PRODUCTION DASHBOARD")
        print("        Phase 8: Production Excellence Initiated")
        print("=" * 80)
        print(f"🕐 Live Update: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | "
              f"⏱️  Uptime: {datetime.now() - self.start_time}")
        print("=" * 80)
    
    def display_pipeline_status(self, flow_data: List[Dict[str, Any]]):
        """Display beautiful pipeline status"""
        print("\n🏗️  PIPELINE FLOW STATUS:")
        print("-" * 80)
        
        for stage in flow_data:
            status_line = f"  {stage['code']}. {stage['emoji']} {stage['state']:<15} │ " \
                         f"{stage['count']:3d} jobs ({stage['percentage']:5.1f}%) │{stage['bar']}"
            print(status_line)
            
            # Show job details for non-empty stages
            if stage['jobs']:
                for job in stage['jobs']:
                    print(f"     • {job}")
        
        print("-" * 80)
    
    def display_system_stats(self, stats: Dict[str, Any]):
        """Display beautiful system statistics"""
        print("\n📊 SYSTEM STATISTICS:")
        print("-" * 80)
        print(f"  📁 Total Jobs: {stats['total_jobs']}")
        print(f"  🧠 LLM Evaluations: {stats['llm_evaluations']}")
        print(f"  📝 Detailed Responses: {stats['detailed_responses']}")
        print(f"  📋 Excel Exports: {stats['excel_exports']}")
        print(f"  ⏱️  System Uptime: {stats['uptime']}")
        print("-" * 80)
    
    def display_recent_activity(self, activity: List[Dict[str, Any]]):
        """Display recent pipeline activity"""
        print("\n🔄 RECENT ACTIVITY:")
        print("-" * 80)
        
        if not activity:
            print("  No recent activity found")
        else:
            for item in activity[:5]:  # Show last 5 activities
                timestamp = item['timestamp'][:19] if item['timestamp'] else 'Unknown'
                status_icon = "✅" if item['status'] == 'success' else "❌"
                print(f"  {status_icon} Job {item['job_id']}: {item['action']} "
                      f"({item['processor']}) - {timestamp}")
        
        print("-" * 80)
    
    def display_next_actions(self):
        """Display next recommended actions"""
        print("\n🎯 NEXT ACTIONS (Phase 8):")
        print("-" * 80)
        
        # Get current status for recommendations
        jobs_at_3 = len(self.status_manager.get_jobs_by_status(3))
        jobs_at_1 = len(self.status_manager.get_jobs_by_status(1))
        
        if jobs_at_3 > 0:
            print(f"  📝 Generate cover letters for {jobs_at_3} processed jobs")
        if jobs_at_1 > 0:
            print(f"  ✨ Enhance descriptions for {jobs_at_1} fetched jobs")
        
        print("  🌐 Build multi-website adapter architecture")
        print("  👥 Design multi-user profile system")
        print("  🧪 Implement comprehensive testing framework")
        print("  Create production documentation")
        print("-" * 80)
    
    def display_system_note(self):
        """Display system status note"""
        print("\nSYSTEM STATUS:")
        print("-" * 80)
        print("  Professional job analysis pipeline monitoring system")
        print("  Real-time tracking of processing performance and quality metrics")
        print("  Designed for reliable Deutsche Bank job matching operations")
        print("=" * 80)
    
    def run_live_dashboard(self, refresh_seconds: int = 30):
        """Run live updating dashboard"""
        print("Starting Job Analysis Pipeline Dashboard...")
        print("   Press Ctrl+C to exit")
        time.sleep(2)
        
        try:
            while True:
                # Get fresh data
                stats = self.get_system_stats()
                flow_data = self.get_pipeline_flow()
                activity = self.get_recent_activity()
                
                # Display beautiful dashboard
                self.display_header()
                self.display_pipeline_status(flow_data)
                self.display_system_stats(stats)
                self.display_recent_activity(activity)
                self.display_next_actions()
                self.display_system_note()
                
                print(f"\n🔄 Next update in {refresh_seconds} seconds... (Ctrl+C to exit)")
                time.sleep(refresh_seconds)
                
        except KeyboardInterrupt:
            print("\n\nDashboard stopped. Production monitoring complete.")
            print("💫 May your pipeline flow with beauty and intention always.")
    
    def run_single_update(self):
        """Run single dashboard update"""
        stats = self.get_system_stats()
        flow_data = self.get_pipeline_flow()
        activity = self.get_recent_activity()
        
        self.display_header()
        self.display_pipeline_status(flow_data)
        self.display_system_stats(stats)
        self.display_recent_activity(activity)
        self.display_next_actions()
        self.display_system_note()

def main():
    """Main dashboard entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Project Sunset Real-Time Dashboard")
    parser.add_argument("--live", action="store_true", help="Run live updating dashboard")
    parser.add_argument("--refresh", type=int, default=30, help="Refresh interval in seconds")
    
    args = parser.parse_args()
    
    dashboard = BeautifulDashboard()
    
    if args.live:
        dashboard.run_live_dashboard(args.refresh)
    else:
        dashboard.run_single_update()

if __name__ == "__main__":
    main()
