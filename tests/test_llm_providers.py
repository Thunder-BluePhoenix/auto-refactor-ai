"""Tests for LLM providers module."""

import os
from unittest.mock import MagicMock, patch

import pytest

from auto_refactor_ai.llm_providers import (
    AnthropicProvider,
    GoogleProvider,
    LLMConfig,
    LLMProvider,
    LLMResponse,
    OllamaProvider,
    OpenAIProvider,
    RefactoringSuggestion,
    check_provider_availability,
    get_provider,
)


class TestLLMProvider:
    """Tests for LLMProvider enum."""

    def test_provider_values(self):
        """Test that all providers have correct values."""
        assert LLMProvider.OPENAI.value == "openai"
        assert LLMProvider.ANTHROPIC.value == "anthropic"
        assert LLMProvider.GOOGLE.value == "google"
        assert LLMProvider.OLLAMA.value == "ollama"


class TestLLMConfig:
    """Tests for LLMConfig dataclass."""

    def test_default_config(self):
        """Test default configuration values."""
        config = LLMConfig()
        assert config.provider == LLMProvider.OPENAI
        assert config.model == "gpt-4o-mini"
        assert config.temperature == 0.3
        assert config.max_tokens == 2000
        assert config.timeout == 60

    def test_custom_config(self):
        """Test custom configuration."""
        config = LLMConfig(
            provider=LLMProvider.ANTHROPIC,
            model="claude-3-haiku-20240307",
            api_key="test-key",
            temperature=0.5,
        )
        assert config.provider == LLMProvider.ANTHROPIC
        assert config.model == "claude-3-haiku-20240307"
        assert config.api_key == "test-key"
        assert config.temperature == 0.5

    def test_from_env_openai(self):
        """Test config from environment for OpenAI."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-openai-key"}):
            config = LLMConfig.from_env(LLMProvider.OPENAI)
            assert config.provider == LLMProvider.OPENAI
            assert config.api_key == "test-openai-key"

    def test_from_env_anthropic(self):
        """Test config from environment for Anthropic."""
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-anthropic-key"}):
            config = LLMConfig.from_env(LLMProvider.ANTHROPIC)
            assert config.provider == LLMProvider.ANTHROPIC
            assert config.api_key == "test-anthropic-key"

    def test_from_env_no_key(self):
        """Test config from environment when no key is set."""
        with patch.dict(os.environ, {}, clear=True):
            config = LLMConfig.from_env(LLMProvider.OPENAI)
            assert config.api_key is None


class TestLLMResponse:
    """Tests for LLMResponse dataclass."""

    def test_successful_response(self):
        """Test successful response."""
        response = LLMResponse(
            content="Test content",
            model="gpt-4o-mini",
            provider=LLMProvider.OPENAI,
            tokens_used=100,
        )
        assert response.success is True
        assert response.content == "Test content"

    def test_error_response(self):
        """Test error response."""
        response = LLMResponse(
            content="",
            model="gpt-4o-mini",
            provider=LLMProvider.OPENAI,
            error="API error",
        )
        assert response.success is False


class TestRefactoringSuggestion:
    """Tests for RefactoringSuggestion dataclass."""

    def test_suggestion_creation(self):
        """Test creating a refactoring suggestion."""
        suggestion = RefactoringSuggestion(
            original_code="def foo(): pass",
            refactored_code="def foo():\n    pass",
            explanation="Added proper formatting",
            confidence=0.9,
            changes_summary=["Added newline", "Fixed indentation"],
        )
        assert suggestion.original_code == "def foo(): pass"
        assert suggestion.confidence == 0.9
        assert len(suggestion.changes_summary) == 2


class TestOpenAIProvider:
    """Tests for OpenAI provider."""

    def test_is_available_with_key(self):
        """Test availability check with API key."""
        config = LLMConfig(api_key="test-key")
        provider = OpenAIProvider(config)
        assert provider.is_available() is True

    def test_is_available_without_key(self):
        """Test availability check without API key."""
        config = LLMConfig(api_key=None)
        provider = OpenAIProvider(config)
        assert provider.is_available() is False

    def test_generate_without_key(self):
        """Test generate returns error without API key."""
        config = LLMConfig(api_key=None)
        provider = OpenAIProvider(config)
        response = provider.generate("Test prompt")
        assert response.success is False
        assert "not configured" in response.error

    def test_generate_with_mock(self):
        """Test generate with mocked OpenAI client."""
        try:
            import openai  # noqa: F401
        except ImportError:
            pytest.skip("OpenAI package not installed")

        # Mock the OpenAI client
        with patch("openai.OpenAI") as mock_openai_class:
            mock_response = MagicMock()
            mock_response.choices = [MagicMock()]
            mock_response.choices[0].message.content = "Refactored code"
            mock_response.usage = MagicMock()
            mock_response.usage.total_tokens = 100

            mock_client = MagicMock()
            mock_client.chat.completions.create.return_value = mock_response
            mock_openai_class.return_value = mock_client

            config = LLMConfig(api_key="test-key")
            provider = OpenAIProvider(config)
            response = provider.generate("Test prompt")

            assert response.content == "Refactored code"
            assert response.tokens_used == 100


class TestAnthropicProvider:
    """Tests for Anthropic provider."""

    def test_is_available_with_key(self):
        """Test availability check with API key."""
        config = LLMConfig(provider=LLMProvider.ANTHROPIC, api_key="test-key")
        provider = AnthropicProvider(config)
        assert provider.is_available() is True

    def test_is_available_without_key(self):
        """Test availability check without API key."""
        config = LLMConfig(provider=LLMProvider.ANTHROPIC, api_key=None)
        provider = AnthropicProvider(config)
        assert provider.is_available() is False


class TestGoogleProvider:
    """Tests for Google provider."""

    def test_is_available_with_key(self):
        """Test availability check with API key."""
        config = LLMConfig(provider=LLMProvider.GOOGLE, api_key="test-key")
        provider = GoogleProvider(config)
        assert provider.is_available() is True

    def test_is_available_without_key(self):
        """Test availability check without API key."""
        config = LLMConfig(provider=LLMProvider.GOOGLE, api_key=None)
        provider = GoogleProvider(config)
        assert provider.is_available() is False


class TestOllamaProvider:
    """Tests for Ollama provider."""

    def test_generate_connection_error(self):
        """Test generate when Ollama is not running."""
        config = LLMConfig(provider=LLMProvider.OLLAMA, base_url="http://localhost:99999")
        provider = OllamaProvider(config)
        response = provider.generate("Test prompt")
        assert response.success is False


class TestGetProvider:
    """Tests for get_provider function."""

    def test_get_openai_provider(self):
        """Test getting OpenAI provider."""
        config = LLMConfig(provider=LLMProvider.OPENAI, api_key="test")
        provider = get_provider(config)
        assert isinstance(provider, OpenAIProvider)

    def test_get_anthropic_provider(self):
        """Test getting Anthropic provider."""
        config = LLMConfig(provider=LLMProvider.ANTHROPIC, api_key="test")
        provider = get_provider(config)
        assert isinstance(provider, AnthropicProvider)

    def test_get_google_provider(self):
        """Test getting Google provider."""
        config = LLMConfig(provider=LLMProvider.GOOGLE, api_key="test")
        provider = get_provider(config)
        assert isinstance(provider, GoogleProvider)

    def test_get_ollama_provider(self):
        """Test getting Ollama provider."""
        config = LLMConfig(provider=LLMProvider.OLLAMA)
        provider = get_provider(config)
        assert isinstance(provider, OllamaProvider)


class TestResponseParsing:
    """Tests for parsing LLM responses."""

    def test_parse_refactoring_response(self):
        """Test parsing a well-formed refactoring response."""
        config = LLMConfig(api_key="test")
        provider = OpenAIProvider(config)

        response_text = """
```python
# REFACTORED CODE
def process_data(data):
    validated = validate(data)
    return transform(validated)
```

EXPLANATION:
Split the function into smaller pieces for better readability.

CHANGES:
- Extracted validation logic
- Simplified main function
"""
        suggestion = provider._parse_refactoring_response("original", response_text)

        assert "def process_data" in suggestion.refactored_code
        assert "Split the function" in suggestion.explanation
        assert len(suggestion.changes_summary) == 2

    def test_parse_malformed_response(self):
        """Test parsing a malformed response."""
        config = LLMConfig(api_key="test")
        provider = OpenAIProvider(config)

        response_text = "Some random text without proper formatting"
        suggestion = provider._parse_refactoring_response("original", response_text)

        assert suggestion.refactored_code == ""
        assert suggestion.confidence == 0.5  # Lower confidence for malformed


class TestCheckProviderAvailability:
    """Tests for check_provider_availability function."""

    def test_check_availability(self):
        """Test checking provider availability."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}, clear=True):
            availability = check_provider_availability()
            assert "openai" in availability
            assert "anthropic" in availability
            assert "google" in availability
            assert "ollama" in availability
