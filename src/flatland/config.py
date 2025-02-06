import os

_api_key = os.environ.get("FLATLAND_OPENAI_KEY", None)

def set_api_key(key: str):
    """
    Set the OpenAI API key.
    """
    global _api_key
    _api_key = key

def get_api_key() -> str:
    """
    Retrieve the OpenAI API key. Raises an error if not set.
    """
    if _api_key is None:
        raise ValueError("OpenAI API key not set. Please call set_api_key() or set the FLATLAND_OPENAI_KEY environment variable.")
    return _api_key
