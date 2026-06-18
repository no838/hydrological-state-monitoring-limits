# Global limits of hydrological state monitoring under streamflow persistence

This public release contains derived source data and source-data-level code for
the paper "Global limits of hydrological state monitoring under streamflow persistence". It updates the previous public archive by adding Figure 5
source-data workbooks, retained-basin metadata, transition-gain model tables,
Q-only surrogate draw tables, and Figure 5 transition/surrogate analysis scripts.

## Version

- Release version: `v1.1.0`
- Repository: https://github.com/no838/hydrological-state-monitoring-limits
- Release URL: https://github.com/no838/hydrological-state-monitoring-limits/releases/tag/v1.1.0
- Previous archived DOI: https://doi.org/10.5281/zenodo.20674526

## Contents

- `data/source_data/`: figure-level workbooks for Figures 1-5 and public-safe supporting tables.
- `code/source_data_checks/`: scripts for inspecting source-data workbooks and figure-level source tables.
- `code/figure_builders/`: Figure 5 transition and surrogate analysis scripts.
- `metadata/`: file manifest, panel source map, source-data hash manifest and checksums.
- `scripts/00_check_inputs.py`: public-release preflight.
- `run_reproduction.py`: lightweight source-data validation runner.

## Reproduction scope

This archive supports inspection of the released source-data workbooks, Figure 5
supporting tables and source-data-level analysis scripts. It is not a raw-data
redistribution archive. Raw MERRA2, GloFAS, CHIRPS/GLEAM, GRDC, GSIM and related
provider records remain subject to their original provider terms and must be
retrieved from the original providers for full upstream reconstruction.

## Quick start

```bash
python3 -m pip install -r requirements.txt
python3 scripts/00_check_inputs.py
python3 run_reproduction.py
```

## Citation

After this release is archived on Zenodo, cite the version DOI assigned by
Zenodo. Until then, cite the repository release URL above and the previous
archived DOI listed for version linkage.

## License

Code is released under the MIT License. Derived source-data tables are released
under CC BY 4.0 where permitted by upstream provider terms. Raw provider records
are not redistributed.
