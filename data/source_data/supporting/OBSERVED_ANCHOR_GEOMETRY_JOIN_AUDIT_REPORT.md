# Observed Anchor Geometry Join Audit

Generated: 2026-06-10T15:23:46

## Bottom line

- The observed-anchor geometry gap is closed only at the support-layer level.
- GSIM final-family basin geometry is join-locked against the current threshold-valid family.
- GRDC final-family station-point geometry is join-locked against the current threshold-valid family.
- GRDC basin-polygon geometry remains partial under the current available polygon family and cannot be treated as fully closed for the 1719-station support route.

## Family-stage audit

| dataset                | stage                            |   rows |   stations |   tiles | note                                                                                                           | matches_threshold_authority   |
|:-----------------------|:---------------------------------|-------:|-----------:|--------:|:---------------------------------------------------------------------------------------------------------------|:------------------------------|
| GSIM219_basin_average  | source_panel_raw                 |  14602 |        219 |       5 | Raw GSIM basin-average source panel before null and support-length filters.                                    | False                         |
| GSIM219_basin_average  | after_required_nonnull           |  14409 |        219 |       5 | After dropping rows with missing rain, wetness, or response.                                                   | False                         |
| GSIM219_basin_average  | final_threshold_valid_family     |  14283 |        210 |       5 | After the authority script's >=24 valid months per station filter.                                             | True                          |
| GSIM219_basin_average  | threshold_authority_summary      |  14283 |        210 |       5 | Counts reported in threshold_response_grid.csv.                                                                | False                         |
| GRDC1736_station_point | source_family_after_join_support | 122783 |       1772 |      75 | Reconstructed GRDC station-point family after join-support filters but before null and support-length filters. | False                         |
| GRDC1736_station_point | after_required_nonnull           | 118675 |       1736 |      75 | After dropping rows with missing rain, wetness, or response.                                                   | False                         |
| GRDC1736_station_point | final_threshold_valid_family     | 118415 |       1719 |      75 | After the authority script's >=24 valid months per station filter.                                             | True                          |
| GRDC1736_station_point | threshold_authority_summary      | 118415 |       1719 |      75 | Counts reported in threshold_response_grid.csv.                                                                | False                         |

## Geometry coverage summary

| dataset                | geometry_type   |   ready_entities |   family_entities |   coverage_share | claim_label              | note                                                                                                                               |
|:-----------------------|:----------------|-----------------:|------------------:|-----------------:|:-------------------------|:-----------------------------------------------------------------------------------------------------------------------------------|
| GSIM219_basin_average  | basin_polygon   |              210 |               210 |        1         | support_geometry_closed  | GSIM join requires metadata.csv, catchment_characteristics.csv and per-basin shapefile presence.                                   |
| GSIM219_basin_average  | reference_point |              210 |               210 |        1         | support_geometry_closed  | GSIM panel already carries station coordinates for all final-family entities.                                                      |
| GRDC1736_station_point | station_point   |             1719 |              1719 |        1         | support_geometry_closed  | GRDC final-family point geometry comes from the reconstructed response panel latitude/longitude.                                   |
| GRDC1736_station_point | basin_polygon   |               54 |              1719 |        0.0314136 | support_geometry_partial | GRDC polygon coverage is limited to the available available polygon family; it does not close the full 1719-station support route. |

## Key bounded findings

- GSIM basin geometry ready: 210/210.
- GRDC station-point geometry ready: 1719/1719.
- GRDC basin-polygon geometry ready: 54/1719.
- GSIM short-support stations removed by the authority filter: 9.
- GRDC short-support stations removed by the authority filter: 17.
