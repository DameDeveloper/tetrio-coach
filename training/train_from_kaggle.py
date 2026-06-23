"""
Kaggle 상위 500명 리플레이 데이터셋으로 ML 모델 학습.

데이터셋: n3koasakura/tetr-io-top-players-replays
- 7.7M rows, 각 row = 1 피스 배치
- 배치별: 보드상태, T-Spin, 콤보, B2B, 가비지, 공격력, rating
"""

import csv
import json
import pickle
from pathlib import Path
from collections import defaultdict

import numpy as np
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report

KAGGLE_CSV = Path.home() / ".cache/kagglehub/datasets/n3koasakura/tetr-io-top-players-replays/versions/1/data.csv"
MODEL_DIR = Path(__file__).parent / "models"

RATING_TIERS = [
    (23000, 'X+'), (21000, 'X'), (19000, 'U'), (17000, 'SS'),
    (15000, 'S+'), (13000, 'S'), (11000, 'A+'), (9000, 'A'),
    (7000, 'B+'), (5000, 'B'), (0, 'C'),
]

WEAKNESS_LABELS = ['speed', 'attack', 'tspin', 'finesse', 'defense', 'balanced']


def _tier_from_rating(rating: float) -> str:
    for threshold, tier in RATING_TIERS:
        if rating >= threshold:
            return tier
    return 'C'


def aggregate_games(csv_path: str | Path = KAGGLE_CSV, max_games: int = 0) -> list[dict]:
    """CSV에서 게임별 통계를 집계한다."""
    print(f"CSV 로딩: {csv_path}")
    games: dict[int, dict] = {}
    row_count = 0

    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            row_count += 1
            gid = int(row['game_id'])

            if gid not in games:
                if max_games and len(games) >= max_games:
                    break
                games[gid] = {
                    'game_id': gid,
                    'won': int(row['won']),
                    'rating': float(row['rating']),
                    'glicko': float(row['glicko']),
                    'pieces': 0,
                    'lines_cleared': 0,
                    'tspins': 0, 'tspin_singles': 0, 'tspin_doubles': 0, 'tspin_triples': 0, 'tspin_minis': 0,
                    'quads': 0, 'triples': 0, 'doubles': 0, 'singles': 0,
                    'total_attack': 0,
                    'max_combo': 0, 'max_btb': 0,
                    'total_garbage_cleared': 0,
                    'total_incoming': 0,
                    'max_height': 0,
                    'total_duration_subframes': 0,
                }

            g = games[gid]
            g['pieces'] += 1

            cleared = int(row['cleared'])
            g['lines_cleared'] += cleared
            tspin = row['t_spin']
            if tspin == 'S':
                g['tspins'] += 1; g['tspin_singles'] += 1
            elif tspin == 'D':
                g['tspins'] += 1; g['tspin_doubles'] += 1
            elif tspin == 'T':
                g['tspins'] += 1; g['tspin_triples'] += 1
            elif tspin == 'M':
                g['tspins'] += 1; g['tspin_minis'] += 1

            if cleared == 4: g['quads'] += 1
            elif cleared == 3 and tspin == 'N': g['triples'] += 1
            elif cleared == 2 and tspin == 'N': g['doubles'] += 1
            elif cleared == 1 and tspin == 'N': g['singles'] += 1

            g['total_attack'] += int(row['attack'])
            combo = int(row['combo'])
            btb = int(row['btb'])
            g['max_combo'] = max(g['max_combo'], combo)
            g['max_btb'] = max(g['max_btb'], btb)
            g['total_garbage_cleared'] += int(row['garbage_cleared'])
            g['total_incoming'] += int(row['incoming_garbage'])

            pf = row['playfield']
            if pf:
                height = len(pf) // 10 + (1 if len(pf) % 10 else 0)
                g['max_height'] = max(g['max_height'], height)

            g['total_duration_subframes'] = max(g['total_duration_subframes'], int(row['subframe']))

            if row_count % 500000 == 0:
                print(f"  {row_count} rows, {len(games)} games...")

    print(f"완료: {row_count} rows → {len(games)} games")
    return list(games.values())


def extract_features_from_game(g: dict) -> list[float]:
    """게임 통계에서 학습용 특성 벡터 추출."""
    pcs = max(g['pieces'], 1)
    duration_s = g['total_duration_subframes'] / 600 if g['total_duration_subframes'] > 0 else 60

    pps = pcs / max(duration_s, 1)
    attack_per_piece = g['total_attack'] / pcs
    tspin_rate = g['tspins'] / pcs * 100
    quad_rate = g['quads'] / pcs * 100
    lines_per_piece = g['lines_cleared'] / pcs
    defense_ratio = g['total_garbage_cleared'] / max(g['total_incoming'], 1)

    return [
        pps,
        attack_per_piece * 60,   # APM 추정
        tspin_rate,
        quad_rate,
        lines_per_piece,
        g['max_combo'],
        g['max_btb'],
        g['max_height'],
        defense_ratio,
        g['rating'] / 1000,      # 정규화된 rating
    ]


FEATURE_NAMES = [
    'pps', 'apm_est', 'tspin_rate', 'quad_rate', 'lines_per_piece',
    'max_combo', 'max_btb', 'max_height', 'defense_ratio', 'rating_norm',
]


def _label_game(g: dict) -> str:
    """게임 통계에서 주요 약점 라벨 추론."""
    pcs = max(g['pieces'], 1)
    dur = g['total_duration_subframes'] / 600 if g['total_duration_subframes'] > 0 else 60
    pps = pcs / max(dur, 1)
    tspin_rate = g['tspins'] / pcs * 100
    attack_rate = g['total_attack'] / pcs
    defense_ratio = g['total_garbage_cleared'] / max(g['total_incoming'], 1)

    if pps < 1.2: return 'speed'
    if attack_rate < 0.3: return 'attack'
    if tspin_rate < 0.5: return 'tspin'
    if defense_ratio < 0.5 and g['total_incoming'] > 10: return 'defense'
    return 'balanced'


def train(max_games: int = 30000):
    """Kaggle 데이터로 모델 학습."""
    games = aggregate_games(max_games=max_games)
    if not games:
        print("데이터 없음")
        return

    X, y = [], []
    for g in games:
        features = extract_features_from_game(g)
        label = _label_game(g)
        X.append(features)
        y.append(label)

    X = np.array(X)
    y = np.array(y)

    print(f"\n학습 데이터: {len(X)} games")
    from collections import Counter
    print(f"라벨 분포: {dict(Counter(y))}")

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train)
    X_test_s = scaler.transform(X_test)

    clf = GradientBoostingClassifier(
        n_estimators=200, max_depth=6, learning_rate=0.1,
        random_state=42,
    )
    print("GradientBoosting 학습 중...")
    clf.fit(X_train_s, y_train)

    train_score = clf.score(X_train_s, y_train)
    test_score = clf.score(X_test_s, y_test)
    print(f"Train accuracy: {train_score:.3f}")
    print(f"Test accuracy:  {test_score:.3f}")
    print(f"\n{classification_report(y_test, clf.predict(X_test_s))}")

    # Feature importance
    print("Feature importance:")
    for name, imp in sorted(zip(FEATURE_NAMES, clf.feature_importances_), key=lambda x: -x[1]):
        print(f"  {name:20s}: {imp:.3f}")

    # 저장
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    with open(MODEL_DIR / "kaggle_classifier.pkl", 'wb') as f:
        pickle.dump(clf, f)
    with open(MODEL_DIR / "kaggle_scaler.pkl", 'wb') as f:
        pickle.dump(scaler, f)

    # 티어별 통계도 저장
    tier_stats = defaultdict(list)
    for g in games:
        tier = _tier_from_rating(g['rating'])
        features = extract_features_from_game(g)
        tier_stats[tier].append(features)

    tier_benchmarks = {}
    for tier, feature_lists in tier_stats.items():
        arr = np.array(feature_lists)
        tier_benchmarks[tier] = {
            'count': len(arr),
            'mean': {n: round(float(v), 3) for n, v in zip(FEATURE_NAMES, arr.mean(axis=0))},
            'std': {n: round(float(v), 3) for n, v in zip(FEATURE_NAMES, arr.std(axis=0))},
            'p25': {n: round(float(v), 3) for n, v in zip(FEATURE_NAMES, np.percentile(arr, 25, axis=0))},
            'p75': {n: round(float(v), 3) for n, v in zip(FEATURE_NAMES, np.percentile(arr, 75, axis=0))},
        }

    with open(MODEL_DIR / "tier_benchmarks.json", 'w', encoding='utf-8') as f:
        json.dump(tier_benchmarks, f, ensure_ascii=False, indent=2)

    print(f"\n모델 저장 완료: {MODEL_DIR}")
    print(f"티어별 벤치마크: {list(tier_benchmarks.keys())}")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--max-games', type=int, default=30000)
    args = parser.parse_args()
    train(max_games=args.max_games)
