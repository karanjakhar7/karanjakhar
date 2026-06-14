// Layered feed-forward neural network behind the contact CTAs. Distinct node
// columns (input -> hidden -> hidden -> output), fully connected between
// adjacent layers, with activation pulses flowing left to right. Same gold
// dot-and-line language as the site background (hero-constellation.js).
(function () {
  "use strict";

  var canvas = document.querySelector(".contact-net-canvas");
  if (!canvas) return; // only present on the home page
  var ctx = canvas.getContext("2d");
  if (!ctx) return;

  var box = canvas.parentElement; // .contact-actions
  var GOLD = "231, 197, 154"; // --accent as rgb
  var LAYERS = [5, 8, 6, 3];  // gradual taper so every gap reads evenly dense
  var PAD_X = 16, PAD_Y = 24;
  var BEAT_MS = 1500;         // time for one layer to fire into the next (calm)
  var NODE_R = 3;           // base neuron radius (px)
  var OUT_NODE_R = 3.4;       // output-layer neuron radius (px)
  var FIRE_BUMP = 1.2;        // extra radius while a neuron fires / receives
  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  var W = 0, H = 0, dpr = 1;
  var layers = [];  // layers[i] = [{x, baseY, phase}, ...]
  var edges = [];   // {a, b, off} where a/b are node refs, off staggers the pulse
  var running = false, raf = 0, inView = true, t0 = 0;

  function measure() {
    var r = box.getBoundingClientRect();
    W = r.width; H = r.height;
    dpr = Math.min(window.devicePixelRatio || 1, 2);
    canvas.width = Math.round(W * dpr);
    canvas.height = Math.round(H * dpr);
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);

    // place nodes per layer; phases are deterministic so a resize never jumps.
    // Constant node spacing across layers, each layer centered vertically, so a
    // layer's height tracks its node count (it doesn't stretch to fill).
    layers = [];
    var usableW = Math.max(1, W - PAD_X * 2);
    var usableH = Math.max(1, H - PAD_Y * 2);
    var maxN = Math.max.apply(null, LAYERS);
    var gap = maxN > 1 ? usableH / (maxN - 1) : 0; // largest layer just fills the height
    for (var i = 0; i < LAYERS.length; i++) {
      var n = LAYERS[i];
      var x = PAD_X + (LAYERS.length === 1 ? usableW / 2 : (usableW * i) / (LAYERS.length - 1));
      var startY = H / 2 - ((n - 1) * gap) / 2; // center this layer
      var col = [];
      for (var k = 0; k < n; k++) {
        col.push({ x: x, baseY: startY + k * gap, phase: (i * 7 + k) * 0.9 });
      }
      layers.push(col);
    }

    // fully connect adjacent layers; tag each synapse with its gap index so a
    // whole layer's synapses can fire together
    edges = [];
    for (var L = 0; L < layers.length - 1; L++) {
      for (var a = 0; a < layers[L].length; a++) {
        for (var b = 0; b < layers[L + 1].length; b++) {
          // deterministic per-synapse weight (0.15..1): some fire bright, some dim
          var w = 0.15 + 0.85 * (((L * 131 + a * 977 + b * 53) % 100) / 100);
          edges.push({ a: layers[L][a], b: layers[L + 1][b], gap: L, w: w });
        }
      }
    }
  }

  function nodeY(node, time) {
    return node.baseY + Math.sin(time * 0.0012 + node.phase) * 1.2; // subtle bob
  }

  function line(ax, ay, bx, by, a) {
    ctx.strokeStyle = "rgba(" + GOLD + "," + a.toFixed(3) + ")";
    ctx.lineWidth = 1;
    ctx.beginPath(); ctx.moveTo(ax, ay); ctx.lineTo(bx, by); ctx.stroke();
  }
  function dot(x, y, r, a) {
    ctx.fillStyle = "rgba(" + GOLD + "," + a.toFixed(3) + ")";
    ctx.beginPath(); ctx.arc(x, y, r, 0, Math.PI * 2); ctx.fill();
  }

  function draw(time) {
    ctx.clearRect(0, 0, W, H);
    var i, e, ay, by, px, py;

    // forward pass: exactly one layer fires at a time. gap `g` is propagating;
    // `ep` (0..1) is how far its signal has travelled — shared by every synapse
    // in that gap, so the whole layer sends simultaneously.
    var G = layers.length - 1;
    var g = -1, ep = 0;
    if (!reduce && G > 0) {
      var cycle = (time / BEAT_MS);       // beats elapsed
      g = Math.floor(cycle) % G;          // active gap
      var p = cycle - Math.floor(cycle);  // raw progress within the beat
      ep = p < 0.5 ? 2 * p * p : 1 - Math.pow(-2 * p + 2, 2) / 2; // easeInOut
    }

    // synapses — line brightness tracks the connection's weight
    for (i = 0; i < edges.length; i++) {
      e = edges[i];
      ay = nodeY(e.a, time); by = nodeY(e.b, time);
      line(e.a.x, ay, e.b.x, by,
           e.gap === g ? 0.14 + e.w * 0.22 : 0.08 + e.w * 0.12);
    }
    // synchronized activation pulses; each fires at its own weighted intensity
    if (g >= 0) {
      for (i = 0; i < edges.length; i++) {
        e = edges[i];
        if (e.gap !== g) continue;
        ay = nodeY(e.a, time); by = nodeY(e.b, time);
        px = e.a.x + (e.b.x - e.a.x) * ep;
        py = ay + (by - ay) * ep;
        dot(px, py, 1.2 + e.w * 1.4, 0.18 + e.w * 0.67);
      }
    }
    // neurons: the firing (source) layer glows as it sends, the next layer
    // brightens as the signal arrives
    for (var L = 0; L < layers.length; L++) {
      var out = L === layers.length - 1;
      var glow = L === g ? (1 - ep) : (L === g + 1 ? ep : 0);
      for (var k = 0; k < layers[L].length; k++) {
        var node = layers[L][k];
        dot(node.x, nodeY(node, time),
            (out ? OUT_NODE_R : NODE_R) + glow * FIRE_BUMP,
            Math.min(1, (out ? 0.8 : 0.7) + glow * 0.15));
      }
    }
  }

  function step(ts) {
    if (!t0) t0 = ts;
    draw(ts - t0);
    raf = requestAnimationFrame(step);
  }

  function start() {
    if (running || reduce || !inView || document.hidden) return;
    running = true; raf = requestAnimationFrame(step);
  }
  function stop() { running = false; if (raf) cancelAnimationFrame(raf); }

  measure();
  if (reduce) draw(0); else start();

  var t;
  function rebuild() { clearTimeout(t); t = setTimeout(function () { measure(); if (reduce) draw(0); }, 200); }
  window.addEventListener("resize", rebuild);
  window.addEventListener("load", rebuild); // layout/fonts settle the box size
  document.addEventListener("visibilitychange", function () {
    if (document.hidden) stop(); else start();
  });
  if ("IntersectionObserver" in window) {
    new IntersectionObserver(function (ent) {
      inView = ent[0].isIntersecting; if (inView) start(); else stop();
    }).observe(canvas);
  }
})();
