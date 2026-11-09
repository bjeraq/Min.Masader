"""Word-pair captions: map raw-concat word timings to final video time, group 2 words, inject into cfg."""
import json, subprocess

SP = '/tmp/claude-0/-home-user-Advisers/43f3f876-332f-5c13-8812-05a26eedb0e5/scratchpad'
WORDS = json.load(open(f'{SP}/build/words_raw.json'))
OFFS = {int(k): v for k, v in json.load(open(f'{SP}/build/concat_offs.json')).items()}
TL = {s['n']: s for s in json.load(open(f'{SP}/build/timeline.json'))['scenes']}
cfg = json.load(open(f'{SP}/build/story_cfg_v3.json', encoding='utf-8'))

FIX = {'علبه': 'علبة', 'طاقه': 'طاقة', 'وعلبه': 'وعلبة', 'المحلاه': 'المحلّاة', 'معفاه': 'معفاة',
       'ايضا': 'أيضاً', 'بعيدا': 'بعيداً', 'سنويا': 'سنوياً', 'فعليا': 'فعلياً', 'قانونا': 'قانوناً',
       'محليا': 'محلياً', 'تعد': 'تُعدّ', 'ب500': 'بـ500', 'وتحسب': 'وتُحسب', 'محدود': 'محدودي'}


def clean(w):
    w = w.rstrip('.،,')
    return FIX.get(w, w)


# stretched/raw ratio per clip (atempo output duration is not exactly raw/tempo)
ratio = {}
for n in range(1, 17):
    d = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0',
                              f'{SP}/narr_f/n{n:02d}.wav'], capture_output=True, text=True).stdout)
    ratio[n] = d / OFFS[n]['dur']

# assign each word to its clip by midpoint, convert to absolute video time
per = {n: [] for n in range(1, 17)}
RAW_PER = {}
for w, a, b in WORDS:
    mid = (a + b) / 2000.0
    n = max(k for k in OFFS if OFFS[k]['off'] <= mid)
    if mid > OFFS[n]['off'] + OFFS[n]['dur'] + 0.05:
        n = min(n + 1, 16)
    r = ratio[n]; v = TL[n]['voice']; o = OFFS[n]['off']
    per[n].append((clean(w), v + (a / 1000.0 - o) * r, v + (b / 1000.0 - o) * r))
    RAW_PER.setdefault(n, []).append((w, a, b))

# sanity: word counts per scene
for n in per:
    assert per[n], n

sc = {s['n']: s for s in cfg['scenes']}
for n, words in per.items():
    s = sc[n]
    if n in (2, 16):         # title card and outro carry their own big text
        s.pop('caps', None)
        continue
    # merge the brand bigram so it never splits, and mark sentence ends
    toks = []
    i = 0
    while i < len(words):
        w, a0, b0 = words[i]
        brk = words[i][0].endswith(('.', '؟')) or clean(words[i][0]) != words[i][0] and False
        raw = WORDS  # noqa
        if w == 'من' and i + 1 < len(words) and words[i + 1][0].startswith('مصادر'):
            toks.append(('من مصادر', a0, words[i + 1][2], True)); i += 2; continue
        toks.append((w, a0, b0, False))
        i += 1
    # sentence-end flags come from the raw (uncleaned) words of this scene
    raws = [w for w, _, _ in RAW_PER[n]]
    ends = set()
    ri = 0
    for k, tk in enumerate(toks):
        step = 2 if tk[3] else 1
        last_raw = raws[min(ri + step - 1, len(raws) - 1)]
        if last_raw.endswith(('.', '؟')):
            ends.add(k)
        ri += step
    caps = []
    k = 0
    while k < len(toks):
        grp = [toks[k]]
        if k not in ends and k + 1 < len(toks):
            grp.append(toks[k + 1])
        t0 = grp[0][1]; t1 = grp[-1][2]
        caps.append({'a': round(t0, 3), 'b': round(t1, 3), 'w': ' '.join(g[0] for g in grp)})
        k += len(grp)
    # show each group until the next begins (or briefly after the last), clamp into the scene
    for k, c in enumerate(caps):
        nxt = caps[k + 1]['a'] if k + 1 < len(caps) else c['b'] + 0.45
        gap = nxt - c['b']
        c['b'] = round(min(c['b'] + (gap if gap < 0.6 else 0.35), s['end'] - 0.15), 3)
    s['caps'] = caps

json.dump(cfg, open(f'{SP}/build/story_cfg_v3.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('caps per scene:', {n: len(sc[n].get('caps', [])) for n in range(1, 17)})
print('scene1 sample:', sc[1]['caps'][:3])
print('scene15 sample:', sc[15]['caps'][:3])
