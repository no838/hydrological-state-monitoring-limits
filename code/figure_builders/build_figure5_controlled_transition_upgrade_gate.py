#!/usr/bin/env python3
"""Controlled-transition upgrade gate for the hydrological-state monitoring package.

This gate asks a narrow question: does the retained basin diagnostic table
support a scalar transition boundary, or is the current evidence better kept as
a smooth lag-persistence decay constraint? It deliberately does not read raw
provider data and therefore cannot close physical phase-transition language.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = PROJECT_ROOT / "outputs" / "xi_star_transition_operator_gate_2026-06-13" / "xi_star_results.csv"
DEFAULT_STRONGER_NULL = PROJECT_ROOT / "outputs" / "xi_star_lag_manifold_stronger_null_gate_2026-06-14"
DEFAULT_OUT = PROJECT_ROOT / "outputs" / "xi_star_controlled_transition_upgrade_gate_2026-06-14"

TARGET = "delta_i_over_persistence"
SOURCE = "source_family"
LAG_COLS = ["rho_lag_1", "rho_lag_2", "rho_lag_3", "rho_lag_7", "rho_lag_14", "rho_lag_30"]
LAGS = np.array([1, 2, 3, 7, 14, 30], dtype=float)


def complete_numeric(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    out = df.copy()
    for col in cols:
        out[col] = pd.to_numeric(out[col], errors="coerce")
    mask = np.isfinite(out[cols].to_numpy(float)).all(axis=1)
    return out.loc[mask].reset_index(drop=True)


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
    # Orient so higher score roughly means higher mean persistence.
    if np.corrcoef(score, lag_x.mean(axis=1))[0, 1] < 0:
        score = -score
    return score


def estimate_beta(lag_x: np.ndarray) -> np.ndarray:
    x = np.log1p(LAGS)
    X = np.column_stack([np.ones(len(x)), x])
    betas = []
    for row in lag_x:
        y = np.log(np.clip(np.abs(row), 1e-4, 0.999))
        coef, *_ = np.linalg.lstsq(X, y, rcond=None)
        betas.append(float(-coef[1]))
    return np.asarray(betas)


def build_control_candidates(df: pd.DataFrame) -> pd.DataFrame:
    lag_x = df[LAG_COLS].to_numpy(float)
    beta = estimate_beta(lag_x)
    short_mean = lag_x[:, :3].mean(axis=1)
    long_mean = lag_x[:, 4:].mean(axis=1)
    mid_mean = lag_x[:, 2:4].mean(axis=1)
    candidates = pd.DataFrame(
        {
            "gauge_id": df.get("gauge_id", pd.Series(range(len(df)))).astype(str).to_numpy(),
            SOURCE: df[SOURCE].astype(str).to_numpy(),
            TARGET: df[TARGET].to_numpy(float),
            "beta_log_lag_decay": beta,
            "chi_short_long_drop": lag_x[:, 0] - lag_x[:, -1],
            "kappa_pc1_persistence": lag_pca_score(lag_x),
            "memory_auc": lag_x.mean(axis=1),
            "mid_tail_curvature": short_mean - 2.0 * mid_mean + long_mean,
        }
    )
    return candidates


def scan_transition_for_variable(z_raw: np.ndarray, y: np.ndarray, sources: np.ndarray, min_side: int) -> list[dict]:
    z = standardize(z_raw)
    linear_r2 = r2_from_design(z[:, None], y)
    rows = []
    quantiles = np.arange(0.20, 0.81, 0.05)
    for q in quantiles:
        cut = float(np.quantile(z, q))
        left = z <= cut
        right = z > cut
        if int(left.sum()) < min_side or int(right.sum()) < min_side:
            continue
        left_sources = len(set(sources[left]))
        right_sources = len(set(sources[right]))
        hinge = np.maximum(0.0, z - cut)
        step = right.astype(float)
        hinge_r2 = r2_from_design(np.column_stack([z, hinge]), y)
        step_r2 = r2_from_design(np.column_stack([z, step]), y)
        best_kind, best_r2 = ("hinge", hinge_r2) if hinge_r2 >= step_r2 else ("step", step_r2)
        rows.append(
            {
                "threshold_quantile": q,
                "threshold_value_z": cut,
                "linear_r2": linear_r2,
                "hinge_r2": hinge_r2,
                "step_r2": step_r2,
                "best_transition_model": best_kind,
                "best_transition_r2": best_r2,
                "transition_gain_r2": best_r2 - linear_r2,
                "n_left": int(left.sum()),
                "n_right": int(right.sum()),
                "source_families_left": left_sources,
                "source_families_right": right_sources,
                "mean_y_left": float(np.mean(y[left])),
                "mean_y_right": float(np.mean(y[right])),
            }
        )
    return rows


def source_block_bootstrap_indices(sources: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    unique = np.array(sorted(set(sources)))
    sampled = rng.choice(unique, size=len(unique), replace=True)
    pieces = [np.where(sources == src)[0] for src in sampled]
    return np.concatenate(pieces)


def bootstrap_best_gain(candidates: pd.DataFrame, best_var: str, best_quantile: float, draws: int, seed: int) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    sources = candidates[SOURCE].astype(str).to_numpy()
    rows = []
    for draw in range(draws):
        idx = source_block_bootstrap_indices(sources, rng)
        sub = candidates.iloc[idx].reset_index(drop=True)
        y = sub[TARGET].to_numpy(float)
        z = standardize(sub[best_var].to_numpy(float))
        cut = float(np.quantile(z, best_quantile))
        left = z <= cut
        right = z > cut
        if left.sum() < 4 or right.sum() < 4:
            gain = float("nan")
        else:
            linear_r2 = r2_from_design(z[:, None], y)
            hinge = np.maximum(0.0, z - cut)
            step = right.astype(float)
            best_r2 = max(
                r2_from_design(np.column_stack([z, hinge]), y),
                r2_from_design(np.column_stack([z, step]), y),
            )
            gain = best_r2 - linear_r2
        rows.append({"draw": draw, "control_variable": best_var, "threshold_quantile": best_quantile, "transition_gain_r2": gain})
    return pd.DataFrame(rows)


def ar_decay_features(df: pd.DataFrame) -> np.ndarray:
    rho1 = np.clip(pd.to_numeric(df["rho1"], errors="coerce").to_numpy(float), -0.999, 0.999)
    vals = np.sign(rho1[:, None]) * (np.abs(rho1[:, None]) ** LAGS[None, :])
    return vals


def classify_decision(best_row: pd.Series, boot_ci: pd.Series, ar_smooth_r2: float) -> tuple[str, str]:
    support_ok = (
        int(best_row["n_left"]) >= 8
        and int(best_row["n_right"]) >= 8
        and int(best_row["source_families_left"]) >= 2
        and int(best_row["source_families_right"]) >= 2
    )
    gain = float(best_row["transition_gain_r2"])
    lower = float(boot_ci["ci05"])
    transition_r2 = float(best_row["best_transition_r2"])
    if support_ok and gain >= 0.08 and lower > 0.02 and transition_r2 >= ar_smooth_r2 + 0.03:
        return "CONTROLLED_TRANSITION_CANDIDATE_SUPPORTED", "transition_gain_survives_bootstrap_and_exceeds_ar_smooth"
    if support_ok and gain >= 0.05 and lower > 0.0:
        return "CONTROLLED_TRANSITION_CANDIDATE_SUPPORT_LIMITED", "transition_gain_positive_but_not_decisive_against_ar_smooth"
    return "SMOOTH_LAG_DECAY_CONSTRAINT_RETAINED", "transition_gain_insufficient_or_support_limited"


def run_gate(input_csv: Path, stronger_null_dir: Path, out_dir: Path, bootstrap_draws: int, seed: int) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    df0 = pd.read_csv(input_csv)
    required = [TARGET, SOURCE, "rho1", *LAG_COLS]
    df = complete_numeric(df0, [c for c in required if c != SOURCE])
    if SOURCE not in df.columns:
        raise ValueError(f"Missing {SOURCE}")
    if len(df) < 20:
        raise ValueError("Controlled-transition gate requires at least 20 complete basins")

    candidates = build_control_candidates(df)
    y = candidates[TARGET].to_numpy(float)
    sources = candidates[SOURCE].astype(str).to_numpy()
    control_cols = [c for c in candidates.columns if c not in {"gauge_id", SOURCE, TARGET}]

    scan_rows = []
    min_side = max(6, int(np.ceil(0.15 * len(candidates))))
    for col in control_cols:
        for row in scan_transition_for_variable(candidates[col].to_numpy(float), y, sources, min_side=min_side):
            row["control_variable"] = col
            scan_rows.append(row)
    scan = pd.DataFrame(scan_rows)
    if scan.empty:
        raise RuntimeError("No supported transition thresholds could be scanned")
    scan = scan.sort_values(["transition_gain_r2", "best_transition_r2"], ascending=False).reset_index(drop=True)
    best = scan.iloc[0]
    best_var = str(best["control_variable"])
    best_quantile = float(best["threshold_quantile"])

    boot = bootstrap_best_gain(candidates, best_var, best_quantile, bootstrap_draws, seed + 101)
    vals = boot["transition_gain_r2"].dropna().to_numpy(float)
    boot_ci = pd.Series(
        {
            "control_variable": best_var,
            "threshold_quantile": best_quantile,
            "n_valid_draws": int(len(vals)),
            "mean_gain": float(np.mean(vals)) if len(vals) else float("nan"),
            "ci05": float(np.quantile(vals, 0.05)) if len(vals) else float("nan"),
            "ci50": float(np.quantile(vals, 0.50)) if len(vals) else float("nan"),
            "ci95": float(np.quantile(vals, 0.95)) if len(vals) else float("nan"),
        }
    )

    ar_r2 = r2_from_design(ar_decay_features(df), df[TARGET].to_numpy(float))
    decision, reason = classify_decision(best, boot_ci, ar_r2)

    candidates.to_csv(out_dir / "control_variable_candidates.csv", index=False)
    scan.to_csv(out_dir / "transition_scan_table.csv", index=False)
    boot.to_csv(out_dir / "transition_bootstrap_draws.csv", index=False)
    pd.DataFrame([boot_ci]).to_csv(out_dir / "transition_bootstrap_ci.csv", index=False)

    summary = {
        "decision": decision,
        "decision_reason": reason,
        "input_csv": str(input_csv),
        "upstream_stronger_null_dir": str(stronger_null_dir),
        "n_basins": int(len(df)),
        "n_source_families": int(df[SOURCE].nunique()),
        "best_control_variable": best_var,
        "best_threshold_quantile": best_quantile,
        "best_threshold_value_z": float(best["threshold_value_z"]),
        "best_transition_model": str(best["best_transition_model"]),
        "best_linear_r2": float(best["linear_r2"]),
        "best_transition_r2": float(best["best_transition_r2"]),
        "best_transition_gain_r2": float(best["transition_gain_r2"]),
        "bootstrap_gain_ci05": float(boot_ci["ci05"]),
        "bootstrap_gain_ci50": float(boot_ci["ci50"]),
        "bootstrap_gain_ci95": float(boot_ci["ci95"]),
        "ar_style_smooth_r2": float(ar_r2),
        "support_left": int(best["n_left"]),
        "support_right": int(best["n_right"]),
        "source_families_left": int(best["source_families_left"]),
        "source_families_right": int(best["source_families_right"]),
    }
    (out_dir / "transition_decision_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    (out_dir / "input_manifest.json").write_text(
        json.dumps(
            {
                "input_csv": str(input_csv),
                "output_dir": str(out_dir),
                "bootstrap_draws": bootstrap_draws,
                "seed": seed,
                "target": TARGET,
                "source_family_column": SOURCE,
                "lag_columns": LAG_COLS,
                "scope": "basin_level_diagnostic_table_only",
                "datahub_lookup_status": "not_needed_for_new_acquisition; uses current project diagnostic authority",
            },
            indent=2,
        )
        + "\n"
    )

    allowed = (
        "- A controlled-transition candidate is supported only as a diagnostic screen on the retained basin table.\n"
        if decision == "CONTROLLED_TRANSITION_CANDIDATE_SUPPORTED"
        else "- The current evidence remains better described as a lag-persistence decay constraint.\n"
    )
    (out_dir / "claim_boundary.md").write_text(
        "# Controlled-transition upgrade claim boundary\n\n"
        f"Decision: `{decision}`\n\n"
        f"Reason: `{reason}`\n\n"
        "Allowed wording:\n\n"
        f"{allowed}"
        "- The gate compares scalar lag-derived control candidates against smooth AR-style lag decay.\n"
        "- Results are exploratory until raw-time-series spectrum-preserving or AR(p) surrogates are run.\n\n"
        "Blocked wording:\n\n"
        "- Do not claim a physical phase transition.\n"
        "- Do not claim a universal order parameter.\n"
        "- Do not claim causal mechanism closure.\n"
        "- Do not use this exploratory gate to alter files outside its output directory.\n"
    )

    (out_dir / "CONTROLLED_TRANSITION_UPGRADE_REPORT.md").write_text(
        "# Controlled-transition upgrade gate\n\n"
        f"Decision: `{decision}`\n\n"
        f"Reason: `{reason}`\n\n"
        "## Best transition screen\n\n"
        f"- best control variable: `{best_var}`\n"
        f"- threshold quantile: `{best_quantile:.2f}`\n"
        f"- transition model: `{best['best_transition_model']}`\n"
        f"- linear R2: `{float(best['linear_r2']):.4f}`\n"
        f"- transition R2: `{float(best['best_transition_r2']):.4f}`\n"
        f"- transition gain R2: `{float(best['transition_gain_r2']):.4f}`\n"
        f"- bootstrap gain CI05/50/95: `{float(boot_ci['ci05']):.4f}` / `{float(boot_ci['ci50']):.4f}` / `{float(boot_ci['ci95']):.4f}`\n"
        f"- AR-style smooth lag-decay R2: `{ar_r2:.4f}`\n\n"
        "## Interpretation\n\n"
        "This is a basin-level diagnostic screen. It can justify a controlled-transition candidate only when the scalar boundary beats a smooth lag-decay explanation with balanced source support. It cannot establish a physical phase transition without raw-time-series nulls.\n"
    )
    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-csv", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--stronger-null-dir", type=Path, default=DEFAULT_STRONGER_NULL)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--bootstrap-draws", type=int, default=999)
    parser.add_argument("--seed", type=int, default=20260614)
    args = parser.parse_args()
    summary = run_gate(args.input_csv, args.stronger_null_dir, args.out_dir, args.bootstrap_draws, args.seed)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
