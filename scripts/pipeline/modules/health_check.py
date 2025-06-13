#!/usr/bin/env python3
"""
Health Check Module
==================

Handles system health checks for the Project Sunset pipeline.
"""

from core import JobMatchingAPI
from core.config_manager import get_config
from core.beautiful_cli import print_info, print_success, print_error, show_progress_spinner


def health_check():
    """Perform system health check with beautiful output"""
    config = get_config()
    
    print_info("Starting Project Sunset Phase 7 health check...")
    show_progress_spinner("Checking system health", 1.5)
    
    try:
        # Initialize modern API
        api = JobMatchingAPI()
        
        # Health check
        health = api.health_check()
        print_info(f"API Health: {health['status']}")
        print_info(f"Available Specialists: {health.get('available_specialists', 0)}")
        
        if health['status'] == 'healthy':
            print_success("Project Sunset Phase 7 - Complete Pipeline Ready!")
            return True
        else:
            print_error(f"Health check failed: {health.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print_error(f"Health check failed with exception: {e}")
        return False
