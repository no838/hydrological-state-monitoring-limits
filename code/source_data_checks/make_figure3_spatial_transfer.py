#!/usr/bin/env python3
"""Figure 3: global spatial classes and transfer limits ."""
from pathlib import Path
import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import box
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from matplotlib.patches import Patch
from matplotlib.lines import Line2D

ROOT = Path(__file__).resolve().parents[1]
FIG_DIR = ROOT / 'Figures'
SRC_DIR = ROOT / 'Source_Data'
SUPPORT_DIR = SRC_DIR / 'supporting'
WORLD_GEOJSON = SUPPORT_DIR / 'naturalearth_lowres_public.geojson'
COL = {
    'more': '#1F6F78',
    'mixed': '#D4A247',
    'less': '#8C510A',
    'grey': '#C9CDD3',
    'navy': '#0B1533',
    'grid': '#D7DCE3',
    'pass': '#1F6F78',
    'fail': '#D4A247',
    'border': '#D9DCE1',
    'zero': '#96A2AF',
}


def load_inputs():
    world = gpd.read_file(WORLD_GEOJSON)
    df = pd.read_csv(SUPPORT_DIR / 'fig3_tile_spatial_source_data.csv')
    valid = df[df['state_monitoring_priority'].notna()].copy()
    valid['priority_display'] = valid['state_monitoring_priority'].map({
        'state_monitoring_more_valuable': 'More valuable',
        'state_monitoring_less_valuable': 'Less valuable',
        'state_monitoring_mixed_low_signal': 'Mixed/context',
        'state_monitoring_mixed_but_watch': 'Mixed/context',
    })
    valid['geometry'] = [box(x0, y0, x1, y1) for x0, y0, x1, y1 in zip(valid['lon_min'], valid['lat_min'], valid['lon_max'], valid['lat_max'])]
    gdf = gpd.GeoDataFrame(valid, geometry='geometry', crs='EPSG:4326')
    region = pd.read_excel(SRC_DIR / 'Source_Data_Fig3_SPATIAL_TRANSFER.xlsx', sheet_name='region_transfer')
    priority = pd.read_excel(SRC_DIR / 'Source_Data_Fig3_SPATIAL_TRANSFER.xlsx', sheet_name='priority_composition')
    return world, gdf, region, priority


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


def draw(world, gdf, region, priority):
    setup()
    region_map = {'asia': 'Asia', 'australasia': 'Australasia', 'europe_west_asia': 'Europe-W Asia', 'high_latitude_north': 'High-latitude N', 'north_america': 'North America', 'south_america': 'South America'}
    region['region_display'] = region['region'].replace(region_map)
    priority['region_display'] = priority['region'].replace(region_map)
    priority = priority.rename(columns={'more': 'More valuable', 'mixed': 'Mixed/context', 'less': 'Less valuable', 'unclassified': 'Unclassified'})
    order = ['Asia', 'Australasia', 'Europe-W Asia', 'High-latitude N', 'North America', 'South America']

    fig = plt.figure(figsize=(13.4, 8.2))
    gs = GridSpec(2, 3, figure=fig, width_ratios=[1.18, 1.0, 1.02], height_ratios=[1.18, 1.0], wspace=0.33, hspace=0.40)
    ax_map = fig.add_subplot(gs[0, 0:2])
    ax_plane = fig.add_subplot(gs[0, 2])
    ax_comp = fig.add_subplot(gs[1, 0:2])
    ax_stab = fig.add_subplot(gs[1, 2])

    # a: large map
    colors = {'More valuable': COL['more'], 'Mixed/context': COL['mixed'], 'Less valuable': COL['less']}
    world.plot(ax=ax_map, color='#FAFAFA', edgecolor=COL['border'], linewidth=0.35)
    for cat in ['More valuable', 'Mixed/context', 'Less valuable']:
        gdf[gdf['priority_display'] == cat].plot(ax=ax_map, color=colors[cat], edgecolor='white', linewidth=0.42)
    ax_map.set_xlim(-180, 180)
    ax_map.set_ylim(-58, 82)
    ax_map.set_xticks([]); ax_map.set_yticks([])
    for sp in ax_map.spines.values(): sp.set_visible(False)
    ptitle(ax_map, 'a', 'Spatial classes of monitoring value')
    handles = [Patch(facecolor=colors[k], edgecolor='none', label=k) for k in ['More valuable', 'Mixed/context', 'Less valuable']]
    ax_map.legend(handles=handles, frameon=False, ncol=3, loc='lower left', bbox_to_anchor=(0.00, -0.10), fontsize=8.9, handlelength=1.8)

    # b: transfer plane
    style(ax_plane, axis='both')
    ax_plane.axvline(0, color=COL['zero'], lw=1.0)
    ax_plane.axhline(0, color=COL['zero'], lw=1.0)
    sizes = 40 + (region['events'] / region['events'].max()) * 95
    point_cols = [COL['pass'] if v else COL['fail'] for v in region['state_value_pass']]
    ax_plane.scatter(region['delta_auc_vs_rain_persistence'], region['delta_brier_vs_rain_persistence'], s=sizes, c=point_cols, ec='white', lw=0.8, zorder=3)
    for _, row in region.iterrows():
        ax_plane.text(row['delta_auc_vs_rain_persistence'] + 0.002, row['delta_brier_vs_rain_persistence'] + 0.00065, row['region_display'], fontsize=7.8)
    ax_plane.set_xlabel('ΔAUC')
    ax_plane.set_ylabel('ΔBrier')
    ptitle(ax_plane, 'b', 'Held-out transfer plane')
    ax_plane.legend(handles=[
        Line2D([0], [0], marker='o', color='w', markerfacecolor=COL['pass'], markeredgecolor='white', markersize=7.3, label='Pass'),
        Line2D([0], [0], marker='o', color='w', markerfacecolor=COL['fail'], markeredgecolor='white', markersize=7.3, label='Fail')],
        frameon=False, loc='upper left', fontsize=8.3)

    # c: composition by region
    pp = priority.set_index('region_display').loc[order]
    left = np.zeros(len(pp))
    for cat in ['More valuable', 'Mixed/context', 'Less valuable']:
        vals = pp[cat].values
        ax_comp.barh(pp.index, vals, left=left, color=colors[cat], height=0.58, label=cat)
        left += vals
    if 'Unclassified' in pp.columns:
        ax_comp.barh(pp.index, pp['Unclassified'].values, left=left, color=COL['grey'], height=0.58, label='Unclassified')
    ax_comp.set_xlim(0, 1.0)
    ax_comp.set_xlabel('Share of valid tiles')
    ax_comp.invert_yaxis()
    style(ax_comp, axis='x')
    ptitle(ax_comp, 'c', 'Composition by region')
    ax_comp.legend(frameon=False, ncol=4, loc='upper center', bbox_to_anchor=(0.50, -0.20), fontsize=8.5)

    # d: stability pass shares
    labels = ['Out of time', 'Out of region', 'Era-region']
    pass_share = [1.0, 2/6, 4/11]
    numerators = ['2/2', '2/6', '4/11']
    bars = ax_stab.bar(labels, pass_share, color=[COL['more'], COL['mixed'], COL['mixed']], width=0.62, edgecolor='none')
    ax_stab.axhline(0.5, color=COL['zero'], lw=1.0, ls=':')
    ax_stab.set_ylim(0, 1.12)
    ax_stab.set_ylabel('Pass share')
    style(ax_stab)
    ptitle(ax_stab, 'd', 'Validation stability')
    for b, txt, val in zip(bars, numerators, pass_share):
        ax_stab.text(b.get_x()+b.get_width()/2, val+0.04, txt, ha='center', va='bottom', fontsize=9.0)
    for tick in ax_stab.get_xticklabels():
        tick.set_rotation(12)
        tick.set_ha('right')

    fig.subplots_adjust(top=0.94, bottom=0.09, left=0.07, right=0.98)
    for ext, kwargs in {'png': {'dpi': 320}, 'pdf': {}, 'svg': {}, 'tiff': {'dpi': 320}}.items():
        fig.savefig(FIG_DIR / f'Figure3.{ext}', bbox_inches='tight', **kwargs)
    plt.close(fig)


if __name__ == '__main__':
    world, gdf, region, priority = load_inputs()
    draw(world, gdf, region, priority)
    print('Figure 3 rebuilt in', FIG_DIR)
