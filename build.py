# -*- coding: utf-8 -*-
"""build.py — 組裝單檔 index.html 並執行輸出前驗證"""
import json, re, os, sys
import gloss
from meta import META, FIVE_STAGES

OUT = os.environ.get('CWSL_OUT', 'index.html')  # 輸出路徑，可以環境變數覆寫

d = json.load(open('corpus.json'))
secs, app, kepan, cmeta = d['sections'], d['apparatus'], d['kepan'], d['meta']

# ---- 組裝資料層 ----
data_sections = []
for s in secs:
    g = gloss.SEC[s['id']]
    assert g['verses'] == s['verses'], s['id']
    data_sections.append({
        'id': s['id'], 'label': g['label'], 'verses': s['verses'],
        'kind': s['kind'], 'juan': s['juan'], 'chars': s['chars'],
        'blocks': s['blocks'], 'kepan': s['kepan'],
        'yi': g['yi'], 'yao': g['yao'], 'ming': g['ming'],
        'tables': gloss.TABLES.get(s['id'], []),
    })

verse_index = {}
for s in data_sections:
    for v in s['verses']:
        verse_index[v] = s['id']

DATA = {
    'meta': META, 'sections': data_sections, 'app': app, 'kepan': kepan,
    'verseIndex': verse_index, 'general': gloss.GENERAL_TERMS,
    'stats': {'net': cmeta['net_chars'], 'app': cmeta['app_entries'],
              'gaiji': len(cmeta['gaiji']), 'unresolved': cmeta['gaiji_unresolved']},
    'stages': {str(k): v for k, v in FIVE_STAGES.items()},
    'orphan': [],
}

# 未落地校勘：位於卷首譯者題名與卷末題記（非論文正文），另列不隱沒
_used = set()
for _s in data_sections:
    for _b in _s['blocks']:
        _txt = _b.get('text', '') + ''.join(_b.get('lines', []))
        _used |= {int(x) for x in re.findall(r'\u2e22(\d+)\u2e23', _txt)}
DATA['orphan'] = [{'i': i + 1, **app[i]} for i in range(len(app)) if i not in _used]

TPL = r"""<!DOCTYPE html>
<html lang="zh-Hant">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1">
<title>成唯識論 · 線上讀本</title>
<link rel="canonical" href="__CANON__">
<meta name="description" content="《成唯識論》十卷全文線上讀本。護法等菩薩造，唐玄奘譯，底本大正藏 T31 no.1585（CBETA）。依世親《唯識三十頌》三十頌分節，附三分科判、頌旨語譯、要義提點與唯識名相，並載三九四則校勘異文。">
<meta property="og:type" content="website">
<meta property="og:locale" content="zh_TW">
<meta property="og:site_name" content="成唯識論 · 線上讀本">
<meta property="og:title" content="成唯識論 · 線上讀本">
<meta property="og:description" content="十卷全文．三十頌分節．三分科判。底本：大正藏 T31 no.1585（CBETA）。附頌旨語譯、要義提點、唯識名相與校勘異文。">
<style>
:root{
  --ink:#141821; --ink2:#2b3242; --paper:#f2f0ea; --paper2:#e7e3d9;
  --indigo:#2f4858; --indigo2:#3f6072; --mirror:#8a7f6b; --seal:#8c3b34;
  --line:rgba(20,24,33,.14); --rule:rgba(20,24,33,.08);
  --serif:"Noto Serif TC","Songti TC","Source Han Serif TC",serif;
  --sans:"Noto Sans TC","PingFang TC","Heiti TC",sans-serif;
}
*{box-sizing:border-box;-webkit-tap-highlight-color:transparent}
html,body{margin:0;padding:0}
body{background:var(--paper);color:var(--ink);font-family:var(--serif);
  line-height:1.95;font-size:17px;overflow-x:hidden}
button{font-family:inherit;color:inherit;border:0;background:none;cursor:pointer}

/* ── 封面 ── */
#cover{position:fixed;inset:0;z-index:60;background:var(--paper);
  display:flex;flex-direction:column;justify-content:center;padding:32px 26px;
  transition:opacity .5s}
#cover.gone{opacity:0;pointer-events:none}
.cv-seal{width:52px;height:52px;border:1.5px solid var(--seal);color:var(--seal);
  display:flex;align-items:center;justify-content:center;font-size:19px;
  letter-spacing:.06em;margin-bottom:26px}
.cv-t{font-size:33px;letter-spacing:.22em;font-weight:600;margin:0 0 6px}
.cv-s{font-size:13px;letter-spacing:.28em;color:var(--indigo2);margin-bottom:22px}
.cv-by{font-size:13.5px;color:var(--ink2);line-height:2.1}
.cv-r{margin:22px 0;border-top:1px solid var(--line);padding-top:18px;
  font-size:12.5px;color:#5a6070;line-height:2}
.cv-go{margin-top:8px;border:1px solid var(--indigo);color:var(--indigo);
  padding:13px 0;width:100%;font-size:15px;letter-spacing:.3em;font-family:var(--serif)}
.cv-go:active{background:var(--indigo);color:var(--paper)}

/* ── 頁首 ── */
header{position:sticky;top:0;z-index:40;background:rgba(242,240,234,.97);
  backdrop-filter:blur(8px);border-bottom:1px solid var(--line)}
.hb{display:flex;align-items:center;gap:10px;padding:9px 12px}
.hb h1{font-size:16px;margin:0;letter-spacing:.14em;font-weight:600;flex:1}
.icb{width:34px;height:34px;display:flex;align-items:center;justify-content:center;
  font-size:13px;border:1px solid var(--line);color:var(--indigo)}
.icb.on{background:var(--indigo);color:var(--paper);border-color:var(--indigo)}

/* ── 頌組 ribbon ── */
#ribbon{display:flex;gap:6px;overflow-x:auto;padding:0 12px 9px;scrollbar-width:none}
#ribbon::-webkit-scrollbar{display:none}
.rc{flex:0 0 auto;padding:5px 11px;border:1px solid var(--line);font-size:12.5px;
  white-space:nowrap;color:var(--ink2);letter-spacing:.04em}
.rc.on{background:var(--ink);color:var(--paper);border-color:var(--ink)}
.rc .rn{font-size:10.5px;opacity:.6;margin-right:4px;font-family:var(--sans)}

/* ── 分頁 ── */
#tabs{display:flex;border-bottom:1px solid var(--line);background:var(--paper)}
.tb{flex:1;padding:10px 0;font-size:13.5px;letter-spacing:.12em;color:#6b7182;
  border-bottom:2px solid transparent}
.tb.on{color:var(--ink);border-bottom-color:var(--seal)}

/* ── 內文 ── */
main{padding:18px 18px 120px;max-width:720px;margin:0 auto}
.sec-hd{margin:2px 0 18px}
.sec-hd .eyebrow{font-family:var(--sans);font-size:11px;letter-spacing:.24em;
  color:var(--mirror);display:block;margin-bottom:5px}
.sec-hd h2{font-size:20px;margin:0;letter-spacing:.1em;font-weight:600}
.sec-hd .meta{font-family:var(--sans);font-size:11.5px;color:#767c8c;margin-top:6px;
  letter-spacing:.04em}
.k{font-family:var(--sans);font-size:12px;letter-spacing:.1em;color:var(--indigo2);
  margin:22px 0 8px;padding-left:9px;border-left:2px solid var(--indigo2)}
.k.lv3{opacity:.85;font-size:11.5px} .k.lv4,.k.lv5,.k.lv6{opacity:.7;font-size:11px;
  border-left-style:dotted}
p.t{margin:0 0 15px;text-align:justify;text-indent:2em}
.vs{margin:20px 0;padding:16px 16px 16px 20px;background:var(--paper2);
  border-left:3px solid var(--seal)}
.vs .vn{font-family:var(--sans);font-size:11px;letter-spacing:.2em;color:var(--seal);
  display:block;margin-bottom:8px}
.vs .vl{font-size:17.5px;letter-spacing:.06em;line-height:2.15;margin:0}
.ap{border-bottom:1px dotted var(--seal);cursor:pointer}
.ap sup{font-family:var(--sans);font-size:9px;color:var(--seal);
  vertical-align:super;margin-left:1px}
.jm{font-family:var(--sans);font-size:11px;color:#8b909e;letter-spacing:.16em;
  text-align:center;margin:26px 0;border-top:1px solid var(--rule);padding-top:6px}

.card{background:#fff;border:1px solid var(--line);padding:17px 17px 14px;
  margin-bottom:14px}
.card h3{font-family:var(--sans);font-size:12px;letter-spacing:.2em;color:var(--indigo2);
  margin:0 0 11px;font-weight:600}
.card p{margin:0;text-align:justify}
ol.yao{margin:0;padding-left:1.25em} ol.yao li{margin-bottom:12px;text-align:justify}
dl.ming{margin:0} dl.ming dt{font-weight:600;letter-spacing:.06em;margin-top:13px;
  color:var(--indigo)} dl.ming dt:first-child{margin-top:0}
dl.ming dd{margin:3px 0 0;font-size:15.5px;color:var(--ink2);text-align:justify}
.tbl{width:100%;border-collapse:collapse;font-size:14px;font-family:var(--sans);
  margin-top:4px}
.tbl th{background:var(--paper2);font-weight:600;font-size:11.5px;letter-spacing:.1em;
  color:var(--indigo2);padding:7px 8px;text-align:left;border:1px solid var(--line)}
.tbl td{padding:7px 8px;border:1px solid var(--rule);vertical-align:top;line-height:1.75;
  color:var(--ink2)}
.tbl td:first-child{white-space:nowrap;color:var(--ink);font-family:var(--serif);
  letter-spacing:.04em}
.tnote{font-size:13px;color:#6c7283;line-height:1.85;margin:0 0 10px;text-align:justify}
.twrap{overflow-x:auto;-webkit-overflow-scrolling:touch}
.jt{font-family:var(--sans);font-size:11.5px;letter-spacing:.2em;color:var(--mirror);
  text-align:center;margin:24px 0 4px}
.by{font-size:14px;color:#5c6272;text-align:center;letter-spacing:.08em;margin:0 0 14px}
.hh{font-size:18px;letter-spacing:.14em;text-align:center;margin:30px 0 10px;
  font-weight:600}

/* ── 抽屜 ── */
#scrim{position:fixed;inset:0;background:rgba(20,24,33,.42);z-index:45;display:none}
#scrim.on{display:block}
.drawer{position:fixed;top:0;bottom:0;width:min(88vw,380px);background:var(--paper);
  z-index:50;transition:transform .28s;overflow-y:auto;padding:16px 16px 60px}
#toc{left:0;transform:translateX(-102%);border-right:1px solid var(--line)}
#toc.on{transform:none}
#chat{position:fixed;inset:0;width:auto;z-index:52;background:var(--paper);
  transform:translateY(102%);display:flex;flex-direction:column;padding:0;border:0}
#chat.on{transform:none}
.dh{font-family:var(--sans);font-size:12px;letter-spacing:.2em;color:var(--mirror);
  margin:20px 0 9px;border-bottom:1px solid var(--rule);padding-bottom:5px}
.dh:first-child{margin-top:4px}
.axis{display:flex;flex-wrap:wrap;gap:6px}
.axis button{border:1px solid var(--line);padding:5px 9px;font-size:12.5px;
  font-family:var(--sans);color:var(--ink2)}
.axis button.on{background:var(--indigo);color:var(--paper);border-color:var(--indigo)}
.ktree button{display:block;width:100%;text-align:left;font-size:13px;padding:5px 0;
  color:var(--ink2);line-height:1.7}
.ktree .l1{font-weight:600;color:var(--ink);letter-spacing:.1em;margin-top:10px}
.ktree .l2{padding-left:12px} .ktree .l3{padding-left:24px;font-size:12.5px}
.ktree .l4{padding-left:36px;font-size:12px;color:#6c7283}
.ktree .l5,.ktree .l6{padding-left:46px;font-size:11.5px;color:#7b8090}

/* ── 問答（全螢幕・無氣泡） ── */
.ch-top{display:flex;align-items:center;gap:7px;padding:9px 11px;position:relative;
  border-bottom:1px solid var(--line);background:rgba(242,240,234,.98)}
.ch-top .ttl{flex:1;font-size:14px;letter-spacing:.08em;white-space:nowrap;
  overflow:hidden;text-overflow:ellipsis}
.ch-top .ttl small{display:block;font-family:var(--sans);font-size:10.5px;
  letter-spacing:.16em;color:var(--mirror);margin-top:1px}
.mbtn{width:34px;height:34px;flex:0 0 34px;border:1px solid var(--line);display:flex;
  align-items:center;justify-content:center;color:var(--indigo)}
.mbtn.on{background:var(--indigo);color:var(--paper);border-color:var(--indigo)}
.mbtn svg{width:16px;height:16px;stroke:currentColor;fill:none;stroke-width:1.7;
  stroke-linecap:round;stroke-linejoin:round}
#menu{position:absolute;top:50px;left:9px;width:min(80vw,310px);background:#fff;
  border:1px solid var(--ink);z-index:6;display:none;max-height:74vh;overflow-y:auto}
#menu.on{display:block}
.mgrp{font-family:var(--sans);font-size:10.5px;letter-spacing:.22em;color:var(--mirror);
  padding:12px 13px 5px;border-bottom:1px solid var(--rule)}
.mi{display:block;width:100%;text-align:left;padding:11px 13px;font-size:14px;
  border-bottom:1px solid var(--rule);letter-spacing:.04em}
.mi.warn{color:var(--seal)}
.mi.tgl{display:flex;align-items:center;justify-content:space-between}
.mi.tgl b{font-family:var(--sans);font-size:11px;font-weight:400;color:#8b909e}
.mi.tgl.on b{color:var(--seal)}
.conv{display:flex;align-items:center;gap:5px;padding:8px 9px 8px 13px;
  border-bottom:1px solid var(--rule)}
.conv.on{background:var(--paper2)}
.conv .cn{flex:1;text-align:left;font-size:13.5px;line-height:1.55;overflow:hidden}
.conv .cn small{display:block;font-family:var(--sans);font-size:10.5px;color:#8b909e;
  margin-top:2px;letter-spacing:.06em}
.conv .st{width:30px;height:30px;flex:0 0 30px;color:#c6c0b1;font-size:14px}
.conv .st.on{color:var(--seal)}
.conv .rm{width:30px;height:30px;flex:0 0 30px;color:#b9b3a4;font-size:15px}
.empty{padding:14px 13px;font-family:var(--sans);font-size:12px;color:#8b909e;
  line-height:1.9}
#log{flex:1;overflow-y:auto;padding:16px 16px 24px;max-width:720px;margin:0 auto;width:100%}
.msg{margin-bottom:19px;padding-bottom:17px;border-bottom:1px solid var(--rule)}
.msg:last-child{border-bottom:0}
.msg .who{font-family:var(--sans);font-size:10.5px;letter-spacing:.24em;
  color:var(--mirror);display:block;margin-bottom:7px}
.msg.u .who{color:var(--indigo2)}
.msg .bd{font-size:16px;line-height:1.95;text-align:justify;white-space:pre-wrap}
.msg .tools{margin-top:9px;display:flex;gap:7px}
.msg .tools button{font-family:var(--sans);font-size:11px;color:#6c7283;
  border:1px solid var(--line);padding:3px 9px;letter-spacing:.08em}
.msg .tools button.on{background:var(--seal);color:var(--paper);border-color:var(--seal)}
.ch-in{border-top:1px solid var(--line);padding:9px 10px;display:flex;gap:7px;
  align-items:flex-end;max-width:720px;margin:0 auto;width:100%}
.ch-in textarea{flex:1;border:1px solid var(--line);padding:9px 10px;
  font-family:var(--serif);font-size:15.5px;resize:none;height:42px;max-height:120px;
  background:#fff;line-height:1.6}
.ch-in .snd{border:1px solid var(--indigo);color:var(--indigo);padding:0 15px;
  height:42px;font-size:13px;letter-spacing:.1em}
.ch-in .mic{height:42px;flex:0 0 42px}
.ch-in .mic.on{background:var(--seal);color:var(--paper);border-color:var(--seal)}
.notice{margin:10px 15px 0;padding:9px 11px;border:1px dashed var(--line);
  font-family:var(--sans);font-size:11.5px;color:#6c7283;line-height:1.8;
  max-width:720px}

/* ── 底部列 ── */
#foot{position:fixed;left:0;right:0;bottom:0;z-index:35;background:rgba(242,240,234,.97);
  backdrop-filter:blur(8px);border-top:1px solid var(--line);display:flex;
  align-items:center;gap:8px;padding:8px 12px;max-width:720px;margin:0 auto}
#foot button{border:1px solid var(--line);padding:8px 12px;font-size:12.5px;
  font-family:var(--sans);color:var(--ink2)}
#foot .pos{flex:1;text-align:center;font-family:var(--sans);font-size:11.5px;
  color:#767c8c;letter-spacing:.08em}
#foot button:active{background:var(--paper2)}

/* ── 彈出 ── */
#pop{position:fixed;left:12px;right:12px;bottom:64px;z-index:55;background:#fff;
  border:1px solid var(--ink);padding:14px 15px;display:none;max-width:696px;
  margin:0 auto;font-size:14.5px;line-height:1.9}
#pop.on{display:block}
#pop .pt{font-family:var(--sans);font-size:11px;letter-spacing:.2em;color:var(--seal);
  margin-bottom:7px}
#pop .wit{font-family:var(--sans);font-size:12.5px;color:var(--ink2);margin-top:4px}
#modal{position:fixed;inset:0;z-index:58;background:rgba(20,24,33,.5);display:none;
  padding:26px 16px;overflow-y:auto}
#modal.on{display:block}
.mbox{background:var(--paper);max-width:620px;margin:0 auto;padding:22px 20px 30px;
  border:1px solid var(--ink)}
.mbox h2{font-size:17px;letter-spacing:.14em;margin:0 0 14px}
.mbox dt{font-family:var(--sans);font-size:11.5px;letter-spacing:.14em;
  color:var(--mirror);margin-top:14px}
.mbox dd{margin:3px 0 0;font-size:14.5px;text-align:justify;line-height:1.9}
.mbox .warn{margin-top:18px;padding:11px 12px;border:1px dashed var(--seal);
  font-size:13.5px;color:var(--ink2);line-height:1.9}
@media (prefers-reduced-motion:reduce){*{transition:none!important}}
:focus-visible{outline:2px solid var(--seal);outline-offset:2px}
</style>
</head>
<body>

<div id="cover">
  <div class="cv-seal">識</div>
  <h1 class="cv-t">成唯識論</h1>
  <div class="cv-s">CHENG WEISHI LUN · 十卷</div>
  <div class="cv-by">護法等菩薩造<br>唐 三藏法師玄奘 奉詔譯</div>
  <div class="cv-r" id="coverNote"></div>
  <button class="cv-go" onclick="enter()">開始閱讀</button>
</div>

<header>
  <div class="hb">
    <button class="icb" onclick="tog('toc')" aria-label="目錄">目錄</button>
    <h1>成唯識論</h1>
    <button class="icb" onclick="showMeta()" aria-label="版本註記">註</button>
    <button class="icb" id="hdrTts" onclick="tts()" aria-label="朗讀本節">
      <svg viewBox="0 0 24 24" style="width:16px;height:16px;stroke:currentColor;fill:none;stroke-width:1.7;stroke-linecap:round;stroke-linejoin:round"><path d="M4 9v6h4l5 4V5L8 9H4z"/><path d="M17 8.5a5 5 0 010 7"/></svg></button>
    <button class="icb" onclick="tog('chat')" aria-label="問答">
      <svg viewBox="0 0 24 24" style="width:16px;height:16px;stroke:currentColor;fill:none;stroke-width:1.7;stroke-linecap:round;stroke-linejoin:round"><path d="M20 12a8 8 0 01-11.6 7.1L4 20l1-4.2A8 8 0 1120 12z"/></svg></button>
  </div>
  <div id="ribbon"></div>
</header>

<div id="tabs">
  <button class="tb on" data-t="0">論文</button>
  <button class="tb" data-t="1">頌旨語譯</button>
  <button class="tb" data-t="2">要義提點</button>
  <button class="tb" data-t="3">唯識名相</button>
</div>

<main id="main"></main>

<div id="foot">
  <button onclick="go(-1)">上節</button>
  <span class="pos" id="pos"></span>
  <button onclick="go(1)">下節</button>
</div>

<div id="pop" onclick="this.classList.remove('on')"></div>

<div id="scrim" onclick="closeAll()"></div>

<nav id="toc" class="drawer" aria-label="目錄">
  <div class="dh">十卷</div><div class="axis" id="axJuan"></div>
  <div class="dh">三十頌</div><div class="axis" id="axVerse"></div>
  <div class="dh">三分科判</div><div class="ktree" id="axKepan"></div>
</nav>

<aside id="chat" aria-label="唯識問答">
  <div class="ch-top">
    <button class="mbtn" id="hamb" onclick="togMenu()" aria-label="選單" aria-haspopup="true">
      <svg viewBox="0 0 24 24"><path d="M4 7h16M4 12h16M4 17h16"/></svg></button>
    <div class="ttl" id="convTtl">新對話<small>未歸專案</small></div>
    <button class="mbtn" onclick="share()" aria-label="分享">
      <svg viewBox="0 0 24 24"><path d="M12 16V4M8 8l4-4 4 4"/><path d="M5 14v5a1 1 0 001 1h12a1 1 0 001-1v-5"/></svg></button>
    <button class="mbtn" onclick="tog('chat')" aria-label="關閉">
      <svg viewBox="0 0 24 24"><path d="M6 6l12 12M18 6L6 18"/></svg></button>

    <div id="menu" role="menu">
      <button class="mi" onclick="newConv()">＋　開新對話</button>
      <button class="mi" onclick="renameConv()">重新命名</button>
      <button class="mi" onclick="pickProject()">歸入專案…</button>
      <button class="mi warn" onclick="delConv()">刪除此對話</button>
      <div class="mgrp">紀錄</div>
      <button class="mi tgl" id="starTgl" onclick="togStarred()">僅收藏<b>關</b></button>
      <div id="convList"></div>
      <div class="mgrp">專案</div>
      <div id="projList"></div>
      <button class="mi" onclick="newProject()">＋　新增專案</button>
    </div>
  </div>
  <div class="notice" id="chNotice"></div>
  <div id="log"></div>
  <div class="ch-in">
    <button class="mbtn mic" id="micBtn" onclick="mic()" aria-label="語音輸入">
      <svg viewBox="0 0 24 24"><rect x="9" y="3" width="6" height="11" rx="3"/><path d="M5 11a7 7 0 0014 0M12 18v3"/></svg></button>
    <textarea id="q" placeholder="就本節論文提問…"></textarea>
    <button class="snd" onclick="ask()">送出</button>
  </div>
</aside>

<div id="modal" onclick="if(event.target===this)this.classList.remove('on')">
  <div class="mbox" id="mbox"></div>
</div>

<script id="corpus" type="application/json">__DATA__</script>
<script>
const D=JSON.parse(document.getElementById('corpus').textContent);
const S=D.sections, M=D.meta;
let cur=0, tab=0;

/* ── 校勘標記還原：⸢n⸣…⸤ ── */
function esc(s){return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');}
function mark(s){
  return esc(s)
    .replace(/\u2e22(\d+)\u2e23/g,'<span class="ap" data-i="$1">')
    .replace(/\u2e24/g,'<sup>校</sup></span>');
}
function plain(s){return s.replace(/[\u2e22\u2e24]|\u2e22\d+\u2e23/g,'').replace(/\u2e22\d+\u2e23/g,'');}

/* ── 渲染 ── */
function label(s){
  if(s.kind==='open')return '宗前敬序分';
  if(s.kind==='close')return '釋結施願分';
  const v=s.verses;
  return v.length>1?('頌'+v[0]+'–'+v[v.length-1]):('頌'+v[0]);
}
function ribbon(){
  document.getElementById('ribbon').innerHTML=S.map((s,i)=>
    '<button class="rc'+(i===cur?' on':'')+'" data-i="'+i+'"><span class="rn">'+
    label(s)+'</span>'+s.label+'</button>').join('');
}
function render(){
  const s=S[cur], m=document.getElementById('main');
  let h='<div class="sec-hd"><span class="eyebrow">'+label(s)+' · 卷'+s.juan.join('、')+
        '</span><h2>'+s.label+'</h2><div class="meta">本節 '+s.chars.toLocaleString()+
        ' 淨字'+(s.kepan.length?' · 科判 '+s.kepan.length+' 目':'')+'</div></div>';
  if(tab===0){
    let lastJ=null;
    s.blocks.forEach(b=>{
      if(b.juan&&b.juan!==lastJ){h+='<div class="jm">卷第'+cn(b.juan)+'</div>';lastJ=b.juan;}
      if(b.t==='k')h+='<div class="k lv'+b.lv+'">'+esc(b.text)+'</div>';
      else if(b.t==='j')h+='<div class="jt">'+mark(b.text)+'</div>';
      else if(b.t==='by')h+='<p class="by">'+mark(b.text)+'</p>';
      else if(b.t==='h')h+='<div class="hh">'+mark(b.text)+'</div>';
      else if(b.t==='dn')h+='<div class="jt">'+esc(b.text)+'</div>';
      else if(b.t==='p')h+='<p class="t">'+mark(b.text)+'</p>';
      else if(b.t==='v')h+='<div class="vs">'+(b.num?'<span class="vn">頌 '+b.num+
        (D.stages[b.num]?' · '+D.stages[b.num]:'')+'</span>':'')+
        '<p class="vl">'+b.lines.map(mark).join('<br>')+'</p></div>';
    });
  }else if(tab===1){
    h+='<div class="card"><h3>頌旨語譯</h3><p>'+esc(s.yi)+'</p></div>';
    if(s.verses.length)h+='<div class="card"><h3>本節所釋頌文</h3>'+
      s.blocks.filter(b=>b.t==='v'&&b.num).map(b=>'<p style="margin-bottom:10px">'+
      '<b>'+b.num+'</b>　'+b.lines.map(x=>esc(plain(x))).join('／')+'</p>').join('')+'</div>';
  }else if(tab===2){
    h+='<div class="card"><h3>要義提點</h3><ol class="yao">'+
      s.yao.map(x=>'<li>'+esc(x)+'</li>').join('')+'</ol></div>';
    (s.tables||[]).forEach(t=>{
      h+='<div class="card"><h3>'+esc(t.title)+'</h3>'+
         (t.note?'<p class="tnote">'+esc(t.note)+'</p>':'')+
         '<div class="twrap"><table class="tbl"><thead><tr>'+
         t.cols.map(c=>'<th>'+esc(c)+'</th>').join('')+'</tr></thead><tbody>'+
         t.rows.map(r=>'<tr>'+r.map(x=>'<td>'+esc(x)+'</td>').join('')+'</tr>').join('')+
         '</tbody></table></div></div>';
    });
    if(s.kepan.length)h+='<div class="card"><h3>本節科判</h3><p style="font-size:14.5px;'+
      'color:#4a5060">'+s.kepan.map(esc).join('　·　')+'</p></div>';
  }else{
    h+='<div class="card"><h3>本節名相</h3><dl class="ming">'+
      s.ming.map(x=>'<dt>'+esc(x[0])+'</dt><dd>'+esc(x[1])+'</dd>').join('')+'</dl></div>';
    h+='<div class="card"><h3>通論綱目</h3><dl class="ming">'+
      D.general.map(x=>'<dt>'+esc(x[0])+'</dt><dd>'+esc(x[1])+'</dd>').join('')+'</dl></div>';
  }
  m.innerHTML=h;
  document.getElementById('pos').textContent=(cur+1)+' / '+S.length;
  ribbon();
  const on=document.querySelector('.rc.on'); if(on)on.scrollIntoView({inline:'center',block:'nearest'});
  window.scrollTo(0,0);
  stop();
}
function cn(n){const a='〇一二三四五六七八九十';return n===10?'十':a[n];}

/* ── 導覽 ── */
function go(d){cur=Math.min(S.length-1,Math.max(0,cur+d));render();}
function jump(i){cur=i;render();closeAll();}
document.getElementById('ribbon').onclick=e=>{const b=e.target.closest('.rc');if(b)jump(+b.dataset.i);};
document.getElementById('tabs').onclick=e=>{const b=e.target.closest('.tb');if(!b)return;
  tab=+b.dataset.t;document.querySelectorAll('.tb').forEach(x=>x.classList.toggle('on',x===b));render();};
document.getElementById('main').onclick=e=>{const a=e.target.closest('.ap');if(!a)return;
  const en=D.app[+a.dataset.i], p=document.getElementById('pop');
  p.innerHTML='<div class="pt">校勘異文 · 第 '+(+a.dataset.i+1)+' 則</div><b>'+esc(en.lem)+
    '</b>　'+en.lw.join('')+'<div class="wit">'+en.rdg.map(r=>esc(r.t)+'　'+r.w.join('')).join('<br>')+
    '</div>';p.classList.add('on');};

/* ── 抽屜 ── */
function tog(id){const el=document.getElementById(id),o=el.classList.contains('on');
  closeAll();
  if(!o){el.classList.add('on');
    if(id==='toc')document.getElementById('scrim').classList.add('on');
    if(id==='chat'){if(!conv()&&!mem.convs.length)newConv();else paint();}}}
function closeAll(){['toc','chat'].forEach(i=>document.getElementById(i).classList.remove('on'));
  document.getElementById('scrim').classList.remove('on');
  const m=document.getElementById('menu');if(m)closeMenu();}

/* ── 版本註記 ── */
function showMeta(){
  const st=D.stats;
  document.getElementById('mbox').innerHTML='<h2>版本註記</h2><dl>'+
   '<dt>底本</dt><dd>'+M.canon+'　'+M.extent+'</dd>'+
   '<dt>撰譯</dt><dd>'+M.author+'　'+M.translator+'</dd>'+
   '<dt>根本頌</dt><dd>'+M.root_text+'</dd>'+
   '<dt>語料</dt><dd>'+M.base_text+'</dd>'+
   '<dt>標點</dt><dd>'+M.punctuation+'</dd>'+
   '<dt>對校本</dt><dd>'+M.witnesses.join('　')+'（共 '+M.witnesses.length+' 本，校勘 '+st.app+' 則）</dd>'+
   '<dt>缺字</dt><dd>CBETA 造字 '+st.gaiji+' 字，其中 '+st.unresolved.length+
     ' 字無 Unicode 對映（'+st.unresolved.map(u=>u.id+'　'+u.comp).join('；')+'），以組字式呈現。</dd>'+
   '<dt>全文字數</dt><dd>'+st.net.toLocaleString()+' 淨字（不含標點與校注）</dd>'+
   '<dt>科判</dt><dd>'+M.framework+'</dd>'+
   '<dt>註疏</dt><dd>'+M.commentary_ref+'</dd>'+
   '<dt>授權</dt><dd>'+M.license.code+'<br>'+M.license.text+'</dd>'+
   '<dt>版本</dt><dd>'+M.version+'<br>'+M.changelog.map(esc).join('<br>')+'</dd></dl>'+
   '<div class="warn"><b>待考證</b>　'+M.provenance_note.replace(/\*\*/g,'')+'</div>'+
   '<div class="warn"><b>語料事實</b>　'+M.corpus_note+'</div>'+
   (D.orphan.length?'<div class="warn"><b>題記校勘</b>　下列 '+D.orphan.length+
     ' 則校勘位於卷首譯者題名或卷末題記，非論文正文，故不隨文標示，於此另列：'+
     D.orphan.map(o=>'第 '+o.i+' 則　'+esc(o.lem)+o.lw.join('')+' → '+
       o.rdg.map(r=>esc(r.t)+r.w.join('')).join('、')).join('；')+'</div>':'');
  document.getElementById('modal').classList.add('on');
}

/* ── 目錄三軸 ── */
function buildToc(){
  const jm={}; S.forEach((s,i)=>s.juan.forEach(j=>{(jm[j]=jm[j]||[]).push(i)}));
  document.getElementById('axJuan').innerHTML=Object.keys(jm).sort((a,b)=>a-b)
    .map(j=>'<button onclick="jump('+jm[j][0]+')">卷'+cn(+j)+'</button>').join('');
  let v='';for(let n=1;n<=30;n++)v+='<button onclick="jump('+D.verseIndex[n]+')">'+n+
    (D.stages[n]?'　'+D.stages[n]:'')+'</button>';
  document.getElementById('axVerse').innerHTML=v;
  document.getElementById('axKepan').innerHTML=D.kepan.map(k=>
    '<button class="l'+k.lv+'" onclick="jump('+k.sec+')">'+esc(k.text)+'</button>').join('');
}

/* ── 朗讀：句佇列 + Chrome 續播心跳 ── */
let queue=[],qi=0,speaking=false,beat=null;
function chunks(text){
  const out=[];let buf='';
  const parts=text.replace(/([。！？；：])/g,'$1\u0001').split('\u0001');
  parts.forEach(p=>{p=p.trim();if(!p)return;
    if((buf+p).length>55){if(buf)out.push(buf);
      while(p.length>55){out.push(p.slice(0,55));p=p.slice(55);}buf=p;}
    else buf+=p;});
  if(buf)out.push(buf);return out;
}
function collect(){
  const s=S[cur],t=[];
  if(tab===0)s.blocks.forEach(b=>{if(b.t==='p'||b.t==='h')t.push(plain(b.text));
    else if(b.t==='v')t.push(b.lines.map(plain).join('，'));});
  else if(tab===1)t.push(s.yi);
  else if(tab===2)s.yao.forEach(x=>t.push(x));
  else s.ming.forEach(x=>t.push(x[0]+'。'+x[1]));
  return chunks(t.join(''));
}
function tts(){
  if(speaking){stop();return;}
  if(!('speechSynthesis' in window)){alert('此瀏覽器不支援語音朗讀');return;}
  queue=collect();qi=0;speaking=true;
  document.getElementById('hdrTts').classList.add('on');
  beat=setInterval(()=>{if(speaking)speechSynthesis.resume();},6000);
  next();
}
function next(){
  if(!speaking||qi>=queue.length){stop();return;}
  const u=new SpeechSynthesisUtterance(queue[qi++]);
  u.lang='zh-TW';u.rate=.92;u.onend=next;u.onerror=stop;
  speechSynthesis.speak(u);
}
function stop(){speaking=false;queue=[];qi=0;if(beat){clearInterval(beat);beat=null;}
  if('speechSynthesis' in window)speechSynthesis.cancel();
  const b=document.getElementById('hdrTts');if(b)b.classList.remove('on');
  document.querySelectorAll('.msg .tools button').forEach(x=>x.classList.remove('on'));}

/* ── 問答：紀錄・收藏・專案・分享・語音（需自架 proxy） ── */
const PROXY="";   // 例：https://your-worker.workers.dev/v1/messages
const KEY='cwsl-chat-v1';
let mem={convs:[],projects:['未歸專案'],cur:null,onlyStar:false};
function load(){try{const r=localStorage.getItem(KEY);if(r)mem=JSON.parse(r);}catch(e){}
  if(!mem.projects||!mem.projects.length)mem.projects=['未歸專案'];
  if(!mem.convs)mem.convs=[];}
function save(){try{localStorage.setItem(KEY,JSON.stringify(mem));}catch(e){}}
function conv(){return mem.convs.find(c=>c.id===mem.cur)||null;}
function newConv(){
  const c={id:'c'+Date.now(),title:'新對話',project:mem.projects[0],
    star:false,ts:Date.now(),msgs:[]};
  mem.convs.unshift(c);mem.cur=c.id;save();closeMenu();paint();
  document.getElementById('q').focus();
}
function ensure(){if(!conv()){newConv();}return conv();}
function delConv(){
  const c=conv();if(!c)return;
  if(!confirm('刪除「'+c.title+'」？此對話將無法復原。'))return;
  mem.convs=mem.convs.filter(x=>x.id!==c.id);
  mem.cur=mem.convs.length?mem.convs[0].id:null;save();closeMenu();paint();
}
function renameConv(){const c=ensure();const t=prompt('對話名稱',c.title);
  if(t&&t.trim()){c.title=t.trim();save();paint();}}
function togStar(id){const c=mem.convs.find(x=>x.id===id);if(!c)return;
  c.star=!c.star;save();renderMenu();}
function togStarred(){mem.onlyStar=!mem.onlyStar;save();renderMenu();}
function newProject(){const p=prompt('新增專案名稱','');
  if(p&&p.trim()&&mem.projects.indexOf(p.trim())<0){mem.projects.push(p.trim());
    const c=ensure();c.project=p.trim();save();renderMenu();paint();}}
function pickProject(){const c=ensure();
  const n=prompt('歸入專案（現有：'+mem.projects.join('、')+'）',c.project);
  if(n&&n.trim()){if(mem.projects.indexOf(n.trim())<0)mem.projects.push(n.trim());
    c.project=n.trim();save();paint();renderMenu();}}
function openConv(id){mem.cur=id;save();closeMenu();paint();}
function share(){
  const c=conv();
  if(!c||!c.msgs.length){alert('這個對話還沒有內容可以分享。');return;}
  const txt='《成唯識論》線上讀本 · '+c.title+'\n'+M.canonical+'\n\n'+
    c.msgs.map(m=>(m.role==='user'?'問：':'答：')+m.text).join('\n\n');
  if(navigator.share){navigator.share({title:'成唯識論 · '+c.title,text:txt})
    .catch(()=>{});return;}
  if(navigator.clipboard){navigator.clipboard.writeText(txt)
    .then(()=>alert('已複製對話內容，可貼上分享。'))
    .catch(()=>alert('複製失敗，請手動選取內容。'));return;}
  alert('此瀏覽器不支援分享，請手動選取內容。');
}
function togMenu(){const m=document.getElementById('menu');
  const on=!m.classList.contains('on');
  m.classList.toggle('on',on);document.getElementById('hamb').classList.toggle('on',on);
  if(on)renderMenu();}
function closeMenu(){document.getElementById('menu').classList.remove('on');
  document.getElementById('hamb').classList.remove('on');}
function renderMenu(){
  const st=document.getElementById('starTgl');
  st.classList.toggle('on',mem.onlyStar);
  st.querySelector('b').textContent=mem.onlyStar?'開':'關';
  const list=mem.convs.filter(c=>!mem.onlyStar||c.star);
  document.getElementById('convList').innerHTML=list.length?list.map(c=>
    '<div class="conv'+(c.id===mem.cur?' on':'')+'">'+
    '<button class="cn" onclick="openConv(\''+c.id+'\')">'+esc(c.title)+
    '<small>'+esc(c.project)+' · '+c.msgs.length+' 則 · '+
    new Date(c.ts).toLocaleDateString('zh-TW')+'</small></button>'+
    '<button class="st'+(c.star?' on':'')+'" onclick="togStar(\''+c.id+'\')" '+
    'aria-label="收藏">'+(c.star?'★':'☆')+'</button>'+
    '<button class="rm" onclick="rmConv(\''+c.id+'\')" aria-label="刪除">×</button></div>'
  ).join(''):'<div class="empty">'+(mem.onlyStar?'還沒有收藏的對話。':
    '還沒有對話紀錄。點「開新對話」開始。')+'</div>';
  const byP={};mem.projects.forEach(p=>byP[p]=0);
  mem.convs.forEach(c=>{byP[c.project]=(byP[c.project]||0)+1;});
  document.getElementById('projList').innerHTML=Object.keys(byP).map(p=>
    '<button class="mi tgl" onclick="pickProjectTo(\''+p.replace(/'/g,"\\'")+'\')">'+
    esc(p)+'<b>'+byP[p]+' 則</b></button>').join('');
}
function rmConv(id){const c=mem.convs.find(x=>x.id===id);if(!c)return;
  if(!confirm('刪除「'+c.title+'」？'))return;
  mem.convs=mem.convs.filter(x=>x.id!==id);
  if(mem.cur===id)mem.cur=mem.convs.length?mem.convs[0].id:null;
  save();renderMenu();paint();}
function pickProjectTo(p){const c=ensure();c.project=p;save();paint();renderMenu();}

function paint(){
  const c=conv();
  document.getElementById('convTtl').innerHTML=c?
    esc(c.title)+'<small>'+esc(c.project)+'</small>':'新對話<small>未歸專案</small>';
  const l=document.getElementById('log');
  if(!c||!c.msgs.length){
    l.innerHTML='<div class="empty">就當前節次「'+esc(S[cur].label)+
      '」提問，回答僅依本節論文，不臆補。</div>';return;}
  l.innerHTML=c.msgs.map((m,i)=>'<div class="msg '+(m.role==='user'?'u':'a')+'">'+
    '<span class="who">'+(m.role==='user'?'提問':'回答')+'</span>'+
    '<div class="bd">'+esc(m.text)+'</div>'+
    (m.role==='user'?'':'<div class="tools"><button onclick="speak('+i+',this)">朗讀</button>'+
     '<button onclick="copyMsg('+i+')">複製</button></div>')+'</div>').join('');
  l.scrollTop=l.scrollHeight;
}
function copyMsg(i){const c=conv();if(!c)return;
  if(navigator.clipboard)navigator.clipboard.writeText(c.msgs[i].text)
    .then(()=>alert('已複製。'));}
function speak(i,btn){
  const c=conv();if(!c)return;
  if(speaking){stop();document.querySelectorAll('.tools button').forEach(x=>x.classList.remove('on'));return;}
  if(!('speechSynthesis' in window)){alert('此瀏覽器不支援語音朗讀');return;}
  queue=chunks(c.msgs[i].text);qi=0;speaking=true;btn.classList.add('on');
  beat=setInterval(()=>{if(speaking)speechSynthesis.resume();},6000);next();
}

/* 語音輸入 */
let rec=null,listening=false;
function mic(){
  const SR=window.SpeechRecognition||window.webkitSpeechRecognition;
  if(!SR){alert('此瀏覽器不支援語音輸入，請改用鍵盤。');return;}
  const btn=document.getElementById('micBtn');
  if(listening){rec.stop();return;}
  rec=new SR();rec.lang='zh-TW';rec.interimResults=true;rec.continuous=false;
  const box=document.getElementById('q');const base=box.value;
  rec.onstart=()=>{listening=true;btn.classList.add('on');
    box.placeholder='聆聽中…';};
  rec.onresult=e=>{let t='';for(let i=0;i<e.results.length;i++)t+=e.results[i][0].transcript;
    box.value=(base?base+' ':'')+t;};
  rec.onerror=e=>{box.placeholder=e.error==='not-allowed'?
    '需要麥克風權限才能語音輸入':'語音輸入失敗，請改用鍵盤';};
  rec.onend=()=>{listening=false;btn.classList.remove('on');
    box.placeholder='就本節論文提問…';};
  rec.start();
}

async function ask(){
  const box=document.getElementById('q'),q=box.value.trim();if(!q)return;
  const c=ensure();box.value='';
  c.msgs.push({role:'user',text:q});
  if(c.title==='新對話')c.title=q.slice(0,18)+(q.length>18?'…':'');
  c.ts=Date.now();save();paint();
  if(!PROXY){
    c.msgs.push({role:'assistant',text:'問答端點尚未設定。請將原始碼中的 PROXY 常數指向自架的 '+
      'API 轉送端點；GitHub Pages 無法自瀏覽器直接呼叫 Anthropic API（CORS 限制）。\n'+
      '在此之前，紀錄、收藏、專案與分享功能均可正常使用。'});
    save();paint();return;}
  const s=S[cur];
  const ctx='【本節】'+s.label+'（'+label(s)+'）\n'+
    s.blocks.filter(b=>b.t==='p'||b.t==='v'||b.t==='h').map(b=>b.t==='v'?
      b.lines.map(plain).join(''):plain(b.text)).join('').slice(0,6000);
  c.msgs.push({role:'assistant',text:'…'});paint();
  try{
    const r=await fetch(PROXY,{method:'POST',headers:{'Content-Type':'application/json'},
      body:JSON.stringify({model:'claude-sonnet-4-6',max_tokens:1000,
        system:'你是《成唯識論》讀本的隨文問答助理。僅依所附論文回答，'+
          '論文未載者明言「本節未載」，不得臆補。以繁體中文作答，術語用唯識學標準譯名。',
        messages:c.msgs.filter(m=>m.text!=='…').map((m,i)=>({role:m.role,
          content:i===0?ctx+'\n\n【提問】'+m.text:m.text}))})});
    const j=await r.json();
    const t=(j.content||[]).filter(x=>x.type==='text').map(x=>x.text).join('\n')||'（無回應）';
    c.msgs[c.msgs.length-1].text=t;
  }catch(e){c.msgs[c.msgs.length-1].text='連線失敗：'+e.message;}
  save();paint();
}

/* ── 啟動 ── */
function enter(){document.getElementById('cover').classList.add('gone');}
document.getElementById('coverNote').innerHTML=
  '底本：大正新脩大藏經 T31 no.1585 · 語料：CBETA XML TEI-P5，限非商業用途<br>'+
  '分節：世親《唯識三十頌》三十頌，合為二十頌組，另立序分、結分<br>'+
  '科判：CBETA cb:mulu 六級一百目（來源待考證）<br>'+
  M.version+' · 全文 '+D.stats.net.toLocaleString()+' 淨字 · 校勘 '+D.stats.app+
  ' 則 · 語譯、要義、名相二十二節俱全';
document.getElementById('chat').addEventListener('click',e=>{
  const m=document.getElementById('menu');
  if(m.classList.contains('on')&&!m.contains(e.target)&&
     !document.getElementById('hamb').contains(e.target))closeMenu();});
document.getElementById('q').addEventListener('keydown',e=>{
  if(e.key==='Enter'&&(e.metaKey||e.ctrlKey)){e.preventDefault();ask();}});
document.getElementById('chNotice').textContent=
  '僅就當前節次論文作答。紀錄、收藏與專案存於本機瀏覽器，不上傳；'+
  '部署於 GitHub Pages 時須自備 API 轉送端點，瀏覽器無法直接呼叫 Anthropic API。';
load();buildToc();render();paint();
document.addEventListener('keydown',e=>{if(e.key==='ArrowLeft')go(-1);
  if(e.key==='ArrowRight')go(1);if(e.key==='Escape'){const mm=document.getElementById('menu');
  if(mm.classList.contains('on')){closeMenu();return;}
  closeAll();
  document.getElementById('modal').classList.remove('on');
  document.getElementById('pop').classList.remove('on');}});
</script>
</body>
</html>
"""

html = TPL.replace('__DATA__', json.dumps(DATA, ensure_ascii=False,
                                          separators=(',', ':')))
html = html.replace('__CANON__', META['canonical'])

os.makedirs(os.path.dirname(OUT), exist_ok=True)
open(OUT, 'w', encoding='utf-8').write(html)

# ---- 輸出前驗證 ----
size = os.path.getsize(OUT) / 1024
errs = []
if '__DATA__' in html or '__CANON__' in html:
    errs.append('模板佔位未替換')
for s in data_sections:
    if not s['yi'] or not s['yao'] or not s['ming']:
        errs.append('第 %d 節撰述層不全' % s['id'])
if len(data_sections) != 22:
    errs.append('分節數異常')
vs = sorted(verse_index)
if vs != list(range(1, 31)):
    errs.append('三十頌對映不全')
marks = len(re.findall(r'\u2e22\d+\u2e23', html))
print('輸出:', OUT, '%.1f KB' % size)
ntab = sum(len(s['tables']) for s in data_sections)
nrow = sum(len(t['rows']) for s in data_sections for t in s['tables'])
print('對照表 %d 個 / %d 列' % (ntab, nrow))
print('分節 %d · 頌對映 %d · 校勘標記 %d / 條目 %d'
      % (len(data_sections), len(vs), marks, len(app)))
print('驗證:', '、'.join(errs) if errs else 'PASS')
