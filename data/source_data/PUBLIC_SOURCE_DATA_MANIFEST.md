# Public-safe Source Data manifest

The article file set provides figure-level Source Data workbooks in Excel format for Figures 1-5, plus public-safe supporting CSV/JSON/Markdown records under `Source_Data/supporting/`. All records are derived summaries or sanitized audit records. Raw provider data, local caches, credentials and machine-specific paths are excluded.

Figure 5 is represented by two public-safe source-data workbooks: `Source_Data_Fig5_LAG_DECAY_CONSTRAINT.xlsx` records the lag-decay stronger-null summary, and `Source_Data_Fig5_CONTROLLED_TRANSITION.xlsx` records the retained-basin count, transition-gain model table and Q-only surrogate summaries for AR(p), phase-randomized and block-shuffled null families. The Figure 5 surrogate screen uses 39 retained basins and 99 draws per null family.

| File | Linked figure or use | Boundary |
|---|---|---|
| `Source_Data_Fig1_INFORMATION_PARTITION.xlsx` | Fig1 | Derived summaries only; raw provider data and local paths excluded |
| `Source_Data_Fig2_THRESHOLD_CI.xlsx` | Fig2 | Derived summaries only; raw provider data and local paths excluded |
| `Source_Data_Fig3_SPATIAL_TRANSFER.xlsx` | Fig3 | Derived summaries only; raw provider data and local paths excluded |
| `Source_Data_Fig4_STORAGE_FAMILY.xlsx` | Fig4 | Derived summaries only; raw provider data and local paths excluded |
| `Source_Data_Fig5_LAG_DECAY_CONSTRAINT.xlsx` | Fig5 lag-decay stronger-null summary | Derived stronger-null summaries only; raw provider data and local paths excluded |
| `Source_Data_Fig5_CONTROLLED_TRANSITION.xlsx` | Fig5 transition-gain and Q-only surrogate summary | Derived retained-basin and surrogate summaries only; raw provider data and local paths excluded |
| `Source_Data_Observed_Anchor_Geometry_Boundary.xlsx` | Observed anchor | Derived summaries only; raw provider data and local paths excluded |
