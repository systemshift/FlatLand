"""
Enhanced LLM client for FlatLand.

This module extends the FlatLand LLM client to support GPT-4 and GPT-4.5 models
with optimized prompting for grid environment generation.
"""
from flatland.llm.client import EnvironmentGenerator
from flatland.llm.exceptions import LLMGenerationError, LLMAPIError
from flatland.config import set_api_key
import os
import json
import time
from typing import Dict, Any, Optional

# Import the OpenAI client
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

class EnhancedEnvironmentGenerator(EnvironmentGenerator):
    """
    Enhanced environment generator that uses advanced GPT models.
    
    This class extends the base EnvironmentGenerator to implement optimized
    prompting for the latest OpenAI models.
    """
    
    def __init__(self, 
                 api_key: Optional[str] = None, 
                 rate_limit: int = 10,
                 timeout: int = 60):
        """
        Initialize the enhanced environment generator.
        
        Args:
            api_key: OpenAI API key (optional if set via env var or config)
            rate_limit: Number of requests allowed per minute
            timeout: Timeout for API requests in seconds
        """
        super().__init__(api_key, rate_limit, timeout)
        
        # Set up model specific options
        self.model_options = {
            # GPT-4.5 specific options (for future use)
            "gpt-4.5-turbo": {
                "temperature": 0.5,
                "max_tokens": 4000,
                "top_p": 0.9,
                "frequency_penalty": 0.0,
                "presence_penalty": 0.0,
                "response_format": {"type": "json_object"}
            },
            # Current GPT-4 models
            "gpt-4-turbo-preview": {
                "temperature": 0.7,
                "max_tokens": 4000,
                "top_p": 1.0,
                "frequency_penalty": 0.0,
                "presence_penalty": 0.0,
                "response_format": {"type": "json_object"}
            },
            "gpt-4": {
                "temperature": 0.7,
                "max_tokens": 4000,
                "top_p": 1.0,
                "frequency_penalty": 0.0,
                "presence_penalty": 0.0,
                "response_format": {"type": "json_object"}
            }
        }
        
        # Initialize the OpenAI client if available
        if OPENAI_AVAILABLE:
            self.client = OpenAI(api_key=self._api_key)
        else:
            raise ImportError("OpenAI package is not installed. Please install it with 'pip install openai'.")
    
    def _optimize_prompt(self, description: str, style_guidance: Optional[str] = None) -> str:
        """
        Optimize the prompt template for advanced models.
        
        Args:
            description: User's description of the environment
            style_guidance: Optional style guidance for the environment
            
        Returns:
            Optimized prompt
        """
        # Get the base prompt from the template
        with open(self._template_path, 'r') as f:
            prompt_template = f.read()
        
        # Apply model-specific optimizations
        prompt = prompt_template.replace('{description}', description)
        
        if style_guidance:
            prompt += f"\n\nStyle guidance: {style_guidance}"
        
        # Add specific instructions for better JSON output
        prompt += """

Additional guidelines:
1. Ensure all grid positions use zero-based indexing [row, column]
2. Keep grid dimensions reasonable (ideal size is 10x10 to 20x20)
3. Use simple, consistent entity symbols
4. All rules must have a clear "when" condition and "then" action
5. Validate that your JSON follows the required schema before responding
6. Return ONLY the JSON output with no additional text or explanation
"""
        
        return prompt
    
    def generate(self, 
                description: str, 
                style_guidance: Optional[str] = None,
                model: str = "gpt-4-turbo-preview",  # Default to current best model
                max_attempts: int = 3) -> Dict[str, Any]:
        """
        Generate an environment using advanced GPT models.
        
        Args:
            description: User's description of the environment
            style_guidance: Optional style guidance for the environment
            model: The model to use
            max_attempts: Maximum number of attempts to generate a valid environment
            
        Returns:
            A valid environment definition
            
        Raises:
            LLMGenerationError: If the environment cannot be generated after max_attempts
            LLMAPIError: If there is an API error
        """
        # Rate limiting
        self._check_rate_limit()
        
        # Get model options
        model_options = self.model_options.get(model, self.model_options["gpt-4-turbo-preview"])
        
        # Generate optimized prompt
        prompt = self._optimize_prompt(description, style_guidance)
        
        # Track attempts
        attempts = 0
        
        while attempts < max_attempts:
            attempts += 1
            
            try:
                # Call the API with the new client
                response = self.client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": "You are an expert environment designer for grid-based simulations."},
                        {"role": "user", "content": prompt}
                    ],
                    **model_options
                )
                
                # Parse the response
                try:
                    response_content = response.choices[0].message.content
                    environment = json.loads(response_content)
                    
                    # Validate the environment
                    self._validate_environment(environment)
                    
                    # Return the valid environment
                    return environment
                    
                except json.JSONDecodeError:
                    # If we can't parse the JSON, try to extract it from the response
                    if attempts < max_attempts:
                        # Add feedback about JSON format
                        prompt += "\n\nYour previous response contained invalid JSON. Please provide a valid JSON object."
                    else:
                        raise LLMGenerationError("Failed to parse JSON from LLM response")
                
                except Exception as e:
                    # If validation fails, provide feedback and retry
                    if attempts < max_attempts:
                        # Add feedback about validation errors
                        prompt += f"\n\nYour previous response had the following issues: {str(e)}"
                        prompt += "\nPlease fix these issues and provide a valid environment definition."
                    else:
                        raise LLMGenerationError(f"Failed to generate valid environment after {max_attempts} attempts: {str(e)}")
                        
            except Exception as e:
                # Handle API errors
                if attempts < max_attempts:
                    # Wait before retrying
                    time.sleep(2)
                else:
                    raise LLMAPIError(f"API error: {str(e)}")
        
        # If we get here, we've exceeded max attempts
        raise LLMGenerationError(f"Failed to generate valid environment after {max_attempts} attempts")


# Add convenience function for direct use
def generate_environment(
    description: str,
    style_guidance: Optional[str] = None,
    api_key: Optional[str] = None,
    model: str = "gpt-4-turbo-preview"  # Default to current best model
) -> Dict[str, Any]:
    """
    Generate an environment using advanced GPT models.
    
    Args:
        description: User's description of the environment
        style_guidance: Optional style guidance for the environment
        api_key: OpenAI API key (optional if set via env var or config)
        model: The model to use
        
    Returns:
        A valid environment definition
    """
    generator = EnhancedEnvironmentGenerator(api_key)
    return generator.generate(description, style_guidance, model)