"""
Phase 3: ML 기반 약점 분류 모델

상위 랭커 데이터의 통계 특성을 기반으로 플레이어의 약점 패턴을 분류한다.
학습 데이터가 없을 때는 합성 데이터로 사전 학습된 모델을 사용한다.
"""

import json
import pickle
from pathlib import Path

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler

def _get_model_dir() -> Path:
    try:
        from _paths import get_base_dir
        return get_base_dir() / "training" / "models"
    except ImportError:
        return Path(__file__).parent / "models"

MODEL_DIR = _get_model_dir()
MODEL_PATH = MODEL_DIR / "weakness_classifier.pkl"
SCALER_PATH = MODEL_DIR / "scaler.pkl"

FEATURE_KEYS = [
    'avg_apm', 'avg_pps', 'avg_vs',
    'avg_garbage_sent', 'avg_garbage_recv',
    'tspin_rate', 'finesse_fault_rate',
    'round_win_rate',
]

WEAKNESS_LABELS = [
    'speed',       # PPS가 낮음
    'attack',      # APM/어택이 낮음
    'tspin',       # T-Spin 활용 부족
    'finesse',     # 배치 정확도 낮음
    'defense',     # 수비/다운스택 약함
    'balanced',    # 특별한 약점 없음 (균형)
]


def _generate_synthetic_data(n_samples: int = 2000) -> tuple[np.ndarray, np.ndarray]:
    """학습 데이터가 없을 때 사용할 합성 훈련 데이터 생성."""
    rng = np.random.RandomState(42)
    X = []
    y = []

    for _ in range(n_samples):
        label_idx = rng.randint(0, len(WEAKNESS_LABELS))
        label = WEAKNESS_LABELS[label_idx] if label_idx < len(WEAKNESS_LABELS) else 'balanced'

        apm = rng.normal(60, 25)
        pps = rng.normal(2.0, 0.5)
        vs = rng.normal(100, 40)
        sent = rng.normal(35, 15)
        recv = rng.normal(35, 15)
        tspin = rng.normal(3.0, 2.0)
        fault = rng.normal(20, 15)
        winrate = rng.normal(50, 15)

        if label == 'speed':
            pps = rng.normal(1.3, 0.3)
            apm = rng.normal(35, 10)
        elif label == 'attack':
            apm = rng.normal(30, 10)
            sent = rng.normal(15, 5)
        elif label == 'tspin':
            tspin = rng.normal(0.5, 0.5)
        elif label == 'finesse':
            fault = rng.normal(45, 10)
        elif label == 'defense':
            recv = sent + rng.normal(15, 5)
            winrate = rng.normal(35, 10)
        elif label == 'balanced':
            pps = rng.normal(2.2, 0.3)
            apm = rng.normal(75, 15)
            tspin = rng.normal(4.0, 1.5)
            fault = rng.normal(8, 3)
            winrate = rng.normal(55, 10)

        features = [
            max(0, apm), max(0, pps), max(0, vs),
            max(0, sent), max(0, recv),
            max(0, tspin), max(0, fault),
            np.clip(winrate, 0, 100),
        ]
        X.append(features)
        y.append(label)

    return np.array(X), np.array(y)


def train_model(X: np.ndarray = None, y: np.ndarray = None) -> tuple:
    """약점 분류 모델을 학습하고 저장한다."""
    if X is None or y is None:
        X, y = _generate_synthetic_data()

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    clf = RandomForestClassifier(
        n_estimators=100, max_depth=8,
        random_state=42, n_jobs=-1,
    )
    clf.fit(X_scaled, y)

    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    with open(MODEL_PATH, 'wb') as f:
        pickle.dump(clf, f)
    with open(SCALER_PATH, 'wb') as f:
        pickle.dump(scaler, f)

    score = clf.score(X_scaled, y)
    return clf, scaler, score


def load_model() -> tuple | None:
    """저장된 모델을 로드한다. Kaggle 학습 모델을 우선 사용."""
    kaggle_model = MODEL_DIR / "kaggle_classifier.pkl"
    kaggle_scaler = MODEL_DIR / "kaggle_scaler.pkl"
    if kaggle_model.exists() and kaggle_scaler.exists():
        try:
            with open(kaggle_model, 'rb') as f:
                clf = pickle.load(f)
            with open(kaggle_scaler, 'rb') as f:
                scaler = pickle.load(f)
            return clf, scaler
        except Exception:
            pass
    if not MODEL_PATH.exists() or not SCALER_PATH.exists():
        return None
    try:
        with open(MODEL_PATH, 'rb') as f:
            clf = pickle.load(f)
        with open(SCALER_PATH, 'rb') as f:
            scaler = pickle.load(f)
        return clf, scaler
    except Exception:
        return None


KAGGLE_FEATURE_KEYS = [
    'pps', 'apm_est', 'tspin_rate', 'quad_rate', 'lines_per_piece',
    'max_combo', 'max_btb', 'max_height', 'defense_ratio', 'rating_norm',
]


def predict_weakness(agg: dict) -> dict:
    """집계 통계에서 주요 약점을 예측한다."""
    loaded = load_model()
    if loaded is None:
        _, _, score = train_model()
        loaded = load_model()

    if loaded is None:
        return {'primary': 'balanced', 'probabilities': {}, 'confidence': 0}

    clf, scaler = loaded
    n_features = scaler.n_features_in_

    if n_features == len(KAGGLE_FEATURE_KEYS):
        pps = agg.get('avg_pps', 0)
        total_pieces = max(agg.get('total_pieces', 1), 1)
        total_rounds = max(agg.get('rounds', 1), 1)
        total_lines = agg.get('total_lines', 0)

        total_garbage_sent = agg.get('avg_garbage_sent', 0) * total_rounds
        apm_est = (total_garbage_sent / total_pieces) * 60 if total_pieces > 0 else 0

        tspin_rate_kaggle = agg.get('total_tspin', 0) / total_pieces * 100

        features = np.array([[
            pps,
            apm_est,
            tspin_rate_kaggle,
            agg.get('total_quads', 0) / total_pieces * 100,
            total_lines / total_pieces if total_pieces > 0 else 0,
            agg.get('max_combo', 0),
            agg.get('max_btb', 0),
            20,
            agg.get('avg_garbage_sent', 0) / max(agg.get('avg_garbage_recv', 1), 1),
            scaler.mean_[9] if hasattr(scaler, 'mean_') else 24.0,
        ]])
    else:
        features = np.array([[agg.get(k, 0) for k in FEATURE_KEYS]])

    X_scaled = scaler.transform(features)
    probas = clf.predict_proba(X_scaled)[0]
    classes = clf.classes_
    ml_prob = {cls: round(float(p), 3) for cls, p in zip(classes, probas)}

    rule_scores = _rule_based_scores(agg)

    combined = {}
    all_labels = set(list(ml_prob.keys()) + list(rule_scores.keys()))
    for label in all_labels:
        ml_p = ml_prob.get(label, 0)
        rule_p = rule_scores.get(label, 0)
        combined[label] = round(0.4 * ml_p + 0.6 * rule_p, 3)

    sorted_combined = sorted(combined.items(), key=lambda x: x[1], reverse=True)
    primary = sorted_combined[0][0] if sorted_combined else 'balanced'
    confidence = sorted_combined[0][1] if sorted_combined else 0

    return {
        'primary': primary,
        'probabilities': combined,
        'ml_raw': ml_prob,
        'rule_raw': rule_scores,
        'confidence': round(confidence, 3),
        'top3': [(k, v) for k, v in sorted_combined[:3]],
    }


def _rule_based_scores(agg: dict) -> dict:
    """통계 기반 약점 확률 점수 (0~1)."""
    pps = agg.get('avg_pps', 0)
    apm = agg.get('avg_apm', 0)
    tsr = agg.get('tspin_rate', 0)
    fr = agg.get('finesse_fault_rate', 0)
    sent = agg.get('avg_garbage_sent', 0)
    recv = agg.get('avg_garbage_recv', 0)
    has_detail = agg.get('has_detail', False)

    scores = {}
    scores['speed'] = max(0, min(1, (2.0 - pps) / 1.0)) if pps < 2.0 else 0
    scores['attack'] = max(0, min(1, (55 - apm) / 30)) if apm < 55 else 0
    scores['tspin'] = max(0, min(1, (2.0 - tsr) / 2.0)) if tsr < 2.0 else 0
    if has_detail:
        scores['finesse'] = max(0, min(1, (fr - 15) / 40)) if fr > 15 else 0
    else:
        scores['finesse'] = 0
    scores['defense'] = max(0, min(1, (recv - sent) / max(sent, 1) * 0.5)) if recv > sent else 0
    scores['balanced'] = max(0, 1 - max(scores.values())) if scores else 0.5

    total = sum(scores.values())
    if total > 0:
        scores = {k: round(v / total, 3) for k, v in scores.items()}

    return scores


def retrain_from_collected_data(data_path: str | Path = None):
    """수집된 상위 랭커 데이터로 모델을 재학습한다."""
    if data_path is None:
        data_path = Path(__file__).parent / "data" / "match_records.json"

    if not Path(data_path).exists():
        print("수집 데이터 없음, 합성 데이터로 학습합니다.")
        clf, scaler, score = train_model()
        print(f"합성 데이터 학습 완료: accuracy={score:.3f}")
        return

    raw = json.loads(Path(data_path).read_text(encoding='utf-8'))
    players = raw.get('players', {})

    X_list = []
    y_list = []

    for username, matches in players.items():
        if len(matches) < 5:
            continue

        apms, ppss, vss, sents, recvs = [], [], [], [], []
        for m in matches:
            for p in m.get('players', []):
                if p.get('username', '').lower() == username.lower():
                    apms.append(p.get('apm', 0))
                    ppss.append(p.get('pps', 0))
                    vss.append(p.get('vs', 0))
                    sents.append(p.get('garbage_sent', 0))
                    recvs.append(p.get('garbage_recv', 0))

        if not apms:
            continue

        avg = lambda lst: sum(lst) / len(lst) if lst else 0
        features = [
            avg(apms), avg(ppss), avg(vss),
            avg(sents), avg(recvs),
            0, 0,  # tspin_rate, fault_rate (online API에서 불가)
            50,  # win_rate 추정
        ]

        label = _infer_label(features)
        X_list.append(features)
        y_list.append(label)

    if len(X_list) < 20:
        print(f"수집 데이터 부족 ({len(X_list)}명), 합성 데이터를 보충합니다.")
        X_synth, y_synth = _generate_synthetic_data(2000 - len(X_list))
        X_list.extend(X_synth.tolist())
        y_list.extend(y_synth.tolist())

    X = np.array(X_list)
    y = np.array(y_list)
    clf, scaler, score = train_model(X, y)
    print(f"재학습 완료: {len(X_list)}샘플, accuracy={score:.3f}")


def _infer_label(features: list) -> str:
    """특성에서 약점 라벨을 규칙 기반으로 추론 (학습 데이터 라벨링용)."""
    apm, pps, vs, sent, recv, tspin, fault, wr = features
    if pps < 1.5: return 'speed'
    if apm < 40: return 'attack'
    if tspin < 1.0 and tspin > 0: return 'tspin'
    if fault > 35: return 'finesse'
    if recv > sent * 1.3 and recv > 0: return 'defense'
    return 'balanced'


if __name__ == "__main__":
    print("약점 분류 모델 학습 중...")
    clf, scaler, score = train_model()
    print(f"학습 완료: accuracy={score:.3f}")
    print(f"모델 저장: {MODEL_PATH}")

    test_agg = {
        'avg_apm': 55, 'avg_pps': 1.9, 'avg_vs': 119,
        'avg_garbage_sent': 36, 'avg_garbage_recv': 42,
        'tspin_rate': 4.3, 'finesse_fault_rate': 55.8,
        'round_win_rate': 62.5,
    }
    result = predict_weakness(test_agg)
    print(f"\n테스트 예측: {result['primary']} (confidence={result['confidence']})")
    print(f"Top 3: {result['top3']}")
