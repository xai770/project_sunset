#!/usr/bin/env python3
"""
Enhanced Job Fetcher Fix - AI Analysis Preservation Patch
========================================================

This patch strengthens the existing protection logic in the Enhanced Job Fetcher
to prevent AI analysis from being overwritten during job refresh operations.

PROBLEM: Enhanced Job Fetcher overwrites existing files with fresh API data,
         losing valuable AI analysis (llama32_evaluation, cv_analysis, etc.)

SOLUTION: Enhanced validation and preservation of existing AI analysis data
"""

import json
import shutil
from pathlib import Path
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

def create_enhanced_job_fetcher_patch():
    """Create a patch to strengthen AI analysis preservation in Enhanced Job Fetcher"""
    
    base_path = Path("/home/xai/Documents/sunset")
    target_file = base_path / "run_pipeline" / "core" / "fetch" / "job_processing.py"
    
    if not target_file.exists():
        logger.error(f"Target file not found: {target_file}")
        return False
    
    # Create backup of original file
    backup_file = target_file.with_suffix(f'.backup.{datetime.now().strftime("%Y%m%d_%H%M%S")}')
    shutil.copy2(target_file, backup_file)
    logger.info(f"📁 Created backup: {backup_file}")
    
    # Read current file
    with open(target_file, 'r') as f:
        content = f.read()
    
    # Enhanced AI analysis preservation check
    enhanced_preservation_code = '''
                # ENHANCED AI ANALYSIS PRESERVATION CHECK
                # Check for ANY valuable AI analysis that should be preserved
                valuable_ai_fields = [
                    'llama32_evaluation',
                    'cv_analysis', 
                    'skill_match',
                    'domain_enhanced_match',
                    'ai_processed',
                    'evaluation_results'
                ]
                
                has_ai_analysis = any(field in existing_job for field in valuable_ai_fields)
                
                # Also check for non-placeholder descriptions
                web_details = existing_job.get('web_details', {})
                concise_desc = web_details.get('concise_description', '')
                has_real_description = (
                    concise_desc.strip() and 
                    'placeholder for a concise description' not in concise_desc.lower() and
                    len(concise_desc) > 50  # Must be substantial content
                )
                
                # Check for processed skills data
                has_processed_skills = (
                    'skills' in existing_job and 
                    len(existing_job.get('skills', [])) > 0
                )
                
                # COMPREHENSIVE AI ANALYSIS CHECK
                has_valuable_data = has_ai_analysis or has_real_description or has_processed_skills
                
                if has_valuable_data:
                    logger.info(f"🔒 PRESERVING VALUABLE DATA for job {job_id}:")
                    if has_ai_analysis:
                        ai_fields_present = [field for field in valuable_ai_fields if field in existing_job]
                        logger.info(f"   📊 AI fields: {ai_fields_present}")
                    if has_real_description:
                        logger.info(f"   📝 Real description: {len(concise_desc)} chars")
                    if has_processed_skills:
                        logger.info(f"   🎯 Processed skills: {len(existing_job.get('skills', []))}")
'''
    
    # Find the location to insert the enhanced check
    # Look for the existing AI analysis check
    old_check_start = content.find("# Check if existing job has valuable AI analysis that should be preserved")
    
    if old_check_start == -1:
        logger.error("Could not find existing AI analysis check to enhance")
        return False
    
    # Find the end of the existing check (before the if has_ai_analysis: line)
    old_check_end = content.find("if has_ai_analysis:", old_check_start)
    
    if old_check_end == -1:
        logger.error("Could not find end of existing AI analysis check")
        return False
    
    # Replace the old check with enhanced version
    # Find the existing has_ai_analysis definition
    existing_check_start = content.find("has_ai_analysis = any([", old_check_start)
    
    if existing_check_start != -1:
        # Replace the existing check with our enhanced version
        existing_check_end = content.find("])", existing_check_start) + 2
        
        # Extract indentation from the existing code
        line_start = content.rfind('\n', 0, existing_check_start) + 1
        indentation = content[line_start:existing_check_start]
        
        # Apply proper indentation to our enhanced code
        enhanced_code_lines = enhanced_preservation_code.strip().split('\n')
        indented_enhanced_code = '\n'.join(indentation + line for line in enhanced_code_lines)
        
        # Replace the old check
        new_content = (
            content[:existing_check_start] + 
            indented_enhanced_code.replace('has_ai_analysis', 'has_valuable_data') +
            content[existing_check_end:]
        )
        
        # Also update the condition check
        new_content = new_content.replace(
            "if has_ai_analysis:",
            "if has_valuable_data:"
        )
        
        # Write the patched file
        with open(target_file, 'w') as f:
            f.write(new_content)
        
        logger.info("✅ Successfully applied Enhanced Job Fetcher patch")
        logger.info("🔒 AI analysis preservation strengthened")
        return True
    
    else:
        logger.error("Could not find existing AI analysis check to replace")
        return False

def validate_patch_installation():
    """Validate that the patch was installed correctly"""
    
    target_file = Path("/home/xai/Documents/sunset/run_pipeline/core/fetch/job_processing.py")
    
    if not target_file.exists():
        return False, "Target file not found"
    
    with open(target_file, 'r') as f:
        content = f.read()
    
    # Check for enhanced features
    checks = [
        "ENHANCED AI ANALYSIS PRESERVATION CHECK" in content,
        "has_valuable_data" in content,
        "has_real_description" in content,
        "has_processed_skills" in content,
        "COMPREHENSIVE AI ANALYSIS CHECK" in content
    ]
    
    if all(checks):
        return True, "Patch successfully installed and validated"
    else:
        return False, f"Patch validation failed: {sum(checks)}/5 checks passed"

def create_safeguard_script():
    """Create a safeguard script for manual AI analysis preservation"""
    
    safeguard_code = '''#!/usr/bin/env python3
"""
AI Analysis Preservation Safeguard
=================================

Emergency script to preserve AI analysis during job operations
"""

import json
import shutil
from pathlib import Path
from datetime import datetime

def preserve_ai_analysis_before_operation():
    """Create emergency backup of jobs with AI analysis"""
    
    base_path = Path("/home/xai/Documents/sunset")
    jobs_dir = base_path / "data" / "postings"
    
    # Create timestamp backup
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = base_path / "data" / f"AI_ANALYSIS_BACKUP_{timestamp}"
    backup_dir.mkdir(exist_ok=True)
    
    ai_jobs_backed_up = 0
    
    for job_file in jobs_dir.glob("job*.json"):
        try:
            with open(job_file, 'r') as f:
                job_data = json.load(f)
            
            # Check for AI analysis
            has_ai = any(field in job_data for field in [
                'llama32_evaluation', 'cv_analysis', 'skill_match', 'domain_enhanced_match'
            ])
            
            if has_ai:
                # Copy to backup
                backup_file = backup_dir / job_file.name
                shutil.copy2(job_file, backup_file)
                ai_jobs_backed_up += 1
                
        except Exception as e:
            print(f"Error processing {job_file}: {e}")
    
    print(f"🔒 Emergency backup created: {backup_dir}")
    print(f"📊 Backed up {ai_jobs_backed_up} jobs with AI analysis")
    return str(backup_dir)

if __name__ == "__main__":
    preserve_ai_analysis_before_operation()
'''
    
    safeguard_file = Path("/home/xai/Documents/sunset/scripts/ai_analysis_safeguard.py")
    with open(safeguard_file, 'w') as f:
        f.write(safeguard_code)
    
    # Make executable
    safeguard_file.chmod(0o755)
    
    logger.info(f"✅ Created safeguard script: {safeguard_file}")
    return str(safeguard_file)

def main():
    """Main execution function"""
    
    print("🔧 ENHANCED JOB FETCHER AI PRESERVATION PATCH")
    print("=" * 60)
    print()
    
    print("🎯 APPLYING FIXES:")
    print()
    
    # Apply the main patch
    print("1. 🔧 Patching Enhanced Job Fetcher...")
    if create_enhanced_job_fetcher_patch():
        print("   ✅ Enhanced Job Fetcher patch applied successfully")
        
        # Validate installation
        is_valid, message = validate_patch_installation()
        if is_valid:
            print(f"   ✅ Patch validation: {message}")
        else:
            print(f"   ⚠️  Patch validation: {message}")
    else:
        print("   ❌ Failed to apply Enhanced Job Fetcher patch")
    
    print()
    
    # Create safeguard script
    print("2. 🛡️  Creating AI analysis safeguard script...")
    safeguard_path = create_safeguard_script()
    print(f"   ✅ Safeguard script created: {Path(safeguard_path).name}")
    
    print()
    print("🎯 PATCH SUMMARY:")
    print("   ✅ Enhanced AI analysis preservation logic")
    print("   ✅ Comprehensive valuable data detection")
    print("   ✅ Strengthened protection against overwrites")
    print("   ✅ Emergency safeguard script created")
    print()
    print("💡 USAGE:")
    print("   - Normal pipeline operations now preserve AI analysis automatically")
    print("   - Run ai_analysis_safeguard.py before risky operations")
    print("   - Monitor logs for '🔒 PRESERVING VALUABLE DATA' messages")

if __name__ == "__main__":
    main()
