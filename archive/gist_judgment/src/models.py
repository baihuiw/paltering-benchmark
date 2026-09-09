"""
Model Management System for OpenRouter API

PURPOSE:
This module provides a clean interface for calling different LLMs via OpenRouter.
You can easily swap models in and out, call multiple models with the same prompt,
and handle errors gracefully.

"""

# ============================================================================
# IMPORTS - Libraries we need
# ============================================================================

import os  # For accessing environment variables
import time  # For adding delays between API calls (rate limiting)
from datetime import datetime  # For tracking when API calls happen
from dotenv import load_dotenv  # For loading API keys from .env file
from openai import OpenAI  # OpenRouter uses OpenAI's API format

# Load environment variables from .env file
# This makes your API key available via os.getenv()
load_dotenv()


# ============================================================================
# MODELS
# ============================================================================

MODELS = {
    "claude-sonnet": {
        "id": "anthropic/claude-sonnet-4.5",
        "name": "Claude Sonnet 4.5",
        "provider": "Anthropic"
    },
    "gpt-4": {
        "id": "openai/gpt-4-turbo",
        "name": "GPT-4 Turbo",
        "provider": "OpenAI"
    },
    "gemini": {
        "id": "google/gemini-pro-1.5",
        "name": "Gemini Pro 1.5",
        "provider": "Google"
    },
    "llama": {
        "id": "meta-llama/llama-3.1-70b-instruct",
        "name": "Llama 3.1 70B",
        "provider": "Meta"
    }
}

"""
HOW TO ADD NEW MODELS:

Simply add a new entry to the MODELS dictionary above:

"model-key": {
    "id": "provider/model-id-on-openrouter",
    "name": "Human Readable Name",
    "provider": "Provider Name"
}

The "id" must match what OpenRouter expects. Check https://openrouter.ai/models
for the exact model IDs.
"""


# ============================================================================
# HELPER FUNCTIONS - Utilities for working with models
# ============================================================================

def get_available_models():
    """
    Get a list of all available model keys.

    PYTHON CONCEPT - Dictionary methods:
    .keys() returns all the keys in a dictionary
    list() converts it to a list (ordered collection)

    Returns:
        List of strings, each being a model key (e.g., ["claude-sonnet", "gpt-4"])
    """
    return list(MODELS.keys())


def get_model_info(model_key):
    """
    Get detailed information about a specific model.

    Args:
        model_key: String key like "claude-sonnet"

    Returns:
        Dictionary with model information, or None if model doesn't exist

    Example:
        info = get_model_info("claude-sonnet")
        print(info["name"])  # Output: Claude Sonnet 4.5
    """
    return MODELS.get(model_key)  # .get() returns None if key doesn't exist


def validate_model_key(model_key):
    """
    Check if a model key is valid. Raise an error if not.

    PYTHON CONCEPT - Raising exceptions:
    When something goes wrong, we can "raise" an exception to stop execution
    and show an error message. This is better than silently failing.

    Args:
        model_key: String to validate

    Raises:
        ValueError: If the model key doesn't exist

    Example:
        validate_model_key("claude-sonnet")  # OK, does nothing
        validate_model_key("fake-model")     # Raises ValueError
    """
    if model_key not in MODELS:
        available = ", ".join(get_available_models())
        raise ValueError(
            f"Invalid model key: '{model_key}'\n"
            f"Available models: {available}"
        )


# ============================================================================
# MAIN API FUNCTIONS - Call models via OpenRouter
# ============================================================================

def call_model(prompt, model_key, temperature=0.7, max_tokens=1500):
    
    # Validate the model key first
    validate_model_key(model_key)

    # Get model information
    model_info = MODELS[model_key]
    model_id = model_info["id"]
    model_name = model_info["name"]

    # Get API key from environment
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key or api_key == "placeholder":
        return {
            "model_key": model_key,
            "model_id": model_id,
            "prompt": prompt,
            "response": None,
            "timestamp": datetime.now().isoformat(),
            "success": False,
            "error": "OPENROUTER_API_KEY not set in .env file"
        }

    # Create timestamp for this call
    timestamp = datetime.now().isoformat()

    # Initialize result dictionary
    # We'll fill this in as we go
    result = {
        "model_key": model_key,
        "model_id": model_id,
        "prompt": prompt,
        "response": None,
        "timestamp": timestamp,
        "success": False,
        "error": None
    }

    try:
        # Create OpenAI client configured for OpenRouter
        # base_url tells it to use OpenRouter instead of OpenAI
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key
        )

        # Call the model
        # This sends your prompt to OpenRouter, which forwards it to the model
        response = client.chat.completions.create(
            model=model_id,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=temperature,
            max_tokens=max_tokens
        )

        # Extract the response text
        # The response is nested: response → choices → [0] → message → content
        response_text = response.choices[0].message.content

        # Update result with success
        result["response"] = response_text
        result["success"] = True

        # Rate limiting: wait 1 second before allowing next call
        # This prevents hitting API rate limits
        # IMPORTANT: This slows down your eval, but prevents errors
        time.sleep(1)

    except Exception as e:
        # Something went wrong - capture the error
        # PYTHON CONCEPT - Exception handling:
        # "Exception" catches ANY error
        # "as e" gives us access to the error details
        result["error"] = str(e)
        result["success"] = False

    return result


def call_multiple_models(prompt, model_keys, **kwargs):
   
    results = []  # List to collect all results
    total = len(model_keys)  # How many models we're calling

    # Loop through each model
    # enumerate gives us both the index (0, 1, 2...) and the model_key
    for index, model_key in enumerate(model_keys, start=1):
        # Get model name for progress message
        model_info = get_model_info(model_key)
        if model_info:
            model_name = model_info["name"]
        else:
            model_name = model_key

        # Show progress
        # This helps you see what's happening during long eval runs
        print(f"Calling {model_name}... ({index}/{total})")

        # Call the model
        # **kwargs passes through any extra arguments (temperature, etc.)
        result = call_model(prompt, model_key, **kwargs)

        # Add to results list
        results.append(result)

        # Show if it succeeded or failed
        if result["success"]:
            print(f"  ✓ Success")
        else:
            print(f"  ✗ Failed: {result['error']}")

    return results


# ============================================================================
# CONVENIENCE FUNCTION - Get a specific response
# ============================================================================

def get_response_text(result):
    
    if result["success"]:
        return result["response"]
    else:
        return None


# ============================================================================
# TEST BLOCK - Runs when you execute this file directly
# ============================================================================

if __name__ == "__main__":
    """
    PYTHON CONCEPT - if __name__ == "__main__":

    This is a special Python pattern. Code inside this block only runs when
    you execute this file directly (python src/models.py), NOT when you
    import it from another file.

    This lets us:
    1. Test the module by running it directly
    2. Import it in other files without running the test

    Example:
        python src/models.py          → runs this test block
        from src.models import call_model  → doesn't run test block
    """

    print("=" * 70)
    print("TESTING MODEL MANAGEMENT SYSTEM")
    print("=" * 70)

    # Test 1: List available models
    print("\n📋 Available models:")
    for model_key in get_available_models():
        info = get_model_info(model_key)
        print(f"  - {model_key}: {info['name']} ({info['provider']})")

    # Test 2: Single model call
    print("\n🧪 Testing single model call...")
    print("Prompt: 'Say hello in exactly five words'")

    result = call_model(
        prompt="Say hello in exactly five words",
        model_key="claude-sonnet"
    )

    print(f"\nModel: {result['model_id']}")
    print(f"Timestamp: {result['timestamp']}")
    print(f"Success: {result['success']}")

    if result['success']:
        print(f"Response: {result['response']}")
    else:
        print(f"Error: {result['error']}")

    # Test 3: Multiple models (optional - uncomment to test)
    # This will cost more API credits, so it's commented out by default
    """
    print("\n🧪 Testing multiple models...")
    results = call_multiple_models(
        "Say hello in exactly five words",
        ["claude-sonnet", "gpt-4"],
        temperature=0.7
    )

    print(f"\nGot {len(results)} results:")
    for r in results:
        print(f"  {r['model_key']}: {r['success']}")
    """

    print("\n" + "=" * 70)
    print("Test complete!")
    print("=" * 70)
