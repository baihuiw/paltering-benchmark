"""
Stimulus Builder - Converts Markdown stimuli files to JSON format

PURPOSE:
This script reads human-editable Markdown files (stimuli/part_a.md and stimuli/part_b.md),
validates their structure, and converts them to JSON files (data/part_a.json and data/part_b.json)
that can be easily consumed by the evaluation runner.

UPDATED FOR REALISTIC SCENARIOS:
- Part A now includes "User asks:" field for realistic social contexts
- Part B now includes "Source document:" field with factual information

WORKFLOW:
1. Read Markdown files
2. Parse the structured content (scenarios, items, cells)
3. Validate everything (correct number of items, no missing fields, etc.)
4. Convert to JSON format with unique IDs
5. Save JSON files

WHY THIS APPROACH?
- Markdown is easy for humans to read and edit
- JSON is easy for programs to read
- Validation catches errors early
- Single source of truth (Markdown files)
- Reusable for future evals (just swap the Markdown files)

PYTHON CONCEPTS USED:
- Functions: Reusable blocks of code
- File I/O: Reading and writing files
- String manipulation: Extracting data from text
- Lists and Dictionaries: Organizing data
- JSON: A standard format for structured data
- Error handling: Catching and reporting problems
"""

# Import libraries
# These are pre-written code packages that add functionality
import json  # For reading/writing JSON format
import re    # For "regular expressions" - pattern matching in text
import os    # For file and directory operations


# ============================================================================
# CONFIGURATION - Define what we expect in the files
# ============================================================================

# These are the allowed cell types for Part A
# Using a set (curly braces) because we only care about membership, not order
ALLOWED_CELL_TYPES = {
    'fully_true',
    'palter',
    'truthy_falsehood',
    'blatant_falsehood'
}

# File paths - where to read from and write to
PART_A_INPUT = 'stimuli/part_a.md'
PART_B_INPUT = 'stimuli/part_b.md'
PART_A_OUTPUT = 'data/part_a.json'
PART_B_OUTPUT = 'data/part_b.json'

# Expected counts for validation
EXPECTED_SCENARIOS = 5  # Part A should have 5 scenarios
EXPECTED_CELLS_PER_SCENARIO = 4  # Each scenario should have 4 cells
EXPECTED_ITEMS = 5  # Part B should have 5 items


# ============================================================================
# HELPER FUNCTIONS - Small utilities used by larger functions
# ============================================================================

def read_file(filepath):
    """
    Read a file and return its contents as a string.

    PYTHON CONCEPT - File I/O:
    - open(filepath, 'r') opens a file for reading ('r' = read mode)
    - 'with' ensures the file is properly closed after we're done
    - .read() gets all the text from the file

    Args:
        filepath: String path to the file (e.g., 'stimuli/part_a.md')

    Returns:
        String containing the entire file contents
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()


def write_json(data, filepath):
    """
    Write data to a JSON file with nice formatting.

    PYTHON CONCEPT - JSON:
    JSON (JavaScript Object Notation) is a standard way to store structured data.
    It's like a universal language that both humans and programs can read.

    Example JSON:
    [
        {"name": "Alice", "age": 30},
        {"name": "Bob", "age": 25}
    ]

    Args:
        data: Python data structure (lists and dictionaries) to save
        filepath: Where to save the JSON file
    """
    # Create the directory if it doesn't exist
    # os.path.dirname gets the directory part of a path
    # os.makedirs creates directories (exist_ok=True means don't error if it already exists)
    directory = os.path.dirname(filepath)
    if directory:  # Only create if there's actually a directory part
        os.makedirs(directory, exist_ok=True)

    # Write the JSON file
    # indent=2 makes it pretty (2 spaces per indentation level)
    # ensure_ascii=False allows Unicode characters
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def extract_topic_from_heading(heading):
    """
    Extract the topic name from a heading like "## Scenario 1: Climate Change"

    PYTHON CONCEPT - String manipulation:
    We use .split(':') to break the string at the colon, then take the part after it.
    .strip() removes extra whitespace from the beginning and end.

    Args:
        heading: String like "## Scenario 1: Climate Change"

    Returns:
        String like "Climate Change"
    """
    if ':' in heading:
        # Split on ':', take everything after the colon, remove whitespace
        return heading.split(':', 1)[1].strip()
    else:
        # If no colon, just remove the ## and number
        # This is a fallback - properly formatted headings should have colons
        return heading.replace('#', '').strip()


def extract_multiline_field(lines, start_idx, field_name, next_field_names):
    """
    Extract a field that might span multiple lines.

    This helper handles fields like "User asks:" or "Prompt:" that might
    wrap across multiple lines. It collects all lines until it hits the
    next labeled field.

    Args:
        lines: List of all lines in the section
        start_idx: Where to start looking
        field_name: The field we're looking for (e.g., "User asks:")
        next_field_names: List of field names that would end this field

    Returns:
        Tuple of (field_content, next_start_idx)
    """
    content_lines = []
    i = start_idx

    while i < len(lines):
        line = lines[i].strip()

        # Check if this is the start of the next field
        is_next_field = any(line.startswith(name + ':') for name in next_field_names)
        if is_next_field:
            break

        # Skip empty lines at the start
        if not content_lines and not line:
            i += 1
            continue

        # Add this line to content
        if line:
            content_lines.append(line)

        i += 1

    return ' '.join(content_lines), i


# ============================================================================
# PART A PARSER - Parse the 2×2 taxonomy scenarios with realistic contexts
# ============================================================================

def parse_part_a(markdown_text):
    """
    Parse Part A Markdown into structured data.

    UPDATED FORMAT:
    Part A now includes realistic user scenarios with "User asks:" field.

    Structure:
    ## Scenario N: Topic
    Background: ...

    ### cell_type
    User asks: [Multi-line scenario description]
    Statement: [The claim]
    Context: [Truth status explanation]

    Returns:
        List of dictionaries, where each dictionary represents one cell
    """
    results = []  # This will hold all our parsed data

    # Split the text into scenarios using ## as the delimiter
    # [1:] means "skip the first element" (which is the comment block before the first ##)
    scenario_sections = re.split(r'^## ', markdown_text, flags=re.MULTILINE)[1:]

    # Process each scenario
    for scenario_idx, scenario_section in enumerate(scenario_sections, start=1):
        lines = scenario_section.split('\n')
        heading = lines[0].strip()
        topic = extract_topic_from_heading(heading)

        # Extract background
        background = ""
        for line in lines:
            if line.startswith('Background:'):
                background = line.replace('Background:', '').strip()
                break

        if not background:
            raise ValueError(
                f"ERROR in {PART_A_INPUT} - Scenario {scenario_idx} ({topic}): "
                f"Missing 'Background:' field"
            )

        # Split into cells (by ### headings)
        cell_sections = re.split(r'^### ', scenario_section, flags=re.MULTILINE)[1:]

        # Check that we have exactly 4 cells
        if len(cell_sections) != EXPECTED_CELLS_PER_SCENARIO:
            raise ValueError(
                f"ERROR in {PART_A_INPUT} - Scenario {scenario_idx} ({topic}): "
                f"Expected {EXPECTED_CELLS_PER_SCENARIO} cells, found {len(cell_sections)}. "
                f"Each scenario must have: fully_true, palter, truthy_falsehood, blatant_falsehood"
            )

        # Process each cell
        for cell_section in cell_sections:
            cell_lines = cell_section.split('\n')
            cell_type = cell_lines[0].strip()

            # Validate cell type
            if cell_type not in ALLOWED_CELL_TYPES:
                raise ValueError(
                    f"ERROR in {PART_A_INPUT} - Scenario {scenario_idx} ({topic}): "
                    f"Invalid cell type '{cell_type}'. Must be one of: {ALLOWED_CELL_TYPES}"
                )

            # Extract fields: User asks, Statement, Context
            user_asks = ""
            statement = ""
            context = ""

            # Track current field for multi-line parsing
            current_field = None
            field_content = []

            for line in cell_lines[1:]:
                line_stripped = line.strip()
                if not line_stripped:
                    continue

                # Check for field labels
                if line_stripped.startswith('User asks:'):
                    # Save previous field
                    if current_field == 'statement':
                        statement = ' '.join(field_content)
                    elif current_field == 'context':
                        context = ' '.join(field_content)
                    # Start new field
                    current_field = 'user_asks'
                    field_content = [line_stripped.replace('User asks:', '').strip()]
                elif line_stripped.startswith('Statement:'):
                    # Save previous field
                    if current_field == 'user_asks':
                        user_asks = ' '.join(field_content)
                    elif current_field == 'context':
                        context = ' '.join(field_content)
                    # Start new field
                    current_field = 'statement'
                    field_content = [line_stripped.replace('Statement:', '').strip()]
                elif line_stripped.startswith('Context:'):
                    # Save previous field
                    if current_field == 'user_asks':
                        user_asks = ' '.join(field_content)
                    elif current_field == 'statement':
                        statement = ' '.join(field_content)
                    # Start new field
                    current_field = 'context'
                    field_content = [line_stripped.replace('Context:', '').strip()]
                else:
                    # Continuation of current field
                    if current_field:
                        field_content.append(line_stripped)

            # Don't forget the last field
            if current_field == 'user_asks':
                user_asks = ' '.join(field_content)
            elif current_field == 'statement':
                statement = ' '.join(field_content)
            elif current_field == 'context':
                context = ' '.join(field_content)

            # Validate all fields are present
            if not user_asks:
                raise ValueError(
                    f"ERROR in {PART_A_INPUT} - Scenario {scenario_idx} ({topic}), "
                    f"Cell '{cell_type}': Missing 'User asks:' field"
                )
            if not statement:
                raise ValueError(
                    f"ERROR in {PART_A_INPUT} - Scenario {scenario_idx} ({topic}), "
                    f"Cell '{cell_type}': Missing 'Statement:' field"
                )
            if not context:
                raise ValueError(
                    f"ERROR in {PART_A_INPUT} - Scenario {scenario_idx} ({topic}), "
                    f"Cell '{cell_type}': Missing 'Context:' field"
                )

            # Determine verbatim and gist truth based on cell type
            truth_mapping = {
                'fully_true': (True, True),
                'palter': (True, False),
                'truthy_falsehood': (False, True),
                'blatant_falsehood': (False, False)
            }
            verbatim_truth, gist_truth = truth_mapping[cell_type]

            # Create unique ID
            item_id = f"part_a_s{scenario_idx}_{cell_type}"

            # Build the data structure for this cell
            cell_data = {
                'id': item_id,
                'scenario_id': scenario_idx,
                'topic': topic,
                'background': background,
                'cell_type': cell_type,
                'verbatim_truth': verbatim_truth,
                'gist_truth': gist_truth,
                'user_asks': user_asks,  # NEW FIELD
                'statement': statement,
                'context': context
            }

            results.append(cell_data)

    # Validate total count
    expected_total = EXPECTED_SCENARIOS * EXPECTED_CELLS_PER_SCENARIO
    if len(results) != expected_total:
        raise ValueError(
            f"ERROR in {PART_A_INPUT}: Expected {expected_total} total cells "
            f"({EXPECTED_SCENARIOS} scenarios × {EXPECTED_CELLS_PER_SCENARIO} cells), "
            f"but found {len(results)}"
        )

    return results


# ============================================================================
# PART B PARSER - Parse the behavioral production items with source documents
# ============================================================================

def parse_part_b(markdown_text):
    """
    Parse Part B Markdown into structured data.

    UPDATED FORMAT:
    Part B now includes "Source document:" field with factual information.

    Structure:
    ## Item N: Topic

    Source document: |
      [Multi-paragraph factual document]

    Prompt: [Communication task]

    False detail: [What to watch for]

    True fact: [What should be conveyed]

    Returns:
        List of dictionaries, where each dictionary represents one item
    """
    results = []

    # Split into items (by ## headings)
    item_sections = re.split(r'^## ', markdown_text, flags=re.MULTILINE)[1:]

    # Process each item
    for item_idx, item_section in enumerate(item_sections, start=1):
        lines = item_section.split('\n')
        heading = lines[0].strip()
        topic = extract_topic_from_heading(heading)

        # Extract all fields
        source_document = ""
        prompt = ""
        false_detail = ""
        true_fact = ""

        # Track current field
        current_field = None
        field_content = []
        in_source_doc = False

        for i, line in enumerate(lines[1:]):
            line_stripped = line.strip()

            # Check for field labels
            if line_stripped.startswith('Source document:'):
                # Save previous field if any
                if current_field == 'prompt':
                    prompt = ' '.join(field_content)
                elif current_field == 'false_detail':
                    false_detail = ' '.join(field_content)
                elif current_field == 'true_fact':
                    true_fact = ' '.join(field_content)
                # Start source document (special handling for block)
                current_field = 'source_document'
                field_content = []
                in_source_doc = True
            elif line_stripped.startswith('Prompt:'):
                # Save previous field
                if current_field == 'source_document':
                    source_document = '\n'.join(field_content).strip()
                    in_source_doc = False
                elif current_field == 'false_detail':
                    false_detail = ' '.join(field_content)
                elif current_field == 'true_fact':
                    true_fact = ' '.join(field_content)
                # Start new field
                current_field = 'prompt'
                field_content = [line_stripped.replace('Prompt:', '').strip()]
            elif line_stripped.startswith('False detail:'):
                # Save previous field
                if current_field == 'prompt':
                    prompt = ' '.join(field_content)
                elif current_field == 'true_fact':
                    true_fact = ' '.join(field_content)
                # Start new field
                current_field = 'false_detail'
                field_content = [line_stripped.replace('False detail:', '').strip()]
            elif line_stripped.startswith('True fact:'):
                # Save previous field
                if current_field == 'prompt':
                    prompt = ' '.join(field_content)
                elif current_field == 'false_detail':
                    false_detail = ' '.join(field_content)
                # Start new field
                current_field = 'true_fact'
                field_content = [line_stripped.replace('True fact:', '').strip()]
            else:
                # Continuation of current field
                if current_field:
                    if in_source_doc:
                        # For source document, preserve line breaks and indentation
                        if line_stripped:  # Skip empty lines
                            field_content.append(line_stripped)
                    else:
                        # For other fields, join with spaces
                        if line_stripped:
                            field_content.append(line_stripped)

        # Don't forget the last field
        if current_field == 'source_document':
            source_document = '\n'.join(field_content).strip()
        elif current_field == 'prompt':
            prompt = ' '.join(field_content)
        elif current_field == 'false_detail':
            false_detail = ' '.join(field_content)
        elif current_field == 'true_fact':
            true_fact = ' '.join(field_content)

        # Validate all fields are present
        if not source_document:
            raise ValueError(
                f"ERROR in {PART_B_INPUT} - Item {item_idx} ({topic}): "
                f"Missing 'Source document:' field"
            )
        if not prompt:
            raise ValueError(
                f"ERROR in {PART_B_INPUT} - Item {item_idx} ({topic}): "
                f"Missing 'Prompt:' field"
            )
        if not false_detail:
            raise ValueError(
                f"ERROR in {PART_B_INPUT} - Item {item_idx} ({topic}): "
                f"Missing 'False detail:' field"
            )
        if not true_fact:
            raise ValueError(
                f"ERROR in {PART_B_INPUT} - Item {item_idx} ({topic}): "
                f"Missing 'True fact:' field"
            )

        # Create unique ID
        item_id = f"part_b_i{item_idx}"

        # Build data structure
        item_data = {
            'id': item_id,
            'item_id': item_idx,
            'topic': topic,
            'source_document': source_document,  # NEW FIELD
            'prompt': prompt,
            'false_detail': false_detail,
            'true_fact': true_fact
        }

        results.append(item_data)

    # Validate count
    if len(results) != EXPECTED_ITEMS:
        raise ValueError(
            f"ERROR in {PART_B_INPUT}: Expected {EXPECTED_ITEMS} items, "
            f"but found {len(results)}"
        )

    return results


# ============================================================================
# MAIN FUNCTION - Orchestrates the entire build process
# ============================================================================

def build_stimuli():
    """
    Main function that coordinates the entire build process.

    Steps:
    1. Read Markdown files
    2. Parse them (with updated fields)
    3. Validate (happens during parsing)
    4. Write JSON files
    5. Print success message
    """
    print("=" * 70)
    print("BUILDING STIMULI FILES")
    print("=" * 70)

    # Part A
    print(f"\n📖 Reading {PART_A_INPUT}...")
    try:
        part_a_text = read_file(PART_A_INPUT)
        print(f"✓ File read successfully ({len(part_a_text)} characters)")

        print(f"\n🔍 Parsing Part A (with realistic user scenarios)...")
        part_a_data = parse_part_a(part_a_text)
        print(f"✓ Parsed {len(part_a_data)} cells from {EXPECTED_SCENARIOS} scenarios")

        print(f"\n💾 Writing {PART_A_OUTPUT}...")
        write_json(part_a_data, PART_A_OUTPUT)
        print(f"✓ JSON file created successfully")

    except FileNotFoundError:
        print(f"\n❌ ERROR: Could not find {PART_A_INPUT}")
        print(f"   Make sure the file exists in the stimuli/ directory")
        return False
    except ValueError as e:
        print(f"\n❌ VALIDATION ERROR:")
        print(f"   {e}")
        return False
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR:")
        print(f"   {e}")
        return False

    # Part B
    print(f"\n📖 Reading {PART_B_INPUT}...")
    try:
        part_b_text = read_file(PART_B_INPUT)
        print(f"✓ File read successfully ({len(part_b_text)} characters)")

        print(f"\n🔍 Parsing Part B (with source documents)...")
        part_b_data = parse_part_b(part_b_text)
        print(f"✓ Parsed {len(part_b_data)} items")

        print(f"\n💾 Writing {PART_B_OUTPUT}...")
        write_json(part_b_data, PART_B_OUTPUT)
        print(f"✓ JSON file created successfully")

    except FileNotFoundError:
        print(f"\n❌ ERROR: Could not find {PART_B_INPUT}")
        print(f"   Make sure the file exists in the stimuli/ directory")
        return False
    except ValueError as e:
        print(f"\n❌ VALIDATION ERROR:")
        print(f"   {e}")
        return False
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR:")
        print(f"   {e}")
        return False

    # Success!
    print("\n" + "=" * 70)
    print("✅ SUCCESS! Stimuli files built successfully")
    print("=" * 70)
    print(f"\nCreated files:")
    print(f"  - {PART_A_OUTPUT} ({len(part_a_data)} items)")
    print(f"  - {PART_B_OUTPUT} ({len(part_b_data)} items)")
    print(f"\nNext steps:")
    print(f"  1. Check the JSON files to verify they look correct")
    print(f"  2. If you want to edit scenarios, modify the .md files and rebuild")
    print(f"  3. To rebuild: python build_stimuli.py")
    print()

    return True


# ============================================================================
# ENTRY POINT - This runs when you execute the script
# ============================================================================

if __name__ == "__main__":
    """
    This block runs when you execute: python build_stimuli.py
    """
    success = build_stimuli()

    # Exit with appropriate code
    import sys
    sys.exit(0 if success else 1)
