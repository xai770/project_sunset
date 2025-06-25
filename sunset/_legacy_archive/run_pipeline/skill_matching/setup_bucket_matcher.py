#!/usr/bin/env python3
"""
Setup script for bucket-based skill matching system

This script sets up the necessary symbolic links to ensure
the enhanced versions of the bucket matching system are accessible.
"""

import os
import sys
import logging
from pathlib import Path
import shutil

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("bucket_setup")

# Get project root
try:
    from run_pipeline.config.paths import PROJECT_ROOT
except ImportError:
    # Fallback if imported outside the pipeline
    PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

# Define paths
SKILL_MATCHING_DIR = PROJECT_ROOT / "run_pipeline" / "skill_matching"


def ensure_file_exists(file_path: Path) -> bool:
    """Check if a file exists"""
    if file_path.exists():
        logger.info(f"File exists: {file_path}")
        return True
    else:
        logger.warning(f"File does not exist: {file_path}")
        return False


def create_symlink(source_path: Path, target_path: Path) -> bool:
    """Create a symbolic link"""
    try:
        # Remove target if it exists
        if target_path.exists():
            if target_path.is_symlink() or target_path.is_file():
                target_path.unlink()
            else:
                shutil.rmtree(target_path)
                
        # Create parent directory if needed
        target_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create symlink
        target_path.symlink_to(source_path)
        logger.info(f"Created symlink: {target_path} -> {source_path}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to create symlink {target_path}: {str(e)}")
        return False


def copy_file(source_path: Path, target_path: Path) -> bool:
    """Copy a file"""
    try:
        # Create parent directory if needed
        target_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Copy file
        shutil.copy2(source_path, target_path)
        logger.info(f"Copied file: {source_path} -> {target_path}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to copy file {source_path}: {str(e)}")
        return False


def setup_bucket_system():
    """Set up the bucket-based skill matching system"""
    logger.info("Setting up bucket-based skill matching system")
    
    # Check if enhanced files exist
    enhanced_files = {
        "bucket_matcher_fixed.py": SKILL_MATCHING_DIR / "bucket_matcher_fixed.py",
        "bucket_utils_fixed.py": SKILL_MATCHING_DIR / "bucket_utils_fixed.py",
        "bucketed_skill_matcher_enhanced.py": SKILL_MATCHING_DIR / "bucketed_skill_matcher_enhanced.py",
        "bucketed_pipeline_enhanced.py": SKILL_MATCHING_DIR / "bucketed_pipeline_enhanced.py",
        "run_bucket_matcher.py": SKILL_MATCHING_DIR / "run_bucket_matcher.py",
        "test_bucket_matcher.py": SKILL_MATCHING_DIR / "test_bucket_matcher.py"
    }
    
    missing_files = []
    for name, path in enhanced_files.items():
        if not ensure_file_exists(path):
            missing_files.append(name)
            
    if missing_files:
        logger.error(f"Missing required files: {', '.join(missing_files)}")
        return False
    
    # Create symbolic links for consistent imports
    links = [
        (enhanced_files["bucket_matcher_fixed.py"], SKILL_MATCHING_DIR / "bucket_matcher_enhanced.py"),
        (enhanced_files["bucketed_skill_matcher_enhanced.py"], SKILL_MATCHING_DIR / "bucketed_skill_matcher_current.py")
    ]
    
    success = True
    for source, target in links:
        if not create_symlink(source, target):
            success = False
    
    if success:
        logger.info("Bucket-based skill matching system setup complete")
    else:
        logger.warning("Bucket-based skill matching system setup completed with warnings")
    
    return success


def create_init_file():
    """Create or update __init__.py file with necessary imports"""
    init_file = SKILL_MATCHING_DIR / "__init__.py"
    
    init_content = """# Bucket-based skill matching system
try:
    from .run_bucket_matcher import run_enhanced_bucket_matcher
except ImportError:
    pass
"""
    
    try:
        # Check if file exists
        if init_file.exists():
            # Read existing content
            with open(init_file, "r", encoding="utf-8") as f:
                existing_content = f.read()
                
            # Check if our content is already there
            if "run_enhanced_bucket_matcher" in existing_content:
                logger.info(f"Init file already has required imports: {init_file}")
                return True
            
            # Append to existing content
            with open(init_file, "a", encoding="utf-8") as f:
                f.write("\n\n" + init_content)
        else:
            # Create new file
            with open(init_file, "w", encoding="utf-8") as f:
                f.write(init_content)
                
        logger.info(f"Updated init file: {init_file}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to update init file {init_file}: {str(e)}")
        return False


def main():
    """Main entry point"""
    success = setup_bucket_system()
    init_success = create_init_file()
    
    if success and init_success:
        print("\n✅ Bucket-based skill matching system setup complete!")
        print("\nYou can now use the enhanced bucket matcher with:")
        print("  python -m run_pipeline.skill_matching.run_bucket_matcher")
        print("\nOr in the main pipeline with:")
        print("  python -m run_pipeline.core.pipeline --run-skill-matching --bucketed")
        sys.exit(0)
    else:
        print("\n⚠️ Bucket-based skill matching system setup completed with warnings.")
        print("Check the logs for details.")
        sys.exit(1)


if __name__ == "__main__":
    main()
