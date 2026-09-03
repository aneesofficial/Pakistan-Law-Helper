import os
from google import genai
from google.genai import types
from google.genai.errors import APIError
from typing import List, Union
import time
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Configure Gemini
api_key = os.getenv("GEMINI_API_KEY")

class GeminiServiceError(Exception):
    """Custom exception for Gemini service errors."""
    pass

_client = None

def init_gemini():
    """Initializes the Gemini SDK with the API key."""
    global _client
    if not api_key or api_key == "your_gemini_api_key_here":
        raise GeminiServiceError("GEMINI_API_KEY is missing or not configured correctly in .env.")
    
    if _client is None:
        _client = genai.Client(api_key=api_key)

def generate_answer(prompt: str, max_retries: int = 3, primary_model: str = "gemini-3.6-flash", fallback_model: str = "gemini-3.6-flash") -> str:
    """
    Generates a text answer using Gemini based on the provided prompt.
    Implements retries, exponential backoff, and a fallback model.
    """
    init_gemini()
    
    # This account only has access to gemini-3.x generation models. 
    # gemini-2.5-flash, gemini-2.5-flash-lite, and gemini-1.5-flash all return 404 for this API key. 
    # Free tier limit for gemini-3.6-flash is 20 requests/day.
    primary_model = os.getenv("GEMINI_MODEL", "gemini-3.6-flash")
    fallback_model = os.getenv("GEMINI_FALLBACK_MODEL", "gemini-3.6-flash")
    
    max_retries = 3
    delay = 1.0

    # Primary model loop
    for attempt in range(max_retries):
        try:
            response = _client.models.generate_content(
                model=primary_model,
                contents=prompt,
            )
            if not response.text:
                return "The model returned an empty response. This might be due to safety filters."
            return response.text
        except Exception as e:
            error_str = str(e).lower()
            if "api_key" in error_str or "401" in error_str or "403" in error_str:
                raise GeminiServiceError("Authentication error. Please check your GEMINI_API_KEY.")
                
            if "503" in error_str or "unavailable" in error_str or "quota" in error_str or "429" in error_str:
                if attempt < max_retries - 1:
                    time.sleep(delay)
                    delay *= 2
                    continue
                else:
                    break # Give up on primary
            else:
                break # Non-retryable error

    # Fallback model attempt
    try:
        response = _client.models.generate_content(
            model=fallback_model,
            contents=prompt,
        )
        if not response.text:
            return "The model returned an empty response. This might be due to safety filters."
        return response.text
    except Exception as e:
        error_str = str(e).lower()
        if "quota" in error_str or "429" in error_str:
            raise GeminiServiceError("API Quota exceeded or rate limited on fallback model.")
        elif "503" in error_str or "unavailable" in error_str:
            raise GeminiServiceError("503 UNAVAILABLE: Both primary and fallback models are currently experiencing high demand.")
        raise GeminiServiceError(f"Failed to generate answer: {e}")
