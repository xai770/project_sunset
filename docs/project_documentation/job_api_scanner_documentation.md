# Deutsche Bank Job API Scanner Documentation

**Date:** May 16, 2025  
**Author:** Project Sunset Team  
**Version:** 1.0

## Overview

The Job API Scanner is a specialized tool developed for Project Sunset to systematically discover and extract job postings from Deutsche Bank's previously unknown direct API endpoint. This document provides a comprehensive description of the scanner's functionality, implementation, and usage.

## Discovery Context

During the project, we identified a direct API endpoint (`https://api-deutschebank.beesite.de/jobhtml/{job_id}.json`) that provides access to individual job listings. This endpoint was previously undocumented and offered a more efficient way to access job data compared to the standard web scraping approach.

## Technical Specifications

### Core Features

1. **Sequential Job ID Scanning**
   - Systematically scans through job ID ranges to find valid job postings
   - Uses binary search to efficiently find the first valid job ID
   - Detects valid vs. invalid jobs by checking HTML content presence

2. **IP Rotation**
   - Integrates with WireGuard VPN for automatic IP rotation
   - Rotates IP address after configurable number of requests
   - Helps avoid rate limiting and detection

3. **Resilience & Resumability**
   - Maintains progress tracking with automatic saving
   - Can resume scanning from the last scanned job ID
   - Configurable consecutive failure threshold to handle gaps in job ID ranges

4. **Data Management**
   - Saves job data in standardized JSON format
   - Extracts and preserves HTML content separately
   - Maintains detailed logging of all operations

5. **Location Filtering**
   - Filters jobs based on specified locations (e.g., Frankfurt, Berlin)
   - Extracts location information from job HTML content

## Implementation Details

### Key Components

1. **API Communication**
   - Uses the requests library to communicate with the API endpoint
   - Implements proper headers and error handling
   - Adds random delay between requests to avoid detection

2. **HTML Processing**
   - Uses BeautifulSoup to parse and extract data from HTML content
   - Extracts job title, location, and other metadata where available

3. **Data Storage**
   - Maintains a standardized job data structure
   - Creates separate files for each job in JSON format
   - Stores HTML content separately for efficient processing

4. **Progress Tracking**
   - Maintains a progress file to track scanned job IDs
   - Tracks statistics including successful jobs, failed jobs, and IP rotations
   - Provides resumability to continue from the last scanned job ID

5. **Binary Search**
   - Implements a binary search algorithm to efficiently locate the first valid job ID
   - Significantly speeds up the initial phase of scanning

### Directory Structure

```
/home/xai/Documents/sunset/
│
├── job_api_scanner.py                 # Main scanner script
│
├── data/
│   ├── postings/                      # Directory for job data files
│   │   ├── job{id}.json               # Individual job data files
│   │   └── html_content/              # Separate storage for HTML content
│   │       └── db_job_{id}_content.txt
│   │
│   └── job_scans/                     # Scan progress tracking
│       └── api_scan_progress.json     # Progress tracking file
│
└── scripts/
    └── utils/
        └── rotate_wireguard_ip.py     # IP rotation functionality
```

### Data Structure

Each job is stored in a standardized JSON format that includes:

```json
{
  "job_id": 12345,
  "api_details": {
    "html": "...",
    "apply_uri": "...",
    "save_uri": "...",
    "pro_div_id": "...",
    "pro_div_name": "...",
    "pro_div_code": "..."
  },
  "web_details": {
    "url": "https://careers.db.com/professionals/search-roles/#/professional/job/{job_id}",
    "position_title": "...",
    "locations": ["..."],
    "full_description": "..."
  },
  "metadata": {
    "created_at": "2025-05-15T18:43:32.704381",
    "last_updated": {
      "created_at": "2025-05-15T18:43:32.704391",
      "api_checked_at": "2025-05-15T18:49:19.634983",
      "scraped_at": null,
      "cleaned_at": null
    },
    "source": "job_api_scanner"
  },
  "log": [
    {
      "timestamp": "2025-05-15T18:43:32.704395",
      "module": "job_api_scanner",
      "action": "create_job_file",
      "message": "Created job file for ID {job_id} from API data"
    }
  ]
}
```

## Usage

### Command-Line Interface

The Job API Scanner can be run from the command line with several configurable options:

```bash
python job_api_scanner.py [options]
```

### Command-Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `--start-id` | Starting job ID | 50000 |
| `--end-id` | Ending job ID | 65000 |
| `--locations` | Target locations to filter for (comma-separated) | None |
| `--max-failures` | Max consecutive failures before stopping | 10 |
| `--no-ip-rotation` | Disable IP rotation | False |
| `--delay` | Base delay between requests in seconds | 2 |
| `--binary-search` | Use binary search to find first valid job ID | False |

### Example Commands

**Basic scan for all jobs:**
```bash
python job_api_scanner.py
```

**Scan with location filtering:**
```bash
python job_api_scanner.py --locations "Frankfurt,Berlin"
```

**Scan with custom range and binary search:**
```bash
python job_api_scanner.py --start-id 60000 --end-id 62000 --binary-search
```

**Scan with custom settings and no IP rotation:**
```bash
python job_api_scanner.py --delay 3 --max-failures 20 --no-ip-rotation
```

## Key Findings

1. **Job ID Range**: Through binary search, we discovered that the first valid job ID is 60985. We have successfully scanned and saved job data for multiple job IDs starting from this point.

2. **API Structure**: The API returns job data in a consistent JSON format that includes:
   - HTML content of the job posting
   - Application URI for direct application links
   - Professional division information

3. **Data Quality**: The data obtained through the API is highly structured and consistent, making it easier to process compared to web scraping.

4. **ID Gaps**: There are significant gaps in the job ID sequence, with many consecutive IDs returning empty results.

## Integration with Other Components

The Job API Scanner is designed to integrate with the existing job processing pipeline:

1. The scanner saves job data in the same format used by other components
2. HTML content is stored separately to align with the existing processing workflow
3. Metadata is maintained for tracking job processing status across different stages

## Performance Considerations

1. **Rate Limiting**: The scanner implements random delays between requests to avoid triggering rate limiting.
2. **IP Rotation**: Automatic IP rotation using WireGuard helps avoid detection of automated scanning.
3. **Binary Search**: Using binary search significantly accelerates the discovery of valid job ID ranges.
4. **Resumability**: Progress tracking ensures that scans can be resumed without duplicating work.

## Future Improvements

1. **Parallel Processing**: Implement multi-threaded scanning for faster processing.
2. **More Data Extraction**: Extract additional metadata from job listings.
3. **API Monitoring**: Add functionality to monitor for changes in the API structure.
4. **Automated Scheduling**: Implement automatic periodic scanning for new job listings.

## Conclusion

The Job API Scanner provides an efficient and reliable method for systematically discovering and extracting Deutsche Bank job postings. It has successfully identified numerous job listings and saved them in a standardized format for further processing and analysis.
