# Global limits of hydrological state monitoring for high-flow prediction

This public release contains derived source data and lightweight code supporting
the article "Global limits of hydrological state monitoring for high-flow prediction". It is a data/code availability package, not a full
article-file archive. Raw provider data, rendered figures, full figure-building
scripts and manuscript-facing files are not redistributed.

## Version

- Release version: `v1.0.0-round23`
- GitHub repository: https://github.com/no838/hydrological-state-monitoring-limits
- Prior archived version DOI: https://doi.org/10.5281/zenodo.20630565
- Concept DOI reserved for all versions: https://doi.org/10.5281/zenodo.20630564

## Creators

1. Xi-Yin Zhou (first and corresponding author)
2. Chunyan Cao

Affiliations:

1. Guangdong-Hong Kong-Macao Greater Bay Area Weather Research Center for Monitoring, Warning and Forecasting (Shenzhen Institute of Meteorological Innovation), Shenzhen 518000, China
2. Shenzhen Key Laboratory of Southern Severe Weather Research (Shenzhen Key Laboratory of Artificial Intelligence Meteorological Application), Shenzhen, Guangdong 518038, China

## Contents

- `data/source_data/`: figure-level Excel workbooks and public-safe supporting derived tables.
- `code/`: partial reproducibility scripts for inspecting source-data workbooks.
- `metadata/`: source-data index and panel source map.
- `scripts/00_check_inputs.py`: input and sanitization preflight.
- `run_reproduction.py`: lightweight traceability runner.

## Reproduction scope

This release supports inspection of figure source data and limited
source-data-level reproducibility checks. It does not provide full figure
rebuild scripts, full raw-data reconstruction, or the upstream analysis
pipeline because raw MERRA2, GloFAS, CHIRPS/GLEAM, GRDC, GSIM and other
provider archives are not redistributed. Users who need full upstream
reconstruction should retrieve raw provider data from the original providers
under their respective licenses and adapt the inspection scripts to their local
data layout.

## Citation

If using this release before a new Zenodo DOI appears, cite the GitHub release
and the concept DOI above. After Zenodo archives `v1.0.0-round23`, cite the new
version DOI reported by Zenodo.

## License

Code is released under the MIT License. Derived source-data tables are released
under CC BY 4.0 where permitted by upstream provider terms. Raw provider data
are excluded and remain subject to their original licenses.
