# -*- coding: utf-8 -*-
"""
===============================================================================
DARK FACTORY CLOUD ENGINE — PAINEL MASTER ANALYTICS (MULTI-CANAL YOUTUBE STUDIO)
ARQUIVO: painel_template.py
===============================================================================
Design System:
- Zinc / Deep Slate Pro (Linear / Vercel / YouTube Studio Dark Mode)
- ApexCharts Modern SVG Area Splines, Donut & Bar Charts (v4.0.0 fixada)
- Lucide Vector Icons (v0.460.0 fixada)
- Audiência Dinâmica Consolidada e por Canal
- 100% Responsivo (Desktop, Tablet, Mobile)
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

def _metric(lbl, key, val, is_pos):
    cls = "val hi" if is_pos else "val"
    return f'<div class="m"><span class="lbl">{_e(lbl)}</span><span class="{cls}">{_e(val)}</span></div>'

CSS = """
:root {
  --bg: #090D14;
  --surface: #111726;
  --surface-2: #162032;
  --surface-3: #1E2B40;
  --border: rgba(255, 255, 255, 0.08);
  --border-hover: rgba(255, 255, 255, 0.16);
  --border-hi: rgba(56, 189, 248, 0.35);
  --text: #F8FAFC;
  --text-muted: #94A3B8;
  --text-dim: #64748B;
  --cyan: #38BDF8;
  --cyan-dim: rgba(56, 189, 248, 0.12);
  --green: #10B981;
  --green-dim: rgba(16, 185, 129, 0.12);
  --amber: #F59E0B;
  --amber-dim: rgba(245, 158, 11, 0.12);
  --red: #F43F5E;
  --red-dim: rgba(244, 63, 94, 0.12);
  --purple: #C084FC;
  --purple-dim: rgba(192, 132, 252, 0.12);
}

* { box-sizing: border-box; margin: 0; padding: 0; }
html { -webkit-text-size-adjust: 100%; scroll-behavior: smooth; }
body {
  background: var(--bg);
  color: var(--text);
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  line-height: 1.45;
  padding: 16px;
  -webkit-font-smoothing: antialiased;
}
.wrap { max-width: 1440px; margin: 0 auto; }
a { color: inherit; text-decoration: none; }
.num, .mono { font-family: 'JetBrains Mono', monospace; }

/* Lucide Icons Custom */
.lucide, i[data-lucide] {
  width: 15px;
  height: 15px;
  stroke-width: 2px;
  display: inline-block;
  vertical-align: middle;
  flex-shrink: 0;
}
.lucide-lg, i[data-lucide].lucide-lg { width: 20px; height: 20px; }

/* View Sections */
.view-section { display: none; }
.view-section.active { display: block; animation: fadeIn .2s cubic-bezier(0.16, 1, 0.3, 1); }
@keyframes fadeIn { from { opacity: 0; transform: translateY(4px); } to { opacity: 1; transform: translateY(0); } }

/* Topbar Global */
.topbar {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 14px;
  padding: 14px 18px;
  margin-bottom: 14px;
  box-shadow: 0 4px 20px -2px rgba(0,0,0,.3);
}
.topbar-main { display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px; }
.topbar h1 { font-size: 18px; font-weight: 700; display: flex; align-items: center; gap: 8px; letter-spacing: -0.02em; }
.topbar .meta { font-size: 12px; color: var(--text-muted); margin-top: 4px; }
.topbar .meta b { color: var(--text); }
.vph-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: var(--cyan-dim);
  border: 1px solid var(--border-hi);
  color: var(--cyan);
  padding: 5px 12px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 600;
}

/* Quick Switcher Navbar */
.channel-nav-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 14px;
  padding: 8px 12px;
  margin-bottom: 14px;
  flex-wrap: wrap;
  gap: 10px;
}
.btn-back-hub {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: var(--surface-2);
  color: var(--text);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 7px 12px;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all .15s ease;
}
.btn-back-hub:hover {
  background: var(--surface-3);
  border-color: var(--cyan);
  color: var(--cyan);
}
.ch-quick-switcher {
  display: flex;
  gap: 6px;
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
  scrollbar-width: none;
}
.ch-quick-switcher::-webkit-scrollbar { display: none; }
.ch-switch-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: var(--surface-2);
  color: var(--text-muted);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 6px 10px;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  white-space: nowrap;
  transition: all .15s ease;
}
.ch-switch-btn:hover { color: var(--text); background: var(--surface-3); }
.ch-switch-btn.active {
  background: var(--cyan);
  color: #090D14;
  border-color: var(--cyan);
  font-weight: 700;
}
.ch-switch-btn img { width: 18px; height: 18px; border-radius: 50%; object-fit: cover; }

/* 1. HUB / TELA INICIAL */
.hub-hero {
  background: linear-gradient(135deg, rgba(22, 32, 50, 0.9) 0%, rgba(17, 23, 38, 0.95) 100%);
  border: 1px solid var(--border);
  border-radius: 16px;
  padding: 22px;
  margin-bottom: 18px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 14px;
}
.hub-hero h1 { font-size: 21px; font-weight: 700; letter-spacing: -0.02em; display: flex; align-items: center; gap: 8px; }
.hub-hero .meta { font-size: 13px; color: var(--text-muted); margin-top: 4px; }
.hub-chips {
  display: flex;
  gap: 8px;
  margin-top: 14px;
  overflow-x: auto;
  scrollbar-width: none;
}
.hub-chips::-webkit-scrollbar { display: none; }

.hub-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}
@media (max-width: 1200px) { .hub-grid { grid-template-columns: repeat(2, 1fr); } }
@media (max-width: 640px) { .hub-grid { grid-template-columns: 1fr; } }

.hub-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 14px;
  padding: 16px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  cursor: pointer;
  transition: all .2s cubic-bezier(0.16, 1, 0.3, 1);
  position: relative;
  overflow: hidden;
}
.hub-card:hover {
  transform: translateY(-3px);
  border-color: var(--border-hover);
  box-shadow: 0 10px 24px -4px rgba(0,0,0,.5);
}
.hub-card.card-geral {
  background: linear-gradient(135deg, rgba(24, 34, 53, 0.95) 0%, rgba(15, 22, 36, 0.98) 100%);
  border: 1px solid rgba(56, 189, 248, 0.3);
}
.hub-card.card-geral:hover {
  border-color: var(--cyan);
  box-shadow: 0 10px 24px -4px rgba(56, 189, 248, 0.15);
}

.card-top { display: flex; align-items: center; gap: 12px; margin-bottom: 14px; }
.card-avatar-wrap { position: relative; width: 52px; height: 52px; flex-shrink: 0; }
.card-avatar {
  width: 52px;
  height: 52px;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid var(--border);
  background: #0f172a;
}
.card-avatar.geral-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--cyan-dim);
  border-color: var(--border-hi);
  color: var(--cyan);
}
.card-status-dot {
  position: absolute;
  bottom: 0;
  right: 0;
  width: 13px;
  height: 13px;
  border-radius: 50%;
  border: 2px solid var(--surface);
}
.card-status-dot.online { background: var(--green); box-shadow: 0 0 8px rgba(16,185,129,.4); }
.card-status-dot.offline { background: var(--red); }

.card-meta { flex: 1; min-width: 0; }
.card-name { font-size: 15px; font-weight: 700; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; letter-spacing: -0.01em; }
.card-subtext { font-size: 11px; color: var(--text-muted); margin-top: 2px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }

.card-metrics {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
  background: var(--surface-2);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 10px 8px;
  margin-bottom: 12px;
  text-align: center;
}
.cm-item { display: flex; flex-direction: column; gap: 2px; }
.cm-lbl { font-size: 10px; font-weight: 600; text-transform: uppercase; color: var(--text-dim); letter-spacing: 0.04em; }
.cm-val { font-size: 12px; font-weight: 700; font-family: 'JetBrains Mono', monospace; }
.cm-val.cyan { color: var(--cyan); }

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
  font-weight: 600;
  color: var(--cyan);
  padding-top: 4px;
}
.card-footer i { transition: transform .15s ease; }
.hub-card:hover .card-footer i { transform: translateX(3px); }

/* Banner do Canal */
.ch-banner {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 14px;
  padding: 16px 20px;
  margin-bottom: 12px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 14px;
}
.ch-banner-left { display: flex; align-items: center; gap: 14px; }
.ch-banner-avatar {
  width: 58px;
  height: 58px;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid var(--border);
  background: #0f172a;
}
.ch-banner-info h2 { font-size: 18px; font-weight: 700; letter-spacing: -0.01em; display: flex; align-items: center; gap: 8px; }
.ch-banner-info .meta-row { font-size: 12px; color: var(--text-muted); margin-top: 4px; display: flex; align-items: center; flex-wrap: wrap; gap: 6px; }

/* KPI Strip */
.ch-kpi-bar {
  display: grid;
  grid-template-columns: repeat(8, 1fr);
  gap: 10px;
  margin-bottom: 14px;
}
@media (max-width: 1200px) { .ch-kpi-bar { grid-template-columns: repeat(4, 1fr); } }
@media (max-width: 640px) { .ch-kpi-bar { grid-template-columns: repeat(2, 1fr); } }

.ch-kpi-box {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 12px 14px;
  text-align: left;
}
.ch-kpi-lbl { font-size: 11px; font-weight: 600; text-transform: uppercase; color: var(--text-dim); letter-spacing: 0.04em; margin-bottom: 4px; }
.ch-kpi-val { font-size: 15px; font-weight: 700; font-family: 'JetBrains Mono', monospace; }

/* Sub-Navegação em Abas */
.sub-nav {
  display: flex;
  gap: 6px;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 6px;
  margin-bottom: 14px;
  overflow-x: auto;
  scrollbar-width: none;
}
.sub-nav::-webkit-scrollbar { display: none; }
.sub-tab-btn {
  flex: 1;
  min-width: 140px;
  background: transparent;
  color: var(--text-muted);
  border: 0;
  border-radius: 8px;
  padding: 9px 14px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  white-space: nowrap;
  transition: all .15s ease;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 7px;
}
.sub-tab-btn:hover { color: var(--text); background: var(--surface-2); }
.sub-tab-btn.active {
  background: var(--cyan);
  color: #090D14;
  font-weight: 700;
}

.sub-content { display: none; }
.sub-content.active { display: block; animation: fadeIn .2s cubic-bezier(0.16, 1, 0.3, 1); }

/* Panels and Filter Bars */
.filters-panel {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 14px 16px;
  margin-bottom: 14px;
}
.fg-row { display: flex; align-items: center; gap: 12px; margin-bottom: 10px; flex-wrap: wrap; }
.fg-lbl { font-size: 12px; font-weight: 600; color: var(--text-muted); min-width: 80px; display: flex; align-items: center; gap: 6px; }
.fg-ctrl { display: flex; gap: 6px; flex-wrap: wrap; }

.seg {
  display: inline-flex;
  background: var(--surface-2);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 3px;
  gap: 2px;
}
.seg button {
  background: transparent;
  border: 0;
  color: var(--text-muted);
  font-size: 12px;
  font-weight: 600;
  padding: 6px 12px;
  border-radius: 6px;
  cursor: pointer;
  transition: all .15s ease;
  white-space: nowrap;
  display: inline-flex;
  align-items: center;
  gap: 5px;
}
.seg button:hover { color: var(--text); }
.seg button.active { background: var(--cyan); color: #090D14; font-weight: 700; }

.chip {
  background: var(--surface-2);
  color: var(--text-muted);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 6px 12px;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all .15s ease;
  white-space: nowrap;
}
.chip:hover { color: var(--text); background: var(--surface-3); }
.chip.active { background: var(--cyan); color: #090D14; border-color: var(--cyan); font-weight: 700; }

/* KPI Grid */
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
  margin-bottom: 14px;
}
@media (max-width: 900px) { .kpi-grid { grid-template-columns: repeat(2, 1fr); } }
@media (max-width: 480px) { .kpi-grid { grid-template-columns: 1fr; } }

.kpi {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 14px 16px;
}
.kpi-lbl { font-size: 11px; font-weight: 600; text-transform: uppercase; color: var(--text-dim); letter-spacing: 0.04em; margin-top: 4px; display: flex; align-items: center; gap: 5px; }
.kpi-val { font-size: 20px; font-weight: 700; font-family: 'JetBrains Mono', monospace; }

/* Chart Cards */
.chart-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 14px;
}
.chart-head { display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px; }
.chart-head h3 { font-size: 14px; font-weight: 700; display: flex; align-items: center; gap: 6px; letter-spacing: -0.01em; }
.chart-box { min-height: 260px; position: relative; }
.charts-split { display: grid; grid-template-columns: repeat(2, 1fr); gap: 14px; }
@media (max-width: 900px) { .charts-split { grid-template-columns: 1fr; } }

/* AUDIENCE & DEMOGRAPHY SECTION */
.audience-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 14px;
  margin-bottom: 14px;
}
@media (max-width: 900px) { .audience-grid { grid-template-columns: 1fr; } }

.aud-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 18px;
}
.aud-card-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 14px;
  padding-bottom: 10px;
  border-bottom: 1px solid var(--border);
}
.aud-card-head h3 { font-size: 14px; font-weight: 700; display: flex; align-items: center; gap: 7px; }

/* Discovery Split Bar */
.discovery-box {
  background: var(--surface-2);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 14px;
  margin-bottom: 14px;
}
.discovery-bar {
  height: 12px;
  background: rgba(255,255,255,0.06);
  border-radius: 6px;
  overflow: hidden;
  display: flex;
  margin: 10px 0;
}
.discovery-seg-unsub { background: var(--cyan); height: 100%; transition: width .4s ease; }
.discovery-seg-sub { background: var(--purple); height: 100%; transition: width .4s ease; }
.discovery-legend { display: flex; justify-content: space-between; font-size: 12px; color: var(--text-muted); flex-wrap: wrap; gap: 6px; }

/* Country & Device Tables */
.aud-list-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 0;
  border-bottom: 1px solid rgba(255,255,255,0.04);
}
.aud-list-row:last-child { border-bottom: none; }
.aud-col-main { display: flex; align-items: center; gap: 10px; flex: 1; min-width: 0; }
.aud-flag { font-size: 18px; line-height: 1; flex-shrink: 0; }
.aud-name { font-size: 13px; font-weight: 600; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.aud-bar-wrap { width: 100px; height: 6px; background: rgba(255,255,255,0.06); border-radius: 3px; overflow: hidden; margin: 0 12px; flex-shrink: 0; }
.aud-bar-fill { height: 100%; background: var(--cyan); border-radius: 3px; }
.aud-val-group { text-align: right; flex-shrink: 0; }
.aud-val { font-size: 13px; font-weight: 700; font-family: 'JetBrains Mono', monospace; }
.aud-sub { font-size: 11px; color: var(--text-dim); }

/* Device Item Box */
.device-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; }
@media (max-width: 480px) { .device-grid { grid-template-columns: 1fr; } }
.device-box {
  background: var(--surface-2);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 12px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}
.dev-top { display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px; }
.dev-label { font-size: 12px; font-weight: 600; color: var(--text-muted); display: flex; align-items: center; gap: 6px; }
.dev-pct { font-size: 16px; font-weight: 700; font-family: 'JetBrains Mono', monospace; color: var(--text); }

/* Live Video List */
.sec {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 14px;
}
.sec-top { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; flex-wrap: wrap; gap: 10px; }
.sec-title { font-size: 15px; font-weight: 700; display: flex; align-items: center; gap: 7px; letter-spacing: -0.01em; }
.sec-hint { font-size: 12px; color: var(--text-muted); margin-top: 2px; }

.lv-row {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px;
  background: var(--surface-2);
  border: 1px solid var(--border);
  border-radius: 10px;
  margin-bottom: 8px;
  transition: all .15s ease;
}
.lv-row:hover { border-color: var(--border-hover); background: var(--surface-3); }
.lv-rank { font-size: 12px; font-weight: 700; color: var(--text-dim); width: 20px; text-align: center; }
.lv-thumb { width: 72px; height: 42px; border-radius: 6px; object-fit: cover; background: #000; flex-shrink: 0; }
.lv-info { flex: 1; min-width: 0; }
.lv-title { font-size: 13px; font-weight: 600; color: var(--text); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; display: block; }
.lv-title:hover { color: var(--cyan); }
.lv-meta { font-size: 11px; color: var(--text-muted); margin-top: 2px; display: flex; align-items: center; gap: 6px; flex-wrap: wrap; }
.lv-metrics { display: flex; gap: 12px; flex-shrink: 0; }
.m { text-align: right; }
.m .lbl { font-size: 10px; font-weight: 600; text-transform: uppercase; color: var(--text-dim); display: block; }
.m .val { font-size: 13px; font-weight: 700; font-family: 'JetBrains Mono', monospace; }
.m .val.hi { color: var(--cyan); }

/* Pills & Badges */
.pill {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 2px 7px;
  border-radius: 6px;
  font-size: 11px;
  font-weight: 600;
  line-height: 1.2;
}
.pill-green { background: var(--green-dim); color: var(--green); border: 1px solid rgba(16,185,129,.25); }
.pill-red { background: var(--red-dim); color: var(--red); border: 1px solid rgba(244,63,94,.25); }
.pill-amber { background: var(--amber-dim); color: var(--amber); border: 1px solid rgba(245,158,11,.25); }
.pill-cyan { background: var(--cyan-dim); color: var(--cyan); border: 1px solid var(--border-hi); }
.pill-pessoal { background: rgba(56, 189, 248, 0.1); color: #7DD3FC; border: 1px solid rgba(56, 189, 248, 0.2); }
.pill-gvg { background: rgba(168, 85, 247, 0.1); color: #D8B4FE; border: 1px solid rgba(168, 85, 247, 0.2); }

/* 1 de 10 Launch */
.r10-card {
  background: var(--surface-2);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 12px;
}
.r10-head { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
.r10-body { display: flex; gap: 14px; align-items: center; }
.r10-thumb { width: 120px; height: 68px; border-radius: 8px; object-fit: cover; flex-shrink: 0; }
.r10-vinfo { flex: 1; min-width: 0; }
.r10-vtitle { font-size: 14px; font-weight: 700; color: var(--text); display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
.r10-vtitle:hover { color: var(--cyan); }
.r10-metrics {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 10px 14px;
  margin-top: 14px;
  font-size: 12px;
}
.r10-badge { padding: 4px 10px; border-radius: 6px; font-size: 12px; font-weight: 700; }
.r10-b1 { background: var(--green-dim); color: var(--green); border: 1px solid rgba(16,185,129,.3); }
.r10-b2 { background: var(--cyan-dim); color: var(--cyan); border: 1px solid var(--border-hi); }
.r10-b3 { background: rgba(255,255,255,.06); color: var(--text-muted); border: 1px solid var(--border); }
.r10-b4 { background: var(--amber-dim); color: var(--amber); border: 1px solid rgba(245,158,11,.3); }

/* Top 3 Grids */
.top3 { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; }
@media (max-width: 1100px) { .top3 { grid-template-columns: repeat(2, 1fr); } }
@media (max-width: 600px) { .top3 { grid-template-columns: 1fr; } }
.top3 .box { background: var(--surface-2); border: 1px solid var(--border); border-radius: 10px; padding: 12px; }
.top3 h4 { font-size: 12px; font-weight: 700; color: var(--text-muted); margin-bottom: 10px; text-transform: uppercase; letter-spacing: 0.03em; display: flex; align-items: center; gap: 5px; }
.rk { display: flex; align-items: flex-start; gap: 8px; padding: 6px 0; border-bottom: 1px solid rgba(255,255,255,.04); }
.rk:last-child { border-bottom: none; }
.md { font-size: 13px; font-weight: 700; color: var(--text-dim); }
.ri { flex: 1; min-width: 0; font-size: 12px; }
.ri a { font-weight: 600; color: var(--text); display: block; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.ri a:hover { color: var(--cyan); }
.rm { font-size: 11px; color: var(--text-muted); margin-top: 2px; }
.rm .hi { color: var(--cyan); font-weight: 700; }

/* Calendar */
.cal-group { margin-bottom: 16px; }
.cal-date-title { font-size: 13px; font-weight: 700; color: var(--text-muted); margin-bottom: 8px; display: flex; align-items: center; gap: 6px; }
.cal-row {
  display: flex;
  align-items: center;
  gap: 12px;
  background: var(--surface-2);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 10px 14px;
  margin-bottom: 8px;
}
.cal-time { font-size: 12px; font-weight: 700; font-family: 'JetBrains Mono', monospace; color: var(--cyan); width: 85px; flex-shrink: 0; }
.cal-thumb { width: 68px; height: 38px; border-radius: 6px; object-fit: cover; flex-shrink: 0; }
.cal-info { flex: 1; min-width: 0; }
.cal-info h4 { font-size: 13px; font-weight: 600; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.cal-info .sub { font-size: 11px; color: var(--text-muted); margin-top: 2px; }

/* Table Comparativa */
.tbl-wrap { overflow-x: auto; -webkit-overflow-scrolling: touch; }
table.cmp { width: 100%; border-collapse: collapse; font-size: 12px; }
table.cmp th {
  background: var(--surface-2);
  padding: 10px 12px;
  text-align: left;
  font-weight: 600;
  color: var(--text-dim);
  text-transform: uppercase;
  letter-spacing: 0.04em;
  font-size: 11px;
  border-bottom: 1px solid var(--border);
}
table.cmp th.num, table.cmp td.num { text-align: right; }
table.cmp td { padding: 12px; border-bottom: 1px solid rgba(255,255,255,.04); }
table.cmp tr:hover td { background: var(--surface-2); }
table.cmp .cell-ch { min-width: 180px; }

.empty { text-align: center; padding: 32px 16px; color: var(--text-muted); font-size: 13px; }
.empty-mini { text-align: center; padding: 16px 8px; color: var(--text-dim); font-size: 12px; }
"""

JS = """
let activeView = 'hub';
let activeChannelId = null;
let activeChannelSubTab = 'live';
let activeGeralTab = 'live';

let curSinglePeriod = '30d';
let curSingleFormat = 'all';
let curSingleSort = 'd48';

let curGeralPeriod = '30d';
let curGeralFormat = 'all';
let curGeralChannel = 'all';
let curGeralSort = 'd60';
let curGeralGroup = 'all';

// ApexCharts Instances
let chViewsApex = null, chSubsApex = null, chTrafficApex = null;
let geralViewsApex = null, geralSubsApex = null, geralTrafficApex = null;

function refreshIcons() {
  if (window.lucide && typeof window.lucide.createIcons === 'function') {
    window.lucide.createIcons();
  }
}

function openChannel(chId, updateHash = true) {
  if (chId === 'home') {
    activeView = 'hub';
    activeChannelId = null;
    document.getElementById('view-hub').classList.add('active');
    document.getElementById('view-channel').classList.remove('active');
    document.getElementById('view-geral').classList.remove('active');
    if (updateHash) history.pushState(null, '', '#');
    window.scrollTo({ top: 0, behavior: 'smooth' });
    refreshIcons();
    return;
  }

  if (chId === 'geral') {
    activeView = 'geral';
    activeChannelId = null;
    document.getElementById('view-hub').classList.remove('active');
    document.getElementById('view-channel').classList.remove('active');
    document.getElementById('view-geral').classList.add('active');
    document.querySelectorAll('.ch-switch-btn').forEach(b => b.classList.toggle('active', b.dataset.ch === 'geral'));
    if (updateHash) history.pushState(null, '', '#view=geral');
    window.scrollTo({ top: 0, behavior: 'smooth' });
    if (activeGeralTab === 'charts') setTimeout(updateGeralCharts, 60);
    refreshIcons();
    return;
  }

  activeView = 'channel';
  activeChannelId = chId;
  document.getElementById('view-hub').classList.remove('active');
  document.getElementById('view-geral').classList.remove('active');
  document.getElementById('view-channel').classList.add('active');

  document.querySelectorAll('.ch-banner').forEach(el => el.style.display = (el.dataset.canal === chId) ? 'flex' : 'none');
  document.querySelectorAll('.ch-kpi-bar').forEach(el => el.style.display = (el.dataset.canal === chId) ? 'grid' : 'none');
  document.querySelectorAll('.ch-r10-card').forEach(el => el.style.display = (el.dataset.canal === chId) ? 'block' : 'none');
  document.querySelectorAll('.ch-top3-grid').forEach(el => el.style.display = (el.dataset.canal === chId) ? 'grid' : 'none');
  document.querySelectorAll('.ch-aud-panel').forEach(el => el.style.display = (el.dataset.canal === chId) ? 'block' : 'none');

  let schedFound = 0;
  document.querySelectorAll('.ch-sched-item').forEach(el => {
    const show = (el.dataset.canal === chId);
    el.style.display = show ? 'flex' : 'none';
    if (show) schedFound++;
  });
  const schedEmpty = document.getElementById('ch-sched-empty');
  if (schedEmpty) schedEmpty.style.display = (schedFound === 0) ? 'block' : 'none';

  document.querySelectorAll('.ch-switch-btn').forEach(b => b.classList.toggle('active', b.dataset.ch === chId));

  applySingleChannelLive();
  switchChannelSubTab(activeChannelSubTab, document.getElementById('btn-ch-tab-' + activeChannelSubTab));

  if (updateHash) history.pushState(null, '', '#ch=' + chId);
  window.scrollTo({ top: 0, behavior: 'smooth' });
  refreshIcons();
}

function switchChannelSubTab(tabId, btn) {
  activeChannelSubTab = tabId;
  document.querySelectorAll('#view-channel .sub-tab-btn').forEach(b => b.classList.remove('active'));
  document.querySelectorAll('#view-channel .sub-content').forEach(c => c.classList.remove('active'));
  if (btn) btn.classList.add('active');
  const target = document.getElementById('ch-tab-' + tabId);
  if (target) target.classList.add('active');

  if (tabId === 'charts') {
    setTimeout(updateSingleChannelCharts, 60);
  }
  refreshIcons();
}

function switchGeralMainTab(tabId, btn) {
  activeGeralTab = tabId;
  document.querySelectorAll('#view-geral .sub-tab-btn').forEach(b => b.classList.remove('active'));
  document.querySelectorAll('#view-geral .sub-content').forEach(c => c.classList.remove('active'));
  if (btn) btn.classList.add('active');
  const target = document.getElementById('geral-tab-' + tabId);
  if (target) target.classList.add('active');

  if (tabId === 'charts') {
    setTimeout(updateGeralCharts, 60);
  }
  refreshIcons();
}

function getCutoffDate(period) {
  const now = new Date();
  if (period === '7d') {
    const d = new Date(now.getTime() - 7 * 86400000);
    return d.toISOString().slice(0, 10);
  } else if (period === '30d') {
    const d = new Date(now.getTime() - 30 * 86400000);
    return d.toISOString().slice(0, 10);
  } else if (period === 'month') {
    return now.getFullYear() + '-' + String(now.getMonth() + 1).padStart(2, '0') + '-01';
  } else if (period === '180d') {
    const d = new Date(now.getTime() - 180 * 86400000);
    return d.toISOString().slice(0, 10);
  } else if (period === 'year') {
    return now.getFullYear() + '-01-01';
  }
  return '2020-01-01';
}

function filterHubGroup(g, btn) {
  document.querySelectorAll('.hub-chips .chip').forEach(b => b.classList.toggle('active', b === btn));
  document.querySelectorAll('.hub-card:not(.card-geral)').forEach(card => {
    card.style.display = (g === 'all' || card.dataset.grupo === g) ? 'flex' : 'none';
  });
}

function setSingleChannelSort(s, btn) {
  curSingleSort = s;
  document.querySelectorAll('#ch-tab-live .seg button').forEach(b => b.classList.toggle('active', b === btn));
  applySingleChannelLive();
}

function applySingleChannelLive() {
  if (!activeChannelId) return;
  const listEl = document.getElementById('ch-live-list');
  const countEl = document.getElementById('ch-live-count');
  const emptyEl = document.getElementById('ch-live-empty');
  if (!listEl) return;

  const rows = Array.from(listEl.querySelectorAll('.lv-row')).filter(r => r.dataset.canal === activeChannelId);
  const hiddenRows = Array.from(listEl.querySelectorAll('.lv-row')).filter(r => r.dataset.canal !== activeChannelId);
  hiddenRows.forEach(r => r.style.display = 'none');

  rows.sort((a, b) => {
    const va = parseInt(a.dataset[curSingleSort] || '0', 10);
    const vb = parseInt(b.dataset[curSingleSort] || '0', 10);
    return vb - va;
  });

  rows.forEach((r, idx) => {
    r.style.display = 'flex';
    const rk = r.querySelector('.lv-rank');
    if (rk) rk.textContent = String(idx + 1);
    listEl.appendChild(r);
  });

  if (countEl) countEl.textContent = `${rows.length} vídeo(s) com atividade recente no canal`;
  if (emptyEl) emptyEl.style.display = rows.length === 0 ? 'block' : 'none';
  if (rows.length === 0 && emptyEl) emptyEl.textContent = 'Nenhum vídeo com movimentação nas últimas horas neste canal.';
}

function setGeralSort(s, btn) {
  curGeralSort = s;
  document.querySelectorAll('#geral-tab-live .seg button').forEach(b => b.classList.toggle('active', b === btn));
  applyGeralLive();
}

function applyGeralLive() {
  const listEl = document.getElementById('geral-live-list');
  const countEl = document.getElementById('geral-live-count');
  const emptyEl = document.getElementById('geral-live-empty');
  if (!listEl) return;

  const rows = Array.from(listEl.querySelectorAll('.lv-row'));
  const visible = rows.filter(r => curGeralGroup === 'all' || r.dataset.grupo === curGeralGroup);
  const hidden = rows.filter(r => curGeralGroup !== 'all' && r.dataset.grupo !== curGeralGroup);
  hidden.forEach(r => r.style.display = 'none');

  visible.sort((a, b) => {
    const va = parseInt(a.dataset[curGeralSort] || '0', 10);
    const vb = parseInt(b.dataset[curGeralSort] || '0', 10);
    return vb - va;
  });

  visible.forEach((r, idx) => {
    r.style.display = 'flex';
    const rk = r.querySelector('.lv-rank');
    if (rk) rk.textContent = String(idx + 1);
    listEl.appendChild(r);
  });

  if (countEl) countEl.textContent = `${visible.length} vídeo(s) em movimento nos canais`;
  if (emptyEl) emptyEl.style.display = visible.length === 0 ? 'block' : 'none';
}

function filterGeralGroup(g, btn) {
  curGeralGroup = g;
  document.querySelectorAll('#geral-chips .chip').forEach(b => b.classList.toggle('active', b === btn));
  document.querySelectorAll('#view-geral [data-grupo]:not(.lv-row)').forEach(el => {
    el.style.display = (g === 'all' || el.dataset.grupo === g) ? '' : 'none';
  });
  applyGeralLive();
}

const pLabels = {
  '7d': 'Últimos 7 Dias',
  '30d': 'Últimos 30 Dias',
  'month': 'Este Mês',
  '180d': 'Últimos 180 Dias',
  'year': 'Este Ano',
  'all': 'Desde o Início'
};
const fLabels = {
  'all': 'Todos os Formatos',
  'video': '🎬 Só Vídeos Longos',
  'shorts': '⚡ Só Shorts'
};

function setSingleChannelPeriod(p, btn) {
  curSinglePeriod = p;
  document.querySelectorAll('#ch-tab-charts .period-btn').forEach(b => b.classList.toggle('active', b === btn));
  updateSingleChannelCharts();
}

function setSingleChannelFormat(f, btn) {
  curSingleFormat = f;
  document.querySelectorAll('#ch-tab-charts .format-btn').forEach(b => b.classList.toggle('active', b === btn));
  updateSingleChannelCharts();
}

function updateSingleChannelCharts() {
  if (!activeChannelId) return;
  const raw = window.CHANNELS_TIMESERIES || {};
  const chData = raw[activeChannelId];
  if (!chData) return;

  const cutoff = getCutoffDate(curSinglePeriod);
  const dayMap = {}, subMap = {}, minMap = {}, trafMap = {};

  (chData.history_lifetime || chData.history_30d || []).forEach(h => {
    if (h.day < cutoff) return;
    if (curSingleFormat !== 'all' && h.type && h.type !== curSingleFormat) return;
    dayMap[h.day] = (dayMap[h.day] || 0) + (h.views || 0);
    subMap[h.day] = (subMap[h.day] || 0) + (h.net_subs || 0);
    minMap[h.day] = (minMap[h.day] || 0) + (h.minutes || 0);
  });

  (chData.traffic_sources_lifetime || chData.traffic_sources_30d || []).forEach(t => {
    if (t.day && t.day < cutoff) return;
    if (curSingleFormat !== 'all' && t.type && t.type !== curSingleFormat) return;
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
  if (kv) kv.textContent = totV.toLocaleString('pt-BR');
  if (ks) {
    ks.textContent = (totS > 0 ? '+' : '') + totS.toLocaleString('pt-BR');
    ks.style.color = totS > 0 ? 'var(--green)' : (totS < 0 ? 'var(--red)' : 'var(--text-muted)');
  }
  if (km) km.textContent = (totM / 60).toFixed(1) + ' h';
  if (ka) ka.textContent = avgV.toLocaleString('pt-BR') + '/dia';

  const tTitle = document.getElementById('ch-chart-title');
  if (tTitle) tTitle.innerHTML = `<i data-lucide="line-chart"></i> ${chData.title} — ${pLabels[curSinglePeriod]} (${fLabels[curSingleFormat]})`;
  const trafTitle = document.getElementById('ch-chart-traffic-title');
  if (trafTitle) trafTitle.innerHTML = `<i data-lucide="pie-chart"></i> Origem do Tráfego (${fLabels[curSingleFormat]})`;
  const topSrcEl = document.getElementById('ch-traffic-top-source');
  if (topSrcEl) topSrcEl.innerHTML = topTr[1] > 0 ? `Principal: <b>${topTr[0]}</b> (${topTr[1].toLocaleString('pt-BR')} views)` : 'Principal: <b>—</b>';

  // Apex Area Chart (Views)
  const elV = document.querySelector("#chChartViews");
  if (elV && window.ApexCharts) {
    if (chViewsApex) chViewsApex.destroy();
    const optV = {
      series: [{ name: 'Visualizações', data: viewsData }],
      chart: { type: 'area', height: 260, background: 'transparent', toolbar: { show: false }, animations: { enabled: true, speed: 400 } },
      colors: ['#38BDF8'],
      fill: { type: 'gradient', gradient: { shadeIntensity: 1, opacityFrom: 0.35, opacityTo: 0.03, stops: [0, 95, 100] } },
      stroke: { curve: 'smooth', width: 2.5 },
      dataLabels: { enabled: false },
      grid: { borderColor: 'rgba(255,255,255,0.06)', strokeDashArray: 3 },
      xaxis: {
        categories: sortedDays.map(d => d.slice(5)),
        labels: { style: { colors: '#94A3B8', fontSize: '11px', fontFamily: 'Inter' } },
        axisBorder: { show: false },
        axisTicks: { show: false },
        tickAmount: Math.min(12, sortedDays.length)
      },
      yaxis: {
        labels: {
          style: { colors: '#94A3B8', fontSize: '11px', fontFamily: 'JetBrains Mono' },
          formatter: v => v >= 1000 ? (v / 1000).toFixed(1) + 'k' : v.toLocaleString('pt-BR')
        }
      },
      tooltip: { theme: 'dark', y: { formatter: v => v.toLocaleString('pt-BR') + ' views' } }
    };
    chViewsApex = new ApexCharts(elV, optV);
    chViewsApex.render();
  }

  // Apex Bar Chart (Subs)
  const elS = document.querySelector("#chChartSubs");
  if (elS && window.ApexCharts) {
    if (chSubsApex) chSubsApex.destroy();
    const optS = {
      series: [{ name: 'Saldo Inscritos', data: subsData }],
      chart: { type: 'bar', height: 240, background: 'transparent', toolbar: { show: false }, animations: { enabled: true, speed: 400 } },
      plotOptions: {
        bar: {
          colors: { ranges: [{ from: -9999999, to: -1, color: '#F43F5E' }, { from: 0, to: 9999999, color: '#10B981' }] },
          borderRadius: 3,
          columnWidth: '60%'
        }
      },
      dataLabels: { enabled: false },
      grid: { borderColor: 'rgba(255,255,255,0.06)', strokeDashArray: 3 },
      xaxis: {
        categories: sortedDays.map(d => d.slice(5)),
        labels: { style: { colors: '#94A3B8', fontSize: '10px' } },
        axisBorder: { show: false },
        axisTicks: { show: false },
        tickAmount: Math.min(10, sortedDays.length)
      },
      yaxis: {
        labels: {
          style: { colors: '#94A3B8', fontSize: '10px', fontFamily: 'JetBrains Mono' },
          formatter: v => (v > 0 ? '+' : '') + v.toLocaleString('pt-BR')
        }
      },
      tooltip: { theme: 'dark', y: { formatter: v => (v > 0 ? '+' : '') + v.toLocaleString('pt-BR') + ' inscritos' } }
    };
    chSubsApex = new ApexCharts(elS, optS);
    chSubsApex.render();
  }

  // Apex Donut Chart (Traffic)
  const elT = document.querySelector("#chChartTraffic");
  if (elT && window.ApexCharts) {
    if (chTrafficApex) chTrafficApex.destroy();
    let tLabels = Object.keys(trafMap);
    let tData = Object.values(trafMap);
    let tColors = ['#38BDF8','#10B981','#A855F7','#F59E0B','#F43F5E','#06B6D4','#E2E8F0','#64748B','#3B82F6','#F97316'];

    if (tData.length === 0 || tData.every(v => v === 0)) {
      tLabels = ['Nenhum tráfego'];
      tData = [1];
      tColors = ['#1E2B40'];
    }

    const optT = {
      series: tData,
      labels: tLabels,
      chart: { type: 'donut', height: 240, background: 'transparent' },
      colors: tColors,
      stroke: { show: false },
      dataLabels: { enabled: false },
      legend: { position: 'bottom', labels: { colors: '#94A3B8' }, fontSize: '11px', markers: { radius: 3 } },
      plotOptions: {
        pie: {
          donut: {
            size: '70%',
            labels: {
              show: true,
              total: {
                show: true,
                label: 'Total',
                color: '#94A3B8',
                fontSize: '11px',
                fontFamily: 'Inter',
                formatter: w => w.globals.seriesTotals.reduce((a, b) => a + b, 0).toLocaleString('pt-BR')
              },
              value: { color: '#F8FAFC', fontSize: '15px', fontFamily: 'JetBrains Mono', fontWeight: 700 }
            }
          }
        }
      },
      tooltip: {
        theme: 'dark',
        y: {
          formatter: (val, opts) => {
            const tot = opts.globals.seriesTotals.reduce((a, b) => a + b, 0);
            const pct = tot > 0 ? ((val / tot) * 100).toFixed(1) : '0';
            return `${val.toLocaleString('pt-BR')} views (${pct}%)`;
          }
        }
      }
    };
    chTrafficApex = new ApexCharts(elT, optT);
    chTrafficApex.render();
  }
  refreshIcons();
}

function setGeralChartPeriod(p, btn) {
  curGeralPeriod = p;
  document.querySelectorAll('#geral-tab-charts .period-btn').forEach(b => b.classList.toggle('active', b === btn));
  updateGeralCharts();
}

function setGeralChartFormat(f, btn) {
  curGeralFormat = f;
  document.querySelectorAll('#geral-tab-charts .format-btn').forEach(b => b.classList.toggle('active', b === btn));
  updateGeralCharts();
}

function setGeralChartChannel(ch, btn) {
  curGeralChannel = ch;
  document.querySelectorAll('#geral-tab-charts .ch-chip').forEach(b => b.classList.toggle('active', b.dataset.ch === ch));
  updateGeralCharts();
}

function updateGeralCharts() {
  const raw = window.CHANNELS_TIMESERIES || {};
  const cutoff = getCutoffDate(curGeralPeriod);

  const dayMap = {}, subMap = {}, minMap = {}, trafMap = {};
  const chList = (curGeralChannel === 'all') ? Object.values(raw) : [raw[curGeralChannel]].filter(Boolean);

  chList.forEach(ch => {
    (ch.history_lifetime || ch.history_30d || []).forEach(h => {
      if (h.day < cutoff) return;
      if (curGeralFormat !== 'all' && h.type && h.type !== curGeralFormat) return;
      dayMap[h.day] = (dayMap[h.day] || 0) + (h.views || 0);
      subMap[h.day] = (subMap[h.day] || 0) + (h.net_subs || 0);
      minMap[h.day] = (minMap[h.day] || 0) + (h.minutes || 0);
    });

    (ch.traffic_sources_lifetime || ch.traffic_sources_30d || []).forEach(t => {
      if (t.day && t.day < cutoff) return;
      if (curGeralFormat !== 'all' && t.type && t.type !== curGeralFormat) return;
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
  if (kv) kv.textContent = totV.toLocaleString('pt-BR');
  if (ks) {
    ks.textContent = (totS > 0 ? '+' : '') + totS.toLocaleString('pt-BR');
    ks.style.color = totS > 0 ? 'var(--green)' : (totS < 0 ? 'var(--red)' : 'var(--text-muted)');
  }
  if (km) km.textContent = (totM / 60).toFixed(1) + ' h';
  if (ka) ka.textContent = avgV.toLocaleString('pt-BR') + '/dia';

  const titleEl = document.getElementById('geral-chart-title');
  if (titleEl) {
    const chName = (curGeralChannel === 'all') ? 'Todos os Canais' : (raw[curGeralChannel]?.title || curGeralChannel);
    titleEl.innerHTML = `<i data-lucide="line-chart"></i> ${chName} — ${pLabels[curGeralPeriod]} (${fLabels[curGeralFormat]})`;
  }
  const trafTitleEl = document.getElementById('geral-chart-traffic-title');
  if (trafTitleEl) trafTitleEl.innerHTML = `<i data-lucide="pie-chart"></i> Origem do Tráfego (${fLabels[curGeralFormat]})`;
  const topSrcEl = document.getElementById('geral-traffic-top-source');
  if (topSrcEl) topSrcEl.innerHTML = topTr[1] > 0 ? `Principal: <b>${topTr[0]}</b> (${topTr[1].toLocaleString('pt-BR')} views)` : 'Principal: <b>—</b>';

  // Apex Area Chart (Geral Views)
  const elV = document.querySelector("#geralChartViews");
  if (elV && window.ApexCharts) {
    if (geralViewsApex) geralViewsApex.destroy();
    const optV = {
      series: [{ name: 'Visualizações', data: viewsData }],
      chart: { type: 'area', height: 260, background: 'transparent', toolbar: { show: false }, animations: { enabled: true, speed: 400 } },
      colors: ['#38BDF8'],
      fill: { type: 'gradient', gradient: { shadeIntensity: 1, opacityFrom: 0.35, opacityTo: 0.03, stops: [0, 95, 100] } },
      stroke: { curve: 'smooth', width: 2.5 },
      dataLabels: { enabled: false },
      grid: { borderColor: 'rgba(255,255,255,0.06)', strokeDashArray: 3 },
      xaxis: {
        categories: sortedDays.map(d => d.slice(5)),
        labels: { style: { colors: '#94A3B8', fontSize: '11px', fontFamily: 'Inter' } },
        axisBorder: { show: false },
        axisTicks: { show: false },
        tickAmount: Math.min(12, sortedDays.length)
      },
      yaxis: {
        labels: {
          style: { colors: '#94A3B8', fontSize: '11px', fontFamily: 'JetBrains Mono' },
          formatter: v => v >= 1000 ? (v / 1000).toFixed(1) + 'k' : v.toLocaleString('pt-BR')
        }
      },
      tooltip: { theme: 'dark', y: { formatter: v => v.toLocaleString('pt-BR') + ' views' } }
    };
    geralViewsApex = new ApexCharts(elV, optV);
    geralViewsApex.render();
  }

  // Apex Bar Chart (Geral Subs)
  const elS = document.querySelector("#geralChartSubs");
  if (elS && window.ApexCharts) {
    if (geralSubsApex) geralSubsApex.destroy();
    const optS = {
      series: [{ name: 'Saldo Inscritos', data: subsData }],
      chart: { type: 'bar', height: 240, background: 'transparent', toolbar: { show: false }, animations: { enabled: true, speed: 400 } },
      plotOptions: {
        bar: {
          colors: { ranges: [{ from: -9999999, to: -1, color: '#F43F5E' }, { from: 0, to: 9999999, color: '#10B981' }] },
          borderRadius: 3,
          columnWidth: '60%'
        }
      },
      dataLabels: { enabled: false },
      grid: { borderColor: 'rgba(255,255,255,0.06)', strokeDashArray: 3 },
      xaxis: {
        categories: sortedDays.map(d => d.slice(5)),
        labels: { style: { colors: '#94A3B8', fontSize: '10px' } },
        axisBorder: { show: false },
        axisTicks: { show: false },
        tickAmount: Math.min(10, sortedDays.length)
      },
      yaxis: {
        labels: {
          style: { colors: '#94A3B8', fontSize: '10px', fontFamily: 'JetBrains Mono' },
          formatter: v => (v > 0 ? '+' : '') + v.toLocaleString('pt-BR')
        }
      },
      tooltip: { theme: 'dark', y: { formatter: v => (v > 0 ? '+' : '') + v.toLocaleString('pt-BR') + ' inscritos' } }
    };
    geralSubsApex = new ApexCharts(elS, optS);
    geralSubsApex.render();
  }

  // Apex Donut Chart (Geral Traffic)
  const elT = document.querySelector("#geralChartTraffic");
  if (elT && window.ApexCharts) {
    if (geralTrafficApex) geralTrafficApex.destroy();
    let tLabels = Object.keys(trafMap);
    let tData = Object.values(trafMap);
    let tColors = ['#38BDF8','#10B981','#A855F7','#F59E0B','#F43F5E','#06B6D4','#E2E8F0','#64748B','#3B82F6','#F97316'];

    if (tData.length === 0 || tData.every(v => v === 0)) {
      tLabels = ['Nenhum tráfego'];
      tData = [1];
      tColors = ['#1E2B40'];
    }

    const optT = {
      series: tData,
      labels: tLabels,
      chart: { type: 'donut', height: 240, background: 'transparent' },
      colors: tColors,
      stroke: { show: false },
      dataLabels: { enabled: false },
      legend: { position: 'bottom', labels: { colors: '#94A3B8' }, fontSize: '11px', markers: { radius: 3 } },
      plotOptions: {
        pie: {
          donut: {
            size: '70%',
            labels: {
              show: true,
              total: {
                show: true,
                label: 'Total',
                color: '#94A3B8',
                fontSize: '11px',
                fontFamily: 'Inter',
                formatter: w => w.globals.seriesTotals.reduce((a, b) => a + b, 0).toLocaleString('pt-BR')
              },
              value: { color: '#F8FAFC', fontSize: '15px', fontFamily: 'JetBrains Mono', fontWeight: 700 }
            }
          }
        }
      },
      tooltip: {
        theme: 'dark',
        y: {
          formatter: (val, opts) => {
            const tot = opts.globals.seriesTotals.reduce((a, b) => a + b, 0);
            const pct = tot > 0 ? ((val / tot) * 100).toFixed(1) : '0';
            return `${val.toLocaleString('pt-BR')} views (${pct}%)`;
          }
        }
      }
    };
    geralTrafficApex = new ApexCharts(elT, optT);
    geralTrafficApex.render();
  }
  refreshIcons();
}

function initFromUrl() {
  const hash = window.location.hash;
  if (hash.startsWith('#ch=')) {
    const ch = hash.replace('#ch=', '');
    openChannel(ch, false);
  } else if (hash.startsWith('#view=geral')) {
    openChannel('geral', false);
  } else {
    openChannel('home', false);
  }
  refreshIcons();
}

window.addEventListener('popstate', initFromUrl);
document.addEventListener('DOMContentLoaded', () => {
  initFromUrl();
  refreshIcons();
});
"""

def render_html(channels_data, now_utc, all_scheduled=None):
    brt = timezone(timedelta(hours=-3))
    now_str = now_utc.astimezone(brt).strftime("%d/%m/%Y às %H:%M")
    total_ch = len(channels_data)
    online = sum(1 for c in channels_data if c.get("status_conexao") == "ONLINE")
    n_pessoal = sum(1 for c in channels_data if c.get("grupo_slug") == "pessoal")
    n_gvg = sum(1 for c in channels_data if c.get("grupo_slug") == "gvg")
    win = max((c.get("snapshot_window_hours", 0.0) for c in channels_data), default=0.0)
    win_48_txt = f"{min(win, 48.0):.1f}h de 48h medidas" if win < 48 else "48h completas"

    total_vph_60m = sum(c.get("vph_60m", 0) for c in channels_data)
    total_48h_all = sum(c.get("views_48h_canal", 0) for c in channels_data)
    total_subs_all = sum(c.get("inscritos", 0) for c in channels_data)
    total_views_all = sum(c.get("views_7d_canal", 0) for c in channels_data)
    total_hours_all = sum(c.get("watch_minutes_7d_canal", 0.0) for c in channels_data) / 60.0
    total_sched_count = len(all_scheduled) if all_scheduled else sum(c.get("total_videos_agendados", 0) for c in channels_data)

    # 1. Consolidado de Engajamento Global
    tot_likes = sum(c.get("engagement", {}).get("likes", 0) for c in channels_data)
    tot_comments = sum(c.get("engagement", {}).get("comments", 0) for c in channels_data)
    tot_shares = sum(c.get("engagement", {}).get("shares", 0) for c in channels_data)
    tot_net_subs = sum(c.get("engagement", {}).get("net_subscribers", 0) for c in channels_data)

    # 2. Consolidado de Geografia Global
    all_countries_agg = {}
    total_network_geo_views = 0
    for c in channels_data:
        for c_item in c.get("top_countries", []):
            code = c_item.get("code")
            if not code:
                continue
            if code not in all_countries_agg:
                all_countries_agg[code] = {
                    "code": code,
                    "name": c_item.get("name", code),
                    "flag": c_item.get("flag", "🌐"),
                    "views": 0,
                    "watch_minutes": 0.0,
                }
            all_countries_agg[code]["views"] += c_item.get("views", 0)
            all_countries_agg[code]["watch_minutes"] += c_item.get("watch_minutes", 0.0)
            total_network_geo_views += c_item.get("views", 0)

    sorted_network_countries = sorted(all_countries_agg.values(), key=lambda x: x["views"], reverse=True)
    for c_item in sorted_network_countries:
        c_item["pct"] = round((c_item["views"] / total_network_geo_views * 100), 1) if total_network_geo_views > 0 else 0.0

    # 3. Consolidado de Dispositivos Global
    all_devices_agg = {}
    total_network_dev_views = 0
    for c in channels_data:
        for d_item in c.get("device_breakdown", []):
            dev = d_item.get("device")
            if not dev:
                continue
            if dev not in all_devices_agg:
                all_devices_agg[dev] = {
                    "device": dev,
                    "label": d_item.get("label", dev),
                    "icon": d_item.get("icon", "help-circle"),
                    "views": 0,
                }
            all_devices_agg[dev]["views"] += d_item.get("views", 0)
            total_network_dev_views += d_item.get("views", 0)

    sorted_network_devices = sorted(all_devices_agg.values(), key=lambda x: x["views"], reverse=True)
    for d_item in sorted_network_devices:
        d_item["pct"] = round((d_item["views"] / total_network_dev_views * 100), 1) if total_network_dev_views > 0 else 0.0

    # 4. Consolidado de Descoberta vs Inscritos
    total_network_unsub_views = sum(c.get("audience_status", {}).get("unsubscribed_views", 0) for c in channels_data)
    total_network_sub_views = sum(c.get("audience_status", {}).get("subscribed_views", 0) for c in channels_data)
    total_network_aud_views = total_network_unsub_views + total_network_sub_views
    network_unsub_pct = round((total_network_unsub_views / total_network_aud_views * 100), 1) if total_network_aud_views > 0 else 0.0
    network_sub_pct = round((total_network_sub_views / total_network_aud_views * 100), 1) if total_network_aud_views > 0 else 0.0

    for c in channels_data:
        if not c.get("avatar_url"):
            c["avatar_url"] = DEFAULT_AVATARS.get(c.get("id"), "")

    # =========================================================================
    # 1. TELA INICIAL (HUB) - CARDS COM AVATAR E "GERAL" NO MEIO
    # =========================================================================
    hub_cards_html = []
    geral_card_html = f"""
<div class="hub-card card-geral" onclick="openChannel('geral')">
  <div>
    <div class="card-top">
      <div class="card-avatar-wrap">
        <div class="card-avatar geral-icon"><i data-lucide="globe" class="lucide-lg"></i></div>
        <span class="card-status-dot online"></span>
      </div>
      <div class="card-meta">
        <div class="card-name">Visão Geral Consolidada</div>
        <div class="card-subtext">Estúdio Dark · <b>7 Canais Integrados</b></div>
      </div>
    </div>
    <div class="card-metrics">
      <div class="cm-item"><span class="cm-lbl">Ritmo</span><b class="cm-val cyan">+{total_vph_60m}/h</b></div>
      <div class="cm-item"><span class="cm-lbl">Views 48h</span><b class="cm-val">+{total_48h_all:,}</b></div>
      <div class="cm-item"><span class="cm-lbl">Inscritos</span><b class="cm-val">{total_subs_all:,}</b></div>
    </div>
  </div>
  <div class="card-footer">
    <span>Abrir Painel Geral</span>
    <i data-lucide="arrow-right"></i>
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
    <span>Ver Detalhes do Canal</span>
    <i data-lucide="arrow-right"></i>
  </div>
</div>""")

    if len(channels_data) <= 3:
        hub_cards_html.append(geral_card_html)

    # Quick Switcher
    switcher_items = [
        '<button class="btn-back-hub" onclick="openChannel(\'home\')"><i data-lucide="arrow-left"></i> Início</button>',
        '<div class="ch-quick-switcher">',
        '<button class="ch-switch-btn" data-ch="geral" onclick="openChannel(\'geral\')"><i data-lucide="globe"></i> Geral</button>'
    ]
    for c in channels_data:
        switcher_items.append(
            f'<button class="ch-switch-btn" data-ch="{c["id"]}" onclick="openChannel(\'{c["id"]}\')"><img src="{_e(c["avatar_url"])}" alt=""> {_e(c["canal_titulo"])}</button>'
        )
    switcher_items.append('</div>')
    quick_switcher_html = "".join(switcher_items)

    # =========================================================================
    # 2. BANNERS, KPIS E SEÇÕES DO CANAL INDIVIDUAL
    # =========================================================================
    ch_banners_html = []
    ch_audience_html = []
    ch_r10_cards_html = []
    ch_top3_grids_html = []
    ch_sched_items_html = []

    medals = ["1º", "2º", "3º"]

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
        v_count = it.get("views_total", it.get("views_7d", 0))
        s = f'<span class="hi">{it["retention_pct"]:.1f}%</span> ({it["duration_str"]}) · '
        s += f'<span class="warn">⚠️ só {v_count} views</span>' if it.get("low_sample") else f'{v_count:,} views'
        return s

    for c in channels_data:
        on = (c.get("status_conexao") == "ONLINE")
        st_pill = '<span class="pill pill-green"><i data-lucide="check"></i> online</span>' if on else f'<span class="pill pill-red">{_e(c.get("status_conexao"))}</span>'
        handle_url = f"https://www.youtube.com/{c.get('handle', '')}" if c.get('handle') else "https://www.youtube.com"
        impr = f"{c.get('impressions_7d_canal'):,}" if c.get("impressions_7d_canal") is not None else '<span class="pending">⏳ pendente</span>'
        ctr = f"<b>{c.get('ctr_7d_canal'):.2f}%</b>" if c.get("ctr_7d_canal") is not None else '<span class="pending">⏳ pendente</span>'
        ret_pct = c.get('retention_pct_7d_canal')
        ret = (f"<b>{ret_pct:.1f}%</b> <span class='sub'>({c.get('retention_dur_7d_canal', '0m 00s')})</span>"
               if (ret_pct is not None and c.get("views_7d_canal", 0) > 0) else '<span class="sub">—</span>')

        # Banner & Strip
        ch_banners_html.append(f"""
<div class="ch-banner" data-canal="{c['id']}" style="display:none">
  <div class="ch-banner-left">
    <img src="{_e(c['avatar_url'])}" class="ch-banner-avatar" alt="" loading="lazy">
    <div class="ch-banner-info">
      <h2>{_e(c['canal_titulo'])} {st_pill}</h2>
      <div class="meta-row">
        <span>{_e(c['handle'])}</span> · 
        <span class="pill pill-{c['grupo_slug']}">{_e(c['grupo'])}</span> · 
        <a href="{_e(handle_url)}" target="_blank" rel="noopener" style="color:var(--cyan);font-weight:600;display:inline-flex;align-items:center;gap:4px">Canal no YouTube <i data-lucide="external-link"></i></a>
      </div>
    </div>
  </div>
  <div class="vph-badge">
    <i data-lucide="zap"></i> Ritmo: <b>+{c.get('vph_60m', 0)} views/h</b>
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

        # ABA 3: AUDIÊNCIA & DEMOGRAFIA
        eng = c.get("engagement", {})
        sub_stat = c.get("audience_status", {})
        countries = c.get("top_countries", [])
        devices = c.get("device_breakdown", [])

        # Countries rows
        c_rows = []
        if countries:
            for item in countries[:6]:
                pct = item.get("pct", 0.0)
                v_txt = f"{item.get('views', 0):,}"
                h_txt = f"{round(item.get('watch_minutes', 0) / 60, 1):,} h"
                c_rows.append(f"""
<div class="aud-list-row">
  <div class="aud-col-main">
    <span class="aud-flag">{item.get('flag', '🌐')}</span>
    <span class="aud-name">{_e(item.get('name', item.get('code')))}</span>
  </div>
  <div class="aud-bar-wrap">
    <div class="aud-bar-fill" style="width:{min(100, max(2, pct))}%"></div>
  </div>
  <div class="aud-val-group">
    <div class="aud-val">{pct:.1f}%</div>
    <div class="aud-sub">{v_txt} views · {h_txt}</div>
  </div>
</div>""")
        else:
            c_rows.append('<div class="empty-mini">Nenhum dado geográfico disponível ainda.</div>')

        # Devices cards
        d_cards = []
        if devices:
            for d in devices:
                pct = d.get("pct", 0.0)
                ico = d.get("icon", "help-circle")
                d_cards.append(f"""
<div class="device-box">
  <div class="dev-top">
    <span class="dev-label"><i data-lucide="{ico}"></i> {_e(d.get('label'))}</span>
    <span class="dev-pct">{pct:.1f}%</span>
  </div>
  <div class="aud-bar-wrap" style="width:100%;margin:4px 0 6px">
    <div class="aud-bar-fill" style="width:{min(100, max(2, pct))}%"></div>
  </div>
  <div class="aud-sub" style="font-family:'JetBrains Mono'">{d.get('views', 0):,} visualizações</div>
</div>""")
        else:
            d_cards.append('<div class="empty-mini" style="grid-column:span 2">Nenhum dado de dispositivo coletado.</div>')

        unsub_pct = sub_stat.get("unsubscribed_pct", 0.0)
        sub_pct = sub_stat.get("subscribed_pct", 0.0)
        unsub_views = sub_stat.get("unsubscribed_views", 0)
        sub_views = sub_stat.get("subscribed_views", 0)

        # Badge condicional de descoberta
        if unsub_pct >= 80:
            badge_descoberta = '<span class="pill pill-cyan">Alta Tração Orgânica</span>'
        elif unsub_pct >= 50:
            badge_descoberta = '<span class="pill pill-green">Audiência Balanceada</span>'
        else:
            badge_descoberta = '<span class="pill pill-purple">Comunidade Fidelizada</span>'

        net_sub_val = eng.get('net_subscribers', 0)
        net_sub_str = f"+{net_sub_val:,}" if net_sub_val > 0 else f"{net_sub_val:,}"
        net_sub_col = "var(--green)" if net_sub_val > 0 else ("var(--red)" if net_sub_val < 0 else "var(--text-muted)")

        ch_audience_html.append(f"""
<div class="ch-aud-panel" data-canal="{c['id']}" style="display:none">
  <!-- KPIs de Engajamento Vitalício -->
  <div class="kpi-grid">
    <div class="kpi">
      <div class="kpi-val" style="color:var(--cyan)">{eng.get('likes', 0):,}</div>
      <div class="kpi-lbl"><i data-lucide="thumbs-up"></i> Curtidas Totais</div>
    </div>
    <div class="kpi">
      <div class="kpi-val" style="color:var(--green)">{eng.get('comments', 0):,}</div>
      <div class="kpi-lbl"><i data-lucide="message-square"></i> Comentários Totais</div>
    </div>
    <div class="kpi">
      <div class="kpi-val" style="color:var(--amber)">{eng.get('shares', 0):,}</div>
      <div class="kpi-lbl"><i data-lucide="share-2"></i> Compartilhamentos</div>
    </div>
    <div class="kpi">
      <div class="kpi-val" style="color:{net_sub_col}">{net_sub_str}</div>
      <div class="kpi-lbl"><i data-lucide="user-plus"></i> Saldo Real Inscritos</div>
    </div>
  </div>

  <!-- Descoberta vs Base Fiel -->
  <div class="discovery-box">
    <div style="display:flex;justify-content:space-between;align-items:center">
      <div style="font-size:13px;font-weight:700;display:flex;align-items:center;gap:6px">
        <i data-lucide="compass"></i> Descoberta Algorítmica vs Inscritos
      </div>
      {badge_descoberta}
    </div>
    <div class="discovery-bar">
      <div class="discovery-seg-unsub" style="width:{unsub_pct}%" title="Não Inscritos: {unsub_pct}%"></div>
      <div class="discovery-seg-sub" style="width:{sub_pct}%" title="Inscritos: {sub_pct}%"></div>
    </div>
    <div class="discovery-legend">
      <span><b style="color:var(--cyan)">● Não Inscritos (Descoberta):</b> {unsub_pct:.1f}% ({unsub_views:,} views)</span>
      <span><b style="color:var(--purple)">● Inscritos (Base Fiel):</b> {sub_pct:.1f}% ({sub_views:,} views)</span>
    </div>
  </div>

  <!-- Split Grid: Países e Dispositivos -->
  <div class="audience-grid">
    <div class="aud-card">
      <div class="aud-card-head">
        <h3><i data-lucide="globe"></i> Top Países de Audiência</h3>
        <span class="pill pill-cyan">Vitalício</span>
      </div>
      <div>{''.join(c_rows)}</div>
    </div>
    <div class="aud-card">
      <div class="aud-card-head">
        <h3><i data-lucide="monitor-smartphone"></i> Distribuição por Dispositivo</h3>
        <span class="pill pill-cyan">Formatos</span>
      </div>
      <div class="device-grid">{''.join(d_cards)}</div>
    </div>
  </div>
</div>""")

        # 1 de 10
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
                b_cls = "r10-b1"; b_txt = f"1 de {out_of} — Top Desempenho!"
            elif r <= 3:
                b_cls = "r10-b2"; b_txt = f"{r} de {out_of} — Acima da Média"
            elif r <= 7:
                b_cls = "r10-b3"; b_txt = f"{r} de {out_of} — Na Média"
            else:
                b_cls = "r10-b4"; b_txt = f"{r} de {out_of} — Abaixo da Média"

            diff_sign = "+" if diff > 0 else ""
            diff_color = "var(--green)" if diff > 0 else ("var(--red)" if diff < 0 else "var(--text-muted)")

            ch_r10_cards_html.append(f"""
<div class="r10-card ch-r10-card" data-canal="{c['id']}" style="display:none">
  <div>
    <div class="r10-head">
      <div class="r10-ch-info">
        <h4>{_e(c['canal_titulo'])}</h4>
        <div class="sub" style="font-size:12px;color:var(--text-muted)">{_e(c['handle'])}</div>
      </div>
      <span class="r10-badge {b_cls}">{b_txt}</span>
    </div>
    <div class="r10-body">
      <img src="{_e(r10.get('thumbnail'))}" class="r10-thumb" alt="" loading="lazy">
      <div class="r10-vinfo">
        <a href="{_e(r10.get('url'))}" target="_blank" rel="noopener" class="r10-vtitle">{_e(r10.get('title'))}</a>
        <div class="sub" style="margin-top:4px;font-size:12px;color:var(--text-muted)">Publicado: {_e(r10.get('published_formatted'))}</div>
      </div>
    </div>
  </div>
  <div class="r10-metrics">
    <div>Views: <b>{r10.get('views', 0):,}</b></div>
    <div>Média 10 anteriores: <b>{r10.get('avg_prev', 0):,}</b></div>
    <div>Vs Média: <b style="color:{diff_color}">{diff_sign}{diff:.1f}%</b></div>
  </div>
</div>""")

        # Top 3
        pend = _e(c.get("reach_message") or "Aguardando 1º relatório do Google (24–48h)")
        ch_top3_grids_html.append(f"""
<div class="top3 ch-top3-grid" data-canal="{c['id']}" style="display:none">
  <div class="box"><h4><i data-lucide="target"></i> Maior Retenção</h4>{rank_list(c.get('top3_retencao_7d', []), fmt_ret, 'Sem views nos últimos 7 dias.')}</div>
  <div class="box"><h4><i data-lucide="eye"></i> Mais Views (7d)</h4>{rank_list(c.get('top3_views_7d', []), lambda it: f'<span class="hi">{it["views_7d"]:,} views</span> · ret. {it["retention_pct"]:.1f}%', 'Sem views nos últimos 7 dias.')}</div>
  <div class="box"><h4><i data-lucide="mouse-pointer"></i> Maior CTR (7d)</h4>{rank_list(c.get('top3_ctr_7d', []), lambda it: f'<span class="hi">{it["ctr_7d"]:.2f}%</span> · {it["impressions_7d"]:,} impr.', '⏳ ' + pend)}</div>
  <div class="box"><h4><i data-lucide="megaphone"></i> Mais Impressões</h4>{rank_list(c.get('top3_impressoes_7d', []), lambda it: f'<span class="hi">{it["impressions_7d"]:,}</span> impr. · CTR {it["ctr_7d"]:.2f}%', '⏳ ' + pend)}</div>
</div>""")

        # Agendados
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
    # VÍDEOS AO VIVO
    # =========================================================================
    single_live_html = []
    geral_live_html = []
    live = [v for c in channels_data for v in c.get("videos_ao_vivo_movimento", [])]

    for v in live[:150]:
        d60 = v.get("delta_60m")
        d48 = v.get("delta_48h") or 0
        tot = v.get("views_total") or 0
        d60_num = d60 if d60 is not None else 0
        d60_txt = f"+{d60:,}" if d60 is not None else "—"
        badge = '<span class="pill pill-amber">novo &lt;48h</span>' if v.get("is_pub_last_48h") else ""

        geral_live_html.append(f"""
<div class="lv-row" data-canal="{v.get('canal_id') or ''}" data-grupo="{v['grupo_slug']}" data-d60="{d60_num}" data-d48="{d48}" data-total="{tot}">
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
        st = '<span class="pill pill-green"><i data-lucide="check"></i> online</span>' if on else f'<span class="pill pill-red">{_e(c.get("status_conexao"))}</span>'
        impr = f"{c.get('impressions_7d_canal'):,}" if c.get("impressions_7d_canal") is not None else '<span class="pending">⏳ aguardando</span>'
        ctr = f"<b>{c.get('ctr_7d_canal'):.2f}%</b>" if c.get("ctr_7d_canal") is not None else '<span class="pending">⏳ aguardando</span>'
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
    <div class="sub" style="font-size:11px;color:var(--text-muted);margin-top:2px">{_e(c['handle'])} · <span class="pill pill-{c['grupo_slug']}">{_e(c['grupo'])}</span></div>
  </td>
  <td class="num" data-label="Ritmo VPH"><b style="color:var(--cyan)">{vph_txt}</b></td>
  <td class="num" data-label="Views 60 min">+{c.get('views_60m_canal', 0):,}</td>
  <td class="num" data-label="Views 48h">+{c.get('views_48h_canal', 0):,}</td>
  <td class="num" data-label="Views 7d"><b>{c.get('views_7d_canal', 0):,}</b></td>
  <td class="num" data-label="Impressões 7d">{impr}</td>
  <td class="num" data-label="CTR 7d">{ctr}</td>
  <td class="num" data-label="Retenção 7d">{ret}</td>
  <td class="num" data-label="Inscritos">{c.get('inscritos', 0):,}</td>
  <td class="num" data-label="Vídeos">{c.get('total_videos_publicos', 0)} públ.</td>
</tr>""")

    # Top 3 Geral
    cards_geral_top3 = []
    for c in channels_data:
        pend = _e(c.get("reach_message") or "Aguardando 1º relatório do Google (24–48h)")
        vph_badge = f'<span class="pill pill-green"><i data-lucide="zap"></i> +{c.get("vph_60m", 0)}/h</span>'
        cards_geral_top3.append(f"""
<details class="ch" data-grupo="{c['grupo_slug']}" open style="margin-bottom:12px;background:var(--surface);border:1px solid var(--border);border-radius:12px;overflow:hidden">
  <summary style="display:flex;justify-content:space-between;align-items:center;padding:12px 16px;background:var(--surface-2);cursor:pointer">
    <div class="ch-head" style="display:flex;align-items:center;gap:10px">
      <img src="{_e(c['avatar_url'])}" style="width:32px;height:32px;border-radius:50%;object-fit:cover" alt="">
      <div>
        <h3 style="font-size:14px;display:flex;align-items:center;gap:6px">{_e(c['canal_titulo'])} {vph_badge}</h3>
        <small style="font-size:11px;color:var(--text-muted)">{_e(c['handle'])} · <span class="pill pill-{c['grupo_slug']}">{_e(c['grupo'])}</span></small>
      </div>
    </div>
    <div style="font-size:12px;color:var(--text-muted);display:flex;gap:12px">
      <span>Views 7d: <b style="color:var(--text)">{c.get('views_7d_canal', 0):,}</b></span>
      <span>Inscritos: <b style="color:var(--text)">{c.get('inscritos', 0):,}</b></span>
    </div>
  </summary>
  <div class="top3" style="padding:12px">
    <div class="box"><h4><i data-lucide="target"></i> Retenção</h4>{rank_list(c.get('top3_retencao_7d', []), fmt_ret, 'Sem views nos últimos 7 dias.')}</div>
    <div class="box"><h4><i data-lucide="eye"></i> Mais Views</h4>{rank_list(c.get('top3_views_7d', []), lambda it: f'<span class="hi">{it["views_7d"]:,} views</span> · ret. {it["retention_pct"]:.1f}%', 'Sem views nos últimos 7 dias.')}</div>
    <div class="box"><h4><i data-lucide="mouse-pointer"></i> CTR</h4>{rank_list(c.get('top3_ctr_7d', []), lambda it: f'<span class="hi">{it["ctr_7d"]:.2f}%</span> · {it["impressions_7d"]:,} impr.', '⏳ ' + pend)}</div>
    <div class="box"><h4><i data-lucide="megaphone"></i> Impressões</h4>{rank_list(c.get('top3_impressoes_7d', []), lambda it: f'<span class="hi">{it["impressions_7d"]:,}</span> impr. · CTR {it["ctr_7d"]:.2f}%', '⏳ ' + pend)}</div>
  </div>
</details>""")

    # 1 de 10 Geral
    rank10_cards_geral = []
    for c in channels_data:
        r10 = c.get("rank_1_de_10")
        if not r10:
            rank10_cards_geral.append(f"""
<div class="r10-card" data-grupo="{c['grupo_slug']}" onclick="openChannel('{c['id']}')" style="cursor:pointer">
  <div class="r10-head">
    <div class="r10-ch-info"><h4>{_e(c['canal_titulo'])}</h4><div class="sub" style="font-size:11px;color:var(--text-muted)">{_e(c['handle'])}</div></div>
    <span class="pill pill-{c['grupo_slug']}">{_e(c['grupo'])}</span>
  </div>
  <div class="empty-mini">Nenhum vídeo recente com histórico suficiente.</div>
</div>""")
            continue

        r = r10.get("rank", 10)
        out_of = r10.get("out_of", 10)
        diff = r10.get("diff_pct", 0.0)
        if r == 1:
            b_cls = "r10-b1"; b_txt = f"1 de {out_of} — Top Desempenho!"
        elif r <= 3:
            b_cls = "r10-b2"; b_txt = f"{r} de {out_of} — Acima da Média"
        elif r <= 7:
            b_cls = "r10-b3"; b_txt = f"{r} de {out_of} — Na Média"
        else:
            b_cls = "r10-b4"; b_txt = f"{r} de {out_of} — Abaixo da Média"

        diff_sign = "+" if diff > 0 else ""
        diff_color = "var(--green)" if diff > 0 else ("var(--red)" if diff < 0 else "var(--text-muted)")

        rank10_cards_geral.append(f"""
<div class="r10-card" data-grupo="{c['grupo_slug']}">
  <div>
    <div class="r10-head" onclick="openChannel('{c['id']}')" style="cursor:pointer">
      <div class="r10-ch-info">
        <h4>{_e(c['canal_titulo'])}</h4>
        <div class="sub" style="font-size:11px;color:var(--text-muted)">{_e(c['handle'])} · <span class="pill pill-{c['grupo_slug']}">{_e(c['grupo'])}</span></div>
      </div>
      <span class="r10-badge {b_cls}">{b_txt}</span>
    </div>
    <div class="r10-body">
      <img src="{_e(r10.get('thumbnail'))}" class="r10-thumb" alt="" loading="lazy">
      <div class="r10-vinfo">
        <a href="{_e(r10.get('url'))}" target="_blank" rel="noopener" class="r10-vtitle">{_e(r10.get('title'))}</a>
        <div class="sub" style="margin-top:4px;font-size:11px;color:var(--text-muted)">Publicado: {_e(r10.get('published_formatted'))}</div>
      </div>
    </div>
  </div>
  <div class="r10-metrics">
    <div>Views: <b>{r10.get('views', 0):,}</b></div>
    <div>Média 10 anteriores: <b>{r10.get('avg_prev', 0):,}</b></div>
    <div>Vs Média: <b style="color:{diff_color}">{diff_sign}{diff:.1f}%</b></div>
  </div>
</div>""")

    # Calendário Unificado
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
            t_str = "Agendado"

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
  <div class="cal-date-title"><i data-lucide="calendar"></i> {d_label} ({len(items)} {('estreia' if len(items)==1 else 'estreias')})</div>
  {''.join(rows_cal)}
</div>""")
    else:
        cal_html.append('<div class="empty">Nenhum vídeo agendado no momento em nenhum dos canais.</div>')

    # Timeseries JSON
    timeseries_data = {
        c["id"]: {
            "title": c.get("canal_titulo"),
            "handle": c.get("handle"),
            "avatar_url": c.get("avatar_url"),
            "group_slug": c.get("grupo_slug"),
            "history_lifetime": c.get("history_lifetime", []),
            "traffic_sources_lifetime": c.get("traffic_sources_lifetime", []),
            "top_countries": c.get("top_countries", []),
            "device_breakdown": c.get("device_breakdown", []),
            "audience_status": c.get("audience_status", {}),
            "engagement": c.get("engagement", {}),
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

    # Linhas de países consolidada na aba Geral
    network_c_rows = []
    if sorted_network_countries:
        for item in sorted_network_countries[:8]:
            pct = item.get("pct", 0.0)
            v_txt = f"{item.get('views', 0):,}"
            h_txt = f"{round(item.get('watch_minutes', 0) / 60, 1):,} h"
            network_c_rows.append(f"""
<div class="aud-list-row">
  <div class="aud-col-main">
    <span class="aud-flag">{item.get('flag', '🌐')}</span>
    <span class="aud-name">{_e(item.get('name', item.get('code')))}</span>
  </div>
  <div class="aud-bar-wrap">
    <div class="aud-bar-fill" style="width:{min(100, max(2, pct))}%"></div>
  </div>
  <div class="aud-val-group">
    <div class="aud-val">{pct:.1f}%</div>
    <div class="aud-sub">{v_txt} views · {h_txt}</div>
  </div>
</div>""")
    else:
        network_c_rows.append('<div class="empty-mini">Nenhum dado geográfico consolidado.</div>')

    # Cards de dispositivos consolidada na aba Geral
    network_d_cards = []
    if sorted_network_devices:
        for d in sorted_network_devices:
            pct = d.get("pct", 0.0)
            ico = d.get("icon", "help-circle")
            network_d_cards.append(f"""
<div class="device-box">
  <div class="dev-top">
    <span class="dev-label"><i data-lucide="{ico}"></i> {_e(d.get('label'))}</span>
    <span class="dev-pct">{pct:.1f}%</span>
  </div>
  <div class="aud-bar-wrap" style="width:100%;margin:4px 0 6px">
    <div class="aud-bar-fill" style="width:{min(100, max(2, pct))}%"></div>
  </div>
  <div class="aud-sub" style="font-family:'JetBrains Mono'">{d.get('views', 0):,} visualizações</div>
</div>""")
    else:
        network_d_cards.append('<div class="empty-mini" style="grid-column:span 2">Nenhum dado de dispositivo consolidado.</div>')

    tot_net_subs_str = f"+{tot_net_subs:,}" if tot_net_subs > 0 else f"{tot_net_subs:,}"
    tot_net_subs_col = "var(--green)" if tot_net_subs > 0 else ("var(--red)" if tot_net_subs < 0 else "var(--text-muted)")

    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
<meta http-equiv="refresh" content="600">
<meta name="theme-color" content="#090D14">
<title>Dark Studio — Painel Multi-Canal</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;600;700&display=swap" rel="stylesheet">
<script src="https://unpkg.com/lucide@0.460.0/dist/umd/lucide.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/apexcharts@4.0.0/dist/apexcharts.min.js"></script>
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
        <h1><i data-lucide="layout-grid"></i> Dark Studio — Multi-Canal</h1>
        <div class="meta"><b>{online}/{total_ch}</b> canais online · Atualizado às <b>{now_str} BRT</b> · 100% Nuvem</div>
        <div class="hub-chips">
          <button class="chip active" onclick="filterHubGroup('all', this)">Todos os Canais ({total_ch})</button>
          <button class="chip" onclick="filterHubGroup('pessoal', this)">Pessoais ({n_pessoal})</button>
          <button class="chip" onclick="filterHubGroup('gvg', this)">Startup GVG ({n_gvg})</button>
        </div>
      </div>
      <div class="vph-badge" style="font-size:13px;padding:8px 16px">
        <i data-lucide="zap"></i> Ritmo da Fábrica: <b>+{total_vph_60m} views/h</b>
      </div>
    </div>

    <div class="hub-grid">
      {''.join(hub_cards_html)}
    </div>
  </div>

  <!-- ================================================================= -->
  <!-- 2. VISÃO EXCLUSIVA DO CANAL SELECIONADO                           -->
  <!-- ================================================================= -->
  <div class="view-section" id="view-channel">
    <div class="channel-nav-bar">
      {quick_switcher_html}
    </div>

    {''.join(ch_banners_html)}

    <!-- Abas de Navegação do Canal -->
    <div class="sub-nav">
      <button class="sub-tab-btn active" id="btn-ch-tab-live" onclick="switchChannelSubTab('live', this)"><i data-lucide="radio"></i> Ao Vivo & Vídeos</button>
      <button class="sub-tab-btn" id="btn-ch-tab-charts" onclick="switchChannelSubTab('charts', this)"><i data-lucide="line-chart"></i> Gráficos & Desempenho</button>
      <button class="sub-tab-btn" id="btn-ch-tab-audience" onclick="switchChannelSubTab('audience', this)"><i data-lucide="users"></i> Audiência & Geografia</button>
      <button class="sub-tab-btn" id="btn-ch-tab-rank10" onclick="switchChannelSubTab('rank10', this)"><i data-lucide="target"></i> Lançamento (1 de 10)</button>
      <button class="sub-tab-btn" id="btn-ch-tab-top3" onclick="switchChannelSubTab('top3', this)"><i data-lucide="trophy"></i> Top 3 (7 dias)</button>
      <button class="sub-tab-btn" id="btn-ch-tab-calendar" onclick="switchChannelSubTab('calendar', this)"><i data-lucide="calendar"></i> Próximas Estreias</button>
    </div>

    <!-- SUB-ABA 1: AO VIVO & VÍDEOS -->
    <div class="sub-content active" id="ch-tab-live">
      <div class="sec">
        <div class="sec-top">
          <div>
            <div class="sec-title"><i data-lucide="flame"></i> Vídeos com movimentação recente no canal</div>
            <div class="sec-hint">Views ganhas em 60 min e 48 horas acumuladas ({win_48_txt})</div>
          </div>
          <div class="seg" style="max-width:440px">
            <button id="ch-seg-d60" onclick="setSingleChannelSort('d60', this)">Últimos 60 min</button>
            <button class="active" id="ch-seg-d48" onclick="setSingleChannelSort('d48', this)">Últimas 48h</button>
            <button id="ch-seg-total" onclick="setSingleChannelSort('total', this)">Total Views</button>
          </div>
        </div>
        <div class="lv-count" id="ch-live-count" style="font-size:12px;color:var(--text-muted);margin-bottom:8px"></div>
        <div id="ch-live-list">{''.join(single_live_html)}</div>
        <div class="empty" id="ch-live-empty" style="display:none"></div>
      </div>
    </div>

    <!-- SUB-ABA 2: GRÁFICOS & ANALYTICS -->
    <div class="sub-content" id="ch-tab-charts">
      <div class="filters-panel">
        <div class="fg-row">
          <div class="fg-lbl"><i data-lucide="calendar"></i> Período</div>
          <div class="fg-ctrl seg">
            <button class="period-btn" data-p="7d" onclick="setSingleChannelPeriod('7d', this)">7 dias</button>
            <button class="period-btn active" data-p="30d" onclick="setSingleChannelPeriod('30d', this)">30 dias</button>
            <button class="period-btn" data-p="month" onclick="setSingleChannelPeriod('month', this)">Este mês</button>
            <button class="period-btn" data-p="180d" onclick="setSingleChannelPeriod('180d', this)">180 dias</button>
            <button class="period-btn" data-p="year" onclick="setSingleChannelPeriod('year', this)">Este ano</button>
            <button class="period-btn" data-p="all" onclick="setSingleChannelPeriod('all', this)">Desde o Início</button>
          </div>
        </div>
        <div class="fg-row" style="margin-bottom:0">
          <div class="fg-lbl"><i data-lucide="video"></i> Formato</div>
          <div class="fg-ctrl seg" style="max-width:520px">
            <button class="format-btn active" data-f="all" onclick="setSingleChannelFormat('all', this)">Todos (Vídeos + Shorts)</button>
            <button class="format-btn" data-f="video" onclick="setSingleChannelFormat('video', this)">🎬 Só Vídeos (Longos)</button>
            <button class="format-btn" data-f="shorts" onclick="setSingleChannelFormat('shorts', this)">⚡ Só Shorts</button>
          </div>
        </div>
      </div>

      <div class="kpi-grid">
        <div class="kpi"><div class="kpi-val" id="ch-kpi-views">—</div><div class="kpi-lbl"><i data-lucide="eye"></i> Visualizações</div></div>
        <div class="kpi"><div class="kpi-val" id="ch-kpi-subs" style="color:var(--green)">—</div><div class="kpi-lbl"><i data-lucide="user-plus"></i> Saldo de Inscritos</div></div>
        <div class="kpi"><div class="kpi-val" id="ch-kpi-hours" style="color:var(--amber)">—</div><div class="kpi-lbl"><i data-lucide="clock"></i> Tempo de Exibição</div></div>
        <div class="kpi"><div class="kpi-val" id="ch-kpi-avg" style="color:var(--purple)">—</div><div class="kpi-lbl"><i data-lucide="activity"></i> Média Diária</div></div>
      </div>

      <div class="chart-card">
        <div class="chart-head"><h3 id="ch-chart-title"><i data-lucide="line-chart"></i> Curva de Visualizações Diárias</h3></div>
        <div class="chart-box"><div id="chChartViews"></div></div>
      </div>

      <div class="charts-split">
        <div class="chart-card">
          <div class="chart-head"><h3><i data-lucide="user-plus"></i> Saldo Diário de Inscritos (+ / -)</h3></div>
          <div class="chart-box"><div id="chChartSubs"></div></div>
        </div>
        <div class="chart-card">
          <div class="chart-head">
            <h3 id="ch-chart-traffic-title"><i data-lucide="pie-chart"></i> Origem do Tráfego</h3>
            <span class="sub" id="ch-traffic-top-source" style="font-size:11px;color:var(--text-muted)">Principal: <b>—</b></span>
          </div>
          <div class="chart-box"><div id="chChartTraffic"></div></div>
        </div>
      </div>
    </div>

    <!-- SUB-ABA 3: AUDIÊNCIA & DEMOGRAFIA -->
    <div class="sub-content" id="ch-tab-audience">
      {''.join(ch_audience_html)}
    </div>

    <!-- SUB-ABA 4: LANÇAMENTO 1 DE 10 -->
    <div class="sub-content" id="ch-tab-rank10">
      <div class="sec-top" style="margin-bottom:12px">
        <div>
          <div class="sec-title"><i data-lucide="target"></i> Desempenho do Vídeo Mais Recente (1 de 10)</div>
          <div class="sec-hint">Compara as views do último vídeo com a média dos 10 vídeos anteriores do canal</div>
        </div>
      </div>
      {''.join(ch_r10_cards_html)}
    </div>

    <!-- SUB-ABA 5: TOP 3 DO CANAL -->
    <div class="sub-content" id="ch-tab-top3">
      <div class="sec-top" style="margin-bottom:12px">
        <div>
          <div class="sec-title"><i data-lucide="trophy"></i> Top 3 do Canal nos Últimos 7 Dias</div>
          <div class="sec-hint">Retenção vitalícia (com ≥{MIN_VIEWS_FOR_RETENTION_RANK} views), Views, CTR e Impressões</div>
        </div>
      </div>
      {''.join(ch_top3_grids_html)}
    </div>

    <!-- SUB-ABA 6: AGENDADOS DO CANAL -->
    <div class="sub-content" id="ch-tab-calendar">
      <div class="sec-top" style="margin-bottom:12px">
        <div>
          <div class="sec-title"><i data-lucide="calendar"></i> Próximas Estreias Agendadas deste Canal</div>
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
    <div class="channel-nav-bar">
      {quick_switcher_html}
    </div>

    <div class="topbar">
      <div class="topbar-main">
        <div>
          <h1><i data-lucide="globe"></i> Painel Geral — Consolidado de Todos os Canais</h1>
          <div class="meta">Atualizado às <b>{now_str} BRT</b> · <b>{online}/{total_ch}</b> canais online · Nuvem GitHub Actions</div>
        </div>
        <div class="vph-badge">
          <i data-lucide="zap"></i> Ritmo da Fábrica: <b>+{total_vph_60m} views/hora</b>
        </div>
      </div>
      <div class="chips" id="geral-chips" style="margin-top:12px">
        <button class="chip active" onclick="filterGeralGroup('all', this)">Todos ({total_ch})</button>
        <button class="chip" onclick="filterGeralGroup('pessoal', this)">Pessoais ({n_pessoal})</button>
        <button class="chip" onclick="filterGeralGroup('gvg', this)">Startup GVG ({n_gvg})</button>
      </div>
    </div>

    <div class="sub-nav">
      <button class="sub-tab-btn active" id="btn-geral-tab-live" onclick="switchGeralMainTab('live', this)"><i data-lucide="radio"></i> Radar ao Vivo</button>
      <button class="sub-tab-btn" id="btn-geral-tab-charts" onclick="switchGeralMainTab('charts', this)"><i data-lucide="line-chart"></i> Gráficos & Histórico</button>
      <button class="sub-tab-btn" id="btn-geral-tab-audience" onclick="switchGeralMainTab('audience', this)"><i data-lucide="users"></i> Audiência Consolidada</button>
      <button class="sub-tab-btn" id="btn-geral-tab-rank10" onclick="switchGeralMainTab('rank10', this)"><i data-lucide="target"></i> Lançamentos (1 de 10)</button>
      <button class="sub-tab-btn" id="btn-geral-tab-calendar" onclick="switchGeralMainTab('calendar', this)"><i data-lucide="calendar"></i> Calendário ({total_sched_count})</button>
    </div>

    <!-- GERAL TAB 1: RADAR AO VIVO -->
    <div class="sub-content active" id="geral-tab-live">
      <div class="sec">
        <div class="sec-top">
          <div>
            <div class="sec-title"><i data-lucide="flame"></i> Mais vistos agora — todos os canais</div>
            <div class="sec-hint">Views ganhas por vídeo público · janela acumulada: {win_48_txt}</div>
          </div>
          <div class="seg" style="max-width:440px">
            <button class="active" id="geral-seg-d60" onclick="setGeralSort('d60', this)">Últimos 60 min</button>
            <button id="geral-seg-d48" onclick="setGeralSort('d48', this)">Últimas 48h</button>
            <button id="geral-seg-total" onclick="setGeralSort('total', this)">Total Views</button>
          </div>
        </div>
        <div class="lv-count" id="geral-live-count" style="font-size:12px;color:var(--text-muted);margin-bottom:8px"></div>
        <div id="geral-live-list">{''.join(geral_live_html)}</div>
        <div class="empty" id="geral-live-empty" style="display:none"></div>
      </div>

      <div class="sec">
        <div class="sec-top"><div>
          <div class="sec-title"><i data-lucide="table"></i> Comparativo de Desempenho</div>
          <div class="sec-hint">Ritmo VPH (views/h) · 60m / 48h (medição própria) · 7d via Analytics API</div>
        </div></div>
        <div class="tbl-wrap">
          <table class="cmp">
            <thead><tr><th>Canal</th><th class="num">Ritmo VPH</th><th class="num">60 min</th><th class="num">48h</th><th class="num">Views 7d</th><th class="num">Impressões 7d</th><th class="num">CTR 7d</th><th class="num">Retenção 7d</th><th class="num">Inscritos</th><th class="num">Vídeos</th></tr></thead>
            <tbody>{''.join(cmp_rows)}</tbody>
          </table>
        </div>
      </div>

      <div class="sec-top" style="margin:16px 2px 10px"><div>
        <div class="sec-title"><i data-lucide="trophy"></i> Top 3 de cada canal (7 dias)</div>
        <div class="sec-hint">Toque no canal para abrir/fechar · retenção prioriza vídeos com ≥{MIN_VIEWS_FOR_RETENTION_RANK} views</div>
      </div></div>
      {''.join(cards_geral_top3)}
    </div>

    <!-- GERAL TAB 2: GRÁFICOS & HISTÓRICO -->
    <div class="sub-content" id="geral-tab-charts">
      <div class="filters-panel">
        <div class="fg-row">
          <div class="fg-lbl"><i data-lucide="calendar"></i> Período</div>
          <div class="fg-ctrl seg">
            <button class="period-btn" data-p="7d" onclick="setGeralChartPeriod('7d', this)">7 dias</button>
            <button class="period-btn active" data-p="30d" onclick="setGeralChartPeriod('30d', this)">30 dias</button>
            <button class="period-btn" data-p="month" onclick="setGeralChartPeriod('month', this)">Este mês</button>
            <button class="period-btn" data-p="180d" onclick="setGeralChartPeriod('180d', this)">180 dias</button>
            <button class="period-btn" data-p="year" onclick="setGeralChartPeriod('year', this)">Este ano</button>
            <button class="period-btn" data-p="all" onclick="setGeralChartPeriod('all', this)">Desde o Início</button>
          </div>
        </div>
        <div class="fg-row">
          <div class="fg-lbl"><i data-lucide="video"></i> Formato</div>
          <div class="fg-ctrl seg" style="max-width:520px">
            <button class="format-btn active" data-f="all" onclick="setGeralChartFormat('all', this)">Todos (Vídeos + Shorts)</button>
            <button class="format-btn" data-f="video" onclick="setGeralChartFormat('video', this)">🎬 Só Vídeos (Longos)</button>
            <button class="format-btn" data-f="shorts" onclick="setGeralChartFormat('shorts', this)">⚡ Só Shorts</button>
          </div>
        </div>
        <div class="fg-row" style="margin-bottom:0">
          <div class="fg-lbl"><i data-lucide="tv"></i> Canal</div>
          <div class="fg-ctrl ch-chips">{''.join(geral_chart_chips)}</div>
        </div>
      </div>

      <div class="kpi-grid">
        <div class="kpi"><div class="kpi-val" id="geral-kpi-views">—</div><div class="kpi-lbl"><i data-lucide="eye"></i> Visualizações</div></div>
        <div class="kpi"><div class="kpi-val" id="geral-kpi-subs" style="color:var(--green)">—</div><div class="kpi-lbl"><i data-lucide="user-plus"></i> Saldo de Inscritos</div></div>
        <div class="kpi"><div class="kpi-val" id="geral-kpi-hours" style="color:var(--amber)">—</div><div class="kpi-lbl"><i data-lucide="clock"></i> Tempo de Exibição</div></div>
        <div class="kpi"><div class="kpi-val" id="geral-kpi-avg" style="color:var(--purple)">—</div><div class="kpi-lbl"><i data-lucide="activity"></i> Média Diária</div></div>
      </div>

      <div class="chart-card">
        <div class="chart-head"><h3 id="geral-chart-title"><i data-lucide="line-chart"></i> Curva de Visualizações Diárias</h3></div>
        <div class="chart-box"><div id="geralChartViews"></div></div>
      </div>

      <div class="charts-split">
        <div class="chart-card">
          <div class="chart-head"><h3><i data-lucide="user-plus"></i> Saldo Diário de Inscritos (+ / -)</h3></div>
          <div class="chart-box"><div id="geralChartSubs"></div></div>
        </div>
        <div class="chart-card">
          <div class="chart-head">
            <h3 id="geral-chart-traffic-title"><i data-lucide="pie-chart"></i> Origem do Tráfego</h3>
            <span class="sub" id="geral-traffic-top-source" style="font-size:11px;color:var(--text-muted)">Principal: <b>—</b></span>
          </div>
          <div class="chart-box"><div id="geralChartTraffic"></div></div>
        </div>
      </div>
    </div>

    <!-- GERAL TAB 3: AUDIÊNCIA CONSOLIDADA -->
    <div class="sub-content" id="geral-tab-audience">
      <div class="kpi-grid">
        <div class="kpi"><div class="kpi-val" style="color:var(--cyan)">{tot_likes:,}</div><div class="kpi-lbl"><i data-lucide="thumbs-up"></i> Total de Curtidas</div></div>
        <div class="kpi"><div class="kpi-val" style="color:var(--green)">{tot_comments:,}</div><div class="kpi-lbl"><i data-lucide="message-square"></i> Total de Comentários</div></div>
        <div class="kpi"><div class="kpi-val" style="color:var(--amber)">{tot_shares:,}</div><div class="kpi-lbl"><i data-lucide="share-2"></i> Total Compartilhamentos</div></div>
        <div class="kpi"><div class="kpi-val" style="color:{tot_net_subs_col}">{tot_net_subs_str}</div><div class="kpi-lbl"><i data-lucide="user-plus"></i> Saldo Real Inscritos</div></div>
      </div>

      <!-- Descoberta Global da Rede -->
      <div class="discovery-box">
        <div style="display:flex;justify-content:space-between;align-items:center">
          <div style="font-size:13px;font-weight:700;display:flex;align-items:center;gap:6px">
            <i data-lucide="compass"></i> Descoberta Algorítmica da Rede
          </div>
          <span class="pill pill-cyan">Consolidado 7 Canais</span>
        </div>
        <div class="discovery-bar">
          <div class="discovery-seg-unsub" style="width:{network_unsub_pct}%" title="Não Inscritos: {network_unsub_pct}%"></div>
          <div class="discovery-seg-sub" style="width:{network_sub_pct}%" title="Inscritos: {network_sub_pct}%"></div>
        </div>
        <div class="discovery-legend">
          <span><b style="color:var(--cyan)">● Não Inscritos (Descoberta):</b> {network_unsub_pct:.1f}% ({total_network_unsub_views:,} views)</span>
          <span><b style="color:var(--purple)">● Inscritos (Base Fiel):</b> {network_sub_pct:.1f}% ({total_network_sub_views:,} views)</span>
        </div>
      </div>

      <!-- Grid Split Países e Dispositivos Dinâmicos da Rede -->
      <div class="audience-grid">
        <div class="aud-card">
          <div class="aud-card-head">
            <h3><i data-lucide="globe"></i> Top Países da Fábrica ({len(sorted_network_countries)} Regiões)</h3>
            <span class="pill pill-cyan">Consolidado</span>
          </div>
          <div>{''.join(network_c_rows)}</div>
        </div>
        <div class="aud-card">
          <div class="aud-card-head">
            <h3><i data-lucide="monitor-smartphone"></i> Dispositivos da Rede ({total_network_dev_views:,} Views)</h3>
            <span class="pill pill-cyan">Global</span>
          </div>
          <div class="device-grid">{''.join(network_d_cards)}</div>
        </div>
      </div>
    </div>

    <!-- GERAL TAB 4: 1 DE 10 -->
    <div class="sub-content" id="geral-tab-rank10">
      <div class="sec-top" style="margin-bottom:12px">
        <div>
          <div class="sec-title"><i data-lucide="target"></i> Desempenho do Vídeo Mais Recente (1 de 10)</div>
          <div class="sec-hint">Compara as views do último vídeo postado com a média dos 10 vídeos anteriores do canal</div>
        </div>
      </div>
      <div class="rank10-grid" style="display:grid;grid-template-columns:repeat(2,1fr);gap:12px">{''.join(rank10_cards_geral)}</div>
    </div>

    <!-- GERAL TAB 5: CALENDÁRIO DE ESTREIAS -->
    <div class="sub-content" id="geral-tab-calendar">
      <div class="sec-top" style="margin-bottom:12px">
        <div>
          <div class="sec-title"><i data-lucide="calendar"></i> Linha do Tempo de Vídeos Agendados ({total_sched_count} Estreias)</div>
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
