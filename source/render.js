const { chromium } = require('playwright');
const { spawn } = require('child_process');
const fs = require('fs');
(async () => {
  const [, , dir, mode, out, ...rest] = process.argv;
  const b = await chromium.launch(); const pg = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  pg.on('console', m => console.log('PAGE:', m.text())); pg.on('pageerror', e => console.log('ERR:', e.message));
  await pg.goto('file://' + dir + '/index.html'); await pg.evaluate(() => window.ready);
  if (mode === 'shots') { console.log(JSON.stringify(await pg.evaluate(() => window.SHOTS))); }
  if (mode === 'stills') {
    for (const t of rest) {
      const d = await pg.evaluate(t => { renderFrame(+t); return document.getElementById('c').toDataURL('image/jpeg', .85); }, t);
      fs.writeFileSync(`${out}/t_${(+t).toFixed(2).padStart(6, '0')}.jpg`, Buffer.from(d.split(',')[1], 'base64'));
    }
  }
  if (mode === 'video') {
    const total = await pg.evaluate(() => TL.total), fps = 30, n = Math.ceil(total * fps);
    const ff = spawn('ffmpeg', ['-y', '-v', 'error', '-f', 'image2pipe', '-framerate', '30', '-c:v', 'mjpeg', '-i', '-', '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p', out], { stdio: ['pipe', 'inherit', 'inherit'] });
    for (let i = 0; i < n; i++) {
      const d = await pg.evaluate(t => { renderFrame(t); return document.getElementById('c').toDataURL('image/jpeg', .94); }, i / fps);
      if (!ff.stdin.write(Buffer.from(d.split(',')[1], 'base64'))) await new Promise(r => ff.stdin.once('drain', r));
      if (i % 300 === 0) console.log('frame', i, '/', n);
    }
    ff.stdin.end(); await new Promise(r => ff.on('close', r));
  }
  await b.close();
})();
