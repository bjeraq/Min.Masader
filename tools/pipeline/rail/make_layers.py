"""Cut the hero train out of s01/s04 with rembg (isnet-anime) and write layers.json."""
import json, pathlib
from PIL import Image
from rembg import remove, new_session

SRC = pathlib.Path('/tmp/claude-0/-home-user-min-masader/59b58237-73e8-5a26-8661-efeb42e64c46/scratchpad/rail/img')
OUT = pathlib.Path('/home/user/min.masader/site/media/rail/layers')
sess = new_session('u2net')

# crop windows around each train so rembg does not grab palms/sun (x0,y0,x1,y1 in 1152x2048)
REG = {'s01': (0, 1000, 920, 1900), 's04': (260, 820, 1150, 1850)}
META = {'s01': {'ang': 18, 'osc': [3, 1.1, 0.8], 'rumble': 1.3, 'scale0': 1.035, 'amp': 0.4, 'ph': 0.7},
        's04': {'osc': [2, 1, 1.1], 'rumble': 1.2, 'grow': 0.07, 'scale0': 1.03, 'amp': 0.4, 'ph': 1.9}}

lay = {}
for sid, (x0, y0, x1, y1) in REG.items():
    im = Image.open(SRC / f'{sid}.png').convert('RGBA')
    crop = im.crop((x0, y0, x1, y1))
    cut = remove(crop, session=sess)
    bbox = cut.getbbox()
    if not bbox:
        print(sid, 'NO ALPHA'); continue
    part = cut.crop(bbox)
    px, py = x0 + bbox[0], y0 + bbox[1]
    part.save(OUT / f'{sid}_train.png')
    entry = {'src': f'media/rail/layers/{sid}_train.png', 'x': px, 'y': py,
             'w': part.width, 'h': part.height}
    entry.update(META[sid])
    lay[sid] = {'bg': f'media/rail/{sid}.jpg', 'parts': [entry]}
    print(sid, 'part', px, py, part.width, part.height)
    # small preview
    prev = part.copy(); prev.thumbnail((420, 420)); prev.save(OUT / f'{sid}_prev.png')

json.dump(lay, open(OUT / 'layers.json', 'w'))
print('layers.json written')
