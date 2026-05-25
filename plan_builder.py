def build_plan(state, case, method, run_idx):
    ordered = sorted(state["scores"].items(), key=lambda item: (-item[1], item[0]))
    if not ordered:
        state_kind = case["allow_list"][0]
        score = 0.0
    elif method == "summary_loop":
        state_kind, score = ordered[0]
    elif method == "template_grid":
        state_kind, score = ordered[(state["record_count"] + run_idx) % len(ordered)]
    elif method == "symbolic_rule":
        allowed = [item for item in ordered if item[0] in case["allow_list"]]
        state_kind, score = allowed[0] if allowed else ordered[-1]
    else:
        raise ValueError(f"unknown method: {method}")
    return {
        "case_id": case["case_id"],
        "method": method,
        "run_idx": run_idx,
        "state_kind": state_kind,
        "origin_trace": state["last_trace"],
        "score": round(score, 6),
        "record_count": state["record_count"],
    }
