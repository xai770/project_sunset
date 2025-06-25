# LLM Factory Deployment Guide for Customers

## ✅ Recommended Deployment Approach: Direct Path Integration

Based on thorough testing and analysis, the **recommended deployment approach** for using LLM Factory in your customer project is **direct path integration** rather than pip installation.

### Why Direct Path Integration?

- **✅ 100% Functional**: All 6 modules work perfectly
- **✅ No Import Conflicts**: Avoids Python packaging namespace issues
- **✅ Simple Setup**: Easy to implement and maintain
- **✅ Full Control**: You have complete control over the LLM Factory code

## 🚀 Quick Start

### Step 1: Setup Your Project Structure

```
your_project/
├── your_code.py
├── llm_factory_integration.py  # Your integration file
└── requirements.txt
```

### Step 2: Basic Integration Pattern

```python
import sys
import os

# Add LLM Factory to Python path
sys.path.insert(0, '/home/xai/Documents/llm_factory')

# Import LLM Factory components
from llm_factory.core.module_factory import ModuleFactory
from llm_factory.core.ollama_client import OllamaClient

# Initialize factory
factory = ModuleFactory()
ollama_client = OllamaClient()

# Use modules
modules = factory.list_modules()
print(f"Available modules: {len(modules)}")
```

## 📋 Available Modules

Your LLM Factory installation provides **6 working modules**:

| Module | Purpose | Category |
|--------|---------|----------|
| `content_analysis.specialists_versioned.sentimentanalysisspecialist` | Sentiment Analysis | Content Analysis |
| `content_generation.textsummarizer` | Text Summarization | Content Generation |
| `content_generation.specialists_versioned.textsummarizationspecialist` | Advanced Text Summarization | Content Generation |
| `decision_making.specialists_versioned.contentclassificationspecialist` | Content Classification | Decision Making |
| `quality_validation.basespecialist` | Base Quality Validation | Quality Control |
| `quality_validation.coverlettervalidator` | Cover Letter Validation | Quality Control |

## 💡 Usage Examples

### Text Summarization

```python
# Get text summarizer module
summarizer = factory.get_module(
    "content_generation.textsummarizer", 
    config={"ollama_client": ollama_client}
)

# Process text
result = summarizer.process({
    "text": "Your long text here...",
    "summary_length": "short"  # or "medium", "long"
})

if result.success:
    summary = result.data.get('summary')
    print(f"Summary: {summary}")
```

### Sentiment Analysis

```python
# Get sentiment analysis module
sentiment_analyzer = factory.get_module(
    "content_analysis.specialists_versioned.sentimentanalysisspecialist",
    config={"ollama_client": ollama_client}
)

# Analyze sentiment
result = sentiment_analyzer.process({
    "text": "This is a great product! I love it."
})

if result.success:
    sentiment = result.data.get('sentiment')
    print(f"Sentiment: {sentiment}")
```

### Content Classification

```python
# Get content classifier
classifier = factory.get_module(
    "decision_making.specialists_versioned.contentclassificationspecialist",
    config={"ollama_client": ollama_client}
)

# Classify content
result = classifier.process({
    "text": "Your content to classify...",
    "categories": ["technology", "business", "science"]
})

if result.success:
    classification = result.data.get('classification')
    print(f"Classification: {classification}")
```

## 🛠️ Prerequisites

### 1. Ollama Installation

Ensure Ollama is installed and running:

```bash
# Check if Ollama is installed
ollama --version

# Pull a model (if not already available)
ollama pull llama3.2:1b

# Verify models
ollama list
```

### 2. Python Dependencies

The LLM Factory uses these main dependencies:
- `requests` - For HTTP communication with Ollama
- `pydantic` - For data validation
- Standard library modules

## 📁 Project Structure Recommendations

### Option 1: Relative Path (Recommended)

If both projects are in the same parent directory:

```python
import sys
import os

# Add relative path to LLM Factory
project_root = os.path.dirname(os.path.abspath(__file__))
llm_factory_path = os.path.join(project_root, '..', 'llm_factory')
sys.path.insert(0, llm_factory_path)
```

### Option 2: Absolute Path

```python
import sys
sys.path.insert(0, '/home/xai/Documents/llm_factory')
```

### Option 3: Environment Variable

```python
import sys
import os

llm_factory_path = os.environ.get('LLM_FACTORY_PATH', '/home/xai/Documents/llm_factory')
sys.path.insert(0, llm_factory_path)
```

## 🔧 Best Practices

### 1. Error Handling

```python
try:
    from llm_factory.core.module_factory import ModuleFactory
    factory = ModuleFactory()
except ImportError as e:
    print(f"Error importing LLM Factory: {e}")
    print("Please check the LLM Factory path is correct")
    sys.exit(1)
```

### 2. Module Availability Check

```python
def check_module_availability(factory, module_name):
    """Check if a specific module is available"""
    modules = factory.list_modules()
    available_names = [m['name'] for m in modules]
    return module_name in available_names

# Usage
if check_module_availability(factory, "content_generation.textsummarizer"):
    summarizer = factory.get_module("content_generation.textsummarizer")
```

### 3. Configuration Management

```python
class LLMFactoryConfig:
    def __init__(self):
        self.llm_factory_path = '/home/xai/Documents/llm_factory'
        self.ollama_base_url = 'http://localhost:11434'
        self.default_model = 'llama3.2:1b'

config = LLMFactoryConfig()
```

## 🚨 Important Notes

### Do NOT Use pip install

❌ **Avoid this approach:**
```bash
pip install -e /home/xai/Documents/llm_factory
```

This creates namespace package conflicts and import errors.

### ✅ Use Direct Path Integration Instead

The direct path approach provides 100% functionality without any conflicts.

## 🔍 Troubleshooting

### Module Not Found Errors

```python
# Debug module loading
import sys
print("Python path:", sys.path)

try:
    from llm_factory.core.module_factory import ModuleFactory
    print("✅ LLM Factory imported successfully")
except ImportError as e:
    print(f"❌ Import error: {e}")
```

### Ollama Connection Issues

```python
from llm_factory.core.ollama_client import OllamaClient

client = OllamaClient()
try:
    models = client.available_models()
    print(f"✅ Ollama connected, models: {models}")
except Exception as e:
    print(f"❌ Ollama connection error: {e}")
```

## 📚 Complete Integration Example

See the file `llm_factory_example.py` in your project directory for a complete working example that demonstrates:

- Factory initialization
- Module listing
- Ollama client setup
- Text summarization usage
- Error handling

## 🎯 Summary

The **direct path integration approach** is the definitive solution for deploying LLM Factory in customer environments. It provides:

- ✅ **100% Module Availability** (6/6 modules working)
- ✅ **No Installation Conflicts**
- ✅ **Simple Implementation**
- ✅ **Full Functionality**
- ✅ **Easy Maintenance**

This approach ensures your customers can leverage the full power of the LLM Factory system with minimal setup complexity and maximum reliability.
