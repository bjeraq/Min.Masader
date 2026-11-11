"""Fit landscape public-domain archive photos into the 1152x2048 (9:16) scene canvas.
mode 'crop' = cover-crop around a focus x; mode 'fill' = full photo over a blurred, darkened copy."""
import sys, pathlib
from PIL import Image, ImageFilter, ImageEnhance
SRC = pathlib.Path(sys.argv[1]); OUT = pathlib.Path(sys.argv[2]); OUT.mkdir(parents=True, exist_ok=True)
W, H = 1152, 2048
JOBS = {  # out name: (src, mode, focus-x fraction, foreground centre-y fraction)
    'pd1': ('pd_fires.jpg', 'crop', 0.62, None),
    'pd2': ('pd_usace.jpg', 'crop', 0.66, None),
    'pd3': ('pd_shuttle.jpg', 'crop', 0.55, None),
    'pd4': ('pd_capping.jpg', 'fill', None, 0.56),
    'pd5': ('pd_rumaila.jpg', 'fill', None, 0.56),
}
for name, (src, mode, fx, cy) in JOBS.items():
    im = Image.open(SRC / src).convert('RGB')
    if mode == 'crop':
        s = H / im.height; im2 = im.resize((round(im.width * s), H), Image.LANCZOS)
        x0 = int(min(max(fx * im2.width - W / 2, 0), im2.width - W))
        out = im2.crop((x0, 0, x0 + W, H))
    else:
        s = H / im.height; bg = im.resize((round(im.width * s), H), Image.LANCZOS)
        x0 = (bg.width - W) // 2; bg = bg.crop((x0, 0, x0 + W, H)).filter(ImageFilter.GaussianBlur(28))
        bg = ImageEnhance.Brightness(bg).enhance(0.55)
        fw = W; fh = round(im.height * fw / im.width); fg = im.resize((fw, fh), Image.LANCZOS)
        out = bg; out.paste(fg, (0, int(cy * H - fh / 2)))
    out.save(OUT / f'{name}.jpg', quality=88)
    print(name, out.size)
