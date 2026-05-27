# Each scenario: name, events (tick, state_kind, weight_band, decay_rate),
# allow/deny/must constraints, and key_facts to check recall against.
# key_facts: {fact_name: (required_state_kind, min_score)}
# A fact is "recalled" if the condition's output shows that state_kind with
# score >= min_score.

SCENARIOS = [
    {
        "name": "library_routine",
        "description": "Repeated library visits should establish a dominant concept.",
        "events": [
            (1,  "routine_library", 0.9, 0.05),
            (3,  "oneoff_cafe",     0.5, 0.20),
            (5,  "routine_library", 0.9, 0.05),
            (8,  "routine_library", 0.9, 0.05),
            (12, "routine_library", 0.9, 0.05),
        ],
        "allow_list": ["routine_library", "oneoff_cafe"],
        "deny_list": [],
        "must_match": ["routine_library"],
        "key_facts": {
            "library_dominant": ("routine_library", 0.5),
            "cafe_visited":     ("oneoff_cafe",     0.01),
        },
    },
    {
        "name": "gift_decay",
        "description": "Repeated identical gifts should decay in significance over time.",
        "events": [
            (1,  "gift_flower", 0.9, 0.10),
            (3,  "gift_flower", 0.9, 0.10),
            (5,  "gift_flower", 0.9, 0.10),
            (7,  "gift_flower", 0.9, 0.10),
            (9,  "gift_flower", 0.9, 0.10),
        ],
        "allow_list": ["gift_flower"],
        "deny_list": [],
        "must_match": ["gift_flower"],
        "key_facts": {
            "gift_tracked": ("gift_flower", 0.1),
        },
    },
    {
        "name": "boundary_trust",
        "description": "Repeated interruptions conflict with trust; deny list blocks them.",
        "events": [
            (1,  "trust_bond",       0.9, 0.05),
            (3,  "interrupt_action", 0.7, 0.10),
            (5,  "interrupt_action", 0.7, 0.10),
            (7,  "trust_bond",       0.5, 0.05),
            (9,  "interrupt_action", 0.7, 0.10),
            (12, "trust_bond",       0.7, 0.05),
        ],
        "allow_list": ["trust_bond"],
        "deny_list": ["interrupt_action"],
        "must_match": ["trust_bond"],
        "key_facts": {
            "trust_tracked":       ("trust_bond",       0.3),
            "interruption_logged": ("interrupt_action", 0.1),
        },
    },
    {
        "name": "mixed_concepts",
        "description": "Multiple concept families compete; typed state tracks all.",
        "events": [
            (1,  "social_gift",  0.9, 0.10),
            (2,  "work_task",    0.7, 0.10),
            (4,  "social_chat",  0.5, 0.20),
            (6,  "social_gift",  0.9, 0.10),
            (8,  "work_task",    0.7, 0.10),
            (10, "leisure_walk", 0.5, 0.20),
            (12, "social_gift",  0.9, 0.10),
        ],
        "allow_list": ["social_gift", "social_chat"],
        "deny_list": ["work_task"],
        "must_match": ["social_gift"],
        "key_facts": {
            "social_dominant": ("social_gift", 0.5),
            "work_logged":     ("work_task",   0.1),
        },
    },
    {
        "name": "long_session",
        "description": "30-event session to show token cost scaling divergence.",
        "events": [
            (t, "routine_study" if t % 3 != 0 else "oneoff_break", 0.7, 0.05)
            for t in range(1, 31)
        ],
        "allow_list": ["routine_study", "oneoff_break"],
        "deny_list": [],
        "must_match": ["routine_study"],
        "key_facts": {
            "study_dominant": ("routine_study", 0.5),
        },
    },
]
