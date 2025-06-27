# 🎨 PROJECT SUNSET EXAMPLES

Quick demonstrations of our beautiful pipeline capabilities.

---

## 🚀 **BASIC USAGE**

### **Check System Health**
```bash
python main.py --health-check
```

### **Run Complete Pipeline**
```bash
python main.py --run-all
```

### **Check Pipeline Status**  
```bash
python core/status_manager.py --dashboard
```

---

## 🇩🇪 **FRANKFURT JOB PIPELINE**

### **Fetch Frankfurt Jobs**
```bash
python main.py --fetch-jobs
```

### **Process with LLM Evaluation**
```bash
python main.py --process-jobs
```

### **Export to Excel**
```bash
python -m run_pipeline.export_job_matches --feedback-system
```

---

## 🔍 **SEARCH CRITERIA MANAGEMENT**

### **View Active Profile**
```bash
python core/search_criteria_manager.py
```

### **List All Profiles**
```bash
python core/search_criteria_manager.py --list-profiles
```

### **Clean Non-matching Jobs**
```bash
python core/search_criteria_manager.py --cleanup
```

---

## 📊 **STATUS MANAGEMENT**

### **Show Status Dashboard**
```bash
python core/status_manager.py --dashboard
```

### **Find Jobs at Specific Status**
```bash
python core/status_manager.py --status 1  # fetched
python core/status_manager.py --status 3  # processed
```

### **Update Job Status**
```bash
python core/status_manager.py --update 64045 3  # advance job to processed
```

---

## 💫 **ADVANCED WORKFLOWS**

### **Multi-User Profile Setup**
```python
# Add new user profile to config/search_criteria.json
{
  "sarah_pm_focus": {
    "description": "Sarah's Product Management focus",
    "active": false,
    "criteria": {
      "locations": {"cities": ["Berlin", "Hamburg"]},
      "domains": {"preferred": ["Product Management"]}
    }
  }
}
```

### **Custom Job Processing**
```python
from core.status_manager import StatusManager
from core.search_criteria_manager import SearchCriteriaManager

# Check job status
manager = StatusManager()
manager.print_status_dashboard()

# Filter jobs by criteria
criteria = SearchCriteriaManager()
profile = criteria.get_active_profile()
print(criteria.get_profile_summary())
```

---

*These examples showcase the beauty and power of our revolutionary pipeline!* ✨
