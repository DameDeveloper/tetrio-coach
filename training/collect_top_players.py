"""
Phase 1-A: TETR.IO 상위 랭커 데이터 수집기
- 리더보드에서 상위 N명의 유저 목록을 가져옴
- 각 유저의 최근 리그 전적(요약 통계)을 수집
- 결과를 JSON으로 저장
"""

import json
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from datetime import datetime

API_BASE = "https://ch.tetr.io/api"
API_TIMEOUT = 20
RATE_LIMIT_DELAY = 1.0
OUTPUT_DIR = Path(__file__).parent / "data"


def api_get(path: str, params: dict | None = None) -> dict:
    url = f"{API_BASE}{path}"
    if params:
        url += '?' + urllib.parse.urlencode(params, doseq=True)
    req = urllib.request.Request(url, headers={
        'Accept': 'application/json',
        'User-Agent': 'TetrioCoachTrainer/1.0',
    })
    with urllib.request.urlopen(req, timeout=API_TIMEOUT) as resp:
        data = json.loads(resp.read().decode('utf-8'))
    if not data.get('success', True):
        raise ValueError(data.get('error', 'API error'))
    return data.get('data') or {}


def fetch_leaderboard(limit: int = 100) -> list[dict]:
    print(f"리더보드 상위 {limit}명 조회 중...")
    collected = []
    cursor = None
    while len(collected) < limit:
        page_size = min(100, limit - len(collected))
        params = {'limit': page_size}
        if cursor:
            params['after'] = cursor
        data = api_get("/users/by/league", params)
        entries = data.get('entries', [])
        if not entries:
            break
        collected.extend(entries)
        print(f"  {len(collected)}/{limit} 수집됨")
        p = entries[-1].get('p')
        if not isinstance(p, dict):
            break
        cursor = f"{p.get('pri')}:{p.get('sec')}:{p.get('ter')}"
        if len(entries) < page_size:
            break
        time.sleep(RATE_LIMIT_DELAY)
    return collected[:limit]


def fetch_player_records(username: str, max_records: int = 50) -> list[dict]:
    collected = []
    cursor = None
    while len(collected) < max_records:
        page_size = min(100, max_records - len(collected))
        params = {'limit': page_size}
        if cursor:
            params['after'] = cursor
        try:
            data = api_get(
                f"/users/{urllib.parse.quote(username)}/records/league/recent",
                params,
            )
        except Exception as e:
            print(f"    {username} 전적 조회 실패: {e}")
            break

        entries = data.get('entries', [])
        if not entries:
            break
        collected.extend(entries)
        p = entries[-1].get('p') if entries else None
        if not isinstance(p, dict):
            break
        cursor = f"{p.get('pri')}:{p.get('sec')}:{p.get('ter')}"
        if len(entries) < page_size:
            break
        time.sleep(RATE_LIMIT_DELAY)
    return collected[:max_records]


def extract_player_summary(entry: dict) -> dict:
    league = entry.get('league', {})
    return {
        'username': entry.get('username', ''),
        'user_id': entry.get('_id', ''),
        'tr': league.get('tr', 0),
        'glicko': league.get('glicko', 0),
        'rd': league.get('rd', 0),
        'apm': league.get('apm', 0),
        'pps': league.get('pps', 0),
        'vs': league.get('vs', 0),
        'gamesplayed': entry.get('gamesplayed', 0),
        'gameswon': entry.get('gameswon', 0),
        'country': entry.get('country', ''),
    }


def extract_match_summary(record: dict) -> dict:
    results = record.get('results', {})
    leaderboard = results.get('leaderboard', [])
    rounds = results.get('rounds', [])
    extras = record.get('extras', {})

    players = []
    for p in leaderboard:
        if not isinstance(p, dict):
            continue
        stats = p.get('stats', {})
        players.append({
            'username': p.get('username', ''),
            'wins': p.get('wins', 0),
            'apm': round(stats.get('apm', 0), 2),
            'pps': round(stats.get('pps', 0), 2),
            'vs': round(stats.get('vsscore', 0), 2),
            'garbage_sent': stats.get('garbagesent', 0),
            'garbage_recv': stats.get('garbagereceived', 0),
        })

    round_stats = []
    for rd_idx, scoreboard in enumerate(rounds):
        if not isinstance(scoreboard, list):
            continue
        for entry in scoreboard:
            if not isinstance(entry, dict):
                continue
            s = entry.get('stats', {})
            round_stats.append({
                'round': rd_idx + 1,
                'username': entry.get('username', ''),
                'alive': entry.get('alive', False),
                'apm': round(s.get('apm', 0), 2),
                'pps': round(s.get('pps', 0), 2),
                'vs': round(s.get('vsscore', 0), 2),
                'garbage_sent': s.get('garbagesent', 0),
                'garbage_recv': s.get('garbagereceived', 0),
            })

    return {
        'replay_id': record.get('replayid', ''),
        'record_id': record.get('_id', ''),
        'ts': record.get('ts', ''),
        'result': extras.get('result') if isinstance(extras, dict) else None,
        'total_rounds': len(rounds),
        'players': players,
        'round_stats': round_stats,
    }


def collect_all(top_n: int = 100, records_per_player: int = 50):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    leaderboard = fetch_leaderboard(top_n)
    players = [extract_player_summary(e) for e in leaderboard]

    lb_path = OUTPUT_DIR / "leaderboard.json"
    lb_path.write_text(json.dumps({
        'collected_at': datetime.now().isoformat(),
        'count': len(players),
        'players': players,
    }, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"리더보드 저장: {lb_path} ({len(players)}명)")

    all_matches = {}
    for idx, player in enumerate(players, 1):
        username = player['username']
        print(f"[{idx}/{len(players)}] {username} (TR={player['tr']:.0f}) 전적 수집 중...")
        time.sleep(RATE_LIMIT_DELAY)

        records = fetch_player_records(username, max_records=records_per_player)
        if not records:
            print(f"    전적 없음, 건너뜀")
            continue

        matches = [extract_match_summary(r) for r in records]
        all_matches[username] = matches
        print(f"    {len(matches)} 매치 수집됨")

        if idx % 10 == 0:
            _save_matches(all_matches)

    _save_matches(all_matches)
    print(f"\n수집 완료: {len(all_matches)}명, 총 {sum(len(v) for v in all_matches.values())} 매치")


def _save_matches(all_matches: dict):
    path = OUTPUT_DIR / "match_records.json"
    path.write_text(json.dumps({
        'collected_at': datetime.now().isoformat(),
        'player_count': len(all_matches),
        'total_matches': sum(len(v) for v in all_matches.values()),
        'players': all_matches,
    }, ensure_ascii=False), encoding='utf-8')
    print(f"  중간 저장: {path}")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="TETR.IO 상위 랭커 데이터 수집")
    parser.add_argument('--top', type=int, default=100, help="수집할 상위 플레이어 수")
    parser.add_argument('--records', type=int, default=50, help="플레이어당 수집할 매치 수")
    args = parser.parse_args()
    collect_all(top_n=args.top, records_per_player=args.records)
