"""
LLM-based batch domain overlap matching (extracted from enhanced_skill_matcher.py)
"""
import os
import json
import logging
import requests
from typing import List, Tuple, Dict

logger = logging.getLogger("enhanced_skill_matcher.llm")

OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "gemma3:4b")

def batch_llm_domain_overlap(skill_pairs: List[Tuple[str, str]]) -> Dict[str, float]:
    if not skill_pairs:
        return {}
    comparisons = []
    for i, (skill1, skill2) in enumerate(skill_pairs):
        comparisons.append(f"COMPARISON {i+1}:\nSKILL A: {skill1}\nSKILL B: {skill2}")
    prompt = f"""Analyze domain overlap between the following skill pairs.\nFor each pair, consider: domain relatedness, knowledge overlap, context similarity, function similarity.\nRespond with a JSON object where keys are the comparison numbers and values are compatibility percentages (0-100).\n\n{chr(10).join(comparisons)}\nFormat your response EXACTLY as:\n{{\n  \"1\": compatibility_percentage,\n  \"2\": compatibility_percentage,\n  ...etc\n}}\nDo not include any other text or explanation."""
    try:
        url = f"{OLLAMA_HOST.rstrip('/')}/api/generate"
        payload = {
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.1, "num_predict": 2048, "num_ctx": 4096}
        }
        headers = {"Content-Type": "application/json"}
        response = requests.post(url, headers=headers, json=payload, timeout=120)
        if response.status_code == 200:
            data = response.json()
            text = data.get("response", "")
            start_idx = text.find('{')
            end_idx = text.rfind('}') + 1
            if start_idx >= 0 and end_idx > start_idx:
                json_str = text[start_idx:end_idx]
                try:
                    results = json.loads(json_str)
                    output = {}
                    for i, (skill1, skill2) in enumerate(skill_pairs):
                        key = f"{skill1}::{skill2}"
                        score_str = str(i+1)
                        if score_str in results:
                            pct = float(results[score_str])
                            output[key] = min(1.0, max(0.0, pct / 100.0))
                    return output
                except json.JSONDecodeError:
                    logger.warning(f"Failed to parse JSON from LLM response: {json_str}")
            else:
                logger.warning("Could not find JSON in LLM response")
        else:
            logger.warning(f"LLM response error: {response.status_code} - {response.text}")
    except Exception as e:
        logger.error(f"Batch LLM domain overlap failed: {e}")
    return {}
