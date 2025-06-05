#!/bin/bash
# Restore script for the sunset project
# Created on: $(date +"%Y-%m-%d")

# Define source and destination directories
BACKUP_ROOT="/home/xai/backup/sunset"
LATEST_BACKUP="${BACKUP_ROOT}/sunset_backup_latest"
DEFAULT_RESTORE_DIR="/home/xai/Documents/sunset_restored"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

# Parse command line arguments
RESTORE_DIR="$DEFAULT_RESTORE_DIR"
if [ $# -ge 1 ]; then
    RESTORE_DIR="$1"
fi

# Print header
echo "===================================="
echo "Sunset Project Restore Script"
echo "===================================="
echo "Source: $LATEST_BACKUP"
echo "Destination: $RESTORE_DIR"
echo "===================================="

# Check if backup link exists
if [ ! -L "$LATEST_BACKUP" ]; then
    echo "ERROR: Latest backup link not found at $LATEST_BACKUP!"
    exit 1
fi

# Check if backup directory exists
if [ ! -d "$LATEST_BACKUP" ]; then
    echo "ERROR: Latest backup directory does not exist!"
    exit 1
fi

# Check if destination directory already exists
if [ -d "$RESTORE_DIR" ]; then
    echo "WARNING: Destination directory already exists!"
    echo "This will overwrite files in $RESTORE_DIR with the backed up versions."
    
    read -p "Do you want to continue? (y/n): " confirm
    if [[ ! $confirm =~ ^[Yy]$ ]]; then
        echo "Restore aborted by user."
        exit 0
    fi
else
    # Create restore directory
    echo "Creating restore directory: $RESTORE_DIR"
    mkdir -p "$RESTORE_DIR"
    
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to create restore directory!"
        exit 1
    fi
fi

# Create a log file
LOG_FILE="${RESTORE_DIR}/restore_log_${TIMESTAMP}.txt"
touch "$LOG_FILE"

# Function to log messages
log() {
    local timestamp=$(date +"%Y-%m-%d %H:%M:%S")
    echo "[$timestamp] $1" | tee -a "$LOG_FILE"
}

log "Starting restore of sunset project..."
log "Source: $LATEST_BACKUP"
log "Destination: $RESTORE_DIR"

# Use rsync to copy files (preserves permissions, timestamps, etc.)
log "Running rsync to restore files..."
rsync -av --info=progress2 "$LATEST_BACKUP/" "$RESTORE_DIR/" >> "$LOG_FILE" 2>&1

if [ $? -eq 0 ]; then
    log "Restore completed successfully!"
    
    # Calculate restored size
    RESTORE_SIZE=$(du -sh "$RESTORE_DIR" | cut -f1)
    log "Restore size: $RESTORE_SIZE"
    
    # Count number of files restored
    FILE_COUNT=$(find "$RESTORE_DIR" -type f | wc -l)
    log "Total files restored: $FILE_COUNT"
    
    # Get the original backup date from the manifest
    BACKUP_DATE="Unknown"
    MANIFEST_FILE="${LATEST_BACKUP}/backup_manifest.txt"
    if [ -f "$MANIFEST_FILE" ]; then
        BACKUP_DATE=$(grep "Date:" "$MANIFEST_FILE" | cut -d':' -f2- | sed 's/^[ \t]*//')
    fi
    
    # Display final status
    echo ""
    echo "===================================="
    echo "Sunset Project Restore Summary"
    echo "===================================="
    echo "Restored from backup created on: $BACKUP_DATE"
    echo "Source: $LATEST_BACKUP"
    echo "Destination: $RESTORE_DIR"
    echo "Size: $RESTORE_SIZE"
    echo "Files: $FILE_COUNT"
    echo "Status: SUCCESS"
    echo "Log file: $LOG_FILE"
    echo "===================================="
    
    # Remove restore log from the backup directory (it's not part of the original backup)
    if [[ "$RESTORE_DIR" == "$LATEST_BACKUP" ]]; then
        rm -f "$LOG_FILE"
    fi
else
    log "ERROR: Restore failed!"
    echo ""
    echo "Restore failed! See log file for details: $LOG_FILE"
    exit 1
fi
