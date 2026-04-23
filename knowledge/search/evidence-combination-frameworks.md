# Evidence Combination Frameworks

Formal mathematical foundations for combining evidence from multiple sources into confidence scores. These frameworks exist because ad-hoc weighted sums fail on conflicting evidence, path-dependent accumulation, and edge cases where "more data ≠ more confidence."

**Primary use case:** Confidence evolution for synthesized observations in Neuroloom's dreaming pipeline. Also applicable to any scoring formula that combines evidence from multiple graph signals.

---

## The Problem with Ad-Hoc Approaches

### Simple Delta Model (Hindsight's approach)
```
confidence += α          # supporting evidence
confidence -= α          # weakening evidence
confidence -= 2α         # contradicting evidence
```

**Why it fails:**
- **Path-dependent:** The order evidence arrives changes the final score. 3 supports then 1 contradiction ≠ 1 contradiction then 3 supports.
- **No convergence guarantee:** Confidence can oscillate indefinitely if supporting and contradicting evidence alternate.
- **Can't weight evidence by quality:** A high-confidence SUPERSEDES edge from a structurally central memory counts the same as a weak SIMILAR_TO edge from a peripheral memory.
- **Unbounded accumulation:** Without capping, confidence can exceed [0,1] bounds. With capping, information is lost at the boundaries.

### Intuitive Weighted Sum
```
confidence = w1×density + w2×avg_edge_confidence + w3×source_strength + w4×evidence_factor
```

**Why it's better than deltas but still limited:**
- Weights are chosen by intuition, not derived from the signal properties
- Can't represent uncertainty (a score of 0.5 could mean "half confident" or "haven't seen enough evidence")
- All evidence is positive — the formula monotonically increases with more data unless polarity is explicitly modeled

---

## Framework 1: Dempster-Shafer Theory (Evidence Theory)

**Core idea:** Instead of a single confidence number, maintain a belief interval [Bel, Pl] where:
- **Bel (belief)** = minimum confidence given the evidence (lower bound)
- **Pl (plausibility)** = maximum confidence if all uncertain evidence supports the claim (upper bound)
- **Uncertainty** = Pl - Bel (shrinks as evidence accumulates)

### How it works
Each evidence source (graph edge) assigns a mass function:
```
m({true}) = probability this evidence supports the observation
m({false}) = probability this evidence contradicts the observation
m({true, false}) = uncertainty (evidence is ambiguous)
```

Evidence is combined via **Dempster's rule of combination:**
```
m_combined(A) = (1/K) × Σ m1(B)×m2(C)  for all B∩C=A
K = 1 - Σ m1(B)×m2(C)  for all B∩C=∅  (normalization factor for conflict)
```

### Mapping to Neuroloom
- Each graph edge → one evidence source
- Supporting edges (SIMILAR_TO, REFERENCES, VALIDATES): high m({true}), low m({false})
- Contradicting edges (CONTRADICTS, SUPERSEDES): high m({false}), low m({true})
- Neutral edges (CAUSED_BY, RELATED_TO): high m({true, false}) — contributes uncertainty reduction without directional signal
- Edge confidence → scales the mass assignment (high-confidence edge has lower uncertainty)
- PageRank of source memory → modulates the reliability of the evidence source

### When to use
- When you need to represent and track **uncertainty** separately from confidence
- When evidence sources have varying reliability (edge confidence, source PageRank)
- When you need to detect **high conflict** (K approaching 1 means evidence strongly disagrees — flag for review)

### Limitations
- More complex to implement and explain than a single score
- Dempster's rule can produce counterintuitive results when evidence sources are highly correlated (which graph edges may be, since they share source memories)
- The belief interval may be harder to use as a ranking signal than a single number

---

## Framework 2: Bayesian Updating

**Core idea:** Start with a prior (initial confidence from the LLM at synthesis time). Each new piece of evidence updates the posterior via Bayes' rule.

### How it works
```
P(H|E) = P(E|H) × P(H) / P(E)

posterior = likelihood × prior / evidence
```

For each new edge:
```
# Supporting edge
P(observation_true | supporting_edge) ∝ P(supporting_edge | true) × P(true)

# Contradicting edge
P(observation_true | contradicting_edge) ∝ P(contradicting_edge | true) × P(true)
```

### Simplified log-odds form
```
log_odds = log(P/(1-P))

# Each evidence updates:
log_odds_new = log_odds_old + log_likelihood_ratio

# Convert back:
confidence = 1 / (1 + exp(-log_odds_new))
```

The log-likelihood ratio for each edge type:
- Supporting edge: positive (magnitude scaled by edge confidence)
- Contradicting edge: negative (magnitude scaled by edge confidence)
- Neutral edge: zero (no update)

### Mapping to Neuroloom
- Prior: LLM-assigned confidence at synthesis time (e.g., 0.6)
- Each nightly dreaming cycle processes new/changed edges
- Log-likelihood ratios per edge type can be calibrated empirically
- Final confidence is sigmoid(log_odds) — naturally bounded to [0,1]

### When to use
- When you have a meaningful prior (LLM synthesis provides this)
- When evidence arrives incrementally (nightly dreaming cycle)
- When you want a single number (not an interval) that naturally stays in [0,1]

### Limitations
- Assumes evidence sources are independent (graph edges sharing source memories violates this)
- Requires defining likelihood ratios per edge type (needs calibration or expert judgment)
- Prior choice matters — a strong prior resists evidence. A weak prior (0.5) is maximally uncertain.

---

## Framework 3: Signal-to-Noise Ratio

**Core idea:** Treat supporting evidence as signal and contradicting evidence as noise. Confidence is the ratio of signal to total.

### How it works
```
signal = Σ (supporting_edge_confidence × source_pagerank)
noise  = Σ (contradicting_edge_confidence × source_pagerank)
SNR    = signal / (signal + noise)
```

### Enhanced version with density
```
confidence = SNR × density_factor × evidence_saturation

where:
  SNR = signal / (signal + noise)                    # [0, 1]
  density_factor = actual_edges / max_possible_edges  # [0, 1]
  evidence_saturation = tanh(evidence_count × scale)  # [0, 1), diminishing returns
```

### Mapping to Neuroloom
- Supporting edges: SIMILAR_TO, REFERENCES, VALIDATES, EXEMPLIFIES → signal
- Contradicting edges: CONTRADICTS, SUPERSEDES → noise
- Neutral edges: CAUSED_BY, LEADS_TO, RELATED_TO → contribute to density_factor but not SNR
- Edge confidence × source PageRank → weighted contribution to signal or noise
- Evidence saturation via tanh prevents unbounded accumulation

### When to use
- When simplicity and interpretability matter most
- When you need to explain exactly why confidence changed ("3 supporting edges with avg confidence 0.8 vs 1 contradicting edge with confidence 0.9")
- As a starting point before considering more complex frameworks

### Limitations
- No notion of uncertainty (SNR=0.5 could mean "balanced evidence" or "no evidence")
- Neutral edges are excluded from the core ratio — they only affect density
- Doesn't handle evidence reliability beyond the PageRank weighting

---

## Choosing a Framework

| Factor | Dempster-Shafer | Bayesian | SNR |
|--------|----------------|----------|-----|
| **Represents uncertainty** | Yes (belief interval) | Partially (wide credible interval with weak prior) | No |
| **Handles conflicting evidence** | Yes (conflict detection via K) | Yes (opposing likelihoods) | Yes (signal vs noise) |
| **Implementation complexity** | High | Medium | Low |
| **Interpretability** | Medium (intervals) | Medium (log-odds updates) | High (ratio) |
| **Requires prior** | No | Yes (LLM synthesis provides one) | No |
| **Incremental update** | Yes (combine new evidence) | Yes (update posterior) | Yes (recompute ratio) |
| **Path-independent** | Yes (combination is commutative) | Yes (multiplication is commutative) | Yes (sum is commutative) |
| **Evidence quality weighting** | Via mass function reliability | Via likelihood ratio magnitude | Via edge confidence × PageRank |

### Recommendation for Neuroloom
Start with **SNR** for the initial confidence evolution implementation — it's the simplest, most interpretable, and directly maps to our edge type polarity. The polarity-aware formula from the architecture discussion is essentially a weighted SNR with density and saturation factors.

If we later need to represent uncertainty (e.g., "we have confidence 0.7 but the evidence is thin" vs "we have confidence 0.7 with overwhelming evidence"), upgrade to **Bayesian** or **Dempster-Shafer**. The SNR formula can be viewed as a special case of Bayesian with a flat prior, so the upgrade path is smooth.
