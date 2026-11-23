SKYSCOPE_HTML = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1">
<title>VEMMSUNJ · Satellite view</title>
<style>
html,body{margin:0;height:100%;background:#040507;color:#c9d6e3;font:12px/1.4 ui-monospace,Menlo,Consolas,monospace;overflow:hidden}
#scene{position:fixed;inset:0;width:100%;height:100%;display:block;touch-action:none;cursor:grab}
.panel{position:absolute;background:rgba(10,14,20,.93);border:1px solid #27324a;border-radius:4px;z-index:2;max-height:calc(100% - 120px);overflow:hidden;display:flex;flex-direction:column}
.ph{background:#151d2a;padding:6px 9px;font-weight:700;color:#8fb0cf;display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid #27324a;letter-spacing:.02em}
.pb{padding:8px 9px;overflow:auto;flex:1 1 auto}
#left{left:10px;top:10px;width:270px}
#right{right:10px;top:10px;width:270px}
#top{position:fixed;left:50%;transform:translateX(-50%);top:10px;z-index:3;color:#8fb0cf;font-weight:700;letter-spacing:.06em;white-space:nowrap}
#top a{color:#8fb0cf;margin-left:10px;font-weight:400}
#bar{position:fixed;left:50%;transform:translateX(-50%);bottom:10px;z-index:3;background:rgba(10,14,20,.93);border:1px solid #27324a;border-radius:4px;padding:6px 10px;display:flex;gap:8px;align-items:center;flex-wrap:wrap;justify-content:center}
button,input[type=text]{background:#17202d;color:#c9d6e3;border:1px solid #32415c;border-radius:3px;padding:4px 8px;font:inherit;cursor:pointer}
button.on{background:#25456b;border-color:#4d7bb0}
input[type=text]{cursor:text;width:100%;box-sizing:border-box;margin-bottom:6px}
#list{margin-top:4px}
.row{display:flex;align-items:center;gap:7px;padding:3px 4px;border-radius:3px;cursor:pointer;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.row:hover{background:#17202d}
.row.sel{background:#22395a;outline:1px solid #4d7bb0}
.row input{margin:0}
.dot{width:7px;height:7px;border-radius:50%;flex:0 0 auto}
.kv{display:flex;justify-content:space-between;gap:10px;padding:2px 0;border-bottom:1px dotted #1f2a3a}
.kv b{color:#8fb0cf;font-weight:400}
.muted{color:#6f8198}
#status{position:fixed;left:50%;transform:translateX(-50%);top:36px;z-index:3;color:#6f8198;font-size:11px}
@media (max-width:700px){
  #left{width:44%;max-height:44%;left:6px;top:34px;font-size:11px}
  #right{left:6px;right:6px;width:auto;top:auto;bottom:64px;max-height:36%}
  #top{font-size:11px;top:6px}
  #top a{display:none}
  #status{top:26px}
  #bar{font-size:11px;bottom:6px;width:calc(100% - 12px)}
}
</style>
</head>
<body>
<canvas id="scene"></canvas>
<div id="top">VEMMSUNJ · SATELLITE VIEW <a href="/globe">globe</a><a href="/tracker">tracker</a><a href="/">home</a></div>
<div id="status">Loading satellite positions…</div>

<div id="left" class="panel">
  <div class="ph"><span>Satellite Manager</span><span id="count" class="muted"></span></div>
  <div class="pb">
    <input id="q" type="text" placeholder="Search satellites">
    <div style="display:flex;gap:6px;margin-bottom:6px">
      <button id="all">All on</button><button id="none">All off</button>
      <label style="margin-left:auto"><input id="orb" type="checkbox"> Orbit lines</label>
    </div>
    <div id="list"></div>
  </div>
</div>

<div id="right" class="panel">
  <div class="ph"><span id="selname">No satellite selected</span><button id="clear" style="padding:0 6px">×</button></div>
  <div class="pb" id="info"><span class="muted">Tap a satellite on the globe, or pick one from the list, to see its details.</span></div>
</div>

<div id="bar">
  <button id="play" class="on">Pause</button>
  <button data-speed="1">1x</button>
  <button data-speed="60" class="on">60x</button>
  <button data-speed="600">600x</button>
  <button data-speed="3600">3600x</button>
  <button id="live">Live</button>
  <span id="utc" style="min-width:190px;text-align:center"></span>
</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>
(function () {
  var $ = function (s) { return document.querySelector(s); };
  var DEG = Math.PI / 180;
  var statusEl = $('#status');
  if (typeof THREE === 'undefined') { statusEl.textContent = '3D graphics could not load. Check your connection and reload.'; return; }

  var data = null, sats = [], visible = {}, selected = null, showOrbits = false;
  var snapMs = 0, simMs = Date.now(), playing = true, speed = 60;
  var lastT = performance.now(), lastInteract = 0, lastInfo = 0;

  // ---- scene ----
  var canvas = $('#scene');
  var renderer = new THREE.WebGLRenderer({ canvas: canvas, antialias: true });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
  var scene = new THREE.Scene();
  var camera = new THREE.PerspectiveCamera(40, 1, 0.01, 200);
  camera.position.set(0, 0, 3.6);
  var earthGroup = new THREE.Group();
  scene.add(earthGroup);
  scene.add(new THREE.AmbientLight(0x7d8fb5, 0.9));
  var sun = new THREE.DirectionalLight(0xffffff, 1.0);
  sun.position.set(5, 2, 4);
  scene.add(sun);

  // stars
  (function () {
    var n = 1800, p = new Float32Array(n * 3);
    for (var i = 0; i < n; i++) {
      var u = Math.random() * 2 - 1, t = Math.random() * Math.PI * 2, r = Math.sqrt(1 - u * u);
      p[i * 3] = 40 * r * Math.cos(t); p[i * 3 + 1] = 40 * u; p[i * 3 + 2] = 40 * r * Math.sin(t);
    }
    var g = new THREE.BufferGeometry();
    g.setAttribute('position', new THREE.BufferAttribute(p, 3));
    scene.add(new THREE.Points(g, new THREE.PointsMaterial({ color: 0xffffff, size: 1.2, sizeAttenuation: false })));
  })();

  // Earth: blue marble texture if it loads, otherwise a plain ocean colour
  var earthMat = new THREE.MeshPhongMaterial({ color: 0x2a5d8f, shininess: 8 });
  var loader = new THREE.TextureLoader();
  loader.crossOrigin = 'anonymous';
  loader.load('https://unpkg.com/three-globe@2.31.0/example/img/earth-blue-marble.jpg',
    function (t) { earthMat.map = t; earthMat.color.set(0xffffff); earthMat.needsUpdate = true; },
    undefined, function () {});
  earthGroup.add(new THREE.Mesh(new THREE.SphereGeometry(1, 96, 64), earthMat));

  var atmos = new THREE.Mesh(new THREE.SphereGeometry(1.04, 64, 48),
    new THREE.MeshBasicMaterial({ color: 0x4aa3ff, transparent: true, opacity: 0.12, side: THREE.BackSide }));
  scene.add(atmos);

  // ---- helpers ----
  // lat/lon/radius -> position. Matches three.js SphereGeometry texture mapping.
  function toVec(lat, lon, r) {
    var la = lat * DEG, lo = lon * DEG;
    return new THREE.Vector3(r * Math.cos(la) * Math.cos(lo), r * Math.sin(la), -r * Math.cos(la) * Math.sin(lo));
  }
  function colorFor(alt) {
    return alt < 2000 ? [0.5, 0.82, 1] : alt < 30000 ? [1, 0.84, 0.5] : [1, 0.62, 0.42];
  }
  // ground position of a satellite, elapsed seconds after the snapshot (interpolated on its stored samples)
  function groundAt(d, elapsed) {
    var g = d.ground;
    if (!g || g.length < 2 || !d.period_s) return null;
    var n = g.length - 1;
    var ph = (((elapsed % d.period_s) + d.period_s) % d.period_s) / d.period_s;
    var idx = ph * n, i0 = Math.floor(idx), i1 = Math.min(i0 + 1, n), f = idx - i0;
    var a = g[i0], b = g[i1];
    var dl = b[1] - a[1];
    if (dl > 180) dl -= 360;
    if (dl < -180) dl += 360;
    var lon = a[1] + dl * f;
    if (lon > 180) lon -= 360;
    if (lon < -180) lon += 360;
    return { lat: a[0] + (b[0] - a[0]) * f, lon: lon };
  }

  // ---- satellite points and orbit lines ----
  var posAttr = null, pointsObj = null, selObj = null, orbitGroup = new THREE.Group();
  earthGroup.add(orbitGroup);

  function build() {
    sats = data.satellites.filter(function (s) { return s.ground && s.ground.length > 1 && s.period_s; });
    var n = sats.length;
    var pos = new Float32Array(n * 3), col = new Float32Array(n * 3);
    sats.forEach(function (s, i) { visible[s.name] = true; col.set(colorFor(s.alt_km), i * 3); });
    var g = new THREE.BufferGeometry();
    posAttr = new THREE.BufferAttribute(pos, 3);
    g.setAttribute('position', posAttr);
    g.setAttribute('color', new THREE.BufferAttribute(col, 3));
    pointsObj = new THREE.Points(g, new THREE.PointsMaterial({ size: 3, vertexColors: true, sizeAttenuation: false }));
    earthGroup.add(pointsObj);
    var sg = new THREE.BufferGeometry();
    sg.setAttribute('position', new THREE.BufferAttribute(new Float32Array(3), 3));
    selObj = new THREE.Points(sg, new THREE.PointsMaterial({ size: 8, color: 0xffe066, sizeAttenuation: false }));
    selObj.visible = false;
    earthGroup.add(selObj);
    renderList();
    buildOrbits();
    $('#count').textContent = n + ' tracked';
    statusEl.textContent = 'Snapshot ' + (data.fetched_at || '').replace('T', ' ').slice(0, 16) + ' UTC · ' + n + ' satellites';
  }

  function buildOrbits() {
    while (orbitGroup.children.length) orbitGroup.remove(orbitGroup.children[0]);
    sats.forEach(function (s) {
      var isSel = selected && selected.name === s.name;
      if (!visible[s.name] || (!showOrbits && !isSel)) return;
      var pts = s.ground.map(function (p) { return toVec(p[0], p[1], 1 + s.alt_km / 6371); });
      var c = colorFor(s.alt_km);
      var line = new THREE.LineLoop(new THREE.BufferGeometry().setFromPoints(pts),
        new THREE.LineBasicMaterial({ color: new THREE.Color(c[0], c[1], c[2]), transparent: true,
          opacity: isSel ? 0.9 : 0.22 }));
      orbitGroup.add(line);
    });
  }

  function renderList() {
    var list = $('#list'), q = $('#q').value.trim().toLowerCase();
    list.textContent = '';
    sats.slice().sort(function (a, b) { return a.name.localeCompare(b.name); }).forEach(function (s) {
      if (q && s.name.toLowerCase().indexOf(q) < 0) return;
      var row = document.createElement('div');
      row.className = 'row' + (selected && selected.name === s.name ? ' sel' : '');
      row.dataset.name = s.name;
      var cb = document.createElement('input');
      cb.type = 'checkbox'; cb.checked = !!visible[s.name];
      cb.addEventListener('click', function (e) { e.stopPropagation(); });
      cb.addEventListener('change', function () { visible[s.name] = cb.checked; buildOrbits(); });
      var dot = document.createElement('span');
      var c = colorFor(s.alt_km);
      dot.className = 'dot';
      dot.style.background = 'rgb(' + Math.round(c[0] * 255) + ',' + Math.round(c[1] * 255) + ',' + Math.round(c[2] * 255) + ')';
      var name = document.createElement('span');
      name.textContent = s.name;
      row.appendChild(cb); row.appendChild(dot); row.appendChild(name);
      row.addEventListener('click', function () { select(s); });
      list.appendChild(row);
    });
  }

  function select(s) {
    selected = s;
    selObj.visible = !!s;
    buildOrbits();
    renderList();
    lastInfo = 0;
    if (window.matchMedia && window.matchMedia('(max-width:700px)').matches) {
      $('#right').style.display = 'flex';
    }
  }
  function deselect() {
    selected = null; selObj.visible = false; buildOrbits(); renderList();
    $('#info').innerHTML = '<span class="muted">Tap a satellite on the globe, or pick one from the list, to see its details.</span>';
    $('#selname').textContent = 'No satellite selected';
  }

  function updateInfo(elapsed) {
    if (!selected) return;
    var p = groundAt(selected, elapsed);
    if (!p) return;
    $('#selname').textContent = selected.name;
    var rows = [
      ['Latitude', p.lat.toFixed(2) + '°'],
      ['Longitude', p.lon.toFixed(2) + '°'],
      ['Altitude', Math.round(selected.alt_km) + ' km'],
      ['Speed', selected.speed_kms.toFixed(2) + ' km/s'],
      ['Orbit period', Math.round(selected.period_s / 60) + ' min'],
      ['Position time', new Date(simMs).toISOString().slice(0, 16).replace('T', ' ') + ' UTC']
    ];
    $('#info').innerHTML = rows.map(function (r) {
      return '<div class="kv"><span class="muted">' + r[0] + '</span><b>' + r[1] + '</b></div>';
    }).join('') + '<div class="muted" style="margin-top:6px">Positions are estimated from CelesTrak orbit data in the latest snapshot.</div>';
  }

  // ---- picking, dragging, zoom ----
  var drag = null, ray = new THREE.Raycaster();
  ray.params.Points.threshold = 0.04;
  canvas.addEventListener('pointerdown', function (e) {
    drag = { x: e.clientX, y: e.clientY, moved: 0 };
    lastInteract = Date.now();
    canvas.setPointerCapture(e.pointerId);
  });
  canvas.addEventListener('pointermove', function (e) {
    if (!drag) return;
    var dx = e.clientX - drag.x, dy = e.clientY - drag.y;
    drag.moved += Math.abs(dx) + Math.abs(dy);
    drag.x = e.clientX; drag.y = e.clientY;
    earthGroup.rotation.y += dx * 0.005;
    earthGroup.rotation.x = Math.max(-1.2, Math.min(1.2, earthGroup.rotation.x + dy * 0.005));
    lastInteract = Date.now();
  });
  canvas.addEventListener('pointerup', function (e) {
    if (drag && drag.moved < 6) pick(e);
    drag = null;
  });
  canvas.addEventListener('wheel', function (e) {
    e.preventDefault();
    camera.position.z = Math.max(1.6, Math.min(8, camera.position.z * (1 + e.deltaY * 0.001)));
    lastInteract = Date.now();
  }, { passive: false });

  function pick(e) {
    if (!pointsObj) return;
    var r = canvas.getBoundingClientRect();
    var m = new THREE.Vector2(((e.clientX - r.left) / r.width) * 2 - 1, -((e.clientY - r.top) / r.height) * 2 + 1);
    ray.setFromCamera(m, camera);
    var hits = ray.intersectObject(pointsObj).filter(function (h) {
      return visible[sats[h.index].name];
    });
    if (hits.length) { select(sats[hits[0].index]); updateInfo((simMs - snapMs) / 1000); }
    else deselect();
  }

  // ---- controls ----
  $('#q').addEventListener('input', renderList);
  $('#all').addEventListener('click', function () { sats.forEach(function (s) { visible[s.name] = true; }); renderList(); buildOrbits(); });
  $('#none').addEventListener('click', function () { sats.forEach(function (s) { visible[s.name] = false; }); renderList(); buildOrbits(); });
  $('#orb').addEventListener('change', function (e) { showOrbits = e.target.checked; buildOrbits(); });
  $('#clear').addEventListener('click', deselect);
  $('#play').addEventListener('click', function (e) {
    playing = !playing; e.target.textContent = playing ? 'Pause' : 'Play'; e.target.classList.toggle('on', playing);
  });
  document.querySelectorAll('[data-speed]').forEach(function (b) {
    b.addEventListener('click', function () {
      speed = Number(b.dataset.speed);
      document.querySelectorAll('[data-speed]').forEach(function (x) { x.classList.toggle('on', x === b); });
    });
  });
  $('#live').addEventListener('click', function () { simMs = Date.now(); playing = true; speed = 60; });

  // ---- data ----
  function load() {
    fetch('/api/globe', { cache: 'no-store' })
      .then(function (r) { return r.json(); })
      .then(function (d) {
        if (d.error || !d.satellites) { statusEl.textContent = d.error || 'No satellite data yet.'; return; }
        data = d;
        snapMs = Date.parse(d.fetched_at) || Date.now();
        if (!pointsObj) build();
        else { sats = []; data = d; build(); }
      })
      .catch(function () { statusEl.textContent = 'Satellite data could not be loaded. Try again shortly.'; });
  }

  // ---- render loop ----
  function resize() {
    var w = canvas.clientWidth, h = canvas.clientHeight;
    renderer.setSize(w, h, false);
    camera.aspect = w / h;
    camera.updateProjectionMatrix();
  }
  window.addEventListener('resize', resize);
  resize();

  function frame(t) {
    var dt = Math.min(0.1, (t - lastT) / 1000);
    lastT = t;
    if (playing) simMs += dt * 1000 * speed;
    var elapsed = (simMs - snapMs) / 1000;
    if (data && posAttr) {
      sats.forEach(function (s, i) {
        var p = visible[s.name] ? groundAt(s, elapsed) : null;
        if (p) {
          var v = toVec(p.lat, p.lon, 1 + s.alt_km / 6371);
          posAttr.setXYZ(i, v.x, v.y, v.z);
          if (selected === s) selObj.position.copy(v);
        } else {
          posAttr.setXYZ(i, 0, 0, 0);
        }
      });
      posAttr.needsUpdate = true;
      if (Date.now() - lastInfo > 500) { updateInfo(elapsed); lastInfo = Date.now(); }
    }
    if (!drag && Date.now() - lastInteract > 3000) earthGroup.rotation.y += dt * 0.04;
    $('#utc').textContent = new Date(simMs).toISOString().slice(0, 19).replace('T', ' ') + ' UTC';
    renderer.render(scene, camera);
    requestAnimationFrame(frame);
  }
  requestAnimationFrame(frame);
  load();
  setInterval(load, 5 * 60 * 1000);
})();
</script>
</body>
</html>
"""
