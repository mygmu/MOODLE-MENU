# GMU LMS — College Menu

Responsive, animated banner menu for the Gulf Medical University Moodle site.

**Live site:** https://mygmu.github.io/MOODLE-MENU/

## Layout

```
banners/                  the 9 college banner images (1584x396)
gmu-menu.css              layout, animation, mobile crop rules
generate.py               single source of truth — edit and re-run
index.html                the showcase page (generated)
moodle-paste-snippet.html the block to paste into Moodle (generated)
.github/workflows/        Pages deploy workflow
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

1. Open the label/page, switch to HTML view (`< >`).
2. Paste the contents of `moodle-paste-snippet.html`. Save.

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

## Mobile behaviour

Banners are 4:1 with the college name baked into the left third. Shown whole on
a phone that name is ~11px tall. On narrow portrait screens the CSS crops the
banner from the right and anchors left, so the tile grows taller and the title
grows with it.

The crop limit is measured, not chosen: the longest title ends at **58.6%** of
banner width, and `aspect-ratio: 13/5` shows 65%. Lowering that ratio slices
college names off. See the comment block in `gmu-menu.css` before changing it.
