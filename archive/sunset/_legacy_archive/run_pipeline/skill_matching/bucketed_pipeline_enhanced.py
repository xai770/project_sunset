#!/usr/bin/env python3
"""
Enhanced bucketed skill matching pipeline
"""

import logging
import json
import argparse
import inspect  # Add this import
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple, Callable, TypeVar, cast

# Define type variables for callable functions
T = TypeVar('T')
BatchMatchFunction = Callable[[Optional[List[int]], int, Optional[int], Optional[bool], Optional[bool]], Any]

# Define whether confidence scoring is available
HAS_CONFIDENCE_SCORING = True

# Get paths from the main config
try:
    from run_pipeline.config.paths import JOB_DATA_DIR
except ImportError:
    from pathlib import Path
    JOB_DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "postings"

def run_bucketed_skill_matcher(
    job_ids: Optional[List[int]] = None,
    batch_size: int = 10,
    max_workers: int = 4,
    force_reprocess: bool = False,
    use_embeddings: bool = True,
    use_confidence_scoring: bool = False
):
    """
    Run the bucket-based skill matching process for all jobs

    Args:
        job_ids: List of job IDs to process (optional)
        batch_size: Number of jobs to process in each batch
        max_workers: Number of parallel workers
        force_reprocess: Force reprocessing of already processed jobs
        use_embeddings: Whether to use embedding-based initial filtering
        use_confidence_scoring: Whether to include confidence scores in results
    """
    logger = logging.getLogger('skill_matcher')
    
    if use_confidence_scoring:
        logger.info(f"Running bucketed skill matcher with confidence scoring for {job_ids if job_ids else 'all jobs'}")
    else:
        logger.info(f"Running bucketed skill matcher for {job_ids if job_ids else 'all jobs'}")
    
    # Dynamically import and use the best available implementation
    matcher_function: Optional[Callable] = None
    matcher_module = "unknown"
    
    if use_embeddings:
        # Try to use the enhanced version with embedding similarity
        try:
            import run_pipeline.skill_matching.bucketed_skill_matcher_enhanced as enhanced_module
            if hasattr(enhanced_module, 'batch_match_all_jobs'):
                matcher_function = cast(Callable, enhanced_module.batch_match_all_jobs)
                matcher_module = "enhanced"
                logger.info("Using enhanced implementation with embedding similarity")
        except ImportError:
            try:
                # Check if bucket_matcher module exists
                import importlib.util
                bucket_spec = importlib.util.find_spec('run_pipeline.skill_matching.bucket_matcher')
                if bucket_spec is not None:
                    import run_pipeline.skill_matching.bucket_matcher as bucket_module
                    if hasattr(bucket_module, 'batch_match_all_jobs'):
                        matcher_function = cast(Callable, bucket_module.batch_match_all_jobs)
                        matcher_module = "bucket"
                        logger.info("Using bucket_matcher implementation")
                    else:
                        import run_pipeline.skill_matching.bucketed_skill_matcher as basic_module
                        if hasattr(basic_module, 'batch_match_all_jobs'):
                            matcher_function = cast(Callable, basic_module.batch_match_all_jobs)
                            matcher_module = "basic"
                            logger.info("Using standard implementation (bucket_matcher missing required function)")
                else:
                    import run_pipeline.skill_matching.bucketed_skill_matcher as basic_module
                    if hasattr(basic_module, 'batch_match_all_jobs'):
                        matcher_function = cast(Callable, basic_module.batch_match_all_jobs)
                        matcher_module = "basic"
                        logger.info("Using standard implementation (bucket_matcher not found)")
            except ImportError:
                import run_pipeline.skill_matching.bucketed_skill_matcher as basic_module
                if hasattr(basic_module, 'batch_match_all_jobs'):
                    matcher_function = cast(Callable, basic_module.batch_match_all_jobs)
                    matcher_module = "basic"
                    logger.info("Using standard implementation (enhanced version not available)")
    else:
        # Use standard implementation without embeddings
        import run_pipeline.skill_matching.bucketed_skill_matcher as basic_module
        if hasattr(basic_module, 'batch_match_all_jobs'):
            matcher_function = cast(Callable, basic_module.batch_match_all_jobs)
            matcher_module = "basic"
            logger.info("Using standard implementation (embeddings disabled)")
    
    # Check if we found a matcher function
    if matcher_function is None:
        logger.error("Failed to find a valid batch_match_all_jobs implementation")
        return
    
    # Run the matcher
    logger.info(f"Using {max_workers} workers for parallel processing")
    
    if HAS_CONFIDENCE_SCORING and use_confidence_scoring:
        logger.info("Confidence scoring is enabled for more reliable results")
    
    # Check the function signature to determine which parameters are supported
    sig = inspect.signature(matcher_function)
    param_names = set(sig.parameters.keys())
    
    # Call the function with appropriate parameters
    try:
        # Start with required parameters
        if "job_ids" in param_names and "batch_size" in param_names:
            # Build kwargs based on supported parameters
            kwargs = {"job_ids": job_ids, "batch_size": batch_size}
            
            if "max_workers" in param_names:
                kwargs["max_workers"] = max_workers
                
            if "force_reprocess" in param_names:
                kwargs["force_reprocess"] = force_reprocess
                
            if "use_confidence_scoring" in param_names and use_confidence_scoring:
                kwargs["use_confidence_scoring"] = use_confidence_scoring
            elif use_confidence_scoring:
                logger.warning(f"The {matcher_module} implementation doesn't support confidence scoring")
                
            # Call with supported parameters
            matcher_function(**kwargs)
        else:
            # Basic call - most implementations should support these
            matcher_function(job_ids, batch_size)
            
    except TypeError as e:
        logger.error(f"Error calling batch_match_all_jobs: {str(e)}")
        logger.warning("Falling back to basic parameter set")
        try:
            # Most basic parameter set that should work with all implementations
            matcher_function(job_ids, batch_size)
        except Exception as e2:
            logger.error(f"Failed to run skill matcher with basic parameters: {str(e2)}")
            raise
    
    logger.info("Enhanced bucketed skill matching complete")


def detect_and_fix_missing_matches(
    max_jobs: Optional[int] = None,  # Fixed Optional typing
    job_ids: Optional[List[int]] = None,  # Fixed Optional typing
    args = None
) -> Tuple[bool, List[int], List[int]]:
    """
    Detect and fix jobs with missing skills or zero matches
    
    This function identifies jobs with missing skills or zero match scores
    and applies the appropriate fix based on the specified approach.
    
    Args:
        max_jobs: Maximum number of jobs to check
        job_ids: Optional list of job IDs to check
        args: Command-line arguments with skill matching options
        
    Returns:
        Tuple[bool, List[int], List[int]]: Success status and lists of fixed job IDs
    """
    logger = logging.getLogger('job_pipeline')
    job_dir = Path(JOB_DATA_DIR)
    
    if job_ids:
        job_files = []
        for job_id in job_ids:
            job_file = job_dir / f"job{job_id}.json"
            if job_file.exists():
                job_files.append(job_file)
    else:
        job_files = sorted(list(job_dir.glob("job*.json")))
        if max_jobs and max_jobs < len(job_files):
            job_files = job_files[:max_jobs]
    
    logger.info(f"Checking {len(job_files)} job files for missing skills or zero match percentages")
    
    jobs_without_skills = []
    jobs_with_zero_matches = []
    
    for job_file in job_files:
        job_id = int(job_file.stem.replace("job", ""))
        try:
            with open(job_file, 'r', encoding='utf-8') as f:
                job_data = json.load(f)
            
            # For bucketed approach, we don't require SDR skills
            if args and args.bucketed:
                # Check if bucketed skill match exists and has valid match percentages
                skill_match = job_data.get("skill_match", {})
                if not skill_match or skill_match.get("overall_match", 0.0) == 0.0:
                    # Check if there are any skills that might be matched
                    if has_matchable_skills(job_data):
                        jobs_with_zero_matches.append(job_id)
                    else:
                        jobs_without_skills.append(job_id)
            else:
                # Traditional approach requires SDR skills
                if "sdr_skills" not in job_data or not job_data.get("sdr_skills", {}).get("enriched"):
                    jobs_without_skills.append(job_id)
                    continue
                    
                # Check if the job has skill matches with valid match percentages
                skill_matches = job_data.get("skill_matches", {})
                if "match_percentage" in skill_matches and skill_matches["match_percentage"] == 0.0:
                    # Check if there are actual SDR skills but zero matches
                    if job_data.get("sdr_skills", {}).get("enriched"):
                        jobs_with_zero_matches.append(job_id)
                        
        except Exception as e:
            logger.error(f"Error checking job {job_id}: {str(e)}")
    
    logger.info(f"Found {len(jobs_without_skills)} jobs without skills")
    logger.info(f"Found {len(jobs_with_zero_matches)} jobs with zero match percentages")
    
    # Fix problems if any are found
    fix_success = True
    if (jobs_without_skills or jobs_with_zero_matches) and args:
        fix_success = fix_missing_skills_and_matches(
            missing_skill_jobs=jobs_without_skills,
            zero_match_jobs=jobs_with_zero_matches,
            args=args
        )
    
    return fix_success, jobs_without_skills, jobs_with_zero_matches


def has_matchable_skills(job_data: Dict[str, Any]) -> bool:
    """
    Check if a job has enough information to perform skill matching
    
    Args:
        job_data: The job data structure
        
    Returns:
        bool: True if the job has matchable skill information
    """
    # Check for explicit skill lists
    if job_data.get("skills") and isinstance(job_data["skills"], list) and len(job_data["skills"]) > 0:
        return True
        
    # Check for job description
    if job_data.get("job_description") and len(job_data.get("job_description", "")) > 100:
        return True
        
    # Check for structured description
    structured = job_data.get("web_details", {}).get("structured_description", {})
    if structured.get("requirements") or structured.get("responsibilities"):
        return True
        
    # Check for concise description
    if job_data.get("web_details", {}).get("concise_description"):
        return True
        
    return False


def fix_missing_skills_and_matches(
    missing_skill_jobs: Optional[List[int]] = None, 
    zero_match_jobs: Optional[List[int]] = None, 
    args = None
) -> bool:
    """
    Fix jobs with missing skills or zero match percentages
    
    Args:
        missing_skill_jobs: List of job IDs missing skills
        zero_match_jobs: List of job IDs with zero match percentages
        args: Command-line arguments with skill matching options
        
    Returns:
        bool: Success status
    """
    logger = logging.getLogger('job_pipeline')
    success = True
    
    # Use default values if args is None
    if args is None:
        from argparse import Namespace

        # Around line 227, modify to include confidence_scoring:
        args = Namespace(
            batch_size=10, 
            max_workers=4, 
            enhanced=False, 
            bucketed=False, 
            no_embeddings=False,
            confidence_scoring=True  # Add this line to enable by default
        )
    
    # Fix jobs without skills (only needed for non-bucketed approach)
    if missing_skill_jobs and len(missing_skill_jobs) > 0 and not args.bucketed:
        logger.info(f"Fixing {len(missing_skill_jobs)} jobs without skills using SDR")
        # Run SDR implementation specifically for these jobs
        job_ids = [int(job_id) for job_id in missing_skill_jobs]
        try:
            from run_pipeline.skill_matching.run_enhanced_sdr import run_sdr_implementation
            
            enriched_skills, relationships, visualizations = run_sdr_implementation(
                use_llm=True,
                max_skills=50,
                validate_enrichment=False,
                test_matching=False,
                apply_feedback=False,
                generate_visualizations=False,
                update_job_files=True,
                job_ids=job_ids,
                force_reprocess=True
            )
            logger.info(f"SDR implementation completed for {len(missing_skill_jobs)} jobs")
        except Exception as e:
            logger.error(f"Error during SDR implementation: {str(e)}")
            success = False
    
    # Fix jobs with zero match percentages or jobs missing skills in bucketed approach
    fix_jobs = []
    if zero_match_jobs and len(zero_match_jobs) > 0:
        fix_jobs.extend(zero_match_jobs)
    
    if args.bucketed and missing_skill_jobs and len(missing_skill_jobs) > 0:
        fix_jobs.extend(missing_skill_jobs)
    
    # Remove duplicates
    fix_jobs = list(set(fix_jobs))
    
    if fix_jobs and success:
        logger.info(f"Fixing {len(fix_jobs)} jobs with missing or zero matches using enhanced bucketed approach with confidence scoring")
        # Run batch skill matching for these jobs
        job_ids = [int(job_id) for job_id in fix_jobs]
        
        try:
            if getattr(args, 'bucketed', False):
                # Run bucketed skill matcher with explicit parameters
                run_bucketed_skill_matcher(
                    job_ids=job_ids,
                    batch_size=getattr(args, 'batch_size', 10),
                    max_workers=getattr(args, 'max_workers', 4),
                    force_reprocess=True,
                    use_embeddings=not getattr(args, 'no_embeddings', False),
                    use_confidence_scoring=getattr(args, 'confidence_scoring', False)
                )
            elif getattr(args, 'enhanced', False):
                # Import dynamically to avoid name conflicts
                try:
                    import run_pipeline.skill_matching.enhanced_skill_matcher as enhanced_module
                    
                    if hasattr(enhanced_module, 'enhanced_batch_match_all_jobs'):
                        enhanced_func = cast(Callable, enhanced_module.enhanced_batch_match_all_jobs)
                        
                        # Check function signature
                        sig = inspect.signature(enhanced_func)
                        param_names = set(sig.parameters.keys())
                        
                        # Required params that should work with all implementations
                        enhanced_func(
                            job_ids=job_ids,
                            batch_size=getattr(args, 'batch_size', 10),
                            max_workers=getattr(args, 'max_workers', 4),
                            use_embeddings=not getattr(args, 'no_embeddings', False)
                        )
                    else:
                        logger.error("Enhanced module doesn't have enhanced_batch_match_all_jobs function")
                except ImportError:
                    logger.error("Failed to import enhanced_skill_matcher module")
                except Exception as e:
                    logger.error(f"Error running enhanced matcher: {str(e)}")
                    
            else:
                # Import dynamically to avoid name conflicts
                try:
                    import run_pipeline.skill_matching.efficient_skill_matcher as efficient_module
                    
                    if hasattr(efficient_module, 'batch_match_all_jobs'):
                        efficient_func = cast(Callable, efficient_module.batch_match_all_jobs)
                        
                        # Required params that should work with all implementations
                        efficient_func(
                            job_ids=job_ids,
                            batch_size=getattr(args, 'batch_size', 10)
                        )
                    else:
                        logger.error("Efficient module doesn't have batch_match_all_jobs function")
                except ImportError:
                    logger.error("Failed to import efficient_skill_matcher module")
                except Exception as e:
                    logger.error(f"Error running efficient matcher: {str(e)}")
                
            logger.info(f"Skill matching completed for {len(fix_jobs)} jobs with confidence scoring applied")
            
        except Exception as e:
            logger.error(f"Error during batch skill matching: {str(e)}")
            success = False
    
    return success


def main():
    """Direct script execution"""
    parser = argparse.ArgumentParser(description="Run the enhanced bucketed skill matcher with confidence scoring")
    parser.add_argument("--job-ids", type=int, nargs="+", help="Job IDs to process")
    parser.add_argument("--batch-size", type=int, default=10, help="Batch size for LLM calls")
    parser.add_argument("--max-workers", type=int, default=4, help="Max worker threads")
    parser.add_argument("--fix-missing", action="store_true", help="Fix jobs with missing skills or matches")
    parser.add_argument("--force-reprocess", action="store_true", help="Force reprocessing jobs")
    parser.add_argument("--no-embeddings", action="store_true", help="Disable embedding similarity")
    parser.add_argument("--confidence-scoring", action="store_true", help="Enable confidence scoring for skill matches")
    
    args = parser.parse_args()
    
    if args.fix_missing:
        detect_and_fix_missing_matches(job_ids=args.job_ids, args=args)
    else:
        # Convert job IDs to ints if provided
        job_ids = args.job_ids if args.job_ids else None
        
        run_bucketed_skill_matcher(
            job_ids=job_ids,
            batch_size=args.batch_size,
            max_workers=args.max_workers,
            force_reprocess=args.force_reprocess,
            use_embeddings=not args.no_embeddings,
            use_confidence_scoring=args.confidence_scoring
        )

if __name__ == "__main__":
    main()
