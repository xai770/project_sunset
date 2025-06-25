#!/usr/bin/env python3
"""
Logger utility for the job expansion pipeline
"""

import os
import logging
from pathlib import Path
from datetime import datetime

def setup_logger(name, log_dir=None, log_level=logging.INFO):
    """
    Set up a logger with console and file handlers
    
    Args:
        name (str): Logger name
        log_dir (Path, optional): Directory for log files
        log_level (int): Logging level
        
    Returns:
        tuple: (logger, log_file_path)
    """
    # Configure logger
    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    
    # Clear any existing handlers to avoid duplicate logs
    if logger.hasHandlers():
        logger.handlers.clear()
    
    # Create formatter
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    
    # Add console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Add file handler if log_dir is provided
    log_file_path = None
    if log_dir:
        # Create log directory if it doesn't exist
        os.makedirs(log_dir, exist_ok=True)
        
        # Create log file
        log_file_path = log_dir / f"{name}.log"
        file_handler = logging.FileHandler(log_file_path)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        logger.info(f"Logging to: {log_file_path}")
    
    return logger, log_file_path

def create_timestamped_dir(base_dir, prefix):
    """
    Create a timestamped directory for logs or outputs
    
    Args:
        base_dir (Path): Base directory
        prefix (str): Directory name prefix
        
    Returns:
        Path: Path to the created directory
    """
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    dir_path = base_dir / f"{prefix}_{timestamp}"
    os.makedirs(dir_path, exist_ok=True)
    return dir_path
