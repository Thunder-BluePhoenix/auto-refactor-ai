"""Extended LLM provider tests for improving coverage."""

import os
from unittest.mock import patch

from auto_refactor_ai.llm_providers import (
    AnthropicProvider,
    GoogleProvider,
    LLMConfig,
    LLMProvider,
    LLMResponse,
    OllamaProvider,
    OpenAIProvider,
    check_provider_availability,
    get_provider,
)


class TestLLMConfigExtended:
    """Extended tests for LLMConfig."""

    def test_from_env_openai(self):
        """Test creating config from env for OpenAI."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key", "OPENAI_MODEL": "gpt-4"}):
            config = LLMConfig.from_env(LLMProvider.OPENAI)
            assert config.provider == LLMProvider.OPENAI
            assert config.api_key == "test-key"
            assert config.model == "gpt-4"

    def test_from_env_anthropic(self):
        """Test creating config from env for Anthropic."""
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key"}):
            config = LLMConfig.from_env(LLMProvider.ANTHROPIC)
            assert config.provider == LLMProvider.ANTHROPIC
            assert config.api_key == "test-key"

    def test_from_env_google(self):
        """Test creating config from env for Google."""
        with patch.dict(os.environ, {"GOOGLE_API_KEY": "test-key"}):
            config = LLMConfig.from_env(LLMProvider.GOOGLE)
            assert config.provider == LLMProvider.GOOGLE
            assert config.api_key == "test-key"

    def test_from_env_ollama(self):
        """Test creating config from env for Ollama."""
        with patch.dict(
            os.environ, {"OLLAMA_BASE_URL": "http://localhost:11434", "OLLAMA_MODEL": "llama2"}
        ):
            config = LLMConfig.from_env(LLMProvider.OLLAMA)
            assert config.provider == LLMProvider.OLLAMA
            assert config.model == "llama2"
            assert config.base_url == "http://localhost:11434"


class TestLLMResponseExtended:
    """Extended tests for LLMResponse."""

    def test_success_property_with_content(self):
        """Test success property with valid content."""
        response = LLMResponse(
            content="This is a response", model="gpt-4", provider=LLMProvider.OPENAI
        )
        assert response.success is True

    def test_success_property_with_error(self):
        """Test success property with error."""
        response = LLMResponse(
            content="", model="gpt-4", provider=LLMProvider.OPENAI, error="API error"
        )
        assert response.success is False

    def test_success_property_empty_content(self):
        """Test success property with empty content."""
        response = LLMResponse(content="", model="gpt-4", provider=LLMProvider.OPENAI)
        assert response.success is False


class TestOpenAIProviderExtended:
    """Extended tests for OpenAIProvider."""

    def test_is_available_with_key(self):
        """Test is_available returns True with API key."""
        config = LLMConfig(api_key="test-key")
        provider = OpenAIProvider(config)
        assert provider.is_available() is True

    def test_is_available_without_key(self):
        """Test is_available returns False without API key."""
        config = LLMConfig(api_key=None)
        provider = OpenAIProvider(config)
        assert provider.is_available() is False

    def test_generate_without_api_key(self):
        """Test generate returns error without API key."""
        config = LLMConfig(api_key=None)
        provider = OpenAIProvider(config)

        response = provider.generate("test prompt")

        assert response.success is False
        assert "not configured" in response.error

    def test_estimate_cost_gpt4(self):
        """Test cost estimation for GPT-4."""
        config = LLMConfig(api_key="test", model="gpt-4")
        provider = OpenAIProvider(config)

        cost = provider._estimate_cost(1000)
        assert cost > 0


class TestAnthropicProviderExtended:
    """Extended tests for AnthropicProvider."""

    def test_is_available_with_key(self):
        """Test is_available returns True with API key."""
        config = LLMConfig(provider=LLMProvider.ANTHROPIC, api_key="test-key")
        provider = AnthropicProvider(config)
        assert provider.is_available() is True

    def test_generate_without_api_key(self):
        """Test generate returns error without API key."""
        config = LLMConfig(provider=LLMProvider.ANTHROPIC, api_key=None)
        provider = AnthropicProvider(config)

        response = provider.generate("test prompt")

        assert response.success is False
        assert "not configured" in response.error


class TestGoogleProviderExtended:
    """Extended tests for GoogleProvider."""

    def test_is_available_with_key(self):
        """Test is_available returns True with API key."""
        config = LLMConfig(provider=LLMProvider.GOOGLE, api_key="test-key")
        provider = GoogleProvider(config)
        assert provider.is_available() is True

    def test_generate_without_api_key(self):
        """Test generate returns error without API key."""
        config = LLMConfig(provider=LLMProvider.GOOGLE, api_key=None)
        provider = GoogleProvider(config)

        response = provider.generate("test prompt")

        assert response.success is False
        assert "not configured" in response.error


class TestOllamaProviderExtended:
    """Extended tests for OllamaProvider."""

    def test_is_available_offline(self):
        """Test is_available returns False when Ollama not running."""
        config = LLMConfig(provider=LLMProvider.OLLAMA, base_url="http://localhost:99999")
        provider = OllamaProvider(config)

        # Should return False when Ollama is not running
        assert provider.is_available() is False


class TestGetProviderExtended:
    """Extended tests for get_provider function."""

    def test_get_provider_auto_detect_openai(self):
        """Test auto-detect with OpenAI key."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}, clear=True):
            provider = get_provider()
            assert isinstance(provider, OpenAIProvider)

    def test_get_provider_with_config(self):
        """Test get_provider with explicit config."""
        config = LLMConfig(provider=LLMProvider.ANTHROPIC, api_key="test")
        provider = get_provider(config)
        assert isinstance(provider, AnthropicProvider)

    def test_get_provider_google(self):
        """Test getting Google provider."""
        config = LLMConfig(provider=LLMProvider.GOOGLE, api_key="test")
        provider = get_provider(config)
        assert isinstance(provider, GoogleProvider)

    def test_get_provider_ollama(self):
        """Test getting Ollama provider."""
        config = LLMConfig(provider=LLMProvider.OLLAMA)
        provider = get_provider(config)
        assert isinstance(provider, OllamaProvider)


class TestCheckProviderAvailability:
    """Tests for check_provider_availability."""

    def test_returns_dict(self):
        """Test that check_provider_availability returns a dict."""
        result = check_provider_availability()

        assert isinstance(result, dict)
        assert "openai" in result
        assert "anthropic" in result
        assert "google" in result
        assert "ollama" in result


class TestBaseLLMProviderMethods:
    """Tests for BaseLLMProvider helper methods."""

    def test_parse_refactoring_response_with_code(self):
        """Test parsing LLM response with code block."""
        config = LLMConfig(api_key="test")
        provider = OpenAIProvider(config)

        response = """```python
# REFACTORED CODE
def foo():
    return 1
```

EXPLANATION:
Made the function return a value.

CHANGES:
- Added return statement
"""

        result = provider._parse_refactoring_response("def foo(): pass", response)

        assert "return 1" in result.refactored_code
        assert "Added return" in " ".join(result.changes_summary)

    def test_get_system_prompt(self):
        """Test system prompt generation."""
        config = LLMConfig(api_key="test")
        provider = OpenAIProvider(config)

        prompt = provider._get_system_prompt()

        assert "Python" in prompt
        assert "refactor" in prompt.lower()

    def test_get_refactoring_prompt(self):
        """Test refactoring prompt generation."""
        config = LLMConfig(api_key="test")
        provider = OpenAIProvider(config)

        prompt = provider._get_refactoring_prompt(
            code="def foo(): pass",
            issue_type="function-too-long",
            issue_message="Function is too long",
            function_name="foo",
        )

        assert "foo" in prompt
        assert "function-too-long" in prompt
