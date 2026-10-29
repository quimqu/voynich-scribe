# How the Q20 pages are written, from the Beinecke scans (MS 408, IIIF, 1600 px wide): line pitch, ink height of a line, glyph width,
# where the text starts. Pitch = median distance between the line peaks of the ink profile, measured in the middle of the text column
# (30-80% of the page width: no stars, no ragged right edge). Scans downloaded once into VMS_IMG (default C:\Temp\vms_img, ~21 MB).
import os, sys, json, urllib.request, numpy as np, pandas as pd
from PIL import Image
from scipy.signal import find_peaks
from scipy.ndimage import uniform_filter1d
from scipy.stats import spearmanr
from common import score, bif, sheets, REPO
IMG = os.environ.get('VMS_IMG', r'C:\Temp\vms_img'); os.makedirs(IMG, exist_ok=True)
MANIFEST = 'https://collections.library.yale.edu/manifests/2002046'
pages = sorted(score)
if not all(os.path.exists(os.path.join(IMG, p[1:] + '.jpg')) for p in pages):
    m = json.load(urllib.request.urlopen(MANIFEST))
    for c in m['items']:
        lab = list(c['label'].values())[0][0]
        if 'f' + lab in score and not os.path.exists(os.path.join(IMG, lab + '.jpg')):
            sid = c['items'][0]['items'][0]['body']['service'][0]['@id']
            urllib.request.urlretrieve(f'{sid}/full/1600,/0/default.jpg', os.path.join(IMG, lab + '.jpg'))
Z = pd.read_csv(os.path.join(REPO, 'df_lines_ZL3b_strokes.csv'), dtype={'davis_hand': str})
Z = Z[(Z.is_label == 0) & (Z.locus_generic == 'P')]
R = {}
for pg in pages:
    im = np.asarray(Image.open(os.path.join(IMG, pg[1:] + '.jpg')).convert('RGB')).astype(float); g = im.mean(2)
    vel = g > 150                                                           # vellum is bright, the background and the facing page's edge are not
    cols = np.flatnonzero(uniform_filter1d(vel.mean(0), 15) > 0.6); runs = np.split(cols, np.flatnonzero(np.diff(cols) > 5) + 1); c = max(runs, key=len)
    x0, x1 = c[0], c[-1]; w = x1 - x0
    rws = np.flatnonzero(uniform_filter1d(vel[:, x0:x1].mean(1), 15) > 0.8); y0, y1 = rws[0], rws[-1]
    page = g[y0:y1, x0:x1]; rb = im[y0:y1, x0:x1, 0] - im[y0:y1, x0:x1, 2]
    ink = (page < 0.72 * np.median(page)) & ~(rb > 70)                      # dark, and not the red of the stars
    prof = uniform_filter1d(ink[:, int(0.30 * w):int(0.80 * w)].mean(1), 3)
    pk, pr = find_peaks(prof, distance=22, prominence=0.04, width=1, rel_height=0.5)
    gaps = np.diff(pk); gaps = gaps[(gaps > 22) & (gaps < 60)]
    z = Z[Z.page_tag == pg]
    xs = np.flatnonzero(ink[pk[0]:pk[-1]].mean(0) > 0.02); tw = np.percentile(xs, 97) - np.percentile(xs, 3)
    R[pg] = dict(score=score[pg], sheet=bif[pg][2:], lines=len(z), lines_found=len(pk), pitch=float(np.median(gaps)), ink_height=float(np.median(pr['widths'])),
                 glyph_width=tw / z.n_glyphs.mean(), page_height=y1 - y0, text_starts=pk[0] / (y1 - y0), text_span=(pk[-1] - pk[0]) / (y1 - y0))
E = pd.DataFrame(R).T; E = E.astype({c: float for c in E.columns if c != 'sheet'})
pd.set_option('display.width', 200)
print('Q20 pages from the scans (pixels at 1600 px width; text_starts / text_span as a share of the page height)\n')
print(E.sort_values('score').round(3).to_string())
sh = E.groupby('sheet').mean(numeric_only=True).loc[[s[2:] for s in sheets]]
print('\nSpearman with the page score (n = %d) and with the sheet means (n = 6):' % len(E))
for c in ['lines', 'pitch', 'ink_height', 'glyph_width', 'page_height', 'text_starts', 'text_span']:
    r = spearmanr(E.score, E[c]); print('  %-12s page rho %+.2f (p %.3f)   sheet rho %+.2f' % (c, r.statistic, r.pvalue, spearmanr(sh.score, sh[c]).statistic))
print('\nPer sheet (axis order):'); print(sh[['score', 'lines', 'pitch', 'ink_height', 'glyph_width', 'text_starts']].round(3).to_string())
