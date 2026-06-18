#!/usr/bin/env python3
"""Inspect Figure 5 source data for the NC hydrological-state monitoring paper."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source-data",
        type=Path,
        default=Path("Source_Data") / "Source_Data_Fig5_CONTROLLED_TRANSITION.xlsx",
        help="Path to the Figure 5 controlled-transition source-data workbook.",
    )
    return parser.parse_args()


def as_metric_table(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(path)
    df = pd.read_excel(path)
    expected = {"source_table", "metric", "value"}
    missing = expected.difference(df.columns)
    if missing:
        raise ValueError(f"Missing columns: {sorted(missing)}")
    return df


def metric(df: pd.DataFrame, name: str):
    rows = df.loc[df["metric"].astype(str).eq(name), "value"]
    if rows.empty:
        raise KeyError(name)
    return rows.iloc[0]


def main() -> int:
    args = parse_args()
    df = as_metric_table(args.source_data)
    n_basins = int(metric(df, "n_basins"))
    null_draws = int(metric(df, "null_draws_per_family"))
    linear_r2 = float(metric(df, "observed_linear_r2"))
    transition_r2 = float(metric(df, "observed_transition_r2"))
    transition_gain = float(metric(df, "observed_transition_gain_r2"))
    support_left = int(metric(df, "support_left"))
    support_right = int(metric(df, "support_right"))
    null_gt_ci95 = str(metric(df, "all_null_families_transition_gt_ci95")).lower() == "true"

    checks = {
        "n_basins_is_39": n_basins == 39,
        "null_draws_per_family_is_99": null_draws == 99,
        "transition_gain_matches_reported": round(transition_gain, 3) == 0.206,
        "transition_r2_exceeds_linear_r2": transition_r2 > linear_r2,
        "support_boundary_is_balanced": sorted([support_left, support_right]) == [19, 20],
        "observed_exceeds_null_ci95": null_gt_ci95,
    }
    print("Figure 5 source-data checks")
    for key, value in checks.items():
        print(f"{key}: {value}")
    print(f"linear_r2={linear_r2:.6f}")
    print(f"transition_r2={transition_r2:.6f}")
    print(f"transition_gain={transition_gain:.6f}")
    return 0 if all(checks.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
