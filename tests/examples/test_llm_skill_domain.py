#!/usr/bin/env python3
"""
Test script to evaluate different LLM models for skill domain analysis.
This script tests various Ollama models to determine which performs best
for extracting domain information from skills.
"""

import sys
import os
import json
import logging
import time
import subprocess
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('llm_skill_domain_test')

class LLMSkillDomainTester:
    """Test different LLM models for skill domain analysis"""
    
    def __init__(self, models=None):
        """Initialize the tester
        
        Args:
            models: List of model names to test (default: auto-detect from ollama)
        """
        self.models = models or self._detect_available_models()
        self.results = {}
        self.test_skills = [
            "automation",
            "Business Process Automation",
            "CI/CD Deployment Automation",
            "Test Automation Framework Development",
            "project management",
            "Python programming"
        ]
        
    def _detect_available_models(self) -> List[str]:
        """Detect available Ollama models
        
        Returns:
            List of model names
        """
        try:
            result = subprocess.run(
                ["ollama", "list"],
                capture_output=True,
                text=True,
                check=True
            )
            
            lines = result.stdout.strip().split('\n')
            # Skip header line
            if len(lines) > 1:
                lines = lines[1:]
                
            models = []
            for line in lines:
                parts = line.split()
                if parts:
                    # Extract model name (without tag)
                    model_name = parts[0].split(':')[0] if ':' in parts[0] else parts[0]
                    models.append(model_name)
            
            return models
        except Exception as e:
            logger.error(f"Error detecting models: {e}")
            # Return some default models that might be available
            return ["llama3.2", "mistral", "phi4-mini-reasoning"]
    
    def call_ollama_api(self, prompt: str, model: str, temperature: float = 0.2) -> str:
        """Call Ollama API
        
        Args:
            prompt: Prompt to send to the model
            model: Model name
            temperature: Temperature for generation
            
        Returns:
            Generated text
        """
        try:
            # Try importing our existing client
            from scripts.utils.llm_client import call_ollama_api
            logger.info(f"Using existing llm_client to call {model}")
            return call_ollama_api(prompt, model=model, temperature=temperature)
        except ImportError:
            # Fallback to subprocess if our client isn't available
            logger.warning("Could not import call_ollama_api, using subprocess fallback")
            
            with open('/tmp/ollama_prompt.txt', 'w') as f:
                f.write(prompt)
                
            cmd = [
                "ollama", "run", model,
                f"--temp {temperature}",
                "--quiet",
                f"$(cat /tmp/ollama_prompt.txt)"
            ]
            
            try:
                result = subprocess.run(
                    " ".join(cmd),
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=60  # 60-second timeout
                )
                return result.stdout
            except subprocess.TimeoutExpired:
                logger.error(f"Timeout calling {model}")
                return ""
            except Exception as e:
                logger.error(f"Error calling {model}: {e}")
                return ""
    
    def generate_domain_extraction_prompt(self, skill: str) -> str:
        """Generate prompt for domain extraction
        
        Args:
            skill: Skill name
            
        Returns:
            Prompt for domain extraction
        """
        return f"""You are a professional skill domain analyzer. Your task is to extract the key components of the following skill:

SKILL: {skill}

Please analyze this skill and provide the following information in JSON format:
{{
  "name": "{skill}",
  "domain": "The professional domain this skill belongs to",
  "knowledge_components": [
    "List 5-8 specific knowledge areas required for this skill"
  ],
  "contexts": [
    "List 3-5 environments where this skill is typically applied"
  ],
  "functions": [
    "List 3-5 primary purposes or functions of this skill"
  ],
  "proficiency_level": "A number from 1-10 representing typical expertise level required"
}}

Focus on being precise and domain-specific in your analysis. Avoid generic descriptions.
Provide only the JSON output without additional commentary.
"""

    def parse_llm_json_response(self, response: str) -> Optional[Dict[str, Any]]:
        """Parse JSON from LLM response
        
        Args:
            response: String response from LLM
            
        Returns:
            Dictionary from JSON or None if parsing failed
        """
        try:
            # Find JSON content in response (may include markdown code blocks)
            import re
            json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response, re.DOTALL)
            
            if json_match:
                json_str = json_match.group(1)
            else:
                # Try to extract JSON without code blocks
                json_match = re.search(r'(\{.*\})', response, re.DOTALL)
                if json_match:
                    json_str = json_match.group(1)
                else:
                    json_str = response
            
            return json.loads(json_str)
        except Exception as e:
            logger.error(f"Error parsing JSON from LLM response: {e}")
            return None
    
    def validate_domain_info(self, domain_info: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate domain information
        
        Args:
            domain_info: Domain information dict
            
        Returns:
            Tuple of (is_valid, issues)
        """
        issues = []
        
        if not domain_info.get("name"):
            issues.append("Missing name")
            
        if not domain_info.get("domain"):
            issues.append("Missing domain")
            
        knowledge = domain_info.get("knowledge_components", [])
        if not knowledge:
            issues.append("Missing knowledge components")
        elif len(knowledge) < 3:
            issues.append(f"Too few knowledge components ({len(knowledge)})")
            
        contexts = domain_info.get("contexts", [])
        if not contexts:
            issues.append("Missing contexts")
        elif len(contexts) < 2:
            issues.append(f"Too few contexts ({len(contexts)})")
            
        functions = domain_info.get("functions", [])
        if not functions:
            issues.append("Missing functions")
        elif len(functions) < 2:
            issues.append(f"Too few functions ({len(functions)})")
            
        proficiency = domain_info.get("proficiency_level")
        if not proficiency:
            issues.append("Missing proficiency level")
        else:
            try:
                prof_level = int(proficiency)
                if prof_level < 1 or prof_level > 10:
                    issues.append(f"Invalid proficiency level ({prof_level})")
            except (ValueError, TypeError):
                issues.append(f"Non-numeric proficiency level ({proficiency})")
                
        return len(issues) == 0, issues
    
    def evaluate_model(self, model: str, skill: str) -> Dict[str, Any]:
        """Evaluate a model for domain extraction
        
        Args:
            model: Model name
            skill: Skill name
            
        Returns:
            Evaluation results
        """
        logger.info(f"Evaluating {model} for skill: {skill}")
        
        start_time = time.time()
        
        try:
            prompt = self.generate_domain_extraction_prompt(skill)
            response = self.call_ollama_api(prompt, model)
            
            duration = time.time() - start_time
            
            if not response:
                logger.warning(f"{model} returned empty response")
                return {
                    "model": model,
                    "skill": skill,
                    "success": False,
                    "duration": duration,
                    "is_valid_json": False,
                    "validation_issues": ["Empty response"]
                }
                
            # Parse response
            domain_info = self.parse_llm_json_response(response)
            
            if not domain_info:
                logger.warning(f"{model} returned invalid JSON")
                return {
                    "model": model,
                    "skill": skill,
                    "success": False,
                    "duration": duration,
                    "is_valid_json": False,
                    "validation_issues": ["Invalid JSON format"]
                }
                
            # Validate domain info
            is_valid, issues = self.validate_domain_info(domain_info)
            
            if not is_valid:
                logger.warning(f"{model} returned invalid domain info: {issues}")
            else:
                logger.info(f"{model} successfully extracted domain info for {skill}")
                
            return {
                "model": model,
                "skill": skill,
                "success": is_valid,
                "duration": duration,
                "is_valid_json": True,
                "domain_info": domain_info,
                "validation_issues": issues if not is_valid else []
            }
            
        except Exception as e:
            logger.error(f"Error evaluating {model} for {skill}: {e}")
            return {
                "model": model,
                "skill": skill,
                "success": False,
                "duration": time.time() - start_time,
                "is_valid_json": False,
                "validation_issues": [str(e)]
            }
    
    def run_tests(self) -> Dict[str, Dict[str, List[Dict[str, Any]]]]:
        """Run tests for all models and skills
        
        Returns:
            Dictionary mapping models to results
        """
        results = {
            "overall_results": {},
            "model_results": {},
            "skill_results": {},
            "detailed_results": []
        }
        
        for model in self.models:
            model_results = []
            
            for skill in self.test_skills:
                evaluation = self.evaluate_model(model, skill)
                model_results.append(evaluation)
                results["detailed_results"].append(evaluation)
                
            # Calculate success rate for this model
            success_count = sum(1 for r in model_results if r["success"])
            success_rate = success_count / len(model_results) if model_results else 0
            
            # Calculate average response time
            avg_time = sum(r["duration"] for r in model_results) / len(model_results) if model_results else 0
            
            results["model_results"][model] = {
                "success_rate": success_rate,
                "average_time": avg_time,
                "total_tests": len(model_results),
                "successful_tests": success_count
            }
        
        # Calculate overall best model
        if results["model_results"]:
            best_model = max(
                results["model_results"].items(),
                key=lambda x: (x[1]["success_rate"], -x[1]["average_time"])
            )[0]
            
            results["overall_results"]["best_model"] = best_model
            results["overall_results"]["best_success_rate"] = results["model_results"][best_model]["success_rate"]
            results["overall_results"]["best_average_time"] = results["model_results"][best_model]["average_time"]
        
        return results
    
    def save_results(self, results: Dict[str, Any], filename: str = None) -> str:
        """Save test results to file
        
        Args:
            results: Test results
            filename: Output filename (default: auto-generate)
            
        Returns:
            Path to saved file
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"llm_skill_domain_test_{timestamp}.json"
            
        # Create directory if it doesn't exist
        reports_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            "data",
            "reports"
        )
        os.makedirs(reports_dir, exist_ok=True)
        
        filepath = os.path.join(reports_dir, filename)
        
        with open(filepath, 'w') as f:
            json.dump(results, f, indent=2)
            
        logger.info(f"Saved results to {filepath}")
        return filepath
    
    def print_summary(self, results: Dict[str, Any]) -> None:
        """Print summary of test results
        
        Args:
            results: Test results
        """
        print("\n===== LLM SKILL DOMAIN ANALYSIS TEST RESULTS =====\n")
        
        if "overall_results" in results and results["overall_results"]:
            best = results["overall_results"]
            print(f"BEST MODEL: {best['best_model']}")
            print(f"  Success Rate: {best['best_success_rate'] * 100:.1f}%")
            print(f"  Average Time: {best['best_average_time']:.2f} seconds\n")
        
        print("MODEL PERFORMANCE:")
        for model, stats in sorted(
            results["model_results"].items(),
            key=lambda x: x[1]["success_rate"],
            reverse=True
        ):
            print(f"  {model}:")
            print(f"    Success Rate: {stats['success_rate'] * 100:.1f}%")
            print(f"    Average Time: {stats['average_time']:.2f} seconds")
            print(f"    Tests: {stats['successful_tests']}/{stats['total_tests']}\n")
            
        # Print detailed examples for "automation" skill
        print("DETAILED RESULTS FOR 'automation' SKILL:")
        auto_results = [r for r in results["detailed_results"] if r["skill"] == "automation" and r["success"]]
        
        if not auto_results:
            print("  No successful results for 'automation' skill\n")
        else:
            for result in auto_results[:1]:  # Just show the first successful result
                model = result["model"]
                info = result["domain_info"]
                
                print(f"  Model: {model}")
                print(f"  Domain: {info['domain']}")
                print(f"  Knowledge Components: {', '.join(info['knowledge_components'][:3])}...")
                print(f"  Contexts: {', '.join(info['contexts'][:2])}...")
                print(f"  Functions: {', '.join(info['functions'][:2])}...")
                print(f"  Proficiency Level: {info['proficiency_level']}\n")
                
        print(f"Full results saved to: {results['output_file']}")
        print("\n===================================================\n")

def main():
    """Main function"""
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description="Test LLM models for skill domain analysis")
    parser.add_argument(
        "--models",
        nargs="+",
        default=None,
        help="List of models to test (default: auto-detect)"
    )
    parser.add_argument(
        "--skills",
        nargs="+",
        default=None,
        help="List of skills to test (default: use predefined list)"
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Output file for results (default: auto-generate)"
    )
    
    args = parser.parse_args()
    
    # Create tester
    tester = LLMSkillDomainTester(models=args.models)
    
    # Override test skills if provided
    if args.skills:
        tester.test_skills = args.skills
        
    # Run tests
    results = tester.run_tests()
    
    # Save results
    output_file = tester.save_results(results, filename=args.output)
    results["output_file"] = output_file
    
    # Print summary
    tester.print_summary(results)
    
if __name__ == "__main__":
    main()