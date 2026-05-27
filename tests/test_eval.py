import pytest

from eval.conditions import (
    run_open_memory,
    run_template_only,
    run_typed_llm_sim,
    run_typed_templates,
)
from eval.metrics import compute_metrics
from eval.scenarios import SCENARIOS


def _scenario(name):
    return next(s for s in SCENARIOS if s["name"] == name)


# ---------------------------------------------------------------------------
# Structural checks
# ---------------------------------------------------------------------------

class TestConditionOutputShape:
    REQUIRED_KEYS = {
        "expr_score", "token_cost", "facts_recalled",
        "template_hit", "state_replayable", "passed",
    }

    def test_open_memory_keys(self):
        s = _scenario("library_routine")
        for r in run_open_memory(s, seed=0, runs=3):
            assert set(r.keys()) >= self.REQUIRED_KEYS

    def test_template_only_keys(self):
        s = _scenario("library_routine")
        for r in run_template_only(s):
            assert set(r.keys()) >= self.REQUIRED_KEYS

    def test_typed_templates_keys(self):
        s = _scenario("library_routine")
        for r in run_typed_templates(s):
            assert set(r.keys()) >= self.REQUIRED_KEYS

    def test_typed_llm_sim_keys(self):
        s = _scenario("library_routine")
        for r in run_typed_llm_sim(s, seed=0, runs=3):
            assert set(r.keys()) >= self.REQUIRED_KEYS

    def test_run_counts(self):
        s = _scenario("library_routine")
        assert len(run_open_memory(s, seed=0, runs=5)) == 5
        assert len(run_template_only(s)) == 1
        assert len(run_typed_templates(s)) == 1
        assert len(run_typed_llm_sim(s, seed=0, runs=5)) == 5


# ---------------------------------------------------------------------------
# Determinism
# ---------------------------------------------------------------------------

class TestDeterminism:
    def test_typed_templates_zero_variance(self):
        s = _scenario("mixed_concepts")
        r = run_typed_templates(s)[0]
        # Running again should produce identical result
        assert run_typed_templates(s)[0]["expr_score"] == r["expr_score"]

    def test_template_only_zero_variance(self):
        s = _scenario("gift_decay")
        assert run_template_only(s)[0]["expr_score"] == run_template_only(s)[0]["expr_score"]

    def test_open_memory_same_seed_same_result(self):
        s = _scenario("library_routine")
        r1 = [r["expr_score"] for r in run_open_memory(s, seed=7, runs=5)]
        r2 = [r["expr_score"] for r in run_open_memory(s, seed=7, runs=5)]
        assert r1 == r2

    def test_open_memory_different_seeds_different_results(self):
        s = _scenario("library_routine")
        scores_a = [r["expr_score"] for r in run_open_memory(s, seed=1, runs=10)]
        scores_b = [r["expr_score"] for r in run_open_memory(s, seed=99, runs=10)]
        assert scores_a != scores_b


# ---------------------------------------------------------------------------
# Typed state: perfect fact recall and replayability
# ---------------------------------------------------------------------------

class TestTypedStateProperties:
    def test_typed_templates_all_facts_recalled(self):
        for scenario in SCENARIOS:
            result = run_typed_templates(scenario)[0]
            for fact, recalled in result["facts_recalled"].items():
                assert recalled, (
                    f"typed_templates failed to recall '{fact}' in {scenario['name']}"
                )

    def test_typed_templates_replayable(self):
        for scenario in SCENARIOS:
            assert run_typed_templates(scenario)[0]["state_replayable"] is True

    def test_typed_llm_sim_facts_same_as_typed_templates(self):
        for scenario in SCENARIOS:
            base_facts = run_typed_templates(scenario)[0]["facts_recalled"]
            for r in run_typed_llm_sim(scenario, seed=0, runs=5):
                assert r["facts_recalled"] == base_facts

    def test_typed_llm_sim_has_nonzero_variance(self):
        s = _scenario("library_routine")
        scores = [r["expr_score"] for r in run_typed_llm_sim(s, seed=0, runs=20)]
        variance = sum((x - sum(scores) / len(scores)) ** 2 for x in scores) / len(scores)
        assert variance > 0


# ---------------------------------------------------------------------------
# open_memory: high-variance, non-replayable
# ---------------------------------------------------------------------------

class TestOpenMemoryProperties:
    def test_not_replayable(self):
        for scenario in SCENARIOS:
            for r in run_open_memory(scenario, seed=0, runs=3):
                assert r["state_replayable"] is False

    def test_no_template_hit(self):
        for scenario in SCENARIOS:
            for r in run_open_memory(scenario, seed=0, runs=3):
                assert r["template_hit"] is False

    def test_variance_exceeds_typed_templates(self):
        s = _scenario("long_session")
        open_scores = [r["expr_score"] for r in run_open_memory(s, seed=0, runs=20)]
        mean = sum(open_scores) / len(open_scores)
        open_var = sum((x - mean) ** 2 for x in open_scores) / len(open_scores)
        assert open_var > 0, "open_memory should have nonzero variance"


# ---------------------------------------------------------------------------
# Token cost scaling
# ---------------------------------------------------------------------------

class TestTokenCostScaling:
    def test_long_session_open_memory_highest_cost(self):
        s = _scenario("long_session")
        open_cost = run_open_memory(s, seed=0, runs=1)[0]["token_cost"]
        typed_cost = run_typed_templates(s)[0]["token_cost"]
        assert open_cost > typed_cost

    def test_typed_llm_cost_bounded_across_sessions(self):
        short_cost = run_typed_llm_sim(_scenario("library_routine"), seed=0, runs=1)[0]["token_cost"]
        long_cost = run_typed_llm_sim(_scenario("long_session"), seed=0, runs=1)[0]["token_cost"]
        # Typed state is bounded: long session should not blow up
        assert long_cost < 200


# ---------------------------------------------------------------------------
# Metrics aggregation
# ---------------------------------------------------------------------------

class TestMetrics:
    def test_metric_keys(self):
        s = _scenario("library_routine")
        row = compute_metrics("typed_templates", s["name"], run_typed_templates(s))
        expected_keys = {
            "condition", "scenario", "runs", "avg_expr_score",
            "expr_variance", "fact_violation_rate", "avg_token_cost",
            "template_hit_rate", "replayability", "passed_rate",
        }
        assert set(row.keys()) == expected_keys

    def test_typed_templates_zero_violation_zero_variance(self):
        for scenario in SCENARIOS:
            row = compute_metrics(
                "typed_templates", scenario["name"], run_typed_templates(scenario)
            )
            assert row["fact_violation_rate"] == 0.0
            assert row["expr_variance"] == 0.0
            assert row["replayability"] == 1.0

    def test_open_memory_nonzero_variance_library(self):
        s = _scenario("library_routine")
        row = compute_metrics("open_memory", s["name"], run_open_memory(s, seed=0, runs=20))
        assert row["expr_variance"] > 0

    def test_pass_rate_bounds(self):
        for scenario in SCENARIOS:
            for cond, results in [
                ("open_memory",    run_open_memory(scenario, seed=0, runs=5)),
                ("template_only",  run_template_only(scenario)),
                ("typed_templates", run_typed_templates(scenario)),
                ("typed_llm_sim",  run_typed_llm_sim(scenario, seed=0, runs=5)),
            ]:
                row = compute_metrics(cond, scenario["name"], results)
                assert 0.0 <= row["passed_rate"] <= 1.0
