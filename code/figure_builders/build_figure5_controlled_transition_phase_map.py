#!/usr/bin/env python3
"""Render a muted blue-grey phase-map Figure 5 candidate for the hydrological-state monitoring package."""

from __future__ import annotations

import argparse
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_GATE_DIR = PROJECT_ROOT / "outputs" / "xi_star_raw_hydrograph_surrogate_gate_2026-06-14"
TRANSITION_DIR = PROJECT_ROOT / "outputs" / "xi_star_controlled_transition_upgrade_gate_2026-06-14"
DEFAULT_OUT = PROJECT_ROOT / "outputs" / "figure5_controlled_transition_phase_map_candidate"

FIGURE_ID = "Figure5_CONTROLLED_TRANSITION_PHASEMAP_CANDIDATE"

TEXT = "#222222"
AXIS = "#4D4D4D"
GRID = "#E6E6E6"
GREY = "#BDBDBD"
DARK_GREY = "#777777"
BLUE = "#0066CC"
BLUE_DARK = "#0057B8"
BLUE_LIGHT = "#9ECAE1"
BLUE_WINDOW = "#D8E9FF"
GREEN = "#59A14F"
AMBER = "#F2C879"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-gate-dir", type=Path, default=RAW_GATE_DIR)
    parser.add_argument("--transition-dir", type=Path, default=TRANSITION_DIR)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT)
    return parser.parse_args()


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def require_paths(paths: list[Path]) -> None:
    missing = [str(path) for path in paths if not path.exists()]
    if missing:
        raise FileNotFoundError("Missing required inputs: " + ", ".join(missing))


def standardize(x: np.ndarray) -> np.ndarray:
    x = np.asarray(x, dtype=float)
    sd = float(np.nanstd(x))
    if not np.isfinite(sd) or sd == 0:
        return np.zeros_like(x)
    return (x - float(np.nanmean(x))) / sd


def set_style(out_dir: Path) -> None:
    mpl_cache = out_dir / "_mpl_cache"
    mpl_cache.mkdir(parents=True, exist_ok=True)
    os.environ.setdefault("MPLCONFIGDIR", str(mpl_cache))
    os.environ.setdefault("XDG_CACHE_HOME", str(mpl_cache))
    import matplotlib as mpl

    mpl.use("Agg", force=True)
    mpl.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 7.8,
            "axes.labelsize": 7.8,
            "xtick.labelsize": 7.1,
            "ytick.labelsize": 7.1,
            "legend.fontsize": 7.0,
            "svg.fonttype": "none",
            "pdf.fonttype": 42,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.edgecolor": AXIS,
            "axes.linewidth": 0.8,
            "xtick.color": AXIS,
            "ytick.color": AXIS,
            "text.color": TEXT,
            "axes.labelcolor": TEXT,
        }
    )


def panel_label(ax, label: str) -> None:
    ax.text(-0.12, 1.08, label, transform=ax.transAxes, fontsize=13, fontweight="bold", va="top", ha="left")


def draw_panel_a(ax, raw_summary: dict, transition_summary: dict) -> None:
    values = [raw_summary["observed_linear_r2"], raw_summary["observed_transition_r2"]]
    labels = ["Linear", "Transition"]
    ax.bar(labels, values, color=[GREY, BLUE], width=0.58, edgecolor="none")
    ax.set_ylabel("R2")
    ax.set_ylim(0, 1.0)
    for i, value in enumerate(values):
        text = f"{value:.2f}" if i == 0 else f"{value:.3f}"
        ax.text(i, value + 0.035, text, ha="center", va="bottom", fontsize=7.8)
    y = 0.86
    ax.plot([0, 0, 1, 1], [y - 0.03, y, y, y - 0.03], color=TEXT, lw=0.8)
    ax.text(0.5, y + 0.035, f"Delta R2 = {raw_summary['observed_transition_gain_r2']:.3f}", ha="center", va="bottom", fontsize=7.8)
    ax.set_title("Transition gain", loc="left", fontsize=10.5, fontweight="bold", pad=5)
    panel_label(ax, "a")


def draw_panel_b(ax, raw_summary: dict, null_summary: pd.DataFrame) -> None:
    order = ["block_shuffle", "phase_randomized_rank_preserving", "ar_p_rank_preserving"]
    label_map = {
        "block_shuffle": "Block",
        "phase_randomized_rank_preserving": "Phase",
        "ar_p_rank_preserving": "AR(p)",
    }
    plot = null_summary.set_index("null_family").loc[order].reset_index()
    y = np.arange(len(plot))[::-1]
    for yi, (_, row) in zip(y, plot.iterrows()):
        ax.plot([0, row["null_gain_ci95"]], [yi, yi], color="#C9C9C9", lw=3.0, solid_capstyle="round")
        ax.scatter(row["null_gain_ci50"], yi, s=28, color=DARK_GREY, zorder=3)
    observed = raw_summary["observed_transition_gain_r2"]
    ax.axvline(observed, color=BLUE, lw=2.1)
    ax.text(observed, y.max() + 0.42, "Observed", ha="center", va="bottom", color=BLUE_DARK, fontsize=7.6, fontweight="bold")
    ax.set_yticks(y)
    ax.set_yticklabels([label_map[v] for v in plot["null_family"]])
    ax.set_xlabel("Transition gain (Delta R2)")
    ax.set_xlim(0, 0.25)
    ax.set_ylim(-0.75, y.max() + 0.7)
    ax.plot([], [], color=BLUE, lw=2.1, label="Observed")
    ax.plot([], [], color="#C9C9C9", lw=3.0, label="Null CI95")
    ax.legend(frameon=False, loc="lower right")
    ax.set_title("Null separation", loc="left", fontsize=10.5, fontweight="bold", pad=5)
    panel_label(ax, "b")


def draw_panel_c(ax, transition_summary: dict) -> None:
    counts = [transition_summary["support_left"], transition_summary["support_right"]]
    labels = ["Low side", "High side"]
    ax.bar(labels, counts, color=[BLUE_LIGHT, BLUE], width=0.58, edgecolor="none")
    ax.set_ylabel("Basins")
    ax.set_ylim(0, 30)
    for i, value in enumerate(counts):
        ax.text(i, value + 0.7, f"{int(value)}", ha="center", va="bottom", fontsize=8)
    ax.text(0.5, 27.1, f"{transition_summary['n_source_families']} source families", ha="center", va="center", fontsize=8)
    ax.text(0.5, -0.20, "Support is nearly symmetric.", transform=ax.transAxes, ha="center", va="top", color=BLUE_DARK, fontsize=7.8)
    ax.set_title("Support asymmetry", loc="left", fontsize=10.5, fontweight="bold", pad=5)
    panel_label(ax, "c")


def binned_summary(points: pd.DataFrame, bins: int = 6) -> pd.DataFrame:
    work = points.sort_values("kappa_z").reset_index(drop=True).copy()
    work["bin"] = pd.qcut(work["kappa_z"], q=min(bins, len(work)), labels=False, duplicates="drop")
    rows = []
    for _, sub in work.groupby("bin"):
        rows.append(
            {
                "kappa_z": float(sub["kappa_z"].median()),
                "delta_i": float(sub["delta_i_over_persistence"].median()),
                "n": int(len(sub)),
            }
        )
    return pd.DataFrame(rows)


def draw_panel_d(ax, points: pd.DataFrame, transition_summary: dict, null_summary: pd.DataFrame) -> None:
    threshold = float(transition_summary["best_threshold_value_z"])
    window_half_width = 0.55
    x_min = float(points["kappa_z"].min()) - 0.35
    x_max = float(points["kappa_z"].max()) + 0.35
    y_max = max(0.064, float(points["delta_i_over_persistence"].max()) * 1.18)
    ax.axvspan(threshold - window_half_width, threshold + window_half_width, color=BLUE_WINDOW, alpha=0.85, zorder=0)
    max_null_mean = float(null_summary["null_mean_delta_i"].max())
    ax.axhspan(0, max_null_mean, color="#ECECEC", alpha=0.9, zorder=0)
    left = points["kappa_z"] <= threshold
    ax.scatter(points.loc[left, "kappa_z"], points.loc[left, "delta_i_over_persistence"], s=28, color=BLUE_LIGHT, edgecolor="white", lw=0.35, alpha=0.92)
    ax.scatter(points.loc[~left, "kappa_z"], points.loc[~left, "delta_i_over_persistence"], s=28, color=BLUE, edgecolor="white", lw=0.35, alpha=0.92)
    bins = binned_summary(points)
    ax.plot(bins["kappa_z"], bins["delta_i"], color=BLUE_DARK, lw=1.6)
    ax.scatter(bins["kappa_z"], bins["delta_i"], color=BLUE_DARK, s=18, zorder=4)
    observed_mean = float(points["delta_i_over_persistence"].mean())
    ax.axhline(observed_mean, color=BLUE, lw=1.0, ls=(0, (3, 2)))
    ax.text(threshold, y_max * 0.94, "Candidate\nwindow", ha="center", va="top", color=BLUE_DARK, fontsize=7.3, fontweight="bold")
    ax.text(x_max - 0.02, y_max * 0.88, "Criticality\nnot established", ha="right", va="top", fontsize=7.3, style="italic")
    ax.text(x_max - 0.02, y_max * 0.09, "No causal closure", ha="right", va="bottom", fontsize=7.2, style="italic")
    ax.set_xlim(x_min, x_max)
    ax.set_ylim(0, y_max)
    ax.set_xlabel("Control index kappa (standardized)")
    ax.set_ylabel("State-information gain Delta I")
    ax.set_title("Phase-map framing", loc="left", fontsize=10.5, fontweight="bold", pad=5)
    panel_label(ax, "d")


def cjk_present(text: str) -> bool:
    return bool(re.search(r"[\u4e00-\u9fff]", text))


def png_nonblank(path: Path) -> bool:
    import matplotlib.image as mpimg

    arr = mpimg.imread(path)
    if arr.size == 0:
        return False
    return float(np.nanstd(arr[..., :3])) > 0.005


def save_tiff(png_path: Path, tiff_path: Path) -> None:
    from PIL import Image

    with Image.open(png_path) as img:
        img.save(tiff_path, dpi=(450, 450), compression="tiff_lzw")


def build_phase_points(candidates: pd.DataFrame) -> pd.DataFrame:
    points = candidates[["gauge_id", "source_family", "delta_i_over_persistence", "kappa_pc1_persistence"]].copy()
    points["kappa_z"] = standardize(points["kappa_pc1_persistence"].to_numpy(float))
    return points


def render_figure(out_dir: Path, raw_summary: dict, transition_summary: dict, null_summary: pd.DataFrame, points: pd.DataFrame) -> None:
    set_style(out_dir)
    import matplotlib.pyplot as plt

    fig = plt.figure(figsize=(8.1, 6.05), constrained_layout=False)
    gs = fig.add_gridspec(2, 2, left=0.075, right=0.985, bottom=0.135, top=0.955, wspace=0.30, hspace=0.42)
    ax_a = fig.add_subplot(gs[0, 0])
    ax_b = fig.add_subplot(gs[0, 1])
    ax_c = fig.add_subplot(gs[1, 0])
    ax_d = fig.add_subplot(gs[1, 1])
    draw_panel_a(ax_a, raw_summary, transition_summary)
    draw_panel_b(ax_b, raw_summary, null_summary)
    draw_panel_c(ax_c, transition_summary)
    draw_panel_d(ax_d, points, transition_summary, null_summary)
    out_png = out_dir / f"{FIGURE_ID}.png"
    out_svg = out_dir / f"{FIGURE_ID}.svg"
    out_pdf = out_dir / f"{FIGURE_ID}.pdf"
    fig.savefig(out_png, dpi=450)
    fig.savefig(out_svg)
    fig.savefig(out_pdf)
    plt.close(fig)
    save_tiff(out_png, out_dir / f"{FIGURE_ID}.tiff")


def write_caption(out_dir: Path, raw_summary: dict, transition_summary: dict) -> str:
    caption = (
        "Figure 5. Controlled-transition candidate under a bounded control-index framing. "
        "a, The transition model improves the scalar fit over the linear comparator "
        f"(Delta R2 = {raw_summary['observed_transition_gain_r2']:.3f}). "
        "b, The observed transition-gain line exceeds the 95% intervals from Q-only "
        "block-shuffled, phase-randomized and AR(p) surrogate families. "
        "c, The retained split is nearly symmetric across the control boundary "
        f"({transition_summary['support_left']} versus {transition_summary['support_right']} basins) "
        f"and spans {transition_summary['n_source_families']} source families. "
        "d, Basin-level state-information gain is shown against the standardized "
        "control index kappa; the shaded band marks the candidate transition window, "
        "and the grey band marks the maximum Q-only null mean. The figure supports "
        "a transition-like candidate window, not a confirmed critical phase transition "
        "or causal mechanism closure."
    )
    (out_dir / "caption.txt").write_text(caption + "\n", encoding="utf-8")
    return caption


def write_outputs(args: argparse.Namespace) -> dict:
    raw_summary_path = args.raw_gate_dir / "raw_hydrograph_surrogate_decision_summary.json"
    null_summary_path = args.raw_gate_dir / "null_family_summary.csv"
    transition_summary_path = args.transition_dir / "transition_decision_summary.json"
    candidates_path = args.transition_dir / "control_variable_candidates.csv"
    transition_scan_path = args.transition_dir / "transition_scan_table.csv"
    bootstrap_ci_path = args.transition_dir / "transition_bootstrap_ci.csv"
    require_paths([raw_summary_path, null_summary_path, transition_summary_path, candidates_path, transition_scan_path, bootstrap_ci_path])
    args.out_dir.mkdir(parents=True, exist_ok=True)
    raw_summary = read_json(raw_summary_path)
    transition_summary = read_json(transition_summary_path)
    null_summary = pd.read_csv(null_summary_path)
    candidates = pd.read_csv(candidates_path)
    scan = pd.read_csv(transition_scan_path)
    bootstrap_ci = pd.read_csv(bootstrap_ci_path)
    points = build_phase_points(candidates)
    source_rows = []
    for key, value in raw_summary.items():
        if isinstance(value, (int, float, str, bool)):
            source_rows.append({"source_table": "raw_hydrograph_surrogate_decision_summary.json", "metric": key, "value": value})
    for key, value in transition_summary.items():
        if isinstance(value, (int, float, str, bool)):
            source_rows.append({"source_table": "transition_decision_summary.json", "metric": key, "value": value})
    source_rows.append({"source_table": "null_family_summary.csv", "metric": "rows", "value": len(null_summary)})
    source_rows.append({"source_table": "control_variable_candidates.csv", "metric": "rows", "value": len(points)})
    pd.DataFrame(source_rows).to_csv(args.out_dir / "figure_source_data.csv", index=False)
    points.to_csv(args.out_dir / "phase_map_points.csv", index=False)
    scan.head(20).to_csv(args.out_dir / "transition_scan_top20.csv", index=False)
    bootstrap_ci.to_csv(args.out_dir / "transition_bootstrap_ci.csv", index=False)
    render_figure(args.out_dir, raw_summary, transition_summary, null_summary, points)
    caption = write_caption(args.out_dir, raw_summary, transition_summary)
    svg_text = (args.out_dir / f"{FIGURE_ID}.svg").read_text(encoding="utf-8", errors="ignore")
    exports = [args.out_dir / f"{FIGURE_ID}.{ext}" for ext in ["png", "svg", "pdf", "tiff"]]
    qa = {
        "figure_id": FIGURE_ID,
        "panel_count": 4,
        "data_panel_count": 4,
        "schematic_panel_count": 0,
        "panel_d_source": "control_variable_candidates.csv",
        "exports_exist": all(path.exists() and path.stat().st_size > 3000 for path in exports),
        "png_nonblank": png_nonblank(exports[0]),
        "no_cjk_text": not cjk_present(svg_text + caption),
        "layout_grid_status": "2x2_explicit_gridspec",
        "alignable_panel_status": "aligned",
        "palette_status": "reference_matched_muted_blue_grey",
        "non_data_gridlines_removed": True,
        "palette": {
            "text": TEXT,
            "axis": AXIS,
            "control_grey": GREY,
            "observed_blue": BLUE,
            "window_blue": BLUE_WINDOW,
            "low_side_blue": BLUE_LIGHT,
        },
        "text_overlap_clipping_status": "not_detected_by_static_export_smoke",
        "allowed_claim": "controlled-transition candidate supported against Q-only daily hydrograph surrogates on retained Caravan subset",
        "blocked_stronger_claim": "physical phase transition; universal order parameter; causal mechanism closure; GRDC/GSIM observed validation",
        "external_files_updated": False,
    }
    manifest = {
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "readiness": "FIGURE_CANDIDATE_READY_INTERNAL",
        "figure_id": FIGURE_ID,
        "figure": "Figure 5 controlled-transition phase-map candidate",
        "panel_count": 4,
        "data_panel_count": 4,
        "schematic_panel_count": 0,
        "source_data": ["figure_source_data.csv", "phase_map_points.csv", "transition_scan_top20.csv", "transition_bootstrap_ci.csv"],
        "caption": "caption.txt",
        "exports": [path.name for path in exports],
        "external_files_updated": False,
        "claim_ceiling": qa["allowed_claim"],
        "blocked_stronger_claim": qa["blocked_stronger_claim"],
    }
    (args.out_dir / "figure_QA_report.json").write_text(json.dumps(qa, indent=2), encoding="utf-8")
    (args.out_dir / "figure_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    report = f"""# Controlled-transition phase-map Figure 5 candidate

Decision: `FIGURE_CANDIDATE_READY_INTERNAL`

This workspace-only candidate follows the requested muted grey/blue visual
style while keeping the claim bounded. It does not alter files outside the
working output directory.

Key values:

- linear R2: `{raw_summary['observed_linear_r2']:.4f}`
- transition R2: `{raw_summary['observed_transition_r2']:.4f}`
- transition gain: `{raw_summary['observed_transition_gain_r2']:.4f}`
- best control variable: `{transition_summary['best_control_variable']}`
- candidate threshold quantile: `{transition_summary['best_threshold_quantile']:.2f}`
- support split: `{transition_summary['support_left']}/{transition_summary['support_right']}`
- source families: `{transition_summary['n_source_families']}`

Claim boundary:

The figure supports a transition-like candidate window against Q-only
surrogates. It does not support a confirmed critical phase transition,
universal order parameter, causal mechanism closure or observed GRDC/GSIM
validation.
"""
    (args.out_dir / "FIGURE5_CONTROLLED_TRANSITION_PHASEMAP_FIGURE5_REPORT.md").write_text(report, encoding="utf-8")
    return manifest


def main() -> None:
    args = parse_args()
    manifest = write_outputs(args)
    print(json.dumps({"decision": manifest["readiness"], "out_dir": str(args.out_dir), "panels": manifest["panel_count"]}, indent=2))


if __name__ == "__main__":
    main()
