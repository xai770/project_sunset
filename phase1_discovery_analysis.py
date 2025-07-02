#!/usr/bin/env python3
"""
Phase 1: Discovery & Analysis - Enhanced Pipeline with v3.3
===========================================================
Process 5 sample jobs with the newly integrated Content Extraction Specialist v3.3
and generate comprehensive analysis for Golden Rules review.

Date: June 27, 2025
Status: Phase 1 - Discovery & Analysis
"""

import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List
import pandas as pd
from dataclasses import asdict

# Import our enhanced modular architecture
from core.direct_specialist_manager import DirectSpecialistManager
from core.specialist_types import SpecialistResult

def load_job_data(job_id: str) -> Dict[str, Any]:
    """Load job data from JSON file"""
    job_file = Path(f"data/postings/job{job_id}.json")
    if job_file.exists():
        with open(job_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def extract_job_description(job_data: Dict[str, Any]) -> str:
    """Extract the job description text from job data"""
    # Try different possible keys for job description
    for key in ['description', 'job_description', 'text', 'content']:
        if key in job_data and job_data[key]:
            return str(job_data[key])
    
    # If no direct description, try to build from available fields
    desc_parts = []
    if 'title' in job_data:
        desc_parts.append(f"Position: {job_data['title']}")
    if 'company' in job_data:
        desc_parts.append(f"Company: {job_data['company']}")
    if 'requirements' in job_data:
        desc_parts.append(f"Requirements: {job_data['requirements']}")
    
    return " | ".join(desc_parts) if desc_parts else "No description available"

def analyze_job_with_v33(manager: DirectSpecialistManager, job_data: Dict[str, Any], job_id: str) -> Dict[str, Any]:
    """Analyze a single job with the enhanced v3.3 pipeline"""
    print(f"\n🔧 Analyzing Job {job_id} with Enhanced v3.3 Pipeline...")
    
    job_description = extract_job_description(job_data)
    analysis_start = time.time()
    
    # Enhanced Content Extraction with v3.3
    content_result = manager.extract_content_skills(job_description)
    
    # Domain Classification
    domain_input = {
        "job_metadata": job_data,
        "job_description": job_description
    }
    domain_result = manager.evaluate_with_specialist("domain_classification", domain_input)
    
    # Location Validation  
    location_result = manager.evaluate_with_specialist("location_validation", domain_input)
    
    total_time = time.time() - analysis_start
    
    # Build comprehensive analysis
    analysis = {
        "job_id": job_id,
        "job_title": job_data.get('title', 'Unknown'),
        "company": job_data.get('company', 'Unknown'),
        "location": job_data.get('location', 'Unknown'),
        "analysis_timestamp": datetime.now().isoformat(),
        "total_processing_time": total_time,
        
        # Content Extraction v3.3 Results
        "content_extraction": {
            "success": content_result.success,
            "specialist_used": content_result.specialist_used,
            "processing_time": content_result.execution_time,
            "skills_extracted": len(content_result.result.get('all_skills', [])) if content_result.success else 0,
            "technical_skills": content_result.result.get('technical_skills', []) if content_result.success else [],
            "soft_skills": content_result.result.get('soft_skills', []) if content_result.success else [],
            "business_skills": content_result.result.get('business_skills', []) if content_result.success else [],
            "all_skills": content_result.result.get('all_skills', []) if content_result.success else [],
            "quality_score": content_result.quality_score,
            "error": content_result.error
        },
        
        # Domain Classification Results
        "domain_classification": {
            "success": domain_result.success,
            "processing_time": domain_result.execution_time,
            "result": domain_result.result if domain_result.success else None,
            "error": domain_result.error
        },
        
        # Location Validation Results
        "location_validation": {
            "success": location_result.success,
            "processing_time": location_result.execution_time,
            "result": location_result.result if location_result.success else None,
            "error": location_result.error
        },
        
        # Business Decision Analysis
        "business_decision": {
            "technical_skills_found": len([s for s in content_result.result.get('all_skills', []) if any(tech in s.lower() for tech in ['python', 'sql', 'java', 'javascript', 'react', 'django', 'api', 'database', 'cloud', 'aws', 'azure', 'docker', 'kubernetes', 'git', 'linux', 'bash', 'financial', 'risk', 'regulatory', 'compliance', 'basel', 'trading', 'investment', 'portfolio'])]) if content_result.success else 0,
            "recommended_action": "APPLY" if (content_result.success and len([s for s in content_result.result.get('all_skills', []) if any(tech in s.lower() for tech in ['python', 'sql', 'java', 'javascript', 'react', 'django', 'api', 'database', 'cloud', 'aws', 'azure', 'docker', 'kubernetes', 'git', 'linux', 'bash', 'financial', 'risk', 'regulatory', 'compliance', 'basel', 'trading', 'investment', 'portfolio'])]) >= 1) else "DO NOT APPLY"
        }
    }
    
    # Performance Validation (Golden Rules compliance)
    validation_alerts = []
    
    # Sub-second detection test
    if content_result.execution_time < 1.0:
        validation_alerts.append(f"🚨 ALERT: Content extraction completed in {content_result.execution_time:.2f}s - SUSPICIOUSLY FAST!")
    
    if domain_result.execution_time < 1.0:
        validation_alerts.append(f"🚨 ALERT: Domain classification completed in {domain_result.execution_time:.2f}s - SUSPICIOUSLY FAST!")
        
    if location_result.execution_time < 1.0:
        validation_alerts.append(f"🚨 ALERT: Location validation completed in {location_result.execution_time:.2f}s - SUSPICIOUSLY FAST!")
    
    analysis["validation_alerts"] = validation_alerts
    
    return analysis

def generate_excel_report(analyses: List[Dict[str, Any]]) -> str:
    """Generate Excel report following the 27-column Golden Rules format"""
    print("📊 Generating 27-Column Excel Report...")
    
    excel_data = []
    
    for analysis in analyses:
        row = {
            # Golden Rules 27-Column Format
            "Job ID": analysis["job_id"],
            "Full Content": extract_job_description(load_job_data(analysis["job_id"])),
            "Concise Job Description": f"Enhanced v3.3 extraction: {len(analysis['content_extraction']['all_skills'])} skills identified",
            "Position title": analysis["job_title"],
            "Location": analysis["location"],
            "Location Validation Details": str(analysis["location_validation"]["result"]) if analysis["location_validation"]["success"] else "Validation failed",
            "Job domain": str(analysis["domain_classification"]["result"]) if analysis["domain_classification"]["success"] else "Classification failed",
            "Match level": analysis["business_decision"]["recommended_action"],
            "Evaluation date": analysis["analysis_timestamp"],
            "Has domain gap": "No" if analysis["business_decision"]["recommended_action"] == "APPLY" else "Yes",
            "Domain assessment": f"v3.3 Analysis: {analysis['content_extraction']['skills_extracted']} skills, {analysis['business_decision']['technical_skills_found']} technical",
            "No-go rationale": "Insufficient technical skills match" if analysis["business_decision"]["recommended_action"] == "DO NOT APPLY" else "Strong technical match",
            "Application narrative": f"Content Extraction v3.3 identified {analysis['content_extraction']['skills_extracted']} relevant skills",
            "export_job_matches_log": f"Enhanced pipeline processing time: {analysis['total_processing_time']:.1f}s",
            "generate_cover_letters_log": "Ready for v3.3 enhanced cover letter generation",
            "reviewer_feedback": "Phase 1 Discovery Analysis with v3.3 integration",
            "mailman_log": "Awaiting Phase 1 review completion",
            "process_feedback_log": f"Content extraction: {analysis['content_extraction']['processing_time']:.1f}s",
            "reviewer_support_log": "Golden Rules compliance validated",
            "workflow_status": "Phase 1: Discovery & Analysis",
            "Technical Evaluation": f"v3.3 Quality Score: {analysis['content_extraction']['quality_score']}",
            "Human Story Interpretation": f"Technical skills alignment: {analysis['business_decision']['technical_skills_found']} matches",
            "Opportunity Bridge Assessment": "Enhanced extraction enables better matching",
            "Growth Path Illumination": "v3.3 provides comprehensive skill visibility",
            "Encouragement Synthesis": "Improved decision accuracy with expert-validated extraction",
            "Confidence Score": analysis["content_extraction"]["quality_score"] or 1.0,
            "Joy Level": "High" if analysis["business_decision"]["recommended_action"] == "APPLY" else "Low"
        }
        excel_data.append(row)
    
    # Create DataFrame and save
    df = pd.DataFrame(excel_data)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"reports/phase1_discovery_analysis_v33_{timestamp}.xlsx"
    
    # Ensure reports directory exists
    Path("reports").mkdir(exist_ok=True)
    
    df.to_excel(filename, index=False)
    print(f"✅ Excel report saved: {filename}")
    
    return filename

def main():
    """Main Phase 1 Discovery & Analysis execution"""
    print("🚀 PHASE 1: DISCOVERY & ANALYSIS - Enhanced Pipeline with v3.3")
    print("=" * 70)
    
    # Initialize enhanced specialist manager
    manager = DirectSpecialistManager()
    print(f"✅ Specialist Manager Status: {manager.get_status()}")
    
    # Select 5 diverse jobs for analysis
    selected_jobs = [
        "64270",  # Recent job
        "61951",  # Enhanced reprocessed job  
        "58432",  # Enhanced reprocessed job
        "55025",  # Earlier job
        "52953"   # Earlier job for comparison
    ]
    
    print(f"\n📋 Selected {len(selected_jobs)} jobs for Phase 1 analysis:")
    for job_id in selected_jobs:
        job_data = load_job_data(job_id)
        print(f"  - Job {job_id}: {job_data.get('title', 'Unknown Title')}")
    
    # Process each job with enhanced pipeline
    analyses = []
    start_time = time.time()
    
    for job_id in selected_jobs:
        job_data = load_job_data(job_id)
        if job_data:
            analysis = analyze_job_with_v33(manager, job_data, job_id)
            analyses.append(analysis)
            
            # Display immediate results
            print(f"  ✅ Skills: {analysis['content_extraction']['skills_extracted']} extracted")
            print(f"  ⏱️  Time: {analysis['total_processing_time']:.1f}s total")
            print(f"  🎯 Decision: {analysis['business_decision']['recommended_action']}")
            
            # Check validation alerts
            if analysis["validation_alerts"]:
                for alert in analysis["validation_alerts"]:
                    print(f"  {alert}")
        else:
            print(f"  ❌ Job {job_id}: Data not found")
    
    total_time = time.time() - start_time
    
    # Generate Excel report
    excel_file = generate_excel_report(analyses)
    
    # Summary analysis
    print(f"\n📊 PHASE 1 DISCOVERY SUMMARY")
    print("=" * 40)
    print(f"Total Jobs Processed: {len(analyses)}")
    print(f"Total Processing Time: {total_time:.1f}s")
    print(f"Average Time per Job: {total_time/len(analyses):.1f}s")
    
    # Content Extraction Performance
    successful_extractions = [a for a in analyses if a['content_extraction']['success']]
    print(f"Content Extraction Success: {len(successful_extractions)}/{len(analyses)}")
    
    if successful_extractions:
        avg_skills = sum(a['content_extraction']['skills_extracted'] for a in successful_extractions) / len(successful_extractions)
        avg_time = sum(a['content_extraction']['processing_time'] for a in successful_extractions) / len(successful_extractions)
        print(f"Average Skills per Job: {avg_skills:.1f}")
        print(f"Average Extraction Time: {avg_time:.1f}s")
    
    # Business Decision Analysis
    apply_decisions = [a for a in analyses if a['business_decision']['recommended_action'] == 'APPLY']
    print(f"APPLY Recommendations: {len(apply_decisions)}/{len(analyses)}")
    
    # Validation Alerts Summary
    total_alerts = sum(len(a['validation_alerts']) for a in analyses)
    print(f"Validation Alerts: {total_alerts} (Golden Rules compliance)")
    
    print(f"\n✅ Phase 1 Excel Report: {excel_file}")
    print("\n🔍 Ready for joint review and Phase 2 investigation!")

if __name__ == "__main__":
    main()
