const { chromium } = require('playwright');
const fs=require('fs');
(async()=>{
  const SP='/tmp/claude-0/-home-user-min-masader/59b58237-73e8-5a26-8661-efeb42e64c46/scratchpad/rail';
  const FPS=25, DUR=JSON.parse(fs.readFileSync(SP+'/build/story_cfg_rail.json','utf8')).total, N=Math.round(DUR*FPS);
  const dir=process.argv[2], W=parseInt(process.argv[3]||'432'), H=Math.round(W*16/9);
  fs.rmSync(dir,{recursive:true,force:true}); fs.mkdirSync(dir,{recursive:true});
  const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium'});
  const p=await b.newPage({viewport:{width:W,height:H}});
  const errs=[]; p.on('pageerror',e=>errs.push(e.message));
  await p.goto('file:///home/user/min.masader/site/gcc-rail-story.html?capture=1',{waitUntil:'load'});
  await p.waitForFunction(()=>window.__ready===true,null,{timeout:60000});
  await p.waitForTimeout(400);
  for(let i=0;i<N;i++){
    await p.evaluate(x=>window.__renderOut(x), i/FPS);
    await p.screenshot({path:`${dir}/f${String(i).padStart(5,'0')}.jpg`,type:'jpeg',quality:85});
    if(i%250===0) console.log('frame',i,'of',N);
  }
  console.log('DONE errors',JSON.stringify(errs));
  await b.close();
})();
