#!/usr/bin/env python3
"""Supplementary Figure 4: extended storage-family diagnostics."""
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
SRC = ROOT / 'Source_Data' / 'Source_Data_Fig4_STORAGE_FAMILY.xlsx'
COL = {'teal':'#1F6F78','purple':'#7B6BB2','grey':'#AAB2BF','gold':'#D4A247','navy':'#0B1533','grid':'#D7DCE3'}


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
    fam = pd.read_excel(SRC, sheet_name='Family_status')
    sup = pd.read_excel(SRC, sheet_name='Support_breadth')
    heat = pd.read_excel(SRC, sheet_name='Evidence_matrix')
    order = ['Climate', 'Human', 'Soil texture', 'GRACE/TWS', 'Geomorphic', 'Hydroclim.', 'Subsurface', 'Unclassified']
    fam['display_family'] = pd.Categorical(fam['display_family'], order, ordered=True)
    sup['display_family'] = pd.Categorical(sup['display_family'], order, ordered=True)
    heat['display_family'] = pd.Categorical(heat['display_family'], order, ordered=True)
    fam = fam.sort_values('display_family')
    sup = sup.sort_values('display_family')
    heat = heat.sort_values('display_family')
    status_code = {'full_window_counted':2, 'ancillary_support':1, 'not_counted':0}

    setup()
    fig = plt.figure(figsize=(11.6, 7.8), facecolor='white')
    gs = GridSpec(2,2,figure=fig,wspace=0.35,hspace=0.42)
    ax1=fig.add_subplot(gs[0,0])
    ax2=fig.add_subplot(gs[0,1])
    ax3=fig.add_subplot(gs[1,0])
    ax4=fig.add_subplot(gs[1,1])

    # a status strip
    style(ax1, axis='x')
    y=np.arange(len(fam))
    colors=[COL['teal'] if s=='full_window_counted' else COL['purple'] if s=='ancillary_support' else COL['grey'] for s in fam['status_plot']]
    ax1.scatter([1]*len(y), y, s=120, c=colors)
    ax1.set_xlim(0.6,1.4)
    ax1.set_xticks([])
    ax1.set_yticks(y, fam['display_family'])
    ax1.invert_yaxis()
    ptitle(ax1, 'a', 'Family-status classification')
    ax1.legend(handles=[Line2D([0],[0], marker='o', color='w', markerfacecolor=COL['teal'], markersize=9, label='Full-window counted'), Line2D([0],[0], marker='o', color='w', markerfacecolor=COL['purple'], markersize=9, label='Ancillary'), Line2D([0],[0], marker='o', color='w', markerfacecolor=COL['grey'], markersize=9, label='Not counted')], frameon=False, loc='lower right', fontsize=8.3)

    # b support breadth sorted
    style(ax2, axis='x')
    sup2 = sup.sort_values('region_support_share', ascending=True).reset_index(drop=True)
    y2=np.arange(len(sup2))
    ax2.hlines(y2, 0, sup2['region_support_share'], color=COL['grid'], lw=2)
    status_lookup = fam.set_index('display_family')['status_plot'].to_dict()
    cols=[COL['teal'] if status_lookup.get(n)=='full_window_counted' else COL['purple'] if status_lookup.get(n)=='ancillary_support' else COL['grey'] for n in sup2['display_family']]
    ax2.scatter(sup2['region_support_share'], y2, c=cols, s=78, zorder=3)
    ax2.set_yticks(y2, sup2['display_family'])
    ax2.set_xlim(0,1)
    ax2.set_xlabel('Region-support share')
    ptitle(ax2, 'b', 'Family support breadth (ranked)')
    for xi, yi in zip(sup2['region_support_share'], y2):
        ax2.text(xi+0.02, yi, f'{xi:.2f}', va='center', fontsize=8.2, color=COL['navy'])

    # c evidence-detail heatmap
    mat = heat[['full_window_counted','ancillary_aligned','region_support_share']].to_numpy()
    im=ax3.imshow(mat, cmap='BuGn', vmin=0, vmax=1, aspect='auto')
    ax3.set_xticks(range(3), ['Full-window','Ancillary','Region support'])
    ax3.set_yticks(range(len(heat)), heat['display_family'])
    ptitle(ax3, 'c', 'Family evidence-detail matrix')
    for i in range(mat.shape[0]):
        for j in range(mat.shape[1]):
            v=mat[i,j]
            txt=f'{v:.2f}' if j==2 else ('Yes' if v>=0.5 else 'No')
            ax3.text(j,i,txt,ha='center',va='center',fontsize=8.2,color='white' if v>0.5 else COL['navy'])
    for sp in ax3.spines.values(): sp.set_visible(False)
    ax3.tick_params(length=0)
    cbar=fig.colorbar(im, ax=ax3, fraction=0.046, pad=0.02)
    cbar.set_label('Value')

    # d closure ladder
    style(ax4)
    ladder = pd.DataFrame({'step':['Required','Counted','Counted + ancillary','All candidates'], 'families':[3,3,4,8]})
    ax4.plot(range(len(ladder)), ladder['families'], color=COL['navy'], lw=1.7, marker='o', ms=6)
    ax4.scatter(range(len(ladder)), ladder['families'], s=70, c=[COL['gold'],COL['teal'],COL['purple'],COL['grey']], zorder=3)
    ax4.set_xticks(range(len(ladder)), ladder['step'])
    ax4.set_ylabel('Families')
    ax4.set_ylim(0,8.8)
    ptitle(ax4, 'd', 'Closure ladder')
    for i,v in enumerate(ladder['families']):
        ax4.text(i, v+0.2, str(v), ha='center', va='bottom', fontsize=8.8)

    for ext, kwargs in {'png':{'dpi':320}, 'pdf':{}, 'svg':{}}.items():
        fig.savefig(FIG_DIR / f'Supplementary_Figure4.{ext}', bbox_inches='tight', **kwargs)
    plt.close(fig)

if __name__ == '__main__':
    main()
