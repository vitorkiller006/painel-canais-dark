# -*- coding: utf-8 -*-
"""
===============================================================================
DARK FACTORY CLOUD ENGINE — PAINEL MASTER ANALYTICS (MULTI-CANAL YOUTUBE STUDIO)
ARQUIVO: painel_template.py
===============================================================================
Módulos:
1. ⚡ Radar ao Vivo (60m / 48h / Recentes com filtros e Top 3)
2. 📈 Gráficos & Histórico (Time-Series 30 dias de Views, Inscritos e Origens de Tráfego via Chart.js)
3. 🎯 Lançamentos "1 de 10" (Desempenho Relativo do Último Vídeo vs 10 Anteriores)
4. ⚡ Velocímetro de Ritmo VPH (Views Por Hora em tempo real por canal e consolidado)
5. 📅 Calendário de Estreias (Fila unificada de vídeos agendados)
===============================================================================
"""

import json
import html as htmllib
from datetime import timezone, timedelta

MIN_VIEWS_FOR_RETENTION_RANK = 10


def _e(s):
    return htmllib.escape(str(s if s is not None else ""), quote=True)


CSS = """
:root{
  --bg:#090D16;
  --surface:#111827;
  --surface-2:#1E293B;
  --surface-3:#273549;
  --border:rgba(255,255,255,.09);
  --border-hi:rgba(56,189,248,.35);
  --text:#F8FAFC;
  --muted:#94A3B8;
  --cyan:#38BDF8;
  --green:#10B981;
  --amber:#F59E0B;
  --red:#F43F5E;
  --purple:#C084FC;
}
*{box-sizing:border-box;margin:0;padding:0}
html{-webkit-text-size-adjust:100%}
body{background:var(--bg);color:var(--text);font-family:'Inter',system-ui,-apple-system,sans-serif;line-height:1.4;padding:16px}
.wrap{max-width:1440px;margin:0 auto}
a{color:inherit;text-decoration:none}
.num,.mono{font-family:'JetBrains Mono',monospace}

/* Topbar */
.topbar{background:var(--surface);border:1px solid var(--border);border-radius:14px;padding:14px 18px;margin-bottom:14px}
.topbar-main{display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:12px}
.topbar h1{font-size:18px;font-weight:800;display:flex;align-items:center;gap:8px}
.topbar .meta{font-size:12px;color:var(--muted);margin-top:4px}
.topbar .meta b{color:var(--text)}
.vph-badge{display:inline-flex;align-items:center;gap:6px;background:rgba(56,189,248,.12);border:1px solid var(--border-hi);color:var(--cyan);padding:4px 10px;border-radius:999px;font-size:12px;font-weight:700}

/* Navegação Principal (Tabs) */
.main-nav{display:flex;gap:8px;background:var(--surface);border:1px solid var(--border);border-radius:14px;padding:6px;margin-bottom:14px;overflow-x:auto;-webkit-overflow-scrolling:touch;scrollbar-width:none}
.main-nav::-webkit-scrollbar{display:none}
.nav-tab{flex:1;min-width:130px;background:transparent;color:var(--muted);border:0;border-radius:10px;padding:10px 14px;font-size:13px;font-weight:700;cursor:pointer;white-space:nowrap;transition:all .15s}
.nav-tab:hover{color:var(--text);background:var(--surface-2)}
.nav-tab.active{background:var(--cyan);color:#090D16;box-shadow:0 2px 8px rgba(56,189,248,.25)}

/* Filtro por Grupo */
.chips{display:flex;gap:8px;margin-top:12px;overflow-x:auto;-webkit-overflow-scrolling:touch;scrollbar-width:none}
.chips::-webkit-scrollbar{display:none}
.chip{flex:0 0 auto;background:var(--surface-2);color:var(--text);border:1px solid var(--border);padding:8px 14px;border-radius:999px;font-size:12px;font-weight:600;cursor:pointer;min-height:36px;white-space:nowrap}
.chip.active{background:var(--cyan);color:#090D16;border-color:var(--cyan)}

/* Sections */
.tab-content{display:none}
.tab-content.active{display:block}
.sec{background:var(--surface);border:1px solid var(--border);border-radius:14px;padding:14px 16px;margin-bottom:14px}
.sec-title{font-size:16px;font-weight:700}
.sec-hint{font-size:12px;color:var(--muted);margin-top:3px}
.sec-top{display:flex;justify-content:space-between;align-items:flex-end;gap:10px;flex-wrap:wrap;margin-bottom:12px}

/* Segmented sort */
.seg{display:flex;background:var(--surface-2);border:1px solid var(--border);border-radius:12px;padding:3px;gap:3px;width:100%;max-width:460px}
.seg button{flex:1;background:transparent;color:var(--muted);border:0;border-radius:9px;padding:9px 6px;font-size:12px;font-weight:700;cursor:pointer;min-height:38px}
.seg button.active{background:var(--cyan);color:#090D16}
.lv-count{font-size:12px;color:var(--muted);margin:10px 2px 6px}

/* Live list */
.lv-row{display:grid;grid-template-columns:28px 96px 1fr auto;gap:12px;align-items:center;padding:10px 4px;border-top:1px solid rgba(255,255,255,.05)}
.lv-rank{font-family:'JetBrains Mono',monospace;font-weight:700;color:var(--muted);text-align:center;font-size:14px}
.lv-thumb{width:96px;height:54px;object-fit:cover;border-radius:8px;border:1px solid var(--border);background:#000}
.lv-info{min-width:0}
.lv-title{display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;font-size:14px;font-weight:600}
.lv-title:hover{color:var(--cyan)}
.lv-meta{font-size:11px;color:var(--muted);margin-top:4px;display:flex;flex-wrap:wrap;gap:6px;align-items:center}
.lv-metrics{display:flex;gap:6px}
.mt{background:var(--surface-2);border:1px solid var(--border);border-radius:10px;padding:6px 10px;min-width:74px;text-align:right}
.mt-lbl{display:block;font-size:10px;color:var(--muted);text-transform:uppercase;font-weight:600}
.mt-val{display:block;font-family:'JetBrains Mono',monospace;font-weight:700;font-size:14px}
.mt.pos .mt-val{color:var(--green)}
.mt.zero .mt-val{color:var(--muted)}
.mt.sel{border-color:var(--cyan);box-shadow:0 0 0 1px var(--cyan) inset}
.empty{text-align:center;color:var(--muted);font-style:italic;padding:22px 10px;font-size:13px}

/* Pills */
.pill{display:inline-block;font-size:10px;font-weight:700;padding:2px 8px;border-radius:999px;text-transform:uppercase;white-space:nowrap}
.pill-pessoal{background:rgba(56,189,248,.15);color:var(--cyan)}
.pill-gvg{background:rgba(192,132,252,.18);color:var(--purple)}
.pill-amber{background:rgba(245,158,11,.2);color:#FBBF24}
.pill-red{background:rgba(244,63,94,.2);color:var(--red)}
.pill-green{background:rgba(16,185,129,.18);color:var(--green)}
.pending{font-size:11px;color:var(--amber)}

/* Comparison table */
.tbl-wrap{overflow-x:auto}
table.cmp{width:100%;border-collapse:collapse;font-size:13px}
.cmp th{text-align:left;font-size:11px;text-transform:uppercase;color:var(--muted);padding:9px 10px;border-bottom:1px solid var(--border);white-space:nowrap}
.cmp td{padding:10px;border-bottom:1px solid rgba(255,255,255,.05);vertical-align:middle}
.cmp td.num{text-align:right;white-space:nowrap}
.cmp th.num{text-align:right}
.ch-name{font-weight:700}
.sub{font-size:11px;color:var(--muted)}

/* Channel cards Top 3 */
details.ch{background:var(--surface);border:1px solid var(--border);border-radius:14px;margin-bottom:12px;overflow:hidden}
details.ch.off{border-color:rgba(244,63,94,.4)}
details.ch>summary{list-style:none;cursor:pointer;padding:14px 16px;display:flex;justify-content:space-between;align-items:center;gap:10px;flex-wrap:wrap}
details.ch>summary::-webkit-details-marker{display:none}
details.ch>summary::after{content:'▾';color:var(--muted);font-size:16px;transition:transform .2s}
details.ch:not([open])>summary::after{transform:rotate(-90deg)}
.ch-head h3{font-size:16px;font-weight:700;margin-top:4px}
.ch-head small{display:block;font-size:12px;color:var(--muted);font-weight:400;margin-top:2px}
.ch-stats{display:flex;gap:14px;font-size:12px;color:var(--muted);flex-wrap:wrap}
.ch-stats b{color:var(--text);font-family:'JetBrains Mono',monospace}
.top3{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;padding:0 16px 16px}
.box{background:rgba(15,23,42,.65);border:1px solid var(--border);border-radius:10px;padding:12px}
.box h4{font-size:12px;font-weight:700;color:#E2E8F0;margin-bottom:8px;padding-bottom:6px;border-bottom:1px solid var(--border)}
.rk{display:flex;gap:8px;padding:7px 0;border-bottom:1px solid rgba(255,255,255,.04)}
.rk:last-child{border-bottom:0}
.rk .md{font-size:15px;line-height:1.2}
.rk .ri{flex:1;min-width:0}
.rk a{display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;font-size:12px;font-weight:500}
.rk a:hover{color:var(--cyan)}
.rk .rm{font-size:11px;color:var(--muted);margin-top:2px}
.hi{color:var(--cyan);font-weight:700;font-family:'JetBrains Mono',monospace}
.warn{color:var(--amber);font-size:10px;font-weight:600}
.empty-mini{font-size:11px;color:var(--muted);font-style:italic;padding:6px 0}
.off-msg{padding:0 16px 16px;font-size:13px;color:#FDA4AF}

/* MÓDULO 2: GRÁFICOS & HISTÓRICO */
.chart-card{background:var(--surface);border:1px solid var(--border);border-radius:14px;padding:16px;margin-bottom:14px}
.chart-head{display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:10px;margin-bottom:14px}
.chart-head h3{font-size:15px;font-weight:700}
.chart-box{position:relative;width:100%;height:260px}
.chart-grid{display:grid;grid-template-columns:2fr 1fr;gap:14px}
.kpi-row{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin-bottom:14px}
.kpi{background:var(--surface-2);border:1px solid var(--border);border-radius:12px;padding:12px;text-align:center}
.kpi-val{font-size:20px;font-weight:800;font-family:'JetBrains Mono',monospace;color:var(--cyan)}
.kpi-lbl{font-size:11px;color:var(--muted);text-transform:uppercase;margin-top:4px}
.ch-chips{display:flex;gap:6px;overflow-x:auto;-webkit-overflow-scrolling:touch;padding-bottom:4px;margin-bottom:12px}
.ch-chip{background:var(--surface-2);color:var(--text);border:1px solid var(--border);padding:6px 12px;border-radius:8px;font-size:12px;font-weight:600;cursor:pointer;white-space:nowrap}
.ch-chip.active{background:var(--cyan);color:#090D16;border-color:var(--cyan)}

/* MÓDULO 3: 1 DE 10 */
.rank10-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(330px,1fr));gap:14px}
.r10-card{background:var(--surface);border:1px solid var(--border);border-radius:14px;padding:16px;display:flex;flex-direction:column;justify-content:space-between}
.r10-head{display:flex;justify-content:space-between;align-items:flex-start;gap:10px;margin-bottom:12px}
.r10-ch-info h4{font-size:15px;font-weight:700}
.r10-ch-info .sub{font-size:11px;color:var(--muted)}
.r10-badge{padding:4px 10px;border-radius:999px;font-size:12px;font-weight:800;white-space:nowrap}
.r10-b1{background:rgba(16,185,129,.2);color:#34D399;border:1px solid rgba(16,185,129,.4)}
.r10-b2{background:rgba(56,189,248,.2);color:var(--cyan);border:1px solid rgba(56,189,248,.4)}
.r10-b3{background:rgba(245,158,11,.2);color:#FBBF24;border:1px solid rgba(245,158,11,.4)}
.r10-b4{background:rgba(244,63,94,.2);color:#FDA4AF;border:1px solid rgba(244,63,94,.4)}
.r10-body{display:flex;gap:12px;align-items:center;margin-bottom:12px}
.r10-thumb{width:110px;height:62px;object-fit:cover;border-radius:8px;border:1px solid var(--border);background:#000;flex-shrink:0}
.r10-vinfo{min-width:0}
.r10-vtitle{display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;font-size:13px;font-weight:600}
.r10-vtitle:hover{color:var(--cyan)}
.r10-metrics{background:var(--surface-2);border-radius:10px;padding:10px;font-size:12px;display:flex;justify-content:space-between}
.r10-metrics b{font-family:'JetBrains Mono',monospace;color:var(--text)}

/* MÓDULO 5: CALENDÁRIO DE ESTREIAS */
.cal-group{margin-bottom:18px}
.cal-date-title{font-size:14px;font-weight:800;color:var(--cyan);text-transform:uppercase;letter-spacing:.5px;margin-bottom:8px;padding-left:4px;display:flex;align-items:center;gap:6px}
.cal-row{display:grid;grid-template-columns:85px 120px 1fr;gap:12px;align-items:center;background:var(--surface);border:1px solid var(--border);border-radius:12px;padding:10px 14px;margin-bottom:8px}
.cal-time{font-family:'JetBrains Mono',monospace;font-weight:700;font-size:14px;color:var(--text)}
.cal-thumb{width:120px;height:68px;object-fit:cover;border-radius:8px;border:1px solid var(--border);background:#000}
.cal-info h4{font-size:14px;font-weight:600;margin-bottom:4px}

/* Responsive */
@media (max-width:1100px){
  .top3{grid-template-columns:repeat(2,1fr)}
  .chart-grid{grid-template-columns:1fr}
}
@media (max-width:720px){
  body{padding:10px}
  .topbar,.sec,.chart-card,.r10-card{padding:12px;border-radius:12px}
  .topbar h1{font-size:16px}
  .top3{grid-template-columns:1fr;padding:0 12px 12px}
  .kpi-row{grid-template-columns:1fr}
  .lv-row{grid-template-columns:22px 84px 1fr;grid-template-areas:"rank thumb info" "metrics metrics metrics";gap:8px 10px;padding:12px 0}
  .lv-rank{grid-area:rank;font-size:13px}
  .lv-thumb{grid-area:thumb;width:84px;height:47px}
  .lv-info{grid-area:info}
  .lv-metrics{grid-area:metrics;display:grid;grid-template-columns:repeat(3,1fr);gap:6px}
  .mt{min-width:0;text-align:center;padding:7px 4px}
  .mt-val{font-size:15px}

  /* Comparativo vira cards */
  table.cmp thead{display:none}
  table.cmp,table.cmp tbody,table.cmp tr,table.cmp td{display:block;width:100%}
  table.cmp tr{background:var(--surface-2);border:1px solid var(--border);border-radius:12px;padding:10px 12px;margin-bottom:10px}
  table.cmp td{border:0;padding:5px 0;display:flex;justify-content:space-between;align-items:center;gap:10px;text-align:right}
  table.cmp td::before{content:attr(data-label);font-size:11px;color:var(--muted);text-transform:uppercase;font-weight:600;text-align:left}
  table.cmp td.cell-ch{display:block;text-align:left;border-bottom:1px solid var(--border);padding-bottom:8px;margin-bottom:4px}
  table.cmp td.cell-ch::before{display:none}

  /* Calendário mobile */
  .cal-row{grid-template-columns:70px 90px 1fr;gap:8px;padding:8px 10px}
  .cal-thumb{width:90px;height:51px}
  .cal-time{font-size:12px}
  .cal-info h4{font-size:12px}
}
"""

JS = """
let curSort='d60', curGroup='all';
const EMPTY_MSG={
  d60:'Nenhum vídeo ganhou views na última medição (~60 min).',
  d48:'Nenhum vídeo ganhou views na janela de 48h medida até agora.',
  total:'Nenhum vídeo público com movimentação recente.'
};

function switchMainTab(tabId, btn){
  document.querySelectorAll('.nav-tab').forEach(b=>b.classList.remove('active'));
  document.querySelectorAll('.tab-content').forEach(c=>c.classList.remove('active'));
  if(btn) btn.classList.add('active');
  const target = document.getElementById('view-' + tabId);
  if(target) target.classList.add('active');
  if(tabId === 'charts' && window.initChartsOnce) window.initChartsOnce();
  const u = new URL(location.href);
  u.searchParams.set('tab', tabId);
  history.replaceState(null, '', u);
}

function applyLive(){
  const list=document.getElementById('lv-list');
  if(!list) return;
  const rows=[...list.querySelectorAll('.lv-row')];
  const groupRows=rows.filter(r=>curGroup==='all'||r.dataset.grupo===curGroup);
  const c60=groupRows.filter(r=>(+r.dataset.d60)>0).length;
  const c48=groupRows.filter(r=>(+r.dataset.d48)>0).length;
  const cTot=groupRows.length;
  const b60=document.getElementById('seg-d60');
  const b48=document.getElementById('seg-d48');
  const bTot=document.getElementById('seg-total');
  if(b60) b60.textContent='Últimos 60 min ('+c60+')';
  if(b48) b48.textContent='Últimas 48h ('+c48+')';
  if(bTot) bTot.textContent='Recentes ('+cTot+')';

  rows.sort((a,b)=>(+b.dataset[curSort])-(+a.dataset[curSort])||(+b.dataset.d48)-(+a.dataset.d48)||(+b.dataset.total)-(+a.dataset.total));
  let n=0;
  rows.forEach(r=>{
    list.appendChild(r);
    const okG=curGroup==='all'||r.dataset.grupo===curGroup;
    const okV=curSort==='total'||(+r.dataset[curSort])>0;
    const show=okG&&okV;
    r.style.display=show?'':'none';
    if(show){n++;r.querySelector('.lv-rank').textContent=n;}
    r.querySelectorAll('.mt').forEach(m=>m.classList.toggle('sel',m.dataset.k===curSort));
  });
  const em=document.getElementById('lv-empty');
  em.textContent=EMPTY_MSG[curSort];
  em.style.display=n?'none':'';
  document.getElementById('lv-count').textContent='Exibindo '+n+(n===1?' vídeo':' vídeos')+' ('+(curSort==='d60'?'mais vistos em 60 min':curSort==='d48'?'mais vistos em 48h':'total de views')+')';
}

function setSort(s,btn){
  curSort=s;
  document.querySelectorAll('.seg button').forEach(b=>b.classList.toggle('active',b===btn));
  applyLive();
}

function filterGroup(g,btn){
  curGroup=g;
  document.querySelectorAll('.chip').forEach(b=>b.classList.toggle('active',b===btn));
  document.querySelectorAll('[data-grupo]:not(.lv-row)').forEach(el=>{
    el.style.display=(g==='all'||el.dataset.grupo===g)?'':'none';
  });
  applyLive();
  const u=new URL(location.href);
  if(g==='all')u.searchParams.delete('grupo');else u.searchParams.set('grupo',g);
  history.replaceState(null,'',u);
}

// Chart.js Manager
let viewsChartInstance = null;
let trafficChartInstance = null;
let currentChartChannel = 'all';

function renderChannelCharts(chId){
  currentChartChannel = chId;
  document.querySelectorAll('.ch-chip').forEach(b=>b.classList.toggle('active', b.dataset.ch===chId));
  const raw = window.CHANNELS_TIMESERIES || {};
  let days = [], views = [], subs = [], traffic = {};
  
  if(chId === 'all'){
    // Agregação consolidada
    const dayMap = {}, subMap = {}, trafMap = {};
    Object.values(raw).forEach(ch=>{
      (ch.history_30d || []).forEach(h=>{
        dayMap[h.day] = (dayMap[h.day] || 0) + (h.views || 0);
        subMap[h.day] = (subMap[h.day] || 0) + (h.net_subs || 0);
      });
      (ch.traffic_sources_30d || []).forEach(t=>{
        trafMap[t.label] = (trafMap[t.label] || 0) + (t.views || 0);
      });
    });
    days = Object.keys(dayMap).sort();
    views = days.map(d=>dayMap[d]);
    subs = days.map(d=>subMap[d]);
    traffic = trafMap;
  } else if(raw[chId]){
    const ch = raw[chId];
    (ch.history_30d || []).forEach(h=>{
      days.push(h.day);
      views.push(h.views || 0);
      subs.push(h.net_subs || 0);
    });
    (ch.traffic_sources_30d || []).forEach(t=>{
      traffic[t.label] = (traffic[t.label] || 0) + (t.views || 0);
    });
  }

  const totV = views.reduce((a,b)=>a+b, 0);
  const totS = subs.reduce((a,b)=>a+b, 0);
  const topTr = Object.entries(traffic).sort((a,b)=>b[1]-a[1])[0] || ['—', 0];

  const kv = document.getElementById('kpi-views-30d');
  const ks = document.getElementById('kpi-subs-30d');
  const kt = document.getElementById('kpi-top-traffic');
  if(kv) kv.textContent = totV.toLocaleString('pt-BR');
  if(ks) ks.textContent = (totS >= 0 ? '+' : '') + totS.toLocaleString('pt-BR');
  if(kt) kt.textContent = topTr[0];

  // Render Views Line Chart
  const ctxV = document.getElementById('chartViews');
  if(ctxV && window.Chart){
    if(viewsChartInstance) viewsChartInstance.destroy();
    viewsChartInstance = new Chart(ctxV, {
      type: 'line',
      data: {
        labels: days.map(d=>d.slice(5)),
        datasets: [{
          label: 'Views Diárias',
          data: views,
          borderColor: '#38BDF8',
          backgroundColor: 'rgba(56,189,248,0.12)',
          fill: true,
          tension: 0.35,
          borderWidth: 2.5,
          pointRadius: 3,
          pointBackgroundColor: '#38BDF8'
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          x: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#94A3B8', font: { size: 10 } } },
          y: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#94A3B8', font: { size: 10 } } }
        }
      }
    });
  }

  // Render Traffic Doughnut
  const ctxT = document.getElementById('chartTraffic');
  if(ctxT && window.Chart){
    if(trafficChartInstance) trafficChartInstance.destroy();
    const tLabels = Object.keys(traffic);
    const tData = Object.values(traffic);
    trafficChartInstance = new Chart(ctxT, {
      type: 'doughnut',
      data: {
        labels: tLabels,
        datasets: [{
          data: tData,
          backgroundColor: ['#38BDF8','#10B981','#A855F7','#F59E0B','#F43F5E','#E2E8F0','#64748B','#3B82F6'],
          borderWidth: 0
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { position: 'bottom', labels: { color: '#94A3B8', boxWidth: 10, font: { size: 10 } } }
        }
      }
    });
  }
}

window.initChartsOnce = function(){
  if(window.Chart && !viewsChartInstance){
    renderChannelCharts('all');
  }
};

window.addEventListener('DOMContentLoaded',()=>{
  if(window.matchMedia('(max-width:720px)').matches){
    document.querySelectorAll('details.ch').forEach((d,i)=>{if(i>0)d.removeAttribute('open');});
  }
  const rows=[...document.querySelectorAll('.lv-row')];
  const has60=rows.some(r=>(+r.dataset.d60)>0);
  const has48=rows.some(r=>(+r.dataset.d48)>0);
  if(!has60 && has48){
    curSort='d48';
    document.querySelectorAll('.seg button').forEach(b=>b.classList.toggle('active',b.id==='seg-d48'));
  }
  const params = new URLSearchParams(location.search);
  const g = params.get('grupo');
  if(g==='gvg'||g==='pessoal') filterGroup(g, document.getElementById('chip-'+g));
  else applyLive();

  const tab = params.get('tab');
  if(tab && document.getElementById('btn-tab-' + tab)){
    switchMainTab(tab, document.getElementById('btn-tab-' + tab));
  }
});
"""


def _metric(label, key, value_txt, positive):
    cls = "pos" if positive else "zero"
    return f'<div class="mt {cls}" data-k="{key}"><span class="mt-lbl">{label}</span><span class="mt-val">{value_txt}</span></div>'


def render_html(channels_data, generated_at, all_scheduled=None):
    now_brt = generated_at.astimezone(timezone(timedelta(hours=-3)))
    now_str = now_brt.strftime("%d/%m/%Y %H:%M")
    online = sum(1 for c in channels_data if c.get("status_conexao") == "ONLINE")
    total_ch = len(channels_data)
    n_pessoal = sum(1 for c in channels_data if c.get("grupo_slug") == "pessoal")
    n_gvg = sum(1 for c in channels_data if c.get("grupo_slug") == "gvg")
    win = max((c.get("snapshot_window_hours", 0.0) for c in channels_data), default=0.0)
    win_48_txt = f"{min(win, 48.0):.1f}h de 48h medidas" if win < 48 else "48h completas"

    total_vph_60m = sum(c.get("vph_60m", 0) for c in channels_data)
    total_sched_count = len(all_scheduled) if all_scheduled else sum(c.get("total_videos_agendados", 0) for c in channels_data)

    # 1. RADAR AO VIVO
    live = [v for c in channels_data for v in c.get("videos_ao_vivo_movimento", [])]
    live_html = []
    for v in live[:150]:
        d60 = v.get("delta_60m")
        d48 = v.get("delta_48h") or 0
        tot = v.get("views_total") or 0
        d60_num = d60 if d60 is not None else 0
        d60_txt = f"+{d60:,}" if d60 is not None else "—"
        badge = '<span class="pill pill-amber">novo &lt;48h</span>' if v.get("is_pub_last_48h") else ""
        live_html.append(f"""
<div class="lv-row" data-grupo="{v['grupo_slug']}" data-d60="{d60_num}" data-d48="{d48}" data-total="{tot}">
  <div class="lv-rank">·</div>
  <img class="lv-thumb" src="{_e(v.get('thumbnail'))}" alt="" loading="lazy">
  <div class="lv-info">
    <a class="lv-title" href="{_e(v['url'])}" target="_blank" rel="noopener">{_e(v['title'])}</a>
    <div class="lv-meta"><span class="pill pill-{v['grupo_slug']}">{_e(v['canal_titulo'])}</span><span>{_e(v.get('published_formatted'))}</span>{badge}</div>
  </div>
  <div class="lv-metrics">
    {_metric('60 min', 'd60', d60_txt, d60_num > 0)}
    {_metric('48h', 'd48', f'+{d48:,}', d48 > 0)}
    {_metric('Total', 'total', f'{tot:,}', False)}
  </div>
</div>""")

    # 2. COMPARATIVO
    cmp_rows = []
    for c in channels_data:
        on = c.get("status_conexao") == "ONLINE"
        st = '<span class="pill pill-green">online</span>' if on else f'<span class="pill pill-red">{_e(c.get("status_conexao"))}</span>'
        impr = f"{c.get('impressions_7d_canal'):,}" if c.get("impressions_7d_canal") is not None else '<span class="pending">⏳ aguardando Google</span>'
        ctr = f"<b>{c.get('ctr_7d_canal'):.2f}%</b>" if c.get("ctr_7d_canal") is not None else '<span class="pending">⏳ aguardando Google</span>'
        ret = (f"<b>{c.get('retention_pct_7d_canal'):.1f}%</b> <span class='sub'>({c.get('retention_dur_7d_canal')})</span>"
               if c.get("views_7d_canal", 0) > 0 else '<span class="sub">—</span>')
        vph_txt = f"+{c.get('vph_60m', 0)}/h"
        cmp_rows.append(f"""
<tr data-grupo="{c['grupo_slug']}">
  <td class="cell-ch"><div class="ch-name">{_e(c['canal_titulo'])} {st}</div><div class="sub">{_e(c['handle'])} · <span class="pill pill-{c['grupo_slug']}">{_e(c['grupo'])}</span></div></td>
  <td class="num" data-label="Ritmo VPH"><b style="color:var(--cyan)">{vph_txt}</b></td>
  <td class="num" data-label="Views 60 min">+{c.get('views_60m_canal', 0):,}</td>
  <td class="num" data-label="Views 48h">+{c.get('views_48h_canal', 0):,}</td>
  <td class="num" data-label="Views 7d"><b>{c.get('views_7d_canal', 0):,}</b></td>
  <td class="num" data-label="Impressões 7d">{impr}</td>
  <td class="num" data-label="CTR 7d">{ctr}</td>
  <td class="num" data-label="Retenção 7d">{ret}</td>
  <td class="num" data-label="Inscritos">{c.get('inscritos', 0):,}</td>
  <td class="num" data-label="Vídeos">{c.get('total_videos_publicos', 0)} públ. · {c.get('total_videos_agendados', 0)} agend.</td>
</tr>""")

    # 3. TOP 3 POR CANAL
    medals = ["🥇", "🥈", "🥉"]

    def rank_list(items, fmt, empty):
        if not items:
            return f'<div class="empty-mini">{empty}</div>'
        out = []
        for i, it in enumerate(items[:3]):
            out.append(f'<div class="rk"><span class="md">{medals[i]}</span><div class="ri">'
                       f'<a href="{_e(it["url"])}" target="_blank" rel="noopener">{_e(it["title"])}</a>'
                       f'<div class="rm">{fmt(it)}</div></div></div>')
        return "".join(out)

    def fmt_ret(it):
        s = f'<span class="hi">{it["retention_pct"]:.1f}%</span> ({it["duration_str"]}) · '
        s += f'<span class="warn">⚠️ só {it["views_7d"]} views</span>' if it.get("low_sample") else f'{it["views_7d"]:,} views'
        return s

    cards = []
    for c in channels_data:
        if c.get("status_conexao") != "ONLINE":
            cards.append(f"""
<details class="ch off" data-grupo="{c['grupo_slug']}" open>
  <summary><div class="ch-head"><span class="pill pill-{c['grupo_slug']}">{_e(c['grupo'])}</span><h3>{_e(c['canal_titulo'])}<small>{_e(c['nome_projeto'])}</small></h3></div><span class="pill pill-red">desconectado</span></summary>
  <div class="off-msg"><b>Motivo:</b> {_e(c.get('erro'))}<br>Rode no PC: <code>{_e(c.get('auth_bat'))}</code></div>
</details>""")
            continue
        pend = _e(c.get("reach_message") or "Aguardando 1º relatório do Google (24–48h)")
        vph_badge = f'<span class="pill pill-green">⚡ +{c.get("vph_60m", 0)}/h</span>'
        cards.append(f"""
<details class="ch" data-grupo="{c['grupo_slug']}" open>
  <summary>
    <div class="ch-head"><span class="pill pill-{c['grupo_slug']}">{_e(c['grupo'])}</span><h3>{_e(c['canal_titulo'])} {vph_badge}<small>{_e(c['handle'])} · {_e(c['nome_projeto'])}</small></h3></div>
    <div class="ch-stats"><span>👁️ <b>{c.get('views_7d_canal', 0):,}</b> 7d</span><span>⚡ <b>+{c.get('views_48h_canal', 0):,}</b> 48h</span><span>👥 <b>{c.get('inscritos', 0):,}</b></span></div>
  </summary>
  <div class="top3">
    <div class="box"><h4>🎯 Maior retenção (7d)</h4>{rank_list(c.get('top3_retencao_7d', []), fmt_ret, 'Sem views nos últimos 7 dias.')}</div>
    <div class="box"><h4>👁️ Mais views (7d)</h4>{rank_list(c.get('top3_views_7d', []), lambda it: f'<span class="hi">{it["views_7d"]:,} views</span> · ret. {it["retention_pct"]:.1f}%', 'Sem views nos últimos 7 dias.')}</div>
    <div class="box"><h4>🖱️ Maior CTR (7d)</h4>{rank_list(c.get('top3_ctr_7d', []), lambda it: f'<span class="hi">{it["ctr_7d"]:.2f}%</span> · {it["impressions_7d"]:,} impr.', '⏳ ' + pend)}</div>
    <div class="box"><h4>📢 Mais impressões (7d)</h4>{rank_list(c.get('top3_impressoes_7d', []), lambda it: f'<span class="hi">{it["impressions_7d"]:,}</span> impr. · CTR {it["ctr_7d"]:.2f}%', '⏳ ' + pend)}</div>
  </div>
</details>""")

    # 4. MÓDULO 3: LANÇAMENTOS 1 DE 10
    rank10_cards = []
    for c in channels_data:
        r10 = c.get("rank_1_de_10")
        if not r10:
            rank10_cards.append(f"""
<div class="r10-card" data-grupo="{c['grupo_slug']}">
  <div class="r10-head">
    <div class="r10-ch-info"><h4>{_e(c['canal_titulo'])}</h4><div class="sub">{_e(c['handle'])}</div></div>
    <span class="pill pill-group-{c['grupo_slug']}">{_e(c['grupo'])}</span>
  </div>
  <div class="empty-mini">Nenhum vídeo recente com histórico suficiente para comparação.</div>
</div>""")
            continue

        r = r10.get("rank", 10)
        out_of = r10.get("out_of", 10)
        diff = r10.get("diff_pct", 0.0)
        if r == 1:
            b_cls = "r10-b1"
            b_txt = f"🏆 1 de {out_of} — Top Desempenho!"
        elif r <= 3:
            b_cls = "r10-b2"
            b_txt = f"⭐ {r} de {out_of} — Acima da Média"
        elif r <= 7:
            b_cls = "r10-b3"
            b_txt = f"📊 {r} de {out_of} — Na Média"
        else:
            b_cls = "r10-b4"
            b_txt = f"⚠️ {r} de {out_of} — Abaixo da Média"

        diff_sign = "+" if diff > 0 else ""
        diff_color = "var(--green)" if diff > 0 else ("var(--red)" if diff < 0 else "var(--muted)")

        rank10_cards.append(f"""
<div class="r10-card" data-grupo="{c['grupo_slug']}">
  <div>
    <div class="r10-head">
      <div class="r10-ch-info">
        <h4>{_e(c['canal_titulo'])}</h4>
        <div class="sub">{_e(c['handle'])} · <span class="pill pill-{c['grupo_slug']}">{_e(c['grupo'])}</span></div>
      </div>
      <span class="r10-badge {b_cls}">{b_txt}</span>
    </div>
    <div class="r10-body">
      <img src="{_e(r10.get('thumbnail'))}" class="r10-thumb" alt="" loading="lazy">
      <div class="r10-vinfo">
        <a href="{_e(r10.get('url'))}" target="_blank" rel="noopener" class="r10-vtitle">{_e(r10.get('title'))}</a>
        <div class="sub" style="margin-top:4px">Publicado: {_e(r10.get('published_formatted'))}</div>
      </div>
    </div>
  </div>
  <div class="r10-metrics">
    <div>Views: <b>{r10.get('views', 0):,}</b></div>
    <div>Média dos {out_of - 1} anteriores: <b>{r10.get('avg_prev', 0):,}</b></div>
    <div>Vs Média: <b style="color:{diff_color}">{diff_sign}{diff:.1f}%</b></div>
  </div>
</div>""")

    # 5. MÓDULO 5: CALENDÁRIO DE ESTREIAS
    sched_list = all_scheduled or []
    by_date = {}
    for sv in sched_list:
        p_iso = sv.get("published_at", "")
        p_dt = None
        try:
            p_dt = datetime.fromisoformat(p_iso.replace("Z", "+00:00")).astimezone(timezone(timedelta(hours=-3)))
            d_key = p_dt.strftime("%d/%m/%Y (%A)").replace("Monday", "Segunda").replace("Tuesday", "Terça").replace("Wednesday", "Quarta").replace("Thursday", "Quinta").replace("Friday", "Sexta").replace("Saturday", "Sábado").replace("Sunday", "Domingo")
            t_str = p_dt.strftime("%H:%M BRT")
        except Exception:
            d_key = p_iso[:10]
            t_str = "Horário agendado"

        if d_key not in by_date:
            by_date[d_key] = []
        by_date[d_key].append((t_str, sv))

    cal_html = []
    if by_date:
        for d_label, items in by_date.items():
            rows_cal = []
            for t_str, sv in items:
                rows_cal.append(f"""
<div class="cal-row" data-grupo="{sv.get('grupo_slug')}">
  <div class="cal-time">{t_str}</div>
  <img src="{_e(sv.get('thumbnail'))}" class="cal-thumb" alt="" loading="lazy">
  <div class="cal-info">
    <h4><span class="pill pill-{sv.get('grupo_slug')}" style="margin-right:6px">{_e(sv.get('canal_titulo'))}</span> {_e(sv.get('title'))}</h4>
    <div class="sub">{_e(sv.get('canal_handle'))}</div>
  </div>
</div>""")
            cal_html.append(f"""
<div class="cal-group">
  <div class="cal-date-title">📅 {d_label} ({len(items)} {('estreia' if len(items)==1 else 'estreias')})</div>
  {''.join(rows_cal)}
</div>""")
    else:
        cal_html.append('<div class="empty">Nenhum vídeo agendado no momento em nenhum dos canais.</div>')

    # Dados para alimentar o Chart.js
    timeseries_data = {
        c["id"]: {
            "title": c.get("canal_titulo"),
            "handle": c.get("handle"),
            "group_slug": c.get("grupo_slug"),
            "history_30d": c.get("history_30d", []),
            "traffic_sources_30d": c.get("traffic_sources_30d", []),
        }
        for c in channels_data
    }
    timeseries_json = json.dumps(timeseries_data, ensure_ascii=False)

    chart_channel_chips = [
        '<button class="ch-chip active" data-ch="all" onclick="renderChannelCharts(\'all\')">Todos os Canais (Consolidado)</button>'
    ]
    for c in channels_data:
        chart_channel_chips.append(
            f'<button class="ch-chip" data-ch="{c["id"]}" onclick="renderChannelCharts(\'{c["id"]}\')">{_e(c["canal_titulo"])}</button>'
        )

    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
<meta http-equiv="refresh" content="600">
<meta name="theme-color" content="#090D16">
<meta name="apple-mobile-web-app-capable" content="yes">
<title>Painel Canais Dark — YouTube Studio Multi-Canal</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;700;800&display=swap" rel="stylesheet">
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
<style>{CSS}</style>
</head>
<body>
<div class="wrap">

  <!-- Topbar -->
  <div class="topbar">
    <div class="topbar-main">
      <div>
        <h1>📊 Painel Canais Dark</h1>
        <div class="meta">Atualizado <b>{now_str}</b> (BRT) · <b>{online}/{total_ch}</b> online · Nuvem a cada 15–30 min</div>
      </div>
      <div class="vph-badge">
        <span>⚡</span> Ritmo da Fábrica: <b>+{total_vph_60m} views/hora</b>
      </div>
    </div>
    <div class="chips">
      <button class="chip active" id="chip-all" onclick="filterGroup('all',this)">Todos ({total_ch})</button>
      <button class="chip" id="chip-pessoal" onclick="filterGroup('pessoal',this)">Pessoais ({n_pessoal})</button>
      <button class="chip" id="chip-gvg" onclick="filterGroup('gvg',this)">Startup GVG ({n_gvg})</button>
    </div>
  </div>

  <!-- Navegação Principal por Abas -->
  <div class="main-nav">
    <button class="nav-tab active" id="btn-tab-live" onclick="switchMainTab('live', this)">⚡ Radar ao Vivo</button>
    <button class="nav-tab" id="btn-tab-charts" onclick="switchMainTab('charts', this)">📈 Gráficos (30d)</button>
    <button class="nav-tab" id="btn-tab-rank10" onclick="switchMainTab('rank10', this)">🎯 Lançamentos (1 de 10)</button>
    <button class="nav-tab" id="btn-tab-calendar" onclick="switchMainTab('calendar', this)">📅 Calendário ({total_sched_count})</button>
  </div>

  <!-- TAB 1: RADAR AO VIVO -->
  <div class="tab-content active" id="view-live">
    <div class="sec">
      <div class="sec-top">
        <div>
          <div class="sec-title">🔥 Mais vistos agora — todos os canais</div>
          <div class="sec-hint">Views ganhas por vídeo público · janela acumulada: {win_48_txt}</div>
        </div>
        <div class="seg">
          <button class="active" id="seg-d60" onclick="setSort('d60',this)">Últimos 60 min</button>
          <button id="seg-d48" onclick="setSort('d48',this)">Últimas 48h</button>
          <button id="seg-total" onclick="setSort('total',this)">Recentes</button>
        </div>
      </div>
      <div class="lv-count" id="lv-count"></div>
      <div id="lv-list">{''.join(live_html)}</div>
      <div class="empty" id="lv-empty" style="display:none"></div>
    </div>

    <div class="sec">
      <div class="sec-top"><div>
        <div class="sec-title">📋 Comparativo dos canais</div>
        <div class="sec-hint">Ritmo VPH (views/h) · 60m / 48h (medição própria) · 7d via Analytics API</div>
      </div></div>
      <div class="tbl-wrap">
        <table class="cmp">
          <thead><tr><th>Canal</th><th class="num">Ritmo VPH</th><th class="num">60 min</th><th class="num">48h</th><th class="num">Views 7d</th><th class="num">Impressões 7d</th><th class="num">CTR 7d</th><th class="num">Retenção 7d</th><th class="num">Inscritos</th><th class="num">Vídeos</th></tr></thead>
          <tbody>{''.join(cmp_rows)}</tbody>
        </table>
      </div>
    </div>

    <div class="sec-top" style="margin:6px 2px 10px"><div>
      <div class="sec-title">🏆 Top 3 de cada canal (7 dias)</div>
      <div class="sec-hint">Toque no canal para abrir/fechar · retenção prioriza vídeos com ≥{MIN_VIEWS_FOR_RETENTION_RANK} views</div>
    </div></div>
    {''.join(cards)}
  </div>

  <!-- TAB 2: GRÁFICOS & HISTÓRICO -->
  <div class="tab-content" id="view-charts">
    <div class="ch-chips">{''.join(chart_channel_chips)}</div>
    <div class="kpi-row">
      <div class="kpi">
        <div class="kpi-val" id="kpi-views-30d">—</div>
        <div class="kpi-lbl">Visualizações (30 Dias)</div>
      </div>
      <div class="kpi">
        <div class="kpi-val" id="kpi-subs-30d" style="color:var(--green)">—</div>
        <div class="kpi-lbl">Saldo de Inscritos (30d)</div>
      </div>
      <div class="kpi">
        <div class="kpi-val" id="kpi-top-traffic" style="font-size:15px;color:var(--purple)">—</div>
        <div class="kpi-lbl">Principal Origem de Tráfego</div>
      </div>
    </div>
    <div class="chart-grid">
      <div class="chart-card">
        <div class="chart-head">
          <h3>📈 Curva de Visualizações Diárias (30 Dias)</h3>
        </div>
        <div class="chart-box"><canvas id="chartViews"></canvas></div>
      </div>
      <div class="chart-card">
        <div class="chart-head">
          <h3>🚦 Origem do Tráfego</h3>
        </div>
        <div class="chart-box"><canvas id="chartTraffic"></canvas></div>
      </div>
    </div>
  </div>

  <!-- TAB 3: LANÇAMENTOS 1 DE 10 -->
  <div class="tab-content" id="view-rank10">
    <div class="sec-top" style="margin-bottom:12px">
      <div>
        <div class="sec-title">🎯 Desempenho do Vídeo Mais Recente (1 de 10)</div>
        <div class="sec-hint">Compara as views do último vídeo postado com a média dos 10 vídeos anteriores do canal</div>
      </div>
    </div>
    <div class="rank10-grid">{''.join(rank10_cards)}</div>
  </div>

  <!-- TAB 4: CALENDÁRIO DE ESTREIAS -->
  <div class="tab-content" id="view-calendar">
    <div class="sec-top" style="margin-bottom:12px">
      <div>
        <div class="sec-title">📅 Linha do Tempo de Vídeos Agendados ({total_sched_count} Estreias)</div>
        <div class="sec-hint">Fila organizada cronologicamente com as próximas estreias em todos os canais</div>
      </div>
    </div>
    {''.join(cal_html)}
  </div>

</div>
<script>
window.CHANNELS_TIMESERIES = {timeseries_json};
{JS}
</script>
</body>
</html>"""
