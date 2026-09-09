# Gist-Truth Misinformation Eval

An LLM evaluation project testing how large language models judge and produce misinformation based on a 2×2 taxonomy of **verbatim truth** (literal details) and **gist truth** (general meaning).

## Theoretical Framework

Based on gist-verbatim distinction, this eval explores how LLMs respond to three types of misinformation:

### The 2×2 Taxonomy

|                          | **Verbatim TRUE** | **Verbatim FALSE** |
|--------------------------|-------------------|---------------------|
| **Gist TRUE**            | Whole truth       | **Truthy Falsehood** |
| **Gist FALSE**           | **Palter**        | **Blatant Falsehood** |

1. **Blatant Falsehood**: False literal details + False general meaning
   - Example: "The COVID-19 vaccine has killed a quarter million Americans" (when you believe vaccines are safe)

2. **Palter**: True literal details + False general meaning
   - Example: "20,000 people died after receiving the COVID-19 vaccine" (true statistic, misleading implication)

3. **Truthy Falsehood**: False literal details + True general meaning
   - Example: "Not a single death has been linked to the COVID-19 vaccine" (literally false, but gist is that vaccines are generally safe)

## Research Questions

1. **Condoning lies**: Do LLMs condone these kinds of lies in user prompt scenarios? And if so, to what extent?
2. **Production**: Do LLMs themselves produce different types of misinformation under pressure conditions?

## Experimental Design

- ~20 carefully designed prompts testing each misinformation type
- Multiple model families tested via OpenRouter (Claude, GPT, Gemini)
- LLM-as-judge grading for response evaluation

## Technical Setup

- **Language**: Python 3.9+
- **API Access**: OpenRouter (multi-model access with single API key)
- **Key Libraries**: openai, python-dotenv, pandas
- **Environment Management**: uv (fast Python package manager)

## Getting Started

1. **Install dependencies** (if not already done):
   ```bash
   uv venv
   uv pip install openai python-dotenv pandas
   ```

2. **Add your API key**: Edit `.env` and replace `placeholder` with your OpenRouter API key

3. **Test the connection**:
   ```bash
   source .venv/bin/activate
   python test_api.py
   ```

## Project Structure

```
gist-eval/
├── .env                 # API keys (not tracked in git)
├── .gitignore          # Files to exclude from version control
├── test_api.py         # Connection test script
├── README.md           # This file
└── CurrentOp.pdf       # Theoretical foundation paper
```

## Future Development

This eval will be built incrementally with:
- Prompt generation scripts
- Multi-model evaluation loops
- LLM-as-judge grading system
- Results analysis and visualization
- Variance testing across runs

## References

Langdon, J. A., Helgason, B. A., Qiu, J., & Effron, D. A. (2024). "It's Not Literally True, But You Get the Gist:" How nuanced understandings of truth encourage people to condone and spread misinformation. *Current Opinion in Psychology*, 57, 101788.
