const { chromium } = require('playwright');
const fs=require('fs');
(async()=>{
  const FPS=25, DUR=JSON.parse(fs.readFileSync(__dirname+'/story_cfg_v3.json','utf8')).total, N=Math.round(DUR*FPS);
  const dir=process.argv[2]; fs.rmSync(dir,{recursive:true,force:true}); fs.mkdirSync(dir,{recursive:true});
  const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium'});
  const p=await b.newPage({viewport:{width:1080,height:1920}});
  const errs=[]; p.on('pageerror',e=>errs.push(e.message));
  await p.goto('file:///home/user/min.masader/site/excise-story.html?capture=1',{waitUntil:'load'});
  await p.waitForFunction(()=>window.__ready===true,null,{timeout:60000});
  await p.waitForTimeout(500);
  for(let i=0;i<N;i++){
    await p.evaluate(x=>window.__renderOut(x), i/FPS);
    await p.screenshot({path:`${dir}/f${String(i).padStart(5,'0')}.jpg`,type:'jpeg',quality:90});
    if(i%250===0) console.log('frame',i,'of',N, new Date().toISOString());
  }
  console.log('DONE errors',JSON.stringify(errs));
  await b.close();
})();
