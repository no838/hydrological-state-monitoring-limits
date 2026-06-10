# Global limits of hydrological state monitoring for high-flow prediction

Derived source data and lightweight code supporting the article 'Global limits of hydrological state monitoring for high-flow prediction'. The release contains public-safe figure source data, supporting derived audit tables and figure-building scripts. Raw provider data are not redistributed.

Archived release: https://doi.org/10.5281/zenodo.20630565

GitHub repository: https://github.com/no838/hydrological-state-monitoring-limits

## Authors

1. Xi-Yin Zhou (first and corresponding author)
2. Chunyan Cao

Affiliations:
1. Guangdong-Hong Kong-Macao Greater Bay Area Weather Research Center for Monitoring, Warning and Forecasting (Shenzhen Institute of Meteorological Innovation), Shenzhen 518000, China
2. Shenzhen Key Laboratory of Southern Severe Weather Research (Shenzhen Key Laboratory of Artificial Intelligence Meteorological Application), Shenzhen, Guangdong 518038, China

Correspondence: Xi-Yin Zhou <xiyinzhou@foxmail.com>

## Contents

- `data/source_data/`: figure-level Excel workbooks and public-safe supporting derived tables.
- `code/`: lightweight figure-building scripts and Python requirements.
- `figures/`: public copies of Figures 1-4 in PNG, SVG and PDF format.
- `metadata/`: figure manifest, panel source map, captions and figure QA notes.
- `run_reproduction.py`: lightweight validation runner for this public release.
- `scripts/00_check_inputs.py`: input and sanitization preflight.

## Reproduction scope

This release supports inspection of the manuscript figure source data and
lightweight figure/code traceability. It is not a raw-data mirror and does not
claim complete raw-data reproduction. Raw MERRA2, GloFAS, CHIRPS/GLEAM, GRDC,
GSIM or other provider archives are not redistributed. Users should retrieve
raw provider data from the original data providers under their respective
licenses if they need to rebuild the full upstream pipeline.

## Citation

Please cite the archived release as:

Zhou, X.-Y. (2026). Global limits of hydrological state monitoring for high-flow prediction (v1.0.0-round9) [Data set]. Zenodo. https://doi.org/10.5281/zenodo.20630565

The local release metadata lists Chunyan Cao as the second creator. The first published Zenodo record metadata currently displays Xi-Yin Zhou as creator; update the Zenodo record metadata if citation indexing must expose both creators at the record level.

## Quick start

```bash
python3 scripts/00_check_inputs.py
python3 run_reproduction.py
```

The runner verifies the public data/code bundle and prints the figure scripts
that can be executed from the release root.

## License

Code is released under the MIT License. Derived source-data tables are released
under CC BY 4.0 where permitted by upstream provider terms. Raw provider data
are excluded and remain subject to their original licenses.
