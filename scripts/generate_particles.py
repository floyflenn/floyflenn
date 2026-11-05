"""Build the animated SVG. Requires Pillow, numpy, scipy and Inkscape.

Run from the repository root: python scripts/generate_particles.py
The avatar is sampled from assets/avatar/pixel.png; that image and the original
remain untouched. The Python icon path is from Simple Icons (CC0-1.0).
"""
from pathlib import Path
import subprocess
import tempfile
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy.optimize import linear_sum_assignment
from scipy.ndimage import distance_transform_edt

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'assets/terminal/profile.svg'
S = 240
N = 1200
rng = np.random.default_rng(824)
PYTHON_PATH = ('M11.858 0c-.978.005-1.913.088-2.736.234C6.7.662 6.26 1.558 6.26 3.21v2.182h5.725v.727H4.111c-1.664 0-3.121 1-3.577 2.903-.526 2.181-.549 3.542 0 5.82.407 1.694 1.379 2.902 3.043 2.902h1.969v-2.616c0-1.89 1.635-3.557 3.576-3.557h5.72c1.591 0 2.862-1.31 2.862-2.91v-5.45c0-1.553-1.309-2.718-2.863-2.977A18 18 0 0 0 11.858 0M8.762 1.755c.591 0 1.074.491 1.074 1.095 0 .601-.483 1.087-1.074 1.087A1.08 1.08 0 0 1 7.688 2.85c0-.604.48-1.095 1.074-1.095m9.656 4.364v2.543c0 1.971-1.671 3.63-3.577 3.63H9.122c-1.566 0-2.862 1.34-2.862 2.91v5.452c0 1.551 1.349 2.464 2.862 2.91 1.813.532 3.55.628 5.72 0 1.44-.418 2.862-1.258 2.862-2.91V18.47h-5.719v-.727h8.582c1.664 0 2.284-1.16 2.862-2.903.598-1.793.573-3.518 0-5.819-.41-1.656-1.196-2.903-2.862-2.903zm-3.216 13.807a1.08 1.08 0 0 1 1.074 1.088c0 .604-.48 1.094-1.074 1.094-.592 0-1.075-.49-1.075-1.094 0-.601.483-1.088 1.075-1.088')

def blank(): return Image.new('L', (S,S), 0)

def masks():
    # Crop the existing pixel avatar to its ink bounding box and expand to the panel.
    src = Image.open(ROOT/'assets/avatar/pixel.png').convert('L')
    ink = src.point(lambda x: 255 if x < 150 else 0)
    box = ink.getbbox()
    ink = ink.crop(box)
    ink.thumbnail((205,205), Image.Resampling.LANCZOS)
    avatar = blank(); avatar.paste(ink, ((S-ink.width)//2,(S-ink.height)//2))
    with tempfile.TemporaryDirectory() as td:
        svg = Path(td)/'python.svg'; png = Path(td)/'python.png'
        svg.write_text(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path fill="white" fill-rule="evenodd" d="{PYTHON_PATH}"/></svg>')
        subprocess.run(['inkscape', str(svg), '--export-filename='+str(png), '--export-width=200', '--export-height=200'], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        icon = Image.open(png).convert('RGBA').getchannel('A')
        python = blank(); python.paste(icon,(20,20))
    terminal = blank(); d=ImageDraw.Draw(terminal)
    d.rounded_rectangle((19,37,221,203), radius=17, outline=255, width=7)
    d.line([(52,89),(89,120),(52,151)], fill=255, width=8, joint='curve')
    d.rounded_rectangle((108,143,176,154), radius=5, fill=255)
    shield=blank(); d=ImageDraw.Draw(shield)
    d.line([(120,17),(201,48),(197,132),(182,164),(154,190),(120,213),(86,190),(58,164),(43,132),(39,48),(120,17)], fill=255, width=7, joint='curve')
    d.rounded_rectangle((85,100,155,159),radius=8,outline=255,width=8)
    d.arc((95,62,145,119),180,360,fill=255,width=8)
    d.ellipse((115,122,125,132), fill=255); d.rectangle((118,129,122,143), fill=255)
    chip=blank(); d=ImageDraw.Draw(chip)
    d.rounded_rectangle((56,56,184,184),radius=16,outline=255,width=7)
    d.rounded_rectangle((88,88,152,152),radius=9,outline=255,width=8)
    for i in [80,106,134,160]:
        d.line((i,25,i,56),fill=255,width=7); d.line((i,184,i,215),fill=255,width=7)
        d.line((25,i,56,i),fill=255,width=7); d.line((184,i,215,i),fill=255,width=7)
    return [avatar,python,terminal,shield,chip]

def sample(mask):
    # Stratified candidates, with tiny deterministic jitter to retain a dot texture.
    arr=np.asarray(mask); pts=[]
    for y in range(1,S,2):
        for x in range(1,S,2):
            if arr[y,x] > 140: pts.append((x+rng.uniform(-.25,.25),y+rng.uniform(-.25,.25)))
    pts=np.asarray(pts)
    ids=rng.choice(len(pts),N,replace=len(pts)<N)
    return pts[ids]

def match(a,b):
    cost=((a[:,None,:]-b[None,:,:])**2).sum(axis=2)
    _, col=linear_sum_assignment(cost)
    return b[col]

def row(y,label,value):
    return f'<text x="447" y="{y}" fill="#8ca1b8">{label}</text><text x="850" y="{y}" text-anchor="end" fill="#e4effa">{value}</text>'

def main():
    source_masks = masks()
    shapes = [sample(m) for m in source_masks]
    # Thin only the avatar ink. Move existing samples to the nearest remaining ink;
    # all four other target point sets are kept exactly as generated before.
    thin = np.asarray(source_masks[0].filter(ImageFilter.MinFilter(3))) > 140
    nearest = distance_transform_edt(~thin, return_distances=False, return_indices=True)
    xy = np.rint(shapes[0]).astype(int).clip(0, S - 1)
    shapes[0] = np.column_stack((nearest[1, xy[:, 1], xy[:, 0]], nearest[0, xy[:, 1], xy[:, 0]])).astype(float)
    aligned=[shapes[0]]
    for s in shapes[1:]: aligned.append(match(aligned[-1],s))
    # Hold each for 3 s, then morph for 1.44 s. Final target is the first exact state.
    times='0;.135135;.2;.335135;.4;.535135;.6;.735135;.8;.935135;1'
    svg=['''<svg xmlns="http://www.w3.org/2000/svg" width="900" height="550" viewBox="0 0 900 550" role="img">
<title>floyflenn | profile.sh --live</title><desc>Anonymous cybersecurity profile. Dots morph through an avatar, Python, terminal, shield and chip.</desc>
<rect width="900" height="550" rx="12" fill="#0a101f"/><rect x="9" y="9" width="882" height="532" rx="10" fill="none" stroke="#284f65"/>
<path d="M10 46H890" stroke="#24394d"/><circle cx="30" cy="28" r="5" fill="#ef646c"/><circle cx="47" cy="28" r="5" fill="#eebc65"/><circle cx="64" cy="28" r="5" fill="#5bd3a4"/>
<g font-family="ui-monospace,Consolas,Menlo,monospace"><text x="86" y="33" fill="#67ddec" font-size="14" font-weight="bold">profile.sh --live</text><text x="866" y="33" text-anchor="end" fill="#6e839c" font-size="11">FLOYFLENN / PERSONAL LAB</text>
<rect x="20" y="67" width="365" height="455" rx="6" fill="#0c1525" stroke="#3ac5d9"/><rect x="404" y="67" width="476" height="455" rx="6" fill="#0c1525" stroke="#3ac5d9"/>
<rect x="34" y="58" width="112" height="18" fill="#0a101f"/><text x="42" y="71" fill="#67ddec" font-size="12" font-weight="bold">VISUAL.MAP</text><rect x="418" y="58" width="116" height="18" fill="#0a101f"/><text x="426" y="71" fill="#67ddec" font-size="12" font-weight="bold">SYSTEM.INFO</text>
<text x="202" y="110" text-anchor="middle" fill="#8093a9" font-size="11">PARTICLE STUDY / 01—05</text>
<path d="M49 449H356" stroke="#243d50"/><text x="202" y="476" text-anchor="middle" font-size="13" fill="#d8e9f5">@floyflenn</text><text x="202" y="496" text-anchor="middle" font-size="10" fill="#8093a9">observe  /  build  /  explore</text>
<rect x="435" y="91" width="123" height="25" rx="12" fill="#57d4ae"/><text x="496.5" y="108" text-anchor="middle" fill="#0a101f" font-size="12" font-weight="bold">@floyflenn</text><circle cx="585" cy="103.5" r="4" fill="#ef747f"/><text x="596" y="108" fill="#ef929b" font-size="11">LIVE VISUAL</text>
<g font-size="14">''']
    for y,k,v in [(150,'IDENTITY','anonymous'),(182,'PRIMARY','cybersecurity'),(214,'SYSTEMS','Linux / networking'),(246,'CODE','Python / Bash'),(278,'PRACTICE','security labs / log analysis'),(310,'BUILD','scripting / automation'),(342,'EXPLORE','local AI / computer vision'),(374,'ALSO','robotics / control')]: svg.append(row(y,k,v))
    svg.append('''</g><path d="M435 400H849" stroke="#263d52"/><text x="435" y="430" fill="#68ddeb" font-size="13">$ cat focus.txt</text><text x="435" y="455" fill="#dce9f4" font-size="13">Curious about how systems work,</text><text x="435" y="477" fill="#dce9f4" font-size="13">how they fail, and how to improve them.</text><text x="435" y="501" fill="#6fcfae" font-size="12">&gt; keep exploring_</text></g><g>''')
    groups = {}
    for i in range(N):
        vals=[p[i] for p in aligned]+[aligned[0][i]]
        # Panel coordinates: 240 units expanded to 285 units.
        xx=[60+v[0]*1.19 for v in vals]; yy=[130+v[1]*1.19 for v in vals]
        x=';'.join(f'{q:.1f}' for v in xx[:-1] for q in (v,v))+f';{xx[-1]:.1f}'
        y=';'.join(f'{q:.1f}' for v in yy[:-1] for q in (v,v))+f';{yy[-1]:.1f}'
        color=('#a78bfa','#b9a4ff','#8e88eb','#c4b5fd')[i%4]
        pycolor = '#64b5e8' if aligned[1][i][1] < 120 else '#ffd76b'
        groups.setdefault((color, pycolor), []).append(
            f'<circle cx="{xx[0]:.1f}" cy="{yy[0]:.1f}" r="0.95"><animate attributeName="cx" values="{x}" keyTimes="{times}" dur="22.2s" repeatCount="indefinite"/><animate attributeName="cy" values="{y}" keyTimes="{times}" dur="22.2s" repeatCount="indefinite"/></circle>')
    # Animate inherited fill once per color group, rather than once per dot.
    for (color, pycolor), circles in groups.items():
        color_values = ';'.join([color,color,pycolor,pycolor,color,color,color,color,color,color,color])
        svg.append(f'<g fill="{color}"><animate attributeName="fill" values="{color_values}" keyTimes="{times}" dur="22.2s" repeatCount="indefinite"/>')
        svg.extend(circles)
        svg.append('</g>')
    svg.append('</g></svg>')
    OUT.write_text('\n'.join(svg),encoding='utf-8')
    # Static visual QA for each target, using the exact sampled coordinates.
    with tempfile.TemporaryDirectory() as td:
        pass
    for j,pts in enumerate(aligned):
        im=Image.new('RGB',(360,360),'#0c1525'); d=ImageDraw.Draw(im)
        for i,(x,y) in enumerate(pts):
            cx=38+x*1.19; cy=38+y*1.19
            d.ellipse((cx-.95,cy-.95,cx+.95,cy+.95),fill=(('#64b5e8' if y < 120 else '#ffd76b') if j == 1 else ['#a78bfa','#b9a4ff','#8e88eb','#c4b5fd'][i%4]))
        im.save('/tmp/floy-scene-%d.png'%j)
    print(f'Wrote {OUT} ({OUT.stat().st_size} bytes)')
if __name__=='__main__': main()
