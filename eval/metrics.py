def compute_metrics(condition, scenario_name, results):
    n = len(results)
    scores = [r["expr_score"] for r in results]
    avg_score = sum(scores) / n
    expr_variance = sum((s - avg_score) ** 2 for s in scores) / n

    avg_token_cost = sum(r["token_cost"] for r in results) / n
    template_hit_rate = sum(1 for r in results if r["template_hit"]) / n
    replayability = sum(1 for r in results if r["state_replayable"]) / n
    passed_rate = sum(1 for r in results if r.get("passed", False)) / n

    all_facts = set()
    for r in results:
        all_facts.update(r["facts_recalled"])
    if all_facts:
        recalled = sum(
            1 for r in results for f in all_facts if r["facts_recalled"].get(f, False)
        )
        fact_recall = recalled / (n * len(all_facts))
    else:
        fact_recall = 1.0

    return {
        "condition": condition,
        "scenario": scenario_name,
        "runs": n,
        "avg_expr_score": round(avg_score, 4),
        "expr_variance": round(expr_variance, 6),
        "fact_violation_rate": round(1.0 - fact_recall, 4),
        "avg_token_cost": round(avg_token_cost, 1),
        "template_hit_rate": round(template_hit_rate, 4),
        "replayability": round(replayability, 4),
        "passed_rate": round(passed_rate, 4),
    }
