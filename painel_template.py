# -*- coding: utf-8 -*-
"""
===============================================================================
DARK FACTORY CLOUD ENGINE — PAINEL MASTER ANALYTICS (MULTI-CANAL YOUTUBE STUDIO)
ARQUIVO: painel_template.py
===============================================================================
Visões:
1. 🏠 Tela Inicial (Hub / Seletor de Canais com Fotos de Perfil, Ritmo e "Geral" no meio)
2. 📺 Visão Exclusiva do Canal (Dashboard dedicado com vídeos, gráficos, 1 de 10, top 3, agendados)
3. 🌐 Visão Geral Consolidada (Radar geral, comparativo, gráficos de todos os canais, calendário)
===============================================================================
"""

import json
import html as htmllib
from datetime import datetime, timezone, timedelta

MIN_VIEWS_FOR_RETENTION_RANK = 10

DEFAULT_AVATARS = {
    "stickman": "https://yt3.ggpht.com/goglhVSAtKGaDmImc5ImFHN2xuRVe6nO1kEAgvRRcCFNDnc2Ll9gExh9kTtvyWzn7cWvBOZF=s240-c-k-c0x00ffffff-no-rj",
    "biblia": "https://yt3.ggpht.com/FCvbK6LfJRHAeqdwQ7p9tqlCn31dvnzWK5xupy98ZsjSkk5eaT36cjcIsut9iS1miawMe_61uQ=s240-c-k-c0x00ffffff-no-rj",
    "indiano_doc": "https://yt3.ggpht.com/devCRpUBJrmk-rVr8u2bGpku825XI6JGqHlfSu6Lm9qCe0GdpliqhwLKL6sek4FQSa2EwYuJ5GQ=s240-c-k-c0x00ffffff-no-rj",
    "espaco": "https://yt3.ggpht.com/JXn7kKX_0a8Pjo_M5i900WpQozgiEPkFMB--rPeiG3LpLepp5FUlo-iK-R_xnSFhzxNMzAjX=s240-c-k-c0x00ffffff-no-rj",
    "novela": "https://yt3.ggpht.com/GvkrbIFed7MJzRUtmKbOctx9f7-Az6du7c2VVq7FMf9LqUbyzO4zuMzmO7_MrAj8wWNj1d5Q1Q=s240-c-k-c0x00ffffff-no-rj",
    "hearttangle": "https://yt3.ggpht.com/BVmsrWlRE6h3-C7jk6vUOqa3hpdBSjGJQ1JkkvXV0tnOItk5ev9t-VE8WYtOnGE-VAZcfmgsMw=s240-c-k-c0x00ffffff-no-rj",
    "segredos_olga": "https://yt3.ggpht.com/t1Eiys8HqrCd5SX9moZeU1YitQofpQvWxfoS3xD_HxnLYznco-LqvSlPEVLG4mZytRryx7Kr2w=s240-c-k-c0x00ffffff-no-rj",
}


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

/* Master Views */
.view-section{display:none}
.view-section.active{display:block}

/* Topbar Global */
.topbar{background:var(--surface);border:1px solid var(--border);border-radius:14px;padding:14px 18px;margin-bottom:14px}
.topbar-main{display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:12px}
.topbar h1{font-size:18px;font-weight:800;display:flex;align-items:center;gap:8px}
.topbar .meta{font-size:12px;color:var(--muted);margin-top:4px}
.topbar .meta b{color:var(--text)}
.vph-badge{display:inline-flex;align-items:center;gap:6px;background:rgba(56,189,248,.12);border:1px solid var(--border-hi);color:var(--cyan);padding:4px 10px;border-radius:999px;font-size:12px;font-weight:700}

/* Navegação Superior com Voltar e Quick Switcher */
.channel-nav-bar{display:flex;justify-content:space-between;align-items:center;background:var(--surface);border:1px solid var(--border);border-radius:14px;padding:10px 14px;margin-bottom:14px;flex-wrap:wrap;gap:10px}
.btn-back-hub{display:inline-flex;align-items:center;gap:8px;background:var(--surface-2);color:var(--text);border:1px solid var(--border);border-radius:10px;padding:8px 14px;font-size:12px;font-weight:700;cursor:pointer;transition:all .15s}
.btn-back-hub:hover{background:var(--surface-3);border-color:var(--cyan);color:var(--cyan)}
.ch-quick-switcher{display:flex;gap:6px;overflow-x:auto;-webkit-overflow-scrolling:touch;scrollbar-width:none}
.ch-quick-switcher::-webkit-scrollbar{display:none}
.ch-switch-btn{display:inline-flex;align-items:center;gap:6px;background:var(--surface-2);color:var(--muted);border:1px solid var(--border);border-radius:8px;padding:6px 10px;font-size:12px;font-weight:600;cursor:pointer;white-space:nowrap;transition:all .15s}
.ch-switch-btn:hover{color:var(--text);background:var(--surface-3)}
.ch-switch-btn.active{background:var(--cyan);color:#090D16;border-color:var(--cyan);font-weight:700}
.ch-switch-btn img{width:18px;height:18px;border-radius:50%;object-fit:cover}

/* 1. HUB / TELA INICIAL */
.hub-hero{background:linear-gradient(135deg,rgba(30,41,59,.8) 0%,rgba(15,23,42,.95) 100%);border:1px solid var(--border);border-radius:16px;padding:22px;margin-bottom:18px;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:14px;position:relative;overflow:hidden}
.hub-hero h1{font-size:22px;font-weight:800;letter-spacing:-.5px;display:flex;align-items:center;gap:10px}
.hub-hero .meta{font-size:13px;color:var(--muted);margin-top:4px}
.hub-chips{display:flex;gap:8px;margin-top:14px;overflow-x:auto;-webkit-overflow-scrolling:touch;scrollbar-width:none}
.hub-chips::-webkit-scrollbar{display:none}

.hub-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin-bottom:24px}
@media (max-width:1200px){.hub-grid{grid-template-columns:repeat(2,1fr)}}
@media (max-width:640px){.hub-grid{grid-template-columns:1fr}}

.hub-card{background:var(--surface);border:1px solid var(--border);border-radius:16px;padding:18px;display:flex;flex-direction:column;justify-content:space-between;cursor:pointer;transition:all .2s cubic-bezier(0.16,1,0.3,1);position:relative;overflow:hidden}
.hub-card:hover{transform:translateY(-4px);border-color:var(--cyan);box-shadow:0 12px 28px rgba(0,0,0,.4),0 0 20px rgba(56,189,248,.15)}
.hub-card.card-geral{background:linear-gradient(135deg,rgba(30,41,59,.95) 0%,rgba(15,23,42,.98) 100%);border:1.5px solid rgba(56,189,248,.4);box-shadow:0 4px 18px rgba(56,189,248,.1)}
.hub-card.card-geral:hover{border-color:#38BDF8;box-shadow:0 12px 28px rgba(0,0,0,.4),0 0 28px rgba(56,189,248,.25)}

.card-top{display:flex;align-items:center;gap:14px;margin-bottom:14px}
.card-avatar-wrap{position:relative;width:58px;height:58px;flex-shrink:0}
.card-avatar{width:58px;height:58px;border-radius:50%;object-fit:cover;border:2px solid var(--border);background:#0f172a}
.card-avatar.geral-icon{display:flex;align-items:center;justify-content:center;font-size:26px;background:radial-gradient(circle,rgba(56,189,248,.25) 0%,rgba(15,23,42,.9) 100%);border-color:var(--cyan)}
.card-status-dot{position:absolute;bottom:1px;right:1px;width:14px;height:14px;border-radius:50%;border:2px solid var(--surface)}
.card-status-dot.online{background:var(--green)}
.card-status-dot.offline{background:var(--red)}

.card-meta{min-width:0;flex:1}
.card-name{font-size:15px;font-weight:700;color:var(--text);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.card-subtext{font-size:12px;color:var(--muted);margin-top:2px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}

.card-metrics{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;background:var(--surface-2);border-radius:10px;padding:10px 8px;margin-bottom:14px;text-align:center}
.card-metrics .cm-item{display:flex;flex-direction:column}
.card-metrics .cm-lbl{font-size:10px;color:var(--muted);text-transform:uppercase;font-weight:600}
.card-metrics .cm-val{font-family:'JetBrains Mono',monospace;font-size:13px;font-weight:700;margin-top:2px;color:var(--text)}
.card-metrics .cm-val.cyan{color:var(--cyan)}
.card-metrics .cm-val.green{color:var(--green)}

.card-footer{display:flex;justify-content:space-between;align-items:center;font-size:12px;font-weight:600;color:var(--cyan);padding-top:6px;border-top:1px solid rgba(255,255,255,.05)}

/* 2. VISÃO EXCLUSIVA DO CANAL */
.ch-banner{background:linear-gradient(135deg,rgba(30,41,59,.8) 0%,rgba(15,23,42,.95) 100%);border:1px solid var(--border);border-radius:16px;padding:18px 20px;margin-bottom:14px;display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:16px}
.ch-banner-left{display:flex;align-items:center;gap:16px}
.ch-banner-avatar{width:72px;height:72px;border-radius:50%;object-fit:cover;border:2px solid var(--border-hi);box-shadow:0 0 16px rgba(56,189,248,.2);background:#0f172a}
.ch-banner-info h2{font-size:20px;font-weight:800;display:flex;align-items:center;gap:8px}
.ch-banner-info .meta-row{display:flex;align-items:center;gap:8px;font-size:12px;color:var(--muted);margin-top:4px;flex-wrap:wrap}

.ch-kpi-bar{display:grid;grid-template-columns:repeat(8,1fr);gap:8px;margin-bottom:14px}
@media (max-width:1200px){.ch-kpi-bar{grid-template-columns:repeat(4,1fr)}}
@media (max-width:640px){.ch-kpi-bar{grid-template-columns:repeat(2,1fr)}}

.ch-kpi-box{background:var(--surface);border:1px solid var(--border);border-radius:12px;padding:10px 8px;text-align:center}
.ch-kpi-lbl{font-size:10px;color:var(--muted);text-transform:uppercase;font-weight:600}
.ch-kpi-val{font-size:15px;font-weight:800;font-family:'JetBrains Mono',monospace;color:var(--text);margin-top:2px}

/* Sub-navegação interna */
.sub-nav{display:flex;gap:8px;background:var(--surface);border:1px solid var(--border);border-radius:14px;padding:6px;margin-bottom:14px;overflow-x:auto;-webkit-overflow-scrolling:touch;scrollbar-width:none}
.sub-nav::-webkit-scrollbar{display:none}
.sub-tab-btn{flex:1;min-width:130px;background:transparent;color:var(--muted);border:0;border-radius:10px;padding:10px 14px;font-size:13px;font-weight:700;cursor:pointer;white-space:nowrap;transition:all .15s}
.sub-tab-btn:hover{color:var(--text);background:var(--surface-2)}
.sub-tab-btn.active{background:var(--cyan);color:#090D16;box-shadow:0 2px 8px rgba(56,189,248,.25)}

.sub-content{display:none}
.sub-content.active{display:block}

/* Segmented Controls & Chips */
.chips{display:flex;gap:8px;overflow-x:auto;-webkit-overflow-scrolling:touch;scrollbar-width:none}
.chips::-webkit-scrollbar{display:none}
.chip{flex:0 0 auto;background:var(--surface-2);color:var(--text);border:1px solid var(--border);padding:8px 14px;border-radius:999px;font-size:12px;font-weight:600;cursor:pointer;min-height:36px;white-space:nowrap}
.chip.active{background:var(--cyan);color:#090D16;border-color:var(--cyan)}

.seg{display:flex;background:var(--surface-2);border:1px solid var(--border);border-radius:12px;padding:3px;gap:3px;overflow-x:auto;-webkit-overflow-scrolling:touch}
.seg button{flex:1;background:transparent;color:var(--muted);border:0;border-radius:9px;padding:8px 10px;font-size:12px;font-weight:700;cursor:pointer;white-space:nowrap;min-height:36px;transition:all .15s}
.seg button:hover{color:var(--text)}
.seg button.active{background:var(--cyan);color:#090D16}

/* Sections & Cards */
.sec{background:var(--surface);border:1px solid var(--border);border-radius:14px;padding:14px 16px;margin-bottom:14px}
.sec-title{font-size:16px;font-weight:700}
.sec-hint{font-size:12px;color:var(--muted);margin-top:3px}
.sec-top{display:flex;justify-content:space-between;align-items:flex-end;gap:10px;flex-wrap:wrap;margin-bottom:12px}

/* Live video rows */
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

/* Top 3 Cards */
details.ch{background:var(--surface);border:1px solid var(--border);border-radius:14px;margin-bottom:12px;overflow:hidden}
details.ch.off{border-color:rgba(244,63,94,.4)}
details.ch>summary{list-style:none;cursor:pointer;padding:14px 16px;display:flex;justify-content:space-between;align-items:center;gap:10px;flex-wrap:wrap}
details.ch>summary::-webkit-details-marker{display:none}
details.ch>summary::after{content:'▾';color:var(--muted);font-size:16px;transition:transform .2s}
details.ch:not([open])>summary::after{transform:rotate(-90deg)}
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

/* Gráficos e Filtros */
.filters-panel{background:var(--surface);border:1px solid var(--border);border-radius:14px;padding:16px;margin-bottom:14px}
.fg-row{display:flex;align-items:center;gap:10px;margin-bottom:10px;flex-wrap:wrap}
.fg-lbl{font-size:12px;font-weight:700;color:var(--muted);min-width:70px;text-transform:uppercase;letter-spacing:.5px}
.fg-ctrl{flex:1;min-width:280px}
.ch-chips{display:flex;gap:6px;overflow-x:auto;-webkit-overflow-scrolling:touch;padding-bottom:4px}
.ch-chips::-webkit-scrollbar{display:none}
.ch-chip{background:var(--surface-2);color:var(--text);border:1px solid var(--border);padding:7px 12px;border-radius:8px;font-size:12px;font-weight:600;cursor:pointer;white-space:nowrap;transition:all .15s}
.ch-chip:hover{color:var(--text);background:var(--surface-3)}
.ch-chip.active{background:var(--cyan);color:#090D16;border-color:var(--cyan);font-weight:700}

.kpi-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin-bottom:14px}
.kpi{background:var(--surface);border:1px solid var(--border);border-radius:12px;padding:14px;text-align:center}
.kpi-val{font-size:22px;font-weight:800;font-family:'JetBrains Mono',monospace;color:var(--cyan)}
.kpi-lbl{font-size:11px;color:var(--muted);text-transform:uppercase;margin-top:4px;font-weight:600}

.chart-card{background:var(--surface);border:1px solid var(--border);border-radius:14px;padding:16px;margin-bottom:14px}
.chart-head{display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:10px;margin-bottom:14px}
.chart-head h3{font-size:15px;font-weight:700}
.chart-box{position:relative;width:100%;height:270px}
.charts-split{display:grid;grid-template-columns:1fr 1fr;gap:14px}

/* 1 de 10 */
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

/* Calendário */
.cal-group{margin-bottom:18px}
.cal-date-title{font-size:14px;font-weight:800;color:var(--cyan);text-transform:uppercase;letter-spacing:.5px;margin-bottom:8px;padding-left:4px;display:flex;align-items:center;gap:6px}
.cal-row{display:grid;grid-template-columns:85px 120px 1fr;gap:12px;align-items:center;background:var(--surface);border:1px solid var(--border);border-radius:12px;padding:10px 14px;margin-bottom:8px}
.cal-time{font-family:'JetBrains Mono',monospace;font-weight:700;font-size:14px;color:var(--text)}
.cal-thumb{width:120px;height:68px;object-fit:cover;border-radius:8px;border:1px solid var(--border);background:#000}
.cal-info h4{font-size:14px;font-weight:600;margin-bottom:4px}

/* Responsive */
@media (max-width:1100px){
  .top3{grid-template-columns:repeat(2,1fr)}
  .charts-split{grid-template-columns:1fr}
}
@media (max-width:720px){
  body{padding:10px}
  .topbar,.sec,.chart-card,.r10-card,.filters-panel,.hub-hero,.ch-banner{padding:12px;border-radius:12px}
  .topbar h1{font-size:16px}
  .top3{grid-template-columns:1fr;padding:0 12px 12px}
  .kpi-grid{grid-template-columns:repeat(2,1fr);gap:8px}
  .kpi{padding:10px}
  .kpi-val{font-size:18px}
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
let activeView = 'hub'; // 'hub' | 'channel' | 'geral'
let activeChannelId = '';
let activeChannelSubTab = 'live';
let activeGeralTab = 'live';

let curSinglePeriod = '30d', curSingleFormat = 'all', curSingleSort = 'd60';
let curGeralPeriod = '30d', curGeralFormat = 'all', curGeralChannel = 'all', curGeralSort = 'd60', curGeralGroup = 'all';

const EMPTY_MSG={
  d60:'Nenhum vídeo ganhou views na última medição (~60 min).',
  d48:'Nenhum vídeo ganhou views na janela de 48h medida até agora.',
  total:'Nenhum vídeo público com movimentação recente.'
};

function getCutoffDate(period){
  const now = new Date();
  if(period === '7d') return new Date(now.getTime() - 7 * 86400000).toISOString().slice(0, 10);
  if(period === '30d') return new Date(now.getTime() - 30 * 86400000).toISOString().slice(0, 10);
  if(period === 'month') return now.getFullYear() + '-' + String(now.getMonth() + 1).padStart(2, '0') + '-01';
  if(period === '180d') return new Date(now.getTime() - 180 * 86400000).toISOString().slice(0, 10);
  if(period === 'year') return now.getFullYear() + '-01-01';
  return '2000-01-01'; // 'all'
}

// ROUTING: Abrir Canal / Geral / Home Hub
function openChannel(chId, updateHistory){
  if(updateHistory === undefined) updateHistory = true;

  if(chId === 'home'){
    activeView = 'hub';
    activeChannelId = '';
    document.querySelectorAll('.view-section').forEach(s => s.classList.remove('active'));
    document.getElementById('view-hub').classList.add('active');
    window.scrollTo({top: 0, behavior: 'smooth'});

    if(updateHistory){
      const u = new URL(location.href);
      u.searchParams.delete('channel');
      u.searchParams.delete('tab');
      history.pushState(null, '', u);
    }
    return;
  }

  if(chId === 'geral'){
    activeView = 'geral';
    activeChannelId = 'geral';
    document.querySelectorAll('.view-section').forEach(s => s.classList.remove('active'));
    document.getElementById('view-geral').classList.add('active');

    document.querySelectorAll('.ch-switch-btn').forEach(b => {
      b.classList.toggle('active', b.dataset.ch === 'geral');
    });

    if(activeGeralTab === 'charts') updateGeralCharts();
    else applyGeralLive();

    window.scrollTo({top: 0, behavior: 'smooth'});

    if(updateHistory){
      const u = new URL(location.href);
      u.searchParams.set('channel', 'geral');
      history.pushState(null, '', u);
    }
    return;
  }

  // Visão Exclusiva do Canal
  activeView = 'channel';
  activeChannelId = chId;
  document.querySelectorAll('.view-section').forEach(s => s.classList.remove('active'));
  document.getElementById('view-channel').classList.add('active');

  // Mostrar Banner e Cards correspondentes
  document.querySelectorAll('.ch-banner').forEach(b => {
    b.style.display = (b.dataset.canal === chId) ? 'flex' : 'none';
  });
  document.querySelectorAll('.ch-r10-card').forEach(c => {
    c.style.display = (c.dataset.canal === chId) ? 'block' : 'none';
  });
  document.querySelectorAll('.ch-top3-grid').forEach(t => {
    t.style.display = (t.dataset.canal === chId) ? 'grid' : 'none';
  });
  document.querySelectorAll('.ch-sched-item').forEach(s => {
    s.style.display = (s.dataset.canal === chId) ? 'grid' : 'none';
  });

  const schedCount = document.querySelectorAll('.ch-sched-item[data-canal="'+chId+'"]').length;
  const schedEmpty = document.getElementById('ch-sched-empty');
  if(schedEmpty) schedEmpty.style.display = schedCount ? 'none' : 'block';

  // Atualizar Quick Switcher
  document.querySelectorAll('.ch-switch-btn').forEach(b => {
    b.classList.toggle('active', b.dataset.ch === chId);
  });

  // Atualizar Radar ao Vivo e Gráficos do Canal
  applySingleChannelLive();
  if(activeChannelSubTab === 'charts') updateSingleChannelCharts();

  window.scrollTo({top: 0, behavior: 'smooth'});

  if(updateHistory){
    const u = new URL(location.href);
    u.searchParams.set('channel', chId);
    history.pushState(null, '', u);
  }
}

// Sub-navegação interna do canal
function switchChannelSubTab(tabId, btn){
  activeChannelSubTab = tabId;
  document.querySelectorAll('#view-channel .sub-tab-btn').forEach(b => b.classList.remove('active'));
  document.querySelectorAll('#view-channel .sub-content').forEach(c => c.classList.remove('active'));

  if(btn) btn.classList.add('active');
  const target = document.getElementById('ch-tab-' + tabId);
  if(target) target.classList.add('active');

  if(tabId === 'charts') updateSingleChannelCharts();

  const u = new URL(location.href);
  u.searchParams.set('tab', tabId);
  history.replaceState(null, '', u);
}

// Sub-navegação interna da visão Geral
function switchGeralMainTab(tabId, btn){
  activeGeralTab = tabId;
  document.querySelectorAll('#view-geral .sub-tab-btn').forEach(b => b.classList.remove('active'));
  document.querySelectorAll('#view-geral .sub-content').forEach(c => c.classList.remove('active'));

  if(btn) btn.classList.add('active');
  const target = document.getElementById('geral-tab-' + tabId);
  if(target) target.classList.add('active');

  if(tabId === 'charts') updateGeralCharts();

  const u = new URL(location.href);
  u.searchParams.set('tab', tabId);
  history.replaceState(null, '', u);
}

// Filtro de Grupo no Hub
function filterHubGroup(g, btn){
  document.querySelectorAll('.hub-chips .chip').forEach(b => b.classList.toggle('active', b === btn));
  document.querySelectorAll('.hub-card').forEach(c => {
    const isGeral = c.classList.contains('card-geral');
    if(g === 'all'){
      c.style.display = 'flex';
    } else {
      if(isGeral) c.style.display = 'flex';
      else c.style.display = (c.dataset.grupo === g) ? 'flex' : 'none';
    }
  });
}

// Live Radar: Canal Individual
function applySingleChannelLive(){
  const list = document.getElementById('ch-live-list');
  if(!list || !activeChannelId) return;

  const rows = [...list.querySelectorAll('.lv-row')];
  const chRows = rows.filter(r => r.dataset.canal === activeChannelId);

  const c60 = chRows.filter(r => (+r.dataset.d60) > 0).length;
  const c48 = chRows.filter(r => (+r.dataset.d48) > 0).length;
  const cTot = chRows.length;

  const b60 = document.getElementById('ch-seg-d60');
  const b48 = document.getElementById('ch-seg-d48');
  const bTot = document.getElementById('ch-seg-total');
  if(b60) b60.textContent = 'Últimos 60 min (' + c60 + ')';
  if(b48) b48.textContent = 'Últimas 48h (' + c48 + ')';
  if(bTot) bTot.textContent = 'Recentes (' + cTot + ')';

  rows.forEach(r => {
    if(r.dataset.canal !== activeChannelId){
      r.style.display = 'none';
    }
  });

  chRows.sort((a,b) => (+b.dataset[curSingleSort]) - (+a.dataset[curSingleSort]) || (+b.dataset.d48) - (+a.dataset.d48) || (+b.dataset.total) - (+a.dataset.total));

  let n = 0;
  chRows.forEach(r => {
    list.appendChild(r);
    const okV = (curSingleSort === 'total') || ((+r.dataset[curSingleSort]) > 0);
    r.style.display = okV ? '' : 'none';
    if(okV){
      n++;
      r.querySelector('.lv-rank').textContent = n;
    }
    r.querySelectorAll('.mt').forEach(m => m.classList.toggle('sel', m.dataset.k === curSingleSort));
  });

  const em = document.getElementById('ch-live-empty');
  if(em){
    em.textContent = EMPTY_MSG[curSingleSort];
    em.style.display = n ? 'none' : 'block';
  }
  const cnt = document.getElementById('ch-live-count');
  if(cnt){
    cnt.textContent = 'Exibindo ' + n + (n === 1 ? ' vídeo' : ' vídeos') + ' (' + (curSingleSort === 'd60' ? 'mais vistos em 60 min' : curSingleSort === 'd48' ? 'mais vistos em 48h' : 'total de views') + ')';
  }
}

function setSingleChannelSort(s, btn){
  curSingleSort = s;
  document.querySelectorAll('#ch-tab-live .seg button').forEach(b => b.classList.toggle('active', b === btn));
  applySingleChannelLive();
}

// Live Radar: Geral
function applyGeralLive(){
  const list = document.getElementById('geral-live-list');
  if(!list) return;

  const rows = [...list.querySelectorAll('.lv-row')];
  const groupRows = rows.filter(r => curGeralGroup === 'all' || r.dataset.grupo === curGeralGroup);

  const c60 = groupRows.filter(r => (+r.dataset.d60) > 0).length;
  const c48 = groupRows.filter(r => (+r.dataset.d48) > 0).length;
  const cTot = groupRows.length;

  const b60 = document.getElementById('geral-seg-d60');
  const b48 = document.getElementById('geral-seg-d48');
  const bTot = document.getElementById('geral-seg-total');
  if(b60) b60.textContent = 'Últimos 60 min (' + c60 + ')';
  if(b48) b48.textContent = 'Últimas 48h (' + c48 + ')';
  if(bTot) bTot.textContent = 'Recentes (' + cTot + ')';

  rows.sort((a,b) => (+b.dataset[curGeralSort]) - (+a.dataset[curGeralSort]) || (+b.dataset.d48) - (+a.dataset.d48) || (+b.dataset.total) - (+a.dataset.total));

  let n = 0;
  rows.forEach(r => {
    list.appendChild(r);
    const okG = (curGeralGroup === 'all') || (r.dataset.grupo === curGeralGroup);
    const okV = (curGeralSort === 'total') || ((+r.dataset[curGeralSort]) > 0);
    const show = okG && okV;
    r.style.display = show ? '' : 'none';
    if(show){
      n++;
      r.querySelector('.lv-rank').textContent = n;
    }
    r.querySelectorAll('.mt').forEach(m => m.classList.toggle('sel', m.dataset.k === curGeralSort));
  });

  const em = document.getElementById('geral-live-empty');
  if(em){
    em.textContent = EMPTY_MSG[curGeralSort];
    em.style.display = n ? 'none' : 'block';
  }
  const cnt = document.getElementById('geral-live-count');
  if(cnt){
    cnt.textContent = 'Exibindo ' + n + (n === 1 ? ' vídeo' : ' vídeos') + ' (' + (curGeralSort === 'd60' ? 'mais vistos em 60 min' : curGeralSort === 'd48' ? 'mais vistos em 48h' : 'total de views') + ')';
  }
}

function setGeralSort(s, btn){
  curGeralSort = s;
  document.querySelectorAll('#geral-tab-live .seg button').forEach(b => b.classList.toggle('active', b === btn));
  applyGeralLive();
}

function filterGeralGroup(g, btn){
  curGeralGroup = g;
  document.querySelectorAll('#geral-chips .chip').forEach(b => b.classList.toggle('active', b === btn));
  document.querySelectorAll('#view-geral [data-grupo]:not(.lv-row)').forEach(el => {
    el.style.display = (g === 'all' || el.dataset.grupo === g) ? '' : 'none';
  });
  applyGeralLive();
}

// Chart.js Instances
let chViewsChart = null, chSubsChart = null, chTrafficChart = null;
let geralViewsChart = null, geralSubsChart = null, geralTrafficChart = null;

const pLabels = {
  '7d': 'Últimos 7 Dias',
  '30d': 'Últimos 30 Dias',
  'month': 'Este Mês',
  '180d': 'Últimos 180 Dias',
  'year': 'Este Ano',
  'all': 'Geral (Desde o Início)'
};
const fLabels = {
  'all': 'Todos os Formatos',
  'video': '🎬 Só Vídeos Longos',
  'shorts': '⚡ Só Shorts'
};

// Gráficos do Canal Individual
function setSingleChannelPeriod(p, btn){
  curSinglePeriod = p;
  document.querySelectorAll('#ch-tab-charts .period-btn').forEach(b => b.classList.toggle('active', b === btn));
  updateSingleChannelCharts();
}

function setSingleChannelFormat(f, btn){
  curSingleFormat = f;
  document.querySelectorAll('#ch-tab-charts .format-btn').forEach(b => b.classList.toggle('active', b === btn));
  updateSingleChannelCharts();
}

function updateSingleChannelCharts(){
  if(!activeChannelId) return;
  const raw = window.CHANNELS_TIMESERIES || {};
  const chData = raw[activeChannelId];
  if(!chData) return;

  const cutoff = getCutoffDate(curSinglePeriod);
  const dayMap = {}, subMap = {}, minMap = {}, trafMap = {};

  (chData.history_lifetime || chData.history_30d || []).forEach(h => {
    if(h.day < cutoff) return;
    if(curSingleFormat !== 'all' && h.type && h.type !== curSingleFormat) return;
    dayMap[h.day] = (dayMap[h.day] || 0) + (h.views || 0);
    subMap[h.day] = (subMap[h.day] || 0) + (h.net_subs || 0);
    minMap[h.day] = (minMap[h.day] || 0) + (h.minutes || 0);
  });

  (chData.traffic_sources_lifetime || chData.traffic_sources_30d || []).forEach(t => {
    if(t.day && t.day < cutoff) return;
    if(curSingleFormat !== 'all' && t.type && t.type !== curSingleFormat) return;
    trafMap[t.label] = (trafMap[t.label] || 0) + (t.views || 0);
  });

  const sortedDays = Object.keys(dayMap).sort();
  const viewsData = sortedDays.map(d => dayMap[d]);
  const subsData = sortedDays.map(d => subMap[d]);

  const totV = viewsData.reduce((a, b) => a + b, 0);
  const totS = subsData.reduce((a, b) => a + b, 0);
  const totM = Object.values(minMap).reduce((a, b) => a + b, 0);
  const avgV = sortedDays.length > 0 ? Math.round(totV / sortedDays.length) : 0;
  const topTr = Object.entries(trafMap).sort((a, b) => b[1] - a[1])[0] || ['—', 0];

  const kv = document.getElementById('ch-kpi-views');
  const ks = document.getElementById('ch-kpi-subs');
  const km = document.getElementById('ch-kpi-hours');
  const ka = document.getElementById('ch-kpi-avg');
  if(kv) kv.textContent = totV.toLocaleString('pt-BR');
  if(ks) ks.textContent = (totS >= 0 ? '+' : '') + totS.toLocaleString('pt-BR');
  if(km) km.textContent = (totM / 60).toFixed(1) + ' h';
  if(ka) ka.textContent = avgV.toLocaleString('pt-BR') + '/dia';

  const tTitle = document.getElementById('ch-chart-title');
  if(tTitle) tTitle.textContent = `📈 ${chData.title} — ${pLabels[curSinglePeriod]} (${fLabels[curSingleFormat]})`;
  const trafTitle = document.getElementById('ch-chart-traffic-title');
  if(trafTitle) trafTitle.textContent = `🚦 Origem do Tráfego (${fLabels[curSingleFormat]})`;
  const topSrcEl = document.getElementById('ch-traffic-top-source');
  if(topSrcEl) topSrcEl.innerHTML = topTr[1] > 0 ? `Principal: <b>${topTr[0]}</b> (${topTr[1].toLocaleString('pt-BR')} views)` : 'Principal: <b>—</b>';

  // Render Line Chart
  const ctxV = document.getElementById('chChartViews');
  if(ctxV && window.Chart){
    if(chViewsChart) chViewsChart.destroy();
    chViewsChart = new Chart(ctxV, {
      type: 'line',
      data: {
        labels: sortedDays.map(d => d.slice(5)),
        datasets: [{
          label: 'Views',
          data: viewsData,
          borderColor: '#38BDF8',
          backgroundColor: 'rgba(56,189,248,0.12)',
          fill: true,
          tension: 0.35,
          borderWidth: 2.5,
          pointRadius: sortedDays.length > 60 ? 1 : 3,
          pointBackgroundColor: '#38BDF8'
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              label: ctx => `Views: ${ctx.parsed.y.toLocaleString('pt-BR')}`
            }
          }
        },
        scales: {
          x: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#94A3B8', font: { size: 10 }, maxTicksLimit: 14 } },
          y: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#94A3B8', font: { size: 10 } } }
        }
      }
    });
  }

  // Render Subs Bar Chart
  const ctxS = document.getElementById('chChartSubs');
  if(ctxS && window.Chart){
    if(chSubsChart) chSubsChart.destroy();
    chSubsChart = new Chart(ctxS, {
      type: 'bar',
      data: {
        labels: sortedDays.map(d => d.slice(5)),
        datasets: [{
          label: 'Saldo Inscritos',
          data: subsData,
          backgroundColor: subsData.map(v => v >= 0 ? '#10B981' : '#F43F5E'),
          borderRadius: 4
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          x: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#94A3B8', font: { size: 10 }, maxTicksLimit: 14 } },
          y: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#94A3B8', font: { size: 10 } } }
        }
      }
    });
  }

  // Render Traffic Doughnut
  const ctxT = document.getElementById('chChartTraffic');
  if(ctxT && window.Chart){
    if(chTrafficChart) chTrafficChart.destroy();
    let tLabels = Object.keys(trafMap);
    let tData = Object.values(trafMap);
    let tColors = ['#38BDF8','#10B981','#A855F7','#F59E0B','#F43F5E','#E2E8F0','#64748B','#3B82F6','#F97316','#06B6D4'];

    if(tData.length === 0){
      tLabels = ['Nenhum tráfego para este formato/período'];
      tData = [1];
      tColors = ['#334155'];
    }

    chTrafficChart = new Chart(ctxT, {
      type: 'doughnut',
      data: {
        labels: tLabels,
        datasets: [{
          data: tData,
          backgroundColor: tColors,
          borderWidth: 0
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { position: 'bottom', labels: { color: '#94A3B8', boxWidth: 10, font: { size: 10 } } },
          tooltip: {
            callbacks: {
              label: ctx => {
                if(tLabels[0].startsWith('Nenhum')) return ' 0 views';
                const v = ctx.parsed;
                const tot = tData.reduce((a,b)=>a+b, 0);
                const pct = tot > 0 ? ((v / tot) * 100).toFixed(1) : '0';
                return ` ${ctx.label}: ${v.toLocaleString('pt-BR')} views (${pct}%)`;
              }
            }
          }
        }
      }
    });
  }
}

// Gráficos da Visão Geral Consolidada
function setGeralChartPeriod(p, btn){
  curGeralPeriod = p;
  document.querySelectorAll('#geral-tab-charts .period-btn').forEach(b => b.classList.toggle('active', b === btn));
  updateGeralCharts();
}

function setGeralChartFormat(f, btn){
  curGeralFormat = f;
  document.querySelectorAll('#geral-tab-charts .format-btn').forEach(b => b.classList.toggle('active', b === btn));
  updateGeralCharts();
}

function setGeralChartChannel(ch, btn){
  curGeralChannel = ch;
  document.querySelectorAll('#geral-tab-charts .ch-chip').forEach(b => b.classList.toggle('active', b.dataset.ch === ch));
  updateGeralCharts();
}

function updateGeralCharts(){
  const raw = window.CHANNELS_TIMESERIES || {};
  const cutoff = getCutoffDate(curGeralPeriod);

  const dayMap = {}, subMap = {}, minMap = {}, trafMap = {};
  const chList = (curGeralChannel === 'all') ? Object.values(raw) : [raw[curGeralChannel]].filter(Boolean);

  chList.forEach(ch => {
    (ch.history_lifetime || ch.history_30d || []).forEach(h => {
      if(h.day < cutoff) return;
      if(curGeralFormat !== 'all' && h.type && h.type !== curGeralFormat) return;
      dayMap[h.day] = (dayMap[h.day] || 0) + (h.views || 0);
      subMap[h.day] = (subMap[h.day] || 0) + (h.net_subs || 0);
      minMap[h.day] = (minMap[h.day] || 0) + (h.minutes || 0);
    });

    (ch.traffic_sources_lifetime || ch.traffic_sources_30d || []).forEach(t => {
      if(t.day && t.day < cutoff) return;
      if(curGeralFormat !== 'all' && t.type && t.type !== curGeralFormat) return;
      trafMap[t.label] = (trafMap[t.label] || 0) + (t.views || 0);
    });
  });

  const sortedDays = Object.keys(dayMap).sort();
  const viewsData = sortedDays.map(d => dayMap[d]);
  const subsData = sortedDays.map(d => subMap[d]);

  const totV = viewsData.reduce((a, b) => a + b, 0);
  const totS = subsData.reduce((a, b) => a + b, 0);
  const totM = Object.values(minMap).reduce((a, b) => a + b, 0);
  const avgV = sortedDays.length > 0 ? Math.round(totV / sortedDays.length) : 0;
  const topTr = Object.entries(trafMap).sort((a, b) => b[1] - a[1])[0] || ['—', 0];

  const kv = document.getElementById('geral-kpi-views');
  const ks = document.getElementById('geral-kpi-subs');
  const km = document.getElementById('geral-kpi-hours');
  const ka = document.getElementById('geral-kpi-avg');
  if(kv) kv.textContent = totV.toLocaleString('pt-BR');
  if(ks) ks.textContent = (totS >= 0 ? '+' : '') + totS.toLocaleString('pt-BR');
  if(km) km.textContent = (totM / 60).toFixed(1) + ' h';
  if(ka) ka.textContent = avgV.toLocaleString('pt-BR') + '/dia';

  const titleEl = document.getElementById('geral-chart-title');
  if(titleEl){
    const chName = (curGeralChannel === 'all') ? 'Todos os Canais' : (raw[curGeralChannel]?.title || curGeralChannel);
    titleEl.textContent = `📈 ${chName} — ${pLabels[curGeralPeriod]} (${fLabels[curGeralFormat]})`;
  }
  const trafTitleEl = document.getElementById('geral-chart-traffic-title');
  if(trafTitleEl) trafTitleEl.textContent = `🚦 Origem do Tráfego (${fLabels[curGeralFormat]})`;
  const topSrcEl = document.getElementById('geral-traffic-top-source');
  if(topSrcEl) topSrcEl.innerHTML = topTr[1] > 0 ? `Principal: <b>${topTr[0]}</b> (${topTr[1].toLocaleString('pt-BR')} views)` : 'Principal: <b>—</b>';

  // Render Line Chart
  const ctxV = document.getElementById('geralChartViews');
  if(ctxV && window.Chart){
    if(geralViewsChart) geralViewsChart.destroy();
    geralViewsChart = new Chart(ctxV, {
      type: 'line',
      data: {
        labels: sortedDays.map(d => d.slice(5)),
        datasets: [{
          label: 'Views',
          data: viewsData,
          borderColor: '#38BDF8',
          backgroundColor: 'rgba(56,189,248,0.12)',
          fill: true,
          tension: 0.35,
          borderWidth: 2.5,
          pointRadius: sortedDays.length > 60 ? 1 : 3,
          pointBackgroundColor: '#38BDF8'
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              label: ctx => `Views: ${ctx.parsed.y.toLocaleString('pt-BR')}`
            }
          }
        },
        scales: {
          x: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#94A3B8', font: { size: 10 }, maxTicksLimit: 14 } },
          y: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#94A3B8', font: { size: 10 } } }
        }
      }
    });
  }

  // Render Subs Bar Chart
  const ctxS = document.getElementById('geralChartSubs');
  if(ctxS && window.Chart){
    if(geralSubsChart) geralSubsChart.destroy();
    geralSubsChart = new Chart(ctxS, {
      type: 'bar',
      data: {
        labels: sortedDays.map(d => d.slice(5)),
        datasets: [{
          label: 'Saldo Inscritos',
          data: subsData,
          backgroundColor: subsData.map(v => v >= 0 ? '#10B981' : '#F43F5E'),
          borderRadius: 4
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          x: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#94A3B8', font: { size: 10 }, maxTicksLimit: 14 } },
          y: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#94A3B8', font: { size: 10 } } }
        }
      }
    });
  }

  // Render Traffic Doughnut
  const ctxT = document.getElementById('geralChartTraffic');
  if(ctxT && window.Chart){
    if(geralTrafficChart) geralTrafficChart.destroy();
    let tLabels = Object.keys(trafMap);
    let tData = Object.values(trafMap);
    let tColors = ['#38BDF8','#10B981','#A855F7','#F59E0B','#F43F5E','#E2E8F0','#64748B','#3B82F6','#F97316','#06B6D4'];

    if(tData.length === 0){
      tLabels = ['Nenhum tráfego para este formato/período'];
      tData = [1];
      tColors = ['#334155'];
    }

    geralTrafficChart = new Chart(ctxT, {
      type: 'doughnut',
      data: {
        labels: tLabels,
        datasets: [{
          data: tData,
          backgroundColor: tColors,
          borderWidth: 0
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { position: 'bottom', labels: { color: '#94A3B8', boxWidth: 10, font: { size: 10 } } },
          tooltip: {
            callbacks: {
              label: ctx => {
                if(tLabels[0].startsWith('Nenhum')) return ' 0 views';
                const v = ctx.parsed;
                const tot = tData.reduce((a,b)=>a+b, 0);
                const pct = tot > 0 ? ((v / tot) * 100).toFixed(1) : '0';
                return ` ${ctx.label}: ${v.toLocaleString('pt-BR')} views (${pct}%)`;
              }
            }
          }
        }
      }
    });
  }
}

// History & URL Popstate
window.addEventListener('popstate', () => {
  const params = new URLSearchParams(location.search);
  const ch = params.get('channel');
  const tab = params.get('tab');

  if(ch === 'geral'){
    openChannel('geral', false);
    if(tab) switchGeralMainTab(tab, document.getElementById('btn-geral-tab-' + tab));
  } else if(ch && ch !== 'home' && window.CHANNELS_TIMESERIES && window.CHANNELS_TIMESERIES[ch]){
    openChannel(ch, false);
    if(tab) switchChannelSubTab(tab, document.getElementById('btn-ch-tab-' + tab));
  } else {
    openChannel('home', false);
  }
});

window.addEventListener('DOMContentLoaded', () => {
  const params = new URLSearchParams(location.search);
  const ch = params.get('channel');
  const tab = params.get('tab');

  if(ch === 'geral'){
    openChannel('geral', false);
    if(tab) switchGeralMainTab(tab, document.getElementById('btn-geral-tab-' + tab));
  } else if(ch && ch !== 'home' && window.CHANNELS_TIMESERIES && window.CHANNELS_TIMESERIES[ch]){
    openChannel(ch, false);
    if(tab) switchChannelSubTab(tab, document.getElementById('btn-ch-tab-' + tab));
  } else {
    openChannel('home', false);
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
    total_48h_all = sum(c.get("views_48h_canal", 0) for c in channels_data)
    total_subs_all = sum(c.get("inscritos", 0) for c in channels_data)
    total_sched_count = len(all_scheduled) if all_scheduled else sum(c.get("total_videos_agendados", 0) for c in channels_data)

    # Garante avatar_url padrão
    for c in channels_data:
        if not c.get("avatar_url"):
            c["avatar_url"] = DEFAULT_AVATARS.get(c.get("id"), "")

    # =========================================================================
    # 1. TELA INICIAL (HUB) - CARDS COM FOTO DE PERFIL E "GERAL" NO MEIO
    # =========================================================================
    hub_cards_html = []
    
    # Criamos os cards dos canais e colocamos o card "Geral" no meio (índice 3)
    geral_card_html = f"""
<div class="hub-card card-geral" onclick="openChannel('geral')">
  <div>
    <div class="card-top">
      <div class="card-avatar-wrap">
        <div class="card-avatar geral-icon">🌐</div>
        <span class="card-status-dot online"></span>
      </div>
      <div class="card-meta">
        <div class="card-name">🌐 Visão Geral</div>
        <div class="card-subtext">Fábrica Consolidada · <b>7 Canais</b></div>
      </div>
    </div>
    <div class="card-metrics">
      <div class="cm-item"><span class="cm-lbl">Ritmo Geral</span><b class="cm-val cyan">+{total_vph_60m}/h</b></div>
      <div class="cm-item"><span class="cm-lbl">Views 48h</span><b class="cm-val">+{total_48h_all:,}</b></div>
      <div class="cm-item"><span class="cm-lbl">Inscritos</span><b class="cm-val">{total_subs_all:,}</b></div>
    </div>
  </div>
  <div class="card-footer">
    <span>Abrir Painel Geral</span>
    <span>→</span>
  </div>
</div>"""

    for idx, c in enumerate(channels_data):
        if idx == 3:
            hub_cards_html.append(geral_card_html)

        on = (c.get("status_conexao") == "ONLINE")
        st_dot = "online" if on else "offline"
        vph_txt = f"+{c.get('vph_60m', 0)}/h"
        v48_txt = f"+{c.get('views_48h_canal', 0):,}"
        subs_txt = f"{c.get('inscritos', 0):,}"

        hub_cards_html.append(f"""
<div class="hub-card" data-grupo="{c['grupo_slug']}" onclick="openChannel('{c['id']}')">
  <div>
    <div class="card-top">
      <div class="card-avatar-wrap">
        <img src="{_e(c['avatar_url'])}" class="card-avatar" alt="" loading="lazy">
        <span class="card-status-dot {st_dot}"></span>
      </div>
      <div class="card-meta">
        <div class="card-name">{_e(c['canal_titulo'])}</div>
        <div class="card-subtext">{_e(c['handle'])} · <span class="pill pill-{c['grupo_slug']}">{_e(c['grupo'])}</span></div>
      </div>
    </div>
    <div class="card-metrics">
      <div class="cm-item"><span class="cm-lbl">Ritmo</span><b class="cm-val cyan">{vph_txt}</b></div>
      <div class="cm-item"><span class="cm-lbl">48 horas</span><b class="cm-val">{v48_txt}</b></div>
      <div class="cm-item"><span class="cm-lbl">Inscritos</span><b class="cm-val">{subs_txt}</b></div>
    </div>
  </div>
  <div class="card-footer">
    <span>Ver Canal</span>
    <span>→</span>
  </div>
</div>""")

    if len(channels_data) <= 3:
        hub_cards_html.append(geral_card_html)

    # =========================================================================
    # QUICK SWITCHER DE CANAIS (Para alternar 1-click no topo)
    # =========================================================================
    switcher_items = [
        f'<button class="btn-back-hub" onclick="openChannel(\'home\')">← Voltar aos Canais</button>',
        '<div class="ch-quick-switcher">',
        f'<button class="ch-switch-btn" data-ch="geral" onclick="openChannel(\'geral\')">🌐 Geral</button>'
    ]
    for c in channels_data:
        switcher_items.append(
            f'<button class="ch-switch-btn" data-ch="{c["id"]}" onclick="openChannel(\'{c["id"]}\')"><img src="{_e(c["avatar_url"])}" alt=""> {_e(c["canal_titulo"])}</button>'
        )
    switcher_items.append('</div>')
    quick_switcher_html = "".join(switcher_items)

    # =========================================================================
    # 2. VISÃO EXCLUSIVA DO CANAL: BANNERS E SUB-CONTEÚDOS
    # =========================================================================
    ch_banners_html = []
    ch_r10_cards_html = []
    ch_top3_grids_html = []
    ch_sched_items_html = []

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

    for c in channels_data:
        on = (c.get("status_conexao") == "ONLINE")
        st_pill = '<span class="pill pill-green">online</span>' if on else f'<span class="pill pill-red">{_e(c.get("status_conexao"))}</span>'
        handle_url = f"https://www.youtube.com/{c.get('handle', '')}" if c.get('handle') else "https://www.youtube.com"
        impr = f"{c.get('impressions_7d_canal'):,}" if c.get("impressions_7d_canal") is not None else '<span class="pending">⏳ pendente</span>'
        ctr = f"<b>{c.get('ctr_7d_canal'):.2f}%</b>" if c.get("ctr_7d_canal") is not None else '<span class="pending">⏳ pendente</span>'
        ret_pct = c.get('retention_pct_7d_canal')
        ret = (f"<b>{ret_pct:.1f}%</b> <span class='sub'>({c.get('retention_dur_7d_canal', '0m 00s')})</span>"
               if (ret_pct is not None and c.get("views_7d_canal", 0) > 0) else '<span class="sub">—</span>')

        # Banner
        ch_banners_html.append(f"""
<div class="ch-banner" data-canal="{c['id']}" style="display:none">
  <div class="ch-banner-left">
    <img src="{_e(c['avatar_url'])}" class="ch-banner-avatar" alt="" loading="lazy">
    <div class="ch-banner-info">
      <h2>{_e(c['canal_titulo'])} {st_pill}</h2>
      <div class="meta-row">
        <span>{_e(c['handle'])}</span> · 
        <span class="pill pill-{c['grupo_slug']}">{_e(c['grupo'])}</span> · 
        <a href="{_e(handle_url)}" target="_blank" rel="noopener" style="color:var(--cyan);font-weight:600">Abrir no YouTube ↗</a>
      </div>
    </div>
  </div>
  <div class="vph-badge">
    <span>⚡</span> Ritmo: <b>+{c.get('vph_60m', 0)} views/h</b>
  </div>
</div>
<div class="ch-kpi-bar" data-canal="{c['id']}" style="display:none">
  <div class="ch-kpi-box"><div class="ch-kpi-lbl">Ritmo VPH</div><div class="ch-kpi-val" style="color:var(--cyan)">+{c.get('vph_60m', 0)}/h</div></div>
  <div class="ch-kpi-box"><div class="ch-kpi-lbl">60 min</div><div class="ch-kpi-val">+{c.get('views_60m_canal', 0):,}</div></div>
  <div class="ch-kpi-box"><div class="ch-kpi-lbl">48 horas</div><div class="ch-kpi-val">+{c.get('views_48h_canal', 0):,}</div></div>
  <div class="ch-kpi-box"><div class="ch-kpi-lbl">Views 7d</div><div class="ch-kpi-val">{c.get('views_7d_canal', 0):,}</div></div>
  <div class="ch-kpi-box"><div class="ch-kpi-lbl">Inscritos</div><div class="ch-kpi-val">{c.get('inscritos', 0):,}</div></div>
  <div class="ch-kpi-box"><div class="ch-kpi-lbl">Vídeos</div><div class="ch-kpi-val">{c.get('total_videos_publicos', 0)} públ.</div></div>
  <div class="ch-kpi-box"><div class="ch-kpi-lbl">CTR 7d</div><div class="ch-kpi-val">{ctr}</div></div>
  <div class="ch-kpi-box"><div class="ch-kpi-lbl">Retenção 7d</div><div class="ch-kpi-val">{ret}</div></div>
</div>""")

        # 1 de 10 do canal
        r10 = c.get("rank_1_de_10")
        if not r10:
            ch_r10_cards_html.append(f"""
<div class="r10-card ch-r10-card" data-canal="{c['id']}" style="display:none">
  <div class="empty-mini">Nenhum vídeo recente com histórico suficiente para comparação.</div>
</div>""")
        else:
            r = r10.get("rank", 10)
            out_of = r10.get("out_of", 10)
            diff = r10.get("diff_pct", 0.0)
            if r == 1:
                b_cls = "r10-b1"; b_txt = f"🏆 1 de {out_of} — Top Desempenho!"
            elif r <= 3:
                b_cls = "r10-b2"; b_txt = f"⭐ {r} de {out_of} — Acima da Média"
            elif r <= 7:
                b_cls = "r10-b3"; b_txt = f"📊 {r} de {out_of} — Na Média"
            else:
                b_cls = "r10-b4"; b_txt = f"⚠️ {r} de {out_of} — Abaixo da Média"

            diff_sign = "+" if diff > 0 else ""
            diff_color = "var(--green)" if diff > 0 else ("var(--red)" if diff < 0 else "var(--muted)")

            ch_r10_cards_html.append(f"""
<div class="r10-card ch-r10-card" data-canal="{c['id']}" style="display:none">
  <div>
    <div class="r10-head">
      <div class="r10-ch-info">
        <h4>{_e(c['canal_titulo'])}</h4>
        <div class="sub">{_e(c['handle'])}</div>
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

        # Top 3 do canal
        pend = _e(c.get("reach_message") or "Aguardando 1º relatório do Google (24–48h)")
        ch_top3_grids_html.append(f"""
<div class="top3 ch-top3-grid" data-canal="{c['id']}" style="display:none;padding:0">
  <div class="box"><h4>🎯 Maior retenção (7d)</h4>{rank_list(c.get('top3_retencao_7d', []), fmt_ret, 'Sem views nos últimos 7 dias.')}</div>
  <div class="box"><h4>👁️ Mais views (7d)</h4>{rank_list(c.get('top3_views_7d', []), lambda it: f'<span class="hi">{it["views_7d"]:,} views</span> · ret. {it["retention_pct"]:.1f}%', 'Sem views nos últimos 7 dias.')}</div>
  <div class="box"><h4>🖱️ Maior CTR (7d)</h4>{rank_list(c.get('top3_ctr_7d', []), lambda it: f'<span class="hi">{it["ctr_7d"]:.2f}%</span> · {it["impressions_7d"]:,} impr.', '⏳ ' + pend)}</div>
  <div class="box"><h4>📢 Mais impressões (7d)</h4>{rank_list(c.get('top3_impressoes_7d', []), lambda it: f'<span class="hi">{it["impressions_7d"]:,}</span> impr. · CTR {it["ctr_7d"]:.2f}%', '⏳ ' + pend)}</div>
</div>""")

        # Agendados do canal
        for sv in c.get("videos_agendados_fila", []):
            p_iso = sv.get("published_at", "")
            try:
                p_dt = datetime.fromisoformat(p_iso.replace("Z", "+00:00")).astimezone(timezone(timedelta(hours=-3)))
                t_str = p_dt.strftime("%d/%m/%Y às %H:%M BRT")
            except Exception:
                t_str = p_iso[:16]

            ch_sched_items_html.append(f"""
<div class="cal-row ch-sched-item" data-canal="{c['id']}" style="display:none">
  <div class="cal-time">{t_str}</div>
  <img src="{_e(sv.get('thumbnail'))}" class="cal-thumb" alt="" loading="lazy">
  <div class="cal-info">
    <h4>{_e(sv.get('title'))}</h4>
    <div class="sub">{_e(c['canal_titulo'])} · {_e(c['handle'])}</div>
  </div>
</div>""")

    # =========================================================================
    # VÍDEOS AO VIVO (Rows com data-canal e data-grupo)
    # =========================================================================
    live = [v for c in channels_data for v in c.get("videos_ao_vivo_movimento", [])]
    single_live_html = []
    geral_live_html = []

    for v in live[:150]:
        d60 = v.get("delta_60m")
        d48 = v.get("delta_48h") or 0
        tot = v.get("views_total") or 0
        d60_num = d60 if d60 is not None else 0
        d60_txt = f"+{d60:,}" if d60 is not None else "—"
        badge = '<span class="pill pill-amber">novo &lt;48h</span>' if v.get("is_pub_last_48h") else ""

        row_html = f"""
<div class="lv-row" data-canal="{v.get('canal_id') or v.get('canal_slug') or ''}" data-grupo="{v['grupo_slug']}" data-d60="{d60_num}" data-d48="{d48}" data-total="{tot}">
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
</div>"""
        geral_live_html.append(row_html)

    # Para a lista do canal individual, usamos canais com id direto no data-canal
    for c in channels_data:
        for v in c.get("videos_ao_vivo_movimento", []):
            d60 = v.get("delta_60m")
            d48 = v.get("delta_48h") or 0
            tot = v.get("views_total") or 0
            d60_num = d60 if d60 is not None else 0
            d60_txt = f"+{d60:,}" if d60 is not None else "—"
            badge = '<span class="pill pill-amber">novo &lt;48h</span>' if v.get("is_pub_last_48h") else ""

            single_live_html.append(f"""
<div class="lv-row" data-canal="{c['id']}" data-grupo="{c['grupo_slug']}" data-d60="{d60_num}" data-d48="{d48}" data-total="{tot}">
  <div class="lv-rank">·</div>
  <img class="lv-thumb" src="{_e(v.get('thumbnail'))}" alt="" loading="lazy">
  <div class="lv-info">
    <a class="lv-title" href="{_e(v['url'])}" target="_blank" rel="noopener">{_e(v['title'])}</a>
    <div class="lv-meta"><span>{_e(v.get('published_formatted'))}</span>{badge}</div>
  </div>
  <div class="lv-metrics">
    {_metric('60 min', 'd60', d60_txt, d60_num > 0)}
    {_metric('48h', 'd48', f'+{d48:,}', d48 > 0)}
    {_metric('Total', 'total', f'{tot:,}', False)}
  </div>
</div>""")

    # =========================================================================
    # TABELA COMPARATIVA (Visão Geral)
    # =========================================================================
    cmp_rows = []
    for c in channels_data:
        on = (c.get("status_conexao") == "ONLINE")
        st = '<span class="pill pill-green">online</span>' if on else f'<span class="pill pill-red">{_e(c.get("status_conexao"))}</span>'
        impr = f"{c.get('impressions_7d_canal'):,}" if c.get("impressions_7d_canal") is not None else '<span class="pending">⏳ aguardando Google</span>'
        ctr = f"<b>{c.get('ctr_7d_canal'):.2f}%</b>" if c.get("ctr_7d_canal") is not None else '<span class="pending">⏳ aguardando Google</span>'
        ret_pct = c.get('retention_pct_7d_canal')
        ret = (f"<b>{ret_pct:.1f}%</b> <span class='sub'>({c.get('retention_dur_7d_canal', '0m 00s')})</span>"
               if (ret_pct is not None and c.get("views_7d_canal", 0) > 0) else '<span class="sub">—</span>')
        vph_txt = f"+{c.get('vph_60m', 0)}/h"
        cmp_rows.append(f"""
<tr data-grupo="{c['grupo_slug']}" onclick="openChannel('{c['id']}')" style="cursor:pointer">
  <td class="cell-ch">
    <div class="ch-name" style="display:flex;align-items:center;gap:8px">
      <img src="{_e(c['avatar_url'])}" style="width:24px;height:24px;border-radius:50%;object-fit:cover" alt="">
      {_e(c['canal_titulo'])} {st}
    </div>
    <div class="sub">{_e(c['handle'])} · <span class="pill pill-{c['grupo_slug']}">{_e(c['grupo'])}</span></div>
  </td>
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

    # =========================================================================
    # CARDS TOP 3 (Visão Geral)
    # =========================================================================
    cards_geral_top3 = []
    for c in channels_data:
        if c.get("status_conexao") != "ONLINE":
            cards_geral_top3.append(f"""
<details class="ch off" data-grupo="{c['grupo_slug']}" open>
  <summary><div class="ch-head"><span class="pill pill-{c['grupo_slug']}">{_e(c['grupo'])}</span><h3>{_e(c['canal_titulo'])}<small>{_e(c['nome_projeto'])}</small></h3></div><span class="pill pill-red">desconectado</span></summary>
  <div class="off-msg"><b>Motivo:</b> {_e(c.get('erro'))}<br>Rode no PC: <code>{_e(c.get('auth_bat'))}</code></div>
</details>""")
            continue
        pend = _e(c.get("reach_message") or "Aguardando 1º relatório do Google (24–48h)")
        vph_badge = f'<span class="pill pill-green">⚡ +{c.get("vph_60m", 0)}/h</span>'
        cards_geral_top3.append(f"""
<details class="ch" data-grupo="{c['grupo_slug']}" open>
  <summary>
    <div class="ch-head" style="display:flex;align-items:center;gap:10px">
      <img src="{_e(c['avatar_url'])}" style="width:36px;height:36px;border-radius:50%;object-fit:cover" alt="">
      <div>
        <h3>{_e(c['canal_titulo'])} {vph_badge}</h3>
        <small>{_e(c['handle'])} · <span class="pill pill-{c['grupo_slug']}">{_e(c['grupo'])}</span></small>
      </div>
    </div>
    <div class="ch-stats"><span>👁️ <b>{c.get('views_7d_canal', 0):,}</b> 7d</span><span>⚡ <b>+{c.get('views_48h_canal', 0):,}</b> 48h</span><span>👥 <b>{c.get('inscritos', 0):,}</b></span></div>
  </summary>
  <div class="top3">
    <div class="box"><h4>🎯 Maior retenção (7d)</h4>{rank_list(c.get('top3_retencao_7d', []), fmt_ret, 'Sem views nos últimos 7 dias.')}</div>
    <div class="box"><h4>👁️ Mais views (7d)</h4>{rank_list(c.get('top3_views_7d', []), lambda it: f'<span class="hi">{it["views_7d"]:,} views</span> · ret. {it["retention_pct"]:.1f}%', 'Sem views nos últimos 7 dias.')}</div>
    <div class="box"><h4>🖱️ Maior CTR (7d)</h4>{rank_list(c.get('top3_ctr_7d', []), lambda it: f'<span class="hi">{it["ctr_7d"]:.2f}%</span> · {it["impressions_7d"]:,} impr.', '⏳ ' + pend)}</div>
    <div class="box"><h4>📢 Mais impressões (7d)</h4>{rank_list(c.get('top3_impressoes_7d', []), lambda it: f'<span class="hi">{it["impressions_7d"]:,}</span> impr. · CTR {it["ctr_7d"]:.2f}%', '⏳ ' + pend)}</div>
  </div>
</details>""")

    # =========================================================================
    # 1 DE 10 (Visão Geral)
    # =========================================================================
    rank10_cards_geral = []
    for c in channels_data:
        r10 = c.get("rank_1_de_10")
        if not r10:
            rank10_cards_geral.append(f"""
<div class="r10-card" data-grupo="{c['grupo_slug']}" onclick="openChannel('{c['id']}')" style="cursor:pointer">
  <div class="r10-head">
    <div class="r10-ch-info"><h4>{_e(c['canal_titulo'])}</h4><div class="sub">{_e(c['handle'])}</div></div>
    <span class="pill pill-{c['grupo_slug']}">{_e(c['grupo'])}</span>
  </div>
  <div class="empty-mini">Nenhum vídeo recente com histórico suficiente para comparação.</div>
</div>""")
            continue

        r = r10.get("rank", 10)
        out_of = r10.get("out_of", 10)
        diff = r10.get("diff_pct", 0.0)
        if r == 1:
            b_cls = "r10-b1"; b_txt = f"🏆 1 de {out_of} — Top Desempenho!"
        elif r <= 3:
            b_cls = "r10-b2"; b_txt = f"⭐ {r} de {out_of} — Acima da Média"
        elif r <= 7:
            b_cls = "r10-b3"; b_txt = f"📊 {r} de {out_of} — Na Média"
        else:
            b_cls = "r10-b4"; b_txt = f"⚠️ {r} de {out_of} — Abaixo da Média"

        diff_sign = "+" if diff > 0 else ""
        diff_color = "var(--green)" if diff > 0 else ("var(--red)" if diff < 0 else "var(--muted)")

        rank10_cards_geral.append(f"""
<div class="r10-card" data-grupo="{c['grupo_slug']}">
  <div>
    <div class="r10-head" onclick="openChannel('{c['id']}')" style="cursor:pointer">
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

    # =========================================================================
    # CALENDÁRIO UNIFICADO (Visão Geral)
    # =========================================================================
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

    # =========================================================================
    # TIMESERIES DATA PARA CHART.JS
    # =========================================================================
    timeseries_data = {
        c["id"]: {
            "title": c.get("canal_titulo"),
            "handle": c.get("handle"),
            "avatar_url": c.get("avatar_url"),
            "group_slug": c.get("grupo_slug"),
            "history_lifetime": c.get("history_lifetime", []),
            "traffic_sources_lifetime": c.get("traffic_sources_lifetime", []),
        }
        for c in channels_data
    }
    timeseries_json = json.dumps(timeseries_data, ensure_ascii=False)

    geral_chart_chips = [
        '<button class="ch-chip active" data-ch="all" onclick="setGeralChartChannel(\'all\', this)">Todos os Canais (Consolidado)</button>'
    ]
    for c in channels_data:
        geral_chart_chips.append(
            f'<button class="ch-chip" data-ch="{c["id"]}" onclick="setGeralChartChannel(\'{c["id"]}\', this)">{_e(c["canal_titulo"])}</button>'
        )

    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
<meta http-equiv="refresh" content="600">
<meta name="theme-color" content="#090D16">
<meta name="apple-mobile-web-app-capable" content="yes">
<title>Painel Canais Dark — Multi-Canal YouTube Studio</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;700;800&display=swap" rel="stylesheet">
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
<style>{CSS}</style>
</head>
<body>
<div class="wrap">

  <!-- ================================================================= -->
  <!-- 1. TELA INICIAL (HUB / SELETOR DE CANAIS)                         -->
  <!-- ================================================================= -->
  <div class="view-section active" id="view-hub">
    <div class="hub-hero">
      <div>
        <h1>⚡ Dark Factory — Multi-Canal Studio</h1>
        <div class="meta"><b>{online}/{total_ch}</b> canais online · Atualizado <b>{now_str} BRT</b> · 100% na Nuvem</div>
        <div class="hub-chips">
          <button class="chip active" onclick="filterHubGroup('all', this)">Todos os Canais ({total_ch})</button>
          <button class="chip" onclick="filterHubGroup('pessoal', this)">Pessoais ({n_pessoal})</button>
          <button class="chip" onclick="filterHubGroup('gvg', this)">Startup GVG ({n_gvg})</button>
        </div>
      </div>
      <div class="vph-badge" style="font-size:14px;padding:8px 16px">
        <span>⚡</span> Ritmo da Fábrica: <b>+{total_vph_60m} views/h</b>
      </div>
    </div>

    <!-- Grid de Canais com Foto de Perfil e Geral no meio -->
    <div class="hub-grid">
      {''.join(hub_cards_html)}
    </div>
  </div>

  <!-- ================================================================= -->
  <!-- 2. VISÃO EXCLUSIVA DO CANAL SELECIONADO                           -->
  <!-- ================================================================= -->
  <div class="view-section" id="view-channel">
    <!-- Quick Switcher Bar -->
    <div class="channel-nav-bar">
      {quick_switcher_html}
    </div>

    <!-- Banners e Mini KPIs do Canal -->
    {''.join(ch_banners_html)}

    <!-- Sub-Abas do Canal -->
    <div class="sub-nav">
      <button class="sub-tab-btn active" id="btn-ch-tab-live" onclick="switchChannelSubTab('live', this)">⚡ Ao Vivo & Vídeos</button>
      <button class="sub-tab-btn" id="btn-ch-tab-charts" onclick="switchChannelSubTab('charts', this)">📈 Gráficos & Analytics</button>
      <button class="sub-tab-btn" id="btn-ch-tab-rank10" onclick="switchChannelSubTab('rank10', this)">🎯 Lançamento (1 de 10)</button>
      <button class="sub-tab-btn" id="btn-ch-tab-top3" onclick="switchChannelSubTab('top3', this)">🏆 Top 3 (7 dias)</button>
      <button class="sub-tab-btn" id="btn-ch-tab-calendar" onclick="switchChannelSubTab('calendar', this)">📅 Próximas Estreias</button>
    </div>

    <!-- SUB-ABA 1: AO VIVO & VÍDEOS DO CANAL -->
    <div class="sub-content active" id="ch-tab-live">
      <div class="sec">
        <div class="sec-top">
          <div>
            <div class="sec-title">🔥 Vídeos com movimentação recente no canal</div>
            <div class="sec-hint">Views ganhas em 60 min e 48 horas acumuladas ({win_48_txt})</div>
          </div>
          <div class="seg" style="max-width:440px">
            <button class="active" id="ch-seg-d60" onclick="setSingleChannelSort('d60', this)">Últimos 60 min</button>
            <button id="ch-seg-d48" onclick="setSingleChannelSort('d48', this)">Últimas 48h</button>
            <button id="ch-seg-total" onclick="setSingleChannelSort('total', this)">Recentes</button>
          </div>
        </div>
        <div class="lv-count" id="ch-live-count" style="font-size:12px;color:var(--muted);margin-bottom:8px"></div>
        <div id="ch-live-list">{''.join(single_live_html)}</div>
        <div class="empty" id="ch-live-empty" style="display:none"></div>
      </div>
    </div>

    <!-- SUB-ABA 2: GRÁFICOS & ANALYTICS DO CANAL -->
    <div class="sub-content" id="ch-tab-charts">
      <div class="filters-panel">
        <div class="fg-row">
          <div class="fg-lbl">📅 Período</div>
          <div class="fg-ctrl seg">
            <button class="period-btn" data-p="7d" onclick="setSingleChannelPeriod('7d', this)">7 dias</button>
            <button class="period-btn active" data-p="30d" onclick="setSingleChannelPeriod('30d', this)">30 dias</button>
            <button class="period-btn" data-p="month" onclick="setSingleChannelPeriod('month', this)">Este mês</button>
            <button class="period-btn" data-p="180d" onclick="setSingleChannelPeriod('180d', this)">180 dias</button>
            <button class="period-btn" data-p="year" onclick="setSingleChannelPeriod('year', this)">Este ano</button>
            <button class="period-btn" data-p="all" onclick="setSingleChannelPeriod('all', this)">Geral (Início)</button>
          </div>
        </div>
        <div class="fg-row" style="margin-bottom:0">
          <div class="fg-lbl">🎬 Formato</div>
          <div class="fg-ctrl seg" style="max-width:520px">
            <button class="format-btn active" data-f="all" onclick="setSingleChannelFormat('all', this)">Todos (Vídeos + Shorts)</button>
            <button class="format-btn" data-f="video" onclick="setSingleChannelFormat('video', this)">🎬 Só Vídeos (Longos)</button>
            <button class="format-btn" data-f="shorts" onclick="setSingleChannelFormat('shorts', this)">⚡ Só Shorts</button>
          </div>
        </div>
      </div>

      <div class="kpi-grid">
        <div class="kpi"><div class="kpi-val" id="ch-kpi-views">—</div><div class="kpi-lbl">Visualizações</div></div>
        <div class="kpi"><div class="kpi-val" id="ch-kpi-subs" style="color:var(--green)">—</div><div class="kpi-lbl">Saldo de Inscritos</div></div>
        <div class="kpi"><div class="kpi-val" id="ch-kpi-hours" style="color:var(--amber)">—</div><div class="kpi-lbl">Tempo de Exibição</div></div>
        <div class="kpi"><div class="kpi-val" id="ch-kpi-avg" style="color:var(--purple)">—</div><div class="kpi-lbl">Média Diária</div></div>
      </div>

      <div class="chart-card">
        <div class="chart-head"><h3 id="ch-chart-title">📈 Curva de Visualizações Diárias</h3></div>
        <div class="chart-box"><canvas id="chChartViews"></canvas></div>
      </div>

      <div class="charts-split">
        <div class="chart-card">
          <div class="chart-head"><h3>👥 Saldo Diário de Inscritos (+ / -)</h3></div>
          <div class="chart-box"><canvas id="chChartSubs"></canvas></div>
        </div>
        <div class="chart-card">
          <div class="chart-head">
            <h3 id="ch-chart-traffic-title">🚦 Origem do Tráfego</h3>
            <span class="sub" id="ch-traffic-top-source">Principal: <b>—</b></span>
          </div>
          <div class="chart-box"><canvas id="chChartTraffic"></canvas></div>
        </div>
      </div>
    </div>

    <!-- SUB-ABA 3: LANÇAMENTO 1 DE 10 DO CANAL -->
    <div class="sub-content" id="ch-tab-rank10">
      <div class="sec-top" style="margin-bottom:12px">
        <div>
          <div class="sec-title">🎯 Desempenho do Vídeo Mais Recente (1 de 10)</div>
          <div class="sec-hint">Compara as views do último vídeo com a média dos 10 vídeos anteriores do canal</div>
        </div>
      </div>
      {''.join(ch_r10_cards_html)}
    </div>

    <!-- SUB-ABA 4: TOP 3 DO CANAL -->
    <div class="sub-content" id="ch-tab-top3">
      <div class="sec-top" style="margin-bottom:12px">
        <div>
          <div class="sec-title">🏆 Top 3 do Canal nos Últimos 7 Dias</div>
          <div class="sec-hint">Retenção (com ≥{MIN_VIEWS_FOR_RETENTION_RANK} views), Views, CTR e Impressões</div>
        </div>
      </div>
      {''.join(ch_top3_grids_html)}
    </div>

    <!-- SUB-ABA 5: AGENDADOS DO CANAL -->
    <div class="sub-content" id="ch-tab-calendar">
      <div class="sec-top" style="margin-bottom:12px">
        <div>
          <div class="sec-title">📅 Próximas Estreias Agendadas deste Canal</div>
          <div class="sec-hint">Vídeos privados com data e horário programados de publicação</div>
        </div>
      </div>
      {''.join(ch_sched_items_html)}
      <div class="empty" id="ch-sched-empty" style="display:none">Nenhum vídeo agendado no momento para este canal.</div>
    </div>
  </div>

  <!-- ================================================================= -->
  <!-- 3. VISÃO GERAL CONSOLIDADA (TODOS OS CANAIS)                      -->
  <!-- ================================================================= -->
  <div class="view-section" id="view-geral">
    <!-- Quick Switcher Bar -->
    <div class="channel-nav-bar">
      {quick_switcher_html}
    </div>

    <!-- Topbar Consolidada -->
    <div class="topbar">
      <div class="topbar-main">
        <div>
          <h1>🌐 Painel Geral — Consolidado de Todos os Canais</h1>
          <div class="meta">Atualizado <b>{now_str} BRT</b> · <b>{online}/{total_ch}</b> online · Nuvem a cada 15–30 min</div>
        </div>
        <div class="vph-badge">
          <span>⚡</span> Ritmo da Fábrica: <b>+{total_vph_60m} views/hora</b>
        </div>
      </div>
      <div class="chips" id="geral-chips" style="margin-top:12px">
        <button class="chip active" onclick="filterGeralGroup('all', this)">Todos ({total_ch})</button>
        <button class="chip" onclick="filterGeralGroup('pessoal', this)">Pessoais ({n_pessoal})</button>
        <button class="chip" onclick="filterGeralGroup('gvg', this)">Startup GVG ({n_gvg})</button>
      </div>
    </div>

    <!-- Navegação da Visão Geral -->
    <div class="sub-nav">
      <button class="sub-tab-btn active" id="btn-geral-tab-live" onclick="switchGeralMainTab('live', this)">⚡ Radar ao Vivo</button>
      <button class="sub-tab-btn" id="btn-geral-tab-charts" onclick="switchGeralMainTab('charts', this)">📈 Gráficos & Histórico</button>
      <button class="sub-tab-btn" id="btn-geral-tab-rank10" onclick="switchGeralMainTab('rank10', this)">🎯 Lançamentos (1 de 10)</button>
      <button class="sub-tab-btn" id="btn-geral-tab-calendar" onclick="switchGeralMainTab('calendar', this)">📅 Calendário ({total_sched_count})</button>
    </div>

    <!-- GERAL TAB 1: RADAR AO VIVO -->
    <div class="sub-content active" id="geral-tab-live">
      <div class="sec">
        <div class="sec-top">
          <div>
            <div class="sec-title">🔥 Mais vistos agora — todos os canais</div>
            <div class="sec-hint">Views ganhas por vídeo público · janela acumulada: {win_48_txt}</div>
          </div>
          <div class="seg" style="max-width:440px">
            <button class="active" id="geral-seg-d60" onclick="setGeralSort('d60', this)">Últimos 60 min</button>
            <button id="geral-seg-d48" onclick="setGeralSort('d48', this)">Últimas 48h</button>
            <button id="geral-seg-total" onclick="setGeralSort('total', this)">Recentes</button>
          </div>
        </div>
        <div class="lv-count" id="geral-live-count" style="font-size:12px;color:var(--muted);margin-bottom:8px"></div>
        <div id="geral-live-list">{''.join(geral_live_html)}</div>
        <div class="empty" id="geral-live-empty" style="display:none"></div>
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
      {''.join(cards_geral_top3)}
    </div>

    <!-- GERAL TAB 2: GRÁFICOS & HISTÓRICO COM FILTROS AVANÇADOS -->
    <div class="sub-content" id="geral-tab-charts">
      <div class="filters-panel">
        <div class="fg-row">
          <div class="fg-lbl">📅 Período</div>
          <div class="fg-ctrl seg">
            <button class="period-btn" data-p="7d" onclick="setGeralChartPeriod('7d', this)">7 dias</button>
            <button class="period-btn active" data-p="30d" onclick="setGeralChartPeriod('30d', this)">30 dias</button>
            <button class="period-btn" data-p="month" onclick="setGeralChartPeriod('month', this)">Este mês</button>
            <button class="period-btn" data-p="180d" onclick="setGeralChartPeriod('180d', this)">180 dias</button>
            <button class="period-btn" data-p="year" onclick="setGeralChartPeriod('year', this)">Este ano</button>
            <button class="period-btn" data-p="all" onclick="setGeralChartPeriod('all', this)">Geral (Início)</button>
          </div>
        </div>
        <div class="fg-row">
          <div class="fg-lbl">🎬 Formato</div>
          <div class="fg-ctrl seg" style="max-width:520px">
            <button class="format-btn active" data-f="all" onclick="setGeralChartFormat('all', this)">Todos (Vídeos + Shorts)</button>
            <button class="format-btn" data-f="video" onclick="setGeralChartFormat('video', this)">🎬 Só Vídeos (Longos)</button>
            <button class="format-btn" data-f="shorts" onclick="setGeralChartFormat('shorts', this)">⚡ Só Shorts</button>
          </div>
        </div>
        <div class="fg-row" style="margin-bottom:0">
          <div class="fg-lbl">📺 Canal</div>
          <div class="fg-ctrl ch-chips">{''.join(geral_chart_chips)}</div>
        </div>
      </div>

      <div class="kpi-grid">
        <div class="kpi"><div class="kpi-val" id="geral-kpi-views">—</div><div class="kpi-lbl">Visualizações</div></div>
        <div class="kpi"><div class="kpi-val" id="geral-kpi-subs" style="color:var(--green)">—</div><div class="kpi-lbl">Saldo de Inscritos</div></div>
        <div class="kpi"><div class="kpi-val" id="geral-kpi-hours" style="color:var(--amber)">—</div><div class="kpi-lbl">Tempo de Exibição</div></div>
        <div class="kpi"><div class="kpi-val" id="geral-kpi-avg" style="color:var(--purple)">—</div><div class="kpi-lbl">Média Diária</div></div>
      </div>

      <div class="chart-card">
        <div class="chart-head"><h3 id="geral-chart-title">📈 Curva de Visualizações Diárias</h3></div>
        <div class="chart-box"><canvas id="geralChartViews"></canvas></div>
      </div>

      <div class="charts-split">
        <div class="chart-card">
          <div class="chart-head"><h3>👥 Saldo Diário de Inscritos (+ / -)</h3></div>
          <div class="chart-box"><canvas id="geralChartSubs"></canvas></div>
        </div>
        <div class="chart-card">
          <div class="chart-head">
            <h3 id="geral-chart-traffic-title">🚦 Origem do Tráfego</h3>
            <span class="sub" id="geral-traffic-top-source">Principal: <b>—</b></span>
          </div>
          <div class="chart-box"><canvas id="geralChartTraffic"></canvas></div>
        </div>
      </div>
    </div>

    <!-- GERAL TAB 3: 1 DE 10 -->
    <div class="sub-content" id="geral-tab-rank10">
      <div class="sec-top" style="margin-bottom:12px">
        <div>
          <div class="sec-title">🎯 Desempenho do Vídeo Mais Recente (1 de 10)</div>
          <div class="sec-hint">Compara as views do último vídeo postado com a média dos 10 vídeos anteriores do canal</div>
        </div>
      </div>
      <div class="rank10-grid">{''.join(rank10_cards_geral)}</div>
    </div>

    <!-- GERAL TAB 4: CALENDÁRIO DE ESTREIAS -->
    <div class="sub-content" id="geral-tab-calendar">
      <div class="sec-top" style="margin-bottom:12px">
        <div>
          <div class="sec-title">📅 Linha do Tempo de Vídeos Agendados ({total_sched_count} Estreias)</div>
          <div class="sec-hint">Fila organizada cronologicamente com as próximas estreias em todos os canais</div>
        </div>
      </div>
      {''.join(cal_html)}
    </div>
  </div>

</div>
<script>
window.CHANNELS_TIMESERIES = {timeseries_json};
{JS}
</script>
</body>
</html>"""
