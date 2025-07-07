#!/bin/bash
# Local Backup script for the sunset project
# Created on: $(date +"%Y-%m-%d")

# Define source and destination directories
SOURCE_DIR="/home/xai/Documents/sunset"
BACKUP_ROOT="/home/xai/backup/sunset"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_DIR="${BACKUP_ROOT}/sunset_backup_${TIMESTAMP}"

# Check if source directory exists
if [ ! -d "$SOURCE_DIR" ]; then
    echo "ERROR: Source directory $SOURCE_DIR does not exist!"
    exit 1
fi

# Check if backup root directory exists, create if not
if [ ! -d "$BACKUP_ROOT" ]; then
    echo "Creating backup root directory: $BACKUP_ROOT"
    mkdir -p "$BACKUP_ROOT"
    
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to create backup root directory!"
        exit 1
    fi
fi

# Create a backup directory with timestamp
echo "Creating backup directory: $BACKUP_DIR"
mkdir -p "$BACKUP_DIR"

if [ $? -ne 0 ]; then
    echo "ERROR: Failed to create backup directory!"
    exit 1
fi

# Create a log file
LOG_FILE="${BACKUP_DIR}/backup_log.txt"
touch "$LOG_FILE"

# Function to log messages
log() {
    local timestamp=$(date +"%Y-%m-%d %H:%M:%S")
    echo "[$timestamp] $1" | tee -a "$LOG_FILE"
}

log "Starting backup of sunset project..."
log "Source: $SOURCE_DIR"
log "Destination: $BACKUP_DIR"

# Define directories to exclude
EXCLUDE=(
    "__pycache__"
    "*.pyc"
    "data/postings/html_content"  # Optional: exclude large HTML files if needed
    "logs"  # Optional: exclude log files if they're large
)

# Build rsync exclude parameters
EXCLUDE_PARAMS=""
for item in "${EXCLUDE[@]}"; do
    EXCLUDE_PARAMS="$EXCLUDE_PARAMS --exclude=$item"
done

# Use rsync to copy files (preserves permissions, timestamps, etc.)
log "Running rsync to copy files..."
rsync -av --info=progress2 $EXCLUDE_PARAMS "$SOURCE_DIR/" "$BACKUP_DIR/" >> "$LOG_FILE" 2>&1

if [ $? -eq 0 ]; then
    log "Backup completed successfully!"
    
    # Calculate backup size
    BACKUP_SIZE=$(du -sh "$BACKUP_DIR" | cut -f1)
    log "Backup size: $BACKUP_SIZE"
    
    # Count number of files backed up
    FILE_COUNT=$(find "$BACKUP_DIR" -type f | wc -l)
    log "Total files backed up: $FILE_COUNT"
    
    # Create a manifest file with important information
    MANIFEST_FILE="${BACKUP_DIR}/backup_manifest.txt"
    echo "Sunset Project Backup" > "$MANIFEST_FILE"
    echo "======================" >> "$MANIFEST_FILE"
    echo "Date: $(date)" >> "$MANIFEST_FILE"
    echo "Source: $SOURCE_DIR" >> "$MANIFEST_FILE"
    echo "Backup size: $BACKUP_SIZE" >> "$MANIFEST_FILE"
    echo "Files backed up: $FILE_COUNT" >> "$MANIFEST_FILE"
    echo "" >> "$MANIFEST_FILE"
    echo "Key files:" >> "$MANIFEST_FILE"
    echo "- scripts/job_expansion_workflow.py (Main workflow script)" >> "$MANIFEST_FILE"
    echo "- scripts/standalone_job_scraper.py (Job scraper)" >> "$MANIFEST_FILE"
    echo "- scripts/job_description_cleaner.py (Description cleaner)" >> "$MANIFEST_FILE" 
    echo "- scripts/career_pipeline/fetch_and_save_jobs.py (Job fetching)" >> "$MANIFEST_FILE"
    
    echo ""
    echo "Backup completed successfully at: $BACKUP_DIR"
    echo "Log file: $LOG_FILE"
    echo "Manifest file: $MANIFEST_FILE"
else
    log "ERROR: Backup failed!"
    echo ""
    echo "Backup failed! See log file for details: $LOG_FILE"
    exit 1
fi

# Create a symbolic link to the latest backup
LATEST_LINK="${BACKUP_ROOT}/sunset_backup_latest"
rm -f "$LATEST_LINK" 2>/dev/null
ln -s "$BACKUP_DIR" "$LATEST_LINK"

log "Created symbolic link to latest backup: $LATEST_LINK"
echo "Created symbolic link to latest backup: $LATEST_LINK"

# Display final status
echo ""
echo "===================================="
echo "Sunset Project Backup Summary"
echo "===================================="
echo "Date: $(date)"
echo "Source: $SOURCE_DIR"
echo "Destination: $BACKUP_DIR"
echo "Size: $BACKUP_SIZE"
echo "Files: $FILE_COUNT"
echo "Status: SUCCESS"
echo "===================================="
