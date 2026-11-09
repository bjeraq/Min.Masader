"""Build the rail story config (scenes, map choreography, inserts, chips) + audio events,
then emit site/gcc-rail-story.html from the rail template."""
import json, math, pathlib

SP = '/tmp/claude-0/-home-user-min-masader/59b58237-73e8-5a26-8661-efeb42e64c46/scratchpad/rail'
BASE = pathlib.Path('/home/user/min.masader/tools/pipeline')
TL = json.load(open(f'{SP}/build/timeline.json'))
S = {s['n']: s for s in TL['scenes']}
GEO = json.load(open(BASE / 'gmap.json'))


def d(n):
    return S[n]['voice_end'] - S[n]['voice']


def at(n, frac=None, off=None, from_end=None):
    s = S[n]
    if from_end is not None:
        return round(s['voice_end'] - from_end, 3)
    if frac is not None:
        return round(s['voice'] + frac * d(n), 3)
    return round(s['voice'] + (off or 0), 3)


NARR = {
    1: 'تخيّل قطاراً ينطلق من الكويت صباحاً، يعبر الدمام والبحرين والدوحة وأبوظبي، ويصل مسقط في اليوم نفسه. هذا وعد اتفاقية وُقّعت هذا الأسبوع. فما القصة؟',
    2: 'في المنامة، وقّع وزراء النقل الستة الاتفاقية العامة لمشروع سكة حديد دول مجلس التعاون: إطار ملزم يوحّد المعايير والالتزامات والجدول الزمني. والهدف المعلن: تشغيل كامل بنهاية عام ألفين وثلاثين.',
    3: 'الشبكة تمتد نحو ألفين ومئة وسبعة عشر كيلومتراً، بقطارات ركاب سرعتها مئتا كيلومتر في الساعة، ويُتوقع أن تنقل ستة ملايين مسافر ومئتي مليون طن بضائع في عامها الأول.',
    4: 'الكويت نقطة الانطلاق: المرحلة الأولى مئة وأحد عشر كيلومتراً، من محطة الشدادية خلف المطار إلى النويصيب على الحدود السعودية، ضمن مخطط كامل بمئتين وخمسة وستين كيلومتراً.',
    5: 'أين وصلت كل دولة؟ الإمارات أنجزت شبكتها وتشغّلها للشحن منذ ألفين وثلاثة وعشرين. خط حفيت بين عُمان والإمارات قطع أربعين في المئة. السعودية والكويت في مرحلة تصميم مقطعي الربط. ووصلتا قطر والبحرين ما زالتا قيد الدراسة.',
    6: 'أُقرّ المشروع عام ألفين وتسعة، وكان مقرراً أن يكتمل عام ألفين وثمانية عشر، فأجّلته سنوات النفط الصعبة. ونسبة الإنجاز المعلنة، خمسة وخمسون فاصلة تسعة في المئة، تعكس الشبكات الوطنية أساساً. ولا نعرف بعد التكلفة، ولا موعد بدء البناء في الكويت.',
    7: 'تقييم مِن مصادر، رأي تحريري، ونصيحتنا للمسؤول: ما يُقاس علناً يصل أسرع. أعلنوا جدول المناقصات والتكلفة، وانشروا نسبة إنجاز المقطع الكويتي كل ثلاثة أشهر، فيتحول موعد ألفين وثلاثين من أمنية إلى التزام.',
    8: 'مِن مصادر. أخبارٌ بمصادرها.',
}

IMG = {1: 's01', 2: 's02', 3: 's01', 4: 's01', 5: 's01', 6: 's03', 7: 's04', 8: 's04'}
KB = {1: (1.0, 1.1, .5, .5), 2: (1.0, 1.09, .5, .45), 3: (1.14, 1.24, .5, .62), 4: (1.1, 1.16, .45, .5),
      5: (1.16, 1.1, .55, .5), 6: (1.0, 1.1, .5, .55), 7: (1.0, 1.1, .5, .5), 8: (1.1, 1.16, .5, .42)}
HEAD = {3: 'شبكة الدول الست', 4: 'المقطع الكويتي', 5: 'أين وصلت كل دولة؟',
        6: 'لماذا طال الانتظار؟', 7: 'نصيحتنا للمسؤول'}

# ---- geography (lon,lat) ----
SHAD = [47.78, 29.20]; NUW = [48.37, 28.54]; DAM = [50.10, 26.43]; MAN = [50.58, 26.22]
SALWA = [50.82, 24.73]; DOHA = [51.53, 25.28]; AUH = [54.37, 24.45]; AIN = [55.74, 24.21]
SOHAR = [56.75, 24.35]; MUS = [58.59, 23.58]
# land-hugging waypoints so the drawn line never crosses the sea
ROUTE = [SHAD, NUW, [48.33, 27.9], [48.9, 27.1], [49.4, 26.7], DAM,
         [50.0, 25.7], [50.4, 25.0], SALWA, [51.3, 24.22], [52.2, 24.02],
         [53.1, 23.95], [53.9, 24.08], AUH, AIN, SOHAR, [57.35, 24.0], [57.95, 23.75], MUS]
I_SHAD, I_NUW, I_DAM, I_SALWA, I_AUH, I_AIN, I_SOHAR, I_MUS = 0, 1, 5, 8, 13, 14, 15, 18

CHIPS = {
    2: [(at(2, off=0.6), 'المنامة · الأحد 8 نوفمبر 2026')],
    3: [(at(3, from_end=1.8), 'الهدف المعلن: ديسمبر 2030')],
    6: [(at(6, off=0.4), '2009: الإقرار في قمة الكويت'),
        (at(6, frac=0.20), 'كان مقرراً اكتماله عام 2018'),
        (at(6, frac=0.40), 'تأجّل.. ثم أُنشئت هيئة السكك 2021')],
    7: [(at(7, frac=0.30), '١· أعلنوا جدول المناقصات والتكلفة'),
        (at(7, frac=0.55), '٢· انشروا نسبة الإنجاز كل 3 أشهر'),
        (at(7, frac=0.84), '2030: من أمنية إلى التزام')],
}
BADGE = {6: (at(6, frac=0.58), '55.9%')}
INS = {3: (1020, [(at(3, frac=0.08), 'train', '2,117 كم'), (at(3, frac=0.38), 'gauge', '200 كم/س'),
                  (at(3, frac=0.60), 'crowd', '6 ملايين مسافر/عام')])}

scenes = []
FADE = 0.5
for n in range(1, 9):
    s = S[n]
    z0, z1, fx, fy = KB[n]
    nxt = S[n + 1]['start'] if n < 8 else s['end']
    scenes.append({
        'n': n, 'start': s['start'], 'end': s['end'], 'voice': s['voice'], 'voice_end': s['voice_end'],
        'img': f"media/rail/{IMG[n]}.jpg", 'kb': [z0, z1, fx, fy],
        'cam': [{'t': s['start'], 'z': z0, 'x': fx, 'y': fy}, {'t': nxt + FADE, 'z': z1, 'x': fx, 'y': fy}],
        'layers': None, 'fx': {},
        'trans': ['none', 'circle', 'slide', 'zoom', 'circle', 'slide', 'zoom', 'circle'][n - 1],
        'head': HEAD.get(n, ''), 'sub': NARR[n],
        'chips': [{'t': t, 'text': x} for t, x in CHIPS.get(n, [])],
        'badge': ({'t': BADGE[n][0], 'text': BADGE[n][1]} if n in BADGE else None),
        'counter': None,
    })
sc = {x['n']: x for x in scenes}
sc[3]['inserts'] = {'top': INS[3][0], 'items': [{'t': t, 'art': a, 'label': l} for t, a, l in INS[3][1]]}
sc[7]['op'] = True
sc[6]['fx'] = {'qmarks': {'n': 5, 'box': [140, 420, 1010, 1040]}}

# ---------- moving-train layers (rembg cutouts, if built) ----------
LAYJ = pathlib.Path('/home/user/min.masader/site/media/rail/layers/layers.json')
if LAYJ.exists():
    LAY = json.load(open(LAYJ))
    for n in range(1, 9):
        if IMG[n] in LAY:
            L = LAY[IMG[n]]
            sc[n]['layers'] = {'bg': L['bg'], 'parts': [dict(p) for p in L['parts']]}
    if 's01' in LAY:
        p = LAY['s01']['parts'][0]
        ang = p.get('ang', 25)
        head = [p['x'] + p['w'] * 0.80, p['y'] + p['h'] * 0.55]
        rear = [p['x'] + p['w'] * 0.10, p['y'] + p['h'] * 0.40]
        for nn in (1, 3):
            sc[nn]['fx'] = dict(sc[nn].get('fx') or {})
            sc[nn]['fx']['speedlines'] = {'x': head[0], 'y': head[1], 'ang': ang, 'n': 7}
            sc[nn]['fx']['puffs'] = {'x': rear[0], 'y': rear[1], 'ang': ang}

# ---------- map choreography ----------
def P(ll):
    return [(ll[0] - GEO['lon0']) * GEO['cos'] * GEO['k'], (GEO['lat1'] - ll[1]) * GEO['k']]


def arc(pts):
    px = [P(p) for p in pts]
    acc = [0.0]
    for a, b in zip(px, px[1:]):
        acc.append(acc[-1] + math.hypot(b[0] - a[0], b[1] - a[1]))
    return acc


# scene 1: route draw + train, stops pop when passed
r1_t0 = at(1, off=1.5); r1_t1 = at(1, from_end=4.4)
S1 = sc[1]
S1['gmap'] = {
    't_in': at(1, off=1.0),
    'route': {'pts': ROUTE, 't0': r1_t0, 't1': r1_t1,
              'branches': [[DAM, MAN], [SALWA, DOHA]],
              'stops': [
                  {'ll': SHAD, 'at': I_SHAD, 'name': 'الكويت', 'fs': 28, 'dy': -34},
                  {'ll': DAM, 'at': I_DAM, 'name': 'الدمام', 'fs': 24, 'dy': -30},
                  {'ll': AUH, 'at': I_AUH, 'name': 'أبوظبي', 'fs': 24, 'dy': 34},
                  {'ll': MUS, 'at': I_MUS, 'name': 'مسقط', 'fs': 24, 'dy': -30},
              ]},
    'labels': [
        {'text': 'البحرين', 'll': MAN, 't': r1_t1 + 0.35, 'dy': -28, 'fs': 22},
        {'text': 'الدوحة', 'll': DOHA, 't': r1_t1 + 0.5, 'dy': -28, 'fs': 22},
    ],
}
# pop times when the train passes each stop (draw progress uses cosine ease)
acc1 = arc(ROUTE); L1 = acc1[-1]
stop_pops = []
for st in S1['gmap']['route']['stops']:
    f = acc1[st['at']] / L1
    k = math.acos(max(-1, min(1, 1 - 2 * f))) / math.pi
    stop_pops.append(round(r1_t0 + k * (r1_t1 - r1_t0), 3))

# scene 4: zoom to Kuwait, draw the 111 km segment
seg_t0 = at(4, frac=0.18); seg_t1 = at(4, frac=0.42)
S4 = sc[4]
S4['gmap'] = {
    't_in': S4['start'] + 0.25,
    'zoom': {'t': S4['start'] + 0.45, 'z': 4.6, 'll': [48.05, 28.9]},
    'kwfill': at(4, off=0.2),
    'seg': {'pts': [SHAD, NUW], 't0': seg_t0, 't1': seg_t1},
    'labels': [
        {'text': 'الشدادية', 'll': SHAD, 't': seg_t0 + 0.2, 'dy': -36, 'fs': 30},
        {'text': 'النويصيب', 'll': NUW, 't': seg_t1, 'dy': 38, 'fs': 30},
        {'text': '111 كم', 'll': [48.02, 28.92], 't': seg_t1 + 0.35, 'dy': -14, 'fs': 36, 'cls': 'tag'},
        {'text': 'المخطط الكامل: 265 كم', 'll': [47.62, 28.42], 't': at(4, frac=0.82), 'dy': 40, 'fs': 24,
         'bg': '#fbe8da', 'fg': '#b8561b'},
    ],
}

# scene 5: per-country status
S5 = sc[5]
lit = [
    {'c': 'ARE', 't': at(5, frac=0.10), 'col': '#bfe7cd'},
    {'c': 'OMN', 't': at(5, frac=0.34), 'col': '#aee6e0'},
    {'c': 'SAU', 't': at(5, frac=0.56), 'col': '#f3e6b8'},
    {'c': 'KWT', 't': at(5, frac=0.66), 'col': '#f6c9a9', 'hold': True},
    {'c': 'QAT', 't': at(5, frac=0.86), 'col': '#e6e3dc'},
    {'c': 'BHR', 't': at(5, frac=0.86), 'col': '#e6e3dc'},
]
S5['gmap'] = {
    't_in': S5['start'] + 0.25,
    'lit': lit,
    'labels': [
        {'text': 'الإمارات · شبكة تعمل', 'll': [54.3, 23.6], 't': lit[0]['t'] + 0.15, 'fs': 23,
         'bg': '#dff2e5', 'fg': '#20603c'},
        {'text': 'عُمان · حفيت %40', 'll': [56.6, 21.2], 't': lit[1]['t'] + 0.15, 'fs': 23,
         'bg': '#d9eeee', 'fg': '#0f6b6b'},
        {'text': 'السعودية · تصميم المقطع', 'll': [45.6, 24.2], 't': lit[2]['t'] + 0.15, 'fs': 23,
         'bg': '#f7efc9', 'fg': '#7a610e'},
        {'text': 'الكويت · تصميم المقطع', 'll': [47.5, 30.35], 't': lit[3]['t'] + 0.15, 'fs': 26,
         'bg': '#fbe8da', 'fg': '#b8561b'},
        {'text': 'قطر · قيد الدراسة', 'll': [52.1, 24.35], 't': lit[4]['t'] + 0.15, 'fs': 22},
        {'text': 'البحرين · قيد الدراسة', 'll': [51.5, 27.1], 't': lit[5]['t'] + 0.35, 'fs': 22},
    ],
}

cfg = {'total': TL['total'], 'scenes': scenes, 'geo': GEO}

# ---------- audio events ----------
ev = []
ev.append(['deepwhoosh', 0.05, 0.9])
for n in range(2, 9):
    ev.append(['whoosh', round(S[n]['start'] - 0.12, 3), 0.8])
# scene 1: horn + chug while the route draws, pops at stops
ev.append(['horn', round(r1_t0 + 0.1, 3), 0.8])
ev.append(['chug', round(r1_t0, 3), 0.9])
for t in stop_pops:
    ev.append(['pop', t, 0.55])
ev.append(['pop', S1['gmap']['labels'][0]['t'], 0.4])
ev.append(['pop', S1['gmap']['labels'][1]['t'], 0.4])
# scene 2
ev.append(['stamp', at(2, frac=0.30), 0.9])
ev.append(['pop', CHIPS[2][0][0], 0.55])
# scene 3
for it in sc[3]['inserts']['items']:
    ev.append(['pop', it['t'], 0.5])
ev.append(['pop', CHIPS[3][0][0], 0.55])
# scene 4
ev.append(['whoosh', S4['gmap']['zoom']['t'], 0.5])
ev.append(['chug', seg_t0, 0.5])
ev.append(['ding', seg_t1 + 0.05, 0.9])
ev.append(['pop', seg_t1 + 0.35, 0.55])
ev.append(['pop', at(4, frac=0.82), 0.5])
# scene 5
for L in lit:
    ev.append(['pop', L['t'], 0.45])
ev.append(['ding', lit[3]['t'] + 0.15, 0.8])
# scene 6: clock between first two chips, pops, bigpop for the badge
tt = CHIPS[6][0][0] + 0.1
while tt < CHIPS[6][2][0]:
    ev.append(['clock', round(tt, 3), 0.5]); tt += 0.5
for t, _ in CHIPS[6]:
    ev.append(['pop', t, 0.5])
ev.append(['bigpop', BADGE[6][0], 1.0])
# scene 7
ev.append(['ding', S[7]['start'] + 0.5, 0.7])
for t, _ in CHIPS[7]:
    ev.append(['pop', t, 0.5])
# outro
ev.append(['horn', S[8]['start'] + 0.15, 0.5])
ev.append(['chime', S[8]['start'] + 0.3, 0.9])

json.dump(cfg, open(f'{SP}/build/story_cfg_rail.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
json.dump(ev, open(f'{SP}/build/events_rail.json', 'w'), indent=0)
print('scenes', len(scenes), 'events', len(ev), 'total', cfg['total'])
print('stop pops', stop_pops)

# ---------- emit the page ----------
tpl = (BASE / 'rail' / 'story_template_rail.html').read_text(encoding='utf-8')
assert '__CFG__' in tpl
page = tpl.replace('__CFG__', json.dumps(cfg, ensure_ascii=False, separators=(',', ':')))
out = pathlib.Path('/home/user/min.masader/site/gcc-rail-story.html')
out.write_text(page, encoding='utf-8')
print('page', out, len(page))
