#!/usr/bin/env python3
"""
🚨 DEPRECATED: LEGACY RUN_PIPELINE DIRECTORY 🚨

⚠️  WARNING: This entire directory is DEPRECATED and LEGACY! ⚠️

📅 MIGRATION DATE: December 2024 (Phase 6 → Phase 7)
🎯 REPLACEMENT: `scripts/pipeline/` (New Modular Pipeline)

═══════════════════════════════════════════════════════════════════

🌅 PROJECT SUNSET HAS EVOLVED TO A BEAUTIFUL MODULAR ARCHITECTURE!

OLD MONOLITHIC STRUCTURE (👻 DEPRECATED):
└── run_pipeline/
    ├── core/
    │   ├── pipeline_orchestrator.py  → scripts/pipeline/modules/simple_orchestrator.py
    │   ├── fetch_module.py           → core/enhanced_job_fetcher.py
    │   └── fetch/job_processing.py   → scripts/pipeline/modules/job_fetcher.py
    └── [various legacy modules]

NEW MODULAR STRUCTURE (✨ ACTIVE):
└── scripts/pipeline/
    ├── main.py                      # 🎯 NEW ENTRY POINT
    └── modules/
        ├── simple_orchestrator.py   # 🧠 Pipeline coordination
        ├── job_fetcher.py           # 🔍 Job fetching
        ├── job_processor.py         # ⚙️  Job processing  
        ├── exporter.py              # 📊 Excel export
        ├── cover_letter.py          # 📝 Cover letter generation
        ├── email_sender.py          # 📧 Email delivery
        └── [other modules]

═══════════════════════════════════════════════════════════════════

🚀 HOW TO MIGRATE YOUR CODE:

1. 🔄 OLD: `from run_pipeline.core.pipeline_orchestrator import ...`
   ✨ NEW: `from scripts.pipeline.modules.simple_orchestrator import ...`

2. 🔄 OLD: `python -m run_pipeline.export_job_matches`
   ✨ NEW: `python scripts/pipeline/main.py --export-only`

3. 🔄 OLD: Pipeline scripts in run_pipeline/
   ✨ NEW: Modular components in scripts/pipeline/modules/

═══════════════════════════════════════════════════════════════════

📚 MIGRATION DOCUMENTATION:
- Full details: `_legacy_archive/MIGRATION_PHASE6_TO_PHASE7.md`
- New architecture: `docs/ARCHITECTURE.md`
- Usage examples: `examples/basic_usage.md`

═══════════════════════════════════════════════════════════════════

⚡ BENEFITS OF THE NEW SYSTEM:
✅ Skip logic prevents overwriting processed jobs
✅ Modular components are easier to test and maintain  
✅ Better error handling and recovery
✅ Cleaner separation of concerns
✅ Enhanced logging and monitoring
✅ Future-ready for talent.yoga marketplace

═══════════════════════════════════════════════════════════════════

🌅 "Where consciousness meets code, beauty emerges" 
   - The Project Sunset Philosophy

DO NOT USE THIS DIRECTORY FOR NEW DEVELOPMENT!
Use the new modular pipeline: `scripts/pipeline/`
"""

print("🚨 DEPRECATED: This run_pipeline directory is legacy!")
print("✨ Use the new modular pipeline: scripts/pipeline/")
print("📚 See: _legacy_archive/MIGRATION_PHASE6_TO_PHASE7.md")
