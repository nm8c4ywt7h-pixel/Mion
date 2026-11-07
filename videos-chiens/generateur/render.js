const { chromium } = require('playwright');
const fs=require('fs');
(async()=>{
  const [lang,fps,only]=[process.argv[2]||'fr',+(process.argv[3]||30),process.argv[4]];
  const tl=JSON.parse(fs.readFileSync(`timeline_${lang}.json`));
  const b=await chromium.launch({args:['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist']});
  const p=await b.newPage({viewport:{width:1080,height:1920}});
  p.on('console',m=>console.log('PAGE',m.text())); p.on('pageerror',e=>console.log('ERR',e.message));
  await p.goto(`http://127.0.0.1:8765/scene.html?lang=${lang}`);
  await p.waitForFunction('window.ready===true',null,{timeout:60000});
  const dir=`frames_${lang}`;fs.mkdirSync(dir,{recursive:true});
  fs.writeFileSync(`events_${lang}.json`,JSON.stringify(await p.evaluate('window.events')));
  const times= only? only.split(',').map(Number) : [...Array(Math.round(tl.total*fps)).keys()].map(i=>i/fps);
  const t0=Date.now();
  for(let i=0;i<times.length;i++){
    await p.evaluate(t=>window.renderAt(t),times[i]);
    await p.screenshot({path:only?`test_${lang}_${times[i]}.jpg`:`${dir}/${String(i).padStart(4,'0')}.jpg`,type:'jpeg',quality:92});
    if(i%60===0)console.log(i,times.length,((Date.now()-t0)/1000).toFixed(1)+'s');
  }
  await b.close();
})();
