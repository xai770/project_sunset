#!/usr/bin/env python3
"""
Process utilities for the job expansion pipeline
"""

import os
import time
import logging
import subprocess
from pathlib import Path
from datetime import datetime

logger = logging.getLogger('process_utils')

def run_process(command, step_name, log_dir=None, max_retries=3):
    """
    Run a subprocess command with retry logic
    
    Args:
        command (list): Command to run as list of arguments
        step_name (str): Name of the step for logging
        log_dir (Path): Directory to write log files
        max_retries (int): Maximum number of retry attempts
        
    Returns:
        tuple: (success, output) where success is a boolean and output is the process output
    """
    # Create log file path if log_dir is provided
    log_file = None
    if log_dir:
        log_file = log_dir / f"{step_name.lower().replace(' ', '_')}.log"
    
    for attempt in range(1, max_retries + 1):
        if attempt > 1:
            logger.info(f"Retry attempt {attempt}/{max_retries} for {step_name}...")
            time.sleep(5)  # Wait before retry
            
        logger.info(f"Running {step_name}... (attempt {attempt}/{max_retries})")
        
        try:
            # Write command to log file first if log_file exists
            if log_file:
                with open(log_file, 'w') as f:
                    f.write(f"Command: {' '.join(command)}\n\n")
                    f.write(f"Started at: {datetime.now().isoformat()}\n\n")
            
            # Run the command and capture output
            process = subprocess.run(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                check=False
            )
            
            # Append output to log file if log_file exists
            if log_file:
                with open(log_file, 'a') as f:
                    f.write(f"Return code: {process.returncode}\n\n")
                    f.write("Output:\n")
                    f.write(process.stdout)
            
            if process.returncode == 0:
                logger.info(f"✓ {step_name} completed successfully")
                return True, process.stdout
            else:
                logger.error(f"✗ {step_name} failed with exit code {process.returncode}")
                if log_file:
                    logger.error(f"See log file: {log_file}")
        except Exception as e:
            logger.error(f"Exception running {step_name}: {str(e)}")
            if log_file:
                with open(log_file, 'a') as f:
                    f.write(f"Exception: {str(e)}\n")
    
    logger.error(f"ERROR: {step_name} failed after {max_retries} attempts")
    return False, ""

def check_command_available(command, args=None):
    """
    Check if a command is available in PATH
    
    Args:
        command (str): Command to check
        args (list): Optional arguments to pass to the command
        
    Returns:
        tuple: (available, version_str)
    """
    logger.info(f"Checking for {command} installation...")
    
    cmd = [command]
    if args:
        cmd.extend(args)
        
    try:
        process = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False
        )
        
        if process.returncode == 0:
            version_output = process.stdout.strip() or process.stderr.strip()
            logger.info(f"{command} found: {version_output}")
            return True, version_output
        else:
            logger.error(f"{command} is not installed or not in PATH")
            return False, None
    except Exception as e:
        logger.error(f"Exception checking {command}: {str(e)}")
        return False, None
