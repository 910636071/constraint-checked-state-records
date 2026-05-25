def check_plan(plan, case):
    state_kind = plan["state_kind"]
    allow_hit = state_kind in case["allow_list"]
    deny_hit = state_kind in case["deny_list"]
    must_hit = state_kind in case["must_match"]
    passed = allow_hit and not deny_hit and must_hit
    return {
        "case_id": plan["case_id"],
        "method": plan["method"],
        "run_idx": plan["run_idx"],
        "state_kind": state_kind,
        "origin_trace": plan["origin_trace"],
        "record_count": plan["record_count"],
        "score": plan["score"],
        "allow_hit": allow_hit,
        "deny_hit": deny_hit,
        "must_hit": must_hit,
        "passed": passed,
    }
