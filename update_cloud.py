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
HISTORY_FILE = REPO_DIR / "analytics_history_30d.json"

MIN_VIEWS_FOR_RETENTION_RANK = 10
MIN_IMPRESSIONS_FOR_CTR_RANK = 20

TRAFFIC_SOURCE_LABELS = {
    "SHORTS": "Feed do Shorts",
    "RELATED_VIDEO": "Vídeos Sugeridos",
    "YT_SEARCH": "Pesquisa do YouTube",
    "SUBSCRIBER": "Feed de Inscrições",
    "YT_OTHER_PAGE": "Navegação / Início",
    "NO_LINK_OTHER": "Direto / Desconhecido",
    "EXT_URL": "Sites Externos",
    "PLAYLIST": "Playlists",
    "YT_CHANNEL": "Página do Canal",
    "NOTIFICATION": "Notificações",
    "END_SCREEN": "Telas Finais",
    "CARD": "Cards Interativos",
}
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

    snaps_60m_window = [s for s in snaps_sorted if 60 <= (now_ts - s["timestamp"]) <= 5400]
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
        "vph_60m": 0,
        "vph_48h": 0.0,
        "history_lifetime": [],
        "traffic_sources_lifetime": [],
        "history_30d": [],
        "traffic_sources_30d": [],
        "rank_1_de_10": None,
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

        # 5. Histórico Completo desde o início (com separação de Shorts vs Vídeos)
        c_data["history_lifetime"] = []
        try:
            rep_d = yt_ana.reports().query(
                ids="channel==MINE",
                startDate="2020-01-01",
                endDate=end_d_str,
                metrics="views,estimatedMinutesWatched,subscribersGained,subscribersLost",
                dimensions="day,creatorContentType",
                sort="day"
            ).execute()
            for row in rep_d.get("rows", []):
                day_str, c_type, vws, mins, sub_g, sub_l = row
                fmt_type = "shorts" if str(c_type).lower() == "shorts" else "video"
                entry = {
                    "day": day_str,
                    "type": fmt_type,
                    "views": int(vws),
                    "minutes": round(float(mins), 1),
                    "net_subs": int(sub_g - sub_l),
                }
                c_data["history_lifetime"].append(entry)
                # Mantém history_30d retrocompatível
                if day_str >= (today - timedelta(days=30)).isoformat():
                    c_data["history_30d"].append({
                        "day": day_str,
                        "views": int(vws),
                        "minutes": round(float(mins), 1),
                        "net_subs": int(sub_g - sub_l),
                    })
        except Exception:
            pass

        # 6. Origens do Tráfego Detalhadas (por dia e por formato: Shorts vs Vídeos)
        c_data["traffic_sources_lifetime"] = []
        try:
            rep_tr = yt_ana.reports().query(
                ids="channel==MINE",
                startDate="2020-01-01",
                endDate=end_d_str,
                metrics="views",
                dimensions="day,insightTrafficSourceType,creatorContentType",
                sort="day"
            ).execute()
            for row in rep_tr.get("rows", []):
                day_str, src, c_type, vws = row
                if int(vws) <= 0:
                    continue
                fmt_type = "shorts" if str(c_type).lower() == "shorts" else "video"
                item = {
                    "day": day_str,
                    "source": src,
                    "label": TRAFFIC_SOURCE_LABELS.get(src, src),
                    "type": fmt_type,
                    "views": int(vws),
                }
                c_data["traffic_sources_lifetime"].append(item)
        except Exception:
            pass

    except Exception as e:
        c_data["erro"] = f"Analytics: {e}"

    # 7. Cálculo Desempenho '1 de 10' (Último Lançamento vs 10 Anteriores)
    public_vids = [v for v in video_meta_map.values() if v.get("is_public") and v.get("published_at")]
    public_vids.sort(key=lambda x: x.get("published_at", ""), reverse=True)
    if public_vids:
        latest_vid = public_vids[0]
        sample_10 = public_vids[:10]
        by_views = sorted(sample_10, key=lambda x: x["views_total"], reverse=True)
        rank_pos = by_views.index(latest_vid) + 1
        other_views = [x["views_total"] for x in sample_10 if x["video_id"] != latest_vid["video_id"]]
        avg_prev = (sum(other_views) / len(other_views)) if other_views else latest_vid["views_total"]
        diff_pct = round(((latest_vid["views_total"] - avg_prev) / max(1, avg_prev)) * 100, 1)
        c_data["rank_1_de_10"] = {
            "video_id": latest_vid["video_id"],
            "title": latest_vid["title"],
            "url": latest_vid["url"],
            "thumbnail": latest_vid["thumbnail"],
            "views": latest_vid["views_total"],
            "published_formatted": latest_vid.get("published_formatted", ""),
            "rank": rank_pos,
            "out_of": len(sample_10),
            "diff_pct": diff_pct,
            "avg_prev": round(avg_prev),
        }

    # 8. Velocímetro de Views por Hora (VPH)
    c_data["vph_60m"] = c_data["views_60m_canal"]
    c_data["vph_48h"] = round(c_data["views_48h_canal"] / max(1.0, c_data["snapshot_window_hours"]), 1)

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


from painel_template import render_html  # noqa: E402


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

    all_scheduled = []
    for c in results:
        for sv in c.get("videos_agendados_fila", []):
            all_scheduled.append(sv)
    all_scheduled.sort(key=lambda x: x.get("published_at", ""))

    hist_payload = {
        "updated_at_utc": now_utc.isoformat(),
        "channels": {
            c["id"]: {
                "title": c.get("canal_titulo"),
                "handle": c.get("handle"),
                "group": c.get("grupo"),
                "group_slug": c.get("grupo_slug"),
                "vph_60m": c.get("vph_60m", 0),
                "vph_48h": c.get("vph_48h", 0.0),
                "history_lifetime": c.get("history_lifetime", []),
                "traffic_sources_lifetime": c.get("traffic_sources_lifetime", []),
                "history_30d": c.get("history_30d", []),
                "traffic_sources_30d": c.get("traffic_sources_30d", []),
                "rank_1_de_10": c.get("rank_1_de_10"),
            }
            for c in results
        }
    }
    HISTORY_FILE.write_text(json.dumps(hist_payload, ensure_ascii=False, indent=2), encoding="utf-8")

    save_snapshots(snapshots)
    html_out = render_html(results, now_utc, all_scheduled)
    HTML_OUTPUT.write_text(html_out, encoding="utf-8")
    print("✅ index.html, snapshots e histórico 30d atualizados com sucesso na nuvem!")


if __name__ == "__main__":
    main()
