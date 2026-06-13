#!/usr/bin/env python3
from pathlib import Path
import subprocess
import sys

root = Path(__file__).resolve().parent
subprocess.run([sys.executable, str(root / "scripts" / "00_check_inputs.py")], check=True)
print("\nAvailable inspection scripts:")
for script in sorted((root / "code").glob("*.py")):
    print(f"  python3 code/{script.name}")
print("\nThis public release validates source-data availability and partial source-data-level reproducibility. Full figure rebuilding and raw-data reconstruction are outside this public bundle.")
