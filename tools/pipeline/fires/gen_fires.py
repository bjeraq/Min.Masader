"""Build the oil-fires story config (8 scenes: images, chips, badge, inserts, Kuwait fire map, captions)
+ audio events, then emit site/kuwait-oil-fires-story.html from story_template_fires.html."""
import json, math, os, pathlib, random

SP = os.environ.get('SP', '/tmp/claude-0/-home-user-Min-Masader/0d5c69df-74a2-5d9e-8326-acc5fdf4f588/scratchpad/fires')
HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent.parent.parent
TL = json.load(open(f'{SP}/build/timeline.json'))
S = {s['n']: s for s in TL['scenes']}
OFFS = {int(k): v for k, v in json.load(open(f'{SP}/build/concat_offs.json')).items()}
WORDS = json.load(open(f'{SP}/build/words_raw.json', encoding='utf-8'))
GEO = json.load(open(HERE.parent / 'gmap.json'))
N = 8

# ---------- word timings -> final video time ----------
W = []   # (scene, word, a, b)
for w, a, b in WORDS:
    mid = (a + b) / 2000.0
    n = max(k for k in OFFS if OFFS[k]['off'] <= mid + 1e-6)
    v = S[n]['voice']; o = OFFS[n]['off']
    W.append((n, w, round(v + a / 1000.0 - o, 3), round(v + b / 1000.0 - o, 3)))


def wt(n, word, occ=1):
    """start time of the occ-th occurrence of `word` in scene n."""
    k = 0
    for sn, w, a, b in W:
        if sn == n and w == word:
            k += 1
            if k == occ:
                return a
    raise KeyError((n, word, occ))


def at(n, frac):
    s = S[n]
    return round(s['voice'] + frac * (s['voice_end'] - s['voice']), 3)


IMG = {1: 'pd1', 2: 'pd2', 3: 'pd3', 4: 'pd4', 5: 's06', 6: 's03', 7: 'pd5', 8: 's01'}
CREDIT = {1: 'صورة: وزارة الدفاع الأمريكية · مارس 1991 · ملكية عامة',
          2: 'صورة: سلاح المهندسين الأمريكي · مارس 1991 · ملكية عامة',
          3: 'صورة: ناسا · مكوك الفضاء · 7 أبريل 1991 · ملكية عامة',
          4: 'صورة: وزارة الدفاع الأمريكية · 7 أبريل 1991 · ملكية عامة',
          7: 'صورة: مشاة البحرية الأمريكية · الرميلة · 27 مارس 2003 · ملكية عامة'}
KB = {1: (1.0, 1.12, .5, .5), 2: (1.0, 1.1, .5, .5), 3: (1.05, 1.15, .5, .5), 4: (1.0, 1.06, .5, .56),
      5: (1.0, 1.1, .5, .55), 6: (1.12, 1.04, .5, .55), 7: (1.0, 1.08, .5, .56), 8: (1.1, 1.18, .55, .5)}
HEAD = {3: 'الحقول تحترق', 6: 'أسماء من القصة', 7: 'من 1991 إلى 2003'}
NARR = {
    1: 'في 6 نوفمبر 1991 أُطفئت آخر بئر نفط مشتعلة في الكويت: برقان 118. وخلف هذه اللحظة فريقٌ كويتي دخل النار بخبرةٍ قليلة.',
    2: 'في فبراير 1991 أشعلت القوات العراقية المنسحبة النار في 737 بئراً، بحسب كونا.',
    3: 'كانت الآبار تحرق ما بين 4 و6 ملايين برميل يومياً، والدخان امتد إلى دول الجوار.',
    4: 'قُدّر أن الإطفاء سيستغرق سنوات، فجاء 27 فريقاً من نحو 10 دول، وارتفع الإطفاء من بئر يومياً إلى 8.5.',
    5: 'في 9 سبتمبر 1991 تشكّل فريق كويتي من نحو 30 موظفاً في نفط الكويت، وأطفأ 41 بئراً حتى نوفمبر.',
    6: 'سارة أكبر، العضوة الوحيدة في الفريق، وإسحاق القائد، كبير آمري الإطفاء الأسبق.',
    7: 'في 2003 توجه إطفائيون كويتيون إلى حقول الرميلة في العراق.',
    8: 'مِن مصادر. أخبارٌ بمصادرها.',
}
CHIPS = {
    1: [(wt(1, 'نوفمبر') - 0.2, '6 نوفمبر 1991'),
        (wt(1, 'برقان') - 0.1, 'آخر بئر: «برقان 118»'),
        (wt(1, 'فريق') - 0.1, 'فريقٌ كويتي دخل النار')],
    4: [(wt(4, '27') - 0.2, '27 فريقاً من نحو 10 دول'),
        (wt(4, 'ثماني') - 0.1, 'من بئر يومياً ← 8.5 آبار يومياً')],
    5: [(wt(5, 'التاسع') - 0.2, '9 سبتمبر 1991'),
        (wt(5, '30') - 0.2, 'نحو 30 كويتياً · شركة نفط الكويت'),
        (wt(5, 'قاتل') - 0.2, '«Kuwait Wild Well Killers»')],
    7: [(wt(7, 'اطفائيون') - 0.1, 'إطفائيون كويتيون في الميدان'),
        (wt(7, 'الرميله') - 0.2, 'حقول الرميلة · العراق · 2003')],
}
BADGE = {2: {'t': wt(2, '737') - 0.15, 'text': '737', 'label': 'بئراً أُضرمت فيها النار · بحسب كونا'}}
INS = {}
PERSONS = {6: [{'t': round(wt(6, 'ساره') - 0.5, 3), 't_out': round(wt(6, 'واشاد') - 0.25, 3), 'name': 'سارة أكبر',
                'role': 'مهندسة · عضوة في الفريق', 'fact': 'العضوة الوحيدة في الفريق، وكرّمتها الأمم المتحدة عام 1993'},
               {'t': round(wt(6, 'واشاد') - 0.1, 3), 't_out': 999, 'name': 'إسحاق القائد',
                'role': 'كبير آمري الإطفاء الأسبق', 'fact': 'أشاد بإطفاء الفريق 41 بئراً رغم قلة خبرته'}]}
COUNTER = {5: {'t0': round(wt(5, 'وحتى') - 0.2, 3), 't1': round(wt(5, '41') + 0.6, 3), 'a': 0, 'b': 41,
               'unit': 'بئراً', 'note': 'أطفأها الفريق الكويتي حتى نوفمبر 1991'}}

scenes = []
FADE = 0.5
TRANS = ['none', 'zoom', 'circle', 'slide', 'zoom', 'circle', 'slide', 'zoom']
for n in range(1, N + 1):
    s = S[n]
    z0, z1, fx, fy = KB[n]
    nxt = S[n + 1]['start'] if n < N else s['end']
    scenes.append({
        'n': n, 'start': s['start'], 'end': s['end'], 'voice': s['voice'], 'voice_end': s['voice_end'],
        'img': f"media/fires/{IMG[n]}.jpg", 'kb': [z0, z1, fx, fy],
        'cam': [{'t': s['start'], 'z': z0, 'x': fx, 'y': fy}, {'t': nxt + FADE, 'z': z1, 'x': fx, 'y': fy}],
        'layers': None, 'fx': {}, 'trans': TRANS[n - 1],
        'head': HEAD.get(n, ''), 'sub': NARR[n], 'credit': CREDIT.get(n, ''),
        'chips': [{'t': round(t, 3), 'text': x} for t, x in CHIPS.get(n, [])],
        'badge': BADGE.get(n), 'counter': COUNTER.get(n), 'persons': PERSONS.get(n, []),
    })
sc = {x['n']: x for x in scenes}

# ---------- Kuwait fire map ----------
FIELDS = [  # name, centre (lon,lat), spread (deg), share of fire glyphs, label dy
    ('برقان', (47.97, 28.97), (0.10, 0.08), 0.52, 0),
    ('المقوع والأحمدي', (48.07, 29.10), (0.035, 0.03), 0.10, -46),
    ('المناقيش', (47.55, 29.04), (0.05, 0.04), 0.09, -44),
    ('أم قدير', (47.70, 28.84), (0.04, 0.03), 0.07, 44),
    ('الوفرة', (47.93, 28.58), (0.05, 0.03), 0.06, 44),
    ('الروضتين', (47.70, 29.84), (0.05, 0.05), 0.10, -46),
    ('الصابرية', (47.97, 29.80), (0.04, 0.035), 0.06, 44),
]
NF = 150
rng = random.Random(7)
pts = []
for name, (lo, la), (sx, sy), share, _ in FIELDS:
    for _ in range(max(1, round(NF * share))):
        pts.append([round(lo + rng.gauss(0, sx * 0.55), 4), round(la + rng.gauss(0, sy * 0.55), 4)])
rng.shuffle(pts)
ZOOM = {'z': 7.2, 'll': [47.74, 29.22]}

# scene 3: fires ignite in a quick cascade, smoke drifts south-east
S3 = sc[3]
ig0 = S3['start'] + 0.7; ig1 = ig0 + 3.2
fires3 = []
for k, p in enumerate(pts):
    u = k / len(pts)
    fires3.append([p[0], p[1], round(ig0 + (ig1 - ig0) * (u ** 0.8) + rng.uniform(0, 0.15), 3), None])
S3['gmap'] = {
    't_in': S3['start'] + 0.2, 'zoom': {'t': S3['start'] - 1, 'z': ZOOM['z'], 'll': ZOOM['ll']},
    'kwfill': S3['start'], 'kwcol': '#ead6bd', 'fires': fires3, 'fsize': 0.9,
    'smoke': {'t0': ig0 + 0.6, 'll': [47.98, 28.98], 'dir': [0.55, 0.835], 'len': 420, 'wid': 220, 'r': 80,
              'n': 34, 'period': 4.6, 'grow': 3.5, 'op': 0.20},
    'labels': [{'text': f[0], 'll': list(f[1]), 't': ig0 + 0.4 + 0.25 * j, 'dy': f[4], 'fs': 26 if j else 32,
                'cls': 'kw' if j == 0 else ''} for j, f in enumerate(FIELDS) if f[0] != 'المقوع والأحمدي']
              + [{'text': '4–6 ملايين برميل يومياً', 'll': [47.25, 30.32], 't': wt(3, 'ملايين') - 0.2, 'fs': 34, 'cls': 'tag'},
                 {'text': 'الدخان ← دول الجوار', 'll': [48.25, 28.45], 't': wt(3, 'والدخان') - 0.1, 'fs': 28,
                  'bg': '#2b2f33', 'fg': '#ffffff'}],
}

# scene 4: all burning, then they go out one by one while a month ticker runs Mar -> Nov 1991
S4 = sc[4]
o0 = S4['start'] + 1.0; o1 = S4['voice_end'] - 0.4
order = list(range(len(pts))); rng.shuffle(order)
fires4 = [None] * len(pts)
for rank, k in enumerate(order):
    u = rank / (len(pts) - 1)
    fires4[k] = [pts[k][0], pts[k][1], S4['start'] - 2, round(o0 + (o1 - o0) * (u ** 1.15), 3)]
# the last one to go out is a Burgan well
bidx = min(range(len(pts)), key=lambda k: (pts[k][0] - 47.97) ** 2 + (pts[k][1] - 28.97) ** 2)
fires4[bidx][3] = round(o1 + 0.25, 3)
MONTHS = ['مارس', 'أبريل', 'مايو', 'يونيو', 'يوليو', 'أغسطس', 'سبتمبر', 'أكتوبر', 'نوفمبر']
tick = [[round(o0 - 0.6 + (o1 - o0) * j / (len(MONTHS) - 1), 3), f'{m} 1991'] for j, m in enumerate(MONTHS)]
tick[-1][1] = '6 نوفمبر 1991'
S4['gmap'] = {
    't_in': S4['start'] + 0.2, 'zoom': {'t': S4['start'] - 1, 'z': ZOOM['z'], 'll': ZOOM['ll']},
    'kwfill': S4['start'] - 1, 'kwcol': '#ead6bd', 'fires': fires4, 'fsize': 0.9,
    'ticker': {'ll': [47.25, 29.95], 'dy': 0, 'fs': 40, 'items': tick},
    'labels': [{'text': 'آخر بئر: برقان 118', 'll': [pts[bidx][0], pts[bidx][1]], 't': o1 + 0.5, 'dy': 46, 'fs': 30,
                'bg': '#0f6b6b', 'fg': '#ffffff'}],
}

# ---------- captions (two words per card; sentence ends break groups) ----------
FIX = {'اطفئ': 'أُطفئت', 'اخر': 'آخر', 'مشتعله': 'مشتعلة', 'اللحظه': 'اللحظة', 'بخبره': 'بخبرةٍ', 'قليله': 'قليلة',
       '91': '1991', 'اشعلت': 'أشعلت', 'العراقيه': 'العراقية', 'المنسحبه': 'المنسحبة', 'بئرا': 'بئراً',
       'وكاله': 'وكالة', 'الانباء': 'الأنباء', 'الكويتيه': 'الكويتية', 'الابار': 'الآبار', 'اربعة': '4', 'وستة': 'و6',
       'يوميا': 'يومياً', 'الى': 'إلى', 'امتد': 'امتدّ', 'قدر': 'قُدّر', 'ان': 'أن', 'الاطفاء': 'الإطفاء',
       'فريقا': 'فريقاً', 'عشر': '10', 'واحده': 'واحدة', 'ثماني': '8.5', 'ابار': 'آبار', 'ونصف': '',
       'تشكل': 'تشكّل', 'موظفا': 'موظفاً', 'شركه': 'شركة', 'عرف': 'عُرف', 'قاتل': 'قاتلو', 'الجامحه': 'الجامحة',
       'اطفى': 'أطفأ', 'اعضائه': 'أعضائه', 'ساره': 'سارة', 'اكبر': 'أكبر', 'العضوه': 'العضوة', 'كرمتها': 'كرّمتها',
       'الامم': 'الأمم', 'المتحده': 'المتحدة', 'واشاد': 'وأشاد', 'امري': 'آمري', 'الاسبق': 'الأسبق',
       'اسحاق': 'إسحاق', 'باطفاء': 'بإطفاء', 'قله': 'قلة', 'مدرسه': 'مدرسة', 'توجه': 'توجّه', 'اطفائيون': 'إطفائيون',
       'الرميله': 'الرميلة', 'لاطفاء': 'لإطفاء', 'مشتعله': 'مشتعلة'}
per = {n: [] for n in range(1, N + 1)}
for n, w, a, b in W:
    end = w.endswith('.'); w0 = w.rstrip('.')
    fx = FIX.get(w0, w0)
    if fx == '' and per[n]:
        per[n][-1] = (per[n][-1][0], per[n][-1][1], b, end); continue
    per[n].append((fx, a, b, end))
for n in range(1, N):
    caps = []; grp = []
    for tok in per[n]:
        grp.append(tok)
        if len(grp) == 2 or tok[3]:
            caps.append(grp); grp = []
    if grp:
        caps.append(grp)
    out = []
    for j, g in enumerate(caps):
        a = g[0][1]; b = g[-1][2]
        nxt = caps[j + 1][0][1] if j + 1 < len(caps) else S[n]['voice_end'] + 0.2
        out.append({'a': round(a, 3), 'b': round(min(max(b + 0.15, a + 0.35), nxt), 3), 'w': ' '.join(x[0] for x in g)})
    sc[n]['caps'] = out

cfg = {'total': TL['total'], 'scenes': scenes, 'geo': GEO}

# ---------- audio events ----------
ev = [['deepwhoosh', 0.05, 0.8]]
for n in range(2, N + 1):
    ev.append(['whoosh', round(S[n]['start'] - 0.12, 3), 0.7])
for n, lst in CHIPS.items():
    for t, _ in lst:
        ev.append(['pop', round(t, 3), 0.5])
for n, b in BADGE.items():
    ev.append(['bigpop', round(b['t'], 3), 0.9])
for n, (_, items) in INS.items():
    for t, _, _ in items:
        ev.append(['pop', round(t, 3), 0.5])
ev.append(['crackle', round(S[2]['start'] + 0.2, 3), 0.55])
ev.append(['rumble', round(ig0 - 0.2, 3), 0.8])
ev.append(['crackle', round(ig0, 3), 0.6])
for it in tick[1:]:
    ev.append(['tick', it[0], 0.5])
ev.append(['ding', round(o1 + 0.3, 3), 0.9])
ev.append(['ding', round(CHIPS[4][1][0], 3), 0.6])
ev.append(['chime', round(S[8]['start'] + 0.3, 3), 0.9])
for n, lst in PERSONS.items():
    for q in lst:
        ev.append(['whoosh', round(q['t'] - 0.05, 3), 0.45]); ev.append(['pop', round(q['t'] + 0.2, 3), 0.5])
for n, c in COUNTER.items():
    k = 0
    while k <= 41:
        ev.append(['tick', round(c['t0'] + (c['t1'] - c['t0']) * (k / 41) ** 0.6, 3), 0.35]); k += 3
    ev.append(['ding', round(c['t1'] + 0.05, 3), 0.9])
ev.sort(key=lambda e: e[1])

os.makedirs(f'{SP}/build', exist_ok=True)
json.dump(cfg, open(f'{SP}/build/story_cfg_fires.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
json.dump(ev, open(f'{SP}/build/events_fires.json', 'w'), indent=0)
print('scenes', len(scenes), 'fires', len(pts), 'events', len(ev), 'total', cfg['total'])

tpl = (HERE / 'story_template_fires.html').read_text(encoding='utf-8')
assert '__CFG__' in tpl
page = tpl.replace('__CFG__', json.dumps(cfg, ensure_ascii=False, separators=(',', ':')))
out = ROOT / 'site' / 'kuwait-oil-fires-story.html'
out.write_text(page, encoding='utf-8')
print('page', out, len(page))
