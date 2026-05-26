# Paper 2 White Paper Draft

Title: Variance Decay in Constraint-Gated Symbolic State Records

Author: Lijie Wang, Independent Researcher

Date: May 2026

Status: v0.2 theory white paper draft

## Abstract

This note gives a formal path for studying rule-guided behavior distillation in
a finite symbolic concept space. The central claim is deliberately narrow: if
accepted behavior observations are mapped into a finite ConceptObject space
through explicit gates and finite constraints, then the variance of the
empirical concept estimate decays with sample size. If a downstream expression
map is deterministic or Lipschitz-bounded with respect to that concept estimate,
then the expression representation inherits a corresponding variance bound.

The main theorem is a bounded-variance statement, not an unconditional claim
about arbitrary generated text:

```text
Var(mu_hat_m) <= M^2 / (4m)
```

for a bounded scalar committed signal in `[0, M]`, and

```text
Var(E(C_m)) <= L^2 n / (4m)
```

for a finite-dimensional concept estimate passed through an `L`-Lipschitz
expression map. The assumptions are finite concept dimension, fixed explicit
constraints, accepted samples with bounded outcomes, and independent or
suitably weakly dependent observations.

## 1. Scope

Paper 1 establishes a public artifact boundary for checked symbolic records:

```text
r_t -> s_t -> p_t -> z_t -> q
```

Paper 2 moves one level upward. It asks whether repeated behavior observations
can fill a finite concept space in a way that makes the empirical state estimate
stable. It does not require deployment data. It does not claim stability for
unrestricted language-model output. It studies a finite symbolic estimator and
the conditions under which downstream expression variance can be bounded.

The paper does not claim:

- convergence without assumptions;
- stability for arbitrary free-form text;
- superiority over learned methods;
- production readiness;
- real-user validation.

## 2. Core Objects

### 2.1 ConceptObject Space

Let

```text
K = {k_1, ..., k_n}
```

be a finite ConceptObject type space. Each `k_j` is a typed symbolic coordinate.
The finite dimension `n = |K|` is fixed before evaluation.

A ConceptObject is a typed record:

```text
o_t = (id_t, type_t, value_t, source_t, time_t)
```

where:

- `id_t` is a record identifier;
- `type_t in K`;
- `value_t` is a bounded symbolic or numeric value;
- `source_t` identifies the accepted observation that produced it;
- `time_t` is an ordering index.

The key restriction is that ConceptObjects are not free text labels. They must
land in the finite type space `K`.

### 2.2 ConstraintSet

Let

```text
C = (C_allow, C_deny, C_required)
```

be a finite explicit ConstraintSet. A typed candidate may be committed only if
it satisfies the active finite constraints.

In the simplest Boolean form:

```text
pass_C(o_t) =
  type_t in C_allow
  and type_t not in C_deny
  and required_C(o_t) = true.
```

The exact required predicate may vary by case, but it must be finite and
inspectable.

### 2.3 EventLog

Let

```text
E_t = (e_1, ..., e_t)
```

be the authoritative append-only EventLog before step `t + 1`. Each committed
event stores a validated record, a typed ConceptObject, the applied
ConstraintSet, and the gate decision.

The EventLog maintains five invariants:

1. EventLog is append-only.
2. Committed ConceptObjects must pass JudgementGate.
3. Summaries are non-authoritative projections.
4. LLM-generated or rendered text cannot mutate EventLog directly.
5. Rejected records cannot enter the authoritative state.

These invariants separate authoritative symbolic state from derived summaries
or expression-layer output.

## 3. Gate Semantics

Paper 2 uses three explicit gates. They are written as functions so that the
architecture can be checked independently of any implementation.

### 3.1 AssetGate

```text
G_A(r_t) -> {valid, rejected}
```

`r_t` is a raw symbolic record. AssetGate accepts a record only if it satisfies
basic structural requirements, such as required fields, type-compatible fields,
and admissible source metadata. A rejected record stops here.

Invariant:

```text
G_A(r_t) = rejected  =>  r_t notin E_t.
```

### 3.2 TaxonomyGate

```text
G_T(p_t) -> K union {rejected}
```

`p_t` is a parsed symbolic payload derived from a valid record. TaxonomyGate
maps the payload to a finite ConceptObject type in `K`. If no finite type is
available, the payload is rejected.

Invariant:

```text
G_T(p_t) = k  =>  k in K.
```

This gate is the finite-space restriction. It prevents arbitrary text labels
from becoming authoritative concept coordinates.

### 3.3 JudgementGate

```text
G_J(z_t, C, E_t) -> {committed, pending_review, rejected}
```

`z_t` is a typed candidate ConceptObject, `C` is the active ConstraintSet, and
`E_t` is the EventLog state before the decision. JudgementGate checks the typed
candidate against explicit constraints and the current authoritative state.

Invariant:

```text
G_J(z_t, C, E_t) = committed  =>  pass_C(z_t) = true.
```

Only committed ConceptObjects enter the empirical state estimator. Pending or
rejected candidates can be logged for inspection, but they do not update the
authoritative concept state.

## 4. Empirical Concept Estimator

Let

```text
B_m = (b_1, ..., b_m)
```

be the accepted behavior observations after passing through AssetGate,
TaxonomyGate, and JudgementGate.

Each committed observation is mapped to a bounded concept vector:

```text
phi(b_i) = X_i in [0, 1]^n.
```

The empirical concept state is

```text
C_m = (1/m) sum_{i=1}^m X_i.
```

For scalar gate outcomes or scores, let

```text
Y_i in [0, M]
```

be a bounded committed signal and define

```text
mu_hat_m = (1/m) sum_{i=1}^m Y_i.
```

The scalar estimator `mu_hat_m` is the cleanest object for the first theorem.
The vector estimator `C_m` gives the corresponding finite ConceptObject-space
version.

## 5. Main Theorem

### 5.1 Bounded Variance Decay under Finite Concept Constraints

Assume:

1. The ConceptObject type space `K` is finite.
2. The ConstraintSet `C` is fixed and explicit during evaluation.
3. Accepted observations are independent and identically distributed, or satisfy
   an equivalent bounded weak-dependence condition.
4. Each committed scalar signal satisfies `0 <= Y_i <= M`.
5. `mu_hat_m = (1/m) sum_i Y_i`.

Then

```text
Var(mu_hat_m) <= M^2 / (4m).
```

Therefore

```text
Var(mu_hat_m) -> 0
```

as `m -> infinity`.

Proof:

For any bounded random variable `Y_i in [0, M]`,

```text
Var(Y_i) <= M^2 / 4.
```

By independence,

```text
Var(mu_hat_m)
  = Var((1/m) sum_i Y_i)
  = (1/m^2) sum_i Var(Y_i)
  <= (1/m^2) m M^2 / 4
  = M^2 / (4m).
```

Since `M` is fixed, the right side converges to zero.

### 5.2 Vector Concept-State Bound

Assume:

1. `K` is finite with `|K| = n`.
2. `X_1, ..., X_m` are independent bounded concept vectors with common mean
   `theta`.
3. Each coordinate satisfies `0 <= X_{ij} <= 1`.
4. `C_m = (1/m) sum_i X_i`.
5. `E: [0,1]^n -> R^d` is `L`-Lipschitz:

```text
||E(x) - E(y)|| <= L ||x - y||.
```

For a vector-valued random variable `Z`, define total variance as

```text
Var(Z) = Expect ||Z - Expect[Z]||^2.
```

Let

```text
Z_m = E(C_m).
```

Then

```text
Var(Z_m) <= L^2 n / (4m).
```

Proof sketch:

For each coordinate,

```text
Var((C_m)_j) <= 1/(4m).
```

Summing over `n` coordinates gives

```text
Expect ||C_m - theta||^2 <= n/(4m).
```

The Lipschitz condition gives

```text
||E(C_m) - E(theta)||^2 <= L^2 ||C_m - theta||^2.
```

Taking expectations and bounding variance by mean squared distance to the fixed
center `E(theta)` yields

```text
Var(Z_m) <= L^2 n / (4m).
```

This proves the finite concept-state expression bound under the stated
assumptions.

## 6. What the Theorem Does and Does Not Say

The theorem gives a decreasing upper bound. It does not require every finite
empirical point to decrease. A measured curve may fluctuate across seeds or
finite sample sizes.

The theorem supports this statement:

```text
expected variance decreases with sample size under finite bounded constraints.
```

It does not support this stronger statement:

```text
all unconstrained generated text converges monotonically.
```

This distinction is the main safety condition for the theory.

## 7. Relationship to Paper 1

Paper 1 provides minimal evidence for the record-check-score boundary:

```text
SyntheticCase -> TraceStore -> Baselines -> ConstraintCheck -> ScoreCard
```

In Paper 2 terms:

- `SyntheticCase` provides normalized symbolic records.
- `TraceStore` gives the ordered observation substrate.
- `Baselines` provide candidate-generation rules.
- `ConstraintCheck` is the minimal finite-check analogue of JudgementGate.
- `ScoreCard` reports aggregate checked-record statistics.

Paper 1 does not prove variance decay. It provides minimal evidence that a
closed symbolic pipeline can separate records, intermediate state, proposals,
finite checks, and aggregate reporting. Paper 2 uses that separation as the
formal substrate for finite concept filling and variance analysis.

The connection is therefore:

```text
Paper 1 = minimal reproducible evidence for checked-record separation.
Paper 2 = formal variance bound for finite gated concept estimates.
```

## 8. Synthetic Convergence Experiment

Paper 2 can add a synthetic convergence experiment without deployment data. The
experiment should demonstrate the theorem's measurement objects, not claim
production validity.

Suggested variables:

```text
case_count in {100, 500, 1000}
behavior_length in {5, 10, 20, 50, 100, 200}
concept_type_count in {8, 16, 32}
constraint_set_size in {5, 10, 20}
seed_count >= 10
```

Reported metrics:

- mean score;
- variance of score;
- pass rate;
- invalid candidate rate;
- committed record count.

The expected result is a decreasing variance envelope as behavior sample size
increases. The paper should not claim strict monotone decrease for every
finite observed point.

## 9. FCA Mapping

Formal Concept Analysis can be used as background structure, not as the main
claim. Let

```text
(G, M, I)
```

be a formal context where:

- `G` is the set of accepted observations or episodes;
- `M` is the set of typed attributes, identified with `K`;
- `I subset G x M` is the incidence relation induced by committed
  ConceptObjects.

For `g in G` and `k in K`,

```text
g I k
```

means that observation `g` has committed attribute `k`.

For `A subset G`, define

```text
A' = {k in K : for all g in A, g I k}.
```

For `D subset K`, define

```text
D' = {g in G : for all k in D, g I k}.
```

A formal concept is a pair `(A, D)` such that

```text
A' = D
D' = A.
```

This mapping supports the claim that ConceptObject coordinates are finite,
checkable, and composable. It does not claim to replace FCA or extend FCA as a
mathematical theory.

## 10. Relationship to Paper 3

Paper 3 should test whether a renderer or system-level expression layer follows
the variance trend under scripted behavior streams. Paper 3 may measure
`Var(E(C_m))` empirically, but it should inherit the assumptions and definitions
from Paper 2:

- fixed finite concept space;
- fixed measurement representation;
- comparable constrained and unconstrained baselines;
- recorded seeds and sample counts;
- no claim of strict finite-sample monotonicity.

## 11. Limitations

The theory depends on finite concept dimension, bounded outcomes, explicit
constraints, and independence or weak-dependence assumptions. If behavior
samples are adversarial, nonstationary, or contradictory, the bound may not
describe the observed process. If the expression map is an unrestricted
stochastic text generator, raw text variance is not controlled without an
additional measurement map and stability assumption.

The result should therefore be read as a formal bound for finite
constraint-gated symbolic state records, not as a general statement about all
generative systems.
