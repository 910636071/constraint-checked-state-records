from baseline_suite import METHODS
from scripts.make_cases import build_cases
from scripts.run_pilot import run_pilot
from score_card import score_records


def test_pilot_record_count_and_metric_bounds():
    cases = build_cases(20)
    records = list(run_pilot(cases, METHODS, 10))
    assert len(records) == 600
    summary = score_records(records)
    assert summary["runs"] == 600
    assert 0.0 <= summary["avg_q"]
    assert 0.0 <= summary["pass_rate"] <= 1.0
