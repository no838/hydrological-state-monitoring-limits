#!/usr/bin/env python3
"""Supplementary Figure 3: extended spatial-transfer diagnostics."""
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from matplotlib.lines import Line2D

ROOT = Path(__file__).resolve().parents[1]
FIG_DIR = ROOT / 'SI_Figures'
SRC = ROOT / 'Source_Data' / 'Source_Data_Fig3_SPATIAL_TRANSFER.xlsx'
COL = {
    'pass': '#1F6F78',
    'fail': '#D4A247',
    'more': '#1F6F78',
    'mixed': '#D4A247',
    'less': '#8C510A',
    'grey': '#C9CDD3',
    'grid': '#D7DCE3',
    'zero': '#93A0AF',
    'navy': '#0B1533',
}


def setup():
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.titlesize':12.3,'axes.titleweight':'bold','axes.labelsize':10.3,'xtick.labelsize':9.2,'ytick.labelsize':9.2})


def style(ax, axis='y'):
    ax.spines[['top','right']].set_visible(False)
    ax.grid(axis=axis, color=COL['grid'], linewidth=0.8)
    ax.set_axisbelow(True)


def ptitle(ax, letter, title):
    ax.set_title(f'{letter}  {title}', loc='left', pad=8)


def main():
    FIG_DIR.mkdir(exist_ok=True)
    region = pd.read_excel(SRC, sheet_name='region_transfer')
    priority = pd.read_excel(SRC, sheet_name='priority_composition')
    region_map = {'asia':'Asia','australasia':'Australasia','europe_west_asia':'Europe-W Asia','high_latitude_north':'High-latitude N','north_america':'North America','south_america':'South America'}
    region['region_display'] = region['region'].replace(region_map)
    priority['region_display'] = priority['region'].replace(region_map)
    priority = priority.rename(columns={'more':'More valuable','mixed':'Mixed/context','less':'Less valuable','unclassified':'Unclassified'})
    order = ['Asia', 'Australasia', 'Europe-W Asia', 'High-latitude N', 'North America', 'South America']
    region = region.set_index('region_display').loc[order].reset_index()
    priority = priority.set_index('region_display').loc[order]

    setup()
    fig = plt.figure(figsize=(11.6, 8.0), facecolor='white')
    gs = GridSpec(2,2,figure=fig,wspace=0.35,hspace=0.42)
    ax1=fig.add_subplot(gs[0,0])
    ax2=fig.add_subplot(gs[0,1])
    ax3=fig.add_subplot(gs[1,0])
    ax4=fig.add_subplot(gs[1,1])

    # a transfer plane with event-scaled points
    style(ax1, axis='both')
    ax1.axvline(0, color=COL['zero'], lw=1)
    ax1.axhline(0, color=COL['zero'], lw=1)
    sizes = 45 + (region['events']/region['events'].max())*105
    cols = [COL['pass'] if x else COL['fail'] for x in region['state_value_pass']]
    ax1.scatter(region['delta_auc_vs_rain_persistence'], region['delta_brier_vs_rain_persistence'], s=sizes, c=cols, ec='white', lw=0.8, zorder=3)
    for _,r in region.iterrows():
        ax1.text(r['delta_auc_vs_rain_persistence']+0.002, r['delta_brier_vs_rain_persistence']+0.0007, r['region_display'], fontsize=8.3)
    ax1.set_xlabel('ΔAUC vs rain + persistence')
    ax1.set_ylabel('ΔBrier (improvement)')
    ptitle(ax1, 'a', 'Regional transfer plane')
    ax1.legend(handles=[Line2D([0],[0], marker='o', color='w', markerfacecolor=COL['pass'], markeredgecolor='white', markersize=8, label='Pass'), Line2D([0],[0], marker='o', color='w', markerfacecolor=COL['fail'], markeredgecolor='white', markersize=8, label='Fail')], frameon=False, loc='upper left', fontsize=8.6)

    # b support sizes
    style(ax2, axis='x')
    y=np.arange(len(region))
    ax2.barh(y, region['events'], color=COL['pass'], alpha=0.88, height=0.58)
    ax2.set_yticks(y, region['region_display'])
    ax2.invert_yaxis()
    ax2.set_xlabel('Held-out events')
    ptitle(ax2, 'b', 'Regional support sizes')
    for yi, ev, tiles in zip(y, region['events'], region['test_tiles']):
        ax2.text(ev + max(region['events'])*0.015, yi, f'{int(ev)} events | {int(tiles)} tiles', va='center', fontsize=8.3, color=COL['navy'])

    # c class composition heatmap
    mat = priority[['More valuable','Mixed/context','Less valuable']].to_numpy()
    im = ax3.imshow(mat, cmap='YlGnBu', aspect='auto', vmin=0, vmax=1)
    ax3.set_xticks(range(3), ['More valuable','Mixed/context','Less valuable'])
    ax3.set_yticks(range(len(priority.index)), priority.index)
    ptitle(ax3, 'c', 'Regional class-composition matrix')
    for i in range(mat.shape[0]):
        for j in range(mat.shape[1]):
            v = mat[i,j]
            ax3.text(j, i, f'{v:.2f}', ha='center', va='center', fontsize=8.3, color='white' if v>0.5 else COL['navy'])
    for sp in ax3.spines.values(): sp.set_visible(False)
    ax3.tick_params(length=0)
    cbar=fig.colorbar(im, ax=ax3, fraction=0.046, pad=0.02)
    cbar.set_label('Share')

    # d region-wise deltas
    style(ax4, axis='x')
    ypos=np.arange(len(region))
    ax4.axvline(0, color=COL['zero'], lw=1)
    ax4.scatter(region['delta_auc_vs_rain_persistence'], ypos+0.12, color=COL['pass'], s=42, label='ΔAUC')
    ax4.scatter(region['delta_brier_vs_rain_persistence'], ypos-0.12, color=COL['fail'], s=42, label='ΔBrier')
    for yi, x1, x2 in zip(ypos, region['delta_auc_vs_rain_persistence'], region['delta_brier_vs_rain_persistence']):
        ax4.plot([min(x1,x2), max(x1,x2)], [yi, yi], color=COL['grid'], lw=1.0)
    ax4.set_yticks(ypos, region['region_display'])
    ax4.invert_yaxis()
    ax4.set_xlabel('Increment relative to rain + persistence')
    ptitle(ax4, 'd', 'Metric increments by region')
    ax4.legend(frameon=False, loc='lower right', fontsize=8.4)

    for ext, kwargs in {'png':{'dpi':320}, 'pdf':{}, 'svg':{}}.items():
        fig.savefig(FIG_DIR / f'Supplementary_Figure3.{ext}', bbox_inches='tight', **kwargs)
    plt.close(fig)

if __name__ == '__main__':
    main()
