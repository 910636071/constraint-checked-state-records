import argparse
import json
import random
from pathlib import Path


FAMILIES = [
    "family_alpha",
    "family_beta",
    "family_gamma",
    "family_delta",
    "family_epsilon",
    "family_zeta",
]

SIGNALS = [
    "signal_a",
    "signal_b",
    "signal_c",
    "signal_d",
    "signal_e",
    "signal_f",
]

WEIGHTS = [0.5, 0.7, 0.9]
DECAYS = [0.20, 0.10, 0.05]


def build_cases(count=20, seed=37):
    rng = random.Random(seed)
    cases = []
    for case_idx in range(count):
        trace_total = rng.randint(4, 8)
        primary = FAMILIES[case_idx % len(FAMILIES)]
        secondary = FAMILIES[(case_idx + 2) % len(FAMILIES)]
        denied = FAMILIES[(case_idx + 4) % len(FAMILIES)]
        tick = rng.randint(0, 3)
        traces = []
        for trace_idx in range(trace_total):
            tick += rng.randint(1, 5)
            state_kind = FAMILIES[(case_idx + trace_idx + rng.randint(0, 2)) % len(FAMILIES)]
            signal_kind = SIGNALS[(trace_idx + rng.randint(0, 3)) % len(SIGNALS)]
            traces.append(
                {
                    "trace_id": f"trace_{case_idx:03d}_{trace_idx:02d}",
                    "signal_kind": signal_kind,
                    "agent_x": f"agent_{chr(97 + (case_idx + trace_idx) % 6)}",
                    "agent_y": f"agent_{chr(97 + (case_idx + trace_idx + 2) % 6)}",
                    "tick": tick,
                    "attrs": {
                        "state_kind": state_kind,
                        "origin_trace": f"trace_{case_idx:03d}_{trace_idx:02d}",
                        "weight_band": WEIGHTS[(case_idx + trace_idx) % len(WEIGHTS)],
                        "decay_rate": DECAYS[(case_idx + trace_idx + 1) % len(DECAYS)],
                    },
                }
            )
        cases.append(
            {
                "case_id": f"case_{case_idx:03d}",
                "allow_list": [primary, secondary],
                "deny_list": [denied],
                "must_match": [primary],
                "traces": traces,
            }
        )
    return cases


def write_jsonl(cases, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for case in cases:
            handle.write(json.dumps(case, sort_keys=True) + "\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="data/cases_small.jsonl")
    parser.add_argument("--count", type=int, default=20)
    args = parser.parse_args()
    write_jsonl(build_cases(args.count), Path(args.out))


if __name__ == "__main__":
    main()
