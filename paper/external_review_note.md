# External Review Note for the Paper 2 Theory Track

This note records the intended positioning for human mentor or external review.
It should be read together with `paper/paper2_finite_concept_filling.md`.

The repository contains two layers:

1. an inherited clean-room artifact layer from Paper 1, kept as the minimal
   reproducible evidence boundary; and
2. a Paper 2 theory layer, which studies variance decay for finite
   constraint-checked symbolic estimators.

The implementation modules are intentionally close to the Paper 1 artifact. The
new object for review is not another software system. It is the formal question
of whether bounded observations, finite concept coordinates, explicit
constraints, and an append-only event sequence are sufficient to support a
variance-decay statement for an empirical symbolic estimator.

## Concrete Evaluation Setting

The motivating setting is a small scripted game-agent evaluation protocol:

```text
scripted event stream
  -> candidate state records
  -> constraint check
  -> committed symbolic state
  -> later behavior or expression measurement
```

The purpose of the abstraction is to avoid treating persistent agent state as an
uncontrolled text summary. Instead, event records must pass explicit checks
before they enter committed state. Later consistency or expression measurements
can then be defined against that committed symbolic state.

This draft does not include a full game environment. The concrete setting is a
controlled evaluation scaffold for making the state-update assumptions
auditable.

## Current Review Target

The current review target is:

```text
finite concept space
  + explicit constraint set
  + validation / typing / commitment interfaces
  + bounded empirical estimator
  -> variance bound
```

The key theorem is a bounded-variance statement. For scalar committed signals
`Y_i in [0, M]`, the draft states:

```text
Var(mu_hat_m) <= M^2 / (4m).
```

For vector concept estimates passed through an `L`-Lipschitz downstream
measurement map, the draft states:

```text
Var(E(C_m)) <= L^2 n / (4m).
```

These are conditional statements. They require finite dimension, bounded
outcomes, fixed explicit constraints, and independent or weakly dependent
accepted observations.

## Relationship to Paper 1

Paper 1 answers a smaller reproducibility question:

```text
Can a clean-room symbolic pipeline separate records, traces, proposals,
constraint checks, and aggregate scores?
```

Paper 2 uses that separation as a substrate for a broader theory question:

```text
Under finite concept constraints, does the empirical estimator have a
sample-size variance bound?
```

The repeated modules are therefore not intended as a second implementation
claim. They are a frozen minimal artifact used to make the Paper 2 assumptions
inspectable.

## What This Draft Does Not Claim

- It does not claim broad empirical superiority.
- It does not claim convergence for unrestricted generated output.
- It does not include real user data or operational data.
- It does not depend on a product system.
- It does not claim that every finite sample curve decreases monotonically.

## Suggested Review Questions

1. Are the assumptions of the variance theorem explicit enough?
2. Is the mapping from checked records to finite concept coordinates clear?
3. Is the relationship between the Paper 1 artifact and Paper 2 theory
   understandable?
4. Is the proposed synthetic convergence experiment sufficient as a next
   validation step?
5. Should this remain a public white paper, or is it ready to become an
   arXiv-style technical note after adding the synthetic convergence experiment?