"""
Tests for the FlatLand LLM integration module.
"""

import json
import os
from unittest.mock import patch, MagicMock

import pytest
import responses
from openai.types.error import APIError, RateLimitError as OpenAIRateLimitError

from flatland.llm import generate_environment, EnvironmentGenerator
from flatland.llm.exceptions import (
    FlatlandLLMError,
    SchemaValidationError,
    RateLimitError,
    LLMResponseError
)

# Sample valid environment JSON for testing
VALID_ENV = {
    "metadata": {
        "name": "Test Environment",
        "description": "A test environment",
        "version": "1.0.0"
    },
    "initial_state": {
        "grid": {
            "width": 5,
            "height": 5,
            "cells": [[0 for _ in range(5)] for _ in range(5)]
        },
        "entities": [
            {
                "id": "player",
                "type": "player",
                "position": [2, 2],
                "properties": {
                    "movable": True
                }
            }
        ]
    }
}

@pytest.fixture
def mock_openai_response():
    """Mock a successful OpenAI API response."""
    return {
        "choices": [
            {
                "message": {
                    "content": json.dumps(VALID_ENV)
                }
            }
        ]
    }

@pytest.fixture
def env_generator():
    """Create an EnvironmentGenerator instance with a mock API key."""
    with patch.dict(os.environ, {"FLATLAND_OPENAI_KEY": "test-key"}):
        return EnvironmentGenerator()

def test_environment_generator_init_no_key():
    """Test EnvironmentGenerator initialization without API key."""
    with patch.dict(os.environ, clear=True):
        with pytest.raises(FlatlandLLMError) as exc_info:
            EnvironmentGenerator()
        assert "OpenAI API key not found" in str(exc_info.value)

def test_environment_generator_init_with_key():
    """Test EnvironmentGenerator initialization with API key."""
    generator = EnvironmentGenerator(api_key="test-key")
    assert generator.api_key == "test-key"

def test_generate_environment_success(env_generator, mock_openai_response):
    """Test successful environment generation."""
    with patch.object(env_generator.client.chat.completions, "create") as mock_create:
        mock_create.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content=json.dumps(VALID_ENV)))]
        )
        
        result = env_generator.generate("Create a simple test environment")
        assert result.metadata["name"] == "Test Environment"
        assert result.initial_state["grid"]["width"] == 5

def test_generate_environment_invalid_json(env_generator):
    """Test handling of invalid JSON response."""
    with patch.object(env_generator.client.chat.completions, "create") as mock_create:
        mock_create.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content="Invalid JSON"))]
        )
        
        with pytest.raises(LLMResponseError) as exc_info:
            env_generator.generate("Create an environment", max_retries=1)
        assert "Failed to parse LLM response as JSON" in str(exc_info.value)

def test_generate_environment_validation_error(env_generator):
    """Test handling of schema validation errors."""
    invalid_env = VALID_ENV.copy()
    del invalid_env["metadata"]  # Make it invalid
    
    with patch.object(env_generator.client.chat.completions, "create") as mock_create:
        mock_create.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content=json.dumps(invalid_env)))]
        )
        
        with pytest.raises(SchemaValidationError) as exc_info:
            env_generator.generate("Create an environment", max_retries=1)
        assert "validation" in str(exc_info.value)

def test_generate_environment_rate_limit(env_generator):
    """Test rate limit handling."""
    with patch.object(env_generator.client.chat.completions, "create") as mock_create:
        mock_create.side_effect = OpenAIRateLimitError(
            message="Rate limit exceeded",
            response=MagicMock(headers={"Retry-After": "30"})
        )
        
        with pytest.raises(RateLimitError) as exc_info:
            env_generator.generate("Create an environment")
        assert "Rate limit exceeded" in str(exc_info.value)

def test_generate_environment_api_error(env_generator):
    """Test OpenAI API error handling."""
    with patch.object(env_generator.client.chat.completions, "create") as mock_create:
        mock_create.side_effect = APIError(message="API Error")
        
        with pytest.raises(FlatlandLLMError) as exc_info:
            env_generator.generate("Create an environment")
        assert "OpenAI API error" in str(exc_info.value)

def test_rate_limit_decorator():
    """Test the rate limiting decorator."""
    calls = []
    
    @EnvironmentGenerator.rate_limit(max_per_minute=2)
    def test_func():
        calls.append(1)
        return len(calls)
    
    # First two calls should succeed
    assert test_func() == 1
    assert test_func() == 2
    
    # Third call should raise RateLimitError
    with pytest.raises(RateLimitError):
        test_func()

def test_convenience_function():
    """Test the convenience function generate_environment."""
    with patch.dict(os.environ, {"FLATLAND_OPENAI_KEY": "test-key"}):
        with patch("flatland.llm.client.EnvironmentGenerator.generate") as mock_generate:
            mock_generate.return_value = VALID_ENV
            
            result = generate_environment(
                "Create a test environment",
                style_guidance="minimal"
            )
            
            mock_generate.assert_called_once_with(
                "Create a test environment",
                style_guidance="minimal"
            )
            assert result == VALID_ENV
