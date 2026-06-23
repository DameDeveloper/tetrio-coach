"""
Kaggle 상위 500명 리플레이 데이터셋으로 ML 모델 학습.

v2: 순환 논리 해소 — 비지도 클러스터링으로 자연 군집 도출 후
    전문가 규칙으로 라벨 매핑. SMOTE로 클래스 균형 보정.
"""

import csv
import json
import pickle
from pathlib import Path
from collections import defaultdict, Counter

import numpy as np
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, f1_score
from sklearn.cluster import KMeans

KAGGLE_CSV = Path.home() / ".cache/kagglehub/datasets/n3koasakura/tetr-io-top-players-replays/versions/1/data.csv"
MODEL_DIR = Path(__file__).parent / "models"

FEATURE_NAMES = [
    'pps', 'apm_est', 'tspin_rate', 'quad_rate', 'lines_per_piece',
    'max_combo', 'max_btb', 'max_height', 'defense_ratio', 'rating_norm',
]

WEAKNESS_LABELS = ['speed', 'attack', 'tspin', 'finesse', 'defense', 'balanced']


def aggregate_games(csv_path=KAGGLE_CSV, max_games: int = 0) -> list[dict]:
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
                    'game_id': gid, 'won': int(row['won']),
                    'rating': float(row['rating']), 'glicko': float(row['glicko']),
                    'pieces': 0, 'lines_cleared': 0,
                    'tspins': 0, 'tspin_singles': 0, 'tspin_doubles': 0,
                    'tspin_triples': 0, 'tspin_minis': 0,
                    'quads': 0, 'triples': 0, 'doubles': 0, 'singles': 0,
                    'total_attack': 0, 'max_combo': 0, 'max_btb': 0,
                    'total_garbage_cleared': 0, 'total_incoming': 0,
                    'max_height': 0, 'total_duration_subframes': 0,
                }
            g = games[gid]
            g['pieces'] += 1
            cleared = int(row['cleared'])
            g['lines_cleared'] += cleared
            tspin = row['t_spin']
            if tspin == 'S': g['tspins'] += 1; g['tspin_singles'] += 1
            elif tspin == 'D': g['tspins'] += 1; g['tspin_doubles'] += 1
            elif tspin == 'T': g['tspins'] += 1; g['tspin_triples'] += 1
            elif tspin == 'M': g['tspins'] += 1; g['tspin_minis'] += 1
            if cleared == 4: g['quads'] += 1
            elif cleared == 3 and tspin == 'N': g['triples'] += 1
            elif cleared == 2 and tspin == 'N': g['doubles'] += 1
            elif cleared == 1 and tspin == 'N': g['singles'] += 1
            g['total_attack'] += int(row['attack'])
            g['max_combo'] = max(g['max_combo'], int(row['combo']))
            g['max_btb'] = max(g['max_btb'], int(row['btb']))
            g['total_garbage_cleared'] += int(row['garbage_cleared'])
            g['total_incoming'] += int(row['incoming_garbage'])
            pf = row['playfield']
            if pf:
                height = len(pf) // 10 + (1 if len(pf) % 10 else 0)
                g['max_height'] = max(g['max_height'], height)
            g['total_duration_subframes'] = max(g['total_duration_subframes'], int(row['subframe']))
            if row_count % 500000 == 0:
                print(f"  {row_count} rows, {len(games)} games...")

    print(f"완료: {row_count} rows -> {len(games)} games")
    return list(games.values())


def extract_features_from_game(g: dict) -> list[float]:
    pcs = max(g['pieces'], 1)
    duration_s = g['total_duration_subframes'] / 600 if g['total_duration_subframes'] > 0 else 60
    pps = pcs / max(duration_s, 1)
    attack_per_piece = g['total_attack'] / pcs
    tspin_rate = g['tspins'] / pcs * 100
    quad_rate = g['quads'] / pcs * 100
    lines_per_piece = g['lines_cleared'] / pcs
    defense_ratio = g['total_garbage_cleared'] / max(g['total_incoming'], 1)
    return [
        pps, attack_per_piece * 60, tspin_rate, quad_rate, lines_per_piece,
        g['max_combo'], g['max_btb'], g['max_height'],
        defense_ratio, g['rating'] / 1000,
    ]


def _cluster_and_label(X: np.ndarray, n_clusters: int = 8) -> tuple[np.ndarray, dict]:
    """비지도 클러스터링으로 자연 군집을 도출한 뒤, 군집 특성의 상대적 위치로 라벨 매핑."""
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    km = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    clusters = km.fit_predict(X_scaled)

    cluster_profiles = {}
    for c in range(n_clusters):
        mask = clusters == c
        if mask.sum() == 0:
            continue
        means = X[mask].mean(axis=0)
        cluster_profiles[c] = {n: round(float(v), 3) for n, v in zip(FEATURE_NAMES, means)}

    global_mean = {n: round(float(v), 3) for n, v in zip(FEATURE_NAMES, X.mean(axis=0))}

    label_map = {}
    for c, p in cluster_profiles.items():
        gm = global_mean
        pps_z = (p['pps'] - gm['pps']) / max(X[:, 0].std(), 0.01)
        apm_z = (p['apm_est'] - gm['apm_est']) / max(X[:, 1].std(), 0.01)
        ts_z = (p['tspin_rate'] - gm['tspin_rate']) / max(X[:, 2].std(), 0.01)
        lpp_z = (p['lines_per_piece'] - gm['lines_per_piece']) / max(X[:, 4].std(), 0.01)
        height_z = (p['max_height'] - gm['max_height']) / max(X[:, 7].std(), 0.01)

        scores = {
            'speed': -pps_z * 2,
            'attack': -apm_z * 1.5 + (-lpp_z * 0.5),
            'tspin': -ts_z * 2,
            'defense': height_z * 1.5 + (-lpp_z * 0.5),
            'balanced': -(abs(pps_z) + abs(apm_z) + abs(ts_z)) * 0.5,
        }
        label_map[c] = max(scores, key=scores.get)

    labels = np.array([label_map.get(c, 'balanced') for c in clusters])
    return labels, cluster_profiles


def _oversample_minority(X: np.ndarray, y: np.ndarray, min_ratio: float = 0.15) -> tuple[np.ndarray, np.ndarray]:
    """소수 클래스를 오버샘플링하여 최소 비율 보장 (SMOTE 대용, 의존성 없이)."""
    counts = Counter(y)
    max_count = max(counts.values())
    target_min = int(max_count * min_ratio)

    X_new, y_new = list(X), list(y)
    rng = np.random.RandomState(42)

    for cls, cnt in counts.items():
        if cnt >= target_min:
            continue
        mask = y == cls
        X_cls = X[mask]
        n_needed = target_min - cnt
        for _ in range(n_needed):
            idx = rng.randint(0, len(X_cls))
            noise = rng.normal(0, 0.1, X_cls.shape[1])
            X_new.append(X_cls[idx] + noise)
            y_new.append(cls)

    return np.array(X_new), np.array(y_new)


def train(max_games: int = 30000):
    games = aggregate_games(max_games=max_games)
    if not games:
        print("데이터 없음"); return

    X = np.array([extract_features_from_game(g) for g in games])

    # Step 1: 비지도 클러스터링으로 자연 군집 도출
    print("\n[Step 1] K-Means 클러스터링 (k=6)...")
    y_cluster, cluster_profiles = _cluster_and_label(X, n_clusters=6)
    print(f"클러스터 라벨 분포: {dict(Counter(y_cluster))}")
    print("클러스터 프로필:")
    for c, p in sorted(cluster_profiles.items()):
        mapped = None
        for cls, mask_c in zip(*np.unique(y_cluster, return_inverse=True)):
            pass
        print(f"  C{c}: PPS={p['pps']:.2f} APM={p['apm_est']:.1f} TS={p['tspin_rate']:.2f} Def={p['defense_ratio']:.2f}")

    # Step 2: 클래스 균형 보정 (오버샘플링)
    print("\n[Step 2] 소수 클래스 오버샘플링...")
    X_balanced, y_balanced = _oversample_minority(X, y_cluster, min_ratio=0.10)
    print(f"보정 후 분포: {dict(Counter(y_balanced))}")

    # Step 3: 학습
    print("\n[Step 3] GradientBoosting 학습...")
    X_train, X_test, y_train, y_test = train_test_split(
        X_balanced, y_balanced, test_size=0.2, random_state=42, stratify=y_balanced)

    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train)
    X_test_s = scaler.transform(X_test)

    clf = GradientBoostingClassifier(
        n_estimators=200, max_depth=6, learning_rate=0.1, random_state=42)
    clf.fit(X_train_s, y_train)

    y_pred = clf.predict(X_test_s)
    macro_f1 = f1_score(y_test, y_pred, average='macro')
    weighted_f1 = f1_score(y_test, y_pred, average='weighted')
    accuracy = clf.score(X_test_s, y_test)

    print(f"\nAccuracy: {accuracy:.3f}")
    print(f"Macro F1: {macro_f1:.3f}")
    print(f"Weighted F1: {weighted_f1:.3f}")
    print(f"\n{classification_report(y_test, y_pred)}")

    # Step 4: 5-Fold Cross Validation
    print("[Step 4] 5-Fold CV...")
    X_all_s = scaler.transform(X_balanced)
    cv_scores = cross_val_score(clf, X_all_s, y_balanced, cv=5, scoring='f1_macro')
    print(f"CV Macro F1: {cv_scores.mean():.3f} (+/- {cv_scores.std():.3f})")

    # Feature importance
    print("\nFeature importance:")
    for name, imp in sorted(zip(FEATURE_NAMES, clf.feature_importances_), key=lambda x: -x[1]):
        print(f"  {name:20s}: {imp:.3f}")

    # 저장
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    with open(MODEL_DIR / "kaggle_classifier.pkl", 'wb') as f:
        pickle.dump(clf, f)
    with open(MODEL_DIR / "kaggle_scaler.pkl", 'wb') as f:
        pickle.dump(scaler, f)

    # 티어별 벤치마크
    tier_stats = defaultdict(list)
    for g in games:
        tier = _tier_from_rating(g['rating'])
        tier_stats[tier].append(extract_features_from_game(g))
    tier_benchmarks = {}
    for tier, fl in tier_stats.items():
        arr = np.array(fl)
        tier_benchmarks[tier] = {
            'count': len(arr),
            'mean': {n: round(float(v), 3) for n, v in zip(FEATURE_NAMES, arr.mean(axis=0))},
            'std': {n: round(float(v), 3) for n, v in zip(FEATURE_NAMES, arr.std(axis=0))},
            'p25': {n: round(float(v), 3) for n, v in zip(FEATURE_NAMES, np.percentile(arr, 25, axis=0))},
            'p75': {n: round(float(v), 3) for n, v in zip(FEATURE_NAMES, np.percentile(arr, 75, axis=0))},
        }
    with open(MODEL_DIR / "tier_benchmarks.json", 'w', encoding='utf-8') as f:
        json.dump(tier_benchmarks, f, ensure_ascii=False, indent=2)

    # 메타데이터 저장
    meta = {
        'accuracy': round(accuracy, 4),
        'macro_f1': round(macro_f1, 4),
        'weighted_f1': round(weighted_f1, 4),
        'cv_macro_f1_mean': round(float(cv_scores.mean()), 4),
        'cv_macro_f1_std': round(float(cv_scores.std()), 4),
        'label_method': 'kmeans_clustering_with_profile_mapping',
        'n_clusters': 6,
        'oversampling': 'noise_injection_min_ratio_0.10',
        'class_distribution': dict(Counter(y_balanced)),
        'n_train': len(X_train), 'n_test': len(X_test),
    }
    with open(MODEL_DIR / "training_meta.json", 'w', encoding='utf-8') as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

    print(f"\n모델 저장 완료: {MODEL_DIR}")


RATING_TIERS = [
    (23000, 'X+'), (21000, 'X'), (19000, 'U'), (17000, 'SS'),
    (15000, 'S+'), (13000, 'S'), (11000, 'A+'), (9000, 'A'),
    (7000, 'B+'), (5000, 'B'), (0, 'C'),
]

def _tier_from_rating(rating: float) -> str:
    for threshold, tier in RATING_TIERS:
        if rating >= threshold: return tier
    return 'C'


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--max-games', type=int, default=30000)
    args = parser.parse_args()
    train(max_games=args.max_games)
