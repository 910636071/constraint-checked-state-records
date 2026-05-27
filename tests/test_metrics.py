import pytest

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


def test_pilot_exact_values_are_stable():
    cases = build_cases(20, seed=37)
    records = list(run_pilot(cases, METHODS, 10))
    summary = score_records(records)
    assert summary["avg_q"] == pytest.approx(1.034573)
    assert summary["pass_rate"] == pytest.approx(0.21)
    assert summary["avg_record_count"] == pytest.approx(6.85)
