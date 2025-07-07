#!/usr/bin/env python3
import subprocess
import time
import argparse
import logging
import json
import re
import sys
import os
import glob
import requests
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

# Base directory for the project
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Config files directory (new location)
CONFIG_DIR = os.path.join(BASE_DIR, "resources", "network")

# Default WireGuard interface name
WIREGUARD_INTERFACE = "wg-DE-497"

def get_available_configs():
    """Get list of available WireGuard configs in the resources/network directory."""
    config_files = glob.glob(os.path.join(CONFIG_DIR, "wg-*.conf"))
    return [os.path.basename(f).replace(".conf", "") for f in config_files]

def check_ip():
    """Check current public IP address."""
    try:
        response = requests.get('https://api.ipify.org?format=json', timeout=10)
        ip_data = response.json()
        return ip_data['ip']
    except Exception as e:
        logging.error(f"Failed to check IP address: {e}")
        return None

def check_wireguard_status():
    """Check the status of the WireGuard connection."""
    try:
        result = subprocess.run(
            ['sudo', 'wg', 'show', WIREGUARD_INTERFACE], 
            capture_output=True, 
            text=True, 
            check=False
        )
        
        if result.returncode != 0:
            return False, "Not connected"
        
        # Extract the handshake time
        handshake_match = re.search(r'latest handshake: (.*)', result.stdout)
        handshake_time = handshake_match.group(1) if handshake_match else "unknown"
        
        return True, f"Connected (Last handshake: {handshake_time})"
    except Exception as e:
        logging.error(f"Failed to check WireGuard status: {e}")
        return False, str(e)

def disconnect_wireguard():
    """Disconnect from WireGuard."""
    try:
        logging.info(f"Disconnecting from WireGuard interface {WIREGUARD_INTERFACE}...")
        subprocess.run(
            ['sudo', 'wg-quick', 'down', WIREGUARD_INTERFACE], 
            check=True, 
            capture_output=True
        )
        return True
    except subprocess.SubprocessError as e:
        logging.error(f"Failed to disconnect: {e}")
        return False

def connect_wireguard(interface=None):
    """Connect to WireGuard."""
    global WIREGUARD_INTERFACE
    
    if interface:
        WIREGUARD_INTERFACE = interface
        
    try:
        # Check if config file exists in the new location
        config_path = os.path.join(CONFIG_DIR, f"{WIREGUARD_INTERFACE}.conf")
        if not os.path.exists(config_path):
            logging.error(f"Config file not found: {config_path}")
            return False
            
        logging.info(f"Connecting to WireGuard interface {WIREGUARD_INTERFACE} using config at {config_path}...")
        subprocess.run(
            ['sudo', 'wg-quick', 'up', config_path], 
            check=True, 
            capture_output=True
        )
        return True
    except subprocess.SubprocessError as e:
        logging.error(f"Failed to connect: {e}")
        return False

def rotate_ip(wait_time=5, check_before=True, check_after=True, interface=None):
    """Rotate the WireGuard IP by disconnecting and reconnecting."""
    result = {
        "success": False,
        "old_ip": None,
        "new_ip": None,
        "timestamp": datetime.now().isoformat(),
        "status": None
    }
    
    # Check IP before rotation if requested
    if check_before:
        old_ip = check_ip()
        result["old_ip"] = old_ip
        logging.info(f"Current IP address: {old_ip}")
    
    # Check if VPN is connected
    connected, status = check_wireguard_status()
    if connected:
        logging.info(f"WireGuard status: {status}")
    else:
        logging.warning(f"WireGuard is not connected: {status}")
    
    # Disconnect
    if disconnect_wireguard():
        logging.info("Successfully disconnected from WireGuard")
    else:
        result["status"] = "Failed to disconnect"
        return result
    
    # Wait for a bit
    logging.info(f"Waiting for {wait_time} seconds before reconnecting...")
    time.sleep(wait_time)
    
    # Connect
    if connect_wireguard(interface):
        logging.info("Successfully connected to WireGuard")
    else:
        result["status"] = "Failed to connect"
        return result
    
    # Give some time for the connection to establish
    time.sleep(2)
    
    # Check if connected
    connected, status = check_wireguard_status()
    if not connected:
        result["status"] = f"Failed to verify connection: {status}"
        return result
    
    # Check IP after rotation if requested
    if check_after:
        # Wait a bit more to ensure the IP has changed
        time.sleep(2)
        new_ip = check_ip()
        result["new_ip"] = new_ip
        logging.info(f"New IP address: {new_ip}")
        
        # Check if the IP actually changed
        if result["old_ip"] and result["new_ip"] and result["old_ip"] == result["new_ip"]:
            result["status"] = "IP rotation did not change the IP address"
            logging.warning(result["status"])
        else:
            result["status"] = "Successfully rotated IP address"
            result["success"] = True
            logging.info(result["status"])
    else:
        result["status"] = "IP rotation completed, but IP check was skipped"
        result["success"] = True
        logging.info(result["status"])
    
    return result

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='Rotate WireGuard IP address')
    parser.add_argument('--wait', type=int, default=5, help='Time to wait between disconnect and connect (seconds)')
    parser.add_argument('--json', action='store_true', help='Output result as JSON')
    parser.add_argument('--no-check', action='store_true', help='Skip IP address checks')
    parser.add_argument('--log-file', type=str, help='Log to file instead of console')
    parser.add_argument('--interface', type=str, help='WireGuard interface name (e.g., wg-DE-1)')
    parser.add_argument('--list', action='store_true', help='List available WireGuard configs')
    args = parser.parse_args()
    
    # List available configs if requested
    if args.list:
        configs = get_available_configs()
        print(f"Available WireGuard configs in {CONFIG_DIR}:")
        for config in configs:
            print(f"  - {config}")
        return 0
    
    # Configure file logging if requested
    if args.log_file:
        file_handler = logging.FileHandler(args.log_file)
        file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logging.getLogger().addHandler(file_handler)
    
    result = rotate_ip(
        wait_time=args.wait, 
        check_before=not args.no_check,
        check_after=not args.no_check,
        interface=args.interface
    )
    
    if args.json:
        print(json.dumps(result, indent=2))
    
    return 0 if result["success"] else 1

if __name__ == "__main__":
    sys.exit(main())