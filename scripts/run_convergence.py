"""
Synthetic convergence experiment for Paper 2 Section 8.

Demonstrates that Var(Y_i) stays bounded and that the i.i.d.-derived
estimate Var(mu_hat_m) = Var(Y_i) / m decreases with m, consistent with
the theoretical bound M_UPPER^2 / (4m).

Note: the artifact is fully deterministic (fixed seed, no stochastic
sampling), so Var(mu_hat_m) cannot be observed empirically across
independent draws. The table instead reports the i.i.d.-implied estimate
var_q / m alongside the theoretical upper bound.
"""
import argparse
import csv
from pathlib import Path

from baseline_suite import METHODS
from scripts.make_cases import build_cases
from scripts.run_pilot import run_pilot

M_UPPER = 18.0  # geometric series limit: max(weight_band) / min(decay_rate) = 0.9 / 0.05

RUN_LEVELS = (1, 2, 5, 10, 20, 50, 100, 200)


def convergence_rows(cases, methods, run_levels):
    for runs in run_levels:
        records = list(run_pilot(cases, methods, runs))
        m = len(records)
        avg_q = sum(r["score"] for r in records) / m
        var_q = sum((r["score"] - avg_q) ** 2 for r in records) / m
        yield {
            "runs": runs,
            "m": m,
            "avg_q": round(avg_q, 6),
            "var_q": round(var_q, 6),
            "var_mu_hat_iid": round(var_q / m, 8),
            "bound_M2_4m": round(M_UPPER ** 2 / (4 * m), 8),
        }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=37)
    parser.add_argument("--out", default="outputs/convergence.csv")
    args = parser.parse_args()

    cases = build_cases(20, seed=args.seed)
    rows = list(convergence_rows(cases, METHODS, RUN_LEVELS))

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = ["runs", "m", "avg_q", "var_q", "var_mu_hat_iid", "bound_M2_4m"]
    with out.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"wrote {len(rows)} rows to {out}")


if __name__ == "__main__":
    main()
