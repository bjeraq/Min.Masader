"""Word-pair captions for the rail story: map raw-concat word timings to final video time,
clean spelling, group 2 words (sentence ends break groups), inject into story_cfg_rail.json
and re-emit the page."""
import json, subprocess, pathlib

SP = '/tmp/claude-0/-home-user-min-masader/59b58237-73e8-5a26-8661-efeb42e64c46/scratchpad/rail'
BASE = pathlib.Path('/home/user/min.masader/tools/pipeline')
WORDS = json.load(open(f'{SP}/build/words_raw.json'))
OFFS = {int(k): v for k, v in json.load(open(f'{SP}/build/concat_offs.json')).items()}
TL = {s['n']: s for s in json.load(open(f'{SP}/build/timeline.json'))['scenes']}
cfg = json.load(open(f'{SP}/build/story_cfg_rail.json', encoding='utf-8'))
N = 8

FIX = {'تخيل': 'تخيّل', 'قطارا': 'قطاراً', 'صباحا': 'صباحاً', 'وابو': 'وأبوظبي', 'ظبي': '',
       'الاسبوع': 'الأسبوع', 'وقع': 'وقّع', 'وقعت': 'وُقّعت', 'اطار': 'إطار', 'يوحد': 'يوحّد',
       'اين': 'أين', 'الامارات': 'الإمارات', 'انجزت': 'أنجزت', 'وتشغلها': 'وتشغّلها',
       'عمان': 'عُمان', 'والامارات': 'والإمارات', 'اقر': 'أُقرّ', 'اصلي': 'أصلي',
       'فأجلته': 'فأجّلته', 'الانجاز': 'الإنجاز', 'اساسا': 'أساساً', 'علنا': 'علناً',
       'اسرع': 'أسرع', 'اعلنوا': 'أعلنوا', 'انجاز': 'إنجاز', 'اشهر': 'أشهر', 'الى': 'إلى',
       'الاول': 'الأول', 'الاولى': 'الأولى', 'اخبار': 'أخبارٌ', 'أن': 'أن', 'ب265': 'بـ265',
       '2117': '2,117', 'النويص': 'النويصيب', 'صيب': ''}


def clean(w):
    base = w.rstrip('.،,؟')
    return FIX.get(base, base)


# stretched/raw ratio per clip
ratio = {}
for n in range(1, N + 1):
    d = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0',
                              f'{SP}/narr_f/n{n:02d}.wav'], capture_output=True, text=True).stdout)
    ratio[n] = d / OFFS[n]['dur']

per = {n: [] for n in range(1, N + 1)}
for w, a, b in WORDS:
    mid = (a + b) / 2000.0
    n = max(k for k in OFFS if OFFS[k]['off'] <= mid)
    if mid > OFFS[n]['off'] + OFFS[n]['dur'] + 0.05:
        n = min(n + 1, N)
    r = ratio[n]; v = TL[n]['voice']; o = OFFS[n]['off']
    end_s = w.rstrip('،,').endswith(('.', '؟'))
    per[n].append([w, v + (a / 1000.0 - o) * r, v + (b / 1000.0 - o) * r, end_s])

for n in per:
    assert per[n], n

sc = {s['n']: s for s in cfg['scenes']}
for n, words in per.items():
    s = sc[n]
    if n in (2, 8):   # title card / outro carry their own big text — but scene 2 narration matters,
        pass          # keep captions on 2 (title fades mid-scene in render? it does not) -> skip below
    if n == 8:
        s.pop('caps', None)
        continue
    # merge special pairs: (وابو+ظبي) -> وأبوظبي ; (النويص+صيب) -> النويصيب ; (من+مصادر) brand
    toks = []
    i = 0
    while i < len(words):
        w, a0, b0, e0 = words[i]
        cw = clean(w)
        if i + 1 < len(words) and clean(words[i + 1][0]) == '':
            toks.append((cw, a0, words[i + 1][2], words[i + 1][3], True)); i += 2; continue
        if w == 'من' and i + 1 < len(words) and words[i + 1][0].startswith('مصادر'):
            toks.append(('مِن مصادر', a0, words[i + 1][2], words[i + 1][3], True)); i += 2; continue
        toks.append((cw, a0, b0, e0, False))
        i += 1
    caps = []
    k = 0
    while k < len(toks):
        grp = [toks[k]]
        if not toks[k][3] and k + 1 < len(toks) and not toks[k][4]:
            grp.append(toks[k + 1])
        t0 = grp[0][1]; t1 = grp[-1][2]
        caps.append({'a': round(t0, 3), 'b': round(t1, 3), 'w': ' '.join(g[0] for g in grp)})
        k += len(grp)
    for k2, c in enumerate(caps):
        nxt = caps[k2 + 1]['a'] if k2 + 1 < len(caps) else c['b'] + 0.45
        gap = nxt - c['b']
        c['b'] = round(min(c['b'] + (gap if gap < 0.6 else 0.35), s['end'] - 0.15), 3)
    s['caps'] = caps

# scene 2: shorten the title display so captions don't fight it? keep title; captions sit lower. fine.
json.dump(cfg, open(f'{SP}/build/story_cfg_rail.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

tpl = (BASE / 'rail' / 'story_template_rail.html').read_text(encoding='utf-8')
page = tpl.replace('__CFG__', json.dumps(cfg, ensure_ascii=False, separators=(',', ':')))
pathlib.Path('/home/user/min.masader/site/gcc-rail-story.html').write_text(page, encoding='utf-8')
print('caps per scene:', {n: len(sc[n].get('caps', [])) for n in range(1, N + 1)})
print('s1:', sc[1]['caps'][:3])
print('s7:', sc[7]['caps'][:3])
