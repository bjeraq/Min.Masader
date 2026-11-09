const { chromium } = require('playwright');
const fs=require('fs');
(async()=>{
  const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium'});
  const p=await b.newPage({viewport:{width:1080,height:1920}});
  const errs=[]; p.on('pageerror',e=>errs.push(e.message)); p.on('console',m=>{if(m.type()==='error')errs.push('C:'+m.text())});
  await p.goto('file:///home/user/min.masader/site/excise-story.html?capture=1',{waitUntil:'load'});
  await p.waitForFunction(()=>window.__ready===true,null,{timeout:60000});
  fs.mkdirSync(process.argv[3],{recursive:true});
  const ts=JSON.parse(process.argv[2]);
  for(const t of ts){ await p.evaluate(x=>window.__renderOut(x),t); await p.waitForTimeout(50); await p.screenshot({path:`${process.argv[3]}/shot_${t}.jpg`,type:'jpeg',quality:80}); }
  console.log('errors',JSON.stringify(errs));
  await b.close();
})();
