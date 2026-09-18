# -*- coding: utf-8 -*-
"""
ヨヨイ 안쪽 화면 (ops) — 손님에게 보이는 사이트가 아니다.
build.py 가 docs/ 를 지우고 다시 만든 뒤에 이 파일을 돌린다.

  python3 build.py && python3 ops_build.py

만드는 것
  /ops/denwa/   어르신용 「오늘 걸 전화」 — 전화·대본·결과 세 버튼
  /ops/jobs.json  그 화면이 읽는 오늘 걸 전화 목록 (우리가 채운다)
  /ops/card/    손님이 가게 앞에서 보여주는 확정 카드 (?d=… 로 내용을 담아 보냄)
  /ops/         안쪽 화면 목록

전부 robots 로 막고 noindex 를 단다. 검색에는 안 나온다.
"""
import os, json, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
OUT  = os.path.join(HERE, "docs")
OPS  = os.path.join(OUT, "ops")
SITE = "https://yoyoi.jp"
TODAY = datetime.date.today().isoformat()

CSS = """
*{box-sizing:border-box}
:root{--bg:#fbfaf8;--fg:#17140f;--mut:#6b655c;--acc:#b23b2e;--line:#e6e1d8;--ok:#1f7a4d;--no:#a8321f;--card:#fff}
@media (prefers-color-scheme:dark){:root{--bg:#14120f;--fg:#f2efe9;--mut:#a29b90;--line:#2e2a24;--card:#1c1916}}
html,body{margin:0;background:var(--bg);color:var(--fg);
 font-family:-apple-system,BlinkMacSystemFont,"Hiragino Kaku Gothic ProN","Noto Sans JP",sans-serif;
 font-size:20px;line-height:1.6;-webkit-text-size-adjust:100%}
.wrap{max-width:720px;margin:0 auto;padding:16px}
h1{font-size:1.5rem;margin:.2rem 0 .1rem}
.day{color:var(--mut);margin:0 0 1rem}
.card{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:18px;margin:0 0 20px}
.card.done>*:not(.res){opacity:.42}
.top{display:flex;justify-content:space-between;align-items:baseline;gap:8px}
.shop{font-size:1.35rem;font-weight:700;line-height:1.3}
.area{color:var(--mut);font-size:.95rem;white-space:nowrap}
.when{font-size:1.15rem;margin:.5rem 0 .2rem}
.who{color:var(--mut);margin:0 0 .8rem}
.tel{display:block;text-align:center;background:var(--acc);color:#fff;text-decoration:none;
 font-size:1.45rem;font-weight:700;padding:16px;border-radius:12px;margin:.6rem 0 1rem;letter-spacing:.02em}
.lbl{font-size:.95rem;color:var(--mut);margin:1rem 0 .3rem;font-weight:700}
.script{background:var(--bg);border:1px dashed var(--line);border-radius:10px;padding:14px;font-size:1.15rem;line-height:1.85}
.script b{background:rgba(178,59,46,.14);padding:0 .15em;border-radius:3px;font-weight:700}
ul.ask{margin:.2rem 0;padding-left:1.2rem}
ul.ask li{margin:.35rem 0}
.btns{display:grid;grid-template-columns:1fr 1fr 1fr;gap:10px;margin-top:1rem}
button{font:inherit;font-weight:700;padding:16px 6px;border-radius:12px;border:2px solid var(--line);
 background:var(--card);color:var(--fg);cursor:pointer}
button.ok{border-color:var(--ok);color:var(--ok)}
button.no{border-color:var(--no);color:var(--no)}
button.later{color:var(--mut)}
button:active{transform:translateY(1px)}
.res{margin-top:1rem;border-top:1px solid var(--line);padding-top:1rem;display:none}
.res.on{display:block}
textarea{width:100%;min-height:90px;font:inherit;padding:12px;border:1px solid var(--line);
 border-radius:10px;background:var(--bg);color:var(--fg)}
.send{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:10px}
.send a,.send button{display:block;text-align:center;text-decoration:none;padding:14px;border-radius:12px;
 border:2px solid var(--acc);color:var(--acc);background:transparent;font-weight:700}
.send a.p{background:var(--acc);color:#fff}
.reasons{display:flex;flex-wrap:wrap;gap:8px;margin:.4rem 0 0}
.reasons button{padding:10px 14px;font-size:.95rem;border-radius:999px}
.reasons button[aria-pressed=true]{border-color:var(--acc);color:var(--acc)}
.empty{color:var(--mut);text-align:center;padding:3rem 1rem}
.foot{color:var(--mut);font-size:.9rem;text-align:center;padding:2rem 0 3rem}
a.back{color:var(--acc)}
"""

HEAD = """<!doctype html><html lang="ja"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex,nofollow">
<title>%s</title><style>%s</style></head><body>"""


# ── 어르신용: 오늘 걸 전화 ───────────────────────────────────────────
DENWA_JS = r"""
var MAIL='hray7538@gmail.com';
function el(t,c,x){var e=document.createElement(t);if(c)e.className=c;if(x!=null)e.textContent=x;return e;}
function esc(s){return (s||'').replace(/&/g,'&amp;').replace(/</g,'&lt;');}
function script(j){
  var n=j.people, t=j.when, g=j.guest||'', note=(j.notes||[]);
  var s='お世話になります。<b>予約のお願い</b>でお電話しました。<br>'
      + '<b>'+esc(t)+'</b>、<b>'+esc(String(n))+'名</b>でお願いできますでしょうか。<br>'
      + 'お名前は<b>'+esc(g)+'</b>様です。<b>海外からのお客様</b>で、日本語は話されません。<br>'
      + '私がヨヨイという予約の代行をしておりまして、当日のご案内も私どもでいたします。';
  if(note.length) s += '<br>ご確認をお願いしたいのは、'+note.map(esc).join('、')+' です。';
  return s;
}
function card(j,i){
  var c=el('div','card'); c.id='j'+i;
  var top=el('div','top'); top.appendChild(el('div','shop',j.shop));
  if(j.area) top.appendChild(el('div','area',j.area));
  c.appendChild(top);
  c.appendChild(el('div','when',j.when+' ・ '+j.people+'名'));
  c.appendChild(el('div','who',(j.guest||'')+(j.lang?'（'+j.lang+'）':'')));
  var a=el('a','tel','☎ '+j.tel); a.href='tel:'+j.tel.replace(/[^0-9+]/g,''); c.appendChild(a);
  c.appendChild(el('div','lbl','そのまま読んでください'));
  var sc=el('div','script'); sc.innerHTML=script(j); c.appendChild(sc);
  if((j.notes||[]).length){
    c.appendChild(el('div','lbl','聞くこと'));
    var ul=el('ul','ask'); (j.notes).forEach(function(n){ul.appendChild(el('li',null,n));});
    ul.appendChild(el('li',null,'お会計の方法（カードが使えるか）'));
    c.appendChild(ul);
  }
  var b=el('div','btns');
  var ok=el('button','ok','取れた'), no=el('button','no','だめ'), la=el('button','later','あとで');
  b.appendChild(ok); b.appendChild(no); b.appendChild(la); c.appendChild(b);
  var res=el('div','res'); c.appendChild(res);
  function open_(kind){
    res.className='res on'; res.innerHTML='';
    var ta=el('textarea');
    if(kind==='ok'){ ta.value=j.shop+' 取れました。'+j.when+' '+j.people+'名。\n席：\n注意：\n'; }
    else if(kind==='no'){
      res.appendChild(el('div','lbl','理由'));
      var rs=el('div','reasons');
      ['満席','外国人お断り','電話つながらず','条件が合わない'].forEach(function(r){
        var rb=el('button',null,r); rb.setAttribute('aria-pressed','false');
        rb.onclick=function(){ rb.setAttribute('aria-pressed','true'); ta.value=j.shop+' だめでした。理由：'+r+'\n'; };
        rs.appendChild(rb);
      });
      res.appendChild(rs);
      ta.value=j.shop+' だめでした。理由：\n';
    } else { ta.value=j.shop+' あとでかけ直します。'+'\n時間：\n'; }
    res.appendChild(ta);
    var send=el('div','send');
    var mail=el('a','p','メールで送る'); mail.href='#';
    mail.onclick=function(){ mail.href='mailto:'+MAIL+'?subject='+encodeURIComponent('[電話] '+j.shop)+'&body='+encodeURIComponent(ta.value); };
    var cp=el('button',null,'コピー');
    cp.onclick=function(){ ta.select(); try{document.execCommand('copy');cp.textContent='コピーしました';}catch(e){} };
    send.appendChild(mail); send.appendChild(cp); res.appendChild(send);
    c.className='card done';
  }
  ok.onclick=function(){open_('ok');}; no.onclick=function(){open_('no');}; la.onclick=function(){open_('later');};
  return c;
}
fetch('../jobs.json?'+Date.now()).then(function(r){return r.json();}).then(function(d){
  document.getElementById('day').textContent=(d.date||'')+' ・ '+(d.jobs||[]).length+'件';
  var w=document.getElementById('list');
  if(!d.jobs||!d.jobs.length){ w.appendChild(el('div','empty','今日かけるお電話はありません。')); return; }
  d.jobs.forEach(function(j,i){ w.appendChild(card(j,i)); });
}).catch(function(e){
  document.getElementById('list').appendChild(el('div','empty','読み込めませんでした。'+e));
});
"""

def denwa_page():
    return (HEAD % ("今日かけるお電話 | ヨヨイ", CSS)) + """
<div class="wrap">
<h1>今日かけるお電話</h1>
<p class="day" id="day">…</p>
<div id="list"></div>
<p class="foot">終わったら「メールで送る」を押してください。<br>それだけで大丈夫です。</p>
</div>
<script>%s</script></body></html>""" % DENWA_JS


# ── 손님용: 가게 앞에서 보여주는 확정 카드 ─────────────────────────
CARD_JS = r"""
function gp(){
  try{
    var q=location.search.replace(/^\?/,''),o={};
    q.split('&').forEach(function(kv){ if(!kv)return; var p=kv.split('='); o[p[0]]=decodeURIComponent((p[1]||'').replace(/\+/g,' ')); });
    if(o.d){ return JSON.parse(decodeURIComponent(escape(atob(o.d.replace(/-/g,'+').replace(/_/g,'/'))))); }
    return o;
  }catch(e){ return {}; }
}
var d=gp();
function set(id,v){ var e=document.getElementById(id); if(v){e.textContent=v;} else {e.parentNode.style.display='none';} }
if(!d.shop){ document.getElementById('box').innerHTML='<p class="empty">予約の情報がありません。</p>'; }
else{
  set('shop',d.shop); set('when',d.when); set('people',(d.people?d.people+'名':''));
  set('name',d.guest?d.guest+' 様':'');
  var t=document.getElementById('tel'); if(d.tel){ t.href='tel:'+d.tel.replace(/[^0-9+]/g,''); t.textContent='☎ '+d.tel; } else { t.style.display='none'; }
  var m=document.getElementById('map');
  if(d.addr||d.shop){ m.href='https://www.google.com/maps/search/?api=1&query='+encodeURIComponent((d.addr||'')+' '+d.shop); m.textContent='地図 / Map'; } else { m.style.display='none'; }
  document.getElementById('say').textContent='「'+(d.when||'')+'、'+(d.people||'')+'名、'+(d.guest||'')+'で予約しております。」';
  if(d.note){ document.getElementById('note').textContent=d.note; } else { document.getElementById('notebox').style.display='none'; }
}
"""

def card_page():
    return (HEAD % ("予約カード | ヨヨイ", CSS)) + """
<div class="wrap" id="box">
<h1>ご予約カード</h1>
<p class="day">お店でこの画面をお見せください / Show this at the shop</p>
<div class="card">
  <div class="shop" id="shop"></div>
  <div class="when"><span id="when"></span> ・ <span id="people"></span></div>
  <div class="who"><span id="name"></span></div>
  <div class="lbl">お店の方へ / To the staff</div>
  <div class="script" id="say"></div>
  <div class="send" style="margin-top:14px">
    <a class="p" id="tel"></a>
    <a id="map"></a>
  </div>
</div>
<div class="card" id="notebox">
  <div class="lbl">お伝えしてあること / Already told to the shop</div>
  <div id="note"></div>
</div>
<p class="foot">ヨヨイ Yoyoi</p>
</div>
<script>%s</script></body></html>""" % CARD_JS


def index_page():
    return (HEAD % ("ヨヨイ 안쪽 화면", CSS)) + """
<div class="wrap">
<h1>안쪽 화면</h1>
<p class="day">손님에게 보이지 않는 곳입니다. 검색에도 안 나옵니다.</p>
<div class="card">
  <div class="shop"><a href="denwa/">오늘 걸 전화</a></div>
  <div class="who">어르신 직원이 보는 화면. <code>ops/jobs.json</code> 을 채우면 여기에 카드가 생깁니다.</div>
</div>
<div class="card">
  <div class="shop"><a href="card/?shop=%E4%BE%8B%E3%81%AE%E5%BA%97&amp;when=9/19 19:00&amp;people=2&amp;guest=HA&amp;tel=075-000-0000">예약 카드 (예시)</a></div>
  <div class="who">손님이 가게 앞에서 보여주는 화면. 주소에 내용을 담아 보냅니다.</div>
</div>
<div class="card">
  <div class="shop"><a href="daejang/">대장</a></div>
  <div class="who">예약·가게·손님 기록. 두 번은 안 보낸다가 여기서 돌아갑니다.</div>
</div>
<div class="card">
  <div class="shop"><a href="numbers/">숫자판</a></div>
  <div class="who">대장에서 저절로 나오는 숫자. 파는 쪽에 보여줄 것.</div>
</div>
<p class="foot">ヨヨイ Yoyoi</p>
</div></body></html>"""



# ── 대장 (예약·가게·손님) ─────────────────────────────────────────
DAEJANG_JS = r"""
function el(t,c,x){var e=document.createElement(t);if(c)e.className=c;if(x!=null)e.textContent=x;return e;}
var S={asked:'전화 대기',confirmed:'확정',rejected:'거절',came:'왔음',noshow:'안 옴',cancel:'취소'};
function tbl(rows,cols){
  var t=el('table'),h=el('tr');
  cols.forEach(function(c){h.appendChild(el('th',null,c[0]));}); t.appendChild(h);
  if(!rows.length){ var tr=el('tr'); var td=el('td',null,'아직 없습니다.'); td.colSpan=cols.length; tr.appendChild(td); t.appendChild(tr); return t; }
  rows.forEach(function(r){
    var tr=el('tr');
    cols.forEach(function(c){
      var v=c[1](r); var td=el('td');
      if(c[2]){ td.appendChild(el('span','badge b-'+(r.status||''),v)); } else td.textContent=v;
      tr.appendChild(td);
    });
    t.appendChild(tr);
  });
  return t;
}
function show(name){
  ['b','s','g'].forEach(function(k){
    document.getElementById('t'+k).className = (k===name?'tab on':'tab');
    document.getElementById('p'+k).style.display = (k===name?'block':'none');
  });
}
Promise.all([
  fetch('../bookings.json?'+Date.now()).then(function(r){return r.json();}).catch(function(){return {bookings:[]};}),
  fetch('../shops.json?'+Date.now()).then(function(r){return r.json();}).catch(function(){return {shops:[]};})
]).then(function(a){
  var B=a[0].bookings||[], SH=a[1].shops||[];
  document.getElementById('pb').appendChild(tbl(B,[
    ['날짜',function(r){return r.when||'';}],
    ['손님',function(r){return (r.guest||'')+(r.lang?' ('+r.lang+')':'');}],
    ['가게',function(r){return r.shop||'';}],
    ['인원',function(r){return (r.people||'')+'';}],
    ['상태',function(r){return S[r.status]||r.status||'';},true]
  ]));
  document.getElementById('ps').appendChild(tbl(SH,[
    ['가게',function(r){return r.name||'';}],
    ['지역',function(r){return r.area||'';}],
    ['전화',function(r){return r.tel||'';}],
    ['받아줌',function(r){return r.ok===true?'○':(r.ok===false?'×':'—');}],
    ['메모',function(r){return r.note||'';}]
  ]));
  var g={};
  B.forEach(function(r){ if(!r.guest)return; g[r.guest]=g[r.guest]||{guest:r.guest,lang:r.lang,n:0,came:0,noshow:0};
    g[r.guest].n++; if(r.status==='came')g[r.guest].came++; if(r.status==='noshow')g[r.guest].noshow++; });
  var G=Object.keys(g).map(function(k){return g[k];});
  document.getElementById('pg').appendChild(tbl(G,[
    ['손님',function(r){return r.guest;}],
    ['말',function(r){return r.lang||'';}],
    ['예약',function(r){return r.n+'';}],
    ['왔음',function(r){return r.came+'';}],
    ['안 옴',function(r){return r.noshow+'';}]
  ]));
  document.getElementById('sum').textContent='예약 '+B.length+'건 · 가게 '+SH.length+'곳 · 손님 '+G.length+'명';
});
"""

DJ_CSS = """
.tabs{display:flex;gap:8px;margin:0 0 1rem}
.tab{padding:10px 16px;border:2px solid var(--line);border-radius:999px;background:var(--card);
 color:var(--mut);font-weight:700;cursor:pointer;font:inherit}
.tab.on{border-color:var(--acc);color:var(--acc)}
table{width:100%;border-collapse:collapse;font-size:.9rem}
th{text-align:left;color:var(--mut);font-weight:700;border-bottom:1px solid var(--line);padding:8px 6px;white-space:nowrap}
td{border-bottom:1px solid var(--line);padding:10px 6px;vertical-align:top}
.badge{display:inline-block;padding:2px 10px;border-radius:999px;border:1px solid var(--line);font-size:.85rem;white-space:nowrap}
.b-confirmed{border-color:var(--ok);color:var(--ok)}
.b-came{border-color:var(--ok);color:var(--ok)}
.b-noshow,.b-rejected{border-color:var(--no);color:var(--no)}
.num{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin:1rem 0 2rem}
.n{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:16px}
.n b{display:block;font-size:2rem;line-height:1.1}
.n small{display:block;color:var(--mut);font-size:.85rem;margin-top:.3rem}
.n i{display:block;color:var(--mut);font-size:.8rem;font-style:normal;margin-top:.5rem;line-height:1.5}
"""

def daejang_page():
    return (HEAD % ("대장 | ヨヨイ", CSS+DJ_CSS)) + """
<div class="wrap">
<h1>대장</h1>
<p class="day" id="sum">…</p>
<div class="tabs">
 <button class="tab on" id="tb" onclick="show('b')">예약</button>
 <button class="tab" id="ts" onclick="show('s')">가게</button>
 <button class="tab" id="tg" onclick="show('g')">손님</button>
</div>
<div id="pb"></div>
<div id="ps" style="display:none"></div>
<div id="pg" style="display:none"></div>
<p class="foot"><a class="back" href="../">← 안쪽 화면</a></p>
</div>
<script>%s</script></body></html>""" % DAEJANG_JS


# ── 숫자판 ────────────────────────────────────────────────────────
NUM_JS = r"""
function n(id,v,sub){ var e=document.getElementById(id); e.innerHTML=''; 
  var b=document.createElement('b'); b.textContent=v; e.appendChild(b);
  var s=document.createElement('small'); s.textContent=sub; e.appendChild(s);
}
Promise.all([
  fetch('../bookings.json?'+Date.now()).then(function(r){return r.json();}).catch(function(){return {bookings:[],ad_spend:0};}),
  fetch('../shops.json?'+Date.now()).then(function(r){return r.json();}).catch(function(){return {shops:[]};})
]).then(function(a){
  var B=a[0].bookings||[], SH=a[1].shops||[], ad=a[0].ad_spend||0;
  var conf=B.filter(function(r){return ['confirmed','came','noshow'].indexOf(r.status)>=0;});
  var came=B.filter(function(r){return r.status==='came';}).length;
  var no=B.filter(function(r){return r.status==='noshow';}).length;
  var seen=came+no;
  var g={}; B.forEach(function(r){ if(r.guest) g[r.guest]=(g[r.guest]||0)+1; });
  var rep=Object.keys(g).filter(function(k){return g[k]>1;}).length;
  var gn=Object.keys(g).length;
  var okshop=SH.filter(function(s){return s.ok===true;}).length;
  n('n1', conf.length, '확정된 예약');
  n('n2', seen? Math.round(came/seen*100)+'%':'—', '도착률 (온 사람 ÷ 확정)');
  n('n3', gn? Math.round(rep/gn*100)+'%':'—', '재방문 (두 번 이상 온 손님)');
  n('n4', conf.length&&ad? Math.round(ad/conf.length).toLocaleString()+'엔':'—', '예약 한 건당 광고비');
  n('n5', okshop, '받아주는 가게');
  n('n6', no, '안 온 손님');
});
"""

def numbers_page():
    return (HEAD % ("숫자판 | ヨヨイ", CSS+DJ_CSS)) + """
<div class="wrap">
<h1>숫자판</h1>
<p class="day">대장이 쌓이면 저절로 채워집니다. 따로 적을 것은 광고비뿐입니다.</p>
<div class="num">
 <div class="n" id="n1"></div>
 <div class="n" id="n2"></div>
 <div class="n" id="n3"></div>
 <div class="n" id="n4"></div>
 <div class="n" id="n5"></div>
 <div class="n" id="n6"></div>
</div>
<div class="card">
 <div class="lbl">사는 쪽이 보는 것은 이 셋입니다</div>
 <ul class="ask">
  <li><b>도착률</b> — 예약이 실제 손님이 되는 비율. 핫페퍼가 못 푸는 문제입니다.</li>
  <li><b>건당 광고비</b> — 이 숫자가 수수료보다 낮으면 사업이 됩니다.</li>
  <li><b>받아주는 가게 수</b> — 돈으로 못 사는 것. 대화로만 쌓입니다.</li>
 </ul>
</div>
<p class="foot"><a class="back" href="../">← 안쪽 화면</a></p>
</div>
<script>%s</script></body></html>""" % NUM_JS

BOOKINGS = {"ad_spend": 0,
  "note": "status: asked(전화 대기) / confirmed(확정) / rejected(거절) / came(왔음) / noshow(안 옴) / cancel(취소). ad_spend 는 이번 달 광고비(엔).",
  "bookings": []}
SHOPS = {"note": "ok: true=받아줌, false=거절, 없으면 아직 모름", "shops": []}

SAMPLE = {
  "date": TODAY,
  "note": "이 파일을 채우면 어르신 화면에 카드가 생깁니다. jobs 를 비우면 '오늘 걸 전화 없음'이 됩니다.",
  "jobs": [
    {"shop":"（例）京料理 はな", "area":"祇園", "tel":"075-000-0000",
     "when":"9/19(金) 19:00", "people":2, "guest":"HA", "lang":"한국어",
     "notes":["豚肉が食べられないこと","お一人5,000円くらいのコースがあるか"]}
  ]
}

os.makedirs(os.path.join(OPS,"denwa"), exist_ok=True)
os.makedirs(os.path.join(OPS,"card"), exist_ok=True)
open(os.path.join(OPS,"denwa","index.html"),"w",encoding="utf-8").write(denwa_page())
open(os.path.join(OPS,"card","index.html"),"w",encoding="utf-8").write(card_page())
open(os.path.join(OPS,"index.html"),"w",encoding="utf-8").write(index_page())
os.makedirs(os.path.join(OPS,"daejang"), exist_ok=True)
os.makedirs(os.path.join(OPS,"numbers"), exist_ok=True)
open(os.path.join(OPS,"daejang","index.html"),"w",encoding="utf-8").write(daejang_page())
open(os.path.join(OPS,"numbers","index.html"),"w",encoding="utf-8").write(numbers_page())
for nm, dflt in (("bookings.json",BOOKINGS), ("shops.json",SHOPS)):
    sp = os.path.join(HERE,"ops",nm)
    if not os.path.exists(sp):
        os.makedirs(os.path.join(HERE,"ops"), exist_ok=True)
        open(sp,"w",encoding="utf-8").write(json.dumps(dflt, ensure_ascii=False, indent=1))
    open(os.path.join(OPS,nm),"w",encoding="utf-8").write(open(sp,encoding="utf-8").read())

# jobs.json 은 있으면 덮어쓰지 않는다 (우리가 채우는 파일)
src = os.path.join(HERE,"ops","jobs.json")
if os.path.exists(src):
    data = open(src,encoding="utf-8").read()
else:
    os.makedirs(os.path.join(HERE,"ops"), exist_ok=True)
    data = json.dumps(SAMPLE, ensure_ascii=False, indent=1)
    open(src,"w",encoding="utf-8").write(data)
open(os.path.join(OPS,"jobs.json"),"w",encoding="utf-8").write(data)

# robots: 안쪽 화면은 막는다
rp = os.path.join(OUT,"robots.txt")
r = open(rp,encoding="utf-8").read()
if "/ops/" not in r:
    r = r.replace("Allow: /\n", "Allow: /\nDisallow: /ops/\n")
    open(rp,"w",encoding="utf-8").write(r)

print("안쪽 화면 생성: /ops/ , /ops/denwa/ , /ops/card/ · jobs.json %d건" % len(json.loads(data).get("jobs",[])))
