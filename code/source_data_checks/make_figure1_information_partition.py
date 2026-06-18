#!/usr/bin/env python3
"""Figure 1: global geography of persistence-conditioned monitoring value ."""
from pathlib import Path
import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import box
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import Patch
from mpl_toolkits.axes_grid1.inset_locator import inset_axes

ROOT = Path(__file__).resolve().parents[1]
FIG_DIR = ROOT / 'Figures'
SRC_DIR = ROOT / 'Source_Data'
SUPPORT_DIR = SRC_DIR / 'supporting'
WORLD_GEOJSON = SUPPORT_DIR / 'naturalearth_lowres_public.geojson'

COL = {
    'navy': '#0B1533',
    'teal': '#1F6F78',
    'aqua': '#7DB8B0',
    'gold': '#D4A247',
    'brown': '#8C510A',
    'lavender': '#7B6BB2',
    'light': '#F6F7FA',
    'grid': '#D7DCE3',
    'text': '#223047',
    'muted': '#5B6B80',
}
MAP_CMAP = LinearSegmentedColormap.from_list('state_map', [COL['brown'], '#F7F4EA', COL['aqua'], COL['teal']])
REGION_LABELS = {
    'asia': 'Asia',
    'australasia': 'Australasia',
    'europe_west_asia': 'Europe-W Asia',
    'high_latitude_north': 'High-latitude N',
    'north_america': 'North America',
    'south_america': 'South America',
}


def load_world():
    return gpd.read_file(WORLD_GEOJSON)


def build_tile_gdf():
    df = pd.read_csv(SUPPORT_DIR / 'fig3_tile_spatial_source_data.csv')
    valid = df[df['state_monitoring_relevance_score'].notna()].copy()
    valid['priority_display'] = valid['state_monitoring_priority'].map({
        'state_monitoring_more_valuable': 'More valuable',
        'state_monitoring_less_valuable': 'Less valuable',
        'state_monitoring_mixed_low_signal': 'Mixed/context',
        'state_monitoring_mixed_but_watch': 'Mixed/context',
    })
    valid['region_label'] = valid['region'].map(REGION_LABELS).fillna(valid['region'])
    valid['geometry'] = [box(x0, y0, x1, y1) for x0, y0, x1, y1 in zip(valid['lon_min'], valid['lat_min'], valid['lon_max'], valid['lat_max'])]
    return gpd.GeoDataFrame(valid, geometry='geometry', crs='EPSG:4326')


def write_source_data(gdf):
    counts = (
        gdf['priority_display'].value_counts().reindex(['More valuable', 'Mixed/context', 'Less valuable']).fillna(0).astype(int).rename_axis('class_label').reset_index(name='tile_count')
    )
    counts['share_of_valid_tiles'] = counts['tile_count'] / counts['tile_count'].sum()
    region = (
        gdf.groupby('region_label').agg(mean_increment=('state_monitoring_relevance_score', 'mean'), median_increment=('state_monitoring_relevance_score', 'median'), sd_increment=('state_monitoring_relevance_score', 'std'), n_tiles=('tile_id', 'size')).reset_index()
    )
    region['se_increment'] = region['sd_increment'] / np.sqrt(region['n_tiles'])
    region['ci_low'] = region['mean_increment'] - 1.96 * region['se_increment'].fillna(0)
    region['ci_high'] = region['mean_increment'] + 1.96 * region['se_increment'].fillna(0)
    with pd.ExcelWriter(SRC_DIR / 'Source_Data_Fig1_INFORMATION_PARTITION.xlsx', engine='openpyxl') as writer:
        keep_cols = ['tile_id', 'region', 'region_label', 'lat_center', 'lon_center', 'lat_min', 'lat_max', 'lon_min', 'lon_max', 'state_monitoring_relevance_score', 'priority_display', 'observed_anchor_support', 'fullcycle_support_class', 'geometry_claim_boundary']
        gdf[keep_cols].to_excel(writer, sheet_name='Global_monitoring_map', index=False)
        counts.to_excel(writer, sheet_name='Class_composition', index=False)
        region.sort_values('mean_increment', ascending=False).to_excel(writer, sheet_name='Regional_increment', index=False)
        pd.DataFrame({'equation_name': ['Persistence-conditioned monitoring increment'], 'equation': ['ΔS_q = S(Y_q; R, P, A) − S(Y_q; R, P)'], 'definition': ['Incremental predictive score contributed by antecedent state after conditioning on rainfall and streamflow persistence.']}).to_excel(writer, sheet_name='Benchmark_definition', index=False)


def setup_style():
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 10, 'axes.titlesize': 12.4, 'axes.labelsize': 10.2, 'xtick.labelsize': 9.2, 'ytick.labelsize': 9.2, 'axes.facecolor': 'white', 'figure.facecolor': 'white', 'savefig.facecolor': 'white'})


def style_axes(ax):
    ax.spines[['top', 'right']].set_visible(False)
    ax.grid(color=COL['grid'], linewidth=0.8, alpha=0.8)
    ax.set_axisbelow(True)


def ptitle(ax, letter, title):
    ax.set_title(f'{letter}  {title}', loc='left', fontsize=13.3, fontweight='bold', pad=8)


def draw_figure(gdf, world):
    setup_style()
    fig = plt.figure(figsize=(13.8, 8.8))
    gs = GridSpec(2, 3, figure=fig, width_ratios=[1.15, 1.1, 1.0], height_ratios=[1.45, 1.0], wspace=0.32, hspace=0.34)
    ax_map = fig.add_subplot(gs[0, :])
    ax_dist = fig.add_subplot(gs[1, 0])
    ax_comp = fig.add_subplot(gs[1, 1])
    ax_region = fig.add_subplot(gs[1, 2])

    # a dominant map
    world.plot(ax=ax_map, color='#FAFAFA', edgecolor='#D9DCE1', linewidth=0.35)
    gdf.plot(ax=ax_map, column='state_monitoring_relevance_score', cmap=MAP_CMAP, vmin=-6, vmax=6, linewidth=0.45, edgecolor='white')
    support = gdf[gdf['observed_anchor_support'] == True]
    if len(support):
        support.boundary.plot(ax=ax_map, color=COL['navy'], linewidth=0.7)
    ax_map.set_xlim(-180, 180)
    ax_map.set_ylim(-58, 82)
    ax_map.set_xticks([])
    ax_map.set_yticks([])
    for sp in ax_map.spines.values():
        sp.set_visible(False)
    ptitle(ax_map, 'a', 'Global monitoring increment beyond rainfall + persistence')
    cax = inset_axes(ax_map, width='28%', height='4.0%', loc='lower right', borderpad=1.2)
    sm = plt.cm.ScalarMappable(cmap=MAP_CMAP, norm=plt.Normalize(vmin=-6, vmax=6))
    sm.set_array([])
    cbar = fig.colorbar(sm, cax=cax, orientation='horizontal')
    cbar.set_label('Monitoring increment score', fontsize=9.5)
    cbar.ax.tick_params(labelsize=8.7)
    map_legend = [Patch(facecolor='white', edgecolor=COL['navy'], linewidth=1.0, label='Observed-anchor support')]
    ax_map.legend(handles=map_legend, frameon=False, loc='lower left', bbox_to_anchor=(0.00, -0.01), fontsize=8.8, handlelength=1.6)

    # b distribution histogram
    style_axes(ax_dist)
    bins = np.linspace(-6, 6, 17)
    order = ['Less valuable', 'Mixed/context', 'More valuable']
    colors = [COL['brown'], COL['gold'], COL['teal']]
    series = [gdf.loc[gdf['priority_display'] == o, 'state_monitoring_relevance_score'].to_numpy() for o in order]
    ax_dist.hist(series, bins=bins, stacked=True, color=colors, edgecolor='white', linewidth=0.7, label=order)
    ax_dist.axvline(0, color=COL['navy'], linewidth=1.2, linestyle='--')
    ax_dist.set_xlabel('Tile-level monitoring increment score')
    ax_dist.set_ylabel('Tile count')
    ptitle(ax_dist, 'b', 'Distribution across valid tiles')
    ax_dist.legend(frameon=False, fontsize=8.5, loc='upper left')

    # c class composition
    counts = gdf['priority_display'].value_counts().reindex(['More valuable', 'Mixed/context', 'Less valuable']).fillna(0).astype(int)
    total = counts.sum()
    ax_comp.spines[['top', 'right', 'left']].set_visible(False)
    ax_comp.grid(axis='x', color=COL['grid'], linewidth=0.8)
    left = 0
    color_map = {'More valuable': COL['teal'], 'Mixed/context': COL['gold'], 'Less valuable': COL['brown']}
    for label in ['More valuable', 'Mixed/context', 'Less valuable']:
        share = counts[label] / total
        ax_comp.barh([''], [share], left=left, color=color_map[label], height=0.56)
        ax_comp.text(left + share / 2, 0, f'{label}\n{counts[label]} ({share:.0%})', ha='center', va='center', fontsize=9.6, color='white' if label != 'Mixed/context' else COL['navy'])
        left += share
    ax_comp.set_xlim(0, 1)
    ax_comp.set_yticks([])
    ax_comp.set_xlabel('Share of valid tiles (n=130)')
    ptitle(ax_comp, 'c', 'Global class composition')

    # d regional means
    region = (gdf.groupby('region_label').agg(mean_increment=('state_monitoring_relevance_score', 'mean'), sd=('state_monitoring_relevance_score', 'std'), n=('tile_id', 'size')).reset_index().sort_values('mean_increment', ascending=True))
    region['se'] = region['sd'] / np.sqrt(region['n'])
    region['ci'] = 1.96 * region['se'].fillna(0)
    y = np.arange(len(region))
    style_axes(ax_region)
    ax_region.errorbar(region['mean_increment'], y, xerr=region['ci'], fmt='o', color=COL['navy'], ecolor=COL['aqua'], elinewidth=2, capsize=3, markersize=6)
    ax_region.axvline(0, color=COL['navy'], linewidth=1.0, linestyle='--')
    ax_region.set_yticks(y, region['region_label'])
    ax_region.set_xlabel('Mean monitoring increment score')
    ptitle(ax_region, 'd', 'Regional mean increment')
    xmin = min(-3.0, float(region['mean_increment'].min() - 0.8))
    xmax = max(3.0, float(region['mean_increment'].max() + 0.8))
    ax_region.set_xlim(xmin, xmax)
    for yi, (_, row) in enumerate(region.iterrows()):
        xtext = row['mean_increment'] + (0.22 if row['mean_increment'] >= 0 else -0.22)
        ax_region.text(xtext, yi, f"n={int(row['n'])}", va='center', ha='left' if row['mean_increment'] >= 0 else 'right', fontsize=8.2, color=COL['muted'])

    fig.subplots_adjust(top=0.95, bottom=0.06, left=0.06, right=0.985)
    for ext, kwargs in {'png': {'dpi': 320}, 'pdf': {}, 'svg': {}, 'tiff': {'dpi': 320}}.items():
        fig.savefig(FIG_DIR / f'Figure1.{ext}', bbox_inches='tight', **kwargs)
    plt.close(fig)


if __name__ == '__main__':
    world = load_world()
    gdf = build_tile_gdf()
    write_source_data(gdf)
    draw_figure(gdf, world)
    print('Figure 1 rebuilt in', FIG_DIR)
