# Stronger-null claim boundary

Decision: `LAG_MANIFOLD_STRONGER_NULL_SUPPORT_LIMITED`

Reason: `ar_decay_surrogate_recovers_large_share_of_lag_family_signal`

Allowed wording:

- The H1 single-proxy interpretation remains weaker than the lag-family comparator.
- The supported interpretation is H2b: a lag-persistence decay constraint.
- The richer H2a lag-manifold interpretation remains support-limited under the AR-style stronger null.
- This gate is evidence-level stronger-null hardening on the retained basin table.

Blocked wording:

- Do not claim full causal identification.
- Do not claim a physical phase transition.
- Do not claim xi-star is a universal control parameter.
- Do not claim raw-data-level spectrum-preserving validation unless raw Q(t) surrogates are run.

Remaining upgrade path:

1. Run raw-time-series spectrum-preserving and AR(p) surrogates if full causal/physical wording is desired.
2. Add an independent observed/cross-source boundary validation layer.
3. Keep Figure 5 as H1/H2a/H2b discrimination, not order-parameter discovery.
