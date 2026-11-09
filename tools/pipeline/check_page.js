const { chromium } = require('playwright');
(async()=>{
  const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium'});
  const p=await b.newPage({viewport:{width:420,height:900}});
  const errs=[]; p.on('pageerror',e=>errs.push(e.message)); p.on('console',m=>{if(m.type()==='error')errs.push('C:'+m.text())});
  await p.goto('file:///home/user/Advisers/site/excise-tax.html',{waitUntil:'load'});
  await p.fill('#cp','150'); await p.selectOption('#cr',{index:2});
  const out=await p.textContent('#co');
  const sw=await p.evaluate(()=>document.documentElement.scrollWidth);
  if(process.argv[2]) await p.screenshot({path:process.argv[2],fullPage:true,type:'jpeg',quality:70});
  console.log('calc 150 fils soda ->',out.trim(),'| scrollWidth',sw,'| errors',JSON.stringify(errs));
  await b.close();
})();
