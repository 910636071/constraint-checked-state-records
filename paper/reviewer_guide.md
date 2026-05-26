# Reviewer Guide

This guide is for researchers in AI and games, computational creativity,
interactive agents, symbolic evaluation, and reproducible research artifacts.

## One-sentence Summary

This project abstracts a broader interactive-agent and game-AI state problem
into a clean-room symbolic estimator with explicit constraints and auditable
assumptions.

## What to Read First

1. `README.md` for the repository boundary and reproduction commands.
2. `paper/external_review_note.md` for the intended review positioning.
3. `paper/paper2_finite_concept_filling.md` for the Paper 2 theory draft.

## What Is New

The contribution is not the variance inequality by itself. The contribution is
the reduction from checked symbolic records to a finite bounded estimator with
auditable assumptions.

In short, the project asks whether a rule-checked symbolic state pipeline can be
reduced to:

```text
accepted observations
  -> finite concept coordinates
  -> explicit constraint checks
  -> bounded empirical estimator
  -> variance bound
```

This gives later consistency or expression measurements a finite, inspectable
object instead of leaving them inside uncontrolled text summaries.

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

- Not a product system.
- Not a natural-language parser.
- Not a model-training method.
- Not a claim of broad empirical superiority.
- Not a claim that unrestricted generated output converges.

## Main Review Questions

1. Is the reduction from checked symbolic records to a finite bounded estimator
   credible?
2. Are the assumptions in the variance theorem explicit enough?
3. Is the relationship between the minimal artifact and the theory layer clear?
4. Is a synthetic convergence experiment the right next validation step?
