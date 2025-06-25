#!/usr/bin/env python3
"""
Configuration Module
====================

Handles configuration loading and search criteria management.
"""

import json
import logging
from pathlib import Path
from core.rich_cli import print_warning, print_error, print_info

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent


def load_search_criteria(profile_name: str = "xai_frankfurt_focus") -> dict:
    """Load search criteria from config file"""
    config_path = project_root / "config" / "search_criteria.json"
    
    try:
        with open(config_path, 'r') as f:
            config_data = json.load(f)
        
        profiles = config_data.get("search_profiles", {})
        if profile_name not in profiles:
            print_warning(f"Profile '{profile_name}' not found, using default")
            profile_name = config_data.get("global_settings", {}).get("default_profile", "xai_frankfurt_focus")
        
        profile = profiles.get(profile_name, {})
        if not profile.get("active", False):
            print_warning(f"Profile '{profile_name}' is not active")
        
        print_info(f"Loaded search criteria profile: {profile_name}")
        print_info(f"Description: {profile.get('description', 'No description')}")
        
        return profile
        
    except Exception as e:
        print_error(f"Failed to load search criteria: {e}")
        return {}
