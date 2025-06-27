# Documents Directory

This directory contains the generated documents used in the job application process.

## Structure

- `cover_letters/` - Contains cover letters in both Markdown and Word format
- `job_descriptions/` - Contains job descriptions converted to Word format

## Cover Letters

The `cover_letters/` directory contains:

- **Markdown files** - Source format of cover letters
  - `Cover_Letter_XXXXX_*.md` - Cover letters generated from templates

- **Word documents** - Formatted versions for submission
  - `Cover_Letter_XXXXX_*.docx` - Word documents converted from Markdown

The naming convention includes the job ID and position title:
`Cover_Letter_[JOB_ID]_[JOB_TITLE].md`

## Job Descriptions

The `job_descriptions/` directory contains:

- **Word documents** - Job descriptions formatted for printing or reference
  - `job_XXXXX_*.docx` - Word documents generated from job posting JSON

## Workflow

1. Cover letters are created by `generate_cover_letter.py` in Markdown format
2. Markdown cover letters are converted to Word by `md_to_word_converter.py`
3. Job descriptions are converted from JSON to Word by `json_to_word.py`
4. All documents are sent via email using `email_sender.py`
