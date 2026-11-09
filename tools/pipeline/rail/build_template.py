"""Derive story_template_rail.html from story_template_v3.html:
new texts, a rail map engine (route draw + moving train + Kuwait segment + per-country status),
scene-number fixes (8 scenes), and three new ART stickers."""
import re, pathlib

BASE = pathlib.Path('/home/user/min.masader/tools/pipeline')
src = (BASE / 'story_template_v3.html').read_text(encoding='utf-8')


def rep(old, new, count=1):
    global src
    assert src.count(old) == count, (src.count(old), old[:80])
    src = src.replace(old, new, count)


# ---------- texts ----------
rep('<title>الضريبة الانتقائية · فيديو | مِن مصادر</title>',
    '<title>القطار الخليجي · فيديو | مِن مصادر</title>')
rep('<div id="tag">اقتصاد · الكويت</div>', '<div id="tag">اقتصاد · خليجي</div>')
rep('<div id="title"><div class="panel"><div class="k" style="display:inline-block">خبر · اقتصاد</div><h1>الضريبة الانتقائية<br>الخليجية</h1><h2>ماذا قرر مجلس الوزراء؟</h2></div></div>',
    '<div id="title"><div class="panel"><div class="k" style="display:inline-block">خبر · خليجي</div><h1>القطار الخليجي</h1><h2>وُقّعت الاتفاقية.. والكويت نقطة الانطلاق</h2></div></div>')
rep('<div class="src">المصادر: الجريدة · الأنباء · الراي · Gulf News · Times Kuwait<small>رسوم كرتونية بالذكاء الاصطناعي · النسب وفق الإطار الخليجي · النسب النهائية في الكويت لم تُعلن</small></div>',
    '<div class="src">المصادر: كونا · الأنباء · الراي · Arab Times · الشرق الأوسط · الجريدة · السياسة<small>رسوم بالذكاء الاصطناعي · حدود الخريطة: Natural Earth · التفاصيل في مقال «مِن مصادر»</small></div>')
rep('<div id="disc">رسوم توضيحية</div>', '<div id="disc">رسوم توضيحية · خريطة تمثيلية</div>')
rep('<div id="gmap"><div class="mv"></div><div class="leg"><div class="lg"><i></i>دول طبّقت الضريبة منذ 2017</div></div></div>',
    '<div id="gmap"><div class="mv"></div></div>')
# map card sizing: a bit taller placement works as-is; keep.

# chip warn regex
rep("e.className='chip'+(/لم|معفاة/.test(c.text)?' warn':'')",
    "e.className='chip'+(/لم |لا نعرف|قيد الدراسة|أمنية/.test(c.text)?' warn':'')")

# scene-number specifics: title on 2 stays; outro 16 -> 8
rep("outro.style.opacity = (s.n===16) ? ease((t-s.start-0.2)/0.6) : 0;",
    "outro.style.opacity = (s.n===8) ? ease((t-s.start-0.2)/0.6) : 0;")
# title card leaves after ~4s so the signing scene is visible
rep("title.style.opacity = (s.n===2) ? Math.min(ease((t-s.start-0.1)/0.4), 1-ease((t-(s.end-0.3))/0.3)) : 0;",
    "title.style.opacity = (s.n===2) ? Math.min(ease((t-s.start-0.1)/0.4), 1-ease((t-(s.start+4.0))/0.5)) : 0;")

# ---------- part motion: oscillation along travel axis, rumble, slow grow ----------
rep("""      var pop=0.95+0.05*easeOutBack((t-s.start-0.05)/0.55);
      S.parts.forEach(function(P){ var a=P.p.amp, ph=P.p.ph;
        var br=1+0.011*a*Math.sin(2*Math.PI*0.33*t+ph), sx=1-0.004*a*Math.sin(2*Math.PI*0.33*t+ph);
        var rot=0.55*a*Math.sin(2*Math.PI*0.19*t+ph*1.7), bob=-5*a*(0.5+0.5*Math.sin(2*Math.PI*0.42*t+ph*0.9));
        P.e.style.transform='translateY('+bob.toFixed(2)+'px) rotate('+rot.toFixed(3)+'deg) scale('+(sx*pop).toFixed(4)+','+(br*pop).toFixed(4)+')'; });""",
    """      var pop=0.95+0.05*easeOutBack((t-s.start-0.05)/0.55);
      S.parts.forEach(function(P){ var a=P.p.amp||0.6, ph=P.p.ph||0;
        var br=1+0.006*a*Math.sin(2*Math.PI*0.33*t+ph), sx=1-0.003*a*Math.sin(2*Math.PI*0.33*t+ph);
        var rot=0.3*a*Math.sin(2*Math.PI*0.19*t+ph*1.7), bob=-4*a*(0.5+0.5*Math.sin(2*Math.PI*0.42*t+ph*0.9));
        var ex=0,ey=0;
        if(P.p.osc){ var u=Math.sin(2*Math.PI*P.p.osc[2]*t+ph); ex+=P.p.osc[0]*u; ey+=P.p.osc[1]*u; }
        if(P.p.rumble){ ex+=P.p.rumble*Math.sin(2*Math.PI*7.3*t+ph); ey+=0.6*P.p.rumble*Math.sin(2*Math.PI*9.1*t+ph*2); }
        var gs=(P.p.scale0||1)+(P.p.grow||0)*clamp((t-s.start)/Math.max(1,(s.end-s.start)),0,1);
        P.e.style.transform='translate('+ex.toFixed(2)+'px,'+(bob+ey).toFixed(2)+'px) rotate('+rot.toFixed(3)+'deg) scale('+(sx*pop*gs).toFixed(4)+','+(br*pop*gs).toFixed(4)+')'; });""")

# ---------- new FX: speed lines + dust puffs behind a moving train ----------
rep("    stamp:function(g,p){",
    """    speedlines:function(g,p){ var ar=(p.ang||0)*Math.PI/180, dx=Math.cos(ar), dy=Math.sin(ar), ls=[];
      for(var i=0;i<(p.n||7);i++){ ls.push({e:el('line',{stroke:'#ffffff','stroke-width':7+5*rnd(i),'stroke-linecap':'round'},g),o:rnd(i+4),pp:(rnd(i+9)-0.5)*260}); }
      return function(t){ ls.forEach(function(l){ var ph=frac(t*0.9+l.o); var dd=-120-520*ph;
        var x0=p.x+dx*dd-dy*l.pp, y0=p.y+dy*dd+dx*l.pp, x1=x0-dx*(60+80*l.o), y1=y0-dy*(60+80*l.o);
        l.e.setAttribute('x1',x0.toFixed(1)); l.e.setAttribute('y1',y0.toFixed(1)); l.e.setAttribute('x2',x1.toFixed(1)); l.e.setAttribute('y2',y1.toFixed(1));
        l.e.setAttribute('opacity',(0.45*Math.sin(Math.PI*ph)).toFixed(3)); }); }; },
    puffs:function(g,p){ var ar=(p.ang||0)*Math.PI/180, dx=Math.cos(ar), dy=Math.sin(ar), cs=[];
      for(var i=0;i<6;i++){ cs.push({e:el('circle',{fill:'#efe3d0'},g),o:rnd(i+2),pp:(rnd(i+7)-0.5)*40}); }
      return function(t){ cs.forEach(function(c){ var ph=frac(t/1.6+c.o);
        var x=p.x-dx*220*ph-dy*c.pp, y=p.y-dy*220*ph+dx*c.pp-30*ph;
        c.e.setAttribute('cx',x.toFixed(1)); c.e.setAttribute('cy',y.toFixed(1)); c.e.setAttribute('r',(10+34*ph).toFixed(1));
        c.e.setAttribute('opacity',(0.4*(1-ph)*Math.min(1,ph*6)).toFixed(3)); }); }; },
    stamp:function(g,p){""")

# ---------- new ART stickers ----------
rep("    gears:function(){",
    """    train:function(){ return '<rect x="20" y="158" width="168" height="6" rx="3" fill="#9aa5ab"/>'+
      '<rect x="26" y="84" width="130" height="56" rx="14" fill="#0f6b6b" stroke="#13232b" stroke-width="3"/>'+
      '<path d="M156,84 L156,140 L182,140 C186,116 176,92 156,84 Z" fill="#5cc4c4" stroke="#13232b" stroke-width="3"/>'+
      '<rect x="36" y="94" width="24" height="20" rx="4" fill="#bfe9e9"/><rect x="68" y="94" width="24" height="20" rx="4" fill="#bfe9e9"/><rect x="100" y="94" width="24" height="20" rx="4" fill="#bfe9e9"/>'+
      '<circle cx="56" cy="148" r="11" fill="#13232b"/><circle cx="96" cy="148" r="11" fill="#13232b"/><circle cx="136" cy="148" r="11" fill="#13232b"/>'+
      '<line x1="10" y1="100" x2="22" y2="100" stroke="#9aa5ab" stroke-width="5" stroke-linecap="round"/><line x1="4" y1="116" x2="20" y2="116" stroke="#9aa5ab" stroke-width="5" stroke-linecap="round"/>'; },
    gauge:function(){ return '<path d="M32,142 A68,68 0 0 1 168,142" fill="none" stroke="#dfe3df" stroke-width="20" stroke-linecap="round"/>'+
      '<path d="M32,142 A68,68 0 0 1 134,80" fill="none" stroke="#5cc4c4" stroke-width="20" stroke-linecap="round"/>'+
      '<line x1="100" y1="142" x2="141" y2="94" stroke="#13232b" stroke-width="8" stroke-linecap="round"/><circle cx="100" cy="142" r="11" fill="#13232b"/>'+
      '<circle cx="46" cy="118" r="4" fill="#9aa5ab"/><circle cx="70" cy="90" r="4" fill="#9aa5ab"/><circle cx="100" cy="80" r="4" fill="#9aa5ab"/><circle cx="130" cy="90" r="4" fill="#9aa5ab"/><circle cx="154" cy="118" r="4" fill="#9aa5ab"/>'; },
    crowd:function(){ function p(x,y,s,col){ return '<g transform="translate('+x+','+y+') scale('+s+')"><circle cx="0" cy="-26" r="17" fill="'+col+'" stroke="#13232b" stroke-width="3"/><path d="M-24,28 C-24,2 24,2 24,28 Z" fill="'+col+'" stroke="#13232b" stroke-width="3"/></g>'; }
      return p(58,96,0.95,'#e0a98a')+p(142,96,0.95,'#8fc7b1')+p(100,120,1.15,'#5cc4c4')+
      '<rect x="24" y="158" width="152" height="8" rx="4" fill="#c9bfae"/>'; },
    gears:function(){""")

# ---------- replace map engine ----------
map_old_start = "  // ---- animated GCC map (scene with s.gmap) ----"
map_old_end = "  var head=document.getElementById('head')"
i0 = src.index(map_old_start)
i1 = src.index(map_old_end)
new_map = r"""  function mixc(a,b,u){ var pa=[parseInt(a.substr(1,2),16),parseInt(a.substr(3,2),16),parseInt(a.substr(5,2),16)], pb=[parseInt(b.substr(1,2),16),parseInt(b.substr(3,2),16),parseInt(b.substr(5,2),16)];
    return 'rgb('+pa.map(function(v,k){return Math.round(v+(pb[k]-v)*u);}).join(',')+')'; }
  // ---- rail map engine: route draw + train, Kuwait segment zoom, per-country status ----
  var GM=null;
  (function(){
    var any=false; CFG.scenes.forEach(function(s){ if(s.gmap) any=true; }); if(!any||!CFG.geo) return;
    var G=CFG.geo, box=document.getElementById('gmap'), mv=box.querySelector('.mv');
    function P(ll){ return [(ll[0]-G.lon0)*G.cos*G.k, (G.lat1-ll[1])*G.k]; }
    var svg=el('svg',{width:G.w,height:G.h,viewBox:'0 0 '+G.w+' '+G.h}); mv.appendChild(svg);
    var zg=el('g',{},svg);
    G.land.forEach(function(d){ el('path',{d:d,fill:'#efe7d8',stroke:'#c9bfae','stroke-width':1.5,'vector-effect':'non-scaling-stroke'},zg); });
    var cs={}; Object.keys(G.gcc).forEach(function(c){ cs[c]=el('path',{d:G.gcc[c],fill:'#dfe3df',stroke:'#13232b','stroke-width':2,'stroke-linejoin':'round','vector-effect':'non-scaling-stroke'},zg); });
    var branches=el('g',{},zg);
    var routePl=el('polyline',{fill:'none',stroke:'#e0703f','stroke-width':6,'stroke-linecap':'round','stroke-linejoin':'round',opacity:0},zg);
    var segGlow=el('polyline',{fill:'none',stroke:'#5cc4c4','stroke-width':12,'stroke-linecap':'round','stroke-opacity':0},zg);
    var segPl=el('polyline',{fill:'none',stroke:'#0f6b6b','stroke-width':5,'stroke-linecap':'round',opacity:0},zg);
    var dots=el('g',{},zg);
    var train=el('g',{opacity:0},zg);
    train.innerHTML='<rect x="-26" y="-18" width="52" height="20" rx="8" fill="#0f6b6b" stroke="#fffdf8" stroke-width="2.5"/><rect x="-19" y="-13" width="9" height="8" rx="2" fill="#bfe9e9"/><rect x="-6" y="-13" width="9" height="8" rx="2" fill="#bfe9e9"/><rect x="7" y="-13" width="9" height="8" rx="2" fill="#bfe9e9"/><circle cx="-13" cy="4" r="4" fill="#13232b" stroke="#fffdf8" stroke-width="1.5"/><circle cx="0" cy="4" r="4" fill="#13232b" stroke="#fffdf8" stroke-width="1.5"/><circle cx="13" cy="4" r="4" fill="#13232b" stroke="#fffdf8" stroke-width="1.5"/>';
    GM={box:box,mv:mv,zg:zg,cs:cs,routePl:routePl,segPl:segPl,segGlow:segGlow,branches:branches,train:train,dots:dots,P:P,G:G,sc:{},divs:[]};
    CFG.scenes.forEach(function(s){ if(!s.gmap) return; var st={labels:[]};
      (s.gmap.labels||[]).forEach(function(L){ var e=document.createElement('div'); e.className='gl'+(L.cls?' '+L.cls:''); e.textContent=L.text;
        if(L.fs) e.style.fontSize=L.fs+'px'; if(L.bg){ e.style.background=L.bg; } if(L.fg){ e.style.color=L.fg; }
        e.style.opacity=0; mv.appendChild(e); st.labels.push({cfg:L,e:e}); GM.divs.push(e); });
      GM.sc[s.n]=st; });
  })();
  function plen(pts){ var L=0,acc=[0]; for(var i=1;i<pts.length;i++){ L+=Math.hypot(pts[i][0]-pts[i-1][0],pts[i][1]-pts[i-1][1]); acc.push(L);} return {L:L,acc:acc}; }
  function palong(pts,acc,d){ for(var i=1;i<acc.length;i++){ if(d<=acc[i]){ var f=(d-acc[i-1])/Math.max(1e-6,acc[i]-acc[i-1]); return {x:pts[i-1][0]+(pts[i][0]-pts[i-1][0])*f, y:pts[i-1][1]+(pts[i][1]-pts[i-1][1])*f, a:Math.atan2(pts[i][1]-pts[i-1][1],pts[i][0]-pts[i-1][0])}; } } var n=pts.length-1; return {x:pts[n][0],y:pts[n][1],a:0}; }
  function pts2str(px){ return px.map(function(p){return p[0].toFixed(1)+','+p[1].toFixed(1);}).join(' '); }
  function renderMap(t,i,hout){
    if(!GM) return; var s=CFG.scenes[i], m=s.gmap;
    GM.box.style.display=m?'block':'none'; if(!m) return;
    var G=GM.G, kin=(t-m.t_in)/0.5;
    GM.box.style.opacity=(clamp(kin*1.6,0,1)*hout).toFixed(3);
    GM.box.style.transform='translateY('+((1-ease(kin))*60).toFixed(1)+'px) scale('+(0.94+0.06*easeOutBack(clamp(kin,0,1))).toFixed(4)+')';
    var z=1, cx=G.w/2, cy=G.h/2;
    if(m.zoom){ var ze=ease((t-m.zoom.t)/0.9); z=1+(m.zoom.z-1)*ze; var c=GM.P(m.zoom.ll); cx=c[0]-(1-ze)*(c[0]-G.w/2)/z; cy=c[1]-(1-ze)*(c[1]-G.h/2)/z; }
    GM.zg.setAttribute('transform','translate('+(G.w/2)+','+(G.h/2)+') scale('+z.toFixed(4)+') translate('+(-cx).toFixed(2)+','+(-cy).toFixed(2)+')');
    function scr(p){ return [(p[0]-cx)*z+G.w/2,(p[1]-cy)*z+G.h/2]; }
    // hide everything scene-specific, then show the active scene's pieces
    GM.routePl.setAttribute('opacity',0); GM.train.setAttribute('opacity',0);
    GM.segPl.setAttribute('opacity',0); GM.segGlow.setAttribute('stroke-opacity',0);
    while(GM.dots.firstChild===null?false:false){} // no-op keeps linters calm
    Array.prototype.slice.call(GM.dots.childNodes).forEach(function(e){ e.setAttribute('opacity',0); });
    GM.divs.forEach(function(e){ e.style.opacity=0; });
    Object.keys(GM.cs).forEach(function(c){ GM.cs[c].setAttribute('fill','#dfe3df'); GM.cs[c].setAttribute('stroke','#13232b'); GM.cs[c].setAttribute('stroke-width',2); });
    GM.branches.setAttribute('opacity',0);
    if(m.kwfill!==undefined){ var kk=clamp((t-m.kwfill)/0.4,0,1); if(kk>0){ GM.cs.KWT.setAttribute('fill',mixc('#dfe3df','#f6c9a9',kk)); GM.cs.KWT.setAttribute('stroke','#e0703f'); GM.cs.KWT.setAttribute('stroke-width',(2+2*kk).toFixed(2)); } }
    (m.lit||[]).forEach(function(L){ var u=clamp((t-L.t)/0.45,0,1); if(u<=0) return; GM.cs[L.c].setAttribute('fill',mixc('#dfe3df',L.col,u)); if(L.hold){ GM.cs[L.c].setAttribute('stroke','#e0703f'); GM.cs[L.c].setAttribute('stroke-width',(2+2*u).toFixed(2)); } });
    var r=m.route;
    if(r){
      if(!r._px){ r._px=r.pts.map(GM.P); var q=plen(r._px); r._L=q.L; r._acc=q.acc; GM.routePl.setAttribute('points',pts2str(r._px));
        if(r.branches){ GM.branches.innerHTML=''; r.branches.forEach(function(b){ el('polyline',{points:pts2str(b.map(GM.P)),fill:'none',stroke:'#e0703f','stroke-width':4,'stroke-dasharray':'8 7','stroke-linecap':'round'},GM.branches); }); } }
      var k2=clamp((t-r.t0)/(r.t1-r.t0),0,1), e2=0.5-0.5*Math.cos(Math.PI*k2);
      GM.routePl.setAttribute('stroke-dasharray',r._L+' '+r._L);
      GM.routePl.setAttribute('stroke-dashoffset',(r._L*(1-e2)).toFixed(1));
      GM.routePl.setAttribute('opacity',t>=r.t0-0.05?1:0);
      GM.branches.setAttribute('opacity',k2>=1?clamp((t-r.t1)/0.4,0,1):0);
      if(t>=r.t0){ var pos=palong(r._px,r._acc,r._L*e2);
        GM.train.setAttribute('opacity',1);
        var deg=pos.a*180/Math.PI;
        GM.train.setAttribute('transform','translate('+pos.x.toFixed(1)+','+pos.y.toFixed(1)+') rotate('+deg.toFixed(1)+') translate(0,-13) scale(0.9)'); }
      (r.stops||[]).forEach(function(st){
        if(st._p===undefined){ st._p=GM.P(st.ll); st._e=el('circle',{r:4.5,fill:'#13232b',stroke:'#fffdf8','stroke-width':2},GM.dots);
          st._l=document.createElement('div'); st._l.className='gl'; st._l.style.fontSize=(st.fs||24)+'px'; st._l.textContent=st.name; GM.mv.appendChild(st._l); GM.divs.push(st._l); }
        var on=(r._L*e2)>=(r._acc[st.at]-1);
        st._e.setAttribute('cx',st._p[0]); st._e.setAttribute('cy',st._p[1]); st._e.setAttribute('opacity',on?1:0);
        var sp=scr(st._p); st._l.style.left=sp[0].toFixed(1)+'px'; st._l.style.top=(sp[1]+(st.dy||-30)).toFixed(1)+'px';
        st._l.style.transform='translate(-50%,-50%)'; st._l.style.opacity=on?(0.95*hout).toFixed(3):0; });
    }
    var sg=m.seg;
    if(sg){
      if(!sg._px){ sg._px=sg.pts.map(GM.P); var q2=plen(sg._px); sg._L=q2.L; sg._acc=q2.acc;
        GM.segPl.setAttribute('points',pts2str(sg._px)); GM.segGlow.setAttribute('points',pts2str(sg._px)); }
      var ks=clamp((t-sg.t0)/(sg.t1-sg.t0),0,1), es=ease(ks);
      GM.segPl.setAttribute('stroke-dasharray',sg._L+' '+sg._L);
      GM.segPl.setAttribute('stroke-dashoffset',(sg._L*(1-es)).toFixed(2));
      GM.segPl.setAttribute('opacity',t>=sg.t0?1:0);
      if(ks>=1){ var pulse=0.5+0.5*Math.sin(2*Math.PI*1.2*(t-sg.t1)); GM.segGlow.setAttribute('stroke-opacity',((0.2+0.3*pulse)*hout).toFixed(3)); }
      if(t>=sg.t0){ var pos2=palong(sg._px,sg._acc,sg._L*es); GM.train.setAttribute('opacity',1);
        var deg2=pos2.a*180/Math.PI;
        GM.train.setAttribute('transform','translate('+pos2.x.toFixed(1)+','+pos2.y.toFixed(1)+') rotate('+deg2.toFixed(1)+') translate(0,-10) scale(0.38)'); }
    }
    var ST=GM.sc[s.n];
    if(ST){ ST.labels.forEach(function(Lb){ var c=Lb.cfg, o=clamp((t-c.t)/0.35,0,1); if(o<=0){ Lb.e.style.opacity=0; return; }
      var sp=scr(GM.P(c.ll)); Lb.e.style.left=sp[0].toFixed(1)+'px'; Lb.e.style.top=(sp[1]+(c.dy||0)).toFixed(1)+'px';
      Lb.e.style.transform='translate(-50%,-50%) scale('+(0.7+0.3*easeOutBack(o)).toFixed(3)+')';
      Lb.e.style.opacity=(o*0.97*hout).toFixed(3); }); }
  }
"""
src = src[:i0] + new_map + src[i1:]

out = BASE / 'rail' / 'story_template_rail.html'
out.write_text(src, encoding='utf-8')
print('written', out, len(src))
