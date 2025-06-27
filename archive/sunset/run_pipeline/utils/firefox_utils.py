#!/usr/bin/env python3
"""
Firefox browser utilities for the job expansion pipeline
"""

import os
import time
import logging
import subprocess
from pathlib import Path

logger = logging.getLogger('firefox_utils')

# Constants
FIREFOX_CHECK_TIMEOUT = 30  # Seconds to wait for Firefox to start

def check_firefox_installed():
    """
    Check if Firefox is installed
    
    Returns:
        bool: True if Firefox is available, False otherwise
    """
    logger.info("Checking for Firefox installation...")
    
    try:
        process = subprocess.run(
            ["firefox", "--version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False
        )
        
        if process.returncode == 0:
            logger.info(f"Firefox version: {process.stdout.strip()}")
            return True
        else:
            logger.error("Firefox is not installed or not in PATH")
            return False
    except Exception as e:
        logger.error(f"Exception checking Firefox: {str(e)}")
        return False

def check_firefox_running():
    """
    Check if Firefox is already running
    
    Returns:
        bool: True if Firefox is running, False otherwise
    """
    logger.info("Checking if Firefox is already running...")
    try:
        result = subprocess.run(
            ['pgrep', '-f', 'firefox'], 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE
        )
        is_running = result.returncode == 0
        if is_running:
            logger.info("Firefox is already running")
        else:
            logger.info("Firefox is not currently running")
        return is_running
    except Exception as e:
        logger.error(f"Error checking if Firefox is running: {str(e)}")
        return False

def start_firefox():
    """
    Start Firefox in the background
    
    Returns:
        bool: True if Firefox was successfully started, False otherwise
    """
    logger.info("Starting Firefox in the background...")
    try:
        # Use nohup to make Firefox keep running even if the script is terminated
        subprocess.Popen(['nohup', 'firefox', '--no-remote'], 
                       stdout=subprocess.DEVNULL,
                       stderr=subprocess.DEVNULL,
                       start_new_session=True)
        
        # Give Firefox time to fully initialize
        logger.info(f"Waiting {FIREFOX_CHECK_TIMEOUT} seconds for Firefox to initialize...")
        time.sleep(FIREFOX_CHECK_TIMEOUT)
        
        # Check if Firefox is now running
        return check_firefox_running()
    except Exception as e:
        logger.error(f"Error starting Firefox: {str(e)}")
        return False

def ensure_firefox_running():
    """
    Ensure Firefox is running before proceeding with job scraping
    
    Returns:
        bool: True if Firefox is running, False if it couldn't be started
    """
    logger.info("Ensuring Firefox is running...")
    
    # First check if Firefox is already running
    if check_firefox_running():
        return True
        
    # If not, try to start it
    logger.info("Firefox is not running. Attempting to start Firefox...")
    if start_firefox():
        logger.info("Firefox started successfully")
        return True
    else:
        logger.error("Failed to start Firefox. Job scraping requires Firefox to be running.")
        return False

def open_url_in_firefox(url):
    """
    Open a URL in Firefox in a new tab
    
    Args:
        url (str): URL to open
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        if not url:
            logger.error("No URL provided")
            return False
            
        # Use xdg-open which will open in a new tab if Firefox is already running
        logger.info(f"Opening URL in Firefox: {url}")
        subprocess.run(['xdg-open', url])
        return True
    except Exception as e:
        logger.error(f"Error opening URL in Firefox: {str(e)}")
        return False
