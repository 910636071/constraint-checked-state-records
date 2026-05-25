def empty_state():
    return {"scores": {}, "last_trace": None, "record_count": 0}


def build_state(state, record):
    attrs = record["attrs"]
    state_kind = attrs["state_kind"]
    weight = attrs["weight_band"]
    decay = attrs["decay_rate"]
    scores = {}
    for key, value in state["scores"].items():
        scores[key] = round(value * (1.0 - decay), 6)
    scores[state_kind] = round(scores.get(state_kind, 0.0) + weight, 6)
    return {
        "scores": scores,
        "last_trace": record["trace_id"],
        "record_count": state["record_count"] + 1,
    }
