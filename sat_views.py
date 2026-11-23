SAT_HTML = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1">
<title>VEMMSUNJ · __TITLE__</title>
<style>
html,body{margin:0;height:100%;background:#05070a;color:#cfd9e6;font:12px/1.4 ui-monospace,Menlo,Consolas,monospace;overflow:hidden}
#scene{position:fixed;inset:0;width:100%;height:100%;display:block;touch-action:none;cursor:grab}
.panel{position:absolute;background:rgba(9,13,19,.94);border:1px solid #243047;z-index:2;display:flex;flex-direction:column;max-height:calc(100% - 110px)}
.ph{background:#131c2a;padding:6px 9px;font-weight:700;color:#8fb0cf;display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid #243047}
.pb{padding:8px 9px;overflow:auto;flex:1 1 auto}
.sec{color:#4fa3ff;font-weight:700;margin:8px 0 4px;text-align:center;border-top:1px solid #243047;padding-top:6px}
#left{left:10px;top:10px;width:250px}
#right{right:10px;top:10px;width:280px}
#passes{left:10px;bottom:64px;width:330px;max-height:38%}
#bar{position:fixed;left:50%;transform:translateX(-50%);bottom:10px;z-index:3;background:rgba(9,13,19,.94);border:1px solid #243047;padding:6px 10px;display:flex;gap:6px;align-items:center;flex-wrap:wrap;justify-content:center}
#top{position:fixed;left:50%;transform:translateX(-50%);top:8px;z-index:3;color:#8fb0cf;font-weight:700;letter-spacing:.05em;white-space:nowrap}
#top a{color:#8fb0cf;margin-left:10px;font-weight:400;text-decoration:none}
#status{position:fixed;left:50%;transform:translateX(-50%);top:32px;z-index:3;color:#6f8198;font-size:11px;white-space:nowrap}
button,input[type=text],select{background:#16202e;color:#cfd9e6;border:1px solid #2f3f5a;padding:4px 7px;font:inherit;border-radius:2px}
button{cursor:pointer}
button.on{background:#2a4f7a;border-color:#5b8fc9}
input[type=text]{width:100%;box-sizing:border-box;margin-bottom:6px}
select{width:100%;margin-bottom:6px}
.row{display:flex;align-items:center;gap:6px;padding:3px 4px;cursor:pointer;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.row:hover{background:#16202e}
.row.sel{background:#1f3b5e;outline:1px solid #5b8fc9}
.row input{margin:0}
.dot{width:7px;height:7px;border-radius:50%;flex:0 0 auto}
.kv{display:flex;justify-content:space-between;gap:10px;padding:2px 0;border-bottom:1px dotted #1f2a3a}
.kv b{color:#8fb0cf;font-weight:400}
.muted{color:#6f8198}
.pass{display:flex;justify-content:space-between;gap:8px;padding:3px 4px;border-bottom:1px dotted #1f2a3a;white-space:nowrap}
.pass.hot{background:#15303f}
body.globe #left,body.globe #passes{display:none}
body.tracker #left{display:flex}
@media (max-width:700px){
  #left{width:42%;left:6px;top:30px;max-height:42%;font-size:11px}
  #right{left:6px;right:6px;width:auto;top:auto;bottom:58px;max-height:38%;font-size:11px}
  body.globe #right{top:30px;bottom:auto}
  #passes{display:none!important}
  #top{font-size:11px;top:6px}
  #top a{display:none}
  #status{top:24px;font-size:10px}
  #bar{bottom:4px;width:calc(100% - 10px);font-size:11px}
}
</style>
</head>
<body class="__MODE__">
<canvas id="scene"></canvas>
<div id="top">VEMMSUNJ · __TITLE__ <a href="/sat/globe">globe</a><a href="/sat/tracker">tracker</a><a href="/">home</a></div>
<div id="status">Loading satellite positions…</div>

<div id="left" class="panel">
  <div class="ph"><span>TLE Manager</span><button id="pull">Pull Data</button></div>
  <div class="pb">
    <div id="tleage" class="muted" style="margin-bottom:6px"></div>
    <div class="sec" style="border:0;margin:0 0 4px">Satellite Manager</div>
    <input id="q" type="text" placeholder="Search satellites">
    <div style="display:flex;gap:6px;margin-bottom:6px">
      <button id="all">All on</button><button id="none">All off</button>
      <label style="margin-left:auto"><input id="orb" type="checkbox"> Orbits</label>
    </div>
    <div id="list"></div>
  </div>
</div>

<div id="right" class="panel">
  <div class="ph"><span id="selname">No satellite selected</span><button id="clear" style="padding:0 6px">×</button></div>
  <div class="pb" id="info"><span class="muted">Tap a satellite on the Earth, or pick one from the list.</span></div>
</div>

<div id="passes" class="panel">
  <div class="ph"><span>Upcoming Passes</span><span class="muted" id="pcount"></span></div>
  <div class="pb">
    <select id="place"></select>
    <div id="plist"><span class="muted">Loading places…</span></div>
    <div class="muted" style="margin-top:6px">Times are UTC. Passes are predictions above 10°.</div>
  </div>
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
  var lastT = performance.now(), lastInteract = 0, lastInfo = 0, drag = null;
  var CAT = {};

  var canvas = $('#scene');
  var renderer = new THREE.WebGLRenderer({ canvas: canvas, antialias: true });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
  var scene = new THREE.Scene();
  var camera = new THREE.PerspectiveCamera(40, 1, 0.01, 200);
  camera.position.set(0, 0, 3.4);
  var earthGroup = new THREE.Group();
  scene.add(earthGroup);
  scene.add(new THREE.AmbientLight(0x8fa0c4, 0.9));
  var sun = new THREE.DirectionalLight(0xffffff, 1.0);
  sun.position.set(5, 2, 4);
  scene.add(sun);

  (function () {
    var n = 2200, p = new Float32Array(n * 3);
    for (var i = 0; i < n; i++) {
      var u = Math.random() * 2 - 1, t = Math.random() * Math.PI * 2, r = Math.sqrt(1 - u * u);
      p[i * 3] = 40 * r * Math.cos(t); p[i * 3 + 1] = 40 * u; p[i * 3 + 2] = 40 * r * Math.sin(t);
    }
    var g = new THREE.BufferGeometry();
    g.setAttribute('position', new THREE.BufferAttribute(p, 3));
    scene.add(new THREE.Points(g, new THREE.PointsMaterial({ color: 0xffffff, size: 1.1, sizeAttenuation: false })));
  })();

  var earthMat = new THREE.MeshPhongMaterial({ color: 0x2c6aa0, shininess: 10 });
  var loader = new THREE.TextureLoader();
  loader.crossOrigin = 'anonymous';
  loader.load('https://unpkg.com/three-globe@2.31.0/example/img/earth-blue-marble.jpg',
    function (t) { earthMat.map = t; earthMat.color.set(0xffffff); earthMat.needsUpdate = true; },
    undefined, function () {});
  earthGroup.add(new THREE.Mesh(new THREE.SphereGeometry(1, 96, 64), earthMat));
  scene.add(new THREE.Mesh(new THREE.SphereGeometry(1.035, 64, 48),
    new THREE.MeshBasicMaterial({ color: 0x4aa3ff, transparent: true, opacity: 0.1, side: THREE.BackSide })));

  function toVec(lat, lon, r) {
    var la = lat * DEG, lo = lon * DEG;
    return new THREE.Vector3(r * Math.cos(la) * Math.cos(lo), r * Math.sin(la), -r * Math.cos(la) * Math.sin(lo));
  }
  function colorFor(alt) {
    return alt < 2000 ? [0.45, 0.9, 1] : alt < 30000 ? [0.45, 1, 0.55] : [1, 0.6, 0.4];
  }
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

  var posAttr = null, pointsObj = null, selObj = null, orbitGroup = new THREE.Group();
  earthGroup.add(orbitGroup);

  function build() {
    sats = data.satellites.filter(function (s) { return s.ground && s.ground.length > 1 && s.period_s; });
    var n = sats.length;
    var pos = new Float32Array(n * 3), col = new Float32Array(n * 3);
    sats.forEach(function (s, i) {
      if (!(s.name in visible)) visible[s.name] = true;
      col.set(colorFor(s.alt_km), i * 3);
    });
    var g = new THREE.BufferGeometry();
    posAttr = new THREE.BufferAttribute(pos, 3);
    g.setAttribute('position', posAttr);
    g.setAttribute('color', new THREE.BufferAttribute(col, 3));
    if (pointsObj) earthGroup.remove(pointsObj);
    pointsObj = new THREE.Points(g, new THREE.PointsMaterial({ size: 3, vertexColors: true, sizeAttenuation: false }));
    earthGroup.add(pointsObj);
    if (!selObj) {
      var sg = new THREE.BufferGeometry();
      sg.setAttribute('position', new THREE.BufferAttribute(new Float32Array(3), 3));
      selObj = new THREE.Points(sg, new THREE.PointsMaterial({ size: 9, color: 0x39ff6a, sizeAttenuation: false }));
      selObj.visible = false;
      earthGroup.add(selObj);
    }
    renderList();
    buildOrbits();
    $('#tleage').textContent = n + ' satellites · snapshot ' + (data.fetched_at || '').replace('T', ' ').slice(0, 16) + ' UTC';
    statusEl.textContent = n + ' satellites · positions from the latest stored snapshot';
  }

  function buildOrbits() {
    while (orbitGroup.children.length) orbitGroup.remove(orbitGroup.children[0]);
    sats.forEach(function (s) {
      var isSel = selected && selected.name === s.name;
      if (!visible[s.name] || (!showOrbits && !isSel)) return;
      var pts = s.ground.map(function (p) { return toVec(p[0], p[1], 1 + s.alt_km / 6371); });
      var c = colorFor(s.alt_km);
      orbitGroup.add(new THREE.LineLoop(new THREE.BufferGeometry().setFromPoints(pts),
        new THREE.LineBasicMaterial({ color: new THREE.Color(c[0], c[1], c[2]), transparent: true, opacity: isSel ? 0.9 : 0.22 })));
    });
  }

  function renderList() {
    var list = $('#list'), q = $('#q').value.trim().toLowerCase();
    list.textContent = '';
    sats.slice().sort(function (a, b) { return a.name.localeCompare(b.name); }).forEach(function (s) {
      if (q && s.name.toLowerCase().indexOf(q) < 0) return;
      var row = document.createElement('div');
      row.className = 'row' + (selected && selected.name === s.name ? ' sel' : '');
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
    selObj.visible = true;
    buildOrbits();
    renderList();
    lastInfo = 0;
    updateInfo((simMs - snapMs) / 1000);
  }
  function deselect() {
    selected = null; selObj.visible = false; buildOrbits(); renderList();
    $('#selname').textContent = 'No satellite selected';
    $('#info').innerHTML = '<span class="muted">Tap a satellite on the Earth, or pick one from the list.</span>';
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
      ['Period', Math.round(selected.period_s / 60) + ' min'],
      ['Time (UTC)', new Date(simMs).toISOString().slice(0, 16).replace('T', ' ')]
    ];
    $('#info').innerHTML = '<div class="sec">Orbit Data</div>' + rows.map(function (r) {
      return '<div class="kv"><span class="muted">' + r[0] + '</span><b>' + r[1] + '</b></div>';
    }).join('') + '<div class="sec">Actions</div>' +
      '<div><button id="gt" class="' + (showOrbits ? 'on' : '') + '">Orbit lines on/off</button></div>' +
      '<div class="muted" style="margin-top:6px">Positions are estimated from CelesTrak orbit data in the latest snapshot.</div>';
    $('#gt').addEventListener('click', function () { showOrbits = !showOrbits; buildOrbits(); $('#orb').checked = showOrbits; });
  }

  var ray = new THREE.Raycaster();
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
    var hits = ray.intersectObject(pointsObj).filter(function (h) { return visible[sats[h.index].name]; });
    if (hits.length) select(sats[hits[0].index]); else deselect();
  }

  $('#q').addEventListener('input', renderList);
  $('#all').addEventListener('click', function () { sats.forEach(function (s) { visible[s.name] = true; }); renderList(); buildOrbits(); });
  $('#none').addEventListener('click', function () { sats.forEach(function (s) { visible[s.name] = false; }); renderList(); buildOrbits(); });
  $('#orb').addEventListener('change', function (e) { showOrbits = e.target.checked; buildOrbits(); });
  $('#clear').addEventListener('click', deselect);
  $('#pull').addEventListener('click', function () { load(); });
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

  function load() {
    fetch('/api/globe', { cache: 'no-store' })
      .then(function (r) { return r.json(); })
      .then(function (d) {
        if (d.error || !d.satellites) { statusEl.textContent = d.error || 'No satellite data yet.'; return; }
        data = d;
        snapMs = Date.parse(d.fetched_at) || Date.now();
        build();
      })
      .catch(function () { statusEl.textContent = 'Satellite data could not be loaded. Try again shortly.'; });
  }

  function loadPlaces() {
    fetch('/api/listings', { cache: 'no-store' })
      .then(function (r) { return r.json(); })
      .then(function (list) {
        var sel = $('#place');
        sel.textContent = '';
        (list || []).forEach(function (p) {
          var o = document.createElement('option');
          o.value = p.id; o.textContent = p.name;
          sel.appendChild(o);
        });
        sel.addEventListener('change', loadPasses);
        loadPasses();
      })
      .catch(function () { $('#plist').textContent = 'Places could not be loaded.'; });
  }

  function loadPasses() {
    var id = $('#place').value;
    if (!id) return;
    $('#plist').innerHTML = '<span class="muted">Loading passes…</span>';
    fetch('/api/passes/' + id, { cache: 'no-store' })
      .then(function (r) { return r.json(); })
      .then(function (d) {
        var ps = (d.passes || []).slice(0, 12);
        $('#pcount').textContent = ps.length ? ps.length + ' passes' : '';
        if (!ps.length) { $('#plist').innerHTML = '<span class="muted">No passes above 10° in the next 24 hours.</span>'; return; }
        var now = Date.now();
        $('#plist').textContent = '';
        ps.forEach(function (p) {
          var st = Date.parse(p.start), hot = st - now < 3600000 && st > now;
          var row = document.createElement('div');
          row.className = 'pass' + (hot ? ' hot' : '');
          var a = document.createElement('span'); a.textContent = p.satellite;
          var b = document.createElement('span');
          b.className = 'muted';
          b.textContent = String(p.start || '').slice(11, 16) + ' → ' + String(p.end || '').slice(11, 16) + '  ' + Math.round(p.max_altitude_deg || 0) + '°';
          row.appendChild(a); row.appendChild(b);
          $('#plist').appendChild(row);
        });
      })
      .catch(function () { $('#plist').textContent = 'Passes could not be loaded.'; });
  }

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
  if (document.body.classList.contains('tracker')) loadPlaces();
  setInterval(load, 5 * 60 * 1000);
})();
</script>
</body>
</html>
"""

def render_sat_page(mode):
    title = {"globe": "Interactive globe", "tracker": "Satellite tracker"}[mode]
    return SAT_HTML.replace("__MODE__", mode).replace("__TITLE__", title)
