#!/usr/bin/env python3
"""
🚨 DEPRECATED ENTRY POINT - PLEASE USE NEW MODULAR PIPELINE! 🚨

🌅 Welcome to Project Sunset! 

⚠️  This root-level main.py is deprecated. Please use the new modular pipeline:

✨ NEW ENTRY POINT: scripts/pipeline/main.py

🚀 EXAMPLES:
  python scripts/pipeline/main.py --health-check    # System health check
  python scripts/pipeline/main.py --run-all         # Full pipeline run
  python scripts/pipeline/main.py --export-only     # Export to Excel
  python scripts/pipeline/main.py --help            # See all options

📚 MIGRATION GUIDE: _legacy_archive/MIGRATION_PHASE6_TO_PHASE7.md

═══════════════════════════════════════════════════════════════════
🎯 WHY THE NEW SYSTEM IS BETTER:
✅ Skip logic prevents overwriting processed jobs
✅ Modular components are easier to test and maintain  
✅ Better error handling and recovery
✅ Force reprocess option with --force-reprocess flag
✅ Enhanced logging and monitoring
✅ Future-ready for talent.yoga marketplace
═══════════════════════════════════════════════════════════════════

🌅 "Where consciousness meets code, beauty emerges"
"""

import sys
import os

def main():
    print("🚨 DEPRECATED: This entry point is legacy!")
    print("✨ Please use: python scripts/pipeline/main.py")
    print("")
    print("🚀 Quick migration:")
    print("  OLD: python main.py --run-all")
    print("  NEW: python scripts/pipeline/main.py --run-all")
    print("")
    print("📚 Full guide: _legacy_archive/MIGRATION_PHASE6_TO_PHASE7.md")
    print("")
    
    # Check if they passed arguments and offer to redirect
    if len(sys.argv) > 1:
        args = ' '.join(sys.argv[1:])
        print(f"💡 TIP: Run this instead:")
        print(f"  python scripts/pipeline/main.py {args}")
        print("")
        
        response = input("🤔 Would you like me to run the new pipeline for you? (y/N): ")
        if response.lower().startswith('y'):
            print("🚀 Redirecting to new modular pipeline...")
            import subprocess
            cmd = [sys.executable, "scripts/pipeline/main.py"] + sys.argv[1:]
            os.execv(sys.executable, cmd)
    
    return 1

if __name__ == "__main__":
    sys.exit(main())
