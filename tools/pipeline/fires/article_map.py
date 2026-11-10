"""Static SVG map of Kuwait's oil fields for the article (Natural Earth outlines from gmap.json)."""
import json, pathlib
G = json.load(open(pathlib.Path(__file__).resolve().parent.parent / 'gmap.json'))
def P(lon, lat): return ((lon - G['lon0']) * G['cos'] * G['k'], (G['lat1'] - lat) * G['k'])
FIELDS = [('برقان', 47.97, 28.97, 4.2, 0, 7.5), ('المقوع والأحمدي', 48.07, 29.10, 2.0, -9, -4),
          ('المناقيش', 47.55, 29.04, 2.2, 0, 6.5), ('أم قدير', 47.70, 28.84, 2.0, 0, 6),
          ('الوفرة', 47.93, 28.58, 2.0, 0, 6), ('الروضتين', 47.70, 29.84, 2.3, 0, -4.5),
          ('الصابرية', 47.97, 29.80, 2.0, 7, 4)]
x0, y0 = P(46.45, 30.25); x1, y1 = P(48.65, 28.35)
parts = [f'<svg viewBox="{x0:.1f} {y0:.1f} {x1-x0:.1f} {y1-y0:.1f}" role="img" aria-label="خريطة مبسطة للكويت تُظهر مواقع حقول النفط الرئيسية التي اشتعلت آبارها عام 1991">',
         f'<rect x="{x0:.1f}" y="{y0:.1f}" width="{x1-x0:.1f}" height="{y1-y0:.1f}" class="k-sea"/>']
for d in G['land']: parts.append(f'<path d="{d}" class="k-land"/>')
for c, d in G['gcc'].items(): parts.append(f'<path d="{d}" class="{"k-kw" if c == "KWT" else "k-land"}"/>')
for name, lo, la, r, dx, dy in FIELDS:
    x, y = P(lo, la)
    parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r*0.9:.1f}" class="k-fire"/>')
    parts.append(f'<text x="{x+dx:.1f}" y="{y+dy:.1f}" class="k-lbl" text-anchor="middle">{name}</text>')
x, y = P(47.98, 29.37); parts.append(f'<text x="{x:.1f}" y="{y:.1f}" class="k-city" text-anchor="middle">مدينة الكويت</text>')
x, y = P(48.45, 29.0); parts.append(f'<text x="{x:.1f}" y="{y:.1f}" class="k-sealbl" text-anchor="middle">الخليج</text>')
parts.append('</svg>')
print('\n'.join(parts))
