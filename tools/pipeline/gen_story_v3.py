"""v3+: illustrated 'sticker' inserts timed to spoken mentions, animated GCC map in scene 4,
editorial-verdict extras for scenes 14/15 (v5)."""
import json

SP = '/tmp/claude-0/-home-user-Advisers/43f3f876-332f-5c13-8812-05a26eedb0e5/scratchpad'
cfg = json.load(open(f'{SP}/build/story_cfg_v2.json', encoding='utf-8'))
AL = json.load(open(f'{SP}/build/align.json', encoding='utf-8'))
EV = json.load(open(f'{SP}/build/events.json'))
sc = {s['n']: s for s in cfg['scenes']}

# scene -> (row top in px, [(spoken key, art, label)])
INS = {
    1: (1180, [('علبة طاقة', 'can_energy', 'مشروب طاقة'), ('ومشروب غازي', 'can_red', 'مشروب غازي'),
              ('وعلبة سجائر', 'cigpack', 'سجائر'), ('في الكويت', 'towers', 'الكويت')]),
    2: (1330, [('الضريبة', 'can_energy', ''), ('الانتقائية', 'can_red', ''), ('الخليجية', 'cigpack', '')]),
    3: (600, [('مجلس الوزراء', 'building', 'مجلس الوزراء'), ('الاتفاقية الخليجية', 'gcc', 'اتفاقية خليجية')]),
    5: (600, [('ضارة بالصحة', 'heartcrack', 'الصحة'), ('سعر البيع', 'pricetag', 'سعر التجزئة')]),
    6: (980, [('التبغ', 'cigpack', 'سجائر'), ('ومشتقاته', 'shisha', 'معسّل'), ('السجائر الإلكترونية', 'vape', 'سجائر إلكترونية')]),
    7: (980, [('ومشروبات الطاقة', 'cans_energy', 'مشروبات الطاقة')]),
    8: (980, [('والمشروبات الغازية', 'cans_soda', 'مشروبات غازية')]),
    9: (600, [('المشروبات المحلّاة', 'juice', 'مشروبات محلّاة'), ('كمية السكر', 'sugar', 'حسب السكر'), ('الدايت معفاة', 'zerocan', 'دايت: معفاة')]),
    10: (1000, [('فعلبة طاقة', 'can_energy', '500 فلس'), ('بدينار كامل', 'banknote', '1 دينار')]),
    11: (720, [('تقليل الاستهلاك', 'cansdown', 'استهلاك أقل'), ('عن النفط', 'barrel', 'بعيداً عن النفط'), ('مئتي مليون', 'money', '~200 مليون د.ك')]),
    12: (600, [('قانوناً محلياً', 'law', 'قانون محلي'), ('الآلية والإجراءات', 'gears', 'الإجراءات')]),
    13: (1110, [('موعد التطبيق', 'calendar:؟', 'الموعد'), ('في الكويت', 'kwskyline', 'النسب في الكويت'), ('سترتفع الأسعار', 'pricetag_up', 'الأسعار')]),
    14: (600, [('منظمة الصحة', 'globehealth', 'توصية أممية'), ('والسعودية والإمارات', 'calendar:2017', 'منذ 2017'), ('المكسيك', 'cansdown', 'شراء أقل')]),
    15: (1060, [('إيجابية من حيث المبدأ', 'scalecheck', 'إيجابية بشروط')]),
}


def t_rel(n, key):
    a = AL[str(n)]
    i = a['text'].find(key)
    assert i >= 0, (n, key)
    anchors = sorted({(c, t) for c, t in a['anchors']})
    t = anchors[-1][1]
    for (c0, t0), (c1, t1) in zip(anchors, anchors[1:]):
        if c0 <= i <= c1:
            t = t0 + (t1 - t0) * ((i - c0) / max(1, c1 - c0))
            break
    starts = [s for s, _ in a['segments']]
    near = [s for s in starts if abs(s - t) < 0.45]
    if near:
        t = min(near, key=lambda s: abs(s - t))
    return t


events = list(EV)
for n, (top, items) in INS.items():
    s = sc[n]
    prev = s['start'] + 0.2
    out = []
    for key, art, label in items:
        t = max(prev, s['voice'] + t_rel(n, key) - 0.12)
        out.append({'t': round(t, 3), 'art': art, 'label': label})
        events.append(['pop', round(t, 3), 0.45])
        prev = t + 0.35
    s['inserts'] = {'top': top, 'items': out}
# scene 10: the sticker cards replace the face punch-in, keep a gentle push towards the father
S10 = sc[10]
S10['cam'] = [{'t': S10['start'], 'z': 1.0, 'x': .45, 'y': .42}, {'t': S10['end'] + 0.5, 'z': 1.12, 'x': .5, 'y': .4}]

# scene 4: animated GCC map replaces the chips + cards
S4 = sc[4]
v4 = S4['voice']
old_chip_t = {c['t'] for c in S4['chips']}
events = [e for e in events if not (e[0] == 'pop' and e[1] in old_chip_t)]
S4['chips'] = []
S4['fx'] = {}
S4['shake'] = []
t_ama = v4 + t_rel(4, 'أما الكويت')
ta = max(v4 + 0.35, v4 + t_rel(4, 'تطبقها'))
tb = max(ta + 1.2, t_ama - 0.8)
order = ['SAU', 'ARE', 'BHR', 'QAT', 'OMN']
lit = [{'c': c, 't': round(ta + (tb - ta) * k / (len(order) - 1), 3)} for k, c in enumerate(order)]
t_ama = v4 + t_rel(4, 'أما الكويت')
t_kw = t_ama + 0.45
S4['gmap'] = {'t_in': round(S4['start'] + 0.25, 3), 'lit': lit, 't_leg': round(v4 + t_rel(4, 'ألفين وسبعة عشر'), 3),
              't_zoom': round(t_ama - 0.15, 3), 'zoom': 4.0, 'kw': [47.55, 29.3], 't_kw': round(t_kw, 3),
              't_tag': round(max(v4 + t_rel(4, 'فلم تطبقها'), t_kw + 0.5), 3)}
for L in lit:
    events.append(['pop', L['t'], 0.4])
events.append(['whoosh', round(t_ama - 0.15, 3), 0.35])
events.append(['stamp', round(t_kw + 0.3, 3), 0.7])
events.append(['pop', S4['gmap']['t_tag'], 0.5])

# scene 15: opinion badge + a ding when the verdict card lands
S15 = sc[15]
S15['op'] = True
events.append(['ding', round(S15['inserts']['items'][0]['t'] + 0.05, 3), 0.8])

cfg['geo'] = json.load(open(f'{SP}/build/gmap.json'))
cfg['total'] = json.load(open(f'{SP}/build/timeline.json'))['total']

json.dump(cfg, open(f'{SP}/build/story_cfg_v3.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
json.dump(events, open(f'{SP}/build/events_v3.json', 'w'), indent=0)
print('gmap', S4['gmap'])
for s in cfg['scenes']:
    print(s['n'], round(s['voice'], 2), [(i['art'], i['t']) for i in s.get('inserts', {}).get('items', [])])
