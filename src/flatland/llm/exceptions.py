"""
Custom exceptions for the FlatLand LLM integration module.
"""

class FlatlandLLMError(Exception):
    """Base exception for all FlatLand LLM-related errors."""
    pass

class SchemaValidationError(FlatlandLLMError):
    """Raised when generated environment fails schema validation."""
    def __init__(self, message: str, validation_errors: list = None):
        super().__init__(message)
        self.validation_errors = validation_errors or []

class RateLimitError(FlatlandLLMError):
    """Raised when OpenAI API rate limits are exceeded."""
    def __init__(self, message: str, retry_after: int = None):
        super().__init__(message)
        self.retry_after = retry_after

class LLMResponseError(FlatlandLLMError):
    """Raised when there are issues with the LLM response."""
    def __init__(self, message: str, response_text: str = None):
        super().__init__(message)
        self.response_text = response_text
