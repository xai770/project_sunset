import pytest
from unittest.mock import patch, MagicMock
import json
from daily_report_pipeline.specialists.domain_classification_specialist_llm import (
    classify_job_domain_llm,
    validate_domain_signals,
    SUPPORTED_DOMAINS
)

# Test job descriptions
JOBS = {
    'tech': '''
    Senior Software Engineer - Cloud Platform
    
    We are seeking an experienced software engineer to join our cloud platform team.
    Skills required:
    - Python, JavaScript, and cloud technologies
    - Experience with AWS or Azure
    - Strong background in software architecture
    - DevOps and CI/CD experience
    ''',
    
    'finance': '''
    Investment Banking Analyst
    
    Top-tier investment bank seeks analysts for:
    - Financial modeling and valuation
    - M&A transaction support
    - Market research and analysis
    - Client presentation preparation
    '''
}

@patch('httpx.post')
def test_basic_classification(mock_post):
    mock_response = MagicMock()
    mock_response.json.return_value = {
        'response': json.dumps({
            'domain': 'technology',
            'confidence': 95.0,
            'domain_signals': ['software development', 'python', 'cloud'],
            'assessment': 'Strong technology focus'
        })
    }
    mock_post.return_value = mock_response
    
    result = classify_job_domain_llm(JOBS['tech'], job_id='test-1')
    
    assert isinstance(result, dict)
    assert result['domain'] == 'technology'
    assert result['confidence'] >= 90.0
    assert len(result['domain_signals']) >= 2
    assert result['proceed'] is True

def test_empty_input():
    result = classify_job_domain_llm('')
    
    assert isinstance(result, dict)
    assert result['domain'] == 'technology'
    assert result['confidence'] == 0.0
    assert result['proceed'] is False

def test_domain_signals_validation():
    signals = validate_domain_signals(JOBS['tech'], 'technology')
    assert len(signals) >= 2
    assert any('cloud' in signal.lower() for signal in signals)
    
    signals = validate_domain_signals(JOBS['finance'], 'finance')
    assert len(signals) >= 1
    assert any('financial' in signal.lower() for signal in signals)

@patch('httpx.post')
def test_llm_failure_handling(mock_post):
    mock_post.side_effect = Exception('LLM API Error')
    
    result = classify_job_domain_llm(JOBS['tech'])
    assert result['domain'] == 'technology'
    assert 'fallback' in result['domain_signals'][0].lower()
    assert result['proceed'] is True

@patch('httpx.post')
def test_with_metadata(mock_post):
    metadata = {
        'title': 'Senior Cloud Architect',
        'company': 'TechCorp',
        'department': 'Platform Engineering'
    }
    
    mock_response = MagicMock()
    mock_response.json.return_value = {
        'response': json.dumps({
            'domain': 'technology',
            'confidence': 95.0,
            'domain_signals': ['cloud architecture', 'platform engineering'],
            'assessment': 'Clear technology focus'
        })
    }
    mock_post.return_value = mock_response
    
    result = classify_job_domain_llm(JOBS['tech'], job_metadata=metadata)
    assert result['domain'] == 'technology'
    assert result['confidence'] >= 90.0
    assert result['proceed'] is True
