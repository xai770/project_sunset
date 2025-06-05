# Anti-Scraping Module Refactoring

## Summary of Changes (May 11, 2025)

This document summarizes the refactoring of the anti-scraping module to address 403 Forbidden errors and other challenges in the career pipeline.

## Key Changes

### 1. Module Restructuring
- Split monolithic `anti_scraping.py` into multiple modules:
  - `anti_scraping/base.py`: Core functionality and dependencies
  - `anti_scraping/session.py`: Session management 
  - `anti_scraping/utils.py`: Utility functions
  - `anti_scraping/site_specific.py`: Site-specific handlers
- Created compatibility wrapper in original `anti_scraping.py`

### 2. Anti-403 Improvements
- Enhanced user-agent rotation with modern browser signatures
- Implemented progressive retry logic with increasingly aggressive anti-detection measures
- Added site-specific handler for Deutsche Bank careers site
- Improved cookie and header management

### 3. Integration Work
- Updated TLM job extractor to use specialized DB careers handler
- Fixed import handling and dependency management
- Added proper error handling when dependencies aren't available

### 4. Testing and Verification
- Created `verify_anti_scraping.py` to test the refactored modules
- Implemented unit tests for different aspects of anti-scraping
- Created a migration script for easier transition

## File Changes

| File | Changes |
|------|---------|
| `utils/anti_scraping.py` | Converted to compatibility wrapper |
| `utils/anti_scraping/base.py` | Core functionality, imports, dependencies |
| `utils/anti_scraping/session.py` | AntiScrapingSession class |  
| `utils/anti_scraping/utils.py` | Helper functions |
| `utils/anti_scraping/site_specific.py` | Site-specific handlers |
| `utils/anti_scraping/__init__.py` | Package exports |
| `utils/anti_scraping/requirements.txt` | Dependencies |
| `verify_anti_scraping.py` | Testing script |
| `migrate_anti_scraping.py` | Migration script |
| `setup_anti_scraping.sh` | Setup script |

## Implementation Notes

### Handling 403 Errors
The refactored module uses a three-step approach to handle 403 Forbidden errors:

1. **Standard Request**: First attempt with normal headers
2. **Enhanced Headers**: If 403, retry with browser-like headers and user-agent rotation
3. **Fresh Session**: If still 403, create a completely new session with referrer spoofing

### Deutsche Bank Careers Handler
The specialized handler for DB careers (`get_db_careers_page`) implements additional techniques:

1. Uses longer delays (2-5 seconds) to avoid rate limiting
2. Visits the main careers page first to establish cookies
3. Employs Google search referrer to appear as organic traffic

## Usage Examples

### Basic Usage
```python
from scripts.career_pipeline.utils.anti_scraping import get_with_anti_scraping

response = get_with_anti_scraping("https://careers.db.com/...")
```

### Using the DB Careers Handler
```python
from scripts.career_pipeline.utils.anti_scraping import get_db_careers_page

response = get_db_careers_page("https://careers.db.com/...")
```

### Custom Session
```python
from scripts.career_pipeline.utils.anti_scraping import create_session

session = create_session(min_delay=2.0, max_delay=5.0)
response = session.get("https://careers.db.com/...")
```

## Next Steps

1. **Monitor Success Rates**: Track success rates with the new methods
2. **Extend Coverage**: Create handlers for other career portals
3. **Integration**: Further integrate with TLM for adaptive scraping strategies
4. **Proxy Support**: Add proxy rotation for highly protected sites
5. **User-Agent Learning**: Implement success-based learning for user-agent selection
