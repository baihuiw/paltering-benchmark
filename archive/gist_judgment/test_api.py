"""
Test script to verify OpenRouter API connection.

This script:
1. Loads your API key from the .env file
2. Creates a connection to OpenRouter (which provides access to multiple LLMs)
3. Sends a simple test prompt to Claude Sonnet 4.5
4. Prints the response

Python basics for this script:
- Lines starting with # are comments (ignored by Python)
- We "import" libraries to use their functionality
- We use print() to display text in the terminal
- Variables store data (like api_key, client, response)
"""

# Import required libraries
# os: helps us access environment variables and system functions
import os
# load_dotenv: reads the .env file and makes its contents available
from dotenv import load_dotenv
# OpenAI: the library to connect to OpenAI-compatible APIs (OpenRouter uses this format)
from openai import OpenAI

# Load environment variables from .env file
# This reads the .env file and makes OPENROUTER_API_KEY available
load_dotenv()

# Get the API key from environment variables
# os.getenv() retrieves the value of OPENROUTER_API_KEY
api_key = os.getenv("OPENROUTER_API_KEY")

# Check if the API key was loaded successfully
if not api_key or api_key == "placeholder":
    print("ERROR: Please add your real OpenRouter API key to the .env file")
    print("Replace 'placeholder' with your actual key from https://openrouter.ai/keys")
    exit()  # Stop the script if no valid key is found

print("API key loaded successfully!")
print(f"Testing connection to OpenRouter...")

# Create an OpenAI client configured for OpenRouter
# base_url tells it to use OpenRouter instead of OpenAI's servers
# api_key authenticates your requests
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key
)

try:
    # Send a test message to the model
    # This is like having a conversation with the AI
    response = client.chat.completions.create(
        model="anthropic/claude-sonnet-4.5",  # Which model to use
        messages=[
            {
                "role": "user",  # We're the user
                "content": "Say hello in five words"  # Our prompt
            }
        ]
    )

    # Extract the AI's response from the response object
    # The response is nested in: response.choices[0].message.content
    ai_response = response.choices[0].message.content

    # Print the results
    print("\n" + "="*50)
    print("SUCCESS! OpenRouter connection is working.")
    print("="*50)
    print(f"\nPrompt: Say hello in five words")
    print(f"Model: anthropic/claude-sonnet-4.5")
    print(f"\nResponse: {ai_response}")
    print("\n" + "="*50)

except Exception as e:
    # If anything goes wrong, print the error
    print(f"\nERROR: {e}")
    print("\nCommon issues:")
    print("1. Invalid API key - check your .env file")
    print("2. No internet connection")
    print("3. OpenRouter service is down")
