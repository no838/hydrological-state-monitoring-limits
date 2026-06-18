# Xi-star / lag-manifold stronger-null hardening report

Decision: `LAG_MANIFOLD_STRONGER_NULL_SUPPORT_LIMITED`

Reason: `ar_decay_surrogate_recovers_large_share_of_lag_family_signal`

## Observed benchmarks

- Basins: `39`
- Source families: `5`
- R2 lag-family full: `0.6509`
- R2 lag-family PC90: `0.4780`
- R2 xi-star single proxy: `0.1921`
- R2 AR-style lag-decay surrogate: `0.6902`
- AR-style / lag-family ratio: `1.0604`
- Lag manifold PC90 dimension: `1`
- Lag manifold PC95 dimension: `2`

## Null interpretation

The nulls preserve different nuisance structures: source-family support, source-block composition and lag-feature covariance. They are stronger than plain random shuffles but remain evidence-level nulls because they operate on the retained basin diagnostic table rather than on raw daily hydrographs.

## Files

- `observed_benchmark_table.csv`
- `stronger_null_draws.csv`
- `stronger_null_summary.csv`
- `lag_pca_dimension_table.csv`
- `decision_summary.json`
