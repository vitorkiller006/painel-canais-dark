# -*- coding: utf-8 -*-
"""
Template HTML do Painel (mobile-first).
- Radar ao vivo com ordenação: Mais vistos 60 min / 48h / Total
- Filtro por grupo (Todos / Pessoais / Startup GVG) combinável com a ordenação
- Tabela comparativa vira cards no celular
- Cards de Top 3 recolhíveis
"""

import html as htmllib
from datetime import timezone, timedelta

MIN_VIEWS_FOR_RETENTION_RANK = 10


def _e(s):
    return htmllib.escape(str(s if s is not None else ""), quote=True)


CSS = """
:root{--bg:#090D16;--surface:#111827;--surface-2:#1E293B;--border:rgba(255,255,255,.09);--text:#F8FAFC;--muted:#94A3B8;--cyan:#38BDF8;--green:#10B981;--amber:#F59E0B;--red:#F43F5E;--purple:#C084FC}
*{box-sizing:border-box;margin:0;padding:0}
html{-webkit-text-size-adjust:100%}
body{background:var(--bg);color:var(--text);font-family:'Inter',system-ui,sans-serif;line-height:1.4;padding:16px}
.wrap{max-width:1400px;margin:0 auto}
a{color:inherit}
.num,.mono{font-family:'JetBrains Mono',monospace}

/* Topbar */
.topbar{background:var(--surface);border:1px solid var(--border);border-radius:14px;padding:14px 16px;margin-bottom:14px}
.topbar h1{font-size:18px;font-weight:800}
.topbar .meta{font-size:12px;color:var(--muted);margin-top:4px}
.topbar .meta b{color:var(--text)}
.chips{display:flex;gap:8px;margin-top:12px;overflow-x:auto;-webkit-overflow-scrolling:touch;scrollbar-width:none;padding-bottom:2px}
.chips::-webkit-scrollbar{display:none}
.chip{flex:0 0 auto;background:var(--surface-2);color:var(--text);border:1px solid var(--border);padding:9px 14px;border-radius:999px;font-size:13px;font-weight:600;cursor:pointer;min-height:40px;white-space:nowrap}
.chip.active{background:var(--cyan);color:#090D16;border-color:var(--cyan)}

/* Sections */
.sec{background:var(--surface);border:1px solid var(--border);border-radius:14px;padding:14px 16px;margin-bottom:14px}
.sec-title{font-size:16px;font-weight:700}
.sec-hint{font-size:12px;color:var(--muted);margin-top:3px}
.sec-top{display:flex;justify-content:space-between;align-items:flex-end;gap:10px;flex-wrap:wrap;margin-bottom:12px}

/* Segmented sort */
.seg{display:flex;background:var(--surface-2);border:1px solid var(--border);border-radius:12px;padding:3px;gap:3px;width:100%;max-width:460px}
.seg button{flex:1;background:transparent;color:var(--muted);border:0;border-radius:9px;padding:10px 6px;font-size:13px;font-weight:700;cursor:pointer;min-height:42px}
.seg button.active{background:var(--cyan);color:#090D16}
.lv-count{font-size:12px;color:var(--muted);margin:10px 2px 6px}

/* Live list */
.lv-row{display:grid;grid-template-columns:28px 96px 1fr auto;gap:12px;align-items:center;padding:10px 4px;border-top:1px solid rgba(255,255,255,.05)}
.lv-rank{font-family:'JetBrains Mono',monospace;font-weight:700;color:var(--muted);text-align:center;font-size:14px}
.lv-thumb{width:96px;height:54px;object-fit:cover;border-radius:8px;border:1px solid var(--border);background:#000}
.lv-info{min-width:0}
.lv-title{display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;font-size:14px;font-weight:600;text-decoration:none}
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

/* Channel cards */
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
.rk a{display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;font-size:12px;font-weight:500;text-decoration:none}
.rk a:hover{color:var(--cyan)}
.rk .rm{font-size:11px;color:var(--muted);margin-top:2px}
.hi{color:var(--cyan);font-weight:700;font-family:'JetBrains Mono',monospace}
.warn{color:var(--amber);font-size:10px;font-weight:600}
.empty-mini{font-size:11px;color:var(--muted);font-style:italic;padding:6px 0}
.off-msg{padding:0 16px 16px;font-size:13px;color:#FDA4AF}

/* Tablet */
@media (max-width:1100px){.top3{grid-template-columns:repeat(2,1fr)}}

/* Mobile */
@media (max-width:720px){
  body{padding:10px}
  .topbar,.sec{padding:12px;border-radius:12px}
  .topbar h1{font-size:16px}
  .sec-title{font-size:15px}
  .seg{max-width:none}
  .lv-row{grid-template-columns:22px 84px 1fr;grid-template-areas:"rank thumb info" "metrics metrics metrics";gap:8px 10px;padding:12px 0}
  .lv-rank{grid-area:rank;font-size:13px}
  .lv-thumb{grid-area:thumb;width:84px;height:47px}
  .lv-info{grid-area:info}
  .lv-title{font-size:13px}
  .lv-metrics{grid-area:metrics;display:grid;grid-template-columns:repeat(3,1fr);gap:6px}
  .mt{min-width:0;text-align:center;padding:7px 4px}
  .mt-val{font-size:15px}

  /* Comparativo vira cards */
  table.cmp thead{display:none}
  table.cmp,table.cmp tbody,table.cmp tr,table.cmp td{display:block;width:100%}
  table.cmp tr{background:var(--surface-2);border:1px solid var(--border);border-radius:12px;padding:10px 12px;margin-bottom:10px}
  table.cmp td{border:0;padding:5px 0;display:flex;justify-content:space-between;align-items:center;gap:10px;text-align:right}
  table.cmp td.num{text-align:right}
  table.cmp td::before{content:attr(data-label);font-size:11px;color:var(--muted);text-transform:uppercase;font-weight:600;text-align:left;font-family:'Inter',sans-serif}
  table.cmp td.cell-ch{display:block;text-align:left;border-bottom:1px solid var(--border);padding-bottom:8px;margin-bottom:4px}
  table.cmp td.cell-ch::before{display:none}

  .top3{grid-template-columns:1fr;padding:0 12px 12px}
  details.ch>summary{padding:12px}
  .ch-stats{gap:10px;width:100%}
}
"""

JS = """
let curSort='d60', curGroup='all';
const EMPTY_MSG={
  d60:'Nenhum vídeo ganhou views na última medição (~60 min). O robô mede a cada 30 min.',
  d48:'Nenhum vídeo ganhou views na janela de 48h medida até agora.',
  total:'Nenhum vídeo público com movimentação recente.'
};
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
  document.getElementById('lv-count').textContent='Exibindo '+n+(n===1?' vídeo ordenado por ':' vídeos ordenados por ')+(curSort==='d60'?'mais vistos nos últimos 60 min':curSort==='d48'?'mais vistos nas últimas 48h':'total de views');
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
  const g=new URLSearchParams(location.search).get('grupo');
  if(g==='gvg'||g==='pessoal')filterGroup(g,document.getElementById('chip-'+g));
  else applyLive();
});
"""


def _metric(label, key, value_txt, positive):
    cls = "pos" if positive else "zero"
    return f'<div class="mt {cls}" data-k="{key}"><span class="mt-lbl">{label}</span><span class="mt-val">{value_txt}</span></div>'


def render_html(channels_data, generated_at):
    now_brt = generated_at.astimezone(timezone(timedelta(hours=-3)))
    now_str = now_brt.strftime("%d/%m/%Y %H:%M")
    online = sum(1 for c in channels_data if c["status_conexao"] == "ONLINE")
    total_ch = len(channels_data)
    n_pessoal = sum(1 for c in channels_data if c["grupo_slug"] == "pessoal")
    n_gvg = sum(1 for c in channels_data if c["grupo_slug"] == "gvg")
    win = max((c["snapshot_window_hours"] for c in channels_data), default=0.0)
    win_48_txt = f"{min(win, 48.0):.1f}h de 48h medidas" if win < 48 else "48h completas"

    # ---------- 1. Radar ao vivo ----------
    live = [v for c in channels_data for v in c["videos_ao_vivo_movimento"]]
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

    # ---------- 2. Comparativo ----------
    cmp_rows = []
    for c in channels_data:
        on = c["status_conexao"] == "ONLINE"
        st = '<span class="pill pill-green">online</span>' if on else f'<span class="pill pill-red">{_e(c["status_conexao"])}</span>'
        impr = f"{c['impressions_7d_canal']:,}" if c.get("impressions_7d_canal") is not None else '<span class="pending">⏳ aguardando Google</span>'
        ctr = f"<b>{c['ctr_7d_canal']:.2f}%</b>" if c.get("ctr_7d_canal") is not None else '<span class="pending">⏳ aguardando Google</span>'
        ret = (f"<b>{c['retention_pct_7d_canal']:.1f}%</b> <span class='sub'>({c['retention_dur_7d_canal']})</span>"
               if c["views_7d_canal"] > 0 else '<span class="sub">—</span>')
        cmp_rows.append(f"""
<tr data-grupo="{c['grupo_slug']}">
  <td class="cell-ch"><div class="ch-name">{_e(c['canal_titulo'])} {st}</div><div class="sub">{_e(c['handle'])} · <span class="pill pill-{c['grupo_slug']}">{_e(c['grupo'])}</span></div></td>
  <td class="num" data-label="Views 60 min">+{c['views_60m_canal']:,}</td>
  <td class="num" data-label="Views 48h">+{c['views_48h_canal']:,}</td>
  <td class="num" data-label="Views 7d"><b>{c['views_7d_canal']:,}</b></td>
  <td class="num" data-label="Impressões 7d">{impr}</td>
  <td class="num" data-label="CTR 7d">{ctr}</td>
  <td class="num" data-label="Retenção 7d">{ret}</td>
  <td class="num" data-label="Inscritos">{c['inscritos']:,}</td>
  <td class="num" data-label="Vídeos">{c['total_videos_publicos']} públ. · {c['total_videos_agendados']} agend.</td>
</tr>""")

    # ---------- 3. Top 3 por canal ----------
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
        if c["status_conexao"] != "ONLINE":
            cards.append(f"""
<details class="ch off" data-grupo="{c['grupo_slug']}" open>
  <summary><div class="ch-head"><span class="pill pill-{c['grupo_slug']}">{_e(c['grupo'])}</span><h3>{_e(c['canal_titulo'])}<small>{_e(c['nome_projeto'])}</small></h3></div><span class="pill pill-red">desconectado</span></summary>
  <div class="off-msg"><b>Motivo:</b> {_e(c.get('erro'))}<br>Rode no PC: <code>{_e(c.get('auth_bat'))}</code></div>
</details>""")
            continue
        pend = _e(c.get("reach_message") or "Aguardando 1º relatório do Google (24–48h)")
        cards.append(f"""
<details class="ch" data-grupo="{c['grupo_slug']}" open>
  <summary>
    <div class="ch-head"><span class="pill pill-{c['grupo_slug']}">{_e(c['grupo'])}</span><h3>{_e(c['canal_titulo'])}<small>{_e(c['handle'])} · {_e(c['nome_projeto'])}</small></h3></div>
    <div class="ch-stats"><span>👁️ <b>{c['views_7d_canal']:,}</b> 7d</span><span>⚡ <b>+{c['views_48h_canal']:,}</b> 48h</span><span>👥 <b>{c['inscritos']:,}</b></span></div>
  </summary>
  <div class="top3">
    <div class="box"><h4>🎯 Maior retenção (7d)</h4>{rank_list(c['top3_retencao_7d'], fmt_ret, 'Sem views nos últimos 7 dias.')}</div>
    <div class="box"><h4>👁️ Mais views (7d)</h4>{rank_list(c['top3_views_7d'], lambda it: f'<span class="hi">{it["views_7d"]:,} views</span> · ret. {it["retention_pct"]:.1f}%', 'Sem views nos últimos 7 dias.')}</div>
    <div class="box"><h4>🖱️ Maior CTR (7d)</h4>{rank_list(c['top3_ctr_7d'], lambda it: f'<span class="hi">{it["ctr_7d"]:.2f}%</span> · {it["impressions_7d"]:,} impr.', '⏳ ' + pend)}</div>
    <div class="box"><h4>📢 Mais impressões (7d)</h4>{rank_list(c['top3_impressoes_7d'], lambda it: f'<span class="hi">{it["impressions_7d"]:,}</span> impr. · CTR {it["ctr_7d"]:.2f}%', '⏳ ' + pend)}</div>
  </div>
</details>""")

    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
<meta http-equiv="refresh" content="600">
<meta name="theme-color" content="#090D16">
<meta name="apple-mobile-web-app-capable" content="yes">
<title>Painel Canais Dark</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;700&display=swap" rel="stylesheet">
<style>{CSS}</style>
</head>
<body>
<div class="wrap">

  <div class="topbar">
    <h1>📊 Painel Canais Dark</h1>
    <div class="meta">Atualizado <b>{now_str}</b> (BRT) · <b>{online}/{total_ch}</b> online · robô na nuvem a cada 30 min</div>
    <div class="chips">
      <button class="chip active" id="chip-all" onclick="filterGroup('all',this)">Todos ({total_ch})</button>
      <button class="chip" id="chip-pessoal" onclick="filterGroup('pessoal',this)">Pessoais ({n_pessoal})</button>
      <button class="chip" id="chip-gvg" onclick="filterGroup('gvg',this)">Startup GVG ({n_gvg})</button>
    </div>
  </div>

  <div class="sec">
    <div class="sec-top">
      <div>
        <div class="sec-title">🔥 Mais vistos agora — todos os canais</div>
        <div class="sec-hint">Views ganhas por vídeo público · janela 48h: {win_48_txt}</div>
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
      <div class="sec-hint">Views 60 min/48h (medição própria) · 7d via YouTube Analytics · Impressões/CTR via Reporting API</div>
    </div></div>
    <div class="tbl-wrap">
      <table class="cmp">
        <thead><tr><th>Canal</th><th class="num">60 min</th><th class="num">48h</th><th class="num">Views 7d</th><th class="num">Impressões 7d</th><th class="num">CTR 7d</th><th class="num">Retenção 7d</th><th class="num">Inscritos</th><th class="num">Vídeos</th></tr></thead>
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
<script>{JS}</script>
</body>
</html>"""
