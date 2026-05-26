# Reviewer Guide

This guide is for researchers in AI and games, computational creativity,
interactive agents, symbolic evaluation, and reproducible research artifacts.
It starts from a concrete game-agent evaluation setting and then explains the
formal abstraction.

## One-sentence Summary

This project studies a small scripted game-agent evaluation setting: an agent
receives a sequence of event records, a checker decides which records can enter
the committed state, and later behavior or expression can be measured against
that committed state.

## Concrete Setting

The concrete setting is intentionally small:

```text
scripted event stream
  -> candidate state records
  -> constraint check
  -> committed symbolic state
  -> later behavior or expression measurement
```

The motivating problem is that persistent game or narrative agents often carry
long-term state. If that state is maintained only through unconstrained text
summaries, it becomes hard to audit which events actually changed the agent's
state and why.

This repository reduces the problem to symbolic records. It does not implement
a full game environment. The point is to make the state-update and evaluation
assumptions inspectable before moving to a larger environment.

The intended long-term direction is to evaluate whether checked symbolic state
gives a more stable basis for persistent game-agent behavior than unconstrained
text-summary loops.

## What to Read First

1. `README.md` for the repository boundary and reproduction commands.
2. `paper/external_review_note.md` for the intended review positioning.
3. `paper/paper2_finite_concept_filling.md` for the Paper 2 theory draft.

## What Is New

The contribution is not the variance inequality by itself. The contribution is
the reduction from a concrete checked-record evaluation setting to a finite
bounded estimator with auditable assumptions.

In short, the project asks whether a rule-checked symbolic state pipeline can be
reduced to:

```text
accepted observations
  -> finite concept coordinates
  -> explicit constraint checks
  -> bounded empirical estimator
  -> variance bound
```

This gives later behavior-consistency or expression measurements a finite,
inspectable object instead of leaving them inside uncontrolled text summaries.

## Relationship Between Paper 1 and Paper 2

Paper 1 is the frozen public artifact substrate. It shows that normalized
records, traces, proposals, finite checks, and aggregate scores can be separated
in a minimal reproducible pipeline.

Paper 2 is the theory layer. It uses that separation to define a finite concept
space, validation / typing / commitment interfaces, bounded scalar and vector
estimators, and a conditional variance-decay statement.

The repeated implementation files are intentional. They make the assumptions
auditable; they are not presented as a second software contribution.

## What This Is Not

- Not a full game environment.
- Not a product system.
- Not a natural-language parser.
- Not a model-training method.
- Not a claim of broad empirical superiority.
- Not a claim that unrestricted generated output converges.

## Main Review Questions

1. Is the scripted game-agent evaluation setting concrete enough?
2. Is the reduction from checked symbolic records to a finite bounded estimator
   credible?
3. Are the assumptions in the variance theorem explicit enough?
4. Is the relationship between the minimal artifact and the theory layer clear?
5. Is a controlled synthetic evaluation the right next validation step?