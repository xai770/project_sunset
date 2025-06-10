#!/usr/bin/env python3
"""
Lightweight Phase 3 Direct Specialist Test
==========================================

Test only the direct specialist manager without heavy dependencies.
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_direct_import():
    """Test direct import of specialist manager"""
    print("🔍 Testing direct specialist manager import...")
    
    try:
        from run_pipeline.core.direct_specialist_manager import (
            DirectSpecialistManager,
            get_job_matching_specialists,
            get_feedback_specialists,
            is_direct_specialists_available
        )
        print("✅ Direct specialist manager imports successful")
        return True
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

def test_specialist_instantiation():
    """Test creating specialist instances"""
    print("🔍 Testing specialist instantiation...")
    
    try:
        from run_pipeline.core.direct_specialist_manager import DirectSpecialistManager
        
        # Create manager
        manager = DirectSpecialistManager()
        print(f"✅ DirectSpecialistManager created: {type(manager)}")
        
        # Check availability
        available = manager.is_available()
        print(f"📊 Specialists available: {available}")
        
        # Get status
        status = manager.get_status()
        print(f"📋 Status: {status}")
        
        return True
    except Exception as e:
        print(f"❌ Instantiation failed: {e}")
        return False

def test_job_matching_specialists():
    """Test job matching specialist access"""
    print("🔍 Testing job matching specialists...")
    
    try:
        from run_pipeline.core.direct_specialist_manager import get_job_matching_specialists
        
        specialists = get_job_matching_specialists()
        print(f"✅ Job matching specialists created: {type(specialists)}")
        
        # Test basic attributes
        print(f"📊 Model: {specialists.model}")
        print(f"📊 Registry available: {specialists.registry is not None}")
        print(f"📊 Client available: {specialists.client is not None}")
        
        return True
    except Exception as e:
        print(f"❌ Job matching specialists failed: {e}")
        return False

def test_feedback_specialists():
    """Test feedback specialist access"""
    print("🔍 Testing feedback specialists...")
    
    try:
        from run_pipeline.core.direct_specialist_manager import get_feedback_specialists
        
        specialists = get_feedback_specialists()
        print(f"✅ Feedback specialists created: {type(specialists)}")
        
        return True
    except Exception as e:
        print(f"❌ Feedback specialists failed: {e}")
        return False

def main():
    """Run lightweight Phase 3 tests"""
    print("🚀 PHASE 3 DIRECT SPECIALIST LIGHTWEIGHT TEST")
    print("=" * 60)
    
    tests = [
        test_direct_import,
        test_specialist_instantiation,
        test_job_matching_specialists,
        test_feedback_specialists
    ]
    
    results = []
    for test in tests:
        print()
        result = test()
        results.append(result)
        
    print("\n" + "=" * 60)
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"✅ ALL TESTS PASSED ({passed}/{total})")
        print("🎉 Phase 3 Direct Specialist Manager working correctly!")
        return True
    else:
        print(f"❌ SOME TESTS FAILED ({passed}/{total})")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
