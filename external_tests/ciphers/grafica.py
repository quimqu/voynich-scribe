# Gràfica de les corbes d'entropia (estimador del notebook) i de la bateria, a partir de resultats.json i resultats2.json.
import os, json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
HERE = os.path.dirname(os.path.abspath(__file__))
R1 = json.load(open(os.path.join(HERE, 'resultats.json'), encoding='utf-8'))
R2 = json.load(open(os.path.join(HERE, 'resultats2.json'), encoding='utf-8'))['res']
CUR = [('Voynich (ZL3b, escriba)', '#111111', '-', 2.6), ('Llatí (De docta)', '#c0392b', '-', 2.0),
       ('PM-Cipher (notebook)', '#2e86c1', '--', 1.6), ('Lletra+dígit (juny 2025)', '#8e44ad', ':', 1.6),
       ('Tipus Naibbe (1-2 lletres/mot)', '#27ae60', '--', 1.4), ('Nomenclàtor + homòfons + contacte', '#d68910', '-.', 1.4)]
fig, ax = plt.subplots(1, 2, figsize=(12, 4.4))
for name, col, ls, lw in CUR:
    y = R1[name]['wordreset'][:8]; ax[0].plot(range(1, 9), y, ls, color=col, lw=lw, marker='o', ms=3, label=name)
y = R1['PM-Cipher (notebook)']['joint_wordreset'][:8]
ax[0].plot(range(1, 9), y, ':', color='#2e86c1', lw=1.2, label='PM-Cipher: glif + residu (el que cal per llegir-lo)')
ax[0].set_xlabel('n (glifs de context + 1)'); ax[0].set_ylabel('bits per glif'); ax[0].set_title("Entropia dins del mot (estimador del notebook)")
ax[0].grid(alpha=.3); ax[0].legend(fontsize=7)
names = list(R2.keys()); sc = [R2[n]['score'] for n in names]
ax[1].barh(range(len(names)), sc, color=['#111111' if 'Voynich' in n else '#c0392b' if 'Llatí' in n else '#7f8c8d' for n in names])
ax[1].set_yticks(range(len(names))); ax[1].set_yticklabels(names, fontsize=7); ax[1].invert_yaxis()
ax[1].axvline(69, color='#27ae60', ls='--', lw=1); ax[1].text(69.5, len(names) - .6, "escriba (sense contingut) 69", fontsize=7, color='#27ae60')
ax[1].set_xlim(0, 80); ax[1].set_xlabel('mesures reproduïdes de 76'); ax[1].set_title('Bateria de l\'escriba')
plt.tight_layout(); plt.savefig(os.path.join(HERE, 'xifrats.png'), dpi=140)
