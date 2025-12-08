# V6 Implementation Guide: AI-Powered Suggestions

## Overview

V6 adds real LLM integration to Auto Refactor AI, enabling AI-powered refactoring suggestions. The tool can now connect to multiple LLM providers (OpenAI, Anthropic, Google, or local Ollama) to generate context-aware code improvements.

## Goals

1. Integrate LLM providers for code refactoring suggestions
2. Support multiple providers (OpenAI, Anthropic, Google, Ollama)
3. Generate before/after code comparisons
4. Provide explanation of changes made
5. Enable cost estimation and token tracking

## New Features

### 1. `--ai-suggestions` Flag

Get AI-powered refactoring suggestions:

```bash
# Auto-detect provider (checks for API keys)
auto-refactor-ai mycode.py --ai-suggestions

# Specify provider
auto-refactor-ai mycode.py --ai-suggestions --ai-provider openai

# Specify model
auto-refactor-ai mycode.py --ai-suggestions --ai-model gpt-4o

# Limit issues analyzed
auto-refactor-ai mycode.py --ai-suggestions --ai-max-issues 3
```

### 2. `--check-providers` Flag

Check which LLM providers are available:

```bash
$ auto-refactor-ai . --check-providers

🔧 LLM Provider Status:
  ✅ Openai: Available
  ❌ Anthropic: Not configured (ANTHROPIC_API_KEY)
  ❌ Google: Not configured (GOOGLE_API_KEY)
  ❌ Ollama: Not configured ((local))
```

### 3. Multiple LLM Providers

| Provider | Models | Environment Variable |
|----------|--------|---------------------|
| OpenAI | gpt-4o, gpt-4o-mini, gpt-4-turbo | `OPENAI_API_KEY` |
| Anthropic | claude-3-opus, claude-3-sonnet, claude-3-haiku | `ANTHROPIC_API_KEY` |
| Google | gemini-1.5-pro, gemini-1.5-flash | `GOOGLE_API_KEY` |
| Ollama | codellama, llama2, mistral | Local (no key needed) |

## Architecture

### New Modules

```
auto_refactor_ai/
├── __init__.py
├── __main__.py
├── analyzer.py           # Core analysis (V0-V4)
├── cli.py                # Updated with AI flags (V6)
├── config.py             # Configuration (V2)
├── explanations.py       # Template explanations (V5)
├── llm_providers.py      # NEW: LLM provider abstraction (V6)
└── ai_suggestions.py     # NEW: AI suggestion generation (V6)
```

### Module: `llm_providers.py`

Provides a unified interface to multiple LLM providers:

```python
# Core classes
class LLMProvider(Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    OLLAMA = "ollama"

@dataclass
class LLMConfig:
    provider: LLMProvider
    model: str
    api_key: Optional[str]
    temperature: float = 0.3
    max_tokens: int = 2000

@dataclass
class RefactoringSuggestion:
    original_code: str
    refactored_code: str
    explanation: str
    confidence: float
    changes_summary: List[str]

class BaseLLMProvider(ABC):
    def generate(self, prompt: str, system_prompt: str) -> LLMResponse
    def get_refactoring_suggestion(code, issue_type, message, function_name)
```

### Module: `ai_suggestions.py`

Orchestrates AI-powered code analysis:

```python
def extract_function_source(file_path, start_line, end_line) -> str
def get_ai_suggestions(issues, config, max_issues, skip_info) -> AIAnalysisSummary
def format_ai_suggestion(result, show_original) -> str
def print_ai_suggestions(summary, show_original) -> None
```

## Example Output

```bash
$ auto-refactor-ai test_files/test_length_issues.py --ai-suggestions

🤖 Generating AI refactoring suggestions...
   Analyzing up to 5 issues...

================================================================================
🤖 AI REFACTORING SUGGESTION
================================================================================
File: test_files/test_length_issues.py:1-55
Function: very_long_function()
Issue: function-too-long (CRITICAL)
Problem: Function 'very_long_function' is 55 lines long (max: 30)
--------------------------------------------------------------------------------

📝 ORIGINAL CODE:
----------------------------------------
```python
def very_long_function(data):
    # 55 lines of mixed concerns...
    pass
```

✨ SUGGESTED REFACTORING:
----------------------------------------
```python
def very_long_function(data):
    """Main entry point for data processing."""
    validated = validate_data(data)
    processed = process_data(validated)
    return format_output(processed)

def validate_data(data):
    """Validate input data."""
    if not data:
        raise ValueError("Data is required")
    return data

def process_data(data):
    """Process validated data."""
    return transform(data)

def format_output(data):
    """Format data for output."""
    return str(data)
```

💡 EXPLANATION:
----------------------------------------
Split the function into smaller, focused functions following the Single
Responsibility Principle. Each function now has a clear purpose.

📋 CHANGES MADE:
----------------------------------------
  • Extracted validation logic to validate_data()
  • Extracted processing logic to process_data()
  • Extracted formatting to format_output()
  • Main function now coordinates smaller functions

🎯 Confidence: 85%

================================================================================

================================================================================
🤖 AI ANALYSIS SUMMARY
================================================================================
Provider: openai
Model: gpt-4o-mini
Issues Analyzed: 3
Successful Suggestions: 3
Failed: 0
Total Tokens: 1250
Estimated Cost: $0.0002
================================================================================
```

## Installation

### Basic Installation (No AI features)

```bash
pip install auto-refactor-ai
```

### With OpenAI Support

```bash
pip install auto-refactor-ai[ai]
```

### With All AI Providers

```bash
pip install auto-refactor-ai[ai-all]
```

### Provider-Specific

```bash
pip install auto-refactor-ai[ai-anthropic]
pip install auto-refactor-ai[ai-google]
```

## Configuration

### Environment Variables

```bash
# OpenAI
export OPENAI_API_KEY="sk-..."
export OPENAI_MODEL="gpt-4o-mini"  # Optional

# Anthropic
export ANTHROPIC_API_KEY="sk-..."
export ANTHROPIC_MODEL="claude-3-haiku-20240307"  # Optional

# Google
export GOOGLE_API_KEY="..."
export GOOGLE_MODEL="gemini-1.5-flash"  # Optional

# Ollama (local)
export OLLAMA_BASE_URL="http://localhost:11434"  # Optional
export OLLAMA_MODEL="codellama"  # Optional
```

### Programmatic Configuration

```python
from auto_refactor_ai.llm_providers import LLMConfig, LLMProvider, get_provider

# Create custom config
config = LLMConfig(
    provider=LLMProvider.OPENAI,
    model="gpt-4o",
    api_key="sk-...",
    temperature=0.3,
    max_tokens=2000,
)

# Get provider
provider = get_provider(config)

# Generate suggestion
response = provider.generate("Refactor this code...")
```

## Prompt Engineering

### System Prompt

The system prompt instructs the LLM to:

1. Analyze code and identify issues
2. Generate well-refactored alternatives
3. Preserve original behavior
4. Follow Python best practices
5. Apply SOLID principles
6. Return structured output

### User Prompt Template

```
Please refactor the following Python function to fix the detected issue.

FUNCTION: {function_name}
ISSUE TYPE: {issue_type}
ISSUE: {issue_message}

ORIGINAL CODE:
```python
{code}
```

Please provide a refactored version that:
1. Fixes the "{issue_type}" issue
2. Maintains the same functionality
3. Follows Python best practices
```

### Response Parsing

The module parses structured responses:

```
```python
# REFACTORED CODE
<refactored code>
```

EXPLANATION:
<explanation of changes>

CHANGES:
- <change 1>
- <change 2>
```

## Cost Management

### Token Estimation

Each provider tracks token usage:

```python
response = provider.generate(prompt)
print(f"Tokens used: {response.tokens_used}")
print(f"Estimated cost: ${response.cost_estimate:.4f}")
```

### Cost Estimates (per 1K tokens)

| Model | Input Cost | Output Cost |
|-------|------------|-------------|
| gpt-4o | $0.005 | $0.015 |
| gpt-4o-mini | $0.00015 | $0.0006 |
| claude-3-haiku | $0.00025 | $0.00125 |
| gemini-1.5-flash | Free tier | Free tier |
| ollama (local) | Free | Free |

## Testing

### New Test Files

- `tests/test_llm_providers.py` (26 tests)
- `tests/test_ai_suggestions.py` (15 tests)

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run only V6 tests
pytest tests/test_llm_providers.py tests/test_ai_suggestions.py -v

# With coverage
pytest tests/ --cov=auto_refactor_ai --cov-report=term-missing
```

## Error Handling

### Provider Not Available

```python
if not provider.is_available():
    print("Provider not configured. Set API key.")
```

### API Errors

```python
response = provider.generate(prompt)
if not response.success:
    print(f"Error: {response.error}")
```

### Package Not Installed

```python
try:
    import openai
except ImportError:
    print("Run: pip install auto-refactor-ai[ai]")
```

## What You Learn

1. **Calling LLMs from Python**
   - OpenAI API usage
   - Anthropic API usage
   - Google Generative AI
   - Local Ollama integration

2. **Prompt Engineering**
   - System prompts for role definition
   - Structured output formats
   - Response parsing

3. **API Error Handling**
   - Timeouts and retries
   - Rate limiting
   - Error responses

4. **Token Management**
   - Token counting
   - Cost estimation
   - Output limiting

5. **Provider Abstraction**
   - Factory pattern
   - Abstract base classes
   - Multiple implementations

## Security Considerations

1. **API Key Management**
   - Use environment variables
   - Never commit keys to source control
   - Use .env files for local development

2. **Code Privacy**
   - Code is sent to LLM providers
   - Consider using local Ollama for sensitive code
   - Review provider privacy policies

3. **Output Validation**
   - AI suggestions may contain errors
   - Always review before applying
   - Test refactored code

## Next Steps: V7 Preview

V7 will add **Auto-Refactor Mode**:

```bash
auto-refactor-ai mycode.py --apply
```

Features planned:
- Generate unified diff patches
- Interactive approval
- Automatic backup
- Rollback capability

---

**V6 Status:** ✅ COMPLETE
**Next:** V7 - Auto-Refactor Mode
