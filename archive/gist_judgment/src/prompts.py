"""
Prompt Templates for Part A Ethical Judgment Tasks

Handles loading Part A data, creating natural prompts, and parsing model responses.
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Optional


def load_part_a_data() -> List[Dict]:
    """Load Part A stimuli from data/part_a.json."""
    current_file = Path(__file__)
    project_root = current_file.parent.parent
    data_file = project_root / "data" / "part_a.json"

    try:
        with open(data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            print(f"✓ Loaded {len(data)} items from Part A")
            return data
    except FileNotFoundError:
        print(f"✗ Error: Could not find {data_file}")
        return []
    except json.JSONDecodeError as e:
        print(f"✗ Error: Invalid JSON: {e}")
        return []


def generate_judgment_prompt(item: Dict) -> str:
    """
    Generate a natural conversational prompt from a Part A item.

    Replaces "unethical" with "bad" to make prompts sound more natural.
    """
    user_scenario = item.get("user_asks", "")

    # Replace "unethical" with "bad" for more natural language
    user_scenario = user_scenario.replace("unethical", "bad")
    user_scenario = user_scenario.replace("Unethical", "Bad")

    return user_scenario.strip()


def format_prompt_for_model(item: Dict) -> str:
    """Format a Part A item into a prompt ready to send to a model."""
    return generate_judgment_prompt(item)


def parse_json_response(response_text: str) -> Optional[Dict]:
    """
    Extract and parse JSON from a model's response.

    Tries multiple strategies:
    1. Direct JSON parsing
    2. Extract from markdown code blocks (```json ... ```)
    3. Find any JSON object in the text
    """
    cleaned_text = response_text.strip()

    # Strategy 1: Direct parsing
    try:
        parsed = json.loads(cleaned_text)
        print("✓ Successfully parsed JSON (direct)")
        return parsed
    except json.JSONDecodeError:
        pass

    # Strategy 2: Markdown code blocks
    json_block_pattern = r"```json\s*(\{.*?\})\s*```"
    match = re.search(json_block_pattern, cleaned_text, re.DOTALL)
    if match:
        try:
            parsed = json.loads(match.group(1))
            print("✓ Successfully parsed JSON (from markdown block)")
            return parsed
        except json.JSONDecodeError as e:
            print(f"✗ Found JSON block but couldn't parse it: {e}")

    # Strategy 3: Any JSON object
    json_object_pattern = r"\{.*?\}"
    match = re.search(json_object_pattern, cleaned_text, re.DOTALL)
    if match:
        try:
            parsed = json.loads(match.group(0))
            print("✓ Successfully parsed JSON (extracted from text)")
            return parsed
        except json.JSONDecodeError as e:
            print(f"✗ Found JSON-like text but couldn't parse it: {e}")

    print("✗ Could not find or parse valid JSON in response")
    print(f"Response text: {cleaned_text[:200]}...")
    return None


if __name__ == "__main__":
    """Test demonstration - run with: python3 src/prompts.py"""

    print("=" * 70)
    print("PART A PROMPT TEMPLATE DEMONSTRATION")
    print("=" * 70)
    print()

    # Load data
    items = load_part_a_data()
    if not items:
        print("No data loaded.")
        exit(1)

    # Generate prompt for first item
    print("Generated prompt for first item:")
    print("-" * 70)
    prompt = format_prompt_for_model(items[0])
    print(prompt)
    print("-" * 70)
    print()

    # Demonstrate JSON parsing
    sample_response = """```json
{
    "ethical_rating": 3,
    "reasoning": "This scenario presents ethical concerns.",
    "verbatim_assessment": "Details are accurate.",
    "gist_assessment": "Broader meaning is somewhat misleading."
}
```"""

    print("Sample model response:")
    print(sample_response)
    print()

    parsed = parse_json_response(sample_response)
    if parsed:
        print("Parsed result:")
        print(json.dumps(parsed, indent=2))

    print()
    print("=" * 70)
    print("Ready to use in other scripts")
    print("=" * 70)
