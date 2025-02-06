"""
OpenAI client integration for FlatLand environment generation.
"""

import os
import json
import time
from functools import wraps
from typing import Optional, Dict, Any

from openai import OpenAI
try:
    from openai.error import APIError, RateLimitError as OpenAIRateLimitError
except ImportError:
    from openai import APIError, RateLimitError as OpenAIRateLimitError

from ..schemas import ENVIRONMENT_SCHEMA, EnvironmentDefinition
from .exceptions import FlatlandLLMError, SchemaValidationError, RateLimitError, LLMResponseError

def rate_limit(max_per_minute: int = 10):
    """Decorator to implement rate limiting."""
    calls = []
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            now = time.time()
            # Remove calls older than 1 minute
            while calls and calls[0] < now - 60:
                calls.pop(0)
            if len(calls) >= max_per_minute:
                wait_time = calls[0] + 60 - now
                raise RateLimitError(
                    f"Rate limit exceeded. Try again in {int(wait_time)} seconds.",
                    retry_after=int(wait_time)
                )
            calls.append(now)
            return func(*args, **kwargs)
        return wrapper
    return decorator

class EnvironmentGenerator:
    """Main class for generating FlatLand environments using OpenAI."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the environment generator.
        
        Args:
            api_key: OpenAI API key. If not provided, will look for FLATLAND_OPENAI_KEY env var.
        """
        self.api_key = api_key or os.getenv("FLATLAND_OPENAI_KEY")
        if not self.api_key:
            raise FlatlandLLMError(
                "OpenAI API key not found. Set FLATLAND_OPENAI_KEY environment variable "
                "or pass api_key to EnvironmentGenerator."
            )
        
        self.client = OpenAI(api_key=self.api_key)
        self._load_prompt_template()
    
    def _load_prompt_template(self):
        """Load and prepare the system prompt template."""
        try:
            with open('src/flatland/prompt_template.txt', 'r') as f:
                self.prompt_template = f.read()
        except FileNotFoundError:
            raise FlatlandLLMError("Could not find prompt template file")
    
    def _build_messages(self, description: str, style_guidance: Optional[str] = None) -> list:
        """Build the message list for the OpenAI API call."""
        messages = [
            {
                "role": "system",
                "content": self.prompt_template
            },
            {
                "role": "user",
                "content": description
            }
        ]
        
        if style_guidance:
            messages.append({
                "role": "user",
                "content": f"Style guidance: {style_guidance}"
            })
            
        return messages
    
    def _validate_environment(self, env_data: Dict[str, Any]) -> EnvironmentDefinition:
        """Validate the generated environment against the schema."""
        try:
            # Basic JSON schema validation would go here
            # For now, we'll use the EnvironmentDefinition class's validation
            return EnvironmentDefinition.from_dict(env_data)
        except Exception as e:
            raise SchemaValidationError(
                f"Generated environment failed validation: {str(e)}",
                validation_errors=[str(e)]
            )
    
    @rate_limit(max_per_minute=10)
    def generate(
        self,
        description: str,
        style_guidance: Optional[str] = None,
        model: str = "gpt-4-turbo-preview",
        max_retries: int = 3
    ) -> EnvironmentDefinition:
        """Generate a FlatLand environment from a description.
        
        Args:
            description: Free-form description of the desired environment
            style_guidance: Optional styling/theme guidance
            model: OpenAI model to use
            max_retries: Maximum number of retry attempts for validation failures
            
        Returns:
            EnvironmentDefinition object representing the generated environment
            
        Raises:
            SchemaValidationError: If the generated environment is invalid
            RateLimitError: If API rate limits are exceeded
            LLMResponseError: If there are issues with the LLM response
            FlatlandLLMError: For other errors
        """
        messages = self._build_messages(description, style_guidance)
        
        for attempt in range(max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=0.7,
                    max_tokens=4000,
                    top_p=1,
                    frequency_penalty=0,
                    presence_penalty=0
                )
                
                try:
                    env_data = json.loads(response.choices[0].message.content)
                except json.JSONDecodeError as e:
                    if attempt < max_retries - 1:
                        continue
                    raise LLMResponseError(
                        "Failed to parse LLM response as JSON",
                        response_text=response.choices[0].message.content
                    ) from e
                
                try:
                    return self._validate_environment(env_data)
                except SchemaValidationError as e:
                    if attempt < max_retries - 1:
                        # Add validation feedback for next attempt
                        messages.append({
                            "role": "user",
                            "content": f"The previous response had validation errors: {str(e)}"
                        })
                        continue
                    raise
                    
            except OpenAIRateLimitError as e:
                raise RateLimitError(str(e), retry_after=e.retry_after)
            except APIError as e:
                raise FlatlandLLMError(f"OpenAI API error: {str(e)}")
                
        raise LLMResponseError(
            f"Failed to generate valid environment after {max_retries} attempts"
        )

def generate_environment(
    description: str,
    style_guidance: Optional[str] = None,
    **kwargs
) -> EnvironmentDefinition:
    """Convenience function to generate a FlatLand environment.
    
    This is the main entry point for the library.
    
    Args:
        description: Free-form description of the desired environment
        style_guidance: Optional styling/theme guidance
        **kwargs: Additional arguments passed to EnvironmentGenerator.generate()
        
    Returns:
        EnvironmentDefinition object representing the generated environment
    """
    generator = EnvironmentGenerator()
    return generator.generate(description, style_guidance, **kwargs)
