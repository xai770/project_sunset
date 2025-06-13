#!/usr/bin/env python3
"""
Advanced Job Scraper with Browser Automation
===========================================

Bypasses 403 Forbidden errors using Selenium with proper browser headers
"""

import time
import json
import logging
from typing import Optional, Dict, Any
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import TimeoutException, WebDriverException
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

class AdvancedJobScraper:
    """
    Advanced job scraper that uses browser automation to bypass anti-bot protection
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.career_site_base = "https://careers.db.com"
        self.driver = None
        
    def _setup_driver(self) -> bool:
        """Setup Chrome driver with proper options"""
        if not SELENIUM_AVAILABLE:
            self.logger.error("❌ Selenium not available. Install with: pip install selenium")
            return False
            
        try:
            chrome_options = Options()
            chrome_options.add_argument("--headless")  # Run in background
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # Set a real user agent
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
            
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            self.logger.info("✅ Chrome driver initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to setup Chrome driver: {e}")
            return False
    
    def scrape_job_description(self, job_id: str, position_uri: str) -> str:
        """
        Scrape job description using browser automation
        """
        if not self.driver and not self._setup_driver():
            return ""
            
        try:
            # Construct full URL
            if position_uri.startswith('http'):
                job_url = position_uri
            else:
                job_url = f"{self.career_site_base}{position_uri}"
            
            self.logger.info(f"🔍 Scraping job {job_id} from {job_url}")
            
            # Navigate to the page
            self.driver.get(job_url)
            
            # Wait for page to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Give it a moment for dynamic content
            time.sleep(2)
            
            # Try to find job description content
            description_selectors = [
                ".job-description",
                ".job-content", 
                ".position-description",
                "[data-testid='job-description']",
                ".description",
                "main",
                "#job-description"
            ]
            
            description_text = ""
            
            for selector in description_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        description_text = elements[0].text.strip()
                        if len(description_text) > 200:  # Good content length
                            break
                except Exception:
                    continue
            
            # Fallback: get all text content
            if not description_text or len(description_text) < 100:
                try:
                    body_element = self.driver.find_element(By.TAG_NAME, "body")
                    full_text = body_element.text
                    
                    # Try to extract meaningful sections
                    lines = [line.strip() for line in full_text.split('\n') if line.strip()]
                    
                    # Look for job-related content
                    job_content_lines = []
                    found_job_section = False
                    
                    for line in lines:
                        if any(keyword in line.lower() for keyword in 
                               ['responsibilities', 'requirements', 'qualifications', 'duties', 'experience']):
                            found_job_section = True
                        
                        if found_job_section and len(line) > 20:
                            job_content_lines.append(line)
                            
                        # Stop if we get too much content
                        if len('\n'.join(job_content_lines)) > 2000:
                            break
                    
                    if job_content_lines:
                        description_text = '\n'.join(job_content_lines)
                        
                except Exception as e:
                    self.logger.warning(f"⚠️ Failed to extract fallback content: {e}")
            
            if description_text and len(description_text) > 50:
                self.logger.info(f"✅ Successfully scraped {len(description_text)} characters")
                return description_text
            else:
                self.logger.warning(f"⚠️ No meaningful content found for job {job_id}")
                return ""
                
        except TimeoutException:
            self.logger.error(f"❌ Timeout loading job {job_id}")
            return ""
        except Exception as e:
            self.logger.error(f"❌ Error scraping job {job_id}: {e}")
            return ""
    
    def close(self):
        """Close the browser driver"""
        if self.driver:
            try:
                self.driver.quit()
                self.logger.info("🔒 Browser driver closed")
            except Exception as e:
                self.logger.warning(f"⚠️ Error closing driver: {e}")

def test_scraper():
    """Test the advanced scraper"""
    scraper = AdvancedJobScraper()
    
    try:
        # Test with one of our job URIs
        test_uri = "/index.php?ac=jobad&id=63183"
        description = scraper.scrape_job_description("63183", test_uri)
        
        if description:
            print(f"✅ Successfully scraped {len(description)} characters")
            print(f"Preview: {description[:200]}...")
        else:
            print("❌ No description scraped")
            
    finally:
        scraper.close()

if __name__ == "__main__":
    test_scraper()
