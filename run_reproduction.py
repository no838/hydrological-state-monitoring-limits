#!/usr/bin/env python3
from pathlib import Path
import subprocess
import sys

root = Path(__file__).resolve().parent
subprocess.run([sys.executable, str(root / "scripts" / "00_check_inputs.py")], check=True)
print("\nAvailable figure scripts:")
for script in sorted((root / "code").glob("make_figure*.py")):
    print(f"  python3 code/{script.name}")
print("\nThis public release validates source-data availability and code traceability. Full raw-data reconstruction is outside the public bundle because provider raw archives are not redistributed.")
