#!/usr/bin/env python3
from pathlib import Path
import subprocess
import sys

root = Path(__file__).resolve().parent
subprocess.run([sys.executable, str(root / "scripts" / "00_check_inputs.py")], check=True)
subprocess.run([
    sys.executable,
    str(root / "code" / "source_data_checks" / "inspect_figure5_source_data.py"),
    "--source-data",
    str(root / "data" / "source_data" / "Source_Data_Fig5_CONTROLLED_TRANSITION.xlsx"),
], check=True)
print("Source-data validation completed.")
