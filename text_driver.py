def normalize_plan(plan):
    return {
        "case_id": plan["case_id"],
        "method": plan["method"],
        "run_idx": plan["run_idx"],
        "state_kind": plan["state_kind"],
        "origin_trace": plan["origin_trace"],
        "score": plan["score"],
        "record_count": plan["record_count"],
    }
