# Deutsche Bank Career Search API Scanner

## Overview

The Deutsche Bank Career Search API Scanner is a specialized tool designed to efficiently retrieve and process job postings from Deutsche Bank's career website. Unlike the previous brute-force approach that checked job IDs sequentially, this tool leverages Deutsche Bank's search API endpoint to fetch batches of valid jobs directly.

## Key Features

- **Efficient API Scanning**: Directly retrieves batches of valid job listings instead of sequentially checking IDs
- **Pagination Support**: Processes search results across multiple pages
- **Location Filtering**: Supports filtering by country and city codes
- **Resumable Operation**: Saves progress and can resume from where it left off
- **Detailed Job Information**: Combines data from both search results and detailed job HTML
- **Progress Tracking**: Maintains statistics about the scanning process

## Technical Details

### API Endpoints

The tool interacts with two main API endpoints:

1. **Search API**: `https://api-deutschebank.beesite.de/search/`
   - Used to retrieve batches of job listings
   - Supports pagination, sorting, and filtering

2. **Job HTML API**: `https://api-deutschebank.beesite.de/jobhtml/{job_id}.json`
   - Used to fetch detailed information about a specific job
   - Contains the full HTML description and additional metadata

### Search API Request Structure

The Search API accepts a JSON payload with the following structure:

```json
{
  "LanguageCode": "en",
  "SearchParameters": {
    "FirstItem": 1,
    "CountItem": 100,
    "MatchedObjectDescriptor": [
      "PositionID",
      "PositionTitle",
      "PositionLocation.CityName",
      "PositionLocation.CountryName",
      ... (additional fields)
    ],
    "Sort": [
      {
        "Criterion": "PublicationStartDate",
        "Direction": "DESC"
      }
    ]
  },
  "SearchCriteria": [
    {
      "CriterionName": "PositionLocation.Country",
      "CriterionValue": 46
    },
    {
      "CriterionName": "PositionLocation.City",
      "CriterionValue": 1698
    },
    null
  ]
}
```

- `LanguageCode`: Specifies the language for results (e.g., "en" for English)
- `SearchParameters`: Contains pagination, fields to return, and sorting information
- `SearchCriteria`: Contains filtering conditions (optional)

### Location Codes

The API uses numeric codes for countries and cities:

- Each country has a unique country code (e.g., 46)
- Each city has a unique city code (e.g., 1698)

A reference list of these codes can be built by inspecting the search API responses or by analyzing the website's search form.

## Usage

### Basic Usage

```bash
python db_search_api_scanner.py
```

This will scan jobs filtered by Country code 46 and City code 1698 (default settings).

### Filtering by Location

```bash
# Already filtering by country code 46 and city code 1698 by default

# To disable location filtering and scan all jobs
python db_search_api_scanner.py --country-code "None" --city-code "None"

# To use different location filters
python db_search_api_scanner.py --country-code 42 --city-code 1234
```

### Controlling Pagination

```bash
# Start from page 3
python db_search_api_scanner.py --start-page 3

# Retrieve 50 results per page
python db_search_api_scanner.py --results-per-page 50

# Limit to fetching only 5 pages
python db_search_api_scanner.py --max-pages 5
```

### Other Options

```bash
# Force start from page 1 (ignore saved progress)
python db_search_api_scanner.py --force-start

# Set custom delay between requests (in seconds)
python db_search_api_scanner.py --delay 3.5
```

## Comparison with Brute Force Scanner

| Feature | Search API Scanner | Brute Force Scanner |
|---------|-------------------|---------------------|
| Efficiency | Only processes actual jobs | Checks every possible ID |
| Speed | Faster, fewer requests | Slower, many wasted requests |
| Coverage | May miss some jobs depending on API | Can potentially find all jobs |
| Filtering | Built-in location filtering | Requires post-processing |
| Complexity | More complex API interaction | Simpler, sequential checks |

## Data Storage

Jobs are saved in the same format as the brute force scanner for compatibility, with the addition of a `search_details` field that contains the original search result data. This ensures that all existing processes and scripts that work with the job data will continue to function with the new scanner.

## Future Enhancements

1. **Extended Filtering**: Support additional filter criteria beyond location
2. **Keyword Search**: Implement keyword-based job searching
3. **Auto-discovery of Codes**: Build a reference database of country and city codes
4. **Scheduled Scanning**: Set up periodic scanning for new job postings
5. **Integration with Analytics**: Direct integration with job analysis tools

---

This tool represents a significant improvement over the brute force approach, drastically reducing the number of API requests needed to collect job listings while enhancing the ability to target specific subsets of jobs based on location or other criteria.
