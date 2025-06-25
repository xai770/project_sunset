#!/usr/bin/env python3
"""
Excel Exporter Module
=====================

Handles exporting job matches to Excel using the JMFS feedback system format.
"""

import logging


def export_jobs_to_excel(feedback_system=True, reviewer_name="xai"):
    """Export jobs to Excel using the JMFS feedback system format"""
    logger = logging.getLogger(__name__)
    logger.info("=== EXPORTING JOBS TO EXCEL (Phase 7) ===")
    
    try:
        from run_pipeline.export_job_matches import export_job_matches
        
        # Export with feedback system enabled
        excel_path = export_job_matches(
            output_format='excel',
            output_file=None,  # Auto-generate filename
            job_ids=None,  # Export all processed jobs
            feedback_system=feedback_system,
            reviewer_name=reviewer_name
        )
        
        if excel_path:
            logger.info(f"✅ Excel export successful: {excel_path}")
            return excel_path
        else:
            logger.error("❌ Excel export failed - no data to export")
            return None
            
    except Exception as e:
        logger.error(f"❌ Error during Excel export: {e}")
        return None
