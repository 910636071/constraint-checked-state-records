import json

import pytest

from baseline_suite import METHODS, run_method
from case_bank import load_cases, validate_case
from constraint_check import check_plan
from plan_builder import build_plan
from score_card import score_records
from scripts.export_summary import export_summary, read_jsonl
from scripts.term_scan import blocked_terms, scan
from state_builder import build_state, empty_state
from text_driver import normalize_plan
from trace_store import build_trace_store, iter_records


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

PLAN_KEYS = {
    "case_id",
    "method",
    "run_idx",
    "state_kind",
    "origin_trace",
    "score",
    "record_count",
}

CHECKED_KEYS = PLAN_KEYS | {"allow_hit", "deny_hit", "must_hit", "passed"}


def _minimal_plan(state_kind="family_alpha", score=1.0):
    return {
        "case_id": "case_000",
        "method": "summary_loop",
        "run_idx": 0,
        "state_kind": state_kind,
        "origin_trace": "trace_000_00",
        "score": score,
        "record_count": 3,
    }


def _minimal_case(allow=("family_alpha", "family_beta"), deny=("family_delta",), must=("family_alpha",)):
    return {
        "case_id": "case_000",
        "allow_list": list(allow),
        "deny_list": list(deny),
        "must_match": list(must),
        "traces": [_trace("trace_000_00", tick=1)],
    }


def _trace(trace_id, tick=1, state_kind="family_alpha", weight=0.9, decay=0.1):
    return {
        "trace_id": trace_id,
        "signal_kind": "signal_a",
        "agent_x": "agent_a",
        "agent_y": "agent_b",
        "tick": tick,
        "attrs": {
            "state_kind": state_kind,
            "origin_trace": trace_id,
            "weight_band": weight,
            "decay_rate": decay,
        },
    }


# ---------------------------------------------------------------------------
# constraint_check.check_plan
# ---------------------------------------------------------------------------


class TestCheckPlan:
    def test_all_pass_conditions(self):
        plan = _minimal_plan("family_alpha")
        case = _minimal_case()
        result = check_plan(plan, case)
        assert result["passed"] is True
        assert result["allow_hit"] is True
        assert result["deny_hit"] is False
        assert result["must_hit"] is True

    def test_output_keys(self):
        result = check_plan(_minimal_plan(), _minimal_case())
        assert set(result.keys()) == CHECKED_KEYS

    def test_deny_overrides_allow(self):
        # state_kind is in both allow_list and deny_list
        case = _minimal_case(allow=("family_alpha",), deny=("family_alpha",), must=("family_alpha",))
        result = check_plan(_minimal_plan("family_alpha"), case)
        assert result["deny_hit"] is True
        assert result["passed"] is False

    def test_missing_from_allow_fails(self):
        case = _minimal_case(allow=("family_beta",), deny=(), must=("family_alpha",))
        result = check_plan(_minimal_plan("family_alpha"), case)
        assert result["allow_hit"] is False
        assert result["passed"] is False

    def test_missing_from_must_match_fails(self):
        case = _minimal_case(allow=("family_alpha", "family_beta"), deny=(), must=("family_beta",))
        result = check_plan(_minimal_plan("family_alpha"), case)
        assert result["must_hit"] is False
        assert result["passed"] is False

    def test_passthrough_fields(self):
        plan = _minimal_plan("family_alpha", score=0.75)
        result = check_plan(plan, _minimal_case())
        assert result["case_id"] == "case_000"
        assert result["method"] == "summary_loop"
        assert result["run_idx"] == 0
        assert result["state_kind"] == "family_alpha"
        assert result["score"] == 0.75
        assert result["record_count"] == 3


# ---------------------------------------------------------------------------
# state_builder.empty_state / build_state
# ---------------------------------------------------------------------------


class TestStateBuilder:
    def test_empty_state_shape(self):
        s = empty_state()
        assert s == {"scores": {}, "last_trace": None, "record_count": 0}

    def test_build_state_first_record(self):
        s = build_state(empty_state(), _trace("t0", weight=0.9, decay=0.1))
        assert s["record_count"] == 1
        assert s["last_trace"] == "t0"
        assert s["scores"]["family_alpha"] == pytest.approx(0.9)

    def test_build_state_accumulates_same_kind(self):
        s = empty_state()
        s = build_state(s, _trace("t0", state_kind="family_alpha", weight=0.9, decay=0.0))
        s = build_state(s, _trace("t1", state_kind="family_alpha", weight=0.5, decay=0.0))
        assert s["scores"]["family_alpha"] == pytest.approx(1.4)
        assert s["record_count"] == 2

    def test_build_state_decay_applied(self):
        s = empty_state()
        s = build_state(s, _trace("t0", state_kind="family_alpha", weight=1.0, decay=0.0))
        # Second record: same kind, decay=0.5 → existing 1.0 * (1-0.5) = 0.5, then +0.9
        s = build_state(s, _trace("t1", state_kind="family_alpha", weight=0.9, decay=0.5))
        assert s["scores"]["family_alpha"] == pytest.approx(1.4)

    def test_build_state_decay_other_kinds(self):
        s = empty_state()
        s = build_state(s, _trace("t0", state_kind="family_alpha", weight=1.0, decay=0.0))
        # Different kind, decay=0.2 → family_alpha decays to 0.8
        s = build_state(s, _trace("t1", state_kind="family_beta", weight=0.7, decay=0.2))
        assert s["scores"]["family_alpha"] == pytest.approx(0.8)
        assert s["scores"]["family_beta"] == pytest.approx(0.7)

    def test_build_state_updates_last_trace(self):
        s = empty_state()
        s = build_state(s, _trace("t0"))
        s = build_state(s, _trace("t1"))
        assert s["last_trace"] == "t1"


# ---------------------------------------------------------------------------
# plan_builder.build_plan
# ---------------------------------------------------------------------------


class TestPlanBuilder:
    def _state_with_scores(self, scores, record_count=4):
        return {"scores": scores, "last_trace": "t_last", "record_count": record_count}

    def _case(self, allow=("family_alpha", "family_beta"), deny=("family_delta",), must=("family_alpha",)):
        return _minimal_case(allow=allow, deny=deny, must=must)

    def test_summary_loop_picks_highest(self):
        state = self._state_with_scores({"family_alpha": 2.0, "family_beta": 1.0})
        plan = build_plan(state, self._case(), "summary_loop", 0)
        assert plan["state_kind"] == "family_alpha"

    def test_template_grid_rotates(self):
        state = self._state_with_scores({"family_alpha": 2.0, "family_beta": 1.0}, record_count=1)
        plan_0 = build_plan(state, self._case(), "template_grid", 0)
        plan_1 = build_plan(state, self._case(), "template_grid", 1)
        # With record_count=1: idx=(1+run_idx)%2 → run_idx=0 → idx=1 (family_beta), run_idx=1 → idx=0 (family_alpha)
        assert plan_0["state_kind"] != plan_1["state_kind"]

    def test_symbolic_rule_picks_allowed(self):
        state = self._state_with_scores(
            {"family_delta": 5.0, "family_alpha": 1.0, "family_beta": 0.5}
        )
        case = self._case(allow=("family_alpha", "family_beta"), deny=("family_delta",))
        plan = build_plan(state, case, "symbolic_rule", 0)
        # family_delta has highest score but is not in allow_list; should pick family_alpha
        assert plan["state_kind"] == "family_alpha"

    def test_empty_state_returns_allow_list_first(self):
        state = {"scores": {}, "last_trace": None, "record_count": 0}
        case = self._case(allow=("family_gamma", "family_alpha"))
        plan = build_plan(state, case, "summary_loop", 0)
        assert plan["state_kind"] == "family_gamma"
        assert plan["score"] == 0.0

    def test_unknown_method_raises(self):
        state = self._state_with_scores({"family_alpha": 1.0})
        with pytest.raises(ValueError, match="unknown method"):
            build_plan(state, self._case(), "bad_method", 0)

    def test_output_keys(self):
        state = self._state_with_scores({"family_alpha": 1.0})
        plan = build_plan(state, self._case(), "summary_loop", 2)
        assert set(plan.keys()) == PLAN_KEYS

    def test_passthrough_metadata(self):
        state = self._state_with_scores({"family_alpha": 1.0}, record_count=7)
        plan = build_plan(state, self._case(), "summary_loop", 3)
        assert plan["case_id"] == "case_000"
        assert plan["method"] == "summary_loop"
        assert plan["run_idx"] == 3
        assert plan["record_count"] == 7
        assert plan["origin_trace"] == "t_last"


# ---------------------------------------------------------------------------
# trace_store.build_trace_store / iter_records
# ---------------------------------------------------------------------------


class TestTraceStore:
    def test_sorted_by_tick_then_trace_id(self):
        case = {
            "traces": [
                _trace("trace_b", tick=5),
                _trace("trace_a", tick=5),
                _trace("trace_c", tick=2),
            ]
        }
        store = build_trace_store(case)
        ids = [t["trace_id"] for t in store]
        assert ids == ["trace_c", "trace_a", "trace_b"]

    def test_iter_records_yields_all(self):
        case = {"traces": [_trace(f"t{i}", tick=i) for i in range(5)]}
        store = build_trace_store(case)
        records = list(iter_records(store))
        assert len(records) == 5

    def test_iter_records_preserves_order(self):
        case = {"traces": [_trace(f"t{i}", tick=i) for i in range(3)]}
        store = build_trace_store(case)
        records = list(iter_records(store))
        assert [r["trace_id"] for r in records] == ["t0", "t1", "t2"]

    def test_single_trace(self):
        case = {"traces": [_trace("only", tick=10)]}
        store = build_trace_store(case)
        assert len(list(iter_records(store))) == 1


# ---------------------------------------------------------------------------
# text_driver.normalize_plan
# ---------------------------------------------------------------------------


class TestNormalizePlan:
    def test_exact_keys(self):
        result = normalize_plan(_minimal_plan())
        assert set(result.keys()) == PLAN_KEYS

    def test_strips_extra_keys(self):
        plan = dict(_minimal_plan(), extra_field="should_be_gone")
        result = normalize_plan(plan)
        assert "extra_field" not in result

    def test_preserves_values(self):
        plan = _minimal_plan("family_beta", score=0.42)
        result = normalize_plan(plan)
        assert result["state_kind"] == "family_beta"
        assert result["score"] == 0.42
        assert result["record_count"] == 3


# ---------------------------------------------------------------------------
# score_card.score_records
# ---------------------------------------------------------------------------


class TestScoreCard:
    def _record(self, passed=True, score=1.0, record_count=4):
        return {"passed": passed, "score": score, "record_count": record_count}

    def test_empty_input(self):
        result = score_records([])
        assert result == {"runs": 0, "avg_q": 0.0, "var_q": 0.0, "pass_rate": 0.0, "avg_record_count": 0.0}

    def test_all_pass(self):
        records = [self._record(passed=True, score=1.0)] * 10
        result = score_records(records)
        assert result["runs"] == 10
        assert result["pass_rate"] == 1.0

    def test_none_pass(self):
        records = [self._record(passed=False, score=0.5)] * 5
        result = score_records(records)
        assert result["pass_rate"] == 0.0

    def test_avg_q_correct(self):
        records = [self._record(score=0.5), self._record(score=1.5)]
        result = score_records(records)
        assert result["avg_q"] == pytest.approx(1.0)

    def test_var_q_correct(self):
        records = [self._record(score=0.0), self._record(score=2.0)]
        result = score_records(records)
        # population variance: mean=1.0, deviations=[-1,+1], var=1.0
        assert result["var_q"] == pytest.approx(1.0)

    def test_var_q_zero_for_uniform_scores(self):
        records = [self._record(score=1.5)] * 5
        result = score_records(records)
        assert result["var_q"] == pytest.approx(0.0)

    def test_var_q_bounded_by_M2_over_4(self):
        M_UPPER = 18.0
        records = [self._record(score=0.5), self._record(score=1.5)]
        result = score_records(records)
        assert result["var_q"] <= M_UPPER ** 2 / 4

    def test_avg_record_count_correct(self):
        records = [self._record(record_count=2), self._record(record_count=6)]
        result = score_records(records)
        assert result["avg_record_count"] == pytest.approx(4.0)

    def test_partial_pass_rate(self):
        records = [self._record(passed=True)] * 3 + [self._record(passed=False)] * 1
        result = score_records(records)
        assert result["pass_rate"] == pytest.approx(0.75)

    def test_generator_input(self):
        def gen():
            yield self._record(passed=True, score=1.0)
            yield self._record(passed=False, score=0.0)

        result = score_records(gen())
        assert result["runs"] == 2
        assert result["pass_rate"] == pytest.approx(0.5)


# ---------------------------------------------------------------------------
# baseline_suite.run_method
# ---------------------------------------------------------------------------


class TestRunMethod:
    def _case(self):
        from scripts.make_cases import build_cases
        return build_cases(1, seed=42)[0]

    def test_all_methods_return_checked_record(self):
        case = self._case()
        for method in METHODS:
            result = run_method(case, method, 0)
            assert set(result.keys()) == CHECKED_KEYS

    def test_unknown_method_raises(self):
        with pytest.raises(ValueError, match="unknown method"):
            run_method(self._case(), "nonexistent", 0)

    def test_run_idx_reflected(self):
        case = self._case()
        result = run_method(case, "summary_loop", 7)
        assert result["run_idx"] == 7

    def test_case_id_reflected(self):
        case = self._case()
        result = run_method(case, "summary_loop", 0)
        assert result["case_id"] == case["case_id"]

    def test_passed_is_bool(self):
        case = self._case()
        for method in METHODS:
            result = run_method(case, method, 0)
            assert isinstance(result["passed"], bool)

    def test_score_non_negative(self):
        case = self._case()
        for method in METHODS:
            result = run_method(case, method, 0)
            assert result["score"] >= 0.0


# ---------------------------------------------------------------------------
# case_bank.validate_case — error paths
# ---------------------------------------------------------------------------


class TestValidateCase:
    def _valid(self):
        return {
            "case_id": "case_000",
            "allow_list": ["family_alpha"],
            "deny_list": [],
            "must_match": ["family_alpha"],
            "traces": [
                {
                    "trace_id": "t0",
                    "signal_kind": "signal_a",
                    "agent_x": "agent_a",
                    "agent_y": "agent_b",
                    "tick": 1,
                    "attrs": {
                        "state_kind": "family_alpha",
                        "origin_trace": "t0",
                        "weight_band": 0.9,
                        "decay_rate": 0.1,
                    },
                }
            ],
        }

    def test_valid_case_passes(self):
        validate_case(self._valid())  # must not raise

    def test_missing_case_key_raises(self):
        case = self._valid()
        del case["allow_list"]
        with pytest.raises(ValueError, match="case missing keys"):
            validate_case(case)

    def test_empty_traces_raises(self):
        case = self._valid()
        case["traces"] = []
        with pytest.raises(ValueError, match="no traces"):
            validate_case(case)

    def test_missing_trace_key_raises(self):
        case = self._valid()
        del case["traces"][0]["signal_kind"]
        with pytest.raises(ValueError, match="trace missing keys"):
            validate_case(case)

    def test_missing_attrs_key_raises(self):
        case = self._valid()
        del case["traces"][0]["attrs"]["weight_band"]
        with pytest.raises(ValueError, match="trace attrs missing key"):
            validate_case(case)

    def test_load_cases_roundtrip(self, tmp_path):
        path = tmp_path / "cases.jsonl"
        path.write_text(json.dumps(self._valid()) + "\n", encoding="utf-8")
        cases = load_cases(path)
        assert len(cases) == 1
        assert cases[0]["case_id"] == "case_000"


# ---------------------------------------------------------------------------
# plan_builder — symbolic_rule empty-allowed fallback
# ---------------------------------------------------------------------------


class TestPlanBuilderFallback:
    def test_symbolic_rule_falls_back_to_lowest_when_none_allowed(self):
        state = {
            "scores": {"family_delta": 5.0, "family_epsilon": 3.0, "family_zeta": 1.0},
            "last_trace": "t0",
            "record_count": 3,
        }
        # allow_list contains none of the scored kinds
        case = _minimal_case(allow=("family_alpha",), deny=(), must=("family_alpha",))
        plan = build_plan(state, case, "symbolic_rule", 0)
        # ordered[-1] is the lowest-scoring item
        assert plan["state_kind"] == "family_zeta"
        assert plan["score"] == pytest.approx(1.0)


# ---------------------------------------------------------------------------
# scripts.export_summary
# ---------------------------------------------------------------------------


class TestExportSummary:
    def _records(self):
        return [
            {"method": "summary_loop", "passed": True, "score": 1.0, "record_count": 5},
            {"method": "summary_loop", "passed": False, "score": 0.5, "record_count": 5},
            {"method": "template_grid", "passed": True, "score": 2.0, "record_count": 6},
        ]

    def test_read_jsonl_yields_all(self, tmp_path):
        path = tmp_path / "data.jsonl"
        path.write_text(
            "\n".join(json.dumps(r) for r in self._records()) + "\n",
            encoding="utf-8",
        )
        result = list(read_jsonl(path))
        assert len(result) == 3

    def test_read_jsonl_skips_blank_lines(self, tmp_path):
        path = tmp_path / "data.jsonl"
        path.write_text(
            json.dumps(self._records()[0]) + "\n\n" + json.dumps(self._records()[1]) + "\n",
            encoding="utf-8",
        )
        assert len(list(read_jsonl(path))) == 2

    def test_export_summary_writes_csv_per_method(self, tmp_path):
        in_path = tmp_path / "runs.jsonl"
        in_path.write_text(
            "\n".join(json.dumps(r) for r in self._records()) + "\n",
            encoding="utf-8",
        )
        out_path = tmp_path / "summary.csv"
        export_summary(in_path, out_path)
        import csv
        rows = list(csv.DictReader(out_path.open(encoding="utf-8")))
        methods = {row["method"] for row in rows}
        assert methods == {"summary_loop", "template_grid"}

    def test_export_summary_pass_rate_correct(self, tmp_path):
        in_path = tmp_path / "runs.jsonl"
        in_path.write_text(
            "\n".join(json.dumps(r) for r in self._records()) + "\n",
            encoding="utf-8",
        )
        out_path = tmp_path / "summary.csv"
        export_summary(in_path, out_path)
        import csv
        rows = {row["method"]: row for row in csv.DictReader(out_path.open(encoding="utf-8"))}
        assert float(rows["summary_loop"]["pass_rate"]) == pytest.approx(0.5)
        assert float(rows["template_grid"]["pass_rate"]) == pytest.approx(1.0)


# ---------------------------------------------------------------------------
# scripts.term_scan — internal logic
# ---------------------------------------------------------------------------


class TestTermScan:
    def test_blocked_terms_non_empty(self):
        terms = blocked_terms()
        assert len(terms) > 0
        assert all(isinstance(t, str) for t in terms)

    def test_scan_returns_empty_on_clean_repo(self):
        assert scan() == []

    def test_paper2_allowed_terms_are_subset_of_blocked(self):
        # Each exempted term must be a real blocked term — exemptions must cover genuine hits
        from scripts.term_scan import PAPER2_ALLOWED_TERMS
        assert PAPER2_ALLOWED_TERMS.issubset(set(blocked_terms()))
