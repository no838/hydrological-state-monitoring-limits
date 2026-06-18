#!/usr/bin/env python3
"""Figure 4: storage-family evidence and closure ."""
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.lines import Line2D

ROOT = Path(__file__).resolve().parents[1]
FIG_DIR = ROOT / 'Figures'
SRC_DIR = ROOT / 'Source_Data'
SUPPORT_DIR = SRC_DIR / 'supporting'
PUBLIC_CSV = SUPPORT_DIR / 'source_data_Fig4_PUBLIC_SAFE.csv'

COL = {
    'navy': '#0B1533',
    'teal': '#1F6F78',
    'aqua': '#7DB8B0',
    'gold': '#D4A247',
    'purple': '#7B6BB2',
    'grey': '#AAB2BF',
    'grid': '#D7DCE3',
    'text': '#223047',
}
HM_CMAP = LinearSegmentedColormap.from_list('familyhm', ['#F7F8FB', '#B7D8D2', COL['teal']])


def load_data():
    raw = pd.read_csv(PUBLIC_CSV)
    fam = raw[raw['panel'] == 'family_status'].copy()
    fam['display_family'] = fam['display_family'].replace({'Unclass.': 'Unclassified'})
    fam['status_plot'] = fam['status'].replace({'ancillary_only': 'ancillary_support'})
    fam = fam.groupby(['display_family', 'status_plot'], as_index=False).agg(aligned=('aligned', 'max'))
    sup = raw[raw['panel'] == 'support_breadth'].copy()
    sup['display_family'] = sup['display_family'].replace({'Unclass.': 'Unclassified'})
    sup = sup.groupby('display_family', as_index=False)['value'].max().rename(columns={'value': 'region_support_share'})
    sup['region_support_share'] = sup['region_support_share'].fillna(0)
    full = fam[['display_family', 'status_plot', 'aligned']].copy()
    full['full_window_counted'] = (full['status_plot'] == 'full_window_counted').astype(float)
    full['ancillary_aligned'] = ((full['status_plot'] == 'ancillary_support') & (full['aligned'])).astype(float)
    full = full.groupby('display_family', as_index=False)[['full_window_counted', 'ancillary_aligned']].max()
    heat = full.merge(sup, on='display_family', how='outer').fillna(0)
    order = ['Climate', 'Human', 'Soil texture', 'GRACE/TWS', 'Geomorphic', 'Hydroclim.', 'Subsurface', 'Unclassified']
    heat['display_family'] = pd.Categorical(heat['display_family'], order, ordered=True)
    heat = heat.sort_values('display_family')
    status_counts = fam['status_plot'].value_counts().reindex(['full_window_counted', 'ancillary_support', 'not_counted']).fillna(0).astype(int)
    closure = pd.DataFrame({
        'metric': ['Required', 'Counted', 'Counted + ancillary', 'All candidates'],
        'families': [3, int(status_counts.get('full_window_counted', 0)), int(status_counts.get('full_window_counted', 0) + status_counts.get('ancillary_support', 0)), int(len(fam))]
    })
    return fam, sup, heat, status_counts, closure


def write_source_data(fam, sup, heat, status_counts, closure):
    with pd.ExcelWriter(SRC_DIR / 'Source_Data_Fig4_STORAGE_FAMILY.xlsx', engine='openpyxl') as writer:
        fam.to_excel(writer, sheet_name='Family_status', index=False)
        sup.to_excel(writer, sheet_name='Support_breadth', index=False)
        heat.to_excel(writer, sheet_name='Evidence_matrix', index=False)
        status_counts.rename_axis('status').reset_index(name='family_count').to_excel(writer, sheet_name='Status_counts', index=False)
        closure.to_excel(writer, sheet_name='Breadth_summary', index=False)


def setup():
    plt.rcParams.update({
        'font.family': 'DejaVu Sans',
        'font.size': 10,
        'axes.titlesize': 12.2,
        'axes.titleweight': 'bold',
        'axes.labelsize': 10.3,
        'xtick.labelsize': 9.2,
        'ytick.labelsize': 9.2,
        'figure.facecolor': 'white',
        'axes.facecolor': 'white',
        'savefig.facecolor': 'white',
    })


def style(ax, axis='y'):
    ax.spines[['top', 'right']].set_visible(False)
    ax.grid(axis=axis, color=COL['grid'], linewidth=0.8, alpha=0.85)
    ax.set_axisbelow(True)


def ptitle(ax, letter, title):
    ax.set_title(f'{letter}  {title}', loc='left', pad=7)


def draw(fam, sup, heat, status_counts, closure):
    setup()
    fig = plt.figure(figsize=(13.3, 8.0))
    gs = GridSpec(3, 2, figure=fig, width_ratios=[1.25, 1.0], height_ratios=[0.85, 1.0, 1.0], wspace=0.34, hspace=0.48)
    ax_matrix = fig.add_subplot(gs[:, 0])
    ax_counts = fig.add_subplot(gs[0, 1])
    ax_support = fig.add_subplot(gs[1, 1])
    ax_closure = fig.add_subplot(gs[2, 1])

    # a matrix as dominant panel
    mat = heat[['full_window_counted', 'ancillary_aligned', 'region_support_share']].to_numpy()
    im = ax_matrix.imshow(mat, aspect='auto', cmap=HM_CMAP, vmin=0, vmax=1)
    ax_matrix.set_xticks([0, 1, 2], ['Full-window\ncounted', 'Ancillary\naligned', 'Region support\nshare'])
    ax_matrix.set_yticks(np.arange(len(heat)), heat['display_family'])
    ptitle(ax_matrix, 'a', 'Proxy-family evidence matrix')
    for i in range(mat.shape[0]):
        for j in range(mat.shape[1]):
            val = mat[i, j]
            txt = f'{val:.2f}' if j == 2 else ('Yes' if val >= 0.5 else 'No')
            ax_matrix.text(j, i, txt, ha='center', va='center', fontsize=8.5, color='white' if val > 0.58 else COL['navy'])
    ax_matrix.tick_params(length=0)
    for sp in ax_matrix.spines.values(): sp.set_visible(False)
    cbar = fig.colorbar(im, ax=ax_matrix, fraction=0.046, pad=0.025)
    cbar.set_label('Evidence strength')

    # b status counts
    order = ['full_window_counted', 'ancillary_support', 'not_counted']
    labels = ['Full-window', 'Ancillary', 'Not counted']
    colors = [COL['teal'], COL['purple'], COL['grey']]
    vals = [status_counts.get(k, 0) for k in order]
    style(ax_counts)
    bars = ax_counts.bar(np.arange(len(vals)), vals, color=colors, width=0.60, edgecolor='none')
    ax_counts.set_xticks(np.arange(len(vals)), labels)
    ax_counts.set_ylabel('Families')
    ax_counts.set_ylim(0, max(vals)+1.2)
    ptitle(ax_counts, 'b', 'Evidence-status counts')
    for b in bars:
        ax_counts.text(b.get_x()+b.get_width()/2, b.get_height()+0.08, f'{int(b.get_height())}', ha='center', va='bottom', fontsize=8.8)

    # c support breadth as ranked lollipop
    sup2 = sup.sort_values('region_support_share', ascending=True).reset_index(drop=True)
    y = np.arange(len(sup2))
    status_lookup = fam.groupby('display_family')['status_plot'].first().to_dict()
    point_cols = [COL['teal'] if status_lookup.get(n) == 'full_window_counted' else COL['purple'] if status_lookup.get(n) == 'ancillary_support' else COL['grey'] for n in sup2['display_family']]
    style(ax_support, axis='x')
    ax_support.hlines(y, 0, sup2['region_support_share'], color=COL['grid'], lw=2.0)
    ax_support.scatter(sup2['region_support_share'], y, s=70, c=point_cols, zorder=3)
    ax_support.set_yticks(y, sup2['display_family'])
    ax_support.set_xlim(0, 1)
    ax_support.set_xlabel('Region-support share')
    ptitle(ax_support, 'c', 'Regional support breadth')
    for xi, yi in zip(sup2['region_support_share'], y):
        ax_support.text(xi + 0.02, yi, f'{xi:.2f}', va='center', fontsize=7.9, color=COL['text'])
    ax_support.legend(handles=[
        Line2D([0],[0], marker='o', color='w', markerfacecolor=COL['teal'], markersize=7.5, label='Full-window'),
        Line2D([0],[0], marker='o', color='w', markerfacecolor=COL['purple'], markersize=7.5, label='Ancillary'),
        Line2D([0],[0], marker='o', color='w', markerfacecolor=COL['grey'], markersize=7.5, label='Not counted')],
        frameon=False, loc='lower right', fontsize=7.8)

    # d closure ladder
    style(ax_closure)
    x = np.arange(len(closure))
    ladder_cols = [COL['gold'], COL['teal'], COL['purple'], COL['grey']]
    ax_closure.plot(x, closure['families'], color=COL['navy'], lw=1.4, marker='o', ms=4.5)
    ax_closure.scatter(x, closure['families'], s=65, c=ladder_cols, zorder=3)
    ax_closure.set_xticks(x, closure['metric'])
    ax_closure.set_ylabel('Families')
    ax_closure.set_ylim(0, 8.8)
    ptitle(ax_closure, 'd', 'Closure ladder')
    for xi, yi in zip(x, closure['families']):
        ax_closure.text(xi, yi + 0.22, str(int(yi)), ha='center', va='bottom', fontsize=8.8)

    fig.subplots_adjust(top=0.94, bottom=0.08, left=0.08, right=0.985)
    for ext, kwargs in {'png': {'dpi': 320}, 'pdf': {}, 'svg': {}, 'tiff': {'dpi': 320}}.items():
        fig.savefig(FIG_DIR / f'Figure4.{ext}', bbox_inches='tight', **kwargs)
    plt.close(fig)


if __name__ == '__main__':
    fam, sup, heat, status_counts, closure = load_data()
    write_source_data(fam, sup, heat, status_counts, closure)
    draw(fam, sup, heat, status_counts, closure)
    print('Figure 4 rebuilt in', FIG_DIR)
