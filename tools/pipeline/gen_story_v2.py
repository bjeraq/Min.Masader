"""Extend the v1 story config with layers, camera keyframes and FX timed to the existing audio events."""
import json

SP = '/tmp/claude-0/-home-user-Advisers/43f3f876-332f-5c13-8812-05a26eedb0e5/scratchpad'
SITE = '/home/user/Advisers/site'
cfg = json.load(open(f'{SP}/build/story_cfg.json', encoding='utf-8'))
EV = json.load(open(f'{SP}/build/events.json'))
LAY = json.load(open(f'{SITE}/media/excise/layers/layers.json'))
IW, IH = 1152, 2048
FADE = 0.5
sc = {s['n']: s for s in cfg['scenes']}


def evs(name, n):
    s = sc[n]
    return sorted(t for nm, t, g in EV if nm == name and s['start'] - 0.05 <= t < s['end'] + 0.05)


def nx(px):
    return round(px / IW, 4)


def ny(py):
    return round(py / IH, 4)


# per-image motion amplitude (characters breathe/sway; big blobs that include furniture move less)
AMP = {'s01': 0.45, 's06': 0.8, 's07': 1.0, 's08': 1.0, 's09': 0.35, 's10': 0.5, 's11': 0.9, 's13': 0.8}

for i, s in enumerate(cfg['scenes']):
    n = s['n']
    img_id = s['img'].split('/')[-1].split('.')[0]
    nxt = cfg['scenes'][i + 1]['start'] if i + 1 < len(cfg['scenes']) else s['end']
    z0, z1, fx, fy = s['kb']
    s['cam'] = [{'t': s['start'], 'z': z0, 'x': fx, 'y': fy}, {'t': nxt + FADE, 'z': z1, 'x': fx, 'y': fy}]
    if img_id in LAY and n != 2:
        L = LAY[img_id]
        s['layers'] = {'bg': L['bg'], 'parts': [dict(p, amp=AMP.get(img_id, .6), ph=round(1.3 * k + 0.7 * n, 2))
                                                for k, p in enumerate(L['parts'])]}
    else:
        s['layers'] = None
    s['fx'] = {}
    s['trans'] = ['circle', 'slide', 'zoom'][i % 3] if i > 0 else 'none'

# ---- scene-specific camera moves & FX ----
# s03: snap-zoom onto the document, stamp slams in sync with the stamp sound
st = evs('stamp', 3)[0]
S3 = sc[3]
S3['cam'] = [{'t': S3['start'], 'z': 1.0, 'x': .5, 'y': .62}, {'t': st - 1.25, 'z': 1.07, 'x': .5, 'y': .64},
             {'t': st - 0.95, 'z': 1.5, 'x': nx(470), 'y': ny(1560)}, {'t': S3['end'] + FADE, 'z': 1.58, 'x': nx(470), 'y': ny(1560)}]
S3['fx'] = {'stamp': {'t': st, 'x': 470, 'y': 1565, 'r': 120}}
S3['shake'] = [st]
# s04: pulse rings on the foreground city when "Kuwait has not applied it yet" appears
S4 = sc[4]
S4['fx'] = {'rings': {'t': S4['chips'][1]['t'], 'x': 575, 'y': 1320}, 'sparkles': {'n': 9, 'box': [260, 380, 900, 900]}}
# s05: a scanning highlight sweeps the shelf
S5 = sc[5]
S5['fx'] = {'scan': {'t0': S5['voice'], 't1': S5['voice_end'], 'y0': 560, 'y1': 1560}}
# s06: smoke from the vape, coins pop onto the stack with the coin sound
S6 = sc[6]
S6['fx'] = {'smoke': {'x': 640, 'y': 640}, 'coinstack': {'t': evs('coins', 6)[0], 'x': 880, 'y': 1030, 'n': 6},
            'sticker': {'t': S6['badge']['t'] + 0.35, 'x': 1000, 'y': 1180, 'text': '×2'}}
S6['shake'] = [S6['badge']['t']]
# s07: sparks around the can when it opens, "!" pops with the badge
S7 = sc[7]
S7['fx'] = {'sparks': {'t': evs('canopen', 7)[0], 'x': 575, 'y': 1050}, 'bang': {'t': S7['badge']['t'], 'x': 760, 'y': 860}}
S7['shake'] = [S7['badge']['t']]
# s08: soda bubbles rise, arrow pops up with the badge
S8 = sc[8]
S8['fx'] = {'bubbles': {'x': 335, 'y': 600}, 'arrow': {'t': S8['badge']['t'], 'x': 470, 'y': 520}}
S8['shake'] = [S8['badge']['t']]
# s09: one sugar cube drops on each beat of the cube sound, ring pulse on the sugar-free can with the ding
S9 = sc[9]
cubes = evs('cube', 9)
S9['fx'] = {'cubes': [{'t': t, 'x': x, 'y': 1300} for t, x in zip(cubes, [175, 420, 665, 905])],
            'ring': {'t': evs('ding', 9)[0], 'x': 1015, 'y': 1070}}
# s10: punch-in on the father's face when the counter lands on 1 dinar
S10 = sc[10]
t1 = S10['counter']['t1']
S10['cam'] = [{'t': S10['start'], 'z': 1.0, 'x': .45, 'y': .42}, {'t': t1 - 0.35, 'z': 1.1, 'x': .47, 'y': .4},
              {'t': t1 - 0.05, 'z': 1.7, 'x': nx(690), 'y': ny(520)}, {'t': S10['end'] + FADE, 'z': 1.78, 'x': nx(690), 'y': ny(520)}]
S10['shake'] = [t1 + 0.05]
# s11: start on the family, glide down to the piggy bank at "diversify revenue", coins rain in with the coin sound
S11 = sc[11]
tm = S11['chips'][1]['t']
S11['cam'] = [{'t': S11['start'], 'z': 1.32, 'x': .5, 'y': .26}, {'t': tm - 0.2, 'z': 1.36, 'x': .5, 'y': .26},
              {'t': tm + 0.9, 'z': 1.3, 'x': .5, 'y': .76}, {'t': S11['end'] + FADE, 'z': 1.24, 'x': .5, 'y': .74}]
S11['fx'] = {'coinrain': {'t0': tm + 0.5, 't1': S11['end'] + FADE, 'burst': evs('coins', 11)[0], 'x': 380, 'y': 1430},
             'hearts': {'x': 560, 'y': 330, 't1': tm + 0.9}}
# s12: calendar pages fly away, sand trickles, the "pending" badge thumps in
S12 = sc[12]
S12['fx'] = {'pages': {'x': 470, 'y': 380}, 'sand': [{'x': 400, 'y': 1000}, {'x': 840, 'y': 870}], 'pending': {'t': S12['start'] + 0.35}}
# s13: extra question marks drift up
S13 = sc[13]
S13['fx'] = {'qmarks': {'n': 6, 'box': [140, 300, 1010, 1100]}}
# s16 (outro): TV glow flicker
S16 = sc[16]
S16['fx'] = {'tvglow': {'x': 845, 'y': 560, 'w': 520, 'h': 330}}

json.dump(cfg, open(f'{SP}/build/story_cfg_v2.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('ok', [(s['n'], bool(s['layers']), list(s['fx'])) for s in cfg['scenes']])
