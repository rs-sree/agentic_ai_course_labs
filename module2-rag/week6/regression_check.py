"""Catch a regression before it ships: compare a fresh eval run against a
saved baseline, and fail loudly if retrieval or faithfulness got worse.

This is the same discipline as a test suite in ordinary software - except
what's being tested isn't "does the function return the right type," it's
"does the system still answer as well as it did yesterday."

Run it:  python regression_check.py --save-baseline   (first time, or after an accepted change)
         python regression_check.py                   (every time after, to check for a regression)
"""
import json
import sys

BASELINE_FILE = "eval_baseline.json"
RESULTS_FILE = "eval_results.json"
REGRESSION_TOLERANCE = 0.01  # a drop this small or less is noise, not a regression


def main():
    if "--save-baseline" in sys.argv:
        results = json.load(open(RESULTS_FILE))
        json.dump(results, open(BASELINE_FILE, "w"), indent=2)
        print(f"Saved current eval_results.json as the new baseline ({BASELINE_FILE}).")
        print(f"  hit_rate={results['hit_rate']:.2f}  mrr={results['mrr']:.2f}  "
              f"faithfulness={results['faithfulness']:.2f}")
        return

    try:
        baseline = json.load(open(BASELINE_FILE))
    except FileNotFoundError:
        print(f"No baseline yet. Run `python run_eval.py` then "
              f"`python regression_check.py --save-baseline` first.")
        sys.exit(1)

    current = json.load(open(RESULTS_FILE))

    print(f"{'Metric':<15} {'Baseline':<10} {'Current':<10} {'Change':<10}")
    regressed = False
    for metric in ("hit_rate", "mrr", "faithfulness"):
        base_val = baseline[metric]
        cur_val = current[metric]
        delta = cur_val - base_val
        flag = ""
        if delta < -REGRESSION_TOLERANCE:
            flag = "  <-- REGRESSION"
            regressed = True
        print(f"{metric:<15} {base_val:<10.2f} {cur_val:<10.2f} {delta:+.2f}{flag}")

    if regressed:
        print("\nREGRESSION DETECTED. Do not ship this change until it's understood and fixed.")
        sys.exit(1)
    else:
        print("\nNo regression. Safe to treat this change as an improvement or a neutral change.")


if __name__ == "__main__":
    main()
