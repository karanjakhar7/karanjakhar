// Rotating 3D node constellation behind the hero. Zero dependencies, Canvas 2D
// with manual perspective projection. Reads as neural net / knowledge graph / cosmos.
(function () {
  "use strict";

  var canvas = document.getElementById("site-bg");
  if (!canvas) return;
  var ctx = canvas.getContext("2d");
  if (!ctx) return;

  var GOLD = "231, 197, 154"; // --accent #e7c59a as rgb
  var FOCAL = 480;            // perspective focal length
  var LINK_DIST = 130;        // px (screen space) to draw a connecting line
  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  var W = 0, H = 0, dpr = 1;
  var points = [];
  var angleY = 0, angleX = 0;
  var running = false, rafId = 0, inView = true;

  function build() {
    var rect = canvas.getBoundingClientRect();
    W = rect.width;
    H = rect.height;
    dpr = Math.min(window.devicePixelRatio || 1, 2);
    canvas.width = Math.round(W * dpr);
    canvas.height = Math.round(H * dpr);
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);

    // count scales with area, capped; ~90 on a wide hero, ~45 on a narrow one
    var n = Math.round(Math.min(90, Math.max(40, (W * H) / 11000)));
    var spread = Math.min(W, 900) * 0.55;
    points = [];
    for (var i = 0; i < n; i++) {
      points.push({
        x: (Math.random() - 0.5) * spread * 2,
        y: (Math.random() - 0.5) * spread,
        z: (Math.random() - 0.5) * spread * 2,
        // tiny per-point drift so the cloud breathes rather than rotating rigidly
        dx: (Math.random() - 0.5) * 0.18,
        dy: (Math.random() - 0.5) * 0.18,
        dz: (Math.random() - 0.5) * 0.18
      });
    }
  }

  function draw() {
    ctx.clearRect(0, 0, W, H);
    var cx = W / 2, cy = H / 2;
    var cosY = Math.cos(angleY), sinY = Math.sin(angleY);
    var cosX = Math.cos(angleX), sinX = Math.sin(angleX);
    var proj = [];

    for (var i = 0; i < points.length; i++) {
      var p = points[i];
      p.x += p.dx; p.y += p.dy; p.z += p.dz;
      // rotate around Y then X
      var x1 = p.x * cosY - p.z * sinY;
      var z1 = p.x * sinY + p.z * cosY;
      var y1 = p.y * cosX - z1 * sinX;
      var z2 = p.y * sinX + z1 * cosX;
      var scale = FOCAL / (FOCAL + z2);
      proj.push({
        sx: cx + x1 * scale,
        sy: cy + y1 * scale,
        scale: scale
      });
    }

    // ponytail: O(n^2) pair scan, fine at ~90 pts; spatial grid only if N grows
    for (var a = 0; a < proj.length; a++) {
      for (var b = a + 1; b < proj.length; b++) {
        var ddx = proj[a].sx - proj[b].sx;
        var ddy = proj[a].sy - proj[b].sy;
        var d = Math.sqrt(ddx * ddx + ddy * ddy);
        if (d < LINK_DIST) {
          var alpha = (1 - d / LINK_DIST) * 0.4;
          ctx.strokeStyle = "rgba(" + GOLD + "," + alpha.toFixed(3) + ")";
          ctx.lineWidth = 1;
          ctx.beginPath();
          ctx.moveTo(proj[a].sx, proj[a].sy);
          ctx.lineTo(proj[b].sx, proj[b].sy);
          ctx.stroke();
        }
      }
    }

    for (var j = 0; j < proj.length; j++) {
      var pr = proj[j];
      var r = Math.max(0.6, pr.scale * 1.7);
      ctx.fillStyle = "rgba(" + GOLD + "," + (pr.scale * 0.9).toFixed(3) + ")";
      ctx.beginPath();
      ctx.arc(pr.sx, pr.sy, r, 0, Math.PI * 2);
      ctx.fill();
    }
  }

  function tick() {
    angleY += 0.0014;
    angleX = Math.sin(angleY * 0.5) * 0.18; // gentle tilt, no full X spin
    draw();
    rafId = requestAnimationFrame(tick);
  }

  function start() {
    if (running || reduce || !inView || document.hidden) return;
    running = true;
    rafId = requestAnimationFrame(tick);
  }

  function stop() {
    running = false;
    if (rafId) cancelAnimationFrame(rafId);
  }

  build();
  if (reduce) {
    draw(); // single static frame, no loop
  } else {
    start();
  }

  var resizeTimer;
  window.addEventListener("resize", function () {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(function () {
      build();
      if (reduce) draw();
    }, 200);
  });

  document.addEventListener("visibilitychange", function () {
    if (document.hidden) stop(); else start();
  });

  if ("IntersectionObserver" in window) {
    new IntersectionObserver(function (entries) {
      inView = entries[0].isIntersecting;
      if (inView) start(); else stop();
    }).observe(canvas);
  }
})();
