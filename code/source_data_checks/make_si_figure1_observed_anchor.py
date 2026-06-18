#!/usr/bin/env python3
"""Supplementary Figure 1: observed-anchor support and geometry audit."""
from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec

ROOT = Path(__file__).resolve().parents[1]
FIG_DIR = ROOT / 'SI_Figures'
SRC = ROOT / 'Source_Data' / 'Source_Data_Observed_Anchor_Geometry_Boundary.xlsx'
COL = {'navy': '#0B1533', 'teal': '#1F6F78', 'aqua': '#7DB8B0', 'lavender': '#7B6BB2', 'gold': '#D4A247', 'grey':'#B8C0CC', 'grid':'#D7DCE3'}


def clean(ax, axis='y'):
    ax.spines[['top', 'right']].set_visible(False)
    ax.grid(axis=axis, color=COL['grid'], linewidth=0.8)
    ax.set_axisbelow(True)


def main():
    FIG_DIR.mkdir(exist_ok=True)
    summary = pd.read_excel(SRC, sheet_name='Observed_anchor_summary')
    coverage = pd.read_excel(SRC, sheet_name='Geometry_coverage')
    summary['dataset_short'] = summary['dataset'].str.replace('_basin_average','', regex=False).str.replace('_station_point','', regex=False)
    fig = plt.figure(figsize=(11.6, 5.6), facecolor='white')
    gs = GridSpec(1, 2, figure=fig, width_ratios=[1.0, 1.15], wspace=0.35)
    ax1 = fig.add_subplot(gs[0,0])
    ax2 = fig.add_subplot(gs[0,1])
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10})

    # panel a events + stations
    clean(ax1)
    x = range(len(summary))
    ax1.bar([i-0.18 for i in x], summary['stations'], width=0.34, color=COL['aqua'], label='Stations')
    ax1.bar([i+0.18 for i in x], summary['high_flow_events'], width=0.34, color=COL['teal'], label='High-flow events')
    ax1.set_xticks(list(x), summary['dataset_short'])
    ax1.set_ylabel('Count')
    ax1.set_title('a  Observed-anchor support summary', loc='left', fontsize=13, fontweight='bold')
    ax1.legend(frameon=False, fontsize=8.5)
    for i, row in summary.iterrows():
        ax1.text(i, max(row['stations'], row['high_flow_events']) + 300, row['years'], ha='center', fontsize=8, color='#5B6B80')

    # panel b geometry coverage heatmap-like table
    cov = coverage.copy()
    cov['dataset_short'] = cov['dataset'].str.replace('_basin_average','', regex=False).str.replace('_station_point','', regex=False)
    pivot = cov.pivot_table(index='geometry_type', columns='dataset_short', values='coverage_share', aggfunc='first').fillna(0)
    im = ax2.imshow(pivot.values, cmap='BuGn', vmin=0, vmax=1, aspect='auto')
    ax2.set_xticks(range(len(pivot.columns)), pivot.columns)
    ax2.set_yticks(range(len(pivot.index)), pivot.index.str.replace('_',' ', regex=False))
    ax2.set_title('b  Geometry coverage closure', loc='left', fontsize=13, fontweight='bold')
    for i in range(pivot.shape[0]):
        for j in range(pivot.shape[1]):
            v = pivot.values[i,j]
            ax2.text(j, i, f'{v:.2f}', ha='center', va='center', color='white' if v>0.55 else COL['navy'], fontsize=8.5)
    for sp in ax2.spines.values(): sp.set_visible(False)
    ax2.tick_params(length=0)
    cbar = fig.colorbar(im, ax=ax2, fraction=0.046, pad=0.02)
    cbar.set_label('Coverage share')

    for ext, kwargs in {'png':{'dpi':300}, 'pdf':{}, 'svg':{}}.items():
        fig.savefig(FIG_DIR / f'Supplementary_Figure1.{ext}', bbox_inches='tight', **kwargs)
    plt.close(fig)

if __name__ == '__main__':
    main()
