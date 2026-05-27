"""
Comparative evaluation for Paper 3 Section 5.2.

Runs four conditions across five scenarios and writes eval_results.csv.

Condition 4 (typed_llm_sim) uses Gaussian noise to simulate LLM
expression variance. A real LLM evaluation would replace the noise
model with actual API calls while keeping the typed state substrate
unchanged.
"""
import argparse
import csv
from pathlib import Path

from eval.conditions import (
    run_open_memory,
    run_template_only,
    run_typed_llm_sim,
    run_typed_templates,
)
from eval.metrics import compute_metrics
from eval.scenarios import SCENARIOS

FIELDNAMES = [
    "condition", "scenario", "runs",
    "avg_expr_score", "expr_variance", "fact_violation_rate",
    "avg_token_cost", "template_hit_rate", "replayability", "passed_rate",
]


def run_all(scenarios, seed, runs):
    rows = []
    for scenario in scenarios:
        name = scenario["name"]
        rows.append(compute_metrics(
            "open_memory",    name, run_open_memory(scenario, seed, runs)))
        rows.append(compute_metrics(
            "template_only",  name, run_template_only(scenario)))
        rows.append(compute_metrics(
            "typed_templates", name, run_typed_templates(scenario)))
        rows.append(compute_metrics(
            "typed_llm_sim",  name, run_typed_llm_sim(scenario, seed, runs)))
    return rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--runs", type=int, default=20)
    parser.add_argument("--out", default="outputs/eval_results.csv")
    args = parser.parse_args()

    rows = run_all(SCENARIOS, args.seed, args.runs)

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)
    print(f"wrote {len(rows)} rows to {out}")


if __name__ == "__main__":
    main()
