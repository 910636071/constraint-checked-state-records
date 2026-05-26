# Research Agenda

This repository supports the second research direction:

Variance decay for finite constraint-checked symbolic estimators.

The current repository intentionally reuses the Paper 1 clean-room artifact as a
frozen evidence boundary. Paper 1 is the reproducible protocol. Paper 2 is the
formal theory layer built above that protocol.

## Three-Layer Program

```text
Paper 1: minimal reproducible artifact
Paper 2: finite-space variance theory
Future empirical work: measurement protocol over larger symbolic streams
```

The purpose of this repository is Paper 2. It should not be reviewed as a
second implementation contribution. The software modules remain close to Paper
1 so that the assumptions in Paper 2 can be inspected against a small,
deterministic, public artifact.

## Paper 2 Research Object

Paper 2 studies this abstract object:

```text
accepted observations
  -> finite concept coordinates
  -> explicit constraint checks
  -> bounded empirical estimator
  -> aggregate variance bound
```

The main theorem is conditional. It applies only when:

- the concept coordinate space is finite;
- the constraint set is fixed and explicit during evaluation;
- accepted samples are independent or weakly dependent;
- committed scalar outcomes are bounded; and
- downstream measurement maps are deterministic or Lipschitz-bounded.

## Current Questions

1. Are the assumptions strong enough to make the variance theorem self-contained?
2. Is the interface separation clear enough for another researcher to audit?
3. Does the inherited Paper 1 artifact make the theory less abstract without
   creating unnecessary implementation claims?
4. What synthetic convergence experiment would be the smallest credible next
   validation step?

## Evidence Boundary

The current evidence supports a public theory white paper plus a minimal
artifact reference. It does not yet support broad empirical claims,
real-world operational claims, or claims about unrestricted generated output.

## Next Work

1. Keep the inherited Paper 1 implementation frozen unless a release-blocking
   issue appears.
2. Ask human reviewers to inspect the Paper 2 theorem and assumptions.
3. If expanded, add a synthetic convergence experiment that reports variance
   envelopes rather than strict finite-sample monotonicity.
4. Keep future empirical validation as a separate work item until it has its
   own public abstraction and evidence boundary.
