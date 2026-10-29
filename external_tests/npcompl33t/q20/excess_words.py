# Words over-represented on each Q20 sheet against the rest of Q20 (count >= 8), and the ones the two ends share.
from common import *


def excess(b, k=12):
    W = [w for p in score if bif[p] == b for l in lines[p] for w in l['ws']]; c = Counter(W); n = len(W)
    rest = Counter(w for p in score if bif[p] != b for l in lines[p] for w in l['ws']); nr = sum(rest.values())
    sc = {w: (c[w] / n) / ((rest[w] + 1) / nr) for w in c if c[w] >= 8}
    return sorted(sc, key=lambda w: -sc[w] * c[w] / n)[:k], c


print('Over-represented words per Q20 sheet (count in the sheet), sheets in the order of npcompl33t\'s axis:')
for b in sheets:
    top, c = excess(b); print('  %-8s %s' % (b[2:], ' '.join('%s(%d)' % (w, c[w]) for w in top)))
a = set(excess('T:103-116', 30)[0]); b_ = set(excess('T:108-111', 30)[0]); r = set(excess('T:105-114', 30)[0])
print('\nshared by the two late sheets 103-116 and 108-111:', ' '.join(sorted(a & b_)))
print('shared by 103-116 and the earliest 105-114:', ' '.join(sorted(a & r)) or '-')
print('shared by 108-111 and 105-114:', ' '.join(sorted(b_ & r)) or '-')
