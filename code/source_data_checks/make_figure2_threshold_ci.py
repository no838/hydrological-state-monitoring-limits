#!/usr/bin/env python3
"""Figure 2: threshold-state contrast under the persistence benchmark ."""
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec

ROOT = Path(__file__).resolve().parents[1]
FIG_DIR = ROOT / 'Figures'
SRC_DIR = ROOT / 'Source_Data'
COL = {
    'navy': '#0B1533',
    'teal': '#1F6F78',
    'aqua': '#7DB8B0',
    'raw': '#8C510A',
    'gold': '#D4A247',
    'purple': '#7B6BB2',
    'grey': '#AAB2BF',
    'light': '#F6F7FA',
    'grid': '#D7DCE3',
    'zero': '#96A2AF',
    'text': '#243447',
}


def load_data():
    authority = pd.read_excel(SRC_DIR / 'Source_Data_Fig2_THRESHOLD_CI.xlsx', sheet_name='Authority_CI_surface').sort_values('q_level')
    controls = pd.read_excel(SRC_DIR / 'Source_Data_Fig2_THRESHOLD_CI.xlsx', sheet_name='All_control_families')
    return authority, controls


def setup():
    plt.rcParams.update({
        'font.family': 'DejaVu Sans',
        'font.size': 10,
        'axes.titlesize': 12.2,
        'axes.titleweight': 'bold',
        'axes.labelsize': 10.3,
        'xtick.labelsize': 9.3,
        'ytick.labelsize': 9.3,
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


def draw(authority, controls):
    setup()
    labels = ['Q80', 'Q85', 'Q90', 'Q92.5', 'Q95', 'Q97.5']
    x = np.arange(len(labels))

    fig = plt.figure(figsize=(13.4, 7.8))
    gs = GridSpec(2, 3, figure=fig, height_ratios=[1.38, 1.0], width_ratios=[1.0, 1.0, 0.95], wspace=0.34, hspace=0.44)
    ax_a = fig.add_subplot(gs[0, :])
    ax_b = fig.add_subplot(gs[1, 0])
    ax_c = fig.add_subplot(gs[1, 1])
    ax_d = fig.add_subplot(gs[1, 2])

    # a: dominant persistence-conditioned threshold surface
    y = authority['lambda_bootstrap_p50'].to_numpy()
    lo = authority['lambda_bootstrap_p05'].to_numpy()
    hi = authority['lambda_bootstrap_p95'].to_numpy()
    ax_a.axvspan(2.5, 5.5, color=COL['light'], zorder=0)
    ax_a.fill_between(x, lo, hi, color=COL['teal'], alpha=0.20, lw=0)
    ax_a.plot(x, y, color=COL['teal'], lw=2.9, marker='o', ms=6.5)
    ax_a.axhline(0, color=COL['zero'], lw=1.1)
    ax_a.set_xticks(x, labels)
    ax_a.set_ylabel(r'Threshold-state contrast, $\Delta_{state}(q)$')
    ax_a.set_ylim(-0.06, 0.84)
    style(ax_a)
    ptitle(ax_a, 'a', 'Upper-tail emergence of state contrast')
    ax_a.annotate('Persistence-absorbed range', xy=(1.2, -0.008), xytext=(0.35, 0.17), color=COL['navy'], fontsize=9.2,
                  arrowprops=dict(arrowstyle='-', color=COL['navy'], lw=0.9))
    ax_a.annotate('Residual upper-tail contrast', xy=(4, y[4]), xytext=(3.15, 0.79), color=COL['teal'], fontsize=9.2,
                  arrowprops=dict(arrowstyle='-|>', color=COL['teal'], lw=1.0))
    ax_a.text(5.02, y[5] + 0.05, 'support-thinner', fontsize=8.8, color=COL['text'])

    # b: comparator curves compact
    meta = {
        'raw_state': ('Raw state', COL['raw']),
        'rain_persistence_matched': ('Rain + persistence', COL['teal']),
        'residual_state_matched': ('Residual state', COL['purple']),
    }
    for fam, (lab, col) in meta.items():
        sub = controls[controls['control_family'] == fam].sort_values('q_level')
        yy = sub['lambda_bootstrap_p50'].to_numpy()
        ax_b.plot(x, yy, color=col, lw=2.0, marker='o', ms=5.4, label=lab)
    ax_b.axhline(0, color=COL['zero'], lw=1.0)
    ax_b.set_xticks(x, labels, rotation=0)
    ax_b.set_ylabel(r'$\Delta_{state}(q)$')
    ax_b.set_ylim(-0.05, 0.96)
    style(ax_b)
    ptitle(ax_b, 'b', 'Comparator dependence')
    ax_b.legend(frameon=False, fontsize=8.5, loc='upper left')

    # c: event support and bootstrap completeness
    style(ax_c)
    bars = ax_c.bar(x, authority['high_flow_events'], color=COL['aqua'], width=0.64, edgecolor='none')
    ax_c.set_xticks(x, labels)
    ax_c.set_ylabel('High-flow events')
    ptitle(ax_c, 'c', 'Support and bootstrap completeness')
    ax_c2 = ax_c.twinx()
    valid_pct = authority['bootstrap_draws_valid'] / authority['bootstrap_draws_requested'] * 100.0
    ax_c2.plot(x, valid_pct, color=COL['gold'], lw=2.0, marker='s', ms=5)
    ax_c2.set_ylim(0, 100.5)
    ax_c2.set_ylabel('Valid bootstrap draws (%)')
    ax_c2.spines['top'].set_visible(False)
    ax_c2.spines['right'].set_color(COL['gold'])
    ax_c2.tick_params(axis='y', colors=COL['gold'])
    for b, ev in zip(bars, authority['high_flow_events']):
        ax_c.text(b.get_x()+b.get_width()/2, b.get_height()+180, f'{int(ev):,}', ha='center', va='bottom', fontsize=7.8, color=COL['text'])

    # d: direction of bootstrap draws
    vals = authority['lambda_positive_share'].to_numpy()
    bar_cols = [COL['grey'] if v <= 0 else COL['teal'] for v in vals]
    bars = ax_d.bar(x, vals, color=bar_cols, width=0.64, edgecolor='none')
    ax_d.axhline(0.5, color=COL['zero'], lw=1.0, ls=':')
    ax_d.set_xticks(x, labels)
    ax_d.set_ylim(0, 1.12)
    ax_d.set_ylabel('Positive bootstrap share')
    style(ax_d)
    ptitle(ax_d, 'd', 'Directional support')
    for b, v in zip(bars, vals):
        ax_d.text(b.get_x()+b.get_width()/2, v+0.03, f'{v:.2f}', ha='center', va='bottom', fontsize=8.2)

    fig.subplots_adjust(top=0.94, bottom=0.08, left=0.07, right=0.98)
    for ext, kwargs in {'png': {'dpi': 320}, 'pdf': {}, 'svg': {}, 'tiff': {'dpi': 320}}.items():
        fig.savefig(FIG_DIR / f'Figure2.{ext}', bbox_inches='tight', **kwargs)
    plt.close(fig)


if __name__ == '__main__':
    authority, controls = load_data()
    draw(authority, controls)
    print('Figure 2 rebuilt in', FIG_DIR)
