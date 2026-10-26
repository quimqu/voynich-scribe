# Two forum figures for the seriation test (seriation.py must be in this folder; it is re-run here).
#   fig_horseshoe.png   MDS1 x MDS2, real text against the skribe (seed 1, the first seed, not chosen by looks)
#   fig_herbalA.png     herbal A (hand 1): position on MDS1 against the folio number, real against the skribe
#   PYTHONIOENCODING=utf-8 py -3 external_tests/npcompl33t/figures.py
import os, re
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
ns = {'__file__': os.path.join(HERE, 'seriation.py')}
exec(open(os.path.join(HERE, 'seriation.py'), encoding='utf-8').read().split('import matplotlib')[0], ns)
R = ns['R']
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.stats import spearmanr

INK, MUTED, GRID = '#1f1f1d', '#6b6a63', '#e4e3dd'
COL = {'herbal': '#2a78d6', 'pharmaceutical': '#eb6834', 'stars': '#1baf7a', 'biological': '#eda100'}
OTHER = '#9a9990'
LAB = {'herbal': 'herbal', 'pharmaceutical': 'pharmaceutical', 'stars': 'stars', 'biological': 'biological'}
plt.rcParams.update({'font.size': 11, 'axes.edgecolor': GRID, 'axes.labelcolor': MUTED, 'xtick.color': MUTED, 'ytick.color': MUTED,
                     'axes.titlecolor': INK, 'figure.facecolor': 'white', 'axes.facecolor': 'white'})


def style(ax):
    ax.grid(color=GRID, lw=0.8); ax.set_axisbelow(True)
    for s in ('top', 'right'):
        ax.spines[s].set_visible(False)


# ---------- figure 1: the horseshoe ----------
fig, axes = plt.subplots(1, 2, figsize=(13, 5.6), sharey=False)
for ax, src, title in ((axes[0], 'real', 'Real text (ZL3b)'), (axes[1], 'scribe_seed1', 'Skribe (seed 1): no chronology, no meaning')):
    r = R[src]; X = r['X']; P = r['P']; pages = r['pages']
    secs = np.array([P[p]['S'] for p in pages]); langs = np.array([P[p]['L'] for p in pages])
    for lang, mk in (('A', 'o'), ('B', '^')):
        m = (langs == lang) & ~np.isin(secs, list(COL))
        ax.scatter(X[m, 0], X[m, 1], s=34, marker=mk, c=OTHER, edgecolors='white', linewidths=0.8, alpha=0.9)
        for sec_, c in COL.items():
            m = (langs == lang) & (secs == sec_)
            ax.scatter(X[m, 0], X[m, 1], s=34, marker=mk, c=c, edgecolors='white', linewidths=0.8, alpha=0.95)
    for sec_, lang, name in (('herbal', 'A', 'herbal A'), ('herbal', 'B', 'herbal B'), ('pharmaceutical', 'A', 'pharmaceutical'),
                             ('stars', 'B', 'stars'), ('biological', 'B', 'biological')):   # direct labels at the centroid of each group
        m = (secs == sec_) & (langs == lang)
        cx, cy = X[m, 0].mean(), X[m, 1].mean()
        ax.annotate(name, (cx, cy), xytext={'herbal B': (-38, -22), 'stars': (22, 18), 'biological': (0, -18)}.get(name, (0, 14)), textcoords='offset points', ha='center',
                    color=INK, fontsize=10, fontweight='bold', bbox=dict(boxstyle='round,pad=0.2', fc='white', ec='none', alpha=0.85))
    ax.set_xlabel('MDS dimension 1'); ax.set_ylabel('MDS dimension 2')
    ax.set_title(f"{title}\npages of the same bifolium: {100*r['bif']:.1f}% of the MDS1 range apart", fontsize=11)
    style(ax)
h = [plt.Line2D([], [], ls='', marker='o', mfc=c, mec='white', ms=8, label=LAB[s]) for s, c in COL.items()]
h += [plt.Line2D([], [], ls='', marker='o', mfc=OTHER, mec='white', ms=8, label='other sections'),
      plt.Line2D([], [], ls='', marker='o', mfc='white', mec=INK, ms=8, label='Currier A'),
      plt.Line2D([], [], ls='', marker='^', mfc='white', mec=INK, ms=8, label='Currier B')]
fig.legend(handles=h, loc='lower center', ncol=7, frameon=False, fontsize=10, labelcolor=INK)
fig.suptitle("npcompl33t's seriation (glyph transitions per page, Jensen-Shannon, MDS), rebuilt from his posts", color=INK, fontsize=12)
fig.tight_layout(rect=(0, 0.07, 1, 0.95)); fig.savefig(os.path.join(HERE, 'fig_horseshoe.png'), dpi=120)

# ---------- figure 2: the drift inside herbal A ----------
fig, axes = plt.subplots(1, 2, figsize=(13, 4.8), sharey=True)
for ax, src, title in ((axes[0], 'real', 'Real text'), (axes[1], 'scribe_seed1', 'Skribe (seed 1)')):
    r = R[src]; X = r['X']; P = r['P']
    idx = [i for i, p in enumerate(r['pages']) if P[p]['S'] == 'herbal' and P[p]['H'] == '1']
    f = np.array([int(re.match(r'f(\d+)', r['pages'][i]).group(1)) for i in idx]); y = X[idx, 0]
    q = np.array([P[r['pages'][i]]['Q'] for i in idx]); ph = np.isin(q, ['O', 'P', 'Q'])   # herbal pages bound in the pharmaceutical quires
    ax.scatter(f[~ph], y[~ph], s=34, c=COL['herbal'], edgecolors='white', linewidths=0.8, label='herbal quires 1-7')
    ax.scatter(f[ph], y[ph], s=40, facecolors='white', edgecolors=COL['pharmaceutical'], linewidths=1.8, label='herbal pages in the pharmaceutical quires (f87-f96)')
    rho = spearmanr(f, y); rho2 = spearmanr(f[~ph], y[~ph])
    ax.set_title(f'{title}\nρ {rho.statistic:+.2f} (p {rho.pvalue:.3f}) all;  ρ {rho2.statistic:+.2f} (p {rho2.pvalue:.2f}) quires 1-7 only', fontsize=11)
    ax.set_xlabel('folio number (current binding)'); style(ax)
axes[0].set_ylabel('MDS dimension 1'); axes[0].legend(loc='upper left', frameon=False, fontsize=9, labelcolor=INK)
others = [spearmanr([int(re.match(r'f(\d+)', R[s]['pages'][i]).group(1)) for i in ix], [R[s]['X'][i, 0] for i in ix]).statistic
          for s in R if s != 'real' for ix in [[i for i, p in enumerate(R[s]['pages']) if R[s]['P'][p]['S'] == 'herbal' and R[s]['P'][p]['H'] == '1']]]
fig.suptitle(f'Herbal A (hand 1): position on MDS1 against the folio number (skribe, five seeds, all pages: ρ {min(others):+.2f} to {max(others):+.2f})',
             color=INK, fontsize=12)
fig.tight_layout(rect=(0, 0, 1, 0.9)); fig.savefig(os.path.join(HERE, 'fig_herbalA.png'), dpi=120)
print('saved fig_horseshoe.png, fig_herbalA.png')
