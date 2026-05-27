"""
Real LLM expression condition (Condition 4b) for Paper 3 Section 5.2.

Requires ANTHROPIC_API_KEY in the environment. Replaces the Gaussian
noise simulation in run_typed_llm_sim with actual Claude API calls while
keeping the typed state substrate identical to run_typed_templates.

Usage:
    export ANTHROPIC_API_KEY=sk-ant-...
    python -m scripts.run_eval --use-real-llm
"""
import json
import os

import anthropic

from eval.conditions import _build_state_from_events, run_typed_templates
from constraint_check import check_plan
from plan_builder import build_plan

MODEL = "claude-haiku-4-5-20251001"
MAX_TOKENS = 256


def _build_observation_packet(scenario, state):
    """
    Constructs a bounded observation packet from typed state.
    This is what the LLM is allowed to see — not full history, only
    the committed concept scores and the active constraint set.
    """
    scores_sorted = sorted(state["scores"].items(), key=lambda x: -x[1])
    return {
        "scenario": scenario["name"],
        "active_concepts": [
            {"kind": k, "score": round(v, 3)}
            for k, v in scores_sorted
            if v > 0.01
        ],
        "allow_list": scenario["allow_list"],
        "deny_list": scenario["deny_list"],
        "record_count": state["record_count"],
    }


def _build_prompt(packet, key_facts):
    facts_list = "\n".join(
        f'  - "{name}": does the response reflect that {kind} has score >= {min_score:.2f}?'
        for name, (kind, min_score) in key_facts.items()
    )
    return f"""You are a minimal persona agent. Your only memory is the observation packet below.
Do not invent facts not in the packet.

Observation packet:
{json.dumps(packet, indent=2)}

Respond with valid JSON only:
{{
  "expression": "<2-3 sentence natural response that reflects this state>",
  "facts_present": {{
{chr(10).join(f'    "{name}": true_or_false' for name in key_facts)}
  }}
}}

For each fact in facts_present, answer true if the expression naturally reflects it, false otherwise.
Fact definitions:
{facts_list}"""


def run_typed_llm_real(scenario, runs=5):
    """
    Real LLM condition: typed state pipeline + Claude API expression layer.

    The state substrate (build_state, check_plan) is identical to
    run_typed_templates. Only the expression step uses the LLM.

    Returns per-run outputs in the same format as run_typed_llm_sim so
    compute_metrics works unchanged.
    """
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError(
            "ANTHROPIC_API_KEY not set. "
            "Export your key and re-run with --use-real-llm."
        )

    client = anthropic.Anthropic(api_key=api_key)
    state = _build_state_from_events(scenario["events"])
    packet = _build_observation_packet(scenario, state)

    case = {
        "case_id": scenario["name"],
        "allow_list": scenario["allow_list"],
        "deny_list": scenario["deny_list"],
        "must_match": scenario["must_match"],
        "traces": [],
    }
    plan = build_plan(state, case, "symbolic_rule", 0)
    checked = check_plan(plan, case)

    prompt = _build_prompt(packet, scenario["key_facts"])
    token_cost_state = len(state["scores"]) * 8  # observation packet tokens

    results = []
    for run in range(runs):
        response = client.messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            messages=[{"role": "user", "content": prompt}],
        )
        raw = response.content[0].text.strip()
        token_cost_call = response.usage.input_tokens + response.usage.output_tokens

        try:
            parsed = json.loads(raw)
            expression = parsed.get("expression", "")
            facts_recalled = {
                k: bool(v)
                for k, v in parsed.get("facts_present", {}).items()
            }
        except (json.JSONDecodeError, AttributeError):
            expression = raw
            facts_recalled = {k: False for k in scenario["key_facts"]}

        # expr_score = fraction of facts recalled (0–1 scale)
        n_facts = len(facts_recalled)
        expr_score = (
            sum(1 for v in facts_recalled.values() if v) / n_facts
            if n_facts else 0.0
        )

        results.append({
            "run": run,
            "expr_score": round(expr_score, 4),
            "token_cost": token_cost_state + token_cost_call,
            "facts_recalled": facts_recalled,
            "template_hit": True,
            "state_replayable": True,
            "passed": checked["passed"],
            "expression": expression,  # keep text for inspection
        })

    return results
