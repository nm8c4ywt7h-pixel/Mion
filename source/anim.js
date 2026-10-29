// ===== EL PERRO — motor de animación (canvas 1080x1920) =====
const W = 1080, H = 1920, FLOOR = 1335;
const cv = document.getElementById('c'); let g = cv.getContext('2d');
const P = {
  wallTop: '#173037', wall: '#10242a', wain: '#0d1d22', floor: '#091316', rug: '#14303a', rugEdge: '#2c5360',
  bedFrame: '#0b171b', blanket: '#2c7062', blanketHi: '#3c8877', pillow: '#d5dcde',
  door: '#1a2e34', doorFrame: '#25403f', amber: '#eba446', amberHi: '#f6c46b',
  fur: '#a8763f', furDark: '#7a5129', furLight: '#c99a5e', collar: '#d9262b', tag: '#f3c434',
  skin: '#dedcd8', skinShade: '#b9b6b1', pj: '#3a66a6', pjHi: '#5b8fd2', pants: '#1f2f47',
  momSkin: '#d3cfcb', momShade: '#aba6a1', hair: '#4a291e', robe: '#6b3553', robeDark: '#4f2340',
  hi: '#c8f04b', red: '#ff3b3b'
};
const clamp = (v, a = 0, b = 1) => Math.max(a, Math.min(b, v));
const lerp = (a, b, t) => a + (b - a) * t;
const ease = t => (t = clamp(t), t < .5 ? 2 * t * t : 1 - Math.pow(-2 * t + 2, 2) / 2);
const eo = t => 1 - Math.pow(1 - clamp(t), 3);
const rnd = s => { const x = Math.sin(s * 12.9898 + 78.233) * 43758.5453; return x - Math.floor(x); };
const off = (w = W, h = H) => { const c = document.createElement('canvas'); c.width = w; c.height = h; return c; };

// ---------- timeline anchors ----------
const L = {}; TL.lines.forEach(l => L[String(l.id)] = l);
function A(s) {
  let [b, o] = s.split('+'); o = +(o || 0);
  let neg = 0; if (b.includes('-')) { [b, neg] = b.split('-'); neg = +neg; }
  const [id, c] = b.split(':'); const l = L[id];
  let t = c === 'echo' ? l.echo.t0 : c === 'end' ? l.t1 : c === 'start' ? l.t0 : l.chunks[+c].t0;
  return t + o - neg;
}

// ---------- primitives ----------
function rr(x, y, w, h, r) { g.beginPath(); g.roundRect(x, y, w, h, r); }
function line(pts, w, col) {
  g.strokeStyle = col; g.lineWidth = w; g.lineCap = 'round'; g.lineJoin = 'round';
  g.beginPath(); g.moveTo(pts[0], pts[1]); for (let i = 2; i < pts.length; i += 2) g.lineTo(pts[i], pts[i + 1]); g.stroke();
}
function circ(x, y, r, col) { g.fillStyle = col; g.beginPath(); g.arc(x, y, r, 0, 7); g.fill(); }
function ell(x, y, rx, ry, rot, col) { g.fillStyle = col; g.beginPath(); g.ellipse(x, y, rx, ry, rot, 0, 7); g.fill(); }
function shadedHead(x, y, r, base, shade, dir = 1) {
  circ(x, y, r, shade);
  g.save(); g.beginPath(); g.arc(x, y, r, 0, 7); g.clip();
  circ(x - dir * r * 0.22, y - r * 0.05, r * 0.95, base); g.restore();
}
function star4(x, y, r, col, a = 1) {
  g.save(); g.globalAlpha *= a; g.fillStyle = col; g.translate(x, y);
  for (let k = 0; k < 2; k++) {
    g.beginPath(); g.moveTo(0, -r); g.quadraticCurveTo(r * .12, -r * .12, r, 0); g.quadraticCurveTo(r * .12, r * .12, 0, r);
    g.quadraticCurveTo(-r * .12, r * .12, -r, 0); g.quadraticCurveTo(-r * .12, -r * .12, 0, -r); g.fill(); g.rotate(Math.PI / 4); r *= .55;
  }
  const gr = g.createRadialGradient(0, 0, 0, 0, 0, r * 4); gr.addColorStop(0, 'rgba(255,230,140,.55)'); gr.addColorStop(1, 'rgba(255,230,140,0)');
  g.fillStyle = gr; g.beginPath(); g.arc(0, 0, r * 4, 0, 7); g.fill(); g.restore();
}

// ---------- characters ----------
function drawKid(x, y, s, o = {}) {
  g.save(); g.globalAlpha *= (o.alpha ?? 1);
  const arm = o.arm || 'down', tr = o.tremble ? Math.sin(o.t * 70) * 2 * s : 0; x += tr;
  // legs
  line([x - 16 * s, y - 230 * s, x - 30 * s, y - 8 * s], 28 * s, P.pants);
  line([x + 16 * s, y - 230 * s, x + 30 * s, y - 8 * s], 28 * s, P.pants);
  ell(x - 36 * s, y, 22 * s, 10 * s, 0, P.skinShade); ell(x + 36 * s, y, 22 * s, 10 * s, 0, P.skinShade);
  // left arm
  line([x - 44 * s, y - 410 * s, x - 66 * s, y - 250 * s], 24 * s, P.pj); circ(x - 67 * s, y - 242 * s, 13 * s, P.skin);
  // torso (striped pyjamas)
  g.save(); rr(x - 52 * s, y - 440 * s, 104 * s, 225 * s, 30 * s); g.fillStyle = P.pj; g.fill(); g.clip();
  g.fillStyle = P.pjHi; for (let k = 0; k < 9; k++) g.fillRect(x - 60 * s, y - 432 * s + k * 28 * s, 120 * s, 9 * s);
  g.restore();
  // right arm
  const ra = { down: [x + 66 * s, y - 250 * s], point: [x - 225 * s, y - 400 * s], reach: [x - 175 * s, y - 335 * s], back: [x + 40 * s, y - 260 * s] }[arm];
  line([x + 44 * s, y - 410 * s, ra[0], ra[1]], 24 * s, P.pj); circ(ra[0], ra[1], 13 * s, P.skin);
  // head + hair tuft
  shadedHead(x, y - 500 * s, 64 * s, P.skin, P.skinShade, -1);
  g.fillStyle = '#3a2418'; g.beginPath();
  g.moveTo(x - 50 * s, y - 540 * s); g.quadraticCurveTo(x - 10 * s, y - 600 * s, x + 52 * s, y - 545 * s);
  g.quadraticCurveTo(x + 20 * s, y - 562 * s, x + 6 * s, y - 548 * s); g.quadraticCurveTo(x - 20 * s, y - 566 * s, x - 50 * s, y - 540 * s); g.fill();
  if (o.mouth) { circ(x + 14 * s, y - 470 * s, 7 * s, '#555'); }
  g.restore();
}

function drawMom(x, y, s, o = {}) {
  g.save(); g.globalAlpha *= (o.alpha ?? 1);
  const hand = o.hand ?? 0;
  // hair behind
  g.fillStyle = P.hair; g.beginPath(); g.ellipse(x - 14 * s, y - 640 * s, 90 * s, 135 * s, 0, 0, 7); g.fill();
  // legs
  line([x - 18 * s, y - 330 * s, x - 26 * s, y - 10 * s], 30 * s, P.momShade);
  line([x + 18 * s, y - 330 * s, x + 26 * s, y - 10 * s], 30 * s, P.momSkin);
  // robe
  g.fillStyle = P.robe; g.beginPath(); g.moveTo(x - 64 * s, y - 625 * s); g.lineTo(x + 64 * s, y - 625 * s);
  g.lineTo(x + 100 * s, y - 300 * s); g.lineTo(x - 100 * s, y - 300 * s); g.closePath(); g.fill();
  g.fillStyle = P.robeDark; g.beginPath(); g.moveTo(x + 4 * s, y - 625 * s); g.lineTo(x + 26 * s, y - 470 * s); g.lineTo(x + 70 * s, y - 300 * s); g.lineTo(x + 100 * s, y - 300 * s); g.lineTo(x + 64 * s, y - 625 * s); g.fill();
  line([x - 70 * s, y - 470 * s, x + 74 * s, y - 470 * s], 12 * s, P.robeDark);
  g.fillStyle = P.momSkin; g.beginPath(); g.moveTo(x - 22 * s, y - 625 * s); g.lineTo(x + 22 * s, y - 625 * s); g.lineTo(x, y - 560 * s); g.fill();
  // left arm down
  line([x - 56 * s, y - 600 * s, x - 82 * s, y - 380 * s], 26 * s, P.robe); circ(x - 84 * s, y - 372 * s, 14 * s, P.momSkin);
  // right arm (out into room)
  const hx = lerp(x + 80 * s, x + 360 * s, hand), hy = lerp(y - 380 * s, y - 560 * s, hand);
  const ex = lerp(x + 72 * s, x + 200 * s, hand), ey = lerp(y - 490 * s, y - 585 * s, hand);
  line([x + 56 * s, y - 600 * s, ex, ey], 26 * s, P.robe);
  line([ex, ey, hx, hy], 22 * s, P.momSkin); circ(hx, hy, 15 * s, P.momSkin);
  // head
  shadedHead(x, y - 705 * s, 74 * s, P.momSkin, P.momShade, 1);
  // fringe
  g.fillStyle = P.hair; g.beginPath(); g.moveTo(x - 76 * s, y - 715 * s); g.quadraticCurveTo(x - 40 * s, y - 800 * s, x + 40 * s, y - 782 * s);
  g.quadraticCurveTo(x - 6 * s, y - 760 * s, x - 76 * s, y - 715 * s); g.fill();
  if (o.smile) { g.strokeStyle = '#2a2220'; g.lineWidth = 6 * s; g.lineCap = 'round'; g.beginPath(); g.arc(x + 10 * s, y - 718 * s, 40 * s * o.smile, 0.25 * Math.PI, 0.75 * Math.PI); g.stroke(); }
  g.restore();
}

function drawDogHead(cx, cy, r, o = {}) {
  // ears
  ell(cx - r * .92, cy + r * .45, r * .42, r * 1.05, .18, P.furDark);
  ell(cx + r * .92, cy + r * .45, r * .42, r * 1.05, -.18, P.furDark);
  circ(cx, cy, r, P.fur);
  // muzzle triangle
  g.fillStyle = P.furLight; g.beginPath(); g.moveTo(cx - r * .62, cy + r * .02); g.lineTo(cx + r * .62, cy + r * .02); g.lineTo(cx, cy + r * 1.08); g.closePath(); g.fill();
  // eyes
  const ey = cy - r * .12, ex = r * .33, er = r * .23;
  const lk = o.look ?? 0;
  circ(cx - ex, ey, er, '#050505'); circ(cx + ex, ey, er, '#050505');
  circ(cx - ex + er * .25 + lk * er * .3, ey - er * .25, er * .3, '#fff'); circ(cx + ex + er * .25 + lk * er * .3, ey - er * .25, er * .3, '#fff');
  // brows
  line([cx - ex - er * 1.2, ey - er * 1.45, cx - ex + er * .9, ey - er * 1.0], r * .1, '#3b2512');
  line([cx + ex + er * 1.2, ey - er * 1.45, cx + ex - er * .9, ey - er * 1.0], r * .1, '#3b2512');
  // mouth
  const tt = o.teeth || 0;
  if (tt <= 0) { ell(cx, cy + r * .6, r * .09, r * .13, 0, '#0a0503'); }
  else {
    const mw = r * lerp(.15, .62, tt), my = cy + r * .55;
    g.fillStyle = '#3a0606'; g.beginPath(); g.moveTo(cx - mw, my - r * .08 * tt); g.quadraticCurveTo(cx, my + r * .35 * tt, cx + mw, my - r * .08 * tt);
    g.quadraticCurveTo(cx, my + r * .08, cx - mw, my - r * .08 * tt); g.fill();
    g.fillStyle = '#f4f4f4'; const n = 7;
    for (let i = 0; i < n; i++) {
      const a = i / (n - 1), tx = lerp(cx - mw * .9, cx + mw * .9, a), ty = my - r * .05 * tt + Math.sin(a * Math.PI) * r * .12 * tt;
      g.beginPath(); g.moveTo(tx - mw / n, ty - 3); g.lineTo(tx + mw / n, ty - 3); g.lineTo(tx, ty + r * .12 * tt); g.fill();
    }
  }
  // cracks
  if (o.cracks > 0) {
    g.save(); g.strokeStyle = '#fffbe8'; g.lineWidth = r * .045; g.lineJoin = 'miter'; g.shadowColor = 'rgba(255,255,220,.8)'; g.shadowBlur = r * .08;
    const cr = [[[-.6, .6], [-.42, .3], [-.5, .05], [-.25, -.2]], [[.35, -.75], [.5, -.4], [.32, -.15], [.58, .15], [.4, .5], [.5, .8], [.3, 1.1]], [[.5, -.4], [.78, -.3]], [[-.42, .3], [-.75, .35]]];
    cr.forEach(seg => {
      const n = Math.max(1, Math.floor(seg.length * o.cracks + .999)); g.beginPath();
      seg.slice(0, n).forEach((p, i) => i ? g.lineTo(cx + p[0] * r, cy + p[1] * r) : g.moveTo(cx + p[0] * r, cy + p[1] * r)); g.stroke();
    }); g.restore();
  }
}

function drawFake(x, y, s, o = {}) {
  g.save(); g.globalAlpha *= (o.alpha ?? 1);
  const sw = Math.sin((o.t || 0) * 1.7) * 6 * s;
  // legs
  line([x - 42 * s, y - 470 * s, x - 58 * s, y - 240 * s, x - 46 * s, y - 14 * s], 28 * s, P.furDark);
  line([x + 42 * s, y - 470 * s, x + 58 * s, y - 240 * s, x + 46 * s, y - 14 * s], 28 * s, P.furDark);
  ell(x - 56 * s, y - 6 * s, 30 * s, 12 * s, 0, P.furDark); ell(x + 56 * s, y - 6 * s, 30 * s, 12 * s, 0, P.furDark);
  // arms
  line([x - 96 * s, y - 790 * s, x - 130 * s, y - 600 * s, x - 118 * s + sw, y - 400 * s], 22 * s, P.furDark);
  line([x + 96 * s, y - 790 * s, x + 130 * s, y - 600 * s, x + 118 * s - sw, y - 400 * s], 22 * s, P.furDark);
  // neck + torso
  g.fillStyle = P.fur; g.fillRect(x - 40 * s, y - 880 * s, 80 * s, 100 * s);
  rr(x - 100 * s, y - 805 * s, 200 * s, 350 * s, 46 * s); g.fillStyle = P.fur; g.fill();
  g.fillStyle = 'rgba(0,0,0,.12)'; g.fillRect(x + 20 * s, y - 800 * s, 80 * s, 340 * s);
  g.strokeStyle = '#6a4321'; g.lineWidth = 8 * s; g.lineCap = 'round';
  for (let k = 0; k < 4; k++) { g.beginPath(); g.arc(x, y - 760 * s + k * 62 * s, 62 * s, .25 * Math.PI, .75 * Math.PI); g.stroke(); }
  ell(x + 48 * s, y - 520 * s, 18 * s, 12 * s, 0, P.furLight); ell(x - 50 * s, y - 640 * s, 12 * s, 9 * s, 0, P.furLight);
  drawDogHead(x, y - 965 * s, 122 * s, o);
  g.restore();
}

function drawBuddy(x, y, s, o = {}) {
  g.save(); g.translate(x, y); if (o.dir === -1) g.scale(-1, 1); g.scale(s, s);
  const ly = o.lying ? 1 : 0, tr = o.tremble ? Math.sin(o.t * 80) * 2.5 : 0; g.translate(tr, 0);
  const by = lerp(-175, -78, ly), hy = lerp(-262, -140, ly);
  // tail
  const wag = Math.sin((o.t || 0) * (o.wag ? 14 : 2)) * 10;
  line([-195, by - 10, -245, by - 60 + wag, -255, by - 120 + wag], 16, P.fur);
  // legs
  if (!ly) [-150, -95, 85, 140].forEach((lx, i) => { rr(lx - 18, by + 20, 36, 155, 16); g.fillStyle = i % 2 ? P.fur : P.furDark; g.fill(); });
  ell(0, by, 205, lerp(78, 64, ly), 0, P.fur);
  ell(10, by + 32, 160, 30, 0, 'rgba(255,255,255,.06)');
  if (o.growl) { g.fillStyle = P.furDark; for (let k = 0; k < 7; k++) { const hx = -150 + k * 34; g.beginPath(); g.moveTo(hx - 14, by - 62); g.lineTo(hx, by - 105 - (k % 2) * 14); g.lineTo(hx + 14, by - 62); g.fill(); } }
  // head
  circ(195, hy, 88, P.fur);
  ell(272, hy + 34, 76, 48, .06, P.furLight);
  circ(342, hy + 22, 17, '#120a05');
  if (o.growl) {
    g.fillStyle = '#2b0a06'; g.beginPath(); g.moveTo(222, hy + 62); g.quadraticCurveTo(290, hy + 92, 340, hy + 58); g.lineTo(330, hy + 72); g.quadraticCurveTo(285, hy + 104, 226, hy + 74); g.fill();
    g.fillStyle = '#f5f5f5'; for (let k = 0; k < 5; k++) { const tx = 238 + k * 21; g.beginPath(); g.moveTo(tx - 9, hy + 64 + k * 1.5); g.lineTo(tx + 9, hy + 64 + k * 1.5); g.lineTo(tx, hy + 84); g.fill(); }
  }
  // eye + brow
  circ(215, hy - 20, 23, '#050505'); circ(222, hy - 27, 7, '#fff'); circ(211, hy - 25, 4.5, '#fff');
  if (o.growl) line([178, hy - 66, 248, hy - 44], 10, '#3a2412'); else line([182, hy - 52, 246, hy - 66], 9, '#3a2412');
  if (o.tear) { g.fillStyle = 'rgba(160,210,255,.9)'; g.beginPath(); g.moveTo(222, hy + 6); g.quadraticCurveTo(232, hy + 30, 222, hy + 36); g.quadraticCurveTo(212, hy + 30, 222, hy + 6); g.fill(); }
  // ear
  ell(150, hy + 10, 42, 86, .35, P.furDark);
  // collar + tag
  line([118, hy - 62, 160, hy + 78], 36, P.collar);
  circ(162, hy + 96, 20, P.tag); circ(158, hy + 92, 6, 'rgba(255,255,255,.5)');
  g.restore();
  if (o.glint > 0) {
    const gx = x + (o.dir === -1 ? -162 : 162) * s, gy = y + (hy + 96) * s;
    star4(gx, gy, 70 * s * o.glint, '#fff6c8', clamp(o.glint * 1.4));
  }
}

// ---------- the room ----------
function drawRoom(o = {}) {
  const t = o.t || 0;
  let gr = g.createLinearGradient(0, 0, 0, FLOOR); gr.addColorStop(0, P.wallTop); gr.addColorStop(1, P.wall);
  g.fillStyle = gr; g.fillRect(-400, -400, W + 800, FLOOR + 400);
  // subtle diamond wallpaper
  g.strokeStyle = 'rgba(255,255,255,.025)'; g.lineWidth = 2;
  for (let k = -20; k < 30; k++) { g.beginPath(); g.moveTo(k * 90, -400); g.lineTo(k * 90 + 1400, FLOOR + 1000); g.stroke(); g.beginPath(); g.moveTo(k * 90, -400); g.lineTo(k * 90 - 1400, FLOOR + 1000); g.stroke(); }
  // wainscot
  g.fillStyle = P.wain; g.fillRect(-400, 1000, W + 800, FLOOR - 1000);
  g.fillStyle = 'rgba(255,255,255,.04)'; g.fillRect(-400, 995, W + 800, 10);
  g.strokeStyle = 'rgba(0,0,0,.25)'; g.lineWidth = 3; for (let k = -4; k < 16; k++) { g.beginPath(); g.moveTo(k * 110, 1015); g.lineTo(k * 110, FLOOR); g.stroke(); }
  // window with blinds + moon
  rr(585, 215, 310, 400, 6); g.fillStyle = P.doorFrame; g.fill();
  gr = g.createLinearGradient(0, 235, 0, 595); gr.addColorStop(0, '#0d2738'); gr.addColorStop(1, '#1d4456'); g.fillStyle = gr; g.fillRect(603, 233, 274, 364);
  for (let k = 0; k < 9; k++) circ(620 + rnd(k) * 240, 260 + rnd(k + 9) * 300, 2.5 + rnd(k + 3) * 2, `rgba(255,255,230,${.4 + .5 * Math.abs(Math.sin(t * 2 + k))})`);
  circ(810, 345, 48, '#ece6c6'); circ(830, 330, 44, '#163a4c');
  g.fillStyle = '#28434a'; for (let k = 0; k < 7; k++) g.fillRect(603, 233 + k * 22, 274, 13);
  g.fillStyle = P.doorFrame; g.fillRect(735, 233, 10, 364); g.fillRect(603, 410, 274, 10);
  // moonlight beam on floor
  g.fillStyle = 'rgba(160,215,230,.05)'; g.beginPath(); g.moveTo(603, 597); g.lineTo(877, 597); g.lineTo(1000, 1700); g.lineTo(560, 1700); g.fill();
  // pennant garland
  g.strokeStyle = '#3d555b'; g.lineWidth = 3; g.beginPath(); g.moveTo(380, 120); g.quadraticCurveTo(730, 210, 1090, 120); g.stroke();
  const pc = ['#c99a3a', '#3f8c7c', '#b5574b', '#5d7fb0'];
  for (let k = 0; k < 9; k++) { const a = k / 8, px = lerp(400, 1070, a), py = 120 + Math.sin(a * Math.PI) * 45; g.fillStyle = pc[k % 4]; g.globalAlpha = .55; g.beginPath(); g.moveTo(px - 26, py); g.lineTo(px + 26, py); g.lineTo(px, py + 62); g.fill(); g.globalAlpha = 1; }
  // poster above bed (mountains + moon)
  rr(870, 660, 160, 210, 4); g.fillStyle = '#26383d'; g.fill(); g.fillStyle = '#18323c'; g.fillRect(882, 672, 136, 186);
  g.fillStyle = '#2f6d63'; g.beginPath(); g.moveTo(882, 858); g.lineTo(930, 770); g.lineTo(970, 820); g.lineTo(995, 790); g.lineTo(1018, 858); g.fill(); circ(990, 715, 16, '#e8c76a');
  // door (left)
  const dop = o.door ?? 0;
  rr(60, 540, 320, 800, 4); g.fillStyle = P.doorFrame; g.fill();
  if (dop > 0) {
    gr = g.createLinearGradient(80, 0, 360, 0);
    if (o.darkDoor) { gr.addColorStop(0, '#020303'); gr.addColorStop(1, '#070909'); }
    else { gr.addColorStop(0, P.amberHi); gr.addColorStop(1, P.amber); }
    g.fillStyle = gr; g.fillRect(80, 560, 280, 780);
    // door slab swinging in (hinge right side)
    const sw = 280 * (1 - dop);
    g.fillStyle = P.door; g.beginPath(); g.moveTo(360, 560); g.lineTo(360 - sw, 560 + 30 * dop); g.lineTo(360 - sw, 1335 - 30 * dop); g.lineTo(360, 1335); g.fill();
    if (!o.darkDoor) { g.fillStyle = 'rgba(235,164,70,.12)'; g.beginPath(); g.moveTo(80, 1335); g.lineTo(360, 1335); g.lineTo(520, 1700); g.lineTo(-60, 1700); g.fill(); }
  } else {
    g.fillStyle = P.door; g.fillRect(80, 560, 280, 778);
    g.strokeStyle = 'rgba(0,0,0,.25)'; g.lineWidth = 4; g.strokeRect(115, 600, 210, 300); g.strokeRect(115, 950, 210, 340);
    circ(110, 960, 10, '#6d8086');
  }
  if (o.scratch > 0) {
    g.save(); g.strokeStyle = '#e8dcc0'; g.lineWidth = 7; g.lineCap = 'round';
    for (let k = 0; k < 4; k++) { const a = clamp(o.scratch * 4 - k); if (a <= 0) continue; const sx = 200 + k * 28; g.beginPath(); g.moveTo(sx, 880 + k * 6); g.lineTo(sx + 6 * a, 880 + k * 6 + 230 * a); g.stroke(); }
    g.restore();
  }
  if (o.momInDoor) o.momInDoor();
  if (o.eyesInDoor) { const a = o.eyesInDoor; g.fillStyle = `rgba(30,20,15,${.9 * a})`; g.beginPath(); g.ellipse(230, 900, 95, 160, 0, 0, 7); g.fill(); circ(205, 870, 7, `rgba(255,230,170,${a})`); circ(255, 870, 7, `rgba(255,230,170,${a})`); }
  // nightstand + lamp + clock
  g.fillStyle = '#0e1c20'; g.fillRect(430, 1150, 150, 188); g.fillStyle = '#152a30'; g.fillRect(420, 1140, 170, 16);
  line([505, 1140, 505, 1060], 8, '#33484e'); g.fillStyle = '#2f4a51'; g.beginPath(); g.moveTo(462, 1060); g.lineTo(548, 1060); g.lineTo(530, 1005); g.lineTo(480, 1005); g.fill();
  rr(440, 1095, 70, 42, 6); g.fillStyle = '#050909'; g.fill();
  g.fillStyle = '#ff2f2f'; g.font = '700 26px "JetBrains Mono"'; g.textAlign = 'center'; g.textBaseline = 'middle'; g.fillText('3:33', 475, 1117);
  // floor
  gr = g.createLinearGradient(0, FLOOR, 0, H + 400); gr.addColorStop(0, '#0c181b'); gr.addColorStop(1, '#050b0d');
  g.fillStyle = gr; g.fillRect(-400, FLOOR, W + 800, H + 800);
  g.strokeStyle = 'rgba(255,255,255,.03)'; g.lineWidth = 3; for (let k = 0; k < 8; k++) { g.beginPath(); g.moveTo(-400, FLOOR + 40 + k * k * 18); g.lineTo(W + 400, FLOOR + 40 + k * k * 18); g.stroke(); }
  // rug
  ell(560, 1610, 440, 130, 0, P.rug);
  g.save(); g.setLineDash([22, 16]); g.strokeStyle = P.rugEdge; g.lineWidth = 5; g.beginPath(); g.ellipse(560, 1610, 405, 110, 0, 0, 7); g.stroke(); g.restore();
  // bed (right)
  g.fillStyle = P.bedFrame; g.fillRect(630, 1130, 520, 215);
  rr(640, 1080, 160, 60, 24); g.fillStyle = P.pillow; g.fill();
  rr(625, 1120, 560, 135, 34); g.fillStyle = P.blanket; g.fill();
  g.save(); g.clip(); g.strokeStyle = P.blanketHi; g.lineWidth = 6; for (let k = 0; k < 9; k++) { g.beginPath(); g.moveTo(660 + k * 60, 1130); g.lineTo(640 + k * 60, 1255); g.stroke(); }
  g.fillStyle = 'rgba(255,255,255,.05)'; g.fillRect(620, 1180, 600, 18); g.restore();
  g.fillStyle = '#030607'; g.fillRect(650, 1255, 520, 80);
}

function tallShadow(fn, a) {
  const c = off(); const gg = g; g = c.getContext('2d'); fn(); g = gg;
  g.save(); g.globalAlpha = a; g.filter = 'brightness(0) blur(6px)';
  g.translate(90, FLOOR); g.transform(1, 0, -0.12, 1.55, 0, 0); g.translate(-0, -FLOOR); g.drawImage(c, 0, 0); g.restore();
}

// ---------- scenes ----------
const SC = {};
SC.room = (lt, p, o, t) => {
  drawRoom({ t, door: o.door?.(lt, p) ?? o.doorV ?? 0, darkDoor: o.darkDoor, scratch: o.scratch?.(lt, p) ?? 0,
    eyesInDoor: o.eyes?.(lt, p) ?? 0,
    momInDoor: o.mom ? () => drawMom(o.mom.x ?? 215, FLOOR + 2, o.mom.s ?? 0.95, { hand: o.mom.hand?.(lt, p) ?? o.mom.handV ?? 0, smile: o.mom.smile ?? 0, alpha: o.mom.alpha?.(lt, p) ?? 1 }) : null });
  if (o.fake && o.shadow) tallShadow(() => drawFake(o.fake.x, o.fake.y, o.fake.s, { t }), o.shadow);
  if (o.drain) { const a = o.drain(lt, p); ell(470, 1640, 120, 30, 0, `rgba(0,0,0,${.9 * a})`); g.strokeStyle = `rgba(70,90,95,${a})`; g.lineWidth = 4; for (let k = -2; k <= 2; k++) { g.beginPath(); g.moveTo(470 + k * 36, 1618); g.lineTo(470 + k * 36, 1662); g.stroke(); } circ(452, 1640, 5, `rgba(255,220,160,${a * (.5 + .5 * Math.sin(t * 9))})`); circ(488, 1640, 5, `rgba(255,220,160,${a * (.5 + .5 * Math.sin(t * 9))})`); }
  if (o.buddy) { const b = o.buddy; drawBuddy(b.x?.(lt, p) ?? b.xV, b.y ?? 1700, b.s ?? 0.55, { t, dir: b.dir ?? -1, growl: b.growl, wag: b.wag }); }
  if (o.kid) drawKid(o.kid.x ?? 760, o.kid.y ?? 1660, o.kid.s ?? 1, { t, arm: o.kid.arm?.(lt, p) ?? o.kid.armV, tremble: o.kid.tremble, alpha: o.kid.alpha ?? 1 });
  if (o.fake) {
    const f = o.fake, ft = { t, teeth: f.teeth?.(lt, p) ?? f.teethV ?? 0, cracks: f.cracks?.(lt, p) ?? f.cracksV ?? 0 };
    const melt = f.melt?.(lt, p) ?? 0;
    if (melt <= 0) drawFake(f.x, f.y, f.s, ft);
    else {
      const c = off(); const gg = g; g = c.getContext('2d'); drawFake(f.x, f.y, f.s, ft); g = gg;
      g.save(); g.beginPath(); g.rect(-500, -500, W + 1000, f.y + 520); g.clip();
      g.filter = `brightness(${lerp(1, .05, clamp(melt * 1.6))})`;
      for (let sx = 0; sx < W; sx += 6) {
        const dy = melt * 1150 * (0.55 + 0.45 * Math.sin(sx * 0.045 + 1.3) * Math.sin(sx * .013));
        g.drawImage(c, sx, 0, 6, H, sx, dy * clamp(melt * 1.2), 6, H);
      }
      g.restore();
    }
  }
  if (o.redLine) { const a = o.redLine(lt, p); g.save(); g.setLineDash([34, 18]); g.strokeStyle = `rgba(255,40,40,${a})`; g.lineWidth = 12; g.shadowColor = 'rgba(255,0,0,.8)'; g.shadowBlur = 16; g.beginPath(); g.moveTo(80, FLOOR + 4); g.lineTo(365, FLOOR + 4); g.stroke(); g.restore(); }
  if (o.neck) { // dashed red circle (+X) on fake's neck
    const f = o.fake, nx = f.x, ny = f.y - 845 * f.s, a = eo(o.neck(lt, p)), r = 78 * f.s;
    g.save(); g.setLineDash([16 * f.s, 10 * f.s]); g.strokeStyle = P.red; g.lineWidth = 7 * f.s; g.beginPath(); g.arc(nx, ny, r * (1.4 - .4 * a), 0, 7 * a); g.stroke(); g.restore();
    if (o.cross) { const c = eo(o.cross(lt, p)); if (c > 0) { line([nx - r * .6, ny - r * .6, nx - r * .6 + r * 1.2 * c, ny - r * .6 + r * 1.2 * c], 9 * f.s, P.red); if (c > .5) line([nx + r * .6, ny - r * .6, nx + r * .6 - r * 1.2 * (c - .5) * 2, ny - r * .6 + r * 1.2 * (c - .5) * 2], 9 * f.s, P.red); } }
  }
};
SC.underBed = (lt, p, o, t) => {
  g.fillStyle = '#05090b'; g.fillRect(-400, -400, W + 800, H + 800);
  // floor beyond
  let gr = g.createLinearGradient(0, 900, 0, 1920); gr.addColorStop(0, '#0b1619'); gr.addColorStop(1, '#040809'); g.fillStyle = gr; g.fillRect(-400, 980, W + 800, 1400);
  g.save(); g.setLineDash([22, 16]); g.strokeStyle = 'rgba(44,83,96,.5)'; g.lineWidth = 6; g.beginPath(); g.ellipse(560, 1500, 700, 240, 0, Math.PI, 2 * Math.PI); g.stroke(); g.restore();
  // bed underside zone
  g.fillStyle = '#020405'; g.fillRect(-400, 560, W + 800, 430);
  const dk = o.dark?.(lt, p) ?? 0;
  if (o.buddy) { const b = o.buddy; drawBuddy(b.x?.(lt, p) ?? b.xV ?? 560, b.y ?? 960, b.s ?? 1.0, { t, lying: b.lying ?? 1, tremble: b.tremble, tear: b.tear, dir: 1, glint: b.glint?.(lt, p) ?? 0, wag: b.wag }); }
  if (dk > 0) { g.fillStyle = `rgba(2,4,5,${dk})`; g.fillRect(-400, 560, W + 800, 430); }
  if (o.eyes) { const a = o.eyes(lt, p); circ(745, 805, 7, `rgba(255,255,255,${a})`); circ(775, 800, 7, `rgba(255,255,255,${a})`); }
  if (o.glintOnly) { const a = o.glintOnly(lt, p); star4(680, 905, 80 * a, '#fff3c0', a); }
  // blanket overhang
  rr(-120, 220, 1300, 360, 60); g.fillStyle = P.blanket; g.fill();
  g.save(); g.clip(); g.strokeStyle = P.blanketHi; g.lineWidth = 9; for (let k = -2; k < 14; k++) { g.beginPath(); g.moveTo(k * 95, 220); g.lineTo(k * 95 - 40, 600); g.stroke(); } g.restore();
  rr(-60, 130, 340, 130, 50); g.fillStyle = P.pillow; g.fill();
  g.fillStyle = 'rgba(0,0,0,.35)'; g.fillRect(-400, 545, W + 800, 30);
};
SC.legs = (lt, p, o, t) => {
  drawRoom({ t });
  drawFake(560, 1680, 1.25, { t });
  g.fillStyle = '#020405'; g.fillRect(-400, -400, W + 800, 900); // under-bed frame top
  rr(-120, 320, 1300, 220, 60); g.fillStyle = P.blanket; g.fill();
};
SC.card = (lt, p, o, t) => {
  g.fillStyle = '#07080a'; g.fillRect(-400, -400, W + 800, H + 800);
  const gr = g.createRadialGradient(540, 960, 50, 540, 960, 700); gr.addColorStop(0, 'rgba(40,60,70,.25)'); gr.addColorStop(1, 'rgba(0,0,0,0)'); g.fillStyle = gr; g.fillRect(0, 0, W, H);
  g.textAlign = 'center'; g.textBaseline = 'middle';
  o.lines.forEach((ln, i) => {
    const show = ln.at == null ? 1 : clamp((t - A(ln.at)) / 0.08); if (show <= 0) return;
    g.save(); g.translate(540, ln.y); const sc = 1 + .25 * (1 - eo(show)); g.scale(sc, sc);
    g.font = `900 ${ln.size}px Inter`; g.fillStyle = ln.col; g.shadowColor = ln.col === P.red ? 'rgba(255,0,0,.55)' : 'rgba(255,255,255,.25)'; g.shadowBlur = 30;
    g.fillText(ln.txt, 0, 0); g.restore();
  });
};
SC.end = (lt, p, o, t) => {
  drawRoom({ t, door: 1 });
  g.save(); g.filter = 'brightness(0)'; g.globalAlpha = .9;
  drawMom(215, FLOOR + 2, .95, { hand: 1 }); drawKid(760, 1660, 1, { t }); drawBuddy(620, 1720, .55, { t, dir: -1, growl: 1 });
  g.restore();
  g.fillStyle = 'rgba(3,5,7,.72)'; g.fillRect(-400, -400, W + 800, H + 800);
  drawBuddy(470, 640, .42, { t, dir: 1, lying: 1, tremble: 1 });
  g.textAlign = 'center'; g.textBaseline = 'middle';
  g.font = '600 30px "JetBrains Mono"'; g.fillStyle = 'rgba(220,220,220,.7)'; g.fillText('E L   P E R R O   ·   F I N', 540, 830);
  const l = L['28'];
  const a1 = clamp((t - l.chunks[0].t0) / .1), a2 = clamp((t - l.chunks[1].t0) / .1);
  g.save(); g.font = '900 86px Inter'; g.fillStyle = P.red; g.shadowColor = 'rgba(255,0,0,.6)'; g.shadowBlur = 34;
  if (a1 > 0) { g.globalAlpha = a1; g.fillText('¿LO DICES...', 540, 950); }
  if (a2 > 0) { g.globalAlpha = a2; g.fillText('...O CONFÍAS', 540, 1060); g.fillText('EN EL PERRO?', 540, 1160); }
  g.restore();
};

// ---------- shot list ----------
const R = (o) => ({ ...o });
const fk = (s = .95, x = 540, y = 1660) => ({ x, y, s });
const S = [];
function shot(at, sc, o, cam, hud, fx = {}) { S.push({ at, sc, o, cam, hud, fx }); }
const H35 = ['3:35', 'TU HABITACIÓN'], HB = ['3:35', 'BAJO TU CAMA'], H36 = ['3:36', 'TU HABITACIÓN'], H33 = ['3:33', 'HACE 3 NOCHES'], H37 = ['3:37', 'TU HABITACIÓN'], H38 = ['3:38', 'TU HABITACIÓN'], H39 = ['3:39', 'TU HABITACIÓN'];
const FAKEHEAD = 1660 - 965 * .95;
// 1 — hook
shot('1:0-0.35', 'room', { fake: fk() }, [540, FAKEHEAD + 120, 2.5, 540, FAKEHEAD + 90, 2.75], H35, { punch: 1 });
shot('1:1', 'room', { fake: fk() }, [520, 1050, 1.25, 540, 900, 1.12], H35, { punch: 1 });
shot('1:1+0.62', 'room', { kid: { x: 760, tremble: 1 } }, [800, 1250, 1.9, 790, 1230, 2.0], H35);
// 2 — hiding
shot('2:0', 'underBed', { dark: () => 1, eyes: (lt) => clamp(lt * 3), glintOnly: (lt) => .6 + .4 * Math.sin(lt * 12) }, [560, 860, 1.25, 600, 860, 1.35], HB);
shot('2:1+0.25', 'underBed', { buddy: { xV: 430, tremble: 1, tear: 1 }, dark: (lt) => clamp(.6 - lt) }, [540, 840, 1.2, 560, 850, 1.3], HB);
shot('3:0', 'underBed', { buddy: { xV: 430, tremble: 1, tear: 1 } }, [640, 820, 2.0, 650, 830, 2.15], HB);
shot('4:0', 'underBed', { buddy: { xV: 430, tremble: 1, tear: 1, glint: (lt) => eo(lt * 4) * (0.8 + .2 * Math.sin(lt * 20)) } }, [600, 860, 2.6, 610, 870, 2.8], HB, { punch: 1 });
shot('5:0', 'underBed', { buddy: { xV: 430, tremble: 1, tear: 1 } }, [660, 800, 2.4, 660, 790, 2.55], HB);
shot('5:1', 'legs', {}, [560, 1350, 1.2, 560, 1320, 1.3], HB);
// 6 — the thing
shot('6:0', 'room', { fake: fk(), kid: { x: 820, s: .9 } }, [540, 1400, 1.5, 540, 1050, 1.4], H35);
shot('6:2', 'room', { fake: fk(), kid: { x: 820, s: .9 } }, [540, 980, 1.25, 540, 940, 1.3], H35);
shot('6:3', 'room', { fake: fk() }, [540, FAKEHEAD + 170, 2.2, 540, FAKEHEAD + 150, 2.35], H35);
shot('6:5', 'room', { fake: fk(), neck: (lt) => lt * 4, cross: (lt) => (lt - .45) * 3.5 }, [540, FAKEHEAD + 150, 2.6, 540, FAKEHEAD + 140, 2.75], H35, { punch: 1 });
// 7 — shadow
shot('7:0', 'room', { fake: fk(.85, 500, 1640), shadow: .6, kid: { x: 800, tremble: 1 } }, [560, 1040, 1.12, 560, 1000, 1.02], H35);
// 8 — mom at the door
shot('8:0', 'room', { door: (lt) => eo(lt * 1.5), kid: { x: 800, alpha: 0 } }, [260, 980, 1.7, 240, 960, 1.8], H36);
shot('8:1', 'room', { doorV: 1, mom: { alpha: (lt) => eo(lt * 3), handV: 0 } }, [250, 960, 1.9, 250, 950, 2.0], H36);
shot('8:2', 'room', { doorV: 1, mom: { hand: (lt) => eo(lt * 2.5) } }, [300, 900, 1.9, 320, 890, 2.05], H36);
shot('9:0', 'room', { doorV: 1, mom: { handV: 1 } }, [300, 820, 2.4, 300, 800, 2.6], H36);
shot('9:1', 'room', { doorV: 1, fake: fk(1.0, 640, 1700) }, [640, 1700 - 965 + 120, 2.2, 640, 1700 - 965 + 110, 2.4], H36);
shot('9:echo', 'card', { lines: [{ txt: 'LO DEJARON', y: 900, size: 104, col: '#f2efe6' }, { txt: 'ENTRAR.', y: 1020, size: 104, col: '#f2efe6' }] }, [540, 960, 1, 540, 960, 1.08], null, { glitch: 1 });
// 10–12 — flashback (sepia)
const SEP = { tint: 'sepia' };
shot('10:0', 'room', { kid: { x: 700 } }, [480, 1100, 1.25, 470, 1080, 1.3], H33, SEP);
shot('10:2', 'room', { scratch: (lt) => lt * 1.6 }, [220, 1000, 2.4, 220, 990, 2.5], H33, SEP);
shot('10:3+0.3', 'room', { scratch: () => 1, kid: { x: 620 } }, [400, 1150, 1.5, 400, 1130, 1.55], H33, SEP);
shot('11:0', 'room', { kid: { x: 520, arm: (lt) => lt > .25 ? 'reach' : 'down' }, darkDoor: 1, door: (lt) => eo((lt - .3) * 1.6), eyes: (lt) => clamp((lt - .8) * 2) }, [360, 1100, 1.5, 340, 1080, 1.6], H33, SEP);
shot('12:0', 'room', { kid: { x: 520, armV: 'reach' }, darkDoor: 1, doorV: 1, eyes: () => 1 }, [330, 1020, 1.7, 320, 1000, 1.85], H33, SEP);
// 13 — card
shot('13:start-0.05', 'card', { lines: [{ txt: 'TÚ', y: 880, size: 140, col: '#f2efe6', at: '13:start' }, { txt: 'LO DEJASTE', y: 1020, size: 112, col: P.red, at: '13:start+0.28' }, { txt: 'ENTRAR.', y: 1140, size: 112, col: P.red, at: '13:start+0.28' }] }, [540, 960, 1, 540, 960, 1.06], null, { shake: 1, flash: .5 });
// 14–15 — confrontation
shot('14:0', 'room', { fake: fk() }, [540, FAKEHEAD - 20, 3.2, 540, FAKEHEAD - 25, 3.6], H37);
shot('15:start', 'room', { fake: fk(.85, 470, 1640), kid: { x: 800, arm: (lt) => lt > .5 ? 'point' : 'down' }, fake2: 1 }, [620, 1150, 1.3, 620, 1140, 1.36], H37);
S[S.length - 1].o.fake.teeth = (lt) => clamp((lt - 1.2) * 3);
// 16 — smile cracks
shot('16:0', 'room', { fake: { ...fk(), teethV: 1 } }, [540, FAKEHEAD + 150, 2.5, 540, FAKEHEAD + 140, 2.7], H37, { flash: 1, punch: 1, glitch: .5 });
shot('16:1', 'room', { fake: { ...fk(), teethV: 1, cracks: (lt) => eo(lt * 1.5) } }, [540, FAKEHEAD + 100, 2.6, 540, FAKEHEAD + 100, 2.85], H37, { shake: .6 });
// 17 — melt
shot('17:0', 'room', { doorV: 1, mom: { handV: .75, smile: 1 }, fake: { ...fk(.8, 470, 1640), teethV: 1, cracksV: 1, melt: (lt) => clamp((lt - .6) / 2.1) }, drain: (lt) => clamp((lt - 2) * 1.5) }, [420, 1150, 1.35, 430, 1250, 1.45], H37, { tint: 'red' });
// 18 — empty room
shot('18:0', 'room', { doorV: 1, mom: { handV: 1, smile: 1 }, kid: { x: 780 } }, [540, 1060, 1.05, 540, 1040, 1.0], H37);
// 19–20 — Buddy comes out
shot('19:0', 'underBed', { buddy: { x: (lt) => lerp(380, 560, eo(lt / 1.4)), lying: 1 } }, [560, 900, 1.25, 600, 900, 1.3], H38);
shot('19:1', 'underBed', { buddy: { x: (lt) => lerp(560, 640, eo(lt)), lying: 0, y: 1150 } }, [620, 980, 1.3, 640, 990, 1.35], H38);
shot('20:0', 'underBed', { buddy: { xV: 500, lying: 0, y: 1150, glint: (lt) => eo(lt * 5) } }, [700, 980, 2.5, 700, 990, 2.65], H38, { punch: 1 });
shot('20:1', 'underBed', { buddy: { xV: 500, lying: 0, y: 1150, wag: 1, glint: (lt) => .4 + .6 * Math.abs(Math.sin(lt * 9)) } }, [680, 960, 2.2, 690, 960, 2.3], H38, { shake: .25 });
shot('20:2', 'underBed', { buddy: { xV: 500, lying: 0, y: 1150, wag: 1 } }, [640, 1000, 1.7, 650, 1000, 1.75], H38);
// 21 — "good job"
shot('21:start-0.1', 'room', { doorV: 1, mom: { handV: 1, smile: 1 } }, [300, 860, 2.2, 300, 840, 2.35], H38);
// 22
shot('22:0', 'room', { doorV: 1, mom: { handV: 1, smile: 1 }, kid: { x: 800 }, buddy: { xV: 650 } }, [540, 1150, 1.05, 540, 1130, 1.1], H38);
shot('22:2', 'room', { doorV: 1, mom: { handV: 1, smile: 1 } }, [480, 800, 2.6, 500, 800, 2.8], H38);
shot('22:3', 'room', { doorV: 1, mom: { handV: 1, smile: 1 } }, [230, 640, 3.6, 230, 640, 3.9], H38, { punch: 1 });
// 23 — threshold
shot('23:0', 'room', { doorV: 1, mom: { handV: 1, smile: 1 }, redLine: (lt) => clamp(lt * 3) * (.75 + .25 * Math.sin(lt * 10)) }, [225, 1180, 2.2, 225, 1200, 2.35], H38);
shot('23:2', 'room', { doorV: 1, mom: { handV: 1, smile: 1 }, redLine: (lt) => .75 + .25 * Math.sin(lt * 10) }, [225, 1280, 3.0, 225, 1290, 3.2], H38);
// 24 — calendar
shot('24:0', 'room', { doorV: 1, mom: { handV: 1, smile: 1 }, kid: { x: 800, alpha: 0 } }, [290, 900, 1.8, 290, 890, 1.9], H38, { calendar: 1 });
// 25
shot('25:0', 'underBed', { buddy: { xV: 500, lying: 0, y: 1150 } }, [620, 1000, 1.6, 630, 1000, 1.65], H39);
// 26
shot('26:0', 'room', { doorV: 1, mom: { handV: 1, smile: 1 }, kid: { x: 820 }, buddy: { x: (lt) => lerp(760, 610, eo(lt / 1.2)) } }, [680, 1280, 1.6, 660, 1280, 1.65], H39);
shot('26:2', 'underBed', { buddy: { xV: 500, lying: 0, y: 1150, growl: 1 } }, [680, 950, 2.1, 680, 950, 2.25], H39, { tint: 'red', shake: .5, punch: 1 });
// 27 — mom close
shot('27:start-0.15', 'room', { doorV: 1, mom: { handV: 1, smile: 1 } }, [230, 680, 2.6, 230, 660, 3.2], null, { tint: 'pink' });
shot('27:1+0.9', 'room', { doorV: 1, mom: { handV: 1, smile: 1.2 } }, [230, 640, 4.2, 230, 640, 4.6], H39, { tint: 'pink', flash: .7, punch: 1 });
// 28 — ending
shot('28:start-0.25', 'end', {}, [540, 960, 1.0, 540, 960, 1.04], null, {});
S.forEach(s => s.t0 = s.at === 0 ? 0 : A(s.at)); S[0].t0 = 0;
for (let i = 0; i < S.length; i++) S[i].t1 = i + 1 < S.length ? S[i + 1].t0 : TL.total + 5;

// ---------- overlays ----------
let grain = []; for (let k = 0; k < 6; k++) { const c = off(360, 640), x = c.getContext('2d'), d = x.createImageData(360, 640); for (let i = 0; i < d.data.length; i += 4) { const v = Math.random() * 255; d.data[i] = d.data[i + 1] = d.data[i + 2] = v; d.data[i + 3] = 255; } x.putImageData(d, 0, 0); grain.push(c); }

function hud(h, t) {
  if (!h) return;
  const fl = rnd(Math.floor(t * 12)) < .04 ? .4 : 1;
  g.save(); g.globalAlpha = fl; g.textBaseline = 'alphabetic'; g.textAlign = 'left';
  g.font = '700 22px "JetBrains Mono"'; g.fillStyle = '#ff4a4a'; g.fillText('●  E L   P E R R O', 72, 232);
  g.font = '800 84px "JetBrains Mono"'; g.shadowColor = 'rgba(255,40,40,.55)'; g.shadowBlur = 18; g.fillText(h[0], 66, 318);
  const w = g.measureText(h[0]).width; g.font = '800 24px "JetBrains Mono"'; g.fillText('AM', 74 + w, 318);
  g.shadowBlur = 0; g.fillStyle = 'rgba(255,74,74,.55)'; g.fillRect(70, 334, w + 40, 3);
  g.font = '600 20px "JetBrains Mono"'; g.fillStyle = 'rgba(210,210,210,.75)'; g.fillText(h[1].split('').join(' '), 72, 368);
  g.restore();
}

function wrapWords(words, maxW) {
  const rows = [[]]; let w = 0; const sp = g.measureText(' ').width;
  words.forEach(o => { const ww = g.measureText(o.w).width; if (w + ww > maxW && rows[rows.length - 1].length) { rows.push([]); w = 0; } rows[rows.length - 1].push({ ...o, ww }); w += ww + sp; });
  return rows;
}
function caption(t, capY) {
  // narrator chunk captions
  for (let i = 0; i < TL.lines.length; i++) {
    const l = TL.lines[i]; if (l.who !== 'N' || l.id === 13 || l.id === 28 || l.id === 21.5) continue;
    const nxt = TL.lines[i + 1];
    for (let c = 0; c < l.chunks.length; c++) {
      const ch = l.chunks[c], t0 = ch.t0 - .04;
      const t1 = c + 1 < l.chunks.length ? l.chunks[c + 1].t0 - .04 : Math.min(l.t1 + .35, nxt ? nxt.t0 - .06 : 1e9);
      if (t < t0 || t >= t1) continue;
      const words = ch.text.split(/\s+/).map(w => ({ w: w.replace(/\*/g, '').toUpperCase(), hi: /\*/.test(w) }));
      g.save(); g.font = '900 70px Inter'; g.textBaseline = 'middle';
      const rows = wrapWords(words, 900), sp = g.measureText(' ').width, pop = 1 + .14 * (1 - eo((t - t0) / .09));
      g.translate(540, capY); g.scale(pop, pop);
      rows.forEach((r, ri) => {
        const tw = r.reduce((a, o) => a + o.ww, 0) + sp * (r.length - 1); let x = -tw / 2; const y = (ri - (rows.length - 1) / 2) * 84;
        r.forEach(o => {
          g.lineWidth = 12; g.strokeStyle = 'rgba(0,0,0,.85)'; g.lineJoin = 'round'; g.strokeText(o.w, x, y);
          g.shadowColor = 'rgba(0,0,0,.6)'; g.shadowBlur = 16; g.fillStyle = o.hi ? P.hi : '#fff'; g.fillText(o.w, x, y); g.shadowBlur = 0; x += o.ww + sp;
        });
      });
      g.restore();
    }
  }
  // quotes (MOM / KID)
  const groups = [];
  TL.lines.forEach((l, i) => { if (l.who === 'N') return; if (l.join && groups.length) groups[groups.length - 1].push(l); else groups.push([l]); });
  groups.forEach(gr => {
    const first = gr[0], last = gr[gr.length - 1];
    const idx = TL.lines.indexOf(last), nxt = TL.lines[idx + 1];
    let end = last.t1 + .6; if (last.echo) end = last.echo.t0; if (nxt && nxt.who === 'N' && nxt.id !== 21.5) end = Math.min(end, nxt.t0 - .05);
    if (t < first.t0 - .05 || t > end) return;
    const words = []; gr.forEach(l => l.words.forEach(w => words.push(w)));
    const txt = gr.map(l => l.chunks.map(c => c.text).join(' ')).join(' ').replace(/\*/g, '');
    const toks = txt.split(/\s+/); let wi = 0;
    const vis = toks.map(tok => { const has = /[\wáéíóúñü]/i.test(tok); const w = has ? words[Math.min(wi++, words.length - 1)] : null; return { w: tok, a: w ? clamp((t - w.t0 + .06) / .12) : 1 }; });
    vis[0].w = '“' + vis[0].w; vis[vis.length - 1].w += '”';
    g.save(); g.font = 'italic 800 52px Inter'; g.textBaseline = 'middle';
    const rows = wrapWords(vis, 880), sp = g.measureText(' ').width;
    const y0 = 470 - (rows.length - 1) * 33;
    g.font = '700 22px "JetBrains Mono"'; g.fillStyle = 'rgba(235,164,70,.9)'; g.textAlign = 'center'; g.fillText(`—  ${first.label}  —`, 540, y0 - 64);
    g.font = 'italic 800 52px Inter'; g.textAlign = 'left';
    rows.forEach((r, ri) => {
      const tw = r.reduce((a, o) => a + o.ww, 0) + sp * (r.length - 1); let x = 540 - tw / 2; const y = y0 + ri * 66;
      r.forEach(o => { g.globalAlpha = o.a; g.shadowColor = 'rgba(0,0,0,.9)'; g.shadowBlur = 14; g.fillStyle = '#fff'; g.fillText(o.w, x, y + (1 - o.a) * 8); x += o.ww + sp; });
    });
    g.restore();
  });
}

function calendar(lt, t) {
  const l = L['24'], d = ['LUN', 'MAR', 'MIÉ', 'JUE', 'VIE', 'SÁB', 'DOM'];
  g.save(); g.globalAlpha = clamp(lt * 5); rr(120, 560, 840, 150, 18); g.fillStyle = 'rgba(8,14,16,.82)'; g.fill(); g.strokeStyle = 'rgba(255,255,255,.12)'; g.lineWidth = 2; g.stroke();
  g.textAlign = 'center'; g.font = '700 24px "JetBrains Mono"';
  const dur = l.t1 - l.t0;
  d.forEach((dd, i) => {
    const x = 180 + i * 120; g.fillStyle = 'rgba(220,220,220,.8)'; g.fillText(dd, x, 600);
    const a = clamp((t - l.t0 - i * dur / 7.5) / .1);
    if (a > 0) { const s = 22 * eo(a) + 8 * (1 - eo(a)); line([x - s, 645 - s, x + s, 645 + s], 7, P.red); line([x + s, 645 - s, x - s, 645 + s], 7, P.red); }
  });
  g.restore();
}

// ---------- frame ----------
window.renderFrame = function (t) {
  g.setTransform(1, 0, 0, 1, 0, 0); g.globalAlpha = 1; g.filter = 'none'; g.globalCompositeOperation = 'source-over';
  g.fillStyle = '#000'; g.fillRect(0, 0, W, H);
  let si = S.findIndex(s => t >= s.t0 && t < s.t1); if (si < 0) si = S.length - 1;
  const s = S[si], lt = t - s.t0, p = clamp(lt / (s.t1 - s.t0)), fx = s.fx || {};
  const c = s.cam; let z = lerp(c[2], c[5], ease(p)), cx = lerp(c[0], c[3], ease(p)), cy = lerp(c[1], c[4], ease(p));
  if (fx.punch) z *= 1 + .07 * (1 - eo(lt / .22));
  let sx = 0, sy = 0; if (fx.shake) { const k = fx.shake * 14 * (fx.flash ? Math.max(.25, 1 - lt * 2) : 1); sx = (rnd(t * 91) - .5) * k * 2; sy = (rnd(t * 57 + 3) - .5) * k * 2; }
  g.save(); g.translate(W / 2 + sx, H / 2 + sy); g.scale(z, z); g.translate(-cx, -cy);
  SC[s.sc](lt, p, s.o, t);
  g.restore();
  // tints
  if (fx.tint) {
    g.save();
    if (fx.tint === 'sepia') { g.globalCompositeOperation = 'color'; g.fillStyle = '#7a5a36'; g.fillRect(0, 0, W, H); g.globalCompositeOperation = 'multiply'; g.fillStyle = '#9a8a78'; g.fillRect(0, 0, W, H); }
    if (fx.tint === 'red') { g.globalCompositeOperation = 'multiply'; g.fillStyle = '#c23a3a'; g.fillRect(0, 0, W, H); g.globalCompositeOperation = 'screen'; g.fillStyle = 'rgba(80,0,0,.25)'; g.fillRect(0, 0, W, H); }
    if (fx.tint === 'pink') { g.globalCompositeOperation = 'soft-light'; g.fillStyle = 'rgba(255,90,150,.55)'; g.fillRect(0, 0, W, H); g.globalCompositeOperation = 'multiply'; g.fillStyle = '#e8b0c0'; g.fillRect(0, 0, W, H); }
    g.restore();
  }
  if (fx.calendar) calendar(lt, t);
  // vignette
  const vg = g.createRadialGradient(540, 960, 380, 540, 960, 1250); vg.addColorStop(0, 'rgba(0,0,0,0)'); vg.addColorStop(1, 'rgba(0,0,0,.72)'); g.fillStyle = vg; g.fillRect(0, 0, W, H);
  hud(s.hud, t);
  const capY = 1190;
  caption(t, capY);
  // flash
  if (fx.flash) { const a = fx.flash * (1 - eo(lt / .35)); if (a > 0) { g.fillStyle = `rgba(255,255,255,${a})`; g.fillRect(0, 0, W, H); } }
  // cut flash on every shot (tiny) for rhythm
  if (lt < 0.05 && si > 0) { g.fillStyle = 'rgba(255,255,255,.06)'; g.fillRect(0, 0, W, H); }
  // glitch
  const gl = (fx.glitch || 0) * (lt < .35 ? 1 : (rnd(Math.floor(t * 15)) < .12 ? .6 : 0));
  if (gl > 0) {
    const snap = off(); snap.getContext('2d').drawImage(cv, 0, 0);
    for (let k = 0; k < 7; k++) { const y = rnd(t * 13 + k) * H, h = 20 + rnd(t * 7 + k) * 90, dx = (rnd(t * 29 + k) - .5) * 120 * gl; g.drawImage(snap, 0, y, W, h, dx, y, W, h); }
    g.save(); g.globalCompositeOperation = 'screen'; g.globalAlpha = .35 * gl; g.filter = 'sepia(1) saturate(8) hue-rotate(-50deg)'; g.drawImage(snap, 10 * gl, 0); g.restore();
  }
  // grain
  g.save(); g.globalAlpha = .055; g.globalCompositeOperation = 'overlay'; g.drawImage(grain[Math.floor(t * 24) % grain.length], 0, 0, W, H); g.restore();
  // fade in / out
  const fo = clamp((t - (TL.total - 0.8)) / .8); if (fo > 0) { g.fillStyle = `rgba(0,0,0,${fo})`; g.fillRect(0, 0, W, H); }
};
window.SHOTS = S.map(s => ({ at: s.at, sc: s.sc, t0: s.t0, fx: s.fx }));
window.ready = document.fonts.load('900 70px Inter').then(() => document.fonts.load('800 84px "JetBrains Mono"')).then(() => document.fonts.load('italic 800 52px Inter')).then(() => true);
