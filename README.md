# GMU LMS — College Menu

Responsive, animated banner menu for the Gulf Medical University Moodle site.

**Live site:** https://mygmu.github.io/MOODLE-MENU/

## Layout

```
assets/shield.png            GMU crest, used as the icon on every tile
assets/photos/               the 9 circular college photos
assets/icons/                per-college line icons (caduceus, tooth, DNA...)
assets/deco/constellation.svg  node mesh, left of each card
assets/deco/arc.svg            blue arc + dots, behind the photo
assets/deco/building.png       campus building mark
assets/colors.json           per-college gradient, sampled from the originals
banners/                     original 1584x396 artwork (source archive)
gmu-menu.css                 card design, animation, device bands
generate.py                  single source of truth — edit and re-run
render_check.py              offline layout verification
index.html                   showcase page (generated)
moodle-paste-snippet.html    direct block for Moodle (generated)
embed.html                   bare menu for framing (generated)
moodle-iframe-snippet.html   auto-fitting iframe for Moodle (generated)
.github/workflows/           Pages deploy workflow
```

`index.html` and `moodle-paste-snippet.html` are **generated**. Do not hand-edit
them — edit `generate.py` and re-run it, or the two will drift apart.

## Changing a link, name, or order

Edit `COLLEGES` at the top of `generate.py`, then:

```bash
python generate.py
git add -A && git commit -m "update links" && git push
```

GitHub Pages redeploys automatically on push to `main`.

## Installing in Moodle

Two options — use one, not both:

- **`moodle-iframe-snippet.html`** (recommended) — an auto-fitting iframe. The
  styling lives on GitHub Pages where Moodle's purifier cannot strip it.
- **`moodle-paste-snippet.html`** — the markup directly, no frame. Better for
  accessibility and search, but its `<style>` block may be purified away.

Open the label/page, switch to HTML view (`< >`), paste, save.

Artwork is served from GitHub Pages, so nothing is uploaded into Moodle.

If the animation is gone after saving, Moodle's HTML purifier stripped the
`<style>` block. Paste `gmu-menu.css` into *Site administration → Appearance →
Themes → Boost → Raw initial SCSS*, purge caches, then delete the `<style>`
block from the pasted markup. Layout still works without it — only motion is lost.

## Important: everything must stay at the repo root

GitHub Pages **excludes `.github/` from the published site**. Files placed
there deploy successfully but are never served, which produces a 404 site with
green build checks. Keep `banners/`, `index.html`, and `gmu-menu.css` at the
repository root.

## Design (v2)

Tiles are generated cards, not pre-rendered banners. Each is a colour gradient
with the GMU shield, the college name as **live HTML text**, and the circular
photo lifted from the original artwork.

The v1 banners had the college name baked into the PNG, which forced a crop
hack on phones (shrink a 4:1 image and the title lands at ~11px). Live text
removes that entirely: it scales, wraps, translates, and is selectable.

`banners/` is kept as the source archive. It is no longer served — the site
uses `assets/photos/` and `assets/shield.png`, extracted from it.

## Where the graphics come from

The subject line-icons are the **originals**, lifted out of the v1 banners with
a median-filter background estimate and saved as white alpha PNGs, so they can
be tinted and scaled. Two were drawn to match the set: a paw, because Veterinary
had inherited Medicine's cross from the template it was built on, and a campus
building, because gmu.ac.ae exposes no building graphic (its media library has
only a vendor flyer and stock student photos).

Note that CSS `url()` resolves against the *page*, not against wherever the
stylesheet text came from. `generate.py` therefore rewrites the decorative
`url()`s to absolute for the Moodle paste snippet only — pasted into Moodle,
relative paths would resolve against lms.gmu.ac.ae and 404.

## Everything is sized in vw and %

The Moodle embed is an iframe, and Moodle's purifier strips `<script>`, so the
frame cannot report its height to the parent. Instead the page is built so its
height is **exactly proportional to its width**, which lets one CSS
`aspect-ratio` fit the frame with no JavaScript.

That only holds while every vertical dimension scales with width. A stray `px`
in `gmu-menu.css` will desync the iframe height from its content and leave a
gap or clip a tile. The tile gap is defined once, in `gmu-menu.css`, and parsed
by `generate.py` — do not duplicate it.

## Checking a design change

```bash
python render_check.py
```

Renders the tiles offline with PIL, using values parsed out of `gmu-menu.css`,
and reports whether every title still fits. It approximates — no linework,
shadows, or hover states, and Arial stands in for Montserrat — so it catches
layout failures, not styling nits.
