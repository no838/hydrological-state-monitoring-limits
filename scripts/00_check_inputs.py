#!/usr/bin/env python3
from pathlib import Path
import sys

root = Path(__file__).resolve().parents[1]
required = [
    "data/source_data/Source_Data_Fig1_INFORMATION_PARTITION.xlsx",
    "data/source_data/Source_Data_Fig2_THRESHOLD_CI.xlsx",
    "data/source_data/Source_Data_Fig3_SPATIAL_TRANSFER.xlsx",
    "data/source_data/Source_Data_Fig4_STORAGE_FAMILY.xlsx",
    "code/requirements.txt",
    "metadata/panel_source_map.csv",
    "metadata/figure_manifest.csv",
]
missing = [p for p in required if not (root / p).exists()]
if missing:
    print("Missing required release files:")
    for p in missing:
        print(f"  - {p}")
    sys.exit(1)
blocked_markers = [
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
skip_names = {"00_check_inputs.py", "PUBLIC_RELEASE_SANITIZATION_REPORT.md"}
for path in root.rglob("*"):
    if path.name in skip_names:
        continue
    if path.is_file() and path.suffix.lower() in {".md", ".txt", ".csv", ".json", ".py", ".cff"}:
        text = path.read_text(errors="ignore")
        for marker in blocked_markers:
            if marker in text:
                hits.append((str(path.relative_to(root)), marker))
if hits:
    print("Blocked public-release markers detected:")
    for rel, marker in hits:
        print(f"  - {rel}: {marker}")
    sys.exit(2)
print("Input and sanitization preflight passed.")
