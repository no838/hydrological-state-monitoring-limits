#!/usr/bin/env python3
"""Supplementary Figure 2: comparator families across thresholds."""
from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec

ROOT = Path(__file__).resolve().parents[1]
FIG_DIR = ROOT / 'SI_Figures'
SRC = ROOT / 'Source_Data' / 'Source_Data_Fig2_THRESHOLD_CI.xlsx'
COL = {'navy': '#0B1533', 'teal': '#1F6F78', 'brown': '#8C510A', 'lavender': '#7B6BB2', 'gold':'#D4A247', 'grid':'#D7DCE3'}


def clean(ax, axis='y'):
    ax.spines[['top', 'right']].set_visible(False)
    ax.grid(axis=axis, color=COL['grid'], linewidth=0.8)
    ax.set_axisbelow(True)


def main():
    FIG_DIR.mkdir(exist_ok=True)
    complete = pd.read_excel(SRC, sheet_name='All_control_families')
    baseline = pd.read_excel(SRC, sheet_name='Baseline_status')
    labels = ['Q80','Q85','Q90','Q92.5','Q95','Q97.5']
    x = range(6)
    fam_map = {'raw_state':('Raw state',COL['brown']), 'rain_persistence_matched':('Rain + persistence',COL['teal']), 'residual_state_matched':('Residual state',COL['lavender'])}
    fig = plt.figure(figsize=(11.6,5.8), facecolor='white')
    gs = GridSpec(1,2,figure=fig,width_ratios=[1.2,0.9],wspace=0.35)
    ax1=fig.add_subplot(gs[0,0])
    ax2=fig.add_subplot(gs[0,1])
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10})

    clean(ax1)
    for fam,(lab,col) in fam_map.items():
        sub=complete[complete['control_family']==fam].sort_values('q_level')
        ax1.plot(list(range(len(sub))), sub['lambda_threshold_discount'], marker='o', lw=2.2, color=col, label=lab)
    ax1.axhline(0,color='#94A3B8',lw=1)
    ax1.set_xticks(list(x), labels)
    ax1.set_ylabel('State contrast')
    ax1.set_title('a  Comparator-family threshold curves', loc='left', fontsize=13, fontweight='bold')
    ax1.legend(frameon=False, fontsize=8.5)

    clean(ax2)
    valid = baseline[['q_level','bootstrap_draws_valid']].copy().sort_values('q_level')
    complete_draws = complete[complete['control_family']=='rain_persistence_matched'].sort_values('q_level')[['q_level','bootstrap_draws_valid']]
    ax2.bar([i-0.18 for i in x], valid['bootstrap_draws_valid'], width=0.34, color=COL['gold'], label='Baseline file')
    ax2.bar([i+0.18 for i in x], complete_draws['bootstrap_draws_valid'], width=0.34, color=COL['teal'], label='Complete file')
    ax2.set_xticks(list(x), labels)
    ax2.set_ylabel('Valid bootstrap draws')
    ax2.set_title('b  Bootstrap-file completeness check', loc='left', fontsize=13, fontweight='bold')
    ax2.legend(frameon=False, fontsize=8.5)

    for ext, kwargs in {'png':{'dpi':300}, 'pdf':{}, 'svg':{}}.items():
        fig.savefig(FIG_DIR / f'Supplementary_Figure2.{ext}', bbox_inches='tight', **kwargs)
    plt.close(fig)

if __name__ == '__main__':
    main()
