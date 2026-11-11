"""Derive story_template_fires.html from the rail template:
new texts, a Kuwait oil-fields map engine (fires igniting / going out, smoke drift, month ticker),
badge exit time, and new ART stickers (no brands, no faces)."""
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
src = (HERE.parent / 'rail' / 'story_template_rail.html').read_text(encoding='utf-8')


def rep(old, new, count=1):
    global src
    assert src.count(old) == count, (src.count(old), old[:90])
    src = src.replace(old, new, count)


# ---------- texts ----------
rep('<title>القطار الخليجي · فيديو | مِن مصادر</title>', '<title>35 عاماً على إطفاء آخر بئر · فيديو | مِن مصادر</title>')
rep('<div id="tag">اقتصاد · خليجي</div>', '<div id="tag">الكويت · ذكرى</div>')
rep('<div class="k" style="display:inline-block">خبر · خليجي</div><h1>القطار الخليجي</h1><h2>وُقّعت الاتفاقية.. والكويت نقطة الانطلاق</h2>',
    '<div class="k" style="display:inline-block">ذكرى · 1991–2026</div><h1>35 عاماً<br>على إطفاء آخر بئر</h1><h2>آبار الكويت المشتعلة: الأرقام بمصادرها</h2>')
rep('<div class="src">المصادر: كونا · الأنباء · الراي · Arab Times · الشرق الأوسط · الجريدة · السياسة<small>رسوم بالذكاء الاصطناعي · حدود الخريطة: Natural Earth · التفاصيل في مقال «مِن مصادر»</small></div>',
    '<div class="src">المصادر: كونا · الجريدة · الراي · MEES · Oil &amp; Gas Journal · وزارة الدفاع الأمريكية · ناسا · الأمم المتحدة · نفط الكويت<small>رسوم توضيحية بالذكاء الاصطناعي · مواقع الحرائق على الخريطة تمثيلية · التفاصيل والأرقام المختلفة في مقال «مِن مصادر»</small></div>')
rep('<div id="disc">رسوم توضيحية · خريطة تمثيلية</div>', '<div id="disc">رسوم توضيحية بالذكاء الاصطناعي</div>')
rep("e.className='chip'+(/لم |لا نعرف|قيد الدراسة|أمنية/.test(c.text)?' warn':'')",
    "e.className='chip'+(/لا نعرف|التقدير|متداول/.test(c.text)?' warn':'')")
# badge can leave before the scene ends (to free room for later chips)
rep("badge.style.opacity=clamp(k*2,0,1)*hout;",
    "badge.style.opacity=clamp(k*2,0,1)*hout*(s.badge.t_out?1-ease((t-s.badge.t_out)/0.35):1);")
rep('#badge{position:absolute;top:640px;', '#badge{position:absolute;top:700px;')
rep('<div id="badge"><span></span></div>', '<div id="badge"><span></span><div class="bl"></div></div>')
rep('#badge span{', '#badge .bl{margin-top:22px;display:inline-block;background:rgba(255,253,248,.95);color:#13232b;font-size:46px;font-weight:800;padding:12px 30px;border-radius:24px}\n#badge span{')
rep("if(s.badge) badge.firstChild.textContent=s.badge.text;",
    "if(s.badge){ badge.firstChild.textContent=s.badge.text; badge.lastChild.textContent=s.badge.label||''; badge.lastChild.style.display=s.badge.label?'inline-block':'none'; }")

# ---------- map engine (replace the rail one) ----------
a = src.index('  // ---- rail map engine')
b = src.index("  var head=document.getElementById('head')")
MAP = r"""  // ---- Kuwait oil-fields map engine: fires ignite / go out, smoke drift, month ticker ----
  var GM=null;
  (function(){
    var any=false; CFG.scenes.forEach(function(s){ if(s.gmap) any=true; }); if(!any||!CFG.geo) return;
    var G=CFG.geo, box=document.getElementById('gmap'), mv=box.querySelector('.mv');
    function P(ll){ return [(ll[0]-G.lon0)*G.cos*G.k, (G.lat1-ll[1])*G.k]; }
    var svg=el('svg',{width:G.w,height:G.h,viewBox:'0 0 '+G.w+' '+G.h}); mv.appendChild(svg);
    var zg=el('g',{},svg);
    G.land.forEach(function(d){ el('path',{d:d,fill:'#efe7d8',stroke:'#c9bfae','stroke-width':1.5,'vector-effect':'non-scaling-stroke'},zg); });
    var cs={}; Object.keys(G.gcc).forEach(function(c){ cs[c]=el('path',{d:G.gcc[c],fill:'#e4e1d8',stroke:'#13232b','stroke-width':2,'stroke-linejoin':'round','vector-effect':'non-scaling-stroke'},zg); });
    var ov=el('g',{},svg);               // screen-space overlay (constant-size glyphs)
    var smokeG=el('g',{},ov), fireG=el('g',{},ov);
    var defs=el('defs',{},svg), rg=el('radialGradient',{id:'fglow'},defs);
    el('stop',{offset:0,'stop-color':'#ffd23f','stop-opacity':.95},rg); el('stop',{offset:.45,'stop-color':'#ff7a1a','stop-opacity':.55},rg); el('stop',{offset:1,'stop-color':'#ff5a1a','stop-opacity':0},rg);
    GM={box:box,mv:mv,zg:zg,cs:cs,P:P,G:G,sc:{},divs:[],smokeG:smokeG,fireG:fireG};
    CFG.scenes.forEach(function(s){ if(!s.gmap) return; var m=s.gmap, st={labels:[],fires:[],puffs:[],tick:null};
      (m.labels||[]).forEach(function(L){ var e=document.createElement('div'); e.className='gl'+(L.cls?' '+L.cls:''); e.textContent=L.text;
        if(L.fs) e.style.fontSize=L.fs+'px'; if(L.bg){ e.style.background=L.bg; } if(L.fg){ e.style.color=L.fg; }
        e.style.opacity=0; mv.appendChild(e); st.labels.push({cfg:L,e:e}); GM.divs.push(e); });
      (m.fires||[]).forEach(function(f,k){ var g=el('g',{opacity:0},fireG);
        var glow=el('circle',{r:16,fill:'url(#fglow)'},g);
        var fl=el('path',{d:'M0,-15 C6,-8 8,-3 6,3 C5,7 2,8 0,8 C-2,8 -5,7 -6,3 C-8,-3 -6,-8 0,-15 Z',fill:'#ff7a1a',stroke:'#7a2e0b','stroke-width':1.2},g);
        var core=el('path',{d:'M0,-7 C3,-3 4,0 3,3 C2,5 1,6 0,6 C-1,6 -2,5 -3,3 C-4,0 -3,-3 0,-7 Z',fill:'#ffd23f'},g);
        var ash=el('circle',{r:3.2,fill:'#5b6b75',opacity:0},fireG);
        st.fires.push({g:g,fl:fl,glow:glow,core:core,ash:ash,f:f,ph:rnd(k+11)*6.28,sz:0.75+0.5*rnd(k+29)}); });
      if(m.smoke){ for(var i=0;i<m.smoke.n;i++){ st.puffs.push({e:el('circle',{fill:'#2b2f33',opacity:0},smokeG),o:rnd(i+3),pp:(rnd(i+17)-0.5)}); } }
      if(m.ticker){ var e2=document.createElement('div'); e2.className='gl tag'; e2.style.opacity=0; if(m.ticker.fs) e2.style.fontSize=m.ticker.fs+'px';
        if(m.ticker.bg) e2.style.background=m.ticker.bg; mv.appendChild(e2); st.tick=e2; GM.divs.push(e2); }
      GM.sc[s.n]=st; });
  })();
  function renderMap(t,i,hout){
    if(!GM) return; var s=CFG.scenes[i], m=s.gmap;
    GM.box.style.display=m?'block':'none'; if(!m) return;
    var G=GM.G, kin=(t-m.t_in)/0.5;
    GM.box.style.opacity=(clamp(kin*1.6,0,1)*hout).toFixed(3);
    GM.box.style.transform='translateY('+((1-ease(kin))*60).toFixed(1)+'px) scale('+(0.94+0.06*easeOutBack(clamp(kin,0,1))).toFixed(4)+')';
    var z=1, cx=G.w/2, cy=G.h/2;
    if(m.zoom){ var ze=m.zoom.t<=m.t_in?1:ease((t-m.zoom.t)/0.9); z=1+(m.zoom.z-1)*ze; var c=GM.P(m.zoom.ll); cx=c[0]-(1-ze)*(c[0]-G.w/2)/z; cy=c[1]-(1-ze)*(c[1]-G.h/2)/z; }
    GM.zg.setAttribute('transform','translate('+(G.w/2)+','+(G.h/2)+') scale('+z.toFixed(4)+') translate('+(-cx).toFixed(2)+','+(-cy).toFixed(2)+')');
    function scr(p){ return [(p[0]-cx)*z+G.w/2,(p[1]-cy)*z+G.h/2]; }
    GM.divs.forEach(function(e){ e.style.opacity=0; });
    Object.keys(GM.cs).forEach(function(c){ GM.cs[c].setAttribute('fill','#e4e1d8'); });
    if(m.kwfill!==undefined){ var kk=clamp((t-m.kwfill)/0.5,0,1); GM.cs.KWT.setAttribute('fill',mixc('#e4e1d8',m.kwcol||'#f3d9bf',kk)); }
    Object.keys(GM.sc).forEach(function(n){ var o=GM.sc[n]; var on=(+n===s.n);
      o.fires.forEach(function(F){ if(!on){ F.g.setAttribute('opacity',0); F.ash.setAttribute('opacity',0); } });
      o.puffs.forEach(function(p){ if(!on) p.e.setAttribute('opacity',0); }); });
    var ST=GM.sc[s.n]; if(!ST) return;
    ST.fires.forEach(function(F){ var f=F.f, sp=scr(GM.P([f[0],f[1]])), on=t-f[2], off=(f[3]!=null)?t-f[3]:-1;
      if(on<0){ F.g.setAttribute('opacity',0); F.ash.setAttribute('opacity',0); return; }
      var grow=easeOutBack(clamp(on/0.35,0,1)), out=off>0?1-ease(off/0.35):1;
      var fl=1+0.16*Math.sin(2*Math.PI*3.1*t+F.ph)+0.08*Math.sin(2*Math.PI*7.7*t+F.ph*2);
      var sc=F.sz*grow*out*(m.fsize||1);
      F.g.setAttribute('transform','translate('+sp[0].toFixed(1)+','+sp[1].toFixed(1)+') scale('+(sc*(2-fl)*0.5+sc*0.5).toFixed(3)+','+(sc*fl).toFixed(3)+')');
      F.g.setAttribute('opacity',(out*hout).toFixed(3));
      F.glow.setAttribute('r',(16+3*Math.sin(2*Math.PI*2.3*t+F.ph)).toFixed(1));
      F.ash.setAttribute('cx',sp[0].toFixed(1)); F.ash.setAttribute('cy',sp[1].toFixed(1));
      F.ash.setAttribute('opacity',off>0?(0.75*clamp(off/0.4,0,1)*hout).toFixed(3):0); });
    if(m.smoke){ var sm=m.smoke, so=scr(GM.P(sm.ll)), age=t-sm.t0, dx=sm.dir[0], dy=sm.dir[1];
      ST.puffs.forEach(function(p){ if(age<0){ p.e.setAttribute('opacity',0); return; }
        var ph=frac(age/sm.period+p.o), reach=clamp(age/sm.grow,0,1);
        var d=ph*sm.len*reach, x=so[0]+dx*d-dy*p.pp*sm.wid*ph, y=so[1]+dy*d+dx*p.pp*sm.wid*ph;
        p.e.setAttribute('cx',x.toFixed(1)); p.e.setAttribute('cy',y.toFixed(1)); p.e.setAttribute('r',(14+sm.r*ph).toFixed(1));
        p.e.setAttribute('opacity',((sm.op||0.32)*Math.min(1,ph*5)*(1-ph*0.7)*clamp(age/0.8,0,1)*hout).toFixed(3)); }); }
    if(ST.tick){ var tk=m.ticker, cur=null; tk.items.forEach(function(it){ if(t>=it[0]) cur=it; });
      if(cur){ if(ST.tick.textContent!==cur[1]) ST.tick.textContent=cur[1]; var sp2=scr(GM.P(tk.ll));
        ST.tick.style.left=sp2[0].toFixed(1)+'px'; ST.tick.style.top=(sp2[1]+(tk.dy||0)).toFixed(1)+'px';
        var pk=clamp((t-cur[0])/0.25,0,1); ST.tick.style.transform='translate(-50%,-50%) scale('+(0.9+0.1*easeOutBack(pk)).toFixed(3)+')';
        ST.tick.style.opacity=(0.97*hout).toFixed(3); } }
    ST.labels.forEach(function(Lb){ var c=Lb.cfg, o=clamp((t-c.t)/0.35,0,1)*(c.t_out?1-clamp((t-c.t_out)/0.3,0,1):1); if(o<=0){ Lb.e.style.opacity=0; return; }
      var sp=scr(GM.P(c.ll)); Lb.e.style.left=sp[0].toFixed(1)+'px'; Lb.e.style.top=(sp[1]+(c.dy||0)).toFixed(1)+'px';
      Lb.e.style.transform='translate(-50%,-50%) scale('+(0.7+0.3*easeOutBack(clamp((t-c.t)/0.35,0,1))).toFixed(3)+')';
      Lb.e.style.opacity=(o*0.97*hout).toFixed(3); });
  }
"""
src = src[:a] + MAP + src[b:]

# ---------- new ART stickers ----------
rep("    gears:function(){",
    """    flame:function(){ return '<ellipse cx="100" cy="182" rx="70" ry="9" fill="#13232b" opacity=".18"/>'+
      '<path d="M100,20 C132,58 150,86 146,124 C143,158 124,178 100,178 C76,178 57,158 54,124 C51,94 68,74 80,56 C84,78 92,88 100,92 C96,66 96,44 100,20 Z" fill="#ff7a1a" stroke="#13232b" stroke-width="4"/>'+
      '<path d="M100,84 C118,104 126,122 122,142 C119,160 110,168 100,168 C90,168 81,160 78,142 C75,124 86,108 100,84 Z" fill="#ffd23f"/>'; },
    hourglass:function(){ return '<rect x="50" y="22" width="100" height="14" rx="6" fill="#0f6b6b" stroke="#13232b" stroke-width="3"/><rect x="50" y="164" width="100" height="14" rx="6" fill="#0f6b6b" stroke="#13232b" stroke-width="3"/>'+
      '<path d="M62,36 L138,36 C138,70 108,88 104,100 C108,112 138,130 138,164 L62,164 C62,130 92,112 96,100 C92,88 62,70 62,36 Z" fill="#fffdf8" stroke="#13232b" stroke-width="3"/>'+
      '<path d="M76,56 L124,56 C118,72 104,84 100,92 C96,84 82,72 76,56 Z" fill="#d9a54a"/><path d="M70,160 L130,160 C126,138 108,128 100,124 C92,128 74,138 70,160 Z" fill="#d9a54a"/>'; },
    helmet:function(){ return '<ellipse cx="100" cy="180" rx="72" ry="9" fill="#13232b" opacity=".16"/>'+
      '<path d="M40,132 C40,78 66,48 100,48 C134,48 160,78 160,132 Z" fill="#c9d2d6" stroke="#13232b" stroke-width="4"/>'+
      '<path d="M92,48 L108,48 L112,132 L88,132 Z" fill="#e0703f" stroke="#13232b" stroke-width="3"/>'+
      '<rect x="22" y="128" width="156" height="20" rx="10" fill="#9aa5ab" stroke="#13232b" stroke-width="4"/>'+
      '<path d="M50,148 L150,148 L144,176 L56,176 Z" fill="#dfe6e9" stroke="#13232b" stroke-width="3"/>'; },
    globe:function(){ return '<circle cx="100" cy="100" r="74" fill="#bfe3e6" stroke="#13232b" stroke-width="4"/>'+
      '<path d="M60,58 C78,66 74,84 90,88 C104,92 98,112 84,118 C70,124 66,140 56,132 C38,116 40,76 60,58 Z" fill="#7fb069"/>'+
      '<path d="M122,40 C140,48 156,64 162,86 C150,96 136,90 126,100 C116,110 124,128 140,134 C130,152 118,164 104,170 C108,150 98,140 108,124 C116,112 104,96 112,84 C120,72 110,56 122,40 Z" fill="#7fb069"/>'+
      '<ellipse cx="100" cy="100" rx="74" ry="28" fill="none" stroke="#13232b" stroke-width="2" opacity=".35"/><line x1="100" y1="26" x2="100" y2="174" stroke="#13232b" stroke-width="2" opacity=".35"/>'; },
    oillake:function(){ return '<ellipse cx="100" cy="120" rx="88" ry="46" fill="#e9dcc0"/>'+
      '<path d="M30,118 C34,92 74,84 104,88 C140,92 172,100 170,124 C168,148 130,158 98,156 C62,154 26,144 30,118 Z" fill="#1c2530" stroke="#13232b" stroke-width="4"/>'+
      '<path d="M60,108 C80,100 104,100 122,104" fill="none" stroke="#5cc4c4" stroke-width="5" stroke-linecap="round" opacity=".55"/>'+
      '<path d="M128,62 C130,72 142,74 140,86 C138,94 126,94 124,86 C122,78 126,72 128,62 Z" fill="#1c2530" stroke="#13232b" stroke-width="3"/>'; },
    soil:function(){ return '<ellipse cx="100" cy="176" rx="84" ry="10" fill="#13232b" opacity=".16"/>'+
      '<path d="M18,172 C30,120 58,82 96,70 C136,60 170,108 184,172 Z" fill="#5a4636" stroke="#13232b" stroke-width="4"/>'+
      '<circle cx="70" cy="132" r="8" fill="#3b2d23"/><circle cx="118" cy="110" r="10" fill="#3b2d23"/><circle cx="140" cy="148" r="7" fill="#3b2d23"/><circle cx="92" cy="156" r="6" fill="#3b2d23"/>'+
      '<path d="M96,70 C100,54 112,46 124,46" fill="none" stroke="#1c2530" stroke-width="7" stroke-linecap="round"/>'; },
    dollar:function(){ return '<circle cx="100" cy="100" r="76" fill="#7ccfb0" stroke="#2d6a4f" stroke-width="6"/><circle cx="100" cy="100" r="60" fill="none" stroke="#2d6a4f" stroke-width="3" opacity=".5"/>'+
      '<text x="100" y="132" text-anchor="middle" font-family="Tajawal" font-weight="900" font-size="96" fill="#1b4332">$</text>'; },
    gears:function(){""")


# ---------- draft 2: credit line per scene, generic counter, person cards, new sources ----------
rep('#disc{position:absolute;bottom:52px;left:0;right:0;text-align:center;z-index:20;color:rgba(255,255,255,.75);font-size:28px;font-weight:600}',
    '#disc{position:absolute;bottom:46px;left:40px;right:40px;text-align:center;z-index:20;color:rgba(255,255,255,.85);font-size:26px;font-weight:700;text-shadow:0 2px 8px rgba(0,0,0,.7)}\n'
    '#person{position:absolute;left:60px;right:60px;top:560px;z-index:21;opacity:0}\n'
    '#person .pc{background:rgba(255,253,248,.97);border-radius:40px;padding:40px 44px 44px;box-shadow:0 22px 60px rgba(0,0,0,.4);border-right:16px solid #e0703f;display:flex;gap:34px;align-items:center}\n'
    '#person .av{flex:none;width:170px;height:170px;border-radius:50%;background:#13232b;display:flex;align-items:center;justify-content:center}\n'
    '#person .nm{font-size:66px;font-weight:900;color:#13232b;line-height:1.15}\n'
    '#person .rl{font-size:38px;font-weight:800;color:#0f6b6b;margin-top:8px}\n'
    '#person .ft{font-size:36px;font-weight:700;color:#3b4a52;margin-top:14px;line-height:1.4}')
rep('<div id="sub"></div>', '<div id="sub"></div>\n  <div id="person"><div class="pc"><div class="av"><svg viewBox="0 0 200 200" width="130" height="130"><circle cx="100" cy="72" r="38" fill="#5cc4c4"/><path d="M28,186 C34,130 64,112 100,112 C136,112 166,130 172,186 Z" fill="#5cc4c4"/></svg></div><div><div class="nm"></div><div class="rl"></div><div class="ft"></div></div></div></div>')
rep("""    if(s.counter){ var cc=s.counter, kk=ease((t-cc.t0)/(cc.t1-cc.t0)); var v=Math.round((cc.a+(cc.b-cc.a)*kk)/10)*10;
      counter.querySelector('.num').textContent= v>=1000 ? (v/1000).toFixed(3).replace(/\\.?0+$/,'') : String(v);
      counter.querySelector('.unit').textContent= v>=1000 ? 'دينار' : 'فلس';""",
"""    if(s.counter){ var cc=s.counter, kk=ease((t-cc.t0)/(cc.t1-cc.t0)); var v=Math.round(cc.a+(cc.b-cc.a)*kk);
      counter.querySelector('.num').textContent=String(v);
      counter.querySelector('.unit').textContent=cc.unit||''; counter.querySelector('.note').textContent=cc.note||'';""")
rep("    disc.style.opacity = (s.n===1) ? 1 : 0;",
    """    disc.style.opacity = 1; var dt=(s.credit||'رسم توضيحي بالذكاء الاصطناعي'); if(disc.textContent!==dt) disc.textContent=dt;
    var PS=s.persons||[], pp=null; PS.forEach(function(q){ if(t>=q.t && t<q.t_out) pp=q; });
    var pe=document.getElementById('person');
    if(pp){ if(pe.getAttribute('data-k')!==pp.name){ pe.setAttribute('data-k',pp.name); pe.querySelector('.nm').textContent=pp.name; pe.querySelector('.rl').textContent=pp.role; pe.querySelector('.ft').textContent=pp.fact; }
      var pk=clamp((t-pp.t)/0.4,0,1), po=clamp((pp.t_out-t)/0.3,0,1);
      pe.style.opacity=(Math.min(pk,po)*hout).toFixed(3); pe.style.transform='translateX('+((1-easeOutBack(pk))*-120).toFixed(1)+'px)'; }
    else pe.style.opacity=0;""")
rep('المصادر: كونا · الجريدة · الراي · MEES · Oil &amp; Gas Journal · وزارة الدفاع الأمريكية · ناسا · الأمم المتحدة · نفط الكويت<small>رسوم توضيحية بالذكاء الاصطناعي · مواقع الحرائق على الخريطة تمثيلية · التفاصيل والأرقام المختلفة في مقال «مِن مصادر»</small>',
    'المصادر: كونا · الجريدة · Kuwait Times · The National · MEES · Oil &amp; Gas Journal · MEED<small>صور أرشيفية بالملكية العامة: وزارة الدفاع الأمريكية · ناسا · مشاة البحرية الأمريكية · وبعض المشاهد رسوم بالذكاء الاصطناعي · التفاصيل في مقال «مِن مصادر»</small>')
rep('<h1>35 عاماً<br>على إطفاء آخر بئر</h1><h2>آبار الكويت المشتعلة: الأرقام بمصادرها</h2>',
    '<h1>35 عاماً<br>على إطفاء آخر بئر</h1><h2>وفريقٌ كويتي دخل النار</h2>')

out = HERE / 'story_template_fires.html'
out.write_text(src, encoding='utf-8')
print('template', out, len(src))
