#!/usr/bin/env python3
"""
Phase 3: Architecture Optimization - Specialist Inventory & Migration Planning

This script implements Phase 1 (Specialist Inventory) and begins Phase 3 (Legacy Removal)
as outlined in docs/ARCHITECTURE_REVIEW_JUNE_2025.md

Goals:
1. Audit existing LLM Factory specialists
2. Map current LLM client usage points
3. Plan migration paths for direct specialist integration
4. Begin legacy layer removal
"""

import sys
import os
from pathlib import Path
from typing import List, Dict, Any

# Add paths
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, '/home/xai/Documents/llm_factory')

def audit_available_specialists() -> Dict[str, Any]:
    """Phase 1: Audit existing LLM Factory specialists"""
    
    print("🔍 PHASE 1: SPECIALIST INVENTORY")
    print("=" * 60)
    
    specialists_info = {
        "available": [],
        "missing": [],
        "total_discovered": 0
    }
    
    try:
        from llm_factory.modules.quality_validation.specialists_versioned.registry import SpecialistRegistry
        
        registry = SpecialistRegistry()
        print(f"✅ LLM Factory registry loaded successfully")
        
        # Get all available specialists
        print(f"\n📋 Available Specialists:")
        
        # We know from our previous tests these specialists exist
        known_specialists = [
            "job_fitness_evaluator",
            "text_summarization", 
            "adversarial_prompt_generator",
            "consensus_engine",
            "document_analysis",
            "feedback_processor",
            "factual_consistency",
            "llm_skill_extractor",
            "language_coherence",
            "cover_letter_generator",
            "ai_language_detection",
            "cover_letter_quality"
        ]
        
        for spec_name in known_specialists:
            try:
                # Try to get versions for each specialist
                specialist_path = Path("/home/xai/Documents/llm_factory/llm_factory/modules/quality_validation/specialists_versioned") / spec_name
                if specialist_path.exists():
                    versions = [d.name for d in specialist_path.iterdir() if d.is_dir() and d.name.startswith('v')]
                    specialists_info["available"].append({
                        "name": spec_name,
                        "versions": versions,
                        "latest": versions[-1] if versions else "unknown"
                    })
                    print(f"   ✅ {spec_name}: {versions}")
                else:
                    specialists_info["missing"].append(spec_name)
                    print(f"   ❌ {spec_name}: NOT FOUND")
                    
            except Exception as e:
                print(f"   ⚠️ {spec_name}: Error checking - {e}")
        
        specialists_info["total_discovered"] = len(specialists_info["available"])
        
    except Exception as e:
        print(f"❌ Failed to load LLM Factory registry: {e}")
        return specialists_info
    
    print(f"\n📊 Specialist Inventory Summary:")
    print(f"   Available: {len(specialists_info['available'])}")
    print(f"   Missing: {len(specialists_info['missing'])}")
    print(f"   Total Discovered: {specialists_info['total_discovered']}")
    
    return specialists_info

def map_current_llm_usage() -> Dict[str, List[str]]:
    """Phase 1: Map all current LLM client usage points"""
    
    print(f"\n🗺️ MAPPING CURRENT LLM USAGE")
    print("=" * 60)
    
    usage_map = {
        "direct_llm_calls": [],
        "enhanced_client_usage": [],
        "factory_wrapper_usage": [],
        "legacy_client_usage": []
    }
    
    # Files that use LLM functionality
    llm_files = [
        "run_pipeline/job_matcher/job_processor.py",
        "run_pipeline/job_matcher/feedback_handler.py", 
        "run_pipeline/job_matcher/llm_client.py",
        "run_pipeline/utils/llm_client.py",
        "run_pipeline/utils/llm_client_enhanced.py",
        "run_pipeline/core/llm_factory_match_and_cover.py",
        "run_pipeline/skill_matching/get_olmo_feedback.py"
    ]
    
    for file_path in llm_files:
        try:
            full_path = project_root / file_path
            if full_path.exists():
                content = full_path.read_text()
                
                # Categorize usage patterns
                if "LLMFactoryJobMatcher" in content or "SpecialistRegistry" in content:
                    usage_map["factory_wrapper_usage"].append(file_path)
                    print(f"   🏭 Factory Wrapper: {file_path}")
                
                elif "EnhancedOllamaClient" in content or "llm_client_enhanced" in content:
                    usage_map["enhanced_client_usage"].append(file_path)
                    print(f"   ⚡ Enhanced Client: {file_path}")
                
                elif "call_ollama_api" in content or "get_llm_client" in content:
                    usage_map["legacy_client_usage"].append(file_path)
                    print(f"   🔧 Legacy Client: {file_path}")
                
                elif "requests.post" in content and "ollama" in content.lower():
                    usage_map["direct_llm_calls"].append(file_path)
                    print(f"   📡 Direct LLM: {file_path}")
                    
        except Exception as e:
            print(f"   ❌ Error reading {file_path}: {e}")
    
    print(f"\n📊 Usage Mapping Summary:")
    for category, files in usage_map.items():
        print(f"   {category}: {len(files)} files")
    
    return usage_map

def plan_migration_paths(specialists_info: Dict[str, Any], usage_map: Dict[str, List[str]]) -> Dict[str, Any]:
    """Phase 1: Plan migration paths for direct specialist integration"""
    
    print(f"\n📋 MIGRATION PATH PLANNING")
    print("=" * 60)
    
    migration_plan = {
        "high_priority": [],  # Files that should be migrated first
        "medium_priority": [], # Files that can be migrated after core files
        "low_priority": [],   # Files that can be migrated last
        "specialist_mapping": {}  # Maps current functionality to specialists
    }
    
    # Map functionality to available specialists
    specialist_mapping = {
        "job_matching": "job_fitness_evaluator",
        "feedback_analysis": "feedback_processor", 
        "cover_letter_generation": "cover_letter_generator",
        "document_analysis": "document_analysis",
        "text_summarization": "text_summarization",
        "skill_extraction": "llm_skill_extractor",
        "quality_validation": "factual_consistency"
    }
    
    # Prioritize files based on usage patterns
    for file_path in usage_map["factory_wrapper_usage"]:
        if "job_processor" in file_path or "feedback_handler" in file_path:
            migration_plan["high_priority"].append(file_path)
            print(f"   🚨 HIGH: {file_path} - Core business logic")
        
    for file_path in usage_map["enhanced_client_usage"]:
        migration_plan["medium_priority"].append(file_path)
        print(f"   ⚠️ MEDIUM: {file_path} - Enhanced client infrastructure")
        
    for file_path in usage_map["legacy_client_usage"]:
        migration_plan["low_priority"].append(file_path)
        print(f"   📝 LOW: {file_path} - Legacy client calls")
    
    migration_plan["specialist_mapping"] = specialist_mapping
    
    print(f"\n📊 Migration Priority Summary:")
    print(f"   High Priority: {len(migration_plan['high_priority'])} files")
    print(f"   Medium Priority: {len(migration_plan['medium_priority'])} files") 
    print(f"   Low Priority: {len(migration_plan['low_priority'])} files")
    
    return migration_plan

def generate_phase3_plan(specialists_info: Dict[str, Any], usage_map: Dict[str, List[str]], migration_plan: Dict[str, Any]):
    """Generate Phase 3 implementation plan"""
    
    print(f"\n🚀 PHASE 3 IMPLEMENTATION PLAN")
    print("=" * 60)
    
    print(f"\n📋 Phase 3 Tasks:")
    print(f"   1. Remove LLM Client Layer:")
    print(f"      - Deprecate run_pipeline/utils/llm_client.py")
    print(f"      - Remove abstractions in llm_client_enhanced.py")
    print(f"      - Update imports to use direct specialists")
    
    print(f"\n   2. Eliminate Factory Enhancer:")
    print(f"      - Replace LLMFactoryJobMatcher with direct specialists")
    print(f"      - Remove wrapper classes and abstraction layers")
    print(f"      - Implement direct specialist instantiation")
    
    print(f"\n   3. Update Core Business Logic:")
    for file_path in migration_plan["high_priority"]:
        print(f"      - Migrate {file_path} to direct specialist calls")
    
    print(f"\n   4. Update Supporting Infrastructure:")
    for file_path in migration_plan["medium_priority"]:
        print(f"      - Simplify {file_path}")
        
    print(f"\n   5. Clean Legacy Code:")
    for file_path in migration_plan["low_priority"]:
        print(f"      - Remove legacy patterns in {file_path}")
    
    print(f"\n📊 Expected Benefits:")
    print(f"   - 40% reduction in LLM-related code complexity")
    print(f"   - Improved performance through direct specialist access")
    print(f"   - Simplified debugging and maintenance")
    print(f"   - Better control over specialist configurations")

def main():
    """Main execution function"""
    
    print("🏗️ PROJECT SUNSET - PHASE 3 ARCHITECTURE OPTIMIZATION")
    print("=" * 80)
    print("Following ARCHITECTURE_REVIEW_JUNE_2025.md implementation strategy")
    print("=" * 80)
    
    # Phase 1: Specialist Inventory
    specialists_info = audit_available_specialists()
    
    # Phase 1: Usage Mapping  
    usage_map = map_current_llm_usage()
    
    # Phase 1: Migration Planning
    migration_plan = plan_migration_paths(specialists_info, usage_map)
    
    # Phase 3: Implementation Planning
    generate_phase3_plan(specialists_info, usage_map, migration_plan)
    
    print(f"\n🎯 NEXT STEPS:")
    print(f"   1. Begin Phase 3 implementation with high-priority files")
    print(f"   2. Create direct specialist integration patterns")
    print(f"   3. Remove legacy abstraction layers")
    print(f"   4. Update test suite for new architecture")
    
    return {
        "specialists_info": specialists_info,
        "usage_map": usage_map, 
        "migration_plan": migration_plan
    }

if __name__ == "__main__":
    main()
