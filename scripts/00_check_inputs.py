#!/usr/bin/env python3
from pathlib import Path
import sys

root = Path(__file__).resolve().parents[1]
required = [
    "data/source_data/Source_Data_Fig1_INFORMATION_PARTITION.xlsx",
    "data/source_data/Source_Data_Fig2_THRESHOLD_CI.xlsx",
    "data/source_data/Source_Data_Fig3_SPATIAL_TRANSFER.xlsx",
    "data/source_data/Source_Data_Fig4_STORAGE_FAMILY.xlsx",
    "data/source_data/Source_Data_Fig5_CONTROLLED_TRANSITION.xlsx",
    "data/source_data/Source_Data_Fig5_LAG_DECAY_CONSTRAINT.xlsx",
    "data/source_data/source_data_Fig5_index.csv",
    "data/source_data/supporting/stronger_null_draws.csv",
    "data/source_data/supporting/stronger_null_summary.csv",
    "data/source_data/supporting/observed_benchmark_table.csv",
    "data/source_data/supporting/anti_autocorrelation_operator_benchmark.csv",
    "data/source_data/supporting/xi_star_results.csv",
    "code/figure_builders/build_figure5_raw_hydrograph_surrogate_gate.py",
    "metadata/panel_source_map.csv",
    "metadata/figure_manifest.csv",
    "MANIFEST.csv",
    "SHA256SUMS.txt",
]
missing = [p for p in required if not (root / p).exists()]
if missing:
    print("Missing required release files:")
    for p in missing:
        print(f"  - {p}")
    sys.exit(1)
markers = [
    "/" + "Users/",
    "/" + "Volumes/",
    "sandbox:",
    "/mnt/",
    "pass" + "word",
    "se" + "cret",
    "to" + "ken",
    "api" + "_key",
    "Cover_Letter",
    "Manuscript(",
]
hits = []
skip = {"00_check_inputs.py", "PUBLIC_RELEASE_AUDIT_REPORT.md"}
for path in root.rglob("*"):
    if path.name in skip:
        continue
    if path.is_file() and path.suffix.lower() in {".md", ".txt", ".csv", ".json", ".py", ".cff", ".yaml", ".yml"}:
        text = path.read_text(errors="ignore")
        for marker in markers:
            if marker in text:
                hits.append((str(path.relative_to(root)), marker))
if hits:
    print("Blocked public-release markers detected:")
    for rel, marker in hits:
        print(f"  - {rel}: {marker}")
    sys.exit(2)
print("Public-release input check passed.")
