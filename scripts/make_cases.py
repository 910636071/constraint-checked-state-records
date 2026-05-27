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


def _edge_trace(case_idx, trace_idx, tick, state_kind, weight, decay):
    return {
        "trace_id": f"edge_{case_idx:03d}_{trace_idx:02d}",
        "signal_kind": SIGNALS[trace_idx % len(SIGNALS)],
        "agent_x": f"agent_{chr(97 + trace_idx % 6)}",
        "agent_y": f"agent_{chr(97 + (trace_idx + 2) % 6)}",
        "tick": tick,
        "attrs": {
            "state_kind": state_kind,
            "origin_trace": f"edge_{case_idx:03d}_{trace_idx:02d}",
            "weight_band": weight,
            "decay_rate": decay,
        },
    }


def build_edge_cases():
    return [
        # E0: single trace, zero weight — score stays 0.0
        {
            "case_id": "edge_000",
            "allow_list": ["family_alpha", "family_beta"],
            "deny_list": ["family_delta"],
            "must_match": ["family_alpha"],
            "traces": [_edge_trace(0, 0, 1, "family_alpha", 0.0, 0.0)],
        },
        # E1: single trace, unit weight — score = exactly 1.0
        {
            "case_id": "edge_001",
            "allow_list": ["family_alpha", "family_beta"],
            "deny_list": ["family_delta"],
            "must_match": ["family_alpha"],
            "traces": [_edge_trace(1, 0, 1, "family_alpha", 1.0, 0.0)],
        },
        # E2: three traces same family, decay=0.0 — pure additive: 3 × 0.9 = 2.7
        {
            "case_id": "edge_002",
            "allow_list": ["family_alpha", "family_beta"],
            "deny_list": ["family_delta"],
            "must_match": ["family_alpha"],
            "traces": [_edge_trace(2, i, i + 1, "family_alpha", 0.9, 0.0) for i in range(3)],
        },
        # E3: decay=1.0 on second trace — first family fully zeroed
        {
            "case_id": "edge_003",
            "allow_list": ["family_alpha", "family_beta"],
            "deny_list": ["family_delta"],
            "must_match": ["family_beta"],
            "traces": [
                _edge_trace(3, 0, 1, "family_alpha", 0.9, 0.0),
                _edge_trace(3, 1, 3, "family_beta", 0.9, 1.0),
            ],
        },
        # E4: empty deny_list — nothing can be denied
        {
            "case_id": "edge_004",
            "allow_list": ["family_alpha", "family_beta"],
            "deny_list": [],
            "must_match": ["family_alpha"],
            "traces": [_edge_trace(4, 0, 1, "family_alpha", 0.7, 0.1)],
        },
        # E5: must_match with two items — either satisfies the constraint
        {
            "case_id": "edge_005",
            "allow_list": ["family_alpha", "family_beta"],
            "deny_list": ["family_delta"],
            "must_match": ["family_alpha", "family_beta"],
            "traces": [
                _edge_trace(5, 0, 1, "family_alpha", 0.9, 0.0),
                _edge_trace(5, 1, 3, "family_beta", 0.7, 0.0),
            ],
        },
        # E6: 15 traces — validates pipeline at larger trace count
        {
            "case_id": "edge_006",
            "allow_list": ["family_alpha", "family_gamma"],
            "deny_list": ["family_zeta"],
            "must_match": ["family_alpha"],
            "traces": [
                _edge_trace(6, i, i + 1, FAMILIES[i % len(FAMILIES)],
                            WEIGHTS[i % len(WEIGHTS)], DECAYS[(i + 1) % len(DECAYS)])
                for i in range(15)
            ],
        },
        # E7: all traces the same family — state converges to single scorer
        {
            "case_id": "edge_007",
            "allow_list": ["family_beta", "family_gamma"],
            "deny_list": ["family_alpha"],
            "must_match": ["family_beta"],
            "traces": [_edge_trace(7, i, i + 1, "family_beta", 0.7, 0.1) for i in range(5)],
        },
    ]


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
