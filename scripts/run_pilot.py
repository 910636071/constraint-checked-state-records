import argparse
import json
from pathlib import Path

from baseline_suite import METHODS, run_method
from case_bank import load_cases


def parse_methods(value):
    methods = tuple(item.strip() for item in value.split(",") if item.strip())
    unknown = sorted(set(methods).difference(METHODS))
    if unknown:
        raise ValueError(f"unknown methods: {unknown}")
    return methods


def run_pilot(cases, methods, runs):
    for run_idx in range(runs):
        for case in cases:
            for method in methods:
                yield run_method(case, method, run_idx)


def write_jsonl(records, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for record in records:
            handle.write(json.dumps(record, sort_keys=True) + "\n")
            count += 1
    return count


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--cases", required=True)
    parser.add_argument("--runs", type=int, required=True)
    parser.add_argument("--methods", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    cases = load_cases(args.cases)
    methods = parse_methods(args.methods)
    count = write_jsonl(run_pilot(cases, methods, args.runs), Path(args.out))
    print(f"records={count}")


if __name__ == "__main__":
    main()
