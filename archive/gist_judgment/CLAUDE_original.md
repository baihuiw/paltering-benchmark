# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an LLM evaluation project testing how language models judge and produce misinformation based on a 2×2 taxonomy of **verbatim truth** (literal details) and **gist truth** (general meaning). Based on "It's Not Literally True, But You Get the Gist" (Langdon et al., 2024).

## Development Environment

- **Python**: 3.9+
- **Package Manager**: uv (fast Python package manager)
- **Virtual Environment**: `.venv/` directory
- **API Access**: OpenRouter (provides multi-model access with single API key)
- **Environment**: API key stored in `.env` file as `OPENROUTER_API_KEY`

### Setup Commands

```bash
# Activate virtual environment
source .venv/bin/activate

# Install dependencies
~/.local/bin/uv pip install openai python-dotenv pandas

# Test API connection
python test_api.py
```

## Core Architecture

### Human-Readable Authoring Workflow

The project uses a **Markdown → JSON build pipeline** to separate human authoring from programmatic consumption:

1. **Edit**: Researchers edit scenarios in Markdown files (`stimuli/*.md`)
2. **Build**: Run `python build_stimuli.py` to parse and validate Markdown
3. **Output**: Auto-generated JSON files in `data/` directory
4. **Never edit JSON directly** - it's regenerated from Markdown

This design allows non-programmers to iterate on experimental stimuli without touching code.

### Key Directories

```
stimuli/          # Human-editable Markdown source files (version controlled)
├── part_a.md     # 2×2 taxonomy scenarios (judgment tasks)
└── part_b.md     # Behavioral production items

data/             # Auto-generated JSON (NOT version controlled, rebuild from source)
├── part_a.json   # Built from part_a.md
└── part_b.json   # Built from part_b.md

src/              # Source code modules
├── models.py     # OpenRouter API wrapper and model definitions
└── prompts.py    # Prompt templates and JSON parsing

build_stimuli.py  # Markdown → JSON converter with strict validation
test_api.py       # API connection test script
```

## Part A: Ethical Judgment Tasks

**Structure**: 5 scenarios × 4 cells = 20 items testing the 2×2 taxonomy

**Format in part_a.md**:
```markdown
## Scenario N: [Topic]
Background: [Objective facts]

### fully_true
User asks: [Multi-line realistic scenario]
Statement: [The claim being judged]
Context: [Explanation of truth status]

### palter
User asks: [Scenario]
Statement: [Claim]
Context: [Truth status]

### truthy_falsehood
...

### blatant_falsehood
...
```

**Four cell types**:
- `fully_true`: Verbatim TRUE, Gist TRUE (whole truth)
- `palter`: Verbatim TRUE, Gist FALSE (misleading with true facts)
- `truthy_falsehood`: Verbatim FALSE, Gist TRUE (false details, true meaning)
- `blatant_falsehood`: Verbatim FALSE, Gist FALSE (completely false)

**Prompts**: The `user_asks` field is converted directly to a prompt (with "unethical" replaced by "bad" for natural language). See `src/prompts.py:generate_judgment_prompt()`

## Part B: Behavioral Production Tasks

**Structure**: 5 items testing whether LLMs themselves produce misinformation

**Format in part_b.md**:
```markdown
## Item N: [Topic]

Source document: |
  [Multi-paragraph factual document]

Prompt: [Communication task that might elicit misinformation]

False detail: [Specific false claim to watch for]

True fact: [The actual truth]
```

## Building Stimuli

**Command**: `python build_stimuli.py`

**What it does**:
1. Reads `stimuli/part_a.md` and `stimuli/part_b.md`
2. Parses structured content using regex
3. Validates:
   - Part A: Exactly 5 scenarios, 4 cells each
   - Part A: Only allowed cell types
   - Part B: Exactly 5 items
   - All fields present and non-empty
   - Unique IDs
4. Converts to JSON with structured schema
5. Writes to `data/part_a.json` and `data/part_b.json`

**Validation**: Fails loudly with clear error messages pointing to specific lines if format is incorrect

**When to rebuild**: After any edits to Markdown files in `stimuli/`

## Model Management (src/models.py)

**Available Models** (via OpenRouter):
- `claude-sonnet`: Claude Sonnet 4.5 (anthropic/claude-sonnet-4.5)
- `gpt-4`: GPT-4 Turbo (openai/gpt-4-turbo)
- `gemini`: Gemini Pro 1.5 (google/gemini-pro-1.5)
- `llama`: Llama 3.1 70B (meta-llama/llama-3.1-70b-instruct)

**Key Functions**:
- `call_model(prompt, model_key, temperature=0.7, max_tokens=1500)`: Call single model
- `call_multiple_models(prompt, model_keys, **kwargs)`: Call multiple models in sequence
- `get_available_models()`: List all model keys
- `validate_model_key(model_key)`: Check if model exists

**Adding New Models**: Edit `MODELS` dictionary in `src/models.py` with model ID from https://openrouter.ai/models

**Rate Limiting**: Built-in 1-second delay between API calls to prevent rate limit errors

**Error Handling**: Returns structured result dict with `success` boolean and `error` message if failed

## Prompt Templates (src/prompts.py)

**Part A Functions**:
- `load_part_a_data()`: Load stimuli from `data/part_a.json`
- `generate_judgment_prompt(item)`: Convert Part A item to natural prompt (replaces "unethical" → "bad")
- `format_prompt_for_model(item)`: Alias for prompt generation

**Response Format Philosophy**:
Models receive natural conversational scenarios (e.g., "How bad would it be if I told my mom...") and respond in their natural conversational format. This is intentional:
- Reflects how models actually interact with users
- Provides richer, more realistic responses
- Captures nuanced reasoning that structured formats might miss

**Actual Response Format** (Part A):
Models respond with natural advice/analysis, e.g.:
```
"That statement would be **accurate and appropriate** to tell your mother. Here's why it works well:

**What's good about it:**
- It's factually correct (global temps have risen ~1.1°C since pre-industrial times)
- It's measured and calm in tone..."
```

**Note**: Claude-as-judge (Phase 5) extracts structured ratings from these natural responses

## Development Workflow

### Iterating on Scenarios

1. Edit `stimuli/part_a.md` or `stimuli/part_b.md` in any text editor
2. Run `python build_stimuli.py` to rebuild JSON
3. If validation errors occur, fix Markdown and rebuild
4. JSON files are automatically updated

### Testing Model Calls

```bash
# Test models.py
python src/models.py

# Test prompts.py
python src/prompts.py
```

### Common Development Pattern

The codebase is designed for Python beginners:
- Extensive comments explaining Python concepts
- Clear variable names
- Small, focused functions
- Modular design for reusability
- Test blocks in modules (run when executed directly)

## Important Notes

### API Key Management
- Never commit `.env` file (already in `.gitignore`)
- Replace "placeholder" with real OpenRouter API key
- Test connection with `python test_api.py`

### File Structure Philosophy
1. **Human-readable source files**: Edit Markdown, not JSON/Python dictionaries
2. **Validation first**: Fail loudly with clear errors, not silently with bad data
3. **Modular code**: Easy to swap models, prompts, conditions for future evals
4. **Single source of truth**: Markdown files are authoritative, JSON is derived

### Git Workflow
- `data/*.json` files are in `.gitignore` (auto-generated)
- Markdown stimuli files in `stimuli/` ARE version controlled
- Always rebuild JSON after pulling changes to Markdown files

## Current Status (from BUILD_PLAN.md)

The project follows a phased build plan:
- ✅ **Phase 0**: Setup complete
- ✅ **Phase 1**: Human-readable authoring workflow (COMPLETE)
- ✅ **Phase 2**: Model management system (COMPLETE)
- ✅ **Phase 3**: Prompt templates (COMPLETE - Part A only)
- ✅ **Phase 4**: Core evaluation engine (COMPLETE - pilot runner built and run)
- ⏳ **Phase 5**: LLM-as-judge grading (IN PROGRESS)
- ⏳ **Phase 6**: Variance analysis (run eval twice, compare)
- ⏳ **Phase 7**: Documentation & polish

## Collected Data

**Pilot Runs**: 10 complete runs with Claude Sonnet 4.5
- **Location**: `results/pilot_run1/` through `results/pilot_run10/`
- **Items per run**: 20 (all Part A scenarios × 4 cells)
- **Total responses**: 200
- **Format**: Natural conversational responses to ethical scenarios
- **Consolidated data**: `results/consolidated_pilot_data.json`

Each run contains:
- `results.json`: Full responses with prompts, raw responses, timestamps
- `metadata.json`: Run info, model used, success/failure counts, estimated cost

See `BUILD_PLAN.md` for detailed implementation instructions for each phase.

## Testing the Eval Pipeline

Once Phase 4+ are complete, the workflow will be:
1. `python build_stimuli.py` - Build stimuli from Markdown
2. `python scripts/run_full_eval.py --run-id run_1` - First run
3. `python scripts/run_full_eval.py --run-id run_2` - Second run
4. `python scripts/analyze_variance.py --run1 results/run_1 --run2 results/run_2` - Compare

## Research Context

**Theoretical Framework**: 2×2 taxonomy of verbatim truth × gist truth

**Research Questions**:
1. How do LLMs judge ethicality of each misinformation type?
2. Do LLMs produce different types of misinformation?
3. Are LLMs consistent across multiple trials?

**Paper**: Langdon, J. A., Helgason, B. A., Qiu, J., & Effron, D. A. (2024). "It's Not Literally True, But You Get the Gist:" How nuanced understandings of truth encourage people to condone and spread misinformation. *Current Opinion in Psychology*, 57, 101788.
