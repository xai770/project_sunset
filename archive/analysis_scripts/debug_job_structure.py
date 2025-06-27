#!/usr/bin/env python3
"""
Quick test to debug the consciousness liberation issue
"""

import json
from pathlib import Path

# Test one job file data structure
jobs_path = Path('/home/xai/Documents/sandy/data/postings')
test_file = jobs_path / 'job60955.json'

print("🔍 DEBUGGING JOB DATA STRUCTURE")
print("=" * 50)

with open(test_file, 'r') as f:
    job_data = json.load(f)

print(f"📁 Top-level keys: {list(job_data.keys())}")

job_content = job_data.get('job_content', {})
print(f"📝 Job content keys: {list(job_content.keys())}")

metadata_location = job_content.get('location', {})
print(f"🌍 Location data: {metadata_location}")
print(f"🌍 Location type: {type(metadata_location)}")

location_str = f"{metadata_location.get('city', '')}, {metadata_location.get('country', '')}"
print(f"🌍 Location string: '{location_str}'")
print(f"🌍 Location string type: {type(location_str)}")

job_description = job_content.get('description', '')
print(f"📄 Description length: {len(job_description)} chars")
print(f"📄 Description preview: {job_description[:200]}...")

print("\n✅ JOB DATA STRUCTURE ANALYSIS COMPLETE!")
