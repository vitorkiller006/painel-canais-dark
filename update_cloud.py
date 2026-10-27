# -*- coding: utf-8 -*-
"""
===============================================================================
DARK FACTORY CLOUD ENGINE — GITHUB ACTIONS (100% NUVEM, PC DESLIGADO)
ARQUIVO: update_cloud.py
===============================================================================
Roda direto nos servidores do GitHub Actions a cada 30 minutos:
- Lê os tokens criptografados do GitHub Secret (CHANNELS_TOKENS_JSON)
- Consulta YouTube Data API v3, YouTube Analytics API v2 e YouTube Reporting API v1
- Atualiza analytics_realtime_snapshot.json e index.html no GitHub Pages
===============================================================================
"""

import os
import sys
import csv
import io
import gzip
import json
import urllib.request
from pathlib import Path
from datetime import datetime, timezone, timedelta

try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except Exception:
    pass

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

REPO_DIR = Path(__file__).resolve().parent
HTML_OUTPUT = REPO_DIR / "index.html"
SNAPSHOT_FILE = REPO_DIR / "analytics_realtime_snapshot.json"

MIN_VIEWS_FOR_RETENTION_RANK = 10
MIN_IMPRESSIONS_FOR_CTR_RANK = 20

CHANNELS_CONFIG = [
    {
        "id": "stickman",
        "nome_projeto": "Stickman - Shorts",
        "grupo": "Pessoais (Vitor)",
        "grupo_slug": "pessoal",
        "canal_padrao": "How It's Made Oficial",
        "handle_padrao": "@howitsmadeoficial",
        "expected_channel_id": "UCnhTlPoh9oJ9wzvt7zeG_Sg",
        "auth_bat": "AUTORIZAR_YOUTUBE.bat",
    },
    {
        "id": "biblia",
        "nome_projeto": "Anime + Bíblia",
        "grupo": "Pessoais (Vitor)",
        "grupo_slug": "pessoal",
        "canal_padrao": "Bíblia Oculta",
        "handle_padrao": "@bibliaoculta7",
        "expected_channel_id": "UCvYkrgAEbT7vm1nPY-ssGMA",
        "auth_bat": "AUTORIZAR_YOUTUBE.bat",
    },
    {
        "id": "indiano_doc",
        "nome_projeto": "Canal Indiano + Doc da Índia",
        "grupo": "Pessoais (Vitor)",
        "grupo_slug": "pessoal",
        "canal_padrao": "Untold Bharat",
        "handle_padrao": "@uuntoldbharat2d",
        "expected_channel_id": "UCPvwh6a2S_29fpeNiluP5Vw",
        "auth_bat": "AUTORIZAR_UNTOLD_BHARAT.bat",
    },
    {
        "id": "espaco",
        "nome_projeto": "Espaço + Segredo Oculto",
        "grupo": "Pessoais (Vitor)",
        "grupo_slug": "pessoal",
        "canal_padrao": "Cosmic Abyss",
        "handle_padrao": "@cosmicabyssdoc",
        "expected_channel_id": "UCNUMK-cBY6g2mztWXRO9z7g",
        "auth_bat": "AUTORIZAR_YOUTUBE.bat",
    },
    {
        "id": "novela",
        "nome_projeto": "Novela + Livro",
        "grupo": "Pessoais (Vitor)",
        "grupo_slug": "pessoal",
        "canal_padrao": "Lorena Vane",
        "handle_padrao": "@lorenavane1",
        "expected_channel_id": "UCYaE8-AZDscjX9Og_S7fLXw",
        "auth_bat": "AUTORIZAR_YOUTUBE.bat",
    },
    {
        "id": "hearttangle",
        "nome_projeto": "Indiano + Conflitos de Relacionamento",
        "grupo": "Startup GVG (Vitor + Amigo)",
        "grupo_slug": "gvg",
        "canal_padrao": "HeartTangle",
        "handle_padrao": "@heartangle2d",
        "expected_channel_id": "UCVzhK47egvPSjSKUTU_zzvg",
        "auth_bat": "AUTORIZAR_HEARTTANGLE.bat",
    },
    {
        "id": "segredos_olga",
        "nome_projeto": "Brasileiro + Realista + Conflitos",
        "grupo": "Startup GVG (Vitor + Amigo)",
        "grupo_slug": "gvg",
        "canal_padrao": "Segredos da Olga",
        "handle_padrao": "@segredosdaolga",
        "expected_channel_id": "UCs7UIbmLCqwJUmALKYuR5yQ",
        "auth_bat": "AUTORIZAR_CANAL_BRASILEIRO.bat",
    },
]


def load_credentials_from_env(channel_id, tokens_bundle):
    token_info = tokens_bundle.get(channel_id)
    if not token_info:
        return None, "Token ausente no GitHub Secret CHANNELS_TOKENS_JSON."
    try:
        creds = Credentials.from_authorized_user_info(token_info)
        if not creds.valid:
            if creds.refresh_token:
                creds.refresh(Request())
            else:
                return None, "Token inválido e sem refresh_token."
        return creds, None
    except Exception as e:
        return None, str(e)


def load_snapshots():
    if SNAPSHOT_FILE.exists():
        try:
            with open(SNAPSHOT_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict):
                    return data
        except Exception:
            pass
    return {}


def save_snapshots(snapshots):
    with open(SNAPSHOT_FILE, "w", encoding="utf-8") as f:
        json.dump(snapshots, f, ensure_ascii=False, indent=2)


def format_duration(seconds):
    try:
        s = int(round(float(seconds)))
        return f"{s // 60}m {s % 60:02d}s"
    except Exception:
        return "0m 00s"


def compute_view_deltas(prev_snaps, views_now, now_ts):
    if not prev_snaps:
        return None, None, 0.0

    snaps_sorted = sorted(prev_snaps, key=lambda x: x["timestamp"])
    oldest_age_hours = max(0.0, (now_ts - snaps_sorted[0]["timestamp"]) / 3600.0)

    snaps_60m_window = [s for s in snaps_sorted if 60 <= (now_ts - s["timestamp"]) <= 4500]
    if snaps_60m_window:
        ref_60m = snaps_60m_window[0]
        delta_60m = max(0, views_now - int(ref_60m["views"]))
    else:
        delta_60m = None

    snaps_within_48h = [s for s in snaps_sorted if 60 <= (now_ts - s["timestamp"]) <= 172800]
    snaps_older_48h = [s for s in snaps_sorted if (now_ts - s["timestamp"]) > 172800]
    if snaps_older_48h:
        ref_48h = snaps_older_48h[-1]
        delta_48h = max(0, views_now - int(ref_48h["views"]))
    elif snaps_within_48h:
        ref_48h = snaps_within_48h[0]
        delta_48h = max(0, views_now - int(ref_48h["views"]))
    else:
        delta_48h = None

    return delta_60m, delta_48h, round(oldest_age_hours, 2)


def fetch_reach_reporting_data(creds, start_7d_str):
    reach_info = {
        "status": "NAO_INICIADO",
        "job_id": None,
        "reports_count": 0,
        "impressions_7d_total": None,
        "ctr_7d_avg": None,
        "by_video": {},
        "message": "",
    }
    try:
        rep = build("youtubereporting", "v1", credentials=creds)
        jobs = rep.jobs().list().execute().get("jobs", [])
        reach_job = next((j for j in jobs if j.get("reportTypeId") == "channel_reach_basic_a1"), None)
        if not reach_job:
            reach_job = rep.jobs().create(
                body={"reportTypeId": "channel_reach_basic_a1", "name": "DarkFactory_Reach_Basic"}
            ).execute()
        job_id = reach_job.get("id")
        reach_info["job_id"] = job_id

        reports = rep.jobs().reports().list(jobId=job_id).execute().get("reports", [])
        reach_info["reports_count"] = len(reports)

        if not reports:
            reach_info["status"] = "AGUARDANDO_PRIMEIRO_CSV"
            reach_info["message"] = f"Job #{job_id[:8]} ativo — Google gerando 1º CSV (24–48h)"
            return reach_info

        by_video = {}
        total_impr = 0
        total_weighted_ctr = 0.0

        reports_sorted = sorted(reports, key=lambda r: r.get("startTime", ""), reverse=True)[:7]
        downloaded_dates = set()

        for rpt in reports_sorted:
            start_time = rpt.get("startTime", "")[:10]
            if start_time in downloaded_dates or start_time < start_7d_str:
                continue
            dl_url = rpt.get("downloadUrl")
            if not dl_url:
                continue

            req = urllib.request.Request(dl_url, headers={"Authorization": f"Bearer {creds.token}"})
            with urllib.request.urlopen(req, timeout=30) as response:
                csv_bytes = response.read()
            if csv_bytes[:2] == b'\x1f\x8b':
                try:
                    csv_bytes = gzip.decompress(csv_bytes)
                except Exception:
                    pass
            downloaded_dates.add(start_time)

            reader = csv.DictReader(io.StringIO(csv_bytes.decode("utf-8", errors="replace")))
            for row in reader:
                vid = row.get("video_id", "").strip()
                if not vid:
                    continue
                impr = int(float(row.get("video_thumbnail_impressions", 0) or 0))
                ctr_raw = float(row.get("video_thumbnail_impressions_ctr", 0.0) or 0.0)
                ctr_pct = ctr_raw * 100.0 if ctr_raw <= 1.0 else ctr_raw

                entry = by_video.setdefault(vid, {"impressions": 0, "weighted_ctr_sum": 0.0, "ctr": 0.0})
                entry["impressions"] += impr
                entry["weighted_ctr_sum"] += impr * ctr_pct

                total_impr += impr
                total_weighted_ctr += impr * ctr_pct

        for vid, entry in by_video.items():
            if entry["impressions"] > 0:
                entry["ctr"] = round(entry["weighted_ctr_sum"] / entry["impressions"], 2)

        reach_info["status"] = "OK"
        reach_info["impressions_7d_total"] = total_impr
        reach_info["ctr_7d_avg"] = round(total_weighted_ctr / total_impr, 2) if total_impr > 0 else 0.0
        reach_info["by_video"] = by_video
        reach_info["message"] = f"{len(downloaded_dates)} dia(s) processados"
        return reach_info
    except Exception as e:
        reach_info["status"] = "ERRO"
        reach_info["message"] = str(e)[:120]
        return reach_info


def collect_channel_data(conf, tokens_bundle, snapshots, now_utc):
    c_data = {
        "id": conf["id"],
        "nome_projeto": conf["nome_projeto"],
        "grupo": conf["grupo"],
        "grupo_slug": conf["grupo_slug"],
        "auth_bat": conf["auth_bat"],
        "status_conexao": "OFFLINE",
        "erro": None,
        "canal_titulo": conf["canal_padrao"],
        "canal_id": conf["expected_channel_id"],
        "handle": conf["handle_padrao"],
        "inscritos": 0,
        "total_videos_publicos": 0,
        "total_videos_agendados": 0,
        "total_views_canal": 0,
        "views_60m_canal": 0,
        "views_48h_canal": 0,
        "snapshot_window_hours": 0.0,
        "views_7d_canal": 0,
        "watch_minutes_7d_canal": 0.0,
        "retention_pct_7d_canal": 0.0,
        "retention_dur_7d_canal": "0m 00s",
        "impressions_7d_canal": None,
        "ctr_7d_canal": None,
        "reach_status": "NAO_INICIADO",
        "reach_message": "",
        "videos_ao_vivo_movimento": [],
        "videos_agendados_fila": [],
        "top3_views_7d": [],
        "top3_retencao_7d": [],
        "top3_ctr_7d": [],
        "top3_impressoes_7d": [],
    }

    creds, err = load_credentials_from_env(conf["id"], tokens_bundle)
    if not creds:
        c_data["status_conexao"] = "PENDENTE_AUTH"
        c_data["erro"] = err
        return c_data

    now_ts = now_utc.timestamp()

    try:
        yt_data = build("youtube", "v3", credentials=creds)
        ch_resp = yt_data.channels().list(part="snippet,statistics,contentDetails", mine=True).execute()
        items = ch_resp.get("items", [])
        if not items:
            c_data["status_conexao"] = "SEM_CANAL"
            c_data["erro"] = "Nenhum canal encontrado."
            return c_data

        ch = items[0]
        actual_ch_id = ch.get("id")
        if conf.get("expected_channel_id") and actual_ch_id != conf["expected_channel_id"]:
            c_data["status_conexao"] = "CANAL_TROCADO"
            c_data["erro"] = f"Token conectado ao canal '{ch['snippet'].get('title')}'."
            return c_data

        c_data["status_conexao"] = "ONLINE"
        c_data["canal_titulo"] = ch["snippet"].get("title", conf["canal_padrao"])
        c_data["canal_id"] = actual_ch_id
        c_data["handle"] = ch["snippet"].get("customUrl", conf["handle_padrao"])
        stats = ch.get("statistics", {})
        c_data["inscritos"] = int(stats.get("subscriberCount", 0))
        c_data["total_videos_publicos"] = int(stats.get("videoCount", 0))
        c_data["total_views_canal"] = int(stats.get("viewCount", 0))

        uploads_pl = ch["contentDetails"]["relatedPlaylists"]["uploads"]
        pl_resp = yt_data.playlistItems().list(playlistId=uploads_pl, part="snippet,contentDetails", maxResults=50).execute()
        pl_items = pl_resp.get("items", [])
        video_ids = [item["contentDetails"]["videoId"] for item in pl_items]

        video_meta_map = {}
        max_window_h = 0.0

        if video_ids:
            v_resp = yt_data.videos().list(
                id=",".join(video_ids[:50]),
                part="snippet,statistics,status,contentDetails"
            ).execute()

            for v_item in v_resp.get("items", []):
                vid = v_item["id"]
                s = v_item["snippet"]
                st = v_item.get("statistics", {})
                status_obj = v_item.get("status", {})

                privacy = status_obj.get("privacyStatus", "public")
                publish_at_str = status_obj.get("publishAt")
                pub_str = publish_at_str or s.get("publishedAt", "")

                pub_dt = None
                try:
                    pub_dt = datetime.fromisoformat(pub_str.replace("Z", "+00:00"))
                except Exception:
                    pass

                is_scheduled = (privacy == "private" and publish_at_str is not None)
                is_public = (privacy == "public")

                views_now = int(st.get("viewCount", 0))
                likes_now = int(st.get("likeCount", 0))
                comments_now = int(st.get("commentCount", 0))

                prev_snaps = snapshots.get(vid, [])
                delta_60m, delta_48h, window_h = compute_view_deltas(prev_snaps, views_now, now_ts)
                if window_h > max_window_h:
                    max_window_h = window_h

                if not prev_snaps or (now_ts - prev_snaps[-1]["timestamp"]) >= 300 or prev_snaps[-1]["views"] != views_now:
                    prev_snaps.append({"timestamp": now_ts, "views": views_now})
                prev_snaps = [sn for sn in prev_snaps if (now_ts - sn["timestamp"]) <= 7 * 86400]
                snapshots[vid] = prev_snaps

                is_pub_last_48h = False
                if is_public and pub_dt:
                    age_h = (now_utc - pub_dt).total_seconds() / 3600.0
                    if 0 <= age_h <= 48.0:
                        is_pub_last_48h = True

                thumb_url = (
                    s.get("thumbnails", {}).get("medium", {}).get("url")
                    or s.get("thumbnails", {}).get("default", {}).get("url", "")
                )

                v_entry = {
                    "video_id": vid,
                    "canal_titulo": c_data["canal_titulo"],
                    "canal_handle": c_data["handle"],
                    "grupo": c_data["grupo"],
                    "grupo_slug": c_data["grupo_slug"],
                    "title": s.get("title", ""),
                    "privacy": privacy,
                    "is_scheduled": is_scheduled,
                    "is_public": is_public,
                    "published_at": pub_str,
                    "published_formatted": pub_dt.astimezone(timezone(timedelta(hours=-3))).strftime("%d/%m %H:%M") if pub_dt else pub_str[:10],
                    "thumbnail": thumb_url,
                    "views_total": views_now,
                    "likes": likes_now,
                    "comments": comments_now,
                    "url": f"https://youtu.be/{vid}",
                    "is_pub_last_48h": is_pub_last_48h,
                    "delta_60m": delta_60m,
                    "delta_48h": delta_48h,
                    "window_h": window_h,
                }
                video_meta_map[vid] = v_entry

                if is_scheduled:
                    c_data["videos_agendados_fila"].append(v_entry)

                c_data["views_60m_canal"] += (delta_60m or 0)
                c_data["views_48h_canal"] += (delta_48h or 0)

        c_data["total_videos_agendados"] = len(c_data["videos_agendados_fila"])
        c_data["snapshot_window_hours"] = max_window_h
    except Exception as e:
        c_data["status_conexao"] = "ERRO_DATA_API"
        c_data["erro"] = str(e)
        return c_data

    today = now_utc.date()
    start_7d_str = (today - timedelta(days=7)).isoformat()
    end_d_str = today.isoformat()

    reach_info = fetch_reach_reporting_data(creds, start_7d_str)
    c_data["reach_status"] = reach_info["status"]
    c_data["reach_message"] = reach_info["message"]
    c_data["impressions_7d_canal"] = reach_info["impressions_7d_total"]
    c_data["ctr_7d_canal"] = reach_info["ctr_7d_avg"]

    try:
        yt_ana = build("youtubeAnalytics", "v2", credentials=creds)
        ch_ovr = yt_ana.reports().query(
            ids="channel==MINE",
            startDate=start_7d_str,
            endDate=end_d_str,
            metrics="views,estimatedMinutesWatched,averageViewDuration,averageViewPercentage"
        ).execute()
        ovr_rows = ch_ovr.get("rows", [])
        if ovr_rows and ovr_rows[0][0] > 0:
            c_data["views_7d_canal"] = int(ovr_rows[0][0])
            c_data["watch_minutes_7d_canal"] = round(float(ovr_rows[0][1]), 1)
            c_data["retention_dur_7d_canal"] = format_duration(ovr_rows[0][2])
            c_data["retention_pct_7d_canal"] = round(float(ovr_rows[0][3]), 2)

        ana_res_7d = yt_ana.reports().query(
            ids="channel==MINE",
            startDate=start_7d_str,
            endDate=end_d_str,
            metrics="views,estimatedMinutesWatched,averageViewDuration,averageViewPercentage,likes",
            dimensions="video",
            sort="-views",
            maxResults=50
        ).execute()

        rows_7d = ana_res_7d.get("rows", [])
        parsed_7d = []

        missing_ids = [str(r[0]) for r in rows_7d if str(r[0]) not in video_meta_map]
        if missing_ids:
            try:
                extra_resp = yt_data.videos().list(id=",".join(missing_ids[:50]), part="snippet,statistics").execute()
                for ex in extra_resp.get("items", []):
                    vid = ex["id"]
                    s = ex["snippet"]
                    st = ex.get("statistics", {})
                    video_meta_map[vid] = {
                        "video_id": vid,
                        "canal_titulo": c_data["canal_titulo"],
                        "canal_handle": c_data["handle"],
                        "grupo": c_data["grupo"],
                        "grupo_slug": c_data["grupo_slug"],
                        "title": s.get("title", f"Vídeo {vid}"),
                        "privacy": "public",
                        "is_scheduled": False,
                        "is_public": True,
                        "published_formatted": s.get("publishedAt", "")[:10],
                        "thumbnail": s.get("thumbnails", {}).get("medium", {}).get("url", ""),
                        "views_total": int(st.get("viewCount", 0)),
                        "likes": int(st.get("likeCount", 0)),
                        "url": f"https://youtu.be/{vid}",
                        "is_pub_last_48h": False,
                        "delta_60m": None,
                        "delta_48h": None,
                        "window_h": 0.0,
                    }
            except Exception:
                pass

        for r in rows_7d:
            v_id = str(r[0])
            v_views = int(r[1])
            v_watch_min = round(float(r[2]), 1)
            v_dur_s = float(r[3])
            v_ret_pct = round(float(r[4]), 2)
            v_likes = int(r[5]) if len(r) > 5 else 0
            if v_views <= 0:
                continue

            meta = video_meta_map.get(v_id, {})
            reach_v = reach_info["by_video"].get(v_id, {})
            parsed_7d.append({
                "video_id": v_id,
                "title": meta.get("title") or f"Vídeo {v_id}",
                "thumbnail": meta.get("thumbnail") or "",
                "url": meta.get("url") or f"https://youtu.be/{v_id}",
                "views_7d": v_views,
                "watch_minutes_7d": v_watch_min,
                "duration_seconds": v_dur_s,
                "duration_str": format_duration(v_dur_s),
                "retention_pct": v_ret_pct,
                "likes_7d": v_likes,
                "impressions_7d": reach_v.get("impressions"),
                "ctr_7d": reach_v.get("ctr"),
                "low_sample": v_views < MIN_VIEWS_FOR_RETENTION_RANK,
            })

        c_data["top3_views_7d"] = sorted(parsed_7d, key=lambda x: x["views_7d"], reverse=True)[:3]

        qual_ret = [x for x in parsed_7d if not x["low_sample"]]
        low_ret = [x for x in parsed_7d if x["low_sample"]]
        qual_ret.sort(key=lambda x: (x["retention_pct"], x["views_7d"]), reverse=True)
        low_ret.sort(key=lambda x: (x["retention_pct"], x["views_7d"]), reverse=True)
        c_data["top3_retencao_7d"] = (qual_ret + low_ret)[:3]

        if reach_info["status"] == "OK" and reach_info["by_video"]:
            reach_items = []
            for v_id, r_vals in reach_info["by_video"].items():
                meta = video_meta_map.get(v_id, {})
                impr = r_vals["impressions"]
                ctr = r_vals["ctr"]
                if impr <= 0:
                    continue
                reach_items.append({
                    "video_id": v_id,
                    "title": meta.get("title") or f"Vídeo {v_id}",
                    "url": meta.get("url") or f"https://youtu.be/{v_id}",
                    "impressions_7d": impr,
                    "ctr_7d": ctr,
                    "low_sample": impr < MIN_IMPRESSIONS_FOR_CTR_RANK,
                })
            c_data["top3_impressoes_7d"] = sorted(reach_items, key=lambda x: x["impressions_7d"], reverse=True)[:3]
            qual_ctr = [x for x in reach_items if not x["low_sample"]]
            low_ctr = [x for x in reach_items if x["low_sample"]]
            qual_ctr.sort(key=lambda x: (x["ctr_7d"], x["impressions_7d"]), reverse=True)
            low_ctr.sort(key=lambda x: (x["ctr_7d"], x["impressions_7d"]), reverse=True)
            c_data["top3_ctr_7d"] = (qual_ctr + low_ctr)[:3]
    except Exception as e:
        c_data["erro"] = f"Analytics: {e}"

    for v_entry in video_meta_map.values():
        if not v_entry["is_public"]:
            continue
        d60 = v_entry["delta_60m"] or 0
        d48 = v_entry["delta_48h"] or 0
        if d60 > 0 or d48 > 0 or (v_entry["is_pub_last_48h"] and v_entry["views_total"] > 0):
            c_data["videos_ao_vivo_movimento"].append(v_entry)

    c_data["videos_ao_vivo_movimento"].sort(
        key=lambda x: (x["delta_60m"] or 0, x["delta_48h"] or 0, x["views_total"]),
        reverse=True,
    )
    return c_data


# Importar o gerador de HTML idêntico
def render_html(channels_data, generated_at):
    now_brt = generated_at.astimezone(timezone(timedelta(hours=-3)))
    now_str = now_brt.strftime("%d/%m/%Y às %H:%M:%S (BRT)")
    online_count = sum(1 for c in channels_data if c["status_conexao"] == "ONLINE")
    total_canais = len(channels_data)
    max_snap_window = max((c["snapshot_window_hours"] for c in channels_data), default=0.0)

    all_live_videos = [v for c in channels_data for v in c["videos_ao_vivo_movimento"]]
    all_live_videos.sort(key=lambda x: (x["delta_60m"] or 0, x["delta_48h"] or 0, x["views_total"]), reverse=True)

    live_rows_html = ""
    if all_live_videos:
        for v in all_live_videos[:25]:
            badge_48h_pub = '<span class="pill pill-amber">Postado &lt;48h</span>' if v["is_pub_last_48h"] else ""
            if v["delta_60m"] is None:
                d60_html = '<span class="tiny-note">⏳ ciclo 30m</span>'
                d60_cls = "val-zero"
            else:
                d60_html = f"+{v['delta_60m']:,}"
                d60_cls = "val-positive" if v["delta_60m"] > 0 else "val-zero"
            eff_48h = v["delta_48h"] or 0
            d48_cls = "val-positive" if eff_48h > 0 else "val-zero"
            win_h = v.get("window_h", 0.0)
            live_rows_html += f"""
            <tr data-grupo="{v['grupo_slug']}">
                <td><span class="channel-tag">{v['canal_titulo']}</span><div class="sub-text">{v['canal_handle']}</div></td>
                <td><div class="video-cell"><img src="{v['thumbnail']}" class="thumb-sm" alt=""><div><a href="{v['url']}" target="_blank" class="v-link">{v['title']}</a><div class="sub-text">Publicado: {v['published_formatted']} {badge_48h_pub}</div></div></div></td>
                <td class="num {d60_cls}">{d60_html}</td>
                <td class="num {d48_cls}">+{eff_48h:,} <span class="tiny-note">({win_h:.1f}h medidos)</span></td>
                <td class="num"><b>{v['views_total']:,}</b></td>
            </tr>"""
    else:
        live_rows_html = '<tr><td colspan="5" class="empty-box">Nenhum vídeo registrou novas views nos snapshots recentes ainda.</td></tr>'

    comp_rows_html = ""
    for c in channels_data:
        st_html = '<span class="status-dot dot-green"></span>Conectado' if c["status_conexao"] == "ONLINE" else f'<span class="status-dot dot-red"></span>{c["status_conexao"]}'
        impr_html = f"{c['impressions_7d_canal']:,}" if c["impressions_7d_canal"] is not None else f'<span class="pending-tag" title="{c["reach_message"]}">⏳ Gerando 1º CSV (24-48h)</span>'
        ctr_html = f"<b>{c['ctr_7d_canal']:.2f}%</b>" if c["ctr_7d_canal"] is not None else '<span class="pending-tag">⏳ Aguardando CSV</span>'
        ret_html = f"<b>{c['retention_pct_7d_canal']:.1f}%</b> <span class='sub-text'>({c['retention_dur_7d_canal']})</span>" if c["views_7d_canal"] > 0 else '<span class="sub-text">—</span>'
        agendados_pill = f'<span class="pill pill-blue">{c["total_videos_agendados"]} agendados</span>' if c["total_videos_agendados"] > 0 else '<span class="sub-text">0 agendados</span>'
        comp_rows_html += f"""
        <tr data-grupo="{c['grupo_slug']}">
            <td><div class="ch-name">{c['canal_titulo']}</div><div class="sub-text">{c['handle']} • {c['nome_projeto']}</div></td>
            <td><span class="pill pill-group-{c['grupo_slug']}">{c['grupo']}</span></td>
            <td>{st_html}</td>
            <td class="num">{c['inscritos']:,}</td>
            <td class="num">{c['total_videos_publicos']} públ. / {agendados_pill}</td>
            <td class="num">+{c['views_60m_canal']:,} / +{c['views_48h_canal']:,}</td>
            <td class="num"><b>{c['views_7d_canal']:,}</b></td>
            <td class="num">{impr_html}</td>
            <td class="num">{ctr_html}</td>
            <td class="num">{ret_html}</td>
            <td class="num">{c['total_views_canal']:,}</td>
        </tr>"""

    cards_html = ""
    medals = ["🥇", "🥈", "🥉"]
    for c in channels_data:
        if c["status_conexao"] != "ONLINE":
            cards_html += f"""
            <div class="ch-card ch-offline" data-grupo="{c['grupo_slug']}">
                <div class="ch-card-head"><div><span class="pill pill-group-{c['grupo_slug']}">{c['grupo']}</span><h3>{c['canal_titulo']} <small>({c['nome_projeto']})</small></h3></div><span class="pill pill-red">🔴 DESCONECTADO</span></div>
                <div class="offline-msg"><p><b>Motivo:</b> {c['erro']}</p></div>
            </div>"""
            continue

        ret_list_html = "".join(
            f'<div class="rank-row"><span class="medal">{medals[i]}</span><div class="rank-info"><a href="{item["url"]}" target="_blank" class="rank-title">{item["title"]}</a><div class="rank-metrics"><span class="m-hi">{item["retention_pct"]:.1f}%</span> ({item["duration_str"]}) ' + (f'<span class="warn-sample">⚠️ {item["views_7d"]}v</span>' if item["low_sample"] else f'<span class="ok-sample">({item["views_7d"]:,} views)</span>') + '</div></div></div>'
            for i, item in enumerate(c["top3_retencao_7d"])
        ) or '<div class="empty-mini">Sem views consolidadas nos últimos 7 dias.</div>'

        vws_list_html = "".join(
            f'<div class="rank-row"><span class="medal">{medals[i]}</span><div class="rank-info"><a href="{item["url"]}" target="_blank" class="rank-title">{item["title"]}</a><div class="rank-metrics"><span class="m-hi">{item["views_7d"]:,} views</span> • {item["watch_minutes_7d"]} min • Ret: {item["retention_pct"]:.1f}%</div></div></div>'
            for i, item in enumerate(c["top3_views_7d"])
        ) or '<div class="empty-mini">Sem views nos últimos 7 dias.</div>'

        ctr_list_html = "".join(
            f'<div class="rank-row"><span class="medal">{medals[i]}</span><div class="rank-info"><a href="{item["url"]}" target="_blank" class="rank-title">{item["title"]}</a><div class="rank-metrics"><span class="m-hi">{item["ctr_7d"]:.2f}% CTR</span> • {item["impressions_7d"]:,} impressões</div></div></div>'
            for i, item in enumerate(c["top3_ctr_7d"])
        ) or f'<div class="empty-mini">⏳ {c["reach_message"]}</div>'

        imp_list_html = "".join(
            f'<div class="rank-row"><span class="medal">{medals[i]}</span><div class="rank-info"><a href="{item["url"]}" target="_blank" class="rank-title">{item["title"]}</a><div class="rank-metrics"><span class="m-hi">{item["impressions_7d"]:,} imp.</span> • CTR: {item["ctr_7d"]:.2f}%</div></div></div>'
            for i, item in enumerate(c["top3_impressoes_7d"])
        ) or f'<div class="empty-mini">⏳ {c["reach_message"]}</div>'

        cards_html += f"""
        <div class="ch-card" data-grupo="{c['grupo_slug']}">
            <div class="ch-card-head">
                <div><span class="pill pill-group-{c['grupo_slug']}">{c['grupo']}</span><h3>{c['canal_titulo']} <small>{c['handle']} • {c['nome_projeto']}</small></h3></div>
                <div class="ch-head-stats"><span>👥 <b>{c['inscritos']:,}</b> insc.</span><span>🎬 <b>{c['total_videos_publicos']}</b> públ. ({c['total_videos_agendados']} agend.)</span><span>👁️ <b>{c['views_7d_canal']:,}</b> views (7d)</span></div>
            </div>
            <div class="top3-grid">
                <div class="top3-box"><h4>🎯 Top 3 Maior Retenção (7d)</h4>{ret_list_html}</div>
                <div class="top3-box"><h4>👁️ Top 3 Mais Views (7d)</h4>{vws_list_html}</div>
                <div class="top3-box"><h4>🖱️ Top 3 Maior CTR (7d)</h4>{ctr_list_html}</div>
                <div class="top3-box"><h4>📢 Top 3 Mais Impressões (7d)</h4>{imp_list_html}</div>
            </div>
        </div>"""

    # Reutilizar o mesmo template CSS do index.html atual
    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Painel Master Analytics — 7 Canais</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;600;700&display=swap" rel="stylesheet">
    <style>
        :root {{ --bg: #090D16; --surface: #111827; --surface-2: #1E293B; --border: rgba(255,255,255,0.09); --text: #F8FAFC; --muted: #94A3B8; --cyan: #38BDF8; --green: #10B981; --amber: #F59E0B; --red: #F43F5E; --purple: #A855F7; }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{ background: var(--bg); color: var(--text); font-family: 'Inter', sans-serif; padding: 20px; line-height: 1.4; }}
        .wrap {{ max-width: 1480px; margin: 0 auto; }}
        .topbar {{ display: flex; justify-content: space-between; align-items: center; background: var(--surface); border: 1px solid var(--border); border-radius: 12px; padding: 16px 22px; margin-bottom: 18px; flex-wrap: wrap; gap: 14px; }}
        .topbar h1 {{ font-size: 20px; font-weight: 800; color: #FFF; }}
        .topbar .meta {{ font-size: 12px; color: var(--muted); margin-top: 3px; }}
        .filter-btns {{ display: flex; gap: 8px; }}
        .filter-btn {{ background: var(--surface-2); color: var(--text); border: 1px solid var(--border); padding: 7px 14px; border-radius: 8px; font-size: 12px; font-weight: 600; cursor: pointer; }}
        .filter-btn.active {{ background: var(--cyan); color: #090D16; border-color: var(--cyan); }}
        .sec-box {{ background: var(--surface); border: 1px solid var(--border); border-radius: 12px; padding: 18px 20px; margin-bottom: 20px; }}
        .sec-head {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; flex-wrap: wrap; gap: 8px; }}
        .sec-head h2 {{ font-size: 16px; font-weight: 700; }}
        .sec-head .hint {{ font-size: 12px; color: var(--muted); }}
        .tbl-wrap {{ overflow-x: auto; }}
        table {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
        th {{ text-align: left; font-size: 11px; text-transform: uppercase; color: var(--muted); padding: 9px 10px; border-bottom: 1px solid var(--border); white-space: nowrap; }}
        td {{ padding: 9px 10px; border-bottom: 1px solid rgba(255,255,255,0.04); vertical-align: middle; }}
        tr:hover td {{ background: rgba(255,255,255,0.02); }}
        .num {{ text-align: right; font-family: 'JetBrains Mono', monospace; white-space: nowrap; }}
        .val-positive {{ color: var(--green); font-weight: 700; }}
        .val-zero {{ color: var(--muted); }}
        .tiny-note {{ font-size: 10px; color: var(--muted); font-weight: 400; }}
        .video-cell {{ display: flex; align-items: center; gap: 10px; }}
        .thumb-sm {{ width: 52px; height: 30px; object-fit: cover; border-radius: 4px; border: 1px solid var(--border); }}
        .v-link {{ color: var(--text); text-decoration: none; font-weight: 500; }}
        .v-link:hover {{ color: var(--cyan); text-decoration: underline; }}
        .sub-text {{ font-size: 11px; color: var(--muted); }}
        .channel-tag {{ font-weight: 700; color: #FFF; font-size: 12px; }}
        .pill {{ display: inline-block; font-size: 10px; font-weight: 700; padding: 2px 8px; border-radius: 99px; text-transform: uppercase; }}
        .pill-group-pessoal {{ background: rgba(56,189,248,0.15); color: var(--cyan); }}
        .pill-group-gvg {{ background: rgba(168,85,247,0.18); color: #C084FC; }}
        .pill-amber {{ background: rgba(245,158,11,0.2); color: #FBBF24; }}
        .pill-blue {{ background: rgba(56,189,248,0.15); color: var(--cyan); }}
        .pill-red {{ background: rgba(244,63,94,0.2); color: var(--red); }}
        .status-dot {{ display: inline-block; width: 8px; height: 8px; border-radius: 50%; margin-right: 6px; }}
        .dot-green {{ background: var(--green); }}
        .dot-red {{ background: var(--red); }}
        .pending-tag {{ font-size: 11px; color: var(--amber); font-family: 'Inter', sans-serif; }}
        .ch-card {{ background: var(--surface); border: 1px solid var(--border); border-radius: 12px; padding: 16px 18px; margin-bottom: 16px; }}
        .ch-offline {{ border-color: rgba(244,63,94,0.4); }}
        .ch-card-head {{ display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--border); padding-bottom: 10px; margin-bottom: 12px; flex-wrap: wrap; gap: 10px; }}
        .ch-card-head h3 {{ font-size: 16px; font-weight: 700; margin-top: 4px; }}
        .ch-card-head h3 small {{ font-size: 12px; color: var(--muted); font-weight: 400; margin-left: 6px; }}
        .ch-head-stats {{ display: flex; gap: 16px; font-size: 12px; color: var(--muted); }}
        .ch-head-stats b {{ color: var(--text); font-family: 'JetBrains Mono', monospace; }}
        .top3-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; }}
        .top3-box {{ background: rgba(15, 23, 42, 0.65); border: 1px solid var(--border); border-radius: 8px; padding: 12px; }}
        .top3-box h4 {{ font-size: 12px; font-weight: 700; color: #E2E8F0; margin-bottom: 10px; padding-bottom: 6px; border-bottom: 1px solid var(--border); }}
        .rank-row {{ display: flex; gap: 8px; padding: 6px 0; border-bottom: 1px solid rgba(255,255,255,0.03); }}
        .rank-row:last-child {{ border-bottom: none; }}
        .medal {{ font-size: 15px; line-height: 1.2; }}
        .rank-info {{ flex: 1; min-width: 0; }}
        .rank-title {{ display: block; font-size: 12px; color: var(--text); text-decoration: none; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; font-weight: 500; }}
        .rank-title:hover {{ color: var(--cyan); text-decoration: underline; }}
        .rank-metrics {{ font-size: 11px; color: var(--muted); margin-top: 2px; }}
        .m-hi {{ color: var(--cyan); font-weight: 700; font-family: 'JetBrains Mono', monospace; }}
        .warn-sample {{ color: var(--amber); font-size: 10px; font-weight: 600; }}
        .ok-sample {{ color: var(--muted); font-size: 10px; }}
        .empty-mini {{ font-size: 11px; color: var(--muted); font-style: italic; padding: 8px 0; }}
        .empty-box {{ text-align: center; color: var(--muted); padding: 18px; font-style: italic; }}
        @media (max-width: 1200px) {{ .top3-grid {{ grid-template-columns: repeat(2, 1fr); }} }}
        @media (max-width: 700px) {{ .top3-grid {{ grid-template-columns: 1fr; }} }}
    </style>
</head>
<body>
    <div class="wrap">
        <div class="topbar">
            <div>
                <h1>📊 Painel Master Analytics — 7 Canais Dark</h1>
                <div class="meta">
                    Atualizado em: <b>{now_str}</b> • Canais Online: <b>{online_count}/{total_canais}</b> •
                    Janela de Snapshots acumulada: <b>{max_snap_window:.1f}h</b> (atualização 100% na nuvem via GitHub Actions a cada 30 min)
                </div>
            </div>
            <div class="filter-btns">
                <button class="filter-btn active" id="btn-all" onclick="filterGroup('all', this)">Todos (7)</button>
                <button class="filter-btn" id="btn-pessoal" onclick="filterGroup('pessoal', this)">Meus Pessoais (5)</button>
                <button class="filter-btn" id="btn-gvg" onclick="filterGroup('gvg', this)">Startup GVG (2)</button>
            </div>
        </div>
        <div class="sec-box">
            <div class="sec-head">
                <h2>🔥 1. Vídeos com Views nas Últimas 48h e 60 Minutos (Todos os Canais)</h2>
                <div class="hint">Exibe apenas vídeos públicos que ganharam views reais nos últimos 60 min / 48h.</div>
            </div>
            <div class="tbl-wrap">
                <table>
                    <thead><tr><th style="width:170px;">Canal</th><th>Vídeo (Apenas Públicos com Views Recentes)</th><th class="num" style="width:120px;">Views (60 min)</th><th class="num" style="width:160px;">Views (48h)</th><th class="num" style="width:120px;">Views Totais</th></tr></thead>
                    <tbody>{live_rows_html}</tbody>
                </table>
            </div>
        </div>
        <div class="sec-box">
            <div class="sec-head">
                <h2>📋 2. Comparativo Lado a Lado dos 7 Canais (Últimos 7 Dias)</h2>
                <div class="hint">Métricas estritas dos últimos 7 dias via YouTube Analytics API v2 + YouTube Reporting API v1.</div>
            </div>
            <div class="tbl-wrap">
                <table>
                    <thead><tr><th>Canal</th><th>Grupo</th><th>Status</th><th class="num">Inscritos</th><th class="num">Vídeos (Públ. / Agend.)</th><th class="num">Views 60m / 48h</th><th class="num">Views (7d)</th><th class="num">Impressões (7d)</th><th class="num">CTR Médio (7d)</th><th class="num">Retenção Média (7d)</th><th class="num">Views Totais</th></tr></thead>
                    <tbody>{comp_rows_html}</tbody>
                </table>
            </div>
        </div>
        <div class="sec-head" style="margin: 12px 4px;">
            <h2>🏆 3. Top 3 de Cada Canal nos Últimos 7 Dias (Retenção, Views, CTR e Impressões)</h2>
            <div class="hint">Retenção prioriza vídeos com ≥{MIN_VIEWS_FOR_RETENTION_RANK} views nos últimos 7d.</div>
        </div>
        {cards_html}
    </div>
    <script>
        function filterGroup(group, btn) {{
            document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
            if (btn) btn.classList.add('active');
            document.querySelectorAll('[data-grupo]').forEach(el => {{
                el.style.display = (group === 'all' || el.getAttribute('data-grupo') === group) ? '' : 'none';
            }});
        }}
        window.addEventListener('DOMContentLoaded', () => {{
            const g = new URLSearchParams(window.location.search).get('grupo');
            if (g === 'gvg' || g === 'pessoal') filterGroup(g, document.getElementById('btn-' + g));
        }});
    </script>
</body>
</html>"""


def main():
    raw_secret = os.environ.get("CHANNELS_TOKENS_JSON", "").strip()
    if not raw_secret:
        print("❌ Variável CHANNELS_TOKENS_JSON não encontrada no ambiente.")
        sys.exit(1)

    tokens_bundle = json.loads(raw_secret)
    now_utc = datetime.now(timezone.utc)
    snapshots = load_snapshots()
    results = []

    for conf in CHANNELS_CONFIG:
        c_res = collect_channel_data(conf, tokens_bundle, snapshots, now_utc)
        results.append(c_res)
        print(f" • [{c_res['status_conexao']}] {c_res['canal_titulo']}: Views 7d={c_res['views_7d_canal']}")

    save_snapshots(snapshots)
    html_out = render_html(results, now_utc)
    HTML_OUTPUT.write_text(html_out, encoding="utf-8")
    print("✅ index.html e snapshots atualizados com sucesso na nuvem!")


if __name__ == "__main__":
    main()
