/* =========================================================
   GMU LMS - interactive node network, one canvas per tile.

   Sparse linked nodes rather than a dust field: a handful per card,
   joined by lines when they drift close, and nudged aside by the
   cursor. Loaded ONLY by embed.html and index.html, both served from
   GitHub Pages. It is deliberately absent from the Moodle paste
   snippet, where the purifier strips <script> anyway.

   Two invariants this must not break:

   1. LAYOUT. The canvas is absolutely positioned inside a zero-size
      container, so it contributes nothing to layout. The iframe's
      height is derived from CSS as a fixed ratio of its width, and
      anything that changed content height would desync the frame.

   2. CLICKS. Every tile is a link. The canvas is pointer-events:none
      and the pointer is tracked on window, so nothing here can
      swallow a click.

   Degrades to nothing if JS is unavailable - the card keeps its
   gradient, mesh, arc and icon.
   ========================================================= */
(function () {
  "use strict";

  var reduced = window.matchMedia &&
                window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  var LINK_DIST = 108;   // px between nodes before a line is drawn
  var MOUSE_DIST = 132;  // px within which the cursor pushes and links
  var PUSH = 46;         // px of displacement at the cursor's centre

  var items = [];

  function rand(a, b) { return a + Math.random() * (b - a); }

  function makeNode(w, h) {
    return {
      x: rand(0, w), y: rand(0, h),
      vx: rand(-0.14, 0.14), vy: rand(-0.11, 0.11),
      r: rand(1.3, 2.4),
      ox: 0, oy: 0                      // eased offset from the cursor
    };
  }

  function setup(tile) {
    var host = tile.querySelector(".gmu-tile__particles");
    if (!host) return null;
    var cv = document.createElement("canvas");
    cv.setAttribute("aria-hidden", "true");
    host.appendChild(cv);
    var it = {
      tile: tile, cv: cv, ctx: cv.getContext("2d"),
      w: 0, h: 0, nodes: [], mx: -9999, my: -9999
    };
    resize(it);
    if (window.ResizeObserver) {
      new ResizeObserver(function () { resize(it); }).observe(tile);
    }
    return it;
  }

  function resize(it) {
    var r = it.tile.getBoundingClientRect();
    if (!r.width || !r.height) return;
    var dpr = Math.min(window.devicePixelRatio || 1, 2);
    it.w = r.width; it.h = r.height;
    it.cv.width = Math.round(r.width * dpr);
    it.cv.height = Math.round(r.height * dpr);
    it.cv.style.width = r.width + "px";
    it.cv.style.height = r.height + "px";
    it.ctx.setTransform(dpr, 0, 0, dpr, 0, 0);

    // Sparse: scaled by area, but hard-capped. A wide desktop card gets
    // ~13, a phone card ~6. Enough to read as a network, not a swarm.
    var target = Math.round((r.width * r.height) / 21000);
    target = Math.max(5, Math.min(13, target));
    while (it.nodes.length < target) it.nodes.push(makeNode(r.width, r.height));
    it.nodes.length = target;
    for (var i = 0; i < it.nodes.length; i++) {
      var n = it.nodes[i];
      if (n.x > r.width) n.x = rand(0, r.width);
      if (n.y > r.height) n.y = rand(0, r.height);
    }
  }

  function step(it) {
    var ctx = it.ctx, w = it.w, h = it.h, n = it.nodes, i, j;
    if (!w || !h) return;
    ctx.clearRect(0, 0, w, h);

    for (i = 0; i < n.length; i++) {
      var p = n[i];
      if (!reduced) {
        p.x += p.vx; p.y += p.vy;
        if (p.x < -20) p.x = w + 20; else if (p.x > w + 20) p.x = -20;
        if (p.y < -20) p.y = h + 20; else if (p.y > h + 20) p.y = -20;
      }
      // cursor push, eased so it glides back instead of snapping
      var tx = 0, ty = 0;
      var dx = p.x - it.mx, dy = p.y - it.my;
      var d = Math.sqrt(dx * dx + dy * dy);
      if (d < MOUSE_DIST && d > 0.01) {
        var f = (1 - d / MOUSE_DIST) * PUSH;
        tx = (dx / d) * f; ty = (dy / d) * f;
      }
      p.ox += (tx - p.ox) * 0.12;
      p.oy += (ty - p.oy) * 0.12;
    }

    // links between nodes
    ctx.lineWidth = 1;
    for (i = 0; i < n.length; i++) {
      var a = n[i], ax = a.x + a.ox, ay = a.y + a.oy;
      for (j = i + 1; j < n.length; j++) {
        var b = n[j], bx = b.x + b.ox, by = b.y + b.oy;
        var ddx = ax - bx, ddy = ay - by;
        var dd = Math.sqrt(ddx * ddx + ddy * ddy);
        if (dd < LINK_DIST) {
          ctx.strokeStyle = "rgba(255,255,255," + (0.30 * (1 - dd / LINK_DIST)).toFixed(3) + ")";
          ctx.beginPath(); ctx.moveTo(ax, ay); ctx.lineTo(bx, by); ctx.stroke();
        }
      }
      // link to the cursor
      var mdx = ax - it.mx, mdy = ay - it.my;
      var md = Math.sqrt(mdx * mdx + mdy * mdy);
      if (md < MOUSE_DIST) {
        ctx.strokeStyle = "rgba(255,255,255," + (0.34 * (1 - md / MOUSE_DIST)).toFixed(3) + ")";
        ctx.beginPath(); ctx.moveTo(ax, ay); ctx.lineTo(it.mx, it.my); ctx.stroke();
      }
      ctx.fillStyle = "rgba(255,255,255,.62)";
      ctx.beginPath(); ctx.arc(ax, ay, a.r, 0, 6.2832); ctx.fill();
    }
  }

  function frame() {
    for (var i = 0; i < items.length; i++) step(items[i]);
    requestAnimationFrame(frame);
  }

  function start() {
    var tiles = document.querySelectorAll(".gmu-tile");
    for (var i = 0; i < tiles.length; i++) {
      var it = setup(tiles[i]);
      if (it) items.push(it);
    }
    if (!items.length) return;

    // Tracked on window, not on the canvas: the canvas is
    // pointer-events:none so it never receives events itself.
    window.addEventListener("mousemove", function (e) {
      for (var k = 0; k < items.length; k++) {
        var r = items[k].tile.getBoundingClientRect();
        items[k].mx = e.clientX - r.left;
        items[k].my = e.clientY - r.top;
      }
    }, { passive: true });

    window.addEventListener("mouseleave", function () {
      for (var k = 0; k < items.length; k++) { items[k].mx = -9999; items[k].my = -9999; }
    }, { passive: true });

    window.addEventListener("resize", function () {
      for (var k = 0; k < items.length; k++) resize(items[k]);
    }, { passive: true });

    if (reduced) { for (var m = 0; m < items.length; m++) step(items[m]); }
    else requestAnimationFrame(frame);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", start);
  } else {
    start();
  }
})();
