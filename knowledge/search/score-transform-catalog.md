# Score Transform Catalog

Reference for choosing the right mathematical transform when converting raw signals into [0,1] scores for ranking, importance, or confidence formulas. Each transform has different properties — using the wrong one distorts the signal before it reaches the combination formula.

---

## Transforms

### Log-Scale
```
score = min(1.0, log10(count + 1) / divisor)
```

**Properties:** Compresses high values, spreads low values. Good for power-law distributions where most values are small but a few are very large.

**When to use:** Count-based signals with heavy right skew — access counts, retrieval counts, citation counts.

**Neuroloom usage:** `importance_scoring_service.py` uses `log10(count+1)/2` for access_score and retrieval_score. Score ≈ 1.0 at ~100 counts.

**Parameters:** The divisor controls the saturation point. `/2` saturates at ~100, `/3` saturates at ~1000.

**Watch for:** Log(1) = 0, so a single access/retrieval scores 0.0. If you want "at least some signal" for count=1, consider `log10(count+1)/divisor` with a floor.

---

### Exponential Decay
```
score = base^(t / half_life)
```

**Properties:** Halves at fixed intervals. Aggressive — drops fast initially, then slowly approaches zero. Never reaches zero.

**When to use:** Time-based relevance where recent items are strongly preferred and older items retain a small residual signal.

**Neuroloom usage:** `importance_scoring_service.py` uses `0.5^(days / half_life_days)` for recency_score.

**Parameters:** `half_life` controls how quickly signal decays. 30-day half-life: after 30 days, score = 0.5; after 60 days, score = 0.25.

**Comparison with linear:** Exponential front-loads the decay (drops 50% in the first half-life), while linear spreads it evenly. Choose exponential when freshness matters disproportionately; linear when steady decline is desired.

---

### Linear Decay
```
score = max(floor, 1.0 - (t / window))
```

**Properties:** Steady, predictable decline. Reaches the floor at `t = window`. Simpler to reason about than exponential.

**When to use:** When you want uniform decay rate and a clear "fully stale" boundary.

**Hindsight usage:** `max(0.1, 1.0 - days/365)` for recency. Floor at 0.1 means even year-old items retain some signal.

**Parameters:** `window` is the time-to-floor. `floor` prevents complete zeroing (useful when old items should still appear if nothing else matches).

---

### Sigmoid
```
score = 1 / (1 + exp(-x))
```

**Properties:** S-shaped curve mapping ℝ → (0, 1). Smooth, centered at x=0 (where score = 0.5). Saturates symmetrically at both ends.

**When to use:** Normalizing unbounded model outputs (cross-encoder logits, raw neural network scores) to [0,1].

**Hindsight usage:** Normalizes cross-encoder reranking scores (which can be negative logits) to [0,1].

**Watch for:** Sigmoid is NOT the same as min-max normalization. It's a fixed nonlinear transform — the same input always produces the same output, regardless of the result set. Use when you need absolute normalization; use min-max when you need relative normalization within a result set.

---

### Tanh Saturation
```
score = tanh(count × scale)
```

**Properties:** Maps [0, ∞) → [0, 1) with natural diminishing returns. Similar to sigmoid but asymmetric (starts at 0, not 0.5).

**When to use:** Count-to-score conversion where the first few counts matter most and additional counts yield diminishing value.

**Hindsight usage:** `tanh(shared_entity_count × 0.5)` for graph entity co-occurrence scoring:
- 1 entity → 0.46
- 2 entities → 0.76
- 3 entities → 0.91
- 4 entities → 0.96

**Comparison with log:** Tanh saturates faster and more aggressively. `log10(4+1)/2 = 0.35` vs `tanh(4×0.5) = 0.96`. Use tanh when you want strong saturation; log when you want gentler compression.

**Parameters:** `scale` controls saturation speed. Lower scale (0.3) = gentler curve. Higher scale (1.0) = almost binary (1 count ≈ 0.76, 2 counts ≈ 0.96).

---

### Linear Ratio
```
score = numerator / denominator  (or 0.5 if denominator = 0)
```

**Properties:** Direct proportion. No nonlinearity. Range depends on inputs.

**When to use:** Balanced binary signals where the ratio IS the signal — positive/negative feedback, support/contradiction.

**Neuroloom usage:** `importance_scoring_service.py` uses `positive_count / total` for feedback_score, defaulting to 0.5 (neutral) when no feedback exists.

**Watch for:** Small denominators produce volatile scores. 1 positive out of 1 total = 1.0, which may overweight a single vote. Consider Bayesian smoothing (`(positive + prior) / (total + 2*prior)`) for small sample sizes.

---

## Combination Methods

### Additive (Weighted Sum)
```
score = w1×s1 + w2×s2 + w3×s3
```
Signals contribute independently. A high s2 compensates for low s1. Simple, interpretable. Requires signals to be on comparable scales — mismatched distributions mean weights don't reflect actual influence.

**Neuroloom usage:** Both importance scoring (7 signals) and search scoring (keyword/semantic/importance).

### Multiplicative Boost
```
score = base_score × (1 + α(signal - 0.5))
```
Secondary signals adjust the base proportionally. A low-relevance result gets a small boost even with perfect recency. Preserves the base signal's ordering while allowing ±α/2 adjustment.

**Hindsight usage:** Cross-encoder score × recency boost × temporal boost. Max combined adjustment ≈ ±20%.

### Reciprocal Rank Fusion
```
score = Σ 1/(k + rank_i)
```
Operates on ranks, not scores. No calibration needed across streams. k=60 is the standard constant. Best when combining retrieval strategies with incommensurable score distributions.

---

### Floor (Guaranteed Minimum Score)
```
score = max(floor_value, computed_score)
```

**Properties:** Prevents a penalized or decayed score from falling below a fixed threshold. Guarantees the document remains "visible" in a ranked list even when all penalty multipliers are applied. The floor does not affect documents whose computed score is already above it.

**Plain language:** Think of a graduated tax with a minimum rate. No matter how many deductions you apply, the government always takes at least X%. In retrieval, no matter how heavily penalized a document is (expired, superseded, contradicted), it always scores at least the floor value. This is particularly relevant for provenance queries — "why did we change our mind?" — where you want the old document to surface even though it's been demoted for normal queries.

**Failure mode — population distribution mismatch:** The critical failure mode is when the floor value is set relative to the document's own pre-penalty score, but the non-penalized population scores significantly higher than that floor. If the non-penalized corpus clusters at 0.95–1.05 and the floor for a fully-penalized document is 0.60×0.85 = 0.51, the penalized document ranks ~rank 500+ in a 746-document corpus — its "guaranteed visibility" exists only in an absolute sense, not a competitive one. The floor prevents the score from being 0.0, but provides no guarantee about the document's position in a ranking against non-penalized documents. A floor-based guarantee is only meaningful when the floor is calibrated relative to the score distribution of the non-penalized population, not just relative to the document's own pre-penalty score.

**Worked example:** `max(0.60 × extraction_confidence, compound_pre)`. The floor is proportional to `extraction_confidence`, not a global constant — a high-confidence extraction gets a higher floor than a low-confidence one. Empirically observed failure: with `extraction_confidence=1.0`, this floor = 0.60; but if the non-penalized population clusters at 0.98–1.03, the floor keeps the document away from score=0 without making it competitive.

**When to use:** When you want a penalized document class (superseded, deprecated, out-of-date) to remain retrievable by direct queries for that class (provenance / lineage queries), but you accept it will rank low relative to non-penalized documents on general queries. Appropriate when the retrieval use case is dual: one default-intent mode (where the floor passively keeps old content discoverable) and one explicit-lineage-intent mode (where the lineage query uses graph traversal rather than the score floor to surface the old document). If the lineage use case requires competitive ranking, a floor alone is insufficient — query-intent routing or separate retrieval paths are needed.

**Named pattern in the literature:** Not formally named in IR literature. The closest related concepts are "tiered indexes" (Manning, Raghavan & Schütze, IR book chapter 7) — where documents are organized into tiers by quality and retrieval falls back down tiers only when higher tiers are exhausted — and "score thresholds" in RAG (cosine similarity minimum below which documents are excluded entirely). The floor pattern inverts tiered-index logic: instead of including lower-tier documents only as fallback, it guarantees lower-tier documents always have a non-zero score. The floor concept also appears implicitly in probabilistic retrieval models where IDF ensures that even matched documents cannot score below a certain minimum.

**Comparison with ceiling (cap):**
```
score = min(cap_value, computed_score)
```
A ceiling prevents a very strong signal from dominating entirely. Ceilings are used in BM25's `k1` saturation (term frequency ceils at a maximum contribution) and in importance boost formulas. Floors and ceilings are dual: floor = "at least this"; ceiling = "at most this". They can be composed: `max(floor, min(cap, computed_score))` creates a bounded range.

---

## Normalization Methods

| Method | Formula | Properties | When to use |
|--------|---------|------------|-------------|
| **Min-max (within result set)** | `(x - min) / (max - min)` | Relative to current results; 0.5 if all equal | Calibrating signals within a single query's result set |
| **Min-max (global)** | `(x - global_min) / (global_max - global_min)` | Absolute, requires knowing distribution bounds | When you have stable distribution bounds |
| **Z-score** | `(x - μ) / σ` | Relative to historical distribution; unbounded output | When you have stable historical stats |
| **Percentile** | `rank(x) / N` | Robust to outliers; uniform output distribution | When outliers would distort min-max |
| **Sigmoid** | `1 / (1 + exp(-x))` | Fixed nonlinear mapping; no context needed | Unbounded model outputs (logits) |
