from constraint_check import check_plan
from plan_builder import build_plan
from state_builder import build_state, empty_state
from text_driver import normalize_plan
from trace_store import build_trace_store, iter_records


METHODS = ("summary_loop", "template_grid", "symbolic_rule")


def run_method(case, method, run_idx):
    if method not in METHODS:
        raise ValueError(f"unknown method: {method}")
    state = empty_state()
    for record in iter_records(build_trace_store(case)):
        state = build_state(state, record)
    plan = normalize_plan(build_plan(state, case, method, run_idx))
    return check_plan(plan, case)
