"""LLM Provider abstraction for AI-powered code suggestions.

This module provides a unified interface to multiple LLM providers
(OpenAI, Anthropic, Google) for generating refactoring suggestions.
"""

import json
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional


class LLMProvider(Enum):
    """Supported LLM providers."""

    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    OLLAMA = "ollama"  # Local LLM support


@dataclass
class LLMConfig:
    """Configuration for LLM providers."""

    provider: LLMProvider = LLMProvider.OPENAI
    model: str = "gpt-4o-mini"
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    temperature: float = 0.3
    max_tokens: int = 2000
    timeout: int = 60

    @classmethod
    def from_env(cls, provider: LLMProvider = LLMProvider.OPENAI) -> "LLMConfig":
        """Create config from environment variables."""
        api_key = None
        model = "gpt-4o-mini"
        base_url = None

        if provider == LLMProvider.OPENAI:
            api_key = os.environ.get("OPENAI_API_KEY")
            model = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
        elif provider == LLMProvider.ANTHROPIC:
            api_key = os.environ.get("ANTHROPIC_API_KEY")
            model = os.environ.get("ANTHROPIC_MODEL", "claude-3-haiku-20240307")
        elif provider == LLMProvider.GOOGLE:
            api_key = os.environ.get("GOOGLE_API_KEY")
            model = os.environ.get("GOOGLE_MODEL", "gemini-1.5-flash")
        elif provider == LLMProvider.OLLAMA:
            base_url = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
            model = os.environ.get("OLLAMA_MODEL", "codellama")

        return cls(
            provider=provider,
            model=model,
            api_key=api_key,
            base_url=base_url,
        )


@dataclass
class RefactoringSuggestion:
    """A suggested refactoring from the LLM."""

    original_code: str
    refactored_code: str
    explanation: str
    confidence: float = 0.0
    changes_summary: List[str] = field(default_factory=list)


@dataclass
class LLMResponse:
    """Response from an LLM provider."""

    content: str
    model: str
    provider: LLMProvider
    tokens_used: int = 0
    cost_estimate: float = 0.0
    error: Optional[str] = None

    @property
    def success(self) -> bool:
        return self.error is None and len(self.content) > 0


class BaseLLMProvider(ABC):
    """Base class for LLM providers."""

    def __init__(self, config: LLMConfig):
        self.config = config

    @abstractmethod
    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> LLMResponse:
        """Generate a response from the LLM."""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if the provider is configured and available."""
        pass

    def get_refactoring_suggestion(
        self, code: str, issue_type: str, issue_message: str, function_name: str
    ) -> RefactoringSuggestion:
        """Generate a refactoring suggestion for the given code."""
        system_prompt = self._get_system_prompt()
        user_prompt = self._get_refactoring_prompt(code, issue_type, issue_message, function_name)

        response = self.generate(user_prompt, system_prompt)

        if not response.success:
            return RefactoringSuggestion(
                original_code=code,
                refactored_code="",
                explanation=f"Error: {response.error}",
                confidence=0.0,
            )

        return self._parse_refactoring_response(code, response.content)

    def _get_system_prompt(self) -> str:
        """Get the system prompt for refactoring."""
        return """You are an expert Python code refactoring assistant. Your task is to:
1. Analyze the provided code and its issues
2. Suggest a well-refactored version that fixes the issues
3. Explain your changes clearly

Guidelines:
- Preserve the original behavior and functionality
- Follow Python best practices (PEP 8, type hints when appropriate)
- Apply SOLID principles, especially Single Responsibility
- Use meaningful names for new functions/variables
- Keep functions short and focused (under 30 lines)
- Limit parameters to 5 or less (use dataclasses/config objects for more)
- Avoid deep nesting (use guard clauses, early returns)

Output Format:
Return your response in this exact format:

```python
# REFACTORED CODE
<your refactored code here>
```

EXPLANATION:
<brief explanation of what you changed and why>

CHANGES:
- <change 1>
- <change 2>
- <change 3>
"""

    def _get_refactoring_prompt(
        self, code: str, issue_type: str, issue_message: str, function_name: str
    ) -> str:
        """Generate the refactoring prompt."""
        return f"""Please refactor the following Python function to fix the detected issue.

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
"""

    def _parse_refactoring_response(
        self, original_code: str, response: str
    ) -> RefactoringSuggestion:
        """Parse the LLM response into a RefactoringSuggestion."""
        refactored_code = ""
        explanation = ""
        changes = []

        # Extract code block
        if "```python" in response:
            parts = response.split("```python")
            if len(parts) > 1:
                code_part = parts[1].split("```")[0]
                # Remove the "# REFACTORED CODE" comment if present
                lines = code_part.strip().split("\n")
                if lines and "REFACTORED CODE" in lines[0]:
                    lines = lines[1:]
                refactored_code = "\n".join(lines).strip()

        # Extract explanation
        if "EXPLANATION:" in response:
            exp_parts = response.split("EXPLANATION:")
            if len(exp_parts) > 1:
                exp_text = exp_parts[1]
                if "CHANGES:" in exp_text:
                    exp_text = exp_text.split("CHANGES:")[0]
                explanation = exp_text.strip()

        # Extract changes
        if "CHANGES:" in response:
            changes_parts = response.split("CHANGES:")
            if len(changes_parts) > 1:
                changes_text = changes_parts[1].strip()
                for line in changes_text.split("\n"):
                    line = line.strip()
                    if line.startswith("-"):
                        changes.append(line[1:].strip())

        # Calculate confidence based on response quality
        confidence = 0.8 if refactored_code and explanation else 0.5

        return RefactoringSuggestion(
            original_code=original_code,
            refactored_code=refactored_code,
            explanation=explanation,
            confidence=confidence,
            changes_summary=changes,
        )


class OpenAIProvider(BaseLLMProvider):
    """OpenAI LLM provider (GPT-4, GPT-3.5-turbo, etc.)."""

    def is_available(self) -> bool:
        """Check if OpenAI is configured."""
        return self.config.api_key is not None and len(self.config.api_key) > 0

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> LLMResponse:
        """Generate a response using OpenAI API."""
        if not self.is_available():
            return LLMResponse(
                content="",
                model=self.config.model,
                provider=LLMProvider.OPENAI,
                error="OpenAI API key not configured. Set OPENAI_API_KEY environment variable.",
            )

        try:
            import openai

            client = openai.OpenAI(api_key=self.config.api_key)

            messages: List[Dict[str, str]] = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            response = client.chat.completions.create(
                model=self.config.model,
                messages=messages,  # type: ignore[arg-type]
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens,
                timeout=self.config.timeout,
            )

            content = response.choices[0].message.content or ""
            tokens = response.usage.total_tokens if response.usage else 0

            # Estimate cost (approximate)
            cost = self._estimate_cost(tokens)

            return LLMResponse(
                content=content,
                model=self.config.model,
                provider=LLMProvider.OPENAI,
                tokens_used=tokens,
                cost_estimate=cost,
            )

        except ImportError:
            return LLMResponse(
                content="",
                model=self.config.model,
                provider=LLMProvider.OPENAI,
                error="OpenAI package not installed. Run: pip install openai",
            )
        except Exception as e:
            return LLMResponse(
                content="",
                model=self.config.model,
                provider=LLMProvider.OPENAI,
                error=f"OpenAI API error: {str(e)}",
            )

    def _estimate_cost(self, tokens: int) -> float:
        """Estimate cost based on token usage."""
        # Approximate pricing per 1K tokens
        pricing = {
            "gpt-4o": 0.005,
            "gpt-4o-mini": 0.00015,
            "gpt-4-turbo": 0.01,
            "gpt-4": 0.03,
            "gpt-3.5-turbo": 0.0015,
        }
        rate = pricing.get(self.config.model, 0.001)
        return (tokens / 1000) * rate


class AnthropicProvider(BaseLLMProvider):
    """Anthropic LLM provider (Claude)."""

    def is_available(self) -> bool:
        """Check if Anthropic is configured."""
        return self.config.api_key is not None and len(self.config.api_key) > 0

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> LLMResponse:
        """Generate a response using Anthropic API."""
        if not self.is_available():
            return LLMResponse(
                content="",
                model=self.config.model,
                provider=LLMProvider.ANTHROPIC,
                error="Anthropic API key not configured. Set ANTHROPIC_API_KEY environment variable.",
            )

        try:
            import anthropic  # type: ignore[import-not-found]

            client = anthropic.Anthropic(api_key=self.config.api_key)

            response = client.messages.create(
                model=self.config.model,
                max_tokens=self.config.max_tokens,
                system=system_prompt or "",
                messages=[{"role": "user", "content": prompt}],
            )

            content = response.content[0].text if response.content else ""
            tokens = response.usage.input_tokens + response.usage.output_tokens

            # Estimate cost
            cost = self._estimate_cost(tokens)

            return LLMResponse(
                content=content,
                model=self.config.model,
                provider=LLMProvider.ANTHROPIC,
                tokens_used=tokens,
                cost_estimate=cost,
            )

        except ImportError:
            return LLMResponse(
                content="",
                model=self.config.model,
                provider=LLMProvider.ANTHROPIC,
                error="Anthropic package not installed. Run: pip install anthropic",
            )
        except Exception as e:
            return LLMResponse(
                content="",
                model=self.config.model,
                provider=LLMProvider.ANTHROPIC,
                error=f"Anthropic API error: {str(e)}",
            )

    def _estimate_cost(self, tokens: int) -> float:
        """Estimate cost based on token usage."""
        pricing = {
            "claude-3-opus-20240229": 0.015,
            "claude-3-sonnet-20240229": 0.003,
            "claude-3-haiku-20240307": 0.00025,
            "claude-3-5-sonnet-20241022": 0.003,
        }
        rate = pricing.get(self.config.model, 0.001)
        return (tokens / 1000) * rate


class GoogleProvider(BaseLLMProvider):
    """Google LLM provider (Gemini)."""

    def is_available(self) -> bool:
        """Check if Google is configured."""
        return self.config.api_key is not None and len(self.config.api_key) > 0

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> LLMResponse:
        """Generate a response using Google Gemini API."""
        if not self.is_available():
            return LLMResponse(
                content="",
                model=self.config.model,
                provider=LLMProvider.GOOGLE,
                error="Google API key not configured. Set GOOGLE_API_KEY environment variable.",
            )

        try:
            import google.generativeai as genai  # type: ignore[import-untyped]

            genai.configure(api_key=self.config.api_key)

            model = genai.GenerativeModel(self.config.model)

            full_prompt = prompt
            if system_prompt:
                full_prompt = f"{system_prompt}\n\n{prompt}"

            response = model.generate_content(
                full_prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=self.config.temperature,
                    max_output_tokens=self.config.max_tokens,
                ),
            )

            content = response.text if response.text else ""

            return LLMResponse(
                content=content,
                model=self.config.model,
                provider=LLMProvider.GOOGLE,
                tokens_used=0,  # Gemini doesn't always report tokens
                cost_estimate=0.0,
            )

        except ImportError:
            return LLMResponse(
                content="",
                model=self.config.model,
                provider=LLMProvider.GOOGLE,
                error="Google AI package not installed. Run: pip install google-generativeai",
            )
        except Exception as e:
            return LLMResponse(
                content="",
                model=self.config.model,
                provider=LLMProvider.GOOGLE,
                error=f"Google API error: {str(e)}",
            )


class OllamaProvider(BaseLLMProvider):
    """Ollama provider for local LLMs."""

    def is_available(self) -> bool:
        """Check if Ollama is available."""
        import urllib.request

        try:
            url = f"{self.config.base_url or 'http://localhost:11434'}/api/tags"
            urllib.request.urlopen(url, timeout=2)
            return True
        except Exception:
            return False

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> LLMResponse:
        """Generate a response using Ollama API."""
        import urllib.error
        import urllib.request

        base_url = self.config.base_url or "http://localhost:11434"

        try:
            data = {
                "model": self.config.model,
                "prompt": prompt,
                "system": system_prompt or "",
                "stream": False,
                "options": {
                    "temperature": self.config.temperature,
                    "num_predict": self.config.max_tokens,
                },
            }

            req = urllib.request.Request(
                f"{base_url}/api/generate",
                data=json.dumps(data).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST",
            )

            with urllib.request.urlopen(req, timeout=self.config.timeout) as response:
                result = json.loads(response.read().decode("utf-8"))

            content = result.get("response", "")

            return LLMResponse(
                content=content,
                model=self.config.model,
                provider=LLMProvider.OLLAMA,
                tokens_used=result.get("eval_count", 0),
                cost_estimate=0.0,  # Local = free
            )

        except urllib.error.URLError:
            return LLMResponse(
                content="",
                model=self.config.model,
                provider=LLMProvider.OLLAMA,
                error=f"Ollama not available at {base_url}. Is Ollama running?",
            )
        except Exception as e:
            return LLMResponse(
                content="",
                model=self.config.model,
                provider=LLMProvider.OLLAMA,
                error=f"Ollama error: {str(e)}",
            )


def get_provider(config: Optional[LLMConfig] = None) -> BaseLLMProvider:
    """Get an LLM provider based on configuration.

    Args:
        config: LLM configuration. If None, tries to auto-detect.

    Returns:
        An appropriate LLM provider instance.
    """
    if config is None:
        # Try providers in order of preference
        for provider_type in [LLMProvider.OPENAI, LLMProvider.ANTHROPIC, LLMProvider.GOOGLE]:
            config = LLMConfig.from_env(provider_type)
            if config.api_key:
                break
        else:
            # Fall back to Ollama if no API keys found
            config = LLMConfig.from_env(LLMProvider.OLLAMA)

    providers = {
        LLMProvider.OPENAI: OpenAIProvider,
        LLMProvider.ANTHROPIC: AnthropicProvider,
        LLMProvider.GOOGLE: GoogleProvider,
        LLMProvider.OLLAMA: OllamaProvider,
    }

    provider_class = providers.get(config.provider, OpenAIProvider)
    return provider_class(config)  # type: ignore[abstract]


def check_provider_availability() -> Dict[str, bool]:
    """Check which LLM providers are available."""
    results = {}

    for provider_type in LLMProvider:
        config = LLMConfig.from_env(provider_type)
        provider = get_provider(config)
        results[provider_type.value] = provider.is_available()

    return results
