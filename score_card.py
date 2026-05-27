def score_records(records):
    records = list(records)
    if not records:
        return {"runs": 0, "avg_q": 0.0, "var_q": 0.0, "pass_rate": 0.0, "avg_record_count": 0.0}
    total = len(records)
    passed = sum(1 for record in records if record["passed"])
    avg_q = sum(record["score"] for record in records) / total
    var_q = sum((record["score"] - avg_q) ** 2 for record in records) / total
    avg_count = sum(record["record_count"] for record in records) / total
    return {
        "runs": total,
        "avg_q": round(avg_q, 6),
        "var_q": round(var_q, 6),
        "pass_rate": round(passed / total, 6),
        "avg_record_count": round(avg_count, 6),
    }
