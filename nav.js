(function(){
// Camera v3 for an untouched report page. One move = pan (like scrolling) plus magnify only when needed.
// Rules learned in rehearsal: page zoom reflows responsive pages, so magnify the view instead;
// keep glides short (speed first) and make the first move instant.
var F=window.F=[].slice.call(document.querySelectorAll('figure'));
F.forEach(function(f){var s=f.querySelector('svg'),h=s?s.innerHTML:'',arcs=(h.match(/ A\d/g)||[]).length;
 f.setAttribute('data-kind',s&&s.querySelector('polyline')?'line chart trend':(arcs?(/ L[\d.]+,[\d.]+ A/.test(h)?'donut ring pie chart':'pie chart'):'bar chart'));});
var de=document.documentElement,b=document.body;de.style.zoom='';
window.scrollTo(0,0);de.style.overflow='hidden';b.style.transformOrigin='0 0';
var cam={tx:0,ty:0,s:1},MAXS=4,FILL=0.94;
window.pdcam=function(el,instant){
 var r=el.getBoundingClientRect(),x=(r.left-cam.tx)/cam.s,y=(r.top-cam.ty)/cam.s,w=r.width/cam.s,h=r.height/cam.s;
 var vw=innerWidth,vh=innerHeight,s=Math.min(Math.min(vw/w,vh/h)*FILL,MAXS);
 var nt={tx:vw/2-(x+w/2)*s,ty:vh/2-(y+h/2)*s,s:s};
 var dist=Math.hypot(r.left+r.width/2-vw/2,r.top+r.height/2-vh/2),dur=instant?0:Math.min(0.5,Math.max(0.25,0.25+dist/4000));
 cam=nt;b.style.transition=dur?'transform '+dur.toFixed(2)+'s cubic-bezier(.4,0,.2,1)':'none';
 b.style.transform='translate('+nt.tx+'px,'+nt.ty+'px) scale('+s+')';
 window.pdlast={scale:+s.toFixed(2),glide:+dur.toFixed(2),native:Math.round(Math.max(w/vw,h/vh)*100)};
 return s;};
window.pdmeasure=function(){if(window.cur<0)return 'null';var r=F[cur].querySelector('svg').getBoundingClientRect(),vw=innerWidth,vh=innerHeight,f=Math.max(r.width/vw,r.height/vh),ox=(r.left+r.width/2-vw/2)/vw,oy=(r.top+r.height/2-vh/2)/vh;
 return JSON.stringify({chart:cur+1,fill:Math.round(f*100),off_x:Math.round(ox*100),off_y:Math.round(oy*100),scale:+cam.s.toFixed(2),ok:f>=0.85&&f<=1&&Math.abs(ox)<0.05&&Math.abs(oy)<0.05});};
window.cur=-1;
window.pdto=function(i){i=Math.max(0,Math.min(F.length-1,i));var first=window.cur<0;window.cur=i;pdcam(F[i].querySelector('svg'),first);return i;};
window.pdrel=function(n){return pdto((cur<0?0:cur)+n);};
window.pdfind=function(q){var w=q.toLowerCase().replace(/\b(the|a|go|to|show|slide|chart|graph|one|with|about|me)\b/g,' ').split(/\s+/).filter(Boolean),bi=-1,bs=0;
 F.forEach(function(f,i){var t=(f.textContent+' '+(f.getAttribute('data-say')||'')+' '+f.getAttribute('data-kind')).toLowerCase(),s=0;w.forEach(function(x){if(t.indexOf(x)>=0)s++;});if(s>bs){bs=s;bi=i;}});
 return bi<0?-1:pdto(bi);};
})();
