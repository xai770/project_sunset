#!/usr/bin/env python3
"""
Utility module for loading search strategies from CSV
"""
import os
import json
import pandas as pd
import logging

# Configure logging
logger = logging.getLogger('strategy_loader')

# Import paths config
from run_pipeline.config.paths import PROJECT_ROOT

def load_search_strategies_from_csv():
    """
    Load search strategies from CSV file
    
    Returns:
        list: List of search strategy dictionaries
    """
    strategies_csv_path = os.path.join(PROJECT_ROOT, "run_pipeline", "config", "search_strategies.csv")
    logger.info(f"Loading search strategies from {strategies_csv_path}")
    
    if not os.path.exists(strategies_csv_path):
        logger.error(f"Search strategies CSV file not found: {strategies_csv_path}")
        return []
    
    try:
        # Load the CSV using pandas
        df = pd.read_csv(strategies_csv_path)
        logger.info(f"Loaded {len(df)} search strategies from CSV")
        
        # Convert to list of dictionaries
        strategies = []
        
        for _, row in df.iterrows():
            # Parse parameter value - handles JSON arrays in the CSV
            param_value = row["parameter_value"]
            if param_value.startswith("[") and param_value.endswith("]"):
                # This is a JSON array, parse it
                try:
                    param_value = json.loads(param_value)
                except json.JSONDecodeError:
                    logger.warning(f"Failed to parse parameter value as JSON: {param_value}")
            
            # Create strategy dictionary with dynamic parameter
            strategy = {
                "Description": row["description"],
                row["parameter_name"]: param_value,
                "custom_filter": create_custom_filter(
                    row["filter_location"], 
                    row["filter_field"], 
                    row["filter_value"]
                )
            }
            
            strategies.append(strategy)
        
        return strategies
    except Exception as e:
        logger.error(f"Error loading search strategies from CSV: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return []

def create_custom_filter(filter_location, filter_field, filter_value):
    """
    Create a custom filter function based on the provided parameters
    
    Args:
        filter_location (str): Location filter value or * for any
        filter_field (str): Field to filter on or * for any
        filter_value (str): Value(s) to match, can be pipe-delimited for multiple values
    
    Returns:
        function: Lambda function for filtering
    """
    def custom_filter(job_data, title):
        # First check location if specified
        if filter_location != "*":
            location_match = False
            if "PositionLocation" in job_data:
                for loc in job_data.get("PositionLocation", []):
                    if loc.get("CountryName") == filter_location:
                        location_match = True
                        break
            
            if not location_match:
                return False
        
        # If no field specified or wildcard, just return True (location matched)
        if filter_field == "*" or filter_value == "*":
            return True
        
        # Handle title field specially
        if filter_field.lower() == "title":
            # Check for multiple values (pipe-delimited)
            if "|" in filter_value:
                values = filter_value.split("|")
                return any(value.strip() in title for value in values)
            else:
                return filter_value in title
        
        # For other fields, check in the job data
        # For now, we don't handle this case as it's more complex
        # We could expand this in the future if needed
        
        return True
    
    return custom_filter
