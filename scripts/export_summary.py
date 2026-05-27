import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path

from score_card import score_records


def read_jsonl(path):
    with Path(path).open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                yield json.loads(line)


def export_summary(input_path, out_path):
    groups = defaultdict(list)
    for record in read_jsonl(input_path):
        groups[record["method"]].append(record)
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["method", "runs", "avg_q", "var_q", "pass_rate", "avg_record_count"],
        )
        writer.writeheader()
        for method in sorted(groups):
            row = {"method": method}
            row.update(score_records(groups[method]))
            writer.writerow(row)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    export_summary(args.input, args.out)


if __name__ == "__main__":
    main()
