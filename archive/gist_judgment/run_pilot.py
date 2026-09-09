"""
Pilot Evaluation Runner

PURPOSE:
Runs a cost-effective pilot of the gist-truth evaluation with a single model
and saves structured results for analysis.

USAGE:
    python run_pilot.py --items 20 --runs 2

This will run the first 20 items (Part A) with 2 repetitions.
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Add src to path so we can import our modules
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))  # shared OpenRouter client at the repo root
sys.path.insert(0, str(Path(__file__).parent / "src"))  # this study's own modules

from models import call_model, get_model_info
from prompts import load_part_a_data, generate_judgment_prompt, parse_json_response


def create_output_dir(run_id):
    """Create output directory for this pilot run."""
    output_dir = Path("results") / run_id
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def save_json(data, filepath):
    """Save data as pretty-printed JSON."""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"✓ Saved: {filepath}")


def run_pilot(model_key="claude-sonnet", num_items=20, run_id=None):
    """
    Run pilot evaluation.

    Args:
        model_key: Which model to use (default: claude-sonnet)
        num_items: How many items to run (default: 20 = all Part A)
        run_id: Identifier for this run (default: auto-generated timestamp)
    """

    # Generate run_id if not provided
    if run_id is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        run_id = f"pilot_{timestamp}"

    print("=" * 70)
    print("PILOT EVALUATION RUN")
    print("=" * 70)
    print(f"Run ID: {run_id}")
    print(f"Model: {get_model_info(model_key)['name']}")
    print(f"Items to run: {num_items}")
    print()

    # Load data
    print("Loading stimuli...")
    part_a_items = load_part_a_data()

    if not part_a_items:
        print("ERROR: Could not load Part A data. Run 'python build_stimuli.py' first.")
        return

    # Take only the requested number of items
    items_to_run = part_a_items[:num_items]
    print(f"✓ Loaded {len(items_to_run)} items")
    print()

    # Create output directory
    output_dir = create_output_dir(run_id)
    print(f"Results will be saved to: {output_dir}")
    print()

    # Run evaluation
    results = []
    estimated_cost = 0

    print("Running evaluation...")
    print("-" * 70)

    for idx, item in enumerate(items_to_run, 1):
        item_id = item['id']
        topic = item['topic']
        cell_type = item['cell_type']

        print(f"\n[{idx}/{len(items_to_run)}] {item_id}")
        print(f"  Topic: {topic}")
        print(f"  Cell type: {cell_type}")

        # Generate prompt
        prompt = generate_judgment_prompt(item)

        # Call model
        print(f"  Calling {model_key}...", end=" ")
        api_result = call_model(prompt, model_key, temperature=0.7, max_tokens=1500)

        if api_result['success']:
            print("✓")

            # Try to parse JSON response
            parsed = parse_json_response(api_result['response'])

            # Estimate cost (rough approximation)
            # Input: ~400 tokens @ $3/M, Output: ~250 tokens @ $15/M
            estimated_cost += (400 * 0.000003 + 250 * 0.000015)

        else:
            print(f"✗ Error: {api_result['error']}")
            parsed = None

        # Save result
        result = {
            "item_id": item_id,
            "topic": topic,
            "cell_type": cell_type,
            "verbatim_truth": item['verbatim_truth'],
            "gist_truth": item['gist_truth'],
            "prompt": prompt,
            "raw_response": api_result['response'],
            "parsed_response": parsed,
            "timestamp": api_result['timestamp'],
            "success": api_result['success'],
            "error": api_result.get('error')
        }

        results.append(result)

    print()
    print("-" * 70)
    print(f"Completed {len(results)} items")
    print(f"Estimated cost: ${estimated_cost:.4f}")
    print()

    # Save results
    results_file = output_dir / "results.json"
    save_json(results, results_file)

    # Save metadata
    metadata = {
        "run_id": run_id,
        "timestamp": datetime.now().isoformat(),
        "model": model_key,
        "model_full_name": get_model_info(model_key)['name'],
        "num_items": len(results),
        "successful_calls": sum(1 for r in results if r['success']),
        "failed_calls": sum(1 for r in results if not r['success']),
        "estimated_cost_usd": round(estimated_cost, 4)
    }

    metadata_file = output_dir / "metadata.json"
    save_json(metadata, metadata_file)

    # Save summary
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Run ID: {run_id}")
    print(f"Total items: {metadata['num_items']}")
    print(f"Successful: {metadata['successful_calls']}")
    print(f"Failed: {metadata['failed_calls']}")
    print(f"Estimated cost: ${metadata['estimated_cost_usd']:.4f}")
    print(f"\nResults saved to: {output_dir}")
    print()

    # Show quick preview of parsed responses
    parsed_count = sum(1 for r in results if r['parsed_response'] is not None)
    print(f"Successfully parsed JSON: {parsed_count}/{len(results)}")

    if parsed_count > 0:
        print("\nSample parsed response:")
        sample = next((r for r in results if r['parsed_response'] is not None), None)
        if sample:
            print(json.dumps(sample['parsed_response'], indent=2))

    print()
    print("=" * 70)
    print("Next steps:")
    print("  1. Review results in:", results_file)
    print("  2. Run another pilot with: python run_pilot.py --run-id pilot_run2")
    print("  3. Compare results across runs to assess variance")
    print("=" * 70)
    print()

    return results


if __name__ == "__main__":
    import argparse

    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Run pilot evaluation")
    parser.add_argument(
        "--model",
        default="claude-sonnet",
        help="Model to use (default: claude-sonnet)"
    )
    parser.add_argument(
        "--items",
        type=int,
        default=20,
        help="Number of items to run (default: 20 = all Part A)"
    )
    parser.add_argument(
        "--run-id",
        default=None,
        help="Run identifier (default: auto-generated timestamp)"
    )

    args = parser.parse_args()

    # Run pilot
    run_pilot(
        model_key=args.model,
        num_items=args.items,
        run_id=args.run_id
    )
