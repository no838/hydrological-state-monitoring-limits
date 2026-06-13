#!/usr/bin/env python3
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "data" / "source_data"
EXPECTED = [
    "Source_Data_Fig1_INFORMATION_PARTITION.xlsx",
    "Source_Data_Fig2_THRESHOLD_CI.xlsx",
    "Source_Data_Fig3_SPATIAL_TRANSFER.xlsx",
    "Source_Data_Fig4_STORAGE_FAMILY.xlsx",
    "Source_Data_Observed_Anchor_Geometry_Boundary.xlsx",
    "Supplementary_Tables.xlsx",
]


def summarize_workbook(path: Path) -> dict:
    xls = pd.ExcelFile(path)
    out = {"file": path.name, "sheets": len(xls.sheet_names), "sheet_names": ";".join(xls.sheet_names)}
    rows = []
    for sheet in xls.sheet_names:
        df = pd.read_excel(path, sheet_name=sheet)
        rows.append(f"{sheet}:{len(df)}x{len(df.columns)}")
    out["sheet_shapes"] = ";".join(rows)
    return out


def main() -> None:
    missing = [name for name in EXPECTED if not (SRC / name).exists()]
    if missing:
        raise SystemExit("Missing source-data workbooks: " + ", ".join(missing))
    summary = [summarize_workbook(SRC / name) for name in EXPECTED]
    out_path = ROOT / "metadata" / "source_data_workbook_summary.csv"
    pd.DataFrame(summary).to_csv(out_path, index=False)
    print(f"Wrote {out_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
