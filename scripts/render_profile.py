"""Render five self-contained terminal scenes and a matching pixel avatar.

Run from any directory with Python 3.10+ and Pillow: python scripts/render_profile.py
No network, API keys, telemetry, or GitHub Actions required.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'assets' / 'terminal'
INK, MUTED, LINE, ACCENT = '#202329', '#737b86', '#e0e4e8', '#5264a3'
SCENES = [
    ('profile', 'whoami', 'floyflenn', 'A curious mind. A quiet terminal.', [
        ('focus', 'cybersecurity'), ('approach', 'inspect / build / understand'),
        ('interests', 'systems, automation, local AI'), ('identity', 'an alias, by design')]),
    ('python', 'python -m curiosity', 'small scripts. useful tools.', 'Make the repetitive disappear.', [
        ('language', 'Python'), ('exploring', 'automation & computer vision'),
        ('workflow', 'prototype / test / simplify'), ('principle', 'readable before clever')]),
    ('linux', 'open a shell', 'closer to the system.', 'Follow the process. Read the logs.', [
        ('environment', 'Linux'), ('toolbox', 'Bash / Git / terminal'),
        ('exploring', 'permissions & networking'), ('habit', 'understand the command first')]),
    ('security', 'inspect the surface', 'question the assumptions.', 'Understand how things fail.', [
        ('focus', 'cybersecurity'), ('practice', 'labs & log analysis'),
        ('mindset', 'observe / investigate / verify'), ('scope', 'authorized environments')]),
    ('experiments', 'follow the question', 'ideas into experiments.', 'Software meets the physical world.', [
        ('exploring', 'local AI & computer vision'), ('also', 'robotics & control'),
        ('method', 'build / observe / iterate'), ('account', 'a personal playground')]),
]

def font(size, bold=False):
    name = 'DejaVuSansMono-Bold.ttf' if bold else 'DejaVuSansMono.ttf'
    return ImageFont.truetype(name, size)

def text(d, xy, value, size=18, color=INK, bold=False):
    d.text(xy, value, fill=color, font=font(size, bold))

def render(avatar, index, mobile=False, cursor=True):
    mode, cmd, title, subtitle, rows = SCENES[index]
    w, h = (640, 940) if mobile else (1200, 640)
    im = Image.new('RGB', (w, h), '#ffffff')
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((8, 8, w-9, h-9), 18, outline=LINE, width=2)
    d.line((9, 64, w-10, 64), fill=LINE, width=2)
    for x, c in [(31, '#444950'), (51, '#9299a2'), (71, '#d0d4da')]:
        d.ellipse((x, 31, x+8, 39), fill=c)
    text(d, (101, 25), 'profile.sh --live', 19, bold=True)
    text(d, (w-98, 28), f'0{index+1} / 05', 14, MUTED)
    if mobile:
        art = avatar.resize((240, 240), Image.Resampling.LANCZOS)
        im.paste(art, (200, 79))
        text(d, (253, 312), '@floyflenn', 17, bold=True)
        x, y = 39, 385
        text(d, (39, 354), ' / '.join(s[0] for s in SCENES), 12, MUTED)
    else:
        d.line((365, 97, 365, 563), fill=LINE, width=2)
        art = avatar.resize((310, 310), Image.Resampling.LANCZOS)
        im.paste(art, (32, 150))
        text(d, (108, 465), '@floyflenn', 19, bold=True)
        text(d, (83, 500), 'a quiet kind of curious.', 12, MUTED)
        x, y = 407, 151
        tx = x
        for n, s in enumerate(SCENES):
            color = ACCENT if n == index else MUTED
            text(d, (tx, 98), s[0], 14, color, n == index)
            if n == index:
                d.line((tx, 124, tx+len(s[0])*8.5, 124), fill=ACCENT, width=2)
            tx += len(s[0])*9 + 21
    text(d, (x, y), '$ ' + cmd, 17, ACCENT)
    text(d, (x, y+47), title, 22 if mobile else 25, bold=True)
    text(d, (x, y+88), subtitle, 16, MUTED)
    for j, (key, value) in enumerate(rows):
        yy = y+155+j*47
        text(d, (x, yy), key, 15, MUTED)
        text(d, (x+151, yy-1), value, 15 if mobile else 17)
    text(d, (x, y+366), '> keep exploring' + (' _' if cursor else ''), 17, ACCENT)
    d.line((32, h-57, w-33, h-57), fill=LINE)
    text(d, (35, h-40), 'FLOYFLENN / PERSONAL LAB', 12, MUTED)
    text(d, (w-230, h-40), '5 scenes / one curious mind', 11, MUTED)
    return im

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    avatar = Image.open(ROOT / 'assets/avatar/original.png').convert('RGB')
    # Explicit pixel rendition: 64x64 cells, two colors, nearest-neighbor upscale.
    tiny = ImageOps.grayscale(avatar.resize((64, 64), Image.Resampling.BOX))
    tiny = tiny.point(lambda v: 0 if v < 160 else 255).convert('RGB')
    tiny.resize((1024, 1024), Image.Resampling.NEAREST).save(ROOT / 'assets/avatar/pixel.png')
    for mobile in (False, True):
        frames = [render(avatar, n, mobile, bool(k % 2 == 0)) for n in range(5) for k in range(6)]
        suffix = '-mobile' if mobile else ''
        frames[0].save(OUT / f'profile{suffix}.png')
        frames[0].quantize(colors=32).save(OUT / f'profile{suffix}.gif', save_all=True,
                       append_images=[f.quantize(colors=32) for f in frames[1:]], duration=700, loop=0,
                       optimize=True, disposal=1)
    for n, scene in enumerate(SCENES):
        render(avatar, n).save(OUT / f'{scene[0]}.png')
    print('Rendered pixel avatar, five scenes, desktop and mobile animations.')

if __name__ == '__main__':
    main()
