// Render selected times of the story page to JPEGs for review: node shots_fires.js outdir t1 t2 ...
const { chromium } = require('playwright');
(async()=>{
  const [dir,...ts]=process.argv.slice(2); require('fs').mkdirSync(dir,{recursive:true});
  const b=await chromium.launch(); const p=await b.newPage({viewport:{width:540,height:960}});
  const errs=[]; p.on('pageerror',e=>errs.push(e.message)); p.on('console',m=>{ if(m.type()==='error') errs.push(m.text()); });
  await p.goto('file://'+require('path').resolve(__dirname,'../../../site/kuwait-oil-fires-story.html')+'?capture=1',{waitUntil:'load'});
  await p.waitForFunction(()=>window.__ready===true,null,{timeout:60000}); await p.waitForTimeout(300);
  for(const t of ts){ await p.evaluate(x=>window.__renderOut(x), +t); await p.screenshot({path:`${dir}/t${String(t).padStart(6,'0')}.jpg`,type:'jpeg',quality:80}); }
  console.log('errors',JSON.stringify(errs)); await b.close();
})();
