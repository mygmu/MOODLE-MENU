"""
Offline visual check for the card design.

Renders the tiles with PIL using values PARSED OUT OF gmu-menu.css, so this
check cannot drift from what actually ships. Writes render-desktop.png and
render-mobile.png and reports whether every title fits its card.

This is an approximation, not a browser: it does not draw the diagonal
linework, drop shadows, or hover states, and it uses Arial Bold rather than
Montserrat. It is here to catch layout failures - text overflowing the card
or colliding with the photo - not to judge fine styling.

    python render_check.py
"""

import json
import random
import re
from PIL import Image, ImageDraw, ImageFont

CSS = open("gmu-menu.css", encoding="utf-8").read()
COLORS = json.load(open("assets/colors.json"))

COLLEGES = [
    ("01-college-of-medicine", "College of Medicine"),
    ("02-college-of-pharmacy", "College of Pharmacy"),
    ("03-college-of-dentistry", "College of Dentistry"),
    ("04-college-of-health-sciences", "College of Health Sciences"),
    ("05-management-and-ai", "Thumbay College of Management and AI in Healthcare"),
    ("06-college-of-nursing", "College of Nursing"),
    ("07-veterinary-medicine", "Thumbay College of Veterinary Medicine"),
    ("08-general-education-department", "General Education Department"),
    ("09-foundation-foreign-language", "Center for Foundation & Foreign Language Programs"),
]


def num(pattern, text, default):
    m = re.search(pattern, text)
    return float(m.group(1)) if m else default


def band(max_width):
    """Base values, then whichever @media block applies at this width."""
    base = CSS.split("/* =========================================================\n   DEVICE BANDS")[0]
    v = dict(
        aspect=eval(num(r"aspect-ratio:\s*([\d]+)\s*/", base, 4) and
                    re.search(r"aspect-ratio:\s*(\d+)\s*/\s*(\d+)", base).group(1) + "/" +
                    re.search(r"aspect-ratio:\s*(\d+)\s*/\s*(\d+)", base).group(2)),
        fs=num(r"font-size:\s*([\d.]+)vw", base, 2.45),
        shield=num(r"\.gmu-tile__shield\s*\{[^}]*?width:\s*([\d.]+)vw", base, 6.6),
        gap=num(r"gap:\s*([\d.]+)vw", base, 2.2),
        padr=num(r"padding:\s*0\s+([\d.]+)%", base, 34),
        padl=num(r"padding:\s*0\s+[\d.]+%\s+0\s+([\d.]+)%", base, 3.4),
        photo=num(r"\.gmu-tile__photo\s*\{[^}]*?width:\s*([\d.]+)%", base, 20),
        radius=num(r"border-radius:\s*([\d.]+)vw", base, 1.15),
    )
    for limit in (780, 430):                       # widest first, narrowest wins
        if max_width <= limit:
            m = re.search(r"@media \(max-width: %dpx\) \{(.*?)\n\}" % limit, CSS, re.S)
            if not m:
                continue
            blk = m.group(1)
            a = re.search(r"aspect-ratio:\s*(\d+)\s*/\s*(\d+)", blk)
            if a:
                v["aspect"] = int(a.group(1)) / int(a.group(2))
            v["fs"] = num(r"font-size:\s*([\d.]+)vw", blk, v["fs"])
            v["shield"] = num(r"__shield\s*\{\s*width:\s*([\d.]+)vw", blk, v["shield"])
            v["gap"] = num(r"gap:\s*([\d.]+)vw", blk, v["gap"])
            v["padr"] = num(r"padding-right:\s*([\d.]+)%", blk, v["padr"])
            pad = re.search(r"padding:\s*0\s+([\d.]+)%\s+0\s+([\d.]+)%", blk)
            if pad:
                v["padr"], v["padl"] = float(pad.group(1)), float(pad.group(2))
            v["photo"] = num(r"__photo\s*\{\s*width:\s*([\d.]+)%", blk, v["photo"])
            v["radius"] = num(r"border-radius:\s*([\d.]+)vw", blk, v["radius"])
    return v


def hx(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def font(sz):
    try:
        return ImageFont.truetype(r"C:\Windows\Fonts\arialbd.ttf", max(int(sz), 6))
    except OSError:
        return ImageFont.load_default()


def render(W, tag, gap_pct=1.3):
    v = band(W)
    H = round(W / v["aspect"])
    tiles, report = [], []
    for stem, name in COLLEGES:
        c = COLORS[stem]
        a, b = hx(c["from"]), hx(c["to"])
        im = Image.new("RGB", (W, H))
        d = ImageDraw.Draw(im)
        for x in range(W):
            t = x / max(W - 1, 1)
            d.line([(x, 0), (x, H)], fill=tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3)))
        bloom = Image.new("L", (W, H), 0)
        ImageDraw.Draw(bloom).ellipse(
            (int(W * .62), int(-H * .7), int(W * 1.12), int(H * .85)), fill=54)
        im.paste(Image.new("RGB", (W, H), (255, 255, 255)), (0, 0), bloom)

        # ---- decorative layers (approximated; SVGs are drawn by hand here) ----
        deco = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        dd = ImageDraw.Draw(deco)
        # constellation, left 24%
        rnd = random.Random(7)
        mw = int(W * .24)
        pts = [(rnd.uniform(0, mw), rnd.uniform(0, H)) for _ in range(26)]
        for i, p in enumerate(pts):
            for _, q in sorted((( (p[0]-r[0])**2+(p[1]-r[1])**2 )**.5, r)
                               for j, r in enumerate(pts) if j != i)[:3]:
                dd.line([p, q], fill=(255, 255, 255, 56), width=1)
        for p in pts:
            dd.ellipse((p[0]-2, p[1]-2, p[0]+2, p[1]+2), fill=(255, 255, 255, 72))
        # arc + dots, right
        aw = int(W * .24)
        ax = W - int(W * .02) - aw
        for off, col, wdt in ((0.20, (110, 198, 255, 217), max(2, W//300)),
                              (0.11, (155, 140, 255, 128), max(1, W//600))):
            dd.arc((ax + int(aw*off) - aw//2, 0, ax + int(aw*off) + aw//2, H),
                   -90, 90, fill=col, width=wdt)
        for fy, r in ((.15, .028), (.40, .035), (.61, .035), (.86, .028)):
            cxx = ax + aw*.55
            rr = W*r/2
            dd.ellipse((cxx-rr, H*fy-rr, cxx+rr, H*fy+rr), fill=(56, 182, 255, 255))
        im.paste(deco, (0, 0), deco)

        # campus building, bottom-left
        bld = Image.open("assets/deco/building.png").convert("RGBA")
        bw = round(W * .046)
        bld = bld.resize((bw, round(bw * bld.height / bld.width)), Image.LANCZOS)
        bld.putalpha(bld.split()[-1].point(lambda v: int(v * .34)))
        im.paste(bld, (round(W * .012), H - round(H * .06) - bld.height), bld)

        # subject line-icon watermark
        ic = Image.open(f"assets/icons/{stem}.png").convert("RGBA")
        iw = round(W * .095)
        ic = ic.resize((iw, round(iw * ic.height / ic.width)), Image.LANCZOS)
        ic.putalpha(ic.split()[-1].point(lambda v: int(v * .22)))
        im.paste(ic, (W - round(W * .27) - iw, (H - ic.height) // 2), ic)

        sh = Image.open("assets/shield.png").convert("RGBA")
        sw = round(W * v["shield"] / 100)
        sh = sh.resize((sw, round(sw * sh.height / sh.width)), Image.LANCZOS)
        sx = round(W * v["padl"] / 100)
        im.paste(sh, (sx, (H - sh.height) // 2), sh)

        fsz = round(W * v["fs"] / 100)
        f = font(fsz)
        tx = sx + sh.width + round(W * v["gap"] / 100)
        avail = W * (1 - v["padr"] / 100) - tx
        words = name.upper().split()
        lines, cur = [], ""
        for w in words:
            t = (cur + " " + w).strip()
            if d.textlength(t, font=f) <= avail or not cur:
                cur = t
            else:
                lines.append(cur)
                cur = w
        lines.append(cur)
        widest = max(d.textlength(l, font=f) for l in lines)
        lh = round(fsz * 1.14)
        th = lh * len(lines)
        ty = (H - th) // 2
        for i, l in enumerate(lines):
            d.text((tx, ty + i * lh), l, font=f, fill=(255, 255, 255))
        report.append((name, len(lines), widest <= avail + 1, th <= H * .86))

        ph = Image.open(f"assets/photos/{stem}.png").convert("RGBA")
        pd = round(W * v["photo"] / 100)
        ph = ph.resize((pd, pd), Image.LANCZOS)
        ring = Image.new("RGBA", (pd, pd), (0, 0, 0, 0))
        ImageDraw.Draw(ring).ellipse((0, 0, pd - 1, pd - 1),
                                     outline=(255, 255, 255, 150), width=max(2, round(W * .003)))
        px = W - round(W * .045) - pd
        py = (H - pd) // 2
        im.paste(ph, (px, py), ph)
        im.paste(ring, (px, py), ring)

        r = round(W * v["radius"] / 100)
        m = Image.new("L", (W, H), 0)
        ImageDraw.Draw(m).rounded_rectangle((0, 0, W - 1, H - 1), r, fill=255)
        out = Image.new("RGB", (W, H), (255, 255, 255))
        out.paste(im, (0, 0), m)
        tiles.append(out)

    g = round(W * gap_pct / 100)
    sheet = Image.new("RGB", (W, sum(t.height for t in tiles) + g * 8), (255, 255, 255))
    y = 0
    for t in tiles:
        sheet.paste(t, (0, y))
        y += t.height + g
    print(f"\n{tag}  {W}px  tile {v['aspect']:.2f}:1  shield {v['shield']}vw  "
          f"type {v['fs']}vw   page h/w = {sheet.height / W:.5f}")
    bad = 0
    for n, l, fw, fh in report:
        if not (fw and fh):
            bad += 1
        print(f"   {'OK ' if fw and fh else 'BAD'}  {l} line(s)  "
              f"{'width ok ' if fw else 'TOO WIDE'}  {'height ok' if fh else 'TOO TALL'}   {n}")
    return sheet, bad


d, b1 = render(1200, "DESKTOP")
d.save("render-desktop.png")
m, b2 = render(375, "MOBILE")
m.save("render-mobile.png")
print("\nRESULT:", "all titles fit" if b1 + b2 == 0 else f"{b1 + b2} PROBLEM TILE(S)")
