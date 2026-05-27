# Paper 2 White Paper Draft

Title: Variance Decay for Finite Constraint-Checked Symbolic Estimators

Author: Lijie Wang, Independent Researcher

Date: May 2026

Status: v0.2 theory white paper draft

## Abstract

This note gives a formal path for studying rule-guided behavior distillation in
a finite symbolic concept space. The central claim is deliberately narrow: if
accepted observations are mapped into a finite concept space through explicit
validation, typing, and commitment interfaces, then the variance of the
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
stable. It does not require operational data. It does not claim stability for
unrestricted generated output. It studies a finite symbolic estimator and the
conditions under which a downstream measurement representation can be bounded.

The paper does not claim:

- convergence without assumptions;
- stability for arbitrary free-form text;
- superiority over learned methods;
- production readiness;
- real-user validation.

## 2. Formal Objects

This section fixes the symbols used by the theorem. The definitions are kept
small on purpose: the claim is about a finite bounded estimator, not about a
complete application architecture.

**Definition 1 (Finite concept space).** Let

```text
K = {k_1, ..., k_n},    n = |K| < infinity
```

be a finite concept coordinate space. Each `k_j` is a typed symbolic coordinate.
The dimension `n` is fixed before evaluation.

**Definition 2 (Typed symbolic record).** A typed record at step `t` is

```text
o_t = (id_t, type_t, value_t, source_t, time_t)
```

where `type_t in K`, `value_t` is bounded, `source_t` identifies the accepted
observation that produced the record, and `time_t` is an ordering index. The
important restriction is that `type_t` must land in `K`; a typed record is not a
free text label.

**Definition 3 (Constraint set).** Let

```text
C = (C_allow, C_deny, C_required)
```

be a finite explicit constraint set. A typed candidate may be committed only if
it satisfies the active finite constraints. In the simplest Boolean form:

```text
pass_C(o_t) =
  type_t in C_allow
  and type_t not in C_deny
  and required_C(o_t) = true.
```

The exact required predicate may vary by case, but it must be finite and
inspectable.

**Definition 4 (Append-only event sequence).** Let

```text
E_t = (e_1, ..., e_t)
```

be the authoritative append-only event sequence before step `t + 1`. Each
committed event stores a validated record, a typed record, the applied
constraint set, and the interface decision.

The event sequence maintains five invariants:

1. The event sequence is append-only.
2. Committed typed records must pass the commitment interface.
3. Summaries are non-authoritative projections.
4. Downstream expression output cannot mutate the event sequence directly.
5. Rejected records cannot enter the empirical estimator.

## 3. Formal Interfaces

Paper 2 uses three explicit interfaces. They are written as functions so that
the assumptions can be checked independently of any implementation.

**Definition 5 (Validation interface).** Let `R` be the set of raw symbolic
records. The validation interface is

```text
V: R -> {valid, rejected}.
```

If `V(r_t) = rejected`, then `r_t` cannot be appended to `E_t`.

**Definition 6 (Typing interface).** Let `P` be the set of validated symbolic
payloads. The typing interface is

```text
T: P -> K union {rejected}.
```

If `T(p_t) = k`, then `k in K`. This is the finite-space restriction: arbitrary
text labels cannot become authoritative concept coordinates.

**Definition 7 (Commitment interface).** Let `Z` be the set of typed candidate
records. The commitment interface is evaluated as

```text
J(z_t, C, E_t) -> {committed, pending_review, rejected}.
```

The commitment condition is

```text
J(z_t, C, E_t) = committed  =>  pass_C(z_t) = true.
```

Only committed typed records enter the empirical state estimator. Pending or
rejected candidates can be logged for inspection, but they do not update the
authoritative concept state.

## 4. Empirical Concept Estimator

**Definition 8 (Accepted observation sequence).** Let

```text
B_m = (b_1, ..., b_m)
```

be the sequence of committed observations after validation, typing, and
commitment.

**Definition 9 (Vector estimator).** Let `B` be the set of possible committed
observations, and let

```text
phi: B -> [0, 1]^n
X_i = phi(b_i).
```

For the Paper 1 artifact, `phi` maps each committed record to a normalized
concept coordinate vector. The raw accumulated score for concept coordinate `k`
is divided by `M_UPPER` (defined below) to place each coordinate in `[0, 1]`.

The empirical concept estimate is

```text
C_m = (1/m) sum_{i=1}^m X_i.
```

**Definition 10 (Scalar estimator).** For scalar interface outcomes or scores,
let

```text
Y_i in [0, M]
```

be a bounded committed signal and define

```text
mu_hat_m = (1/m) sum_{i=1}^m Y_i.
```

The scalar estimator `mu_hat_m` is the cleanest object for the first theorem.
The vector estimator `C_m` gives the corresponding finite concept-space
version.

### 4.1 Artifact Score Bound (M_UPPER)

For the Paper 1 artifact, accumulated scores follow a decayed geometric series.
With `weight_band in {0.5, 0.7, 0.9}` and `decay_rate in {0.05, 0.10, 0.20}`,
the geometric series limit gives an analytic upper bound on any accumulated
score:

```text
M_UPPER = max(weight_band) / min(decay_rate) = 0.9 / 0.05 = 18.0
```

Any committed score satisfies `Y_i in [0, M_UPPER]`. For the vector case,
`phi(b) = score_vector / M_UPPER` places each coordinate in `[0, 1]`, as
required by Definition 9.

The empirical pilot (seed=37, 20 cases, 10 runs per method) yields
`Var(Y_i) = 0.257`, which is well below `M_UPPER^2 / 4 = 81`, confirming
that the Popoviciu bound is not tight for this artifact but does hold.

### 4.2 Symbol Consistency

The theorem uses the following symbols consistently:

| Symbol | Meaning |
| --- | --- |
| `K` | finite concept coordinate space |
| `n` | dimension `|K|` |
| `C` | finite explicit constraint set |
| `E_t` | append-only event sequence at step `t` |
| `V` | validation interface |
| `T` | typing interface |
| `J` | commitment interface |
| `B_m` | committed observation sequence of length `m` |
| `phi` | map from committed observations to bounded concept vectors |
| `X_i` | bounded concept vector in `[0,1]^n` |
| `C_m` | empirical concept estimate |
| `Y_i` | bounded scalar committed signal in `[0,M]` |
| `mu_hat_m` | empirical scalar mean |
| `E` | downstream measurement map in `E(C_m)` |

The symbol `E_t` always denotes the event sequence. The symbol `E` without a
time subscript denotes the downstream measurement map used in the vector
variance bound.

## 5. Main Theorem

### 5.1 Bounded Variance Decay under Finite Concept Constraints

Assume:

1. The concept type space `K` is finite.
2. The constraint set `C` is fixed and explicit during evaluation.
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
Var(Z) <= Expect ||Z - c||^2 for any constant c,
```

because total variance is minimized at `c = Expect[Z]`. Choosing
`c = E(theta)` gives

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
- `ConstraintCheck` is the minimal finite-check analogue of the commitment
  interface.
- `ScoreCard` reports aggregate checked-record statistics.

Paper 1 does not prove variance decay. It provides minimal evidence that a
closed symbolic pipeline can separate records, intermediate state, proposals,
finite checks, and aggregate reporting. Paper 2 uses that separation as the
formal substrate for finite concept filling and variance analysis.

The connection is therefore:

```text
Paper 1 = minimal reproducible evidence for checked-record separation.
Paper 2 = formal variance bound for finite constraint-checked concept estimates.
```

## 8. Synthetic Convergence Experiment

A minimal convergence experiment is implemented in
`scripts/run_convergence.py`. It uses the Paper 1 artifact directly and
requires no operational data.

**Design.** The experiment fixes the case set (seed=37, 20 cases) and
sweeps `runs in {1, 2, 5, 10, 20, 50, 100, 200}`, producing
`m = 60` to `m = 12000` committed records. For each level it reports:

- `avg_q`: mean committed score (empirical `mu_hat_m`);
- `var_q`: population variance of individual scores (empirical `Var(Y_i)`);
- `var_mu_hat_iid`: `var_q / m`, the i.i.d.-implied estimate of
  `Var(mu_hat_m)`;
- `bound_M2_4m`: the theoretical upper bound `M_UPPER^2 / (4m)`.

Results are written to `outputs/convergence.csv`.

**Interpretation.** Because the artifact is fully deterministic (fixed
seed, no stochastic draws), `Var(mu_hat_m)` cannot be observed
empirically across independent replications. The table instead reports
`var_q / m` as the i.i.d.-implied variance estimate. The observed
`var_q ≈ 0.25–0.28` remains bounded and well below `M_UPPER^2 / 4 = 81`
across all levels, confirming the Popoviciu assumption. The derived
`var_mu_hat_iid` decreases from `0.0047` at `m=60` to `0.000021` at
`m=12000`, consistent with the `M_UPPER^2 / (4m)` bound.

**Scope caveat.** This experiment demonstrates the theorem's measurement
objects on the frozen artifact. It does not claim external validity,
strict finite-sample monotone decrease, or results beyond this closed
protocol.

## 9. FCA Mapping

Formal Concept Analysis can be used as background structure, not as the main
claim. Let

```text
(G, M, I)
```

be a formal context where:

- `G` is the set of accepted observations or episodes;
- `M` is the set of typed attributes, identified with `K`;
- `I subset G x M` is the incidence relation induced by committed typed records.

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

This mapping supports the claim that concept coordinates are finite,
checkable, and composable. It does not claim to replace FCA or extend FCA as a
mathematical theory.

## 10. Future Empirical Validation

A later empirical study may test whether a downstream measurement layer follows
the variance trend under scripted or synthetic behavior streams. Such a study
may measure `Var(E(C_m))` empirically, but it should inherit the assumptions and
definitions from Paper 2:

- fixed finite concept space;
- fixed measurement representation;
- comparable constrained and unconstrained baselines;
- recorded seeds and sample counts;
- no claim of strict finite-sample monotonicity.

## 11. Limitations

The theory depends on finite concept dimension, bounded outcomes, explicit
constraints, and independence or weak-dependence assumptions. If behavior
samples are adversarial, nonstationary, or contradictory, the bound may not
describe the observed process. If the expression map is unrestricted or
stochastic, output variance is not controlled without an additional measurement
map and stability assumption.

The result should therefore be read as a formal bound for finite
constraint-checked symbolic estimators, not as a general statement about all
generative systems.
