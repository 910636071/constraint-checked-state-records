# Research Agenda

This repository supports the second research direction:

Clean-room minimal artifact for a constraint-checked symbolic pipeline over
normalized records.

## Core Object

The study object is the checked record pipeline:

```text
r_t -> s_t -> p_t -> z_t -> q
```

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
2. Convert the current outline into a short paper draft.
3. Add a result paragraph that explains the observed score/pass-rate tradeoff
   without ranking one method as universally better.
4. Prepare arXiv submission materials after the paper draft is internally
   consistent with the repository.
