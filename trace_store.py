def build_trace_store(case):
    return tuple(sorted(case["traces"], key=lambda trace: (trace["tick"], trace["trace_id"])))


def iter_records(trace_store):
    for trace in trace_store:
        yield trace
