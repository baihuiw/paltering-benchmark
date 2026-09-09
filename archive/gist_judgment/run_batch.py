"""
Batch Pilot Runner - Run multiple repetitions sequentially

PURPOSE:
Runs multiple pilot evaluations in sequence to collect data for variance analysis.

USAGE:
    python run_batch.py --runs 10 --items 20

This will run 10 separate evaluations, each with 20 items.
Total API calls = runs × items
"""

import subprocess
import sys
from datetime import datetime


def run_batch_pilot(num_runs=10, items_per_run=20, model="claude-sonnet"):
    """
    Run multiple pilot evaluations in sequence.

    Args:
        num_runs: Number of separate runs to execute
        items_per_run: Number of items per run
        model: Which model to use
    """

    total_calls = num_runs * items_per_run
    estimated_cost = total_calls * 0.005  # ~$0.005 per call

    print("=" * 70)
    print("BATCH PILOT EVALUATION")
    print("=" * 70)
    print(f"Configuration:")
    print(f"  Runs: {num_runs}")
    print(f"  Items per run: {items_per_run}")
    print(f"  Model: {model}")
    print(f"  Total API calls: {total_calls}")
    print(f"  Estimated cost: ${estimated_cost:.2f}")
    print()

    response = input(f"Proceed with {num_runs} runs? (y/n): ")
    if response.lower() != 'y':
        print("Cancelled.")
        return

    print()
    print("=" * 70)
    print("STARTING BATCH RUNS")
    print("=" * 70)
    print()

    # Track successful and failed runs
    successful_runs = []
    failed_runs = []

    start_time = datetime.now()

    for run_num in range(1, num_runs + 1):
        run_id = f"pilot_run{run_num}"

        print(f"\n{'=' * 70}")
        print(f"RUN {run_num}/{num_runs}: {run_id}")
        print(f"{'=' * 70}\n")

        # Run the pilot script
        cmd = [
            "python",
            "run_pilot.py",
            "--model", model,
            "--items", str(items_per_run),
            "--run-id", run_id
        ]

        try:
            result = subprocess.run(
                cmd,
                check=True,
                capture_output=False,  # Show output in real-time
                text=True
            )
            successful_runs.append(run_id)
            print(f"\n✓ Completed: {run_id}")

        except subprocess.CalledProcessError as e:
            failed_runs.append(run_id)
            print(f"\n✗ Failed: {run_id}")
            print(f"Error: {e}")

            # Ask if we should continue
            response = input("\nContinue with remaining runs? (y/n): ")
            if response.lower() != 'y':
                print("Stopping batch run.")
                break

    end_time = datetime.now()
    duration = end_time - start_time

    # Final summary
    print()
    print("=" * 70)
    print("BATCH RUN COMPLETE")
    print("=" * 70)
    print(f"Total time: {duration}")
    print(f"Successful runs: {len(successful_runs)}/{num_runs}")
    if failed_runs:
        print(f"Failed runs: {len(failed_runs)}")
        print(f"  {', '.join(failed_runs)}")
    print()
    print(f"Successful runs:")
    for run_id in successful_runs:
        print(f"  - {run_id}")
    print()
    print(f"Total API calls made: ~{len(successful_runs) * items_per_run}")
    print(f"Estimated total cost: ${len(successful_runs) * items_per_run * 0.005:.2f}")
    print()
    print("Results saved in: results/")
    print()
    print("Next steps:")
    print("  1. Review individual runs: ls -la results/")
    print("  2. Analyze variance across runs")
    print("  3. Examine response patterns by cell_type")
    print("=" * 70)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run batch pilot evaluations")
    parser.add_argument(
        "--runs",
        type=int,
        default=10,
        help="Number of runs to execute (default: 10)"
    )
    parser.add_argument(
        "--items",
        type=int,
        default=20,
        help="Items per run (default: 20)"
    )
    parser.add_argument(
        "--model",
        default="claude-sonnet",
        help="Model to use (default: claude-sonnet)"
    )
    parser.add_argument(
        "--start-from",
        type=int,
        default=1,
        help="Start from run number (default: 1, use 2 if run1 already exists)"
    )

    args = parser.parse_args()

    # Adjust for start-from
    if args.start_from > 1:
        print(f"Starting from run {args.start_from}")
        # We'll need to modify the run numbering
        actual_runs = args.runs - (args.start_from - 1)
        if actual_runs <= 0:
            print(f"Error: --start-from {args.start_from} is >= --runs {args.runs}")
            sys.exit(1)

    run_batch_pilot(
        num_runs=args.runs,
        items_per_run=args.items,
        model=args.model
    )
