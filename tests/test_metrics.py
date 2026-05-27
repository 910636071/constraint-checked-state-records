import pytest

from baseline_suite import METHODS
from scripts.make_cases import build_cases, build_edge_cases
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
    assert summary["var_q"] == pytest.approx(0.257140)
    assert summary["pass_rate"] == pytest.approx(0.21)
    assert summary["avg_record_count"] == pytest.approx(6.85)


def test_var_q_bounded_by_M_squared_over_4():
    M_UPPER = 18.0
    cases = build_cases(20, seed=37)
    records = list(run_pilot(cases, METHODS, 10))
    summary = score_records(records)
    assert summary["var_q"] < M_UPPER ** 2 / 4


def test_convergence_var_mu_hat_decreases():
    cases = build_cases(20, seed=37)
    run_levels = (5, 20, 100)
    var_mu_hats = []
    for runs in run_levels:
        records = list(run_pilot(cases, METHODS, runs))
        summary = score_records(records)
        m = summary["runs"]
        var_mu_hats.append(summary["var_q"] / m)
    assert var_mu_hats[0] > var_mu_hats[1] > var_mu_hats[2]


def test_edge_case_pilot_metric_bounds():
    cases = build_edge_cases()
    records = list(run_pilot(cases, METHODS, 5))
    assert len(records) == len(cases) * len(METHODS) * 5
    summary = score_records(records)
    assert 0.0 <= summary["avg_q"]
    assert 0.0 <= summary["pass_rate"] <= 1.0


def test_edge_case_pilot_nonzero_pass_rate():
    cases = build_edge_cases()
    records = list(run_pilot(cases, METHODS, 10))
    summary = score_records(records)
    assert summary["pass_rate"] > 0.0
