import json
from pathlib import Path


REQUIRED_CASE_KEYS = {"case_id", "traces", "allow_list", "deny_list", "must_match"}
REQUIRED_TRACE_KEYS = {"trace_id", "signal_kind", "agent_x", "agent_y", "tick", "attrs"}


def load_cases(path):
    cases = []
    with Path(path).open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                case = json.loads(line)
                validate_case(case)
                cases.append(case)
    return cases


def validate_case(case):
    missing = REQUIRED_CASE_KEYS.difference(case)
    if missing:
        raise ValueError(f"case missing keys: {sorted(missing)}")
    if not case["traces"]:
        raise ValueError("case has no traces")
    for trace in case["traces"]:
        missing_trace = REQUIRED_TRACE_KEYS.difference(trace)
        if missing_trace:
            raise ValueError(f"trace missing keys: {sorted(missing_trace)}")
        attrs = trace["attrs"]
        for key in ("state_kind", "origin_trace", "weight_band", "decay_rate"):
            if key not in attrs:
                raise ValueError(f"trace attrs missing key: {key}")
