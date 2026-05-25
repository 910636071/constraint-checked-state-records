# Research Agenda

This repository supports the second research direction:

Public artifact boundary closure for constraint-checked symbolic state records.

The direction is to define a small reproducible protocol in which normalized
records, trace state, deterministic proposals, finite constraint checks, and
aggregate score reporting remain separated and auditable. The current artifact
is therefore closer to a public white paper / external-review artifact than a
full technical paper.

## Core Object

The study object is the checked record pipeline:

```text
r_t -> s_t -> p_t -> z_t -> q
```

At the implementation level, the same object is represented as:

```text
SyntheticCase -> TraceStore -> Baselines -> ConstraintCheck -> ScoreCard
```

The paper should use the symbolic chain as the formal object and the
implementation chain as the artifact boundary.

The current artifact fixes:

- 20 synthetic normalized cases.
- Three deterministic candidate-selection methods.
- One finite constraint-checking protocol.
- One aggregate score card.

## Research Questions

1. How do deterministic candidate-selection methods change score and pass-rate
   under the same checked-record protocol?
2. Which parts of the result come from state construction, candidate selection,
   and constraint checking?
3. How small can the protocol remain while still producing inspectable
   method-level differences?

## Evidence Boundary

The current evidence supports only a compact artifact paper / technical note.
It does not support claims about broad empirical superiority, large-scale model
behavior, or deployment behavior.

## Next Work

1. Keep the implementation frozen unless a release-blocking issue appears.
2. Collect external feedback on whether the boundary is clear and useful.
3. Decide whether to continue as a public white paper or expand into an
   arXiv-style technical note.
4. If expanded later, add stronger baselines or larger symbolic case banks only
   as v0.2 work.
