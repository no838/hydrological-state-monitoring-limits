#!/usr/bin/env python3
"""Raw-hydrograph surrogate gate for the hydrological-state monitoring package.

This internal gate asks whether the controlled-transition candidate survives
raw daily streamflow nulls. It re-reads the daily files retained by the xi-star
operator gate, recomputes conditional state information gain from the real
hydrograph, and compares it with Q-only surrogates that preserve different
parts of the hydrograph structure.

It must not refresh paper, figures, or release-package artifacts.
"""

from __future__ import annotations

import argparse
import json
import math
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = PROJECT_ROOT / "outputs" / "xi_star_transition_operator_gate_2026-06-13" / "xi_star_results.csv"
DEFAULT_OUT = PROJECT_ROOT / "outputs" / "xi_star_raw_hydrograph_surrogate_gate_2026-06-14"

STATE_CANDIDATES = (
    "volumetric_soil_water_layer_1_mean",
    "volumetric_soil_water_layer_2_mean",
    "volumetric_soil_water_layer_3_mean",
    "volumetric_soil_water_layer_4_mean",
    "snow_depth_water_equivalent_mean",
    "total_precipitation_sum",
)
LAG_COLS = ["rho_lag_1", "rho_lag_2", "rho_lag_3", "rho_lag_7", "rho_lag_14", "rho_lag_30"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-csv", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--null-draws", type=int, default=199)
    parser.add_argument("--max-basins", type=int, default=0)
    parser.add_argument("--min-days", type=int, default=365)
    parser.add_argument("--bins", type=int, default=4)
    parser.add_argument("--block-size", type=int, default=30)
    parser.add_argument("--ar-order", type=int, default=3)
    parser.add_argument("--seed", type=int, default=20260614)
    return parser.parse_args()


def finite_series(values: object) -> pd.Series:
    return pd.to_numeric(pd.Series(values), errors="coerce").replace([np.inf, -np.inf], np.nan)


def digitize_quantile(series: pd.Series, bins: int) -> pd.Series:
    data = finite_series(series)
    out = pd.Series(np.nan, index=data.index)
    ok = data.notna()
    if ok.sum() < bins or data[ok].nunique() < 2:
        return out
    q = min(bins, int(data[ok].nunique()))
    out.loc[ok] = pd.qcut(data.loc[ok].rank(method="first"), q=q, duplicates="drop").cat.codes.astype(float)
    return out


def mutual_info_discrete(y: pd.Series, x: pd.Series) -> float:
    pair = pd.DataFrame({"y": y, "x": x}).dropna()
    if len(pair) < 20 or pair["y"].nunique() < 2 or pair["x"].nunique() < 2:
        return float("nan")
    total = float(len(pair))
    pxy = pair.groupby(["x", "y"]).size() / total
    px = pair.groupby("x").size() / total
    py = pair.groupby("y").size() / total
    value = 0.0
    for (xv, yv), prob in pxy.items():
        denom = px.loc[xv] * py.loc[yv]
        if prob > 0 and denom > 0:
            value += float(prob * math.log2(prob / denom))
    return value


def conditional_mi_discrete(y: pd.Series, x: pd.Series, z: pd.Series) -> float:
    frame = pd.DataFrame({"y": y, "x": x, "z": z}).dropna()
    if len(frame) < 30 or frame["y"].nunique() < 2 or frame["x"].nunique() < 2 or frame["z"].nunique() < 2:
        return float("nan")
    total = float(len(frame))
    value = 0.0
    for _, group in frame.groupby("z"):
        mi = mutual_info_discrete(group["y"], group["x"])
        if np.isfinite(mi):
            value += (len(group) / total) * mi
    return float(value)


def compute_delta_i(q: pd.Series, s: pd.Series, bins: int) -> tuple[float, int, int]:
    frame = pd.DataFrame({"q": finite_series(q), "s": finite_series(s)}).dropna().reset_index(drop=True)
    frame = frame[frame["q"] >= 0.0].reset_index(drop=True)
    if len(frame) < 120:
        return float("nan"), int(len(frame)), 0
    q90 = frame["q"].quantile(0.90)
    frame["event"] = (frame["q"] >= q90).astype(int)
    frame["q_lag1_bin"] = digitize_quantile(frame["q"].shift(1), bins)
    frame["s_lag1_bin"] = digitize_quantile(frame["s"].shift(1), bins)
    complete = frame[["event", "s_lag1_bin", "q_lag1_bin"]].dropna()
    events = int(complete["event"].sum()) if not complete.empty else 0
    if len(complete) < 80 or events < 8:
        return float("nan"), int(len(complete)), events
    return conditional_mi_discrete(complete["event"], complete["s_lag1_bin"], complete["q_lag1_bin"]), int(len(complete)), events


def select_state_column(df: pd.DataFrame, preferred: str | None) -> str | None:
    if preferred and preferred in df.columns and finite_series(df[preferred]).notna().sum() >= 120:
        return preferred
    for col in STATE_CANDIDATES:
        if col in df.columns and finite_series(df[col]).notna().sum() >= 120:
            return col
    return None


def prepare_daily_frame(path: Path, state_column: str | None, min_days: int) -> tuple[pd.DataFrame | None, str | None, str]:
    try:
        df = pd.read_csv(path)
    except Exception as exc:
        return None, None, f"read_failed:{str(exc)[:120]}"
    if "date" not in df.columns or "streamflow" not in df.columns:
        return None, None, "missing_date_or_streamflow"
    s_col = select_state_column(df, state_column)
    if s_col is None:
        return None, None, "missing_state_column"
    out = pd.DataFrame(
        {
            "date": pd.to_datetime(df["date"], errors="coerce"),
            "q": finite_series(df["streamflow"]),
            "s": finite_series(df[s_col]),
        }
    ).dropna().sort_values("date").reset_index(drop=True)
    out = out[out["q"] >= 0.0].reset_index(drop=True)
    if len(out) < min_days:
        return None, s_col, "too_few_days"
    return out, s_col, "ok"


def rank_remap(reference: np.ndarray, simulated: np.ndarray) -> np.ndarray:
    order = np.argsort(np.argsort(simulated, kind="mergesort"), kind="mergesort")
    sorted_ref = np.sort(reference)
    return sorted_ref[np.clip(order, 0, len(sorted_ref) - 1)]


def ar_p_surrogate(q: pd.Series, rng: np.random.Generator, order: int) -> pd.Series:
    x = finite_series(q).interpolate(limit_direction="both").to_numpy(dtype=float)
    if len(x) < order + 20 or np.nanstd(x) <= 0:
        return pd.Series(x, index=q.index)
    y = x[order:]
    X = np.column_stack([x[order - lag : len(x) - lag] for lag in range(1, order + 1)])
    X = np.column_stack([np.ones(len(X)), X])
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    resid = y - X @ beta
    sigma = float(np.nanstd(resid)) if np.nanstd(resid) > 0 else float(np.nanstd(x) * 0.1)
    sim = np.empty_like(x)
    sim[:order] = x[:order]
    for i in range(order, len(sim)):
        pred = beta[0] + sum(beta[lag] * sim[i - lag] for lag in range(1, order + 1))
        sim[i] = pred + rng.normal(0.0, sigma)
    return pd.Series(rank_remap(x, sim), index=q.index)


def phase_randomized_surrogate(q: pd.Series, rng: np.random.Generator) -> pd.Series:
    x = finite_series(q).interpolate(limit_direction="both").to_numpy(dtype=float)
    if len(x) < 32 or np.nanstd(x) <= 0:
        return pd.Series(x, index=q.index)
    centered = x - np.nanmean(x)
    spectrum = np.fft.rfft(centered)
    randomized = spectrum.copy()
    if len(randomized) > 2:
        phases = rng.uniform(0.0, 2.0 * math.pi, size=len(randomized) - 2)
        randomized[1:-1] = np.abs(spectrum[1:-1]) * np.exp(1j * phases)
    sim = np.fft.irfft(randomized, n=len(centered)) + np.nanmean(x)
    return pd.Series(rank_remap(x, sim), index=q.index)


def block_shuffle_surrogate(q: pd.Series, rng: np.random.Generator, block_size: int) -> pd.Series:
    x = finite_series(q).to_numpy(dtype=float)
    blocks = [x[i : i + block_size] for i in range(0, len(x), block_size)]
    order = rng.permutation(len(blocks))
    sim = np.concatenate([blocks[i] for i in order])
    return pd.Series(sim[: len(x)], index=q.index)


def standardize(x: np.ndarray) -> np.ndarray:
    x = x.astype(float)
    sd = float(np.nanstd(x))
    if not np.isfinite(sd) or sd == 0:
        return np.zeros_like(x)
    return (x - float(np.nanmean(x))) / sd


def lag_pca_score(lag_x: np.ndarray) -> np.ndarray:
    xz = np.column_stack([standardize(lag_x[:, i]) for i in range(lag_x.shape[1])])
    _, _, vt = np.linalg.svd(xz, full_matrices=False)
    score = xz @ vt[0].T
    if np.corrcoef(score, lag_x.mean(axis=1))[0, 1] < 0:
        score = -score
    return score


def r2_from_design(design: np.ndarray, y: np.ndarray) -> float:
    mask = np.isfinite(y) & np.isfinite(design).all(axis=1)
    if mask.sum() < design.shape[1] + 2:
        return float("nan")
    X0 = design[mask].astype(float)
    y0 = y[mask].astype(float)
    X = np.column_stack([np.ones(len(X0)), X0])
    beta, *_ = np.linalg.lstsq(X, y0, rcond=None)
    pred = X @ beta
    ss_res = float(np.sum((y0 - pred) ** 2))
    ss_tot = float(np.sum((y0 - y0.mean()) ** 2))
    return max(0.0, 1.0 - ss_res / ss_tot) if ss_tot else 0.0


def transition_gain(y: np.ndarray, z_raw: np.ndarray, threshold_quantile: float = 0.5) -> tuple[float, float, float, int, int]:
    z = standardize(z_raw)
    mask = np.isfinite(y) & np.isfinite(z)
    y0 = y[mask]
    z0 = z[mask]
    if len(y0) < 8:
        return float("nan"), float("nan"), float("nan"), 0, 0
    cut = float(np.quantile(z0, threshold_quantile))
    right = z0 > cut
    left = ~right
    if left.sum() < 3 or right.sum() < 3:
        return float("nan"), float("nan"), float("nan"), int(left.sum()), int(right.sum())
    linear = r2_from_design(z0[:, None], y0)
    hinge = np.maximum(0.0, z0 - cut)
    step = right.astype(float)
    trans = max(r2_from_design(np.column_stack([z0, hinge]), y0), r2_from_design(np.column_stack([z0, step]), y0))
    return trans - linear, linear, trans, int(left.sum()), int(right.sum())


def build_control_table(input_df: pd.DataFrame) -> pd.DataFrame:
    df = input_df.copy()
    for col in LAG_COLS:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    lag_x = df[LAG_COLS].to_numpy(float)
    df["kappa_pc1_persistence"] = lag_pca_score(lag_x)
    df["memory_auc"] = np.nanmean(lag_x, axis=1)
    return df


def run_gate(args: argparse.Namespace) -> dict:
    out_dir = args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    input_df = pd.read_csv(args.input_csv)
    required = {"gauge_id", "source_family", "input_path", *LAG_COLS}
    missing = sorted(required.difference(input_df.columns))
    if missing:
        raise ValueError(f"Missing required columns: {missing}")
    input_df = build_control_table(input_df)
    if args.max_basins and len(input_df) > args.max_basins:
        input_df = input_df.head(args.max_basins).copy()
    rng = np.random.default_rng(args.seed)
    per_basin_rows: list[dict[str, object]] = []
    audit_rows: list[dict[str, object]] = []
    null_families = ("ar_p_rank_preserving", "phase_randomized_rank_preserving", "block_shuffle")
    for _, row in input_df.iterrows():
        gauge_id = str(row["gauge_id"])
        path = Path(str(row["input_path"]))
        daily, state_col, status = prepare_daily_frame(path, str(row.get("state_column", "")), args.min_days)
        if daily is None:
            audit_rows.append({"gauge_id": gauge_id, "source_family": row["source_family"], "input_path": str(path), "status": status})
            continue
        observed, n_rows, events = compute_delta_i(daily["q"], daily["s"], args.bins)
        base = {
            "gauge_id": gauge_id,
            "source_family": str(row["source_family"]),
            "input_path": str(path),
            "state_column_used": state_col,
            "complete_days": int(len(daily)),
            "analysis_rows": n_rows,
            "event_count": events,
            "kappa_pc1_persistence": float(row["kappa_pc1_persistence"]),
            "memory_auc": float(row["memory_auc"]),
            "observed_delta_i": observed,
        }
        per_basin_rows.append({**base, "null_family": "observed", "draw": -1, "delta_i": observed})
        for family in null_families:
            for draw in range(args.null_draws):
                if family == "ar_p_rank_preserving":
                    q_null = ar_p_surrogate(daily["q"], rng, args.ar_order)
                elif family == "phase_randomized_rank_preserving":
                    q_null = phase_randomized_surrogate(daily["q"], rng)
                elif family == "block_shuffle":
                    q_null = block_shuffle_surrogate(daily["q"], rng, args.block_size)
                else:  # pragma: no cover
                    raise ValueError(family)
                delta_i, rows_used, event_count = compute_delta_i(q_null, daily["s"], args.bins)
                per_basin_rows.append(
                    {
                        **base,
                        "analysis_rows": rows_used,
                        "event_count": event_count,
                        "null_family": family,
                        "draw": draw,
                        "delta_i": delta_i,
                    }
                )
        audit_rows.append({"gauge_id": gauge_id, "source_family": row["source_family"], "input_path": str(path), "status": "retained"})
    per_basin = pd.DataFrame(per_basin_rows)
    audit = pd.DataFrame(audit_rows)
    per_basin.to_csv(out_dir / "per_basin_surrogate_delta_i.csv", index=False)
    audit.to_csv(out_dir / "input_file_audit.csv", index=False)
    observed = per_basin[per_basin["null_family"] == "observed"].copy()
    observed = observed[np.isfinite(pd.to_numeric(observed["delta_i"], errors="coerce"))].reset_index(drop=True)
    n_basins = int(len(observed))
    n_families = int(observed["source_family"].nunique()) if n_basins else 0
    obs_gain, obs_linear, obs_transition, left_n, right_n = transition_gain(
        observed["delta_i"].to_numpy(float), observed["kappa_pc1_persistence"].to_numpy(float), 0.5
    )
    summary_rows = []
    contrast_rows = []
    for family in null_families:
        fam = per_basin[per_basin["null_family"] == family].copy()
        null_means = fam.groupby("gauge_id")["delta_i"].mean()
        obs_by_basin = observed.set_index("gauge_id")["delta_i"]
        joined = pd.DataFrame({"observed": obs_by_basin, "null_mean": null_means}).dropna()
        gains = []
        for draw, sub in fam.groupby("draw"):
            merged = observed[["gauge_id", "kappa_pc1_persistence"]].merge(
                sub[["gauge_id", "delta_i"]], on="gauge_id", how="inner"
            )
            gain, linear, transition, _, _ = transition_gain(
                merged["delta_i"].to_numpy(float), merged["kappa_pc1_persistence"].to_numpy(float), 0.5
            )
            gains.append({"null_family": family, "draw": int(draw), "null_transition_gain_r2": gain, "null_linear_r2": linear, "null_transition_r2": transition})
        gain_df = pd.DataFrame(gains)
        contrast_rows.extend(gains)
        valid_gains = gain_df["null_transition_gain_r2"].dropna().to_numpy(float) if not gain_df.empty else np.array([])
        summary_rows.append(
            {
                "null_family": family,
                "n_draws": int(len(valid_gains)),
                "observed_mean_delta_i": float(observed["delta_i"].mean()) if n_basins else float("nan"),
                "null_mean_delta_i": float(fam["delta_i"].mean()) if len(fam) else float("nan"),
                "mean_observed_minus_null": float((joined["observed"] - joined["null_mean"]).mean()) if len(joined) else float("nan"),
                "share_basins_observed_gt_null_mean": float((joined["observed"] > joined["null_mean"]).mean()) if len(joined) else float("nan"),
                "observed_transition_gain_r2": obs_gain,
                "null_gain_ci50": float(np.quantile(valid_gains, 0.50)) if len(valid_gains) else float("nan"),
                "null_gain_ci95": float(np.quantile(valid_gains, 0.95)) if len(valid_gains) else float("nan"),
                "observed_exceeds_null_ci95": bool(np.isfinite(obs_gain) and len(valid_gains) and obs_gain > np.quantile(valid_gains, 0.95)),
            }
        )
    family_summary = pd.DataFrame(summary_rows)
    contrast = pd.DataFrame(contrast_rows)
    family_summary.to_csv(out_dir / "null_family_summary.csv", index=False)
    contrast.to_csv(out_dir / "transition_surrogate_contrast.csv", index=False)
    max_null_mean = float(family_summary["null_mean_delta_i"].max()) if not family_summary.empty else float("nan")
    all_mean_positive = bool((family_summary["mean_observed_minus_null"] > 0).all()) if not family_summary.empty else False
    all_gt_ci95 = bool(family_summary["observed_exceeds_null_ci95"].all()) if not family_summary.empty else False
    all_gt_median = bool((family_summary["observed_transition_gain_r2"] > family_summary["null_gain_ci50"]).all()) if not family_summary.empty else False
    if n_basins < 8 or n_families < 2:
        decision = "RAW_HYDROGRAPH_SURROGATE_GATE_NOT_READY"
        reason = "support_too_small"
    elif all_mean_positive and all_gt_ci95:
        decision = "RAW_HYDROGRAPH_SURROGATE_TRANSITION_SUPPORTED"
        reason = "observed_delta_i_and_transition_gain_exceed_raw_q_surrogates"
    elif all_mean_positive and all_gt_median:
        decision = "RAW_HYDROGRAPH_SURROGATE_SUPPORT_LIMITED"
        reason = "observed_delta_i_positive_but_transition_not_above_all_strong_null_tails"
    else:
        decision = "RAW_HYDROGRAPH_SURROGATE_NOT_REJECTED"
        reason = "q_only_surrogates_can_match_or_exceed_observed_structure"
    decision_summary = {
        "decision": decision,
        "decision_reason": reason,
        "input_csv": str(args.input_csv),
        "n_basins": n_basins,
        "n_source_families": n_families,
        "null_draws_per_family": args.null_draws,
        "observed_mean_delta_i": float(observed["delta_i"].mean()) if n_basins else float("nan"),
        "max_null_mean_delta_i": max_null_mean,
        "observed_transition_gain_r2": obs_gain,
        "observed_linear_r2": obs_linear,
        "observed_transition_r2": obs_transition,
        "support_left": left_n,
        "support_right": right_n,
        "all_null_families_mean_positive": all_mean_positive,
        "all_null_families_transition_gt_ci95": all_gt_ci95,
        "all_null_families_transition_gt_median": all_gt_median,
    }
    (out_dir / "raw_hydrograph_surrogate_decision_summary.json").write_text(json.dumps(decision_summary, indent=2), encoding="utf-8")
    manifest = {
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "purpose": "raw daily hydrograph surrogate gate for controlled-transition upgrade",
        "input_csv": str(args.input_csv),
        "out_dir": str(out_dir),
        "null_families": list(null_families),
        "null_draws": args.null_draws,
        "min_days": args.min_days,
        "bins": args.bins,
        "block_size": args.block_size,
        "ar_order": args.ar_order,
        "seed": args.seed,
        "decision": decision,
        "claim_boundary": "exploratory gate only; does not alter files outside its output directory",
    }
    (out_dir / "input_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    boundary = f"""# Claim boundary

Decision: `{decision}`

Reason: `{reason}`

Allowed wording:

- Raw daily hydrograph surrogates were used as a stronger internal null for the controlled-transition upgrade.
- The gate tests whether observed conditional state information and its transition-like organization exceed Q-only AR(p), phase-randomized and block-shuffled hydrographs.
- Results are limited to the retained Caravan daily subset from the xi-star operator route.

Blocked wording:

- Do not call this a physical phase transition.
- Do not call this a universal order parameter.
- Do not call this causal mechanism closure.
- Do not use this gate to alter files outside its output directory.
"""
    (out_dir / "claim_boundary.md").write_text(boundary, encoding="utf-8")
    report = f"""# Raw hydrograph surrogate gate

## Decision

`{decision}`

## Question

Does the controlled-transition candidate survive raw daily Q-only surrogate
nulls that preserve autocorrelation, spectrum or block persistence?

## Null families

- `ar_p_rank_preserving`
- `phase_randomized_rank_preserving`
- `block_shuffle`

## Key metrics

- basins retained: `{n_basins}`
- source families retained: `{n_families}`
- observed mean delta I: `{decision_summary['observed_mean_delta_i']}`
- maximum null mean delta I: `{decision_summary['max_null_mean_delta_i']}`
- observed transition gain R2: `{obs_gain}`
- observed transition R2: `{obs_transition}`
- observed linear R2: `{obs_linear}`

## Interpretation boundary

This gate is stronger than the basin-table transition screen because it reuses
the raw daily hydrographs. It is still an internal Caravan-subset gate and
cannot replace GRDC observed-flow validation or support causal/phase-transition
language by itself.
"""
    (out_dir / "RAW_HYDROGRAPH_SURROGATE_REPORT.md").write_text(report, encoding="utf-8")
    return decision_summary


def main() -> None:
    args = parse_args()
    summary = run_gate(args)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
