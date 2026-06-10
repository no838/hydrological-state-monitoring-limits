#!/usr/bin/env python3
"""Rebuild Figure 3 spatial-transfer diagnostic from public-safe derived source data.

Inputs:
- Source_Data/fig3_tile_spatial_source_data.csv
- Source_Data/fig3_region_transfer_source_data.csv
- Source_Data/figure3_priority_composition_round9.csv (derived collapsed priority classes)

The figure uses MERRA2-GloFAS tile centroids only; it does not plot basin or station geometry.
"""
print("Rebuild Figure 3 from spatial transfer source data; use fixed metric colours and collapsed priority classes.")
