"""
TETR.IO AI Coach — 리플레이 분석 + 자체 AI 코칭 엔진
사용법: python tetrio_coach.py
"""

import json
import re
import os
import sys
import platform
import threading
import uuid
import urllib.error
import urllib.parse
import urllib.request
import unicodedata
import html
import webbrowser
from datetime import datetime
from pathlib import Path

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext

# ── 외부 의존성 라이브러리 체크 ──────────────────────────────────────────
MATPLOTLIB_AVAILABLE = True
try:
    import matplotlib
    matplotlib.use("TkAgg")
    import matplotlib.font_manager as fm
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    from matplotlib.figure import Figure
except Exception:
    MATPLOTLIB_AVAILABLE = False
    matplotlib = None
    fm = None
    FigureCanvasTkAgg = None
    Figure = object
    print("matplotlib를 불러올 수 없어 그래프는 비활성화됩니다. 텍스트/로드맵 분석은 계속 가능합니다.")

from i18n import t, init as i18n_init, set_language, get_language, SUPPORTED_LANGS, LANG_NAMES

# ── 설정 상수 ─────────────────────────────────────────────────
WINDOW_SIZE     = "1250x850"
WINDOW_MIN      = (950, 700)
SIDEBAR_WIDTH   = 300
COACH_ROUNDS    = 12
TETRIO_API_BASE = "https://ch.tetr.io/api"
SITE_PAGE_LIMIT = 100
API_TIMEOUT     = 20
_API_SESSION_ID = uuid.uuid4().hex
REPORT_DIR      = Path.home() / ".tetrio_coach_reports"

# ── 색상 팔레트 ───────────────────────────────────────────────
C = {
    "bg":      "#0d0f14", "panel":   "#13161e", "card":    "#1a1e2a",
    "border":  "#252a38", "accent":  "#7c5cfc", "accent2": "#00d4aa",
    "accent3": "#ff4d6d", "text":    "#e8eaf0", "muted":   "#6b7280",
    "yellow":  "#fbbf24", "blue":    "#3b82f6", "green":   "#22c55e",
}

# ── 시스템 폰트 및 유틸리티 ────────────────────────────────────────
def _detect_cjk_font() -> str:
    lang = get_language() if 'get_language' in dir() else 'ko'
    candidates_map = {
        'ko': {
            "Windows": ["Malgun Gothic", "NanumGothic", "Gulim"],
            "Darwin":  ["Apple SD Gothic Neo", "AppleGothic", "NanumGothic"],
            "Linux":   ["NanumGothic", "UnDotum", "Noto Sans CJK KR"],
        },
        'ja': {
            "Windows": ["Yu Gothic", "Meiryo", "MS Gothic"],
            "Darwin":  ["Hiragino Sans", "Hiragino Kaku Gothic Pro"],
            "Linux":   ["Noto Sans CJK JP", "TakaoGothic"],
        },
        'zh': {
            "Windows": ["Microsoft YaHei", "SimHei", "NSimSun"],
            "Darwin":  ["PingFang SC", "STHeiti"],
            "Linux":   ["Noto Sans CJK SC", "WenQuanYi Micro Hei"],
        },
        'en': {
            "Windows": ["Segoe UI", "DejaVu Sans"],
            "Darwin":  ["Helvetica Neue", "Helvetica"],
            "Linux":   ["DejaVu Sans", "Liberation Sans"],
        },
    }
    lang_map = candidates_map.get(lang, candidates_map.get('ko', {}))
    candidates = lang_map.get(platform.system(), [])
    if not MATPLOTLIB_AVAILABLE or fm is None:
        return "DejaVu Sans"
    available = {f.name for f in fm.fontManager.ttflist}
    return next((f for f in candidates if f in available), "DejaVu Sans")

_CJK_FONT = _detect_cjk_font()
if MATPLOTLIB_AVAILABLE and matplotlib is not None:
    matplotlib.rcParams["font.family"] = _CJK_FONT
    matplotlib.rcParams["axes.unicode_minus"] = False


def normalize_name(name: str) -> str:
    return unicodedata.normalize("NFKC", name).lower().strip()


# ── TETR.IO 공통 분석 헬퍼 ───────────────────────────────────────
def _safe_int(value, default: int = 0) -> int:
    try: return int(float(value))
    except Exception: return default

def _safe_float(value, default: float = 0.0) -> float:
    try: return round(float(value), 2)
    except Exception: return default

def resolve_player_identifier(text: str) -> str:
    raw = (text or '').strip()
    if not raw: return ''
    try:
        parsed = urllib.parse.urlparse(raw)
        if parsed.scheme and parsed.netloc:
            parts = [p for p in parsed.path.split('/') if p]
            if len(parts) >= 2 and parts[0].lower() == 'u': return urllib.parse.unquote(parts[1])
            if parts: return urllib.parse.unquote(parts[-1])
    except Exception: pass
    return raw

def _normalize_match_result(value) -> tuple[str | None, bool | None]:
    if not isinstance(value, str): return None, None
    s = value.strip().lower()
    if not s: return None, None
    if 'victory' in s or s == 'win' or s.endswith('win'): return 'win', True
    if 'defeat' in s or s == 'loss' or s.endswith('loss') or s.endswith('lose'): return 'loss', False
    if 'tie' in s: return 'draw', None
    if 'contest' in s or 'nullif' in s or 'cancel' in s: return 'void', None
    return value, None

def _api_get_json(path: str, params: dict | None = None, timeout: int = API_TIMEOUT) -> dict:
    url = f"{TETRIO_API_BASE}{path}"
    if params: url += '?' + urllib.parse.urlencode(params, doseq=True)
    req = urllib.request.Request(
        url,
        headers={
            'Accept': 'application/json',
            'User-Agent': 'TetrioCoach/1.0',
            'X-Session-ID': _API_SESSION_ID,
        },
        method='GET',
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            payload = resp.read().decode('utf-8')
    except urllib.error.HTTPError as e:
        raise ConnectionError(f'TETR.IO API HTTP 오류: {e.code}') from e
    except urllib.error.URLError as e:
        raise ConnectionError(f'TETR.IO API 연결 실패: {e.reason}') from e

    data = json.loads(payload)
    if not data.get('success', True):
        err = data.get('error')
        msg = err.get('message') if isinstance(err, dict) else str(err)
        raise ValueError(msg or 'TETR.IO API 요청 실패')
    return data.get('data') or {}


# ── 통합 범용 파싱 엔진 (로컬 & 온라인 모두 지원) ───────────────────────────
def _extract_round_scoreboards(raw: dict) -> tuple[list, dict, dict]:
    def _listish(value):
        return value if isinstance(value, list) else None

    def _dig(*keys, base):
        cur = base
        for key in keys:
            if not isinstance(cur, dict):
                return None
            cur = cur.get(key)
        return cur

    rounds_candidates = []
    results_block = raw.get('results') if isinstance(raw.get('results'), dict) else {}
    replay_block = raw.get('replay') if isinstance(raw.get('replay'), dict) else {}

    # 다양한 TETR.IO 레코드 형태를 모두 수용
    rounds_candidates.extend([
        _listish(_dig('rounds', base=results_block)),
        _listish(raw.get('endcontext')),
        _listish(raw.get('rounds')),
        _listish(_dig('rounds', base=replay_block)),
        _listish(_dig('results', 'rounds', base=replay_block)),
        _listish(_dig('results', 'rounds', base=raw.get('replay', {}))),
    ])

    rounds = next((c for c in rounds_candidates if c), None)
    if not isinstance(rounds, list) or not rounds:
        raise ValueError('라운드 데이터를 찾지 못했습니다. (데이터 구조가 다르거나 비어있는 기록입니다.)')

    # scoreboards가 2중 리스트가 아닌 경우도 방어적으로 처리
    if rounds and isinstance(rounds[0], dict):
        rounds = [rounds]

    extras = raw.get('extras') if isinstance(raw.get('extras'), dict) else {}
    leaderboard = None

    leaderboard_candidates = [
        _dig('leaderboard', base=results_block),
        raw.get('leaderboard'),
        _dig('results', 'leaderboard', base=raw) if isinstance(raw, dict) else None,
        _dig('leaderboard', base=replay_block),
    ]
    leaderboard = next((c for c in leaderboard_candidates if isinstance(c, list) and c), None)

    return rounds, extras, {'results': results_block, 'leaderboard': leaderboard}

def _identify_player_context(raw: dict, fallback_username: str = '') -> tuple[str, str, set[str], set[str]]:
    user_block = raw.get('user') if isinstance(raw.get('user'), dict) else {}
    username = user_block.get('username') or raw.get('username') or raw.get('name') or fallback_username or '?'
    user_id = str(user_block.get('id') or user_block.get('_id') or raw.get('user_id') or raw.get('_id') or '')
    names = {normalize_name(v) for v in [username, fallback_username, raw.get('username', ''), raw.get('name', '')] if isinstance(v, str) and v.strip()}
    ids = {str(v) for v in [user_id, raw.get('_id', ''), raw.get('id', '')] if v}
    return username, user_id, names, ids

def _find_leaderboard_entry(leaderboard: list | None, target_names: set[str], target_ids: set[str]) -> dict | None:
    if not isinstance(leaderboard, list): return None
    for entry in leaderboard:
        if not isinstance(entry, dict): continue
        entry_id = str(entry.get('id') or entry.get('_id') or '')
        entry_name = normalize_name(entry.get('username', '') or entry.get('name', ''))
        if (entry_id and entry_id in target_ids) or (entry_name and entry_name in target_names): return entry
    return leaderboard[0] if len(leaderboard) == 1 and isinstance(leaderboard[0], dict) else None

def _pick_scoreboard_entry(scoreboard: list, target_names: set[str], target_ids: set[str]) -> dict | None:
    if not isinstance(scoreboard, list): scoreboard = [scoreboard] if isinstance(scoreboard, dict) else []
    for entry in scoreboard:
        if not isinstance(entry, dict): continue
        entry_id = str(entry.get('id') or entry.get('_id') or '')
        entry_name = normalize_name(entry.get('username', '') or entry.get('name', ''))
        if (entry_id and entry_id in target_ids) or (entry_name and entry_name in target_names): return entry
    for entry in scoreboard:
        if not isinstance(entry, dict): continue
        if entry.get('alive') is True or entry.get('success') is True or entry.get('active') is True: return entry
    for entry in scoreboard:
        if isinstance(entry, dict): return entry
    return None

def _infer_round_win(entry: dict) -> bool:
    for key in ('success', 'alive', 'won'):
        if key in entry: return bool(entry.get(key))
    if 'active' in entry: return bool(entry.get('active'))
    return False

def parse_record_payload(raw: dict, fallback_username: str = '', source_label: str = '', origin: str = 'file') -> dict:
    if not isinstance(raw, dict): raise ValueError('기록 데이터 형식이 올바르지 않습니다.')

    rounds_raw, extras, containers = _extract_round_scoreboards(raw)
    leaderboard = containers.get('leaderboard')
    username, user_id, target_names, target_ids = _identify_player_context(raw, fallback_username)
    match_entry = _find_leaderboard_entry(leaderboard, target_names, target_ids)

    gametype = raw.get('gametype', raw.get('gamemode', 'league'))
    ts = raw.get('ts', raw.get('timestamp', ''))
    record_id = str(raw.get('replayid') or raw.get('_id') or source_label or username)
    record_label = source_label or raw.get('replayid') or raw.get('_id') or username

    match_result_raw = extras.get('result') if isinstance(extras, dict) else None
    match_result, match_won_flag = _normalize_match_result(match_result_raw)

    match_wins = _safe_int(match_entry.get('wins', 0), 0) if match_entry else None
    match_total_rounds = len(rounds_raw)

    if match_result is None and isinstance(leaderboard, list) and leaderboard:
        wins = [_safe_int(p.get('wins', -1), -1) for p in leaderboard if isinstance(p, dict)]
        best_wins = max(wins) if wins else -1
        if match_entry and best_wins >= 0:
            entry_wins = _safe_int(match_entry.get('wins', 0), 0)
            if entry_wins == best_wins and len([w for w in wins if w == best_wins]) == 1:
                match_result, match_won_flag = 'win', True
            elif entry_wins < best_wins:
                match_result, match_won_flag = 'loss', False
            elif entry_wins > best_wins:
                match_result, match_won_flag = 'win', True

    if match_result is None and match_entry is not None:
        # leaderboards가 없거나 애매한 경우, 라운드 승패로 최종 결과 추정
        round_wins = 0
        for scoreboard in rounds_raw:
            candidate = _pick_scoreboard_entry(scoreboard, target_names, target_ids)
            if candidate is not None and _infer_round_win(candidate):
                round_wins += 1
        round_losses = len(rounds_raw) - round_wins
        if round_wins > round_losses: match_result, match_won_flag = 'win', True
        elif round_wins < round_losses: match_result, match_won_flag = 'loss', False
        else: match_result, match_won_flag = 'draw', None

    extracted_rounds: list[dict] = []
    for idx, scoreboard in enumerate(rounds_raw, start=1):
        candidate = _pick_scoreboard_entry(scoreboard, target_names, target_ids)
        if candidate is None: continue

        round_won = _infer_round_win(candidate)

        # 통계 데이터 우선순위: replay.results.stats > candidate.stats > candidate
        deep_stats = {}
        replay_block = candidate.get('replay')
        if isinstance(replay_block, dict):
            results_block = replay_block.get('results')
            if isinstance(results_block, dict):
                ds = results_block.get('stats')
                if isinstance(ds, dict):
                    deep_stats = ds

        stats_obj = candidate.get('stats', candidate)
        if "stats" in candidate and isinstance(candidate["stats"], dict):
            stats_obj = candidate["stats"]
        elif "result" in candidate and isinstance(candidate["result"], dict):
            stats_obj = candidate["result"].get("stats", candidate["result"])

        def _get_stat(key, default=0):
            if key in deep_stats: return deep_stats[key]
            if key in stats_obj: return stats_obj[key]
            if key in candidate: return candidate[key]
            return default

        clears_raw = deep_stats.get("clears") or stats_obj.get("clears") or candidate.get("clears") or {}
        if not isinstance(clears_raw, dict): clears_raw = {}
        fin = deep_stats.get("finesse") or stats_obj.get("finesse") or candidate.get("finesse") or {}
        if not isinstance(fin, dict): fin = {}
        garbage_obj = deep_stats.get("garbage") or stats_obj.get("garbage") or {}
        if not isinstance(garbage_obj, dict): garbage_obj = {}

        tspin_singles = _safe_int(clears_raw.get("tspinsingles", 0)) + _safe_int(clears_raw.get("tspin_singles", 0)) + _safe_int(clears_raw.get("tspin_single", 0))
        tspin_doubles = _safe_int(clears_raw.get("tspindoubles", 0)) + _safe_int(clears_raw.get("tspin_doubles", 0)) + _safe_int(clears_raw.get("tspin_double", 0))
        tspin_triples = _safe_int(clears_raw.get("tspintriples", 0)) + _safe_int(clears_raw.get("tspin_triples", 0)) + _safe_int(clears_raw.get("tspin_triple", 0))
        tspin_quads = _safe_int(clears_raw.get("tspinquads", 0)) + _safe_int(clears_raw.get("tspin_quads", 0)) + _safe_int(clears_raw.get("tspin_quad", 0))
        tspin_minis = (
            _safe_int(clears_raw.get("minitspins", 0)) + _safe_int(clears_raw.get("minitspinsingles", 0)) +
            _safe_int(clears_raw.get("minitspindoubles", 0)) + _safe_int(clears_raw.get("minitspintriples", 0)) +
            _safe_int(clears_raw.get("minitspinquads", 0)) +
            _safe_int(clears_raw.get("tspin_minis", 0)) + _safe_int(clears_raw.get("tspin_mini", 0))
        )
        tspin_count = tspin_singles + tspin_doubles + tspin_triples + tspin_quads + tspin_minis
        if tspin_count == 0:
            tspin_count = _safe_int(deep_stats.get("tspins", 0)) or _safe_int(clears_raw.get("tspins", 0))

        allclear = _safe_int(clears_raw.get("allclear", 0))
        top_combo = _safe_int(_get_stat("topcombo", 0))
        top_btb = _safe_int(_get_stat("topbtb", 0))
        score = _safe_int(_get_stat("score", 0))

        duration_ms = _get_stat("finaltime", 0) or _get_stat("duration", 0)

        garbage_sent_val = garbage_obj.get("sent") if garbage_obj else None
        if garbage_sent_val is None:
            garbage_sent_val = _get_stat("garbagesent", 0)
        garbage_recv_val = garbage_obj.get("received") if garbage_obj else None
        if garbage_recv_val is None:
            garbage_recv_val = _get_stat("garbagereceived", 0)
        if isinstance(garbage_sent_val, dict): garbage_sent_val = garbage_sent_val.get("sent", 0)
        if isinstance(garbage_recv_val, dict): garbage_recv_val = garbage_recv_val.get("received", 0)

        garbage_attack = _safe_int(garbage_obj.get("attack", 0))
        garbage_cleared = _safe_int(garbage_obj.get("cleared", 0))
        max_spike = _safe_int(garbage_obj.get("maxspike", 0))

        has_detail = bool(deep_stats)

        parsed = {
            "round": idx,
            "source_file": record_label,
            "username": candidate.get("username") or candidate.get("name") or username,
            "has_detail": has_detail,
            "apm": round(_safe_float(_get_stat("apm", 0)), 2),
            "pps": round(_safe_float(_get_stat("pps", 0) or _get_stat("pps", 0)), 2),
            "vs": round(_safe_float(_get_stat("vsscore", 0) or _get_stat("vs", 0)), 2),
            "inputs": _safe_int(_get_stat("inputs", 0)),
            "pieces": _safe_int(_get_stat("piecesplaced", 0) or _get_stat("pieces", 0)),
            "lines": _safe_int(_get_stat("lines", 0)),
            "clears": {
                "single": _safe_int(clears_raw.get("singles", clears_raw.get("single", 0))),
                "double": _safe_int(clears_raw.get("doubles", clears_raw.get("double", 0))),
                "triple": _safe_int(clears_raw.get("triples", clears_raw.get("triple", 0))),
                "quad": _safe_int(clears_raw.get("quads", clears_raw.get("quad", 0))),
                "tspin": tspin_count,
                "tspin_single": tspin_singles,
                "tspin_double": tspin_doubles,
                "tspin_triple": tspin_triples,
                "tspin_quad": tspin_quads,
                "tspin_mini": tspin_minis,
                "allclear": allclear,
            },
            "garbage_sent": _safe_int(garbage_sent_val),
            "garbage_recv": _safe_int(garbage_recv_val),
            "garbage_attack": garbage_attack,
            "garbage_cleared": garbage_cleared,
            "max_spike": max_spike,
            "top_combo": top_combo,
            "top_btb": top_btb,
            "score": score,
            "won": round_won,
            "finesse_faults": _safe_int(fin.get("faults", 0)),
            "finesse_perfect": _safe_int(fin.get("perfectpieces", 0)),
            "duration_ms": _safe_int(duration_ms),
            "ts": ts,
            "match_round": idx,
            "match_total_rounds": match_total_rounds,
            "match_id": record_id,
            "match_label": record_label,
            "match_result": match_result,
            "match_won": match_won_flag,
            "match_wins": match_wins,
            "record_kind": origin,
            "match_source": "TETR.IO API" if origin == 'site' else "local file",
        }
        extracted_rounds.append(parsed)

    if not extracted_rounds: raise ValueError('유효한 라운드 데이터를 찾지 못했습니다.')

    if match_result is None:
        round_wins = sum(1 for r in extracted_rounds if r.get('won'))
        round_losses = len(extracted_rounds) - round_wins
        if round_wins > round_losses: match_result, match_won_flag = 'win', True
        elif round_wins < round_losses: match_result, match_won_flag = 'loss', False
        else: match_result, match_won_flag = 'draw', None
        if match_wins is None: match_wins = round_wins

    return {
        'filename': record_label,
        'filepath': raw.get('filepath', record_label),
        'ts': ts,
        'gametype': gametype,
        'rounds': extracted_rounds,
        'match_summary': {
            'match_id': record_id,
            'label': record_label,
            'rounds': match_total_rounds,
            'wins': match_wins,
            'losses': max(match_total_rounds - _safe_int(match_wins, 0), 0) if match_wins is not None else None,
            'result': match_result,
            'origin': origin,
            'avg_apm': round(sum(_safe_float(r.get('apm', 0)) for r in extracted_rounds) / max(len(extracted_rounds), 1), 2),
            'avg_pps': round(sum(_safe_float(r.get('pps', 0)) for r in extracted_rounds) / max(len(extracted_rounds), 1), 2),
            'avg_vs': round(sum(_safe_float(r.get('vs', 0)) for r in extracted_rounds) / max(len(extracted_rounds), 1), 2),
            'sent': sum(_safe_int(r.get('garbage_sent', 0)) for r in extracted_rounds),
            'recv': sum(_safe_int(r.get('garbage_recv', 0)) for r in extracted_rounds),
        },
    }

def parse_local_ttrm(filepath: str, username: str = '') -> dict:
    path = Path(filepath)
    if not path.exists(): raise FileNotFoundError(f'파일을 찾을 수 없습니다: {path.name}')
    try: raw = json.loads(path.read_text(encoding='utf-8'))
    except json.JSONDecodeError as e: raise ValueError(f'JSON 파싱 실패 ({path.name}): {e}') from e

    raw['filepath'] = str(path)
    return parse_record_payload(raw, fallback_username=username, source_label=path.stem, origin='file')

def fetch_recent_league_records(username: str, max_records: int | None = None, ui_callback=None) -> list[dict]:
    user = resolve_player_identifier(username)
    if not user: raise ValueError('분석할 사용자 이름이 비어 있습니다.')

    limit_total = None if not max_records or max_records <= 0 else max_records
    collected: list[dict] = []
    cursor = None
    seen_cursors: set[str] = set()

    while True:
        remaining = None if limit_total is None else max(limit_total - len(collected), 0)
        if remaining == 0: break
        page_limit = SITE_PAGE_LIMIT if remaining is None else min(SITE_PAGE_LIMIT, remaining)
        params = {'limit': page_limit}
        if cursor: params['after'] = cursor

        data = _api_get_json(f"/users/{urllib.parse.quote(user)}/records/league/recent", params=params)
        entries = data.get('entries', []) if isinstance(data, dict) else []
        if not entries: break

        for entry in entries:
            if isinstance(entry, dict):
                collected.append(entry)
                if limit_total is not None and len(collected) >= limit_total:
                    return collected[:limit_total]

        # UI 프로그레스 리포트
        if ui_callback:
            ui_callback(len(collected), limit_total)

        last = entries[-1] if entries else None
        p = last.get('p') if isinstance(last, dict) else None
        if not isinstance(p, dict): break
        cursor = f"{p.get('pri')}:{p.get('sec')}:{p.get('ter')}"
        if cursor in seen_cursors: break
        seen_cursors.add(cursor)
        if len(entries) < page_limit: break

    return collected


# ── 데이터 통계 및 스타일 분석 ─────────────────────────────────────
def _sum_clear(rounds: list[dict], key: str) -> int:
    return sum(_safe_int(r.get('clears', {}).get(key, 0)) for r in rounds)

def _sum_field(rounds: list[dict], key: str) -> int:
    return sum(_safe_int(r.get(key, 0)) for r in rounds)

def _max_field(rounds: list[dict], key: str) -> int:
    return max((_safe_int(r.get(key, 0)) for r in rounds), default=0)

def compute_aggregates_v2(rounds: list[dict]) -> dict:
    if not rounds: return {}
    n = len(rounds)
    def avg(key: str) -> float: return round(sum(_safe_float(r.get(key, 0)) for r in rounds) / n, 2)

    wins = sum(1 for r in rounds if r.get('won'))
    detail_rounds = sum(1 for r in rounds if r.get('has_detail'))
    has_detail = detail_rounds > 0

    clear_keys = ['tspin', 'tspin_single', 'tspin_double', 'tspin_triple', 'tspin_quad',
                  'tspin_mini', 'single', 'double', 'triple', 'quad', 'allclear']
    clears = {k: _sum_clear(rounds, k) for k in clear_keys}

    total_pieces = _sum_field(rounds, 'pieces')
    total_faults = _sum_field(rounds, 'finesse_faults')
    total_perfect_pieces = _sum_field(rounds, 'finesse_perfect')
    total_lines = _sum_field(rounds, 'lines')
    total_score = _sum_field(rounds, 'score')
    max_combo = _max_field(rounds, 'top_combo')
    max_btb = _max_field(rounds, 'top_btb')
    max_spike = _max_field(rounds, 'max_spike')

    match_groups: dict[str, list[dict]] = {}
    for r in rounds:
        key = str(r.get('match_id') or r.get('source_file') or r.get('match_label') or r.get('round'))
        match_groups.setdefault(key, []).append(r)

    match_wins = match_losses = match_draws = 0
    for group in match_groups.values():
        explicit = next((g.get('match_result') for g in group if g.get('match_result')), None)
        if explicit == 'win': match_wins += 1
        elif explicit == 'loss': match_losses += 1
        elif explicit == 'draw': match_draws += 1
        else:
            round_wins = sum(1 for g in group if g.get('won'))
            round_losses = len(group) - round_wins
            if round_wins > round_losses: match_wins += 1
            elif round_wins < round_losses: match_losses += 1
            else: match_draws += 1

    matches = len(match_groups)
    round_win_rate = round(wins / n * 100, 1)
    match_played = matches if matches else 1
    match_win_rate = round(match_wins / match_played * 100, 1)

    return {
        'rounds': n, 'games': n, 'matches': matches,
        'has_detail': has_detail, 'detail_rounds': detail_rounds,
        'wins': wins, 'losses': n - wins,
        'match_wins': match_wins, 'match_losses': match_losses, 'match_draws': match_draws,
        'win_rate': round_win_rate, 'round_win_rate': round_win_rate, 'match_win_rate': match_win_rate,
        'avg_apm': avg('apm'), 'avg_pps': avg('pps'), 'avg_vs': avg('vs'),
        'avg_garbage_sent': avg('garbage_sent'), 'avg_garbage_recv': avg('garbage_recv'),
        'total_tspin': clears['tspin'], 'total_quads': clears['quad'],
        'tspin_rate': round(clears['tspin'] / max(total_pieces, 1) * 100, 2),
        'total_tspin_single': clears['tspin_single'], 'total_tspin_double': clears['tspin_double'],
        'total_tspin_triple': clears['tspin_triple'], 'total_tspin_quad': clears['tspin_quad'],
        'total_tspin_mini': clears['tspin_mini'],
        'total_singles': clears['single'], 'total_doubles': clears['double'],
        'total_triples': clears['triple'], 'total_lines': total_lines,
        'total_allclear': clears['allclear'],
        'total_score': total_score,
        'max_combo': max_combo, 'max_btb': max_btb, 'max_spike': max_spike,
        'finesse_fault_rate': round(total_faults / max(total_pieces, 1) * 100, 1),
        'finesse_perfect_rate': round(total_perfect_pieces / max(total_pieces, 1) * 100, 1),
        'total_finesse_faults': total_faults, 'total_perfect_pieces': total_perfect_pieces,
        'total_pieces': total_pieces,
        'apm_trend': _trend([_safe_float(r.get('apm', 0)) for r in rounds]),
        'pps_trend': _trend([_safe_float(r.get('pps', 0)) for r in rounds]),
    }

def _trend(vals: list) -> str:
    if len(vals) < 2: return t('stats.trend_flat')
    mid = len(vals) // 2
    a = sum(vals[:mid]) / max(mid, 1)
    b = sum(vals[mid:]) / max(len(vals) - mid, 1)
    diff = b - a
    if diff > 0.5: return t('stats.trend_up')
    if diff < -0.5: return t('stats.trend_down')
    return t('stats.trend_flat')

def analyze_play_style_v2(agg: dict) -> dict:
    avg_apm = _safe_float(agg.get('avg_apm', 0))
    avg_pps = _safe_float(agg.get('avg_pps', 0))
    avg_vs = _safe_float(agg.get('avg_vs', 0))
    sent = _safe_float(agg.get('avg_garbage_sent', 0))
    recv = _safe_float(agg.get('avg_garbage_recv', 0))
    fault_rate = _safe_float(agg.get('finesse_fault_rate', 0))
    tspin_rate = _safe_float(agg.get('tspin_rate', 0))
    pressure = sent / max(recv, 1.0)

    tags = []
    if avg_pps >= 2.3: tags.append(t('style.fast'))
    elif avg_pps <= 1.9: tags.append(t('style.slow'))
    else: tags.append(t('style.mid_speed'))

    if avg_apm >= 80 or pressure >= 1.2: tags.append(t('style.aggressive'))
    elif recv > sent: tags.append(t('style.defensive'))
    else: tags.append(t('style.balanced'))

    if fault_rate <= 5: tags.append(t('style.balanced'))
    elif fault_rate >= 10: tags.append(t('style.finesse_needed'))
    if tspin_rate >= 4: tags.append(t('style.tspin_user'))

    core = tags[:3]
    return {
        'primary': ' / '.join(core),
        'pressure_ratio': round(pressure, 2),
        'summary': f"APM {avg_apm}, PPS {avg_pps}, VS {avg_vs}, ATK {sent}L, RCV {recv}L, Fault {fault_rate}% — {' / '.join(core)}",
    }

def _select_coaching_rounds_v2(rounds: list[dict], n: int = COACH_ROUNDS) -> list[dict]:
    if len(rounds) <= n: return rounds
    selected = []
    recent_n = max(4, n // 2)
    selected.extend(rounds[-recent_n:])
    for key in ('apm', 'pps', 'vs', 'garbage_sent', 'garbage_recv', 'finesse_faults'):
        try:
            selected.append(max(rounds, key=lambda r: _safe_float(r.get(key, 0))))
            selected.append(min(rounds, key=lambda r: _safe_float(r.get(key, 0))))
        except Exception: continue

    dedup = {}
    for r in selected:
        k = (r.get('match_id'), r.get('match_round'), r.get('round'), r.get('source_file'))
        dedup[k] = r
    ordered = sorted(dedup.values(), key=lambda r: (_safe_int(r.get('round', 0)), _safe_int(r.get('match_round', 0))))
    return ordered[:n]




def _training_priority_map(agg: dict) -> list[dict]:
    avg_apm = _safe_float(agg.get("avg_apm", 0))
    avg_pps = _safe_float(agg.get("avg_pps", 0))
    avg_vs = _safe_float(agg.get("avg_vs", 0))
    sent = _safe_float(agg.get("avg_garbage_sent", 0))
    recv = _safe_float(agg.get("avg_garbage_recv", 0))
    fault_rate = _safe_float(agg.get("finesse_fault_rate", 0))
    tspin_rate = _safe_float(agg.get("tspin_rate", 0))
    round_win_rate = _safe_float(agg.get("round_win_rate", agg.get("win_rate", 0)))
    pressure = sent / max(recv, 1.0)

    rows: list[tuple[int, dict]] = []

    if fault_rate >= 12:
        rows.append((100, {
            "title": "정확도 복구",
            "reason": f"Finesse Fault 비율이 {fault_rate}%로 높습니다.",
            "drill": "빈 보드/낮은 속도 구간에서 10분간 정확 배치만 반복하고, 미스드랍이 나온 위치를 바로 메모하세요.",
            "target": "1세션당 Fault 비율을 20% 이상 낮추기",
            "duration": "15분",
            "metric": f"현재 Fault율 {fault_rate}%",
        }))
    elif fault_rate >= 8:
        rows.append((90, {
            "title": "정교함 보완",
            "reason": f"Finesse Fault 비율이 {fault_rate}%로 보완 여지가 있습니다.",
            "drill": "첫 10판은 속도보다 배치 정확도에 집중하고, 한 판 끝날 때마다 실수 유형을 1개씩 적으세요.",
            "target": "연속 3판 이상 큰 미스드랍 없이 유지",
            "duration": "12분",
            "metric": f"현재 Fault율 {fault_rate}%",
        }))

    if avg_pps < 1.9:
        rows.append((95, {
            "title": "스피드 업",
            "reason": f"평균 PPS가 {avg_pps}로 속도 자체가 부족한 편입니다.",
            "drill": "2분 스프린트 3회 + 20초 휴식으로 리듬을 만들고, 스택 높이를 일정하게 유지하세요.",
            "target": "PPS를 0.1~0.2 끌어올리기",
            "duration": "15분",
            "metric": f"현재 PPS {avg_pps}",
        }))
    elif avg_pps > 2.4:
        rows.append((40, {
            "title": "속도 유지",
            "reason": f"평균 PPS가 {avg_pps}로 충분히 빠르지만, 정확도와의 균형이 중요합니다.",
            "drill": "빠른 판에서도 왼쪽/오른쪽 이동 횟수를 줄이며 홀드 활용만 최적화하세요.",
            "target": "속도 유지 상태에서 Fault 증가 억제",
            "duration": "10분",
            "metric": f"현재 PPS {avg_pps}",
        }))

    if avg_apm < 50:
        rows.append((88, {
            "title": "공격 루트 개선",
            "reason": f"평균 APM이 {avg_apm}로 공격 전개가 약합니다.",
            "drill": "오프닝 3가지(예: STSD 계열, opener 기본형)를 정해 반복하고, 4연쇄 공격 루트를 외우세요.",
            "target": "한 판당 어택량을 안정적으로 늘리기",
            "duration": "15분",
            "metric": f"현재 APM {avg_apm}",
        }))

    if tspin_rate < 2:
        rows.append((80, {
            "title": "T-Spin 인식",
            "reason": f"T-Spin 비율이 {tspin_rate}%로 활용도가 낮습니다.",
            "drill": "T-Spin Double 패턴만 따로 연습하고, '쌓기→오픈→회전' 순서를 고정하세요.",
            "target": "T-Spin 기회 탐지 속도 향상",
            "duration": "12분",
            "metric": f"현재 T-Spin 비율 {tspin_rate}%",
        }))
    elif tspin_rate >= 4:
        rows.append((35, {
            "title": "T-Spin 유지",
            "reason": f"T-Spin 비율이 {tspin_rate}%로 강점이 있습니다.",
            "drill": "T-Spin을 억지로 늘리기보다 다운스택 타이밍에서만 효율적으로 사용하세요.",
            "target": "T-Spin 유지 + 낭비 감소",
            "duration": "10분",
            "metric": f"현재 T-Spin 비율 {tspin_rate}%",
        }))

    if recv > sent:
        rows.append((92, {
            "title": "수비/회복",
            "reason": f"평균 수신 {recv}L가 평균 어택 {sent}L보다 높습니다.",
            "drill": "받은 쓰레기를 즉시 처리하는 연습을 위해, 고정된 스택에서 5라인 이하를 빠르게 복구하세요.",
            "target": "받은 쓰레기 처리 시간 단축",
            "duration": "10분",
            "metric": f"어택 {sent}L / 수신 {recv}L",
        }))
    elif pressure < 0.9:
        rows.append((70, {
            "title": "압박 밸런스",
            "reason": f"공격 대비 수신 비율이 낮아 공격 효율이 떨어질 수 있습니다.",
            "drill": "공격 전개 전에 보드 상태를 한 번 더 확인하고, 불필요한 홀드를 줄이세요.",
            "target": "어택/수비 균형 개선",
            "duration": "10분",
            "metric": f"압박 비율 {round(pressure, 2)}",
        }))

    if round_win_rate < 50:
        rows.append((85, {
            "title": "결정력",
            "reason": f"라운드 승률이 {round_win_rate}%로, 마무리 판단이 흔들리고 있습니다.",
            "drill": "패배 라운드 3개를 다시 보고, 마지막 20초의 판단을 한 줄로 복기하세요.",
            "target": "접전 라운드 승률 개선",
            "duration": "8분",
            "metric": f"현재 라운드 승률 {round_win_rate}%",
        }))

    if avg_vs and avg_vs < 45:
        rows.append((60, {
            "title": "종합 전투력",
            "reason": f"VS Score가 {avg_vs}로 공격/생존/회복이 함께 부족할 수 있습니다.",
            "drill": "라운드마다 '지금 공격할지, 쌓을지, 다운스택할지'를 한 문장으로 말하며 플레이하세요.",
            "target": "상황 판단 자동화",
            "duration": "8분",
            "metric": f"현재 VS {avg_vs}",
        }))

    rows.sort(key=lambda x: x[0], reverse=True)
    return [r for _, r in rows[:4]]


def _summarize_source_label(source_label: str, max_len: int = 80) -> str:
    if len(source_label) <= max_len:
        return source_label
    parts = [p.strip() for p in source_label.split(',') if p.strip()]
    if len(parts) <= 2:
        return source_label[:max_len - 3] + '...'
    return f"{parts[0]}, {parts[1]} +{len(parts) - 2}"



def build_training_roadmap_v2(agg: dict, my_rounds: list[dict], match_summaries: list[dict], username: str, source_label: str) -> str:
    short_source = _summarize_source_label(source_label)
    style = analyze_play_style_v2(agg)
    priorities = _training_priority_map(agg)

    lines = [
        f"{t('report.roadmap_header')} — {username}",
        f"{short_source}",
        "",
        t('coach.section_style'),
        style["summary"],
        "",
        t('coach.section_priority'),
    ]

    if priorities:
        for i, item in enumerate(priorities, start=1):
            lines.extend([
                f"{i}. {item['title']}",
                f"   - {item['reason']}",
                f"   - {item['drill']}",
                f"   - {item['target']}",
                f"   - {item['duration']}",
            ])
    else:
        lines.append(t('coach.no_weaknesses'))

    lines.append("")
    lines.append(t('coach.data_insufficient'))
    return "\n".join(lines)


def _roadmap_to_html(title: str, text_block: str, agg: dict, username: str, source_label: str, match_summaries: list[dict], profile_url: str) -> str:
    summary_cards = [
        (t('stats.total_matches'), agg.get("matches", 0)),
        (t('stats.total_rounds'), agg.get("rounds", agg.get("games", 0))),
        (t('stats.round_winrate'), f"{agg.get('round_win_rate', agg.get('win_rate', 0))}%"),
        ("APM", agg.get("avg_apm", 0)),
        ("PPS", agg.get("avg_pps", 0)),
        (t('stats.finesse'), f"{agg.get('finesse_fault_rate', 0)}%"),
    ]
    recent_html = ""
    for m in (match_summaries[-8:] if match_summaries else []):
        recent_html += f"""
        <tr>
            <td>{html.escape(str(m.get('label', 'Unknown')))}</td>
            <td>{html.escape(str(m.get('result', '?')))}</td>
            <td>{html.escape(str(m.get('wins', 0)))}</td>
            <td>{html.escape(str(m.get('losses', 0)))}</td>
            <td>{html.escape(str(m.get('avg_apm', 0)))}</td>
            <td>{html.escape(str(m.get('avg_pps', 0)))}</td>
        </tr>"""
    escaped_text = html.escape(text_block).replace("\n", "<br>")
    cards_html = "".join(
        f"<div class='card'><div class='k'>{html.escape(str(k))}</div><div class='v'>{html.escape(str(v))}</div></div>"
        for k, v in summary_cards
    )
    return f"""<!doctype html>
<html lang="{get_language()}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<style>
body{{font-family:system-ui,-apple-system,Segoe UI,Malgun Gothic,sans-serif;background:#0d0f14;color:#e8eaf0;margin:0;padding:24px;}}
.wrap{{max-width:1180px;margin:0 auto;}}
h1,h2,h3{{margin:0 0 12px 0;}}
.sub{{color:#9ca3af;margin-bottom:18px;}}
.cards{{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:12px;margin:18px 0;}}
.card{{background:#1a1e2a;border:1px solid #252a38;border-radius:14px;padding:14px;}}
.card .k{{font-size:12px;color:#9ca3af}}
.card .v{{font-size:22px;font-weight:700;margin-top:6px}}
.panel{{background:#13161e;border:1px solid #252a38;border-radius:14px;padding:18px;margin:18px 0;}}
pre{{white-space:pre-wrap;word-break:break-word;font-family:inherit;line-height:1.55;margin:0;}}
table{{width:100%;border-collapse:collapse;margin-top:10px;}}
th,td{{border-bottom:1px solid #252a38;padding:8px 6px;text-align:left;font-size:13px;}}
a{{color:#7c5cfc;text-decoration:none;}}
small{{color:#9ca3af;}}
</style>
</head>
<body>
<div class="wrap">
  <h1>{html.escape(title)}</h1>
  <div class="sub">{html.escape(username)} · {html.escape(source_label)} · {datetime.now().strftime("%Y-%m-%d %H:%M")}</div>
  <div class="cards">{cards_html}</div>
  <div class="panel">
    <h2>{html.escape(t('report.roadmap_header'))}</h2>
    <pre>{escaped_text}</pre>
  </div>
  <div class="panel">
    <h2>{html.escape(t('report.profile_header'))}</h2>
    <p><a href="{html.escape(profile_url)}" target="_blank" rel="noopener noreferrer">{html.escape(profile_url)}</a></p>
  </div>
  <div class="panel">
    <h2>{html.escape(t('report.recent_header'))}</h2>
    <table>
      <thead><tr><th>{html.escape(t('report.match_col'))}</th><th>{html.escape(t('report.result_col'))}</th><th>W</th><th>L</th><th>APM</th><th>PPS</th></tr></thead>
      <tbody>{recent_html or '<tr><td colspan="6">' + html.escape(t('report.no_recent')) + '</td></tr>'}</tbody>
    </table>
  </div>
</div>
</body>
</html>"""


def _write_training_report(agg: dict, my_rounds: list[dict], match_summaries: list[dict], username: str, source_label: str, roadmap_text: str) -> Path:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    safe = re.sub(r'[^A-Za-z0-9._-]+', '_', normalize_name(username) or 'user')
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    profile_url = f"https://ch.tetr.io/u/{urllib.parse.quote(resolve_player_identifier(username))}/league"
    html_text = _roadmap_to_html(
        title=t('report.title', username=username),
        text_block=roadmap_text,
        agg=agg,
        username=username,
        source_label=source_label,
        match_summaries=match_summaries,
        profile_url=profile_url,
    )
    out = REPORT_DIR / f"{safe}_{ts}_roadmap.html"
    out.write_text(html_text, encoding="utf-8")
    return out


def _open_url(url: str) -> None:
    try:
        webbrowser.open(url, new=2, autoraise=True)
    except Exception:
        pass




# ── 그래프 생성 플로터 ──────────────────────────────────────────
def make_figure(my_rounds: list, file_boundaries: list, username: str) -> Figure | None:
    if not MATPLOTLIB_AVAILABLE:
        return None
    xs = list(range(1, len(my_rounds) + 1))
    fig = Figure(figsize=(10, 6), facecolor=C["panel"])
    fig.subplots_adjust(hspace=0.48, wspace=0.36, left=0.08, right=0.97, top=0.91, bottom=0.08)

    title_cfg = dict(color=C["text"], fontsize=9, fontweight="bold", pad=5)
    tick_cfg  = dict(colors=C["muted"], labelsize=7)

    def _style_ax(ax):
        ax.tick_params(axis="both", **tick_cfg)
        for sp in ax.spines.values(): sp.set_edgecolor(C["border"])
        ax.set_facecolor(C["card"])
        ax.grid(axis="y", color=C["border"], lw=0.5, ls="--")
        for bx in file_boundaries: ax.axvline(x=bx + 0.5, color=C["muted"], lw=0.8, ls=":", alpha=0.6)
        step = max(1, len(xs) // 20)
        visible_ticks = xs[::step]
        ax.set_xticks(visible_ticks)
        ax.set_xticklabels([f"R{x}" for x in visible_ticks], color=C["muted"], fontsize=6, rotation=45 if len(xs) > 40 else 0)

    ms = max(1, 6 - len(xs) // 20)
    lw = max(0.8, 2 - len(xs) / 100)

    def _line_ax(pos, title, ys, color):
        ax = fig.add_subplot(pos, facecolor=C["card"])
        ax.plot(xs, ys, color=color, lw=lw, marker="o", ms=ms, zorder=3)
        ax.fill_between(xs, ys, alpha=0.12, color=color)
        ax.set_title(title, **title_cfg)
        _style_ax(ax)
        return ax

    _line_ax(231, t('graph.apm'),  [r["apm"] for r in my_rounds], C["accent"])
    _line_ax(232, t('graph.pps'),    [r["pps"] for r in my_rounds], C["accent2"])
    _line_ax(233, t('graph.vs'),      [r["vs"]  for r in my_rounds], C["yellow"])

    ax4 = fig.add_subplot(234, facecolor=C["card"])
    ax4.plot(xs, [r["garbage_sent"] for r in my_rounds], color=C["accent3"], lw=lw, marker="o", ms=ms, label=t('graph.garbage_sent'))
    ax4.plot(xs, [r["garbage_recv"] for r in my_rounds], color=C["blue"],    lw=lw, marker="s", ms=ms, label=t('graph.garbage_recv'))
    ax4.set_title(t('graph.garbage'), **title_cfg)
    ax4.legend(fontsize=7, facecolor=C["card"], edgecolor=C["border"], labelcolor=C["text"])
    _style_ax(ax4)

    ax5 = fig.add_subplot(235, facecolor=C["card"])
    w = min(0.35, max(0.1, 10.0 / max(len(xs), 1)))
    ax5.bar([x - w/2 for x in xs], [r["clears"]["tspin"] for r in my_rounds], w, color=C["accent"],  label="T-Spin")
    ax5.bar([x + w/2 for x in xs], [r["clears"]["quad"]  for r in my_rounds], w, color=C["accent2"], label="Quad")
    ax5.set_title(t('graph.clears'), **title_cfg)
    ax5.legend(fontsize=7, facecolor=C["card"], edgecolor=C["border"], labelcolor=C["text"])
    _style_ax(ax5)

    _line_ax(236, t('graph.finesse'), [r["finesse_faults"] for r in my_rounds], C["accent3"])
    fig.suptitle(t('graph.title', username=username, count=len(my_rounds)), color=C["text"], fontsize=11, fontweight="bold")
    return fig


# ── GUI 레이아웃 구성 및 이벤트 핸들러 ───────────────────────────
def _sep(parent): tk.Frame(parent, bg=C['border'], height=1).pack(fill='x', pady=8)
def _section(parent, title):
    f = tk.Frame(parent, bg=C['panel'])
    f.pack(fill='x', padx=16, pady=(0, 4))
    tk.Label(f, text=title, bg=C['panel'], fg=C['muted'], font=('Segoe UI', 8, 'bold')).pack(anchor='w', pady=(0, 4))
    return f
def _btn(parent, text, cmd, secondary=False):
    return tk.Button(parent, text=text, command=cmd, bg=C['card'] if secondary else C['accent'], fg=C['text'],
                     activebackground=C['border'] if secondary else C['accent2'], activeforeground='white',
                     relief='flat', font=('Segoe UI', 9, 'bold'), cursor='hand2', pady=4)


class TetrioCoachAppModern(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("TETR.IO AI Coach")
        self.configure(bg=C["bg"])
        self.geometry(WINDOW_SIZE)
        self.minsize(*WINDOW_MIN)
        self._files: list[str] = []
        self._last_report_path: Path | None = None
        self._last_profile_url: str = ""
        i18n_init()
        self._build_ui()

    def _build_ui(self):
        sidebar = tk.Frame(self, bg=C['panel'], width=SIDEBAR_WIDTH)
        sidebar.pack(side='left', fill='y')
        sidebar.pack_propagate(False)

        lf = tk.Frame(sidebar, bg=C['panel'])
        lf.pack(fill='x', padx=16, pady=(20, 4))
        tk.Label(lf, text='⬡ TETR.IO', bg=C['panel'], fg=C['accent'], font=('Segoe UI', 16, 'bold')).pack(anchor='w')
        tk.Label(lf, text=t('app.subtitle'), bg=C['panel'], fg=C['muted'], font=('Segoe UI', 10)).pack(anchor='w')
        _sep(sidebar)

        # 1. 소스 선택 레이아웃
        sec0 = _section(sidebar, t('ui.source_select'))
        self.var_source = tk.StringVar(value='online')
        
        tk.Radiobutton(sec0, text=t('ui.source_online'), variable=self.var_source, value='online',
                       bg=C['panel'], fg=C['text'], selectcolor=C['card'], activebackground=C['panel'],
                       activeforeground=C['text'], font=('Segoe UI', 9), command=self._on_source_change).pack(anchor='w')
        
        self.frm_online = tk.Frame(sec0, bg=C["panel"])
        self.frm_online.pack(fill="x", padx=16, pady=4)
        tk.Label(self.frm_online, text=t('ui.limit_label'), bg=C["panel"], fg=C["muted"], font=("Segoe UI", 8)).pack(side="left")
        self.var_site_limit = tk.StringVar(value="0") 
        tk.Entry(self.frm_online, textvariable=self.var_site_limit, width=6, bg=C["card"], fg=C["text"], relief="flat", insertbackground=C['text']).pack(side="left", padx=4)

        tk.Radiobutton(sec0, text=t('ui.source_local'), variable=self.var_source, value='local',
                       bg=C['panel'], fg=C['text'], selectcolor=C['card'], activebackground=C['panel'],
                       activeforeground=C['text'], font=('Segoe UI', 9), command=self._on_source_change).pack(anchor='w', pady=(8,0))
        
        self.frm_local = tk.Frame(sec0, bg=C["panel"])
        self.btn_add = _btn(self.frm_local, t('ui.add_files'), self._add_files, secondary=True)
        self.btn_add.pack(fill='x', pady=(4, 2))
        self.lb_files = tk.Listbox(self.frm_local, bg=C['card'], fg=C['text'], selectbackground=C['accent'], selectforeground='white', relief='flat', height=4, font=('Segoe UI', 8))
        self.lb_files.pack(fill='x', expand=True)
        self.btn_del = _btn(self.frm_local, t('ui.del_file'), self._del_file, secondary=True)
        self.btn_del.pack(fill='x', pady=(2, 0))
        _sep(sidebar)

        # 2. 계정 및 API 연동
        sec2 = _section(sidebar, t('ui.nickname'))
        self.var_user = tk.StringVar()
        tk.Entry(sec2, textvariable=self.var_user, bg=C['card'], fg=C['text'], insertbackground=C['text'], relief='flat', font=('Segoe UI', 9)).pack(fill='x', ipady=5, padx=2)
        _sep(sidebar)

        # Language selector
        sec_lang = _section(sidebar, '🌐 ' + t('ui.language'))
        self._lang_display = [f"{LANG_NAMES[l]} ({l})" for l in SUPPORTED_LANGS]
        self._lang_codes = list(SUPPORTED_LANGS)
        current_idx = self._lang_codes.index(get_language()) if get_language() in self._lang_codes else 0
        self.var_lang_display = tk.StringVar(value=self._lang_display[current_idx])
        lang_cb = ttk.Combobox(sec_lang, textvariable=self.var_lang_display, values=self._lang_display, state='readonly', width=18, font=('Segoe UI', 9))
        lang_cb.pack(fill='x', padx=2, ipady=4)
        lang_cb.bind('<<ComboboxSelected>>', lambda _e: self._change_language())
        _sep(sidebar)

        # 3. 프로그레스바 및 진행도 
        self.frm_progress = tk.Frame(sidebar, bg=C['panel'])
        self.frm_progress.pack(fill='x', padx=16, pady=4)
        
        self.progress_bar = ttk.Progressbar(self.frm_progress, orient='horizontal', mode='determinate', length=100)
        
        self.btn_analyze = _btn(sidebar, t('ui.btn_analyze'), self._start_analysis)
        self.btn_analyze.pack(fill='x', padx=16, pady=(4, 8))

        self.btn_profile = _btn(sidebar, t('ui.btn_profile'), self._open_profile, secondary=True)
        self.btn_profile.pack(fill='x', padx=16, pady=(0, 4))

        self.btn_report = _btn(sidebar, t('ui.btn_report'), self._open_report, secondary=True)
        self.btn_report.pack(fill='x', padx=16, pady=(0, 8))
        self.btn_report.config(state='disabled')

        log_frame = tk.Frame(sidebar, bg=C['panel'])
        log_frame.pack(fill='x', padx=16)
        self._step_labels = {}
        for step in ['collect', 'parse', 'analyze']:
            row = tk.Frame(log_frame, bg=C['panel'])
            row.pack(fill='x', pady=1)
            tk.Label(row, text=f'  {t("status." + step)}', bg=C['panel'], fg=C['muted'], font=('Segoe UI', 8), width=8, anchor='w').pack(side='left')
            lbl = tk.Label(row, text=t('status.waiting'), bg=C['panel'], fg=C['border'], font=('Segoe UI', 8))
            lbl.pack(side='left')
            self._step_labels[step] = lbl

        # 4. 우측 메인 대시보드
        main = tk.Frame(self, bg=C['bg'])
        main.pack(side='right', fill='both', expand=True)

        style = ttk.Style()
        style.theme_use('default')
        style.configure('C.TNotebook', background=C['bg'], borderwidth=0)
        style.configure('C.TNotebook.Tab', background=C['card'], foreground=C['muted'], padding=[14, 6], font=('Segoe UI', 9))
        style.map('C.TNotebook.Tab', background=[('selected', C['panel'])], foreground=[('selected', C['accent'])])

        self.nb = ttk.Notebook(main, style='C.TNotebook')
        self.nb.pack(fill='both', expand=True, padx=12, pady=12)

        self.tab_graph = tk.Frame(self.nb, bg=C['bg'])
        self.nb.add(self.tab_graph, text=t('ui.tab_graph'))
        tk.Label(self.tab_graph, text=t('ui.graph_placeholder'), bg=C['bg'], fg=C['muted'], font=('Segoe UI', 13)).pack(expand=True)

        self.tab_coach = tk.Frame(self.nb, bg=C['bg'])
        self.nb.add(self.tab_coach, text=t('ui.tab_coach'))
        _kr_ui_font = 'Malgun Gothic' if platform.system() == 'Windows' else 'Apple SD Gothic Neo' if platform.system() == 'Darwin' else 'sans-serif'
        self.txt_coach = scrolledtext.ScrolledText(self.tab_coach, bg=C['card'], fg=C['text'], font=(_kr_ui_font, 10), relief='flat', wrap='word', insertbackground=C['text'], padx=20, pady=20)
        self.txt_coach.pack(fill='both', expand=True, padx=8, pady=8)
        self.txt_coach.insert('end', t('ui.coach_placeholder'))
        self.txt_coach.config(state='disabled')

        self.tab_stats = tk.Frame(self.nb, bg=C['bg'])
        self.nb.add(self.tab_stats, text=t('ui.tab_stats'))
        self.stats_frame = tk.Frame(self.tab_stats, bg=C['bg'])
        self.stats_frame.pack(fill='both', expand=True, padx=20, pady=20)
        tk.Label(self.stats_frame, text=t('ui.stats_placeholder'), bg=C['bg'], fg=C['muted'], font=('Segoe UI', 11)).pack(expand=True)

        self.tab_roadmap = tk.Frame(self.nb, bg=C['bg'])
        self.nb.add(self.tab_roadmap, text=t('ui.tab_roadmap'))
        self.roadmap_frame = tk.Frame(self.tab_roadmap, bg=C['bg'])
        self.roadmap_frame.pack(fill='both', expand=True, padx=20, pady=20)
        self.txt_roadmap = scrolledtext.ScrolledText(
            self.roadmap_frame, bg=C['card'], fg=C['text'], font=('Segoe UI', 10),
            relief='flat', wrap='word', insertbackground=C['text'], padx=20, pady=20
        )
        self.txt_roadmap.pack(fill='both', expand=True)
        self.txt_roadmap.insert('end', t('ui.roadmap_placeholder'))
        self.txt_roadmap.config(state='disabled')

        self._on_source_change()

    def _on_source_change(self):
        if self.var_source.get() == 'online':
            self.frm_local.pack_forget()
            self.frm_online.pack(fill="x", padx=16, pady=4)
        else:
            self.frm_online.pack_forget()
            self.frm_local.pack(fill="x", pady=(4, 0))

    def _add_files(self):
        paths = filedialog.askopenfilenames(title=t('ui.file_dialog_title'), filetypes=[("TETR.IO Replay", "*.ttrm *.ttr"), ("All Files", "*.*")])
        for p in paths:
            if p not in self._files:
                self._files.append(p)
                self.lb_files.insert("end", Path(p).name)

    def _del_file(self):
        sel = self.lb_files.curselection()
        if not sel: return
        idx = sel[0]
        self._files.pop(idx)
        self.lb_files.delete(idx)

    def _change_language(self):
        display = self.var_lang_display.get()
        idx = self._lang_display.index(display) if display in self._lang_display else 0
        lang = self._lang_codes[idx]
        set_language(lang)
        self.destroy()
        app = TetrioCoachAppModern()
        app.mainloop()

    def _set_step(self, step: str, msg: str, color: str):
        # GUI 스레드 안전 호출 헬퍼
        self.after(0, lambda: self._step_labels[step].config(text=msg, fg=color))

    def _update_progress(self, current: int, total: int = None):
        def _gui_update():
            if total:
                self.progress_bar.config(mode='determinate', maximum=total, value=current)
            else:
                self.progress_bar.config(mode='indeterminate')
                self.progress_bar.step(5)
        self.after(0, _gui_update)

    def _start_analysis(self):
        source = self.var_source.get().strip()
        username_raw = self.var_user.get().strip()
        username = resolve_player_identifier(username_raw)

        if not username:
            messagebox.showwarning(t('err.input_missing.title'), t('err.input_missing.body'))
            return

        if source == 'local' and not self._files:
            messagebox.showwarning(t('err.files_missing.title'), t('err.files_missing.body'))
            return

        # UI 초기화 및 잠금
        self.btn_analyze.config(state='disabled', text=t('ui.btn_analyzing'))
        self.btn_report.config(state='disabled')
        self.progress_bar.pack(fill='x', expand=True, pady=4)
        self.progress_bar.config(value=0)

        for step in self._step_labels:
            self._set_step(step, t('status.waiting'), C['border'])

        threading.Thread(target=self._run_analysis_thread, args=(username, source), daemon=True).start()

    def _collect_online(self, username: str) -> tuple[list[dict], list[dict], list[str]]:
        raw_limit = self.var_site_limit.get().strip()
        max_records = int(raw_limit) if raw_limit.isdigit() and int(raw_limit) > 0 else None

        self._set_step('collect', t('status.collecting'), C['yellow'])
        records = fetch_recent_league_records(
            username, max_records=max_records,
            ui_callback=lambda cur, tot: self._update_progress(cur, tot or 100),
        )
        if not records:
            raise ValueError(t('err.no_data.body'))

        self._set_step('parse', t('status.parsing_api'), C['yellow'])
        all_rounds, match_summaries, errors = [], [], []
        for idx, record in enumerate(records, start=1):
            self._update_progress(idx, len(records))
            try:
                label = record.get('replayid') or record.get('_id') or f'recent-{idx}'
                parsed = parse_record_payload(record, fallback_username=username, source_label=label, origin='site')
                all_rounds.extend(parsed['rounds'])
                match_summaries.append(parsed.get('match_summary', {}))
            except Exception as e:
                errors.append(f"• {record.get('replayid', 'Unknown')}: {e}")
        return all_rounds, match_summaries, errors

    def _collect_local(self, username: str) -> tuple[list[dict], list[dict], list[str]]:
        self._set_step('parse', t('status.parsing_local'), C['yellow'])
        all_rounds, match_summaries, errors = [], [], []
        for idx, fp in enumerate(self._files, start=1):
            self._update_progress(idx, len(self._files))
            try:
                meta = parse_local_ttrm(fp, username)
                all_rounds.extend(meta['rounds'])
                match_summaries.append(meta.get('match_summary', {}))
            except Exception as e:
                errors.append(f'• {Path(fp).name}: {e}')
        return all_rounds, match_summaries, errors

    def _run_analysis_thread(self, username: str, source: str):
        try:
            self._set_step('collect', t('status.collecting_progress'), C['yellow'])
            self._update_progress(10, 100)

            try:
                if source == 'online':
                    all_rounds, match_summaries, parse_errors = self._collect_online(username)
                else:
                    all_rounds, match_summaries, parse_errors = self._collect_local(username)
            except ValueError as e:
                self._set_step('collect', t('status.no_data'), C['accent3'])
                self.after(0, lambda m=str(e): messagebox.showwarning(t('err.no_data.title'), m))
                return

            if parse_errors:
                err_msg = t('err.parse_warn.body', details='\n'.join(parse_errors))
                self.after(0, lambda m=err_msg: messagebox.showwarning(t('err.parse_warn.title'), m))

            if not all_rounds:
                self._set_step('collect', t('status.fail'), C['accent3'])
                self._set_step('parse', t('status.fail'), C['accent3'])
                return

            self._set_step('collect', t('status.done_matches', count=len(match_summaries)), C['green'])

            norm_user = normalize_name(username)
            my_rounds = [r for r in all_rounds if normalize_name(r.get('username', '')) == norm_user]

            if not my_rounds:
                usernames_found = sorted({r.get('username', '?') for r in all_rounds if r.get('username', '?') != '?'})
                self.after(0, lambda ul=usernames_found: messagebox.showwarning(
                    t('err.name_mismatch.title'),
                    t('err.name_mismatch.body', username=username, found=', '.join(ul)),
                ))
                self._set_step('parse', t('status.fail'), C['accent3'])
                return

            agg = compute_aggregates_v2(my_rounds)
            filenames_raw = ', '.join(sorted({r.get('match_label') or r.get('source_file') for r in my_rounds if r.get('match_label') or r.get('source_file')}))
            filenames = _summarize_source_label(filenames_raw)
            self._set_step('parse', t('status.done_rounds', count=len(my_rounds)), C['green'])

            self._update_progress(50, 100)
            my_sources = [r.get('match_label') or r.get('source_file') for r in my_rounds]
            my_boundaries = [i for i in range(1, len(my_rounds)) if my_sources[i] != my_sources[i - 1]]
            fig = make_figure(my_rounds, my_boundaries, username)
            self.after(0, lambda f=fig: self._show_graph(f))
            self.after(0, lambda a=agg: self._refresh_stats_tab(a))

            # 자체 AI 분석 (규칙 기반, LLM 불필요)
            self._set_step('analyze', t('status.analyzing'), C['yellow'])
            self._update_progress(60, 100)
            short_source = _summarize_source_label(filenames or source)

            try:
                from training.feedback_generator import generate_full_feedback
                coaching, roadmap_text = generate_full_feedback(agg, username, source_label=short_source)
            except Exception as e:
                coaching = t('err.analysis_fail', error=str(e))
                roadmap_text = build_training_roadmap_v2(agg, my_rounds, match_summaries, username, filenames or source)

            self._update_progress(85, 100)
            report_path = _write_training_report(agg, my_rounds, match_summaries, username, filenames or source, roadmap_text)
            self._last_report_path = report_path
            self._last_profile_url = f"https://ch.tetr.io/u/{urllib.parse.quote(resolve_player_identifier(username))}/league"
            self.after(0, lambda t=roadmap_text: self._show_roadmap(t))
            self.after(0, lambda: self.btn_report.config(state='normal'))
            self.after(0, lambda t=coaching: self._show_coaching(t))

            self._set_step('analyze', t('status.done'), C['green'])
            self._update_progress(100, 100)

        except Exception as e:
            self._set_step('collect', t('status.error'), C['accent3'])
            self._set_step('analyze', t('status.error'), C['accent3'])
            self.after(0, lambda err=str(e): messagebox.showerror(t('err.fatal.title'), err))
        finally:
            # 분석 버튼 활성화 및 프로그레스바 숨김 처리
            def _reset_ui():
                self.btn_analyze.config(state='normal', text=t('ui.btn_analyze'))
                self.progress_bar.pack_forget()
            self.after(0, _reset_ui)


    def _show_graph(self, fig: Figure | None):
        for w in self.tab_graph.winfo_children(): w.destroy()
        if fig is None or not MATPLOTLIB_AVAILABLE:
            tk.Label(
                self.tab_graph,
                text=t('err.no_graph'),
                bg=C['bg'], fg=C['muted'], font=('Segoe UI', 12)
            ).pack(expand=True)
            return
        canvas = FigureCanvasTkAgg(fig, master=self.tab_graph)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    def _show_coaching(self, text: str):
        self.txt_coach.config(state="normal")
        self.txt_coach.delete("1.0", tk.END)
        self.txt_coach.insert("end", text)
        self.txt_coach.config(state="disabled")
        self.nb.select(self.tab_coach)

    def _show_roadmap(self, text: str):
        self.txt_roadmap.config(state="normal")
        self.txt_roadmap.delete("1.0", tk.END)
        self.txt_roadmap.insert("end", text)
        self.txt_roadmap.config(state="disabled")
        self.nb.select(self.tab_roadmap)

    def _open_profile(self):
        username_raw = self.var_user.get().strip()
        username = resolve_player_identifier(username_raw)
        if not username:
            messagebox.showwarning(t('err.input_needed.title'), t('err.input_needed.body'))
            return
        url = f"https://ch.tetr.io/u/{urllib.parse.quote(username)}/league"
        self._last_profile_url = url
        _open_url(url)

    def _open_report(self):
        if not self._last_report_path or not self._last_report_path.exists():
            messagebox.showinfo(t('err.report_missing.title'), t('err.report_missing.body'))
            return
        _open_url(self._last_report_path.as_uri())

    def _refresh_stats_tab(self, agg: dict):
        for w in self.stats_frame.winfo_children(): w.destroy()

        has_detail = agg.get('has_detail', False)

        # 데이터 소스 안내 배너
        banner = tk.Frame(self.stats_frame, bg=C['accent'] if has_detail else C['card'], highlightbackground=C['border'], highlightthickness=1)
        banner.pack(fill='x', pady=(0, 10))
        if has_detail:
            banner_text = t('stats.banner_local')
        else:
            banner_text = t('stats.banner_online')
        tk.Label(banner, text=banner_text, bg=banner.cget('bg'), fg=C['text'], font=('Segoe UI', 8, 'bold'), pady=6).pack()

        # 상단 요약 카드
        top = tk.Frame(self.stats_frame, bg=C['panel'], highlightbackground=C['border'], highlightthickness=1)
        top.pack(fill='x', pady=(0, 14))
        summary = [
            (t('stats.total_matches'), f"{agg.get('matches', 0)}", C['accent2']),
            (t('stats.total_rounds'), f"{agg.get('rounds', agg.get('games', 0))}", C['green']),
            (t('stats.round_winrate'), f"{agg.get('round_win_rate', agg.get('win_rate', 0))}%", C['accent']),
            ('APM', str(agg.get('avg_apm', 0)), C['yellow']),
            ('PPS', str(agg.get('avg_pps', 0)), C['blue']),
        ]
        for col, (label, val, color) in enumerate(summary):
            f = tk.Frame(top, bg=C['panel'])
            f.grid(row=0, column=col, padx=16, pady=10, sticky='ew')
            top.columnconfigure(col, weight=1)
            tk.Label(f, text=label, bg=C['panel'], fg=C['muted'], font=('Segoe UI', 8)).pack()
            tk.Label(f, text=val, bg=C['panel'], fg=color, font=('Segoe UI', 18, 'bold')).pack()

        # 공통 통계 (온라인/로컬 모두 표시)
        common_detail = [
            (t('stats.match_record'), t('stats.wins_losses', wins=agg.get('match_wins', 0), losses=agg.get('match_losses', 0), draws=agg.get('match_draws', 0))),
            (t('stats.round_record'), t('stats.round_wl', wins=agg.get('wins', 0), losses=agg.get('losses', 0))),
            (t('stats.avg_attack'), f"{agg.get('avg_garbage_sent', 0)}L"),
            (t('stats.avg_recv'), f"{agg.get('avg_garbage_recv', 0)}L"),
            (t('stats.avg_vs'), f"{agg.get('avg_vs', 0)}"),
            (t('stats.apm_trend'), agg.get('apm_trend', '-')),
            (t('stats.pps_trend'), agg.get('pps_trend', '-')),
        ]

        grid = tk.Frame(self.stats_frame, bg=C['bg'])
        grid.pack(fill='x')
        cols = 3
        for i, (label, val) in enumerate(common_detail):
            r, c = divmod(i, cols)
            card = tk.Frame(grid, bg=C['card'], highlightbackground=C['border'], highlightthickness=1)
            card.grid(row=r, column=c, padx=6, pady=6, sticky='nsew')
            grid.columnconfigure(c, weight=1)
            tk.Label(card, text=label, bg=C['card'], fg=C['muted'], font=('Segoe UI', 8)).pack(anchor='w', padx=10, pady=(8, 2))
            tk.Label(card, text=val, bg=C['card'], fg=C['accent'], font=('Segoe UI', 15, 'bold')).pack(anchor='w', padx=10, pady=(0, 8))

        if has_detail:
            # 상세 통계 헤더
            tk.Label(self.stats_frame, text=t('stats.detail_header'), bg=C['bg'], fg=C['accent2'], font=('Segoe UI', 9, 'bold')).pack(anchor='w', padx=6, pady=(12, 4))

            detail_items = [
                (t('stats.tspin_detail'), f"TSS {agg.get('total_tspin_single', 0)} / TSD {agg.get('total_tspin_double', 0)} / TST {agg.get('total_tspin_triple', 0)} / Mini {agg.get('total_tspin_mini', 0)}"),
                (t('stats.total_tspin'), f"{agg.get('total_tspin', 0)}  ({agg.get('tspin_rate', 0)}%)"),
                (t('stats.line_clears'), f"S{agg.get('total_singles', 0)} / D{agg.get('total_doubles', 0)} / T{agg.get('total_triples', 0)} / Q{agg.get('total_quads', 0)}"),
                (t('stats.total_lines'), str(agg.get('total_lines', 0))),
                (t('stats.perfect_clear'), str(agg.get('total_allclear', 0))),
                (t('stats.max_combo'), str(agg.get('max_combo', 0))),
                (t('stats.max_b2b'), str(agg.get('max_btb', 0))),
                (t('stats.max_spike'), f"{agg.get('max_spike', 0)}L"),
                (t('stats.finesse'), f"Fault {agg.get('total_finesse_faults', 0)} ({agg.get('finesse_fault_rate', 0)}%) / Perfect {agg.get('finesse_perfect_rate', 0)}%"),
                (t('stats.total_pieces'), str(agg.get('total_pieces', 0))),
            ]

            grid2 = tk.Frame(self.stats_frame, bg=C['bg'])
            grid2.pack(fill='both', expand=True)
            for i, (label, val) in enumerate(detail_items):
                r, c = divmod(i, cols)
                card = tk.Frame(grid2, bg=C['card'], highlightbackground=C['accent2'], highlightthickness=1)
                card.grid(row=r, column=c, padx=6, pady=6, sticky='nsew')
                grid2.columnconfigure(c, weight=1)
                tk.Label(card, text=label, bg=C['card'], fg=C['muted'], font=('Segoe UI', 8)).pack(anchor='w', padx=10, pady=(8, 2))
                tk.Label(card, text=val, bg=C['card'], fg=C['accent2'], font=('Segoe UI', 15, 'bold')).pack(anchor='w', padx=10, pady=(0, 8))

if __name__ == "__main__":
    app = TetrioCoachAppModern()
    app.mainloop()