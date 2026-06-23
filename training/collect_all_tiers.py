"""
Collect ~100 random players per rank tier from the TETR.IO league leaderboard.

Addresses the data-mismatch limitation: the placement-level ML classifier is
trained on top-500 (Kaggle) data, but the evaluation/feedback layer needs
all-tier statistical benchmarks so that players are assessed against the norms
of their own tier rather than absolute thresholds.

Output: training/data/all_tier_players.json and training/models/tier_benchmarks_all.json
"""

import json
import time
import random
import urllib.request
import urllib.parse
from pathlib import Path
from collections import defaultdict

import numpy as np

API = "https://ch.tetr.io/api"
DATA_DIR = Path(__file__).parent / "data"
MODEL_DIR = Path(__file__).parent / "models"

# Target ranks (TETR.IO letter ranks) to sample, mapped to the paper's 11 tiers.
TARGET_RANKS = ['x+', 'x', 'u', 'ss', 's+', 's', 'a+', 'a', 'b+', 'b', 'c']
PER_TIER = 100
PAGE_LIMIT = 100
MAX_PAGES = 700
SLEEP = 0.22


def api_get(path, params=None):
    url = f"{API}{path}"
    if params:
        url += '?' + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={
        'Accept': 'application/json', 'User-Agent': 'TetrioCoachTrainer/1.0'})
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.loads(resp.read().decode('utf-8')).get('data', {})


def _save_partial(buckets):
    """Save raw buckets incrementally so an interrupted run still yields data."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    (DATA_DIR / "all_tier_raw.json").write_text(
        json.dumps({r: buckets[r] for r in TARGET_RANKS}, ensure_ascii=False), encoding='utf-8')


def collect():
    buckets = defaultdict(list)
    cursor = None
    last_tr = None

    for page in range(MAX_PAGES):
        params = {'limit': PAGE_LIMIT}
        if cursor:
            params['after'] = cursor
        try:
            data = api_get('/users/by/league', params)
        except Exception as e:
            print(f"  page {page} error: {e}; retrying...")
            time.sleep(2)
            continue

        entries = data.get('entries', [])
        if not entries:
            break

        for e in entries:
            lg = e.get('league', {})
            rank = (lg.get('rank') or '').lower()
            if rank in TARGET_RANKS and len(buckets[rank]) < PER_TIER * 3:
                buckets[rank].append({
                    'username': e.get('username', ''),
                    'rank': rank,
                    'tr': round(lg.get('tr', 0), 1),
                    'apm': round(lg.get('apm', 0) or 0, 2),
                    'pps': round(lg.get('pps', 0) or 0, 2),
                    'vs': round(lg.get('vs', 0) or 0, 2),
                    'gamesplayed': lg.get('gamesplayed', 0),
                    'gameswon': lg.get('gameswon', 0),
                    'glicko': round(lg.get('glicko', 0) or 0, 1),
                })
            last_tr = lg.get('tr', last_tr)

        p = entries[-1].get('p')
        if not isinstance(p, dict):
            break
        cursor = f"{p.get('pri')}:{p.get('sec')}:{p.get('ter')}"

        # Stop once every target rank has enough candidates
        if all(len(buckets[r]) >= PER_TIER for r in TARGET_RANKS):
            print(f"  all tiers filled by page {page}")
            break

        if page % 20 == 0:
            counts = {r: len(buckets[r]) for r in TARGET_RANKS}
            print(f"  page {page}: TR~{last_tr:.0f} {counts}")
            _save_partial(buckets)  # incremental save so data is never lost
        time.sleep(SLEEP)

    # Random-sample 100 per tier
    random.seed(42)
    sampled = {}
    for r in TARGET_RANKS:
        pool = buckets[r]
        sampled[r] = random.sample(pool, min(PER_TIER, len(pool))) if pool else []

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    (DATA_DIR / "all_tier_players.json").write_text(
        json.dumps(sampled, ensure_ascii=False, indent=1), encoding='utf-8')

    # Build benchmarks per tier
    benchmarks = {}
    for r in TARGET_RANKS:
        ps = sampled[r]
        if not ps:
            continue
        apm = np.array([p['apm'] for p in ps])
        pps = np.array([p['pps'] for p in ps])
        vs = np.array([p['vs'] for p in ps])
        tr = np.array([p['tr'] for p in ps])
        wr = np.array([p['gameswon'] / max(p['gamesplayed'], 1) * 100 for p in ps])
        def stat(a):
            return {'mean': round(float(a.mean()), 2), 'std': round(float(a.std()), 2),
                    'p25': round(float(np.percentile(a, 25)), 2), 'p50': round(float(np.percentile(a, 50)), 2),
                    'p75': round(float(np.percentile(a, 75)), 2)}
        benchmarks[r.upper()] = {
            'n': len(ps), 'tr': stat(tr), 'apm': stat(apm),
            'pps': stat(pps), 'vs': stat(vs), 'winrate': stat(wr),
        }

    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    (MODEL_DIR / "tier_benchmarks_all.json").write_text(
        json.dumps(benchmarks, ensure_ascii=False, indent=2), encoding='utf-8')

    print("\n=== Per-tier benchmarks (n, TR, APM, PPS, VS, Win%) ===")
    for r in TARGET_RANKS:
        b = benchmarks.get(r.upper())
        if not b:
            print(f"  {r.upper()}: no data")
            continue
        print(f"  {r.upper():3s}: n={b['n']:3d} TR={b['tr']['mean']:7.0f} APM={b['apm']['mean']:6.1f} "
              f"PPS={b['pps']['mean']:4.2f} VS={b['vs']['mean']:6.1f} Win={b['winrate']['mean']:.1f}%")

    total = sum(len(v) for v in sampled.values())
    print(f"\nTotal sampled: {total} players across {len([r for r in TARGET_RANKS if sampled[r]])} tiers")


if __name__ == "__main__":
    collect()
