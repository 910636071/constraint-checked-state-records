"""
Four evaluation conditions for the Paper 3 comparative protocol.

Conditions 1 and 4 involve a stochastic element; conditions 2 and 3 are
deterministic. Condition 4 (typed_llm_sim) simulates LLM expression
variance with Gaussian noise — a real LLM evaluation would replace this
with actual API calls against the same typed state substrate.
"""
import random

from constraint_check import check_plan
from plan_builder import build_plan
from state_builder import build_state, empty_state

# Token cost model (estimated tokens per structural unit)
_TOKENS_PER_EVENT_SUMMARY = 18   # one event description in raw summary
_TOKENS_PER_CONCEPT_FIELD = 8    # one typed concept in observation packet
_TOKENS_PER_TEMPLATE = 6         # fixed template lookup
_TOKENS_LLM_RENDER_OVERHEAD = 40 # render-intent header for LLM call

# Simulated LLM noise
_LLM_NOISE_SIGMA = 0.30

# open_memory: age-based drop rate for summarization compression
_DROP_RATE = 0.55


def _make_trace(idx, tick, state_kind, weight, decay):
    return {
        "trace_id": f"t{idx:04d}",
        "signal_kind": "signal_a",
        "agent_x": "agent_a",
        "agent_y": "agent_b",
        "tick": tick,
        "attrs": {
            "state_kind": state_kind,
            "origin_trace": f"t{idx:04d}",
            "weight_band": weight,
            "decay_rate": decay,
        },
    }


def _build_state_from_events(events):
    state = empty_state()
    for idx, (tick, state_kind, weight, decay) in enumerate(events):
        state = build_state(state, _make_trace(idx, tick, state_kind, weight, decay))
    return state


def _fact_recall_from_state(state, key_facts):
    return {
        name: state["scores"].get(kind, 0.0) >= min_score
        for name, (kind, min_score) in key_facts.items()
    }


# ---------------------------------------------------------------------------
# Condition 1: open_memory
# ---------------------------------------------------------------------------

def run_open_memory(scenario, seed, runs=20):
    """
    Simulates summary-based memory: events accumulate as raw text tokens;
    each interaction compresses the buffer by randomly dropping older events
    with probability proportional to age. Fact recall degrades over time
    as older events are lost. Variance arises from random drop outcomes.
    """
    rng = random.Random(seed)
    events = scenario["events"]
    n = len(events)
    key_facts = scenario["key_facts"]
    results = []

    for run in range(runs):
        retained = []
        for idx, ev in enumerate(events):
            tick, state_kind, weight, decay = ev
            retained.append({"state_kind": state_kind, "weight": weight, "idx": idx})
            # Apply age-based compression after each event addition
            kept = []
            for item in retained:
                age_factor = 1.0 - item["idx"] / max(n - 1, 1)
                drop_prob = age_factor * _DROP_RATE
                if rng.random() >= drop_prob:
                    kept.append(item)
            retained = kept

        expr_score = sum(item["weight"] for item in retained)
        token_cost = n * _TOKENS_PER_EVENT_SUMMARY  # summary grows with history

        retained_kinds = {item["state_kind"] for item in retained}
        retained_scores = {}
        for item in retained:
            k = item["state_kind"]
            retained_scores[k] = retained_scores.get(k, 0.0) + item["weight"]

        facts_recalled = {
            name: (
                kind in retained_kinds
                and retained_scores.get(kind, 0.0) >= min_score
            )
            for name, (kind, min_score) in key_facts.items()
        }

        results.append({
            "expr_score": round(expr_score, 4),
            "token_cost": token_cost,
            "facts_recalled": facts_recalled,
            "template_hit": False,
            "state_replayable": False,
            "passed": False,
        })
    return results


# ---------------------------------------------------------------------------
# Condition 2: template_only
# ---------------------------------------------------------------------------

def run_template_only(scenario):
    """
    Deterministic template system. Responds only to the most recent event
    type with a fixed template. No concept accumulation across events.
    Zero variance by construction; poor recall for accumulated facts.
    """
    events = scenario["events"]
    last_tick, last_kind, last_weight, _ = events[-1]
    key_facts = scenario["key_facts"]

    # Template only knows about the most recent event kind
    facts_recalled = {
        name: (kind == last_kind)
        for name, (kind, _) in key_facts.items()
    }

    return [{
        "expr_score": round(last_weight, 4),
        "token_cost": _TOKENS_PER_TEMPLATE,
        "facts_recalled": facts_recalled,
        "template_hit": True,
        "state_replayable": False,
        "passed": False,
    }]


# ---------------------------------------------------------------------------
# Condition 3: typed_templates
# ---------------------------------------------------------------------------

def run_typed_templates(scenario):
    """
    Uses the Paper 1 artifact pipeline: deterministic typed state
    accumulation with template-based output. State is fully replayable
    from the event log. Zero variance; high fact recall.
    """
    state = _build_state_from_events(scenario["events"])
    case = {
        "case_id": scenario["name"],
        "allow_list": scenario["allow_list"],
        "deny_list": scenario["deny_list"],
        "must_match": scenario["must_match"],
        "traces": [],
    }
    plan = build_plan(state, case, "symbolic_rule", 0)
    checked = check_plan(plan, case)

    # Observation packet size: one entry per active concept in state
    token_cost = len(state["scores"]) * _TOKENS_PER_CONCEPT_FIELD
    facts_recalled = _fact_recall_from_state(state, scenario["key_facts"])

    return [{
        "expr_score": round(plan["score"], 4),
        "token_cost": token_cost,
        "facts_recalled": facts_recalled,
        "template_hit": True,
        "state_replayable": True,
        "passed": checked["passed"],
    }]


# ---------------------------------------------------------------------------
# Condition 4: typed_llm_sim
# ---------------------------------------------------------------------------

def run_typed_llm_sim(scenario, seed, runs=20):
    """
    Typed state pipeline with simulated LLM expression variance.
    The state layer is identical to typed_templates (deterministic,
    replayable, high fact recall). The expression layer adds Gaussian
    noise of sigma=_LLM_NOISE_SIGMA to simulate stochastic decoding.

    NOTE: A real LLM evaluation would replace the noise model with
    actual API calls. The state substrate (typed concepts, observation
    packets, constraint checks) would remain unchanged.
    """
    base = run_typed_templates(scenario)[0]
    base_score = base["expr_score"]
    token_cost = base["token_cost"] + _TOKENS_LLM_RENDER_OVERHEAD

    rng = random.Random(seed)
    results = []
    for _ in range(runs):
        noise = rng.gauss(0, _LLM_NOISE_SIGMA)
        expr_score = round(max(0.0, base_score + noise), 4)
        results.append({
            "expr_score": expr_score,
            "token_cost": token_cost,
            "facts_recalled": base["facts_recalled"],
            "template_hit": True,
            "state_replayable": True,
            "passed": base["passed"],
        })
    return results
