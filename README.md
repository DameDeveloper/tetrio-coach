# TetrioCoach: An Adaptive Tetris AI Coaching System Based on Large-Scale Replay Data Analysis

**TetrioCoach: 대규모 리플레이 데이터 기반 적응형 테트리스 AI 코칭 시스템**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)

---

## Overview

TetrioCoach is an AI-powered coaching system for competitive Tetris (TETR.IO) that automatically analyzes player replays, classifies weaknesses using machine learning, and generates personalized training feedback — all without external LLM dependencies.

### Key Features

- **ML Weakness Classifier**: GradientBoosting model trained on 61,935 real matches (7.7M placements) from top 500 players, achieving 99.6% test accuracy
- **16 Build Patterns**: Comprehensive database of competitive Tetris openers and strategies (TKI, DT Cannon, PCO, STSD, etc.) sourced from [Hard Drop Wiki](https://harddrop.com/wiki/Opener) and [FOUR.lol](https://four.lol/)
- **11-Tier Recommendation Matrix**: Rank-specific build recommendations from beginner (C) to top-level (X+)
- **Dual Data Pipeline**: Supports both online TETR.IO API (summary stats) and local `.ttrm` replay files (detailed stats including T-Spin types, line clears, finesse)
- **Self-contained Inference**: Complete feedback generation in <100ms with zero API calls

---

## System Architecture

```
L1 — DATA ACQUISITION
├── TETR.IO Public API (APM/PPS/VS/Garbage)
├── Local .ttrm Replay Files (full replay events)
├── Kaggle Dataset (7.7M placements, top 500 players)
└── Build Pattern DB (16 builds, 11 tiers)

L2 — STATISTICAL ANALYSIS
├── Aggregation Engine (30+ metrics)
├── Board Simulator (SRS + DAS/ARR replay)
├── Play Style Analyzer (speed/attack/defense tags)
└── Build Pattern Detector (TKI/DT/PCO/STSD)

L3 — AI INTELLIGENCE
├── ML Weakness Classifier (GradientBoosting, 99.6%)
├── Rule-based Evaluator (benchmark thresholds)
└── Heuristic Board Evaluator (height/holes/bumpiness)

L4 — FEEDBACK GENERATION
├── Coaching Report (8-section analysis)
├── Training Roadmap (tier-specific 20-min routines)
├── Build Advisor (counter strategies)
└── Matchup Advice (ML-driven priority)
```

---

## Installation

```bash
git clone https://github.com/DameDeveloper/tetrio-coach.git
cd tetrio-coach
pip install -r requirements.txt
```

## Quick Start

### Run the GUI Application
```bash
python tetrio_coach.py
```

### Analyze a .ttrm Replay (Python API)
```python
from tetrio_coach import parse_local_ttrm, compute_aggregates_v2
from training.feedback_generator import generate_full_feedback

result = parse_local_ttrm("replay.ttrm", "player_name")
agg = compute_aggregates_v2(result["rounds"])
coaching, roadmap = generate_full_feedback(agg, "player_name")
print(coaching)
print(roadmap)
```

### Retrain the ML Model (Optional)
```bash
pip install kagglehub
python training/train_from_kaggle.py --max-games 60000
```

---

## Pre-trained Models

Pre-trained model artifacts are included in `training/models/` for immediate use:

| File | Description | Size |
|------|-------------|------|
| `kaggle_classifier.pkl` | GradientBoosting weakness classifier trained on 20K games | 4.9 MB |
| `kaggle_scaler.pkl` | StandardScaler for feature normalization | 0.6 KB |
| `tier_benchmarks.json` | Per-tier statistics (mean, std, percentiles) | 1.2 KB |
| `weakness_classifier.pkl` | Fallback RandomForest classifier (synthetic data) | 3.3 MB |

---

## Project Structure

```
tetrio-coach/
├── tetrio_coach.py              # Main application (Tkinter GUI + parser + stats)
├── training/
│   ├── feedback_generator.py    # Coaching report & roadmap generation
│   ├── evaluator.py             # Player profiling & weakness detection
│   ├── ml_model.py              # ML classifier (predict / train)
│   ├── build_patterns.py        # 16 build patterns + tier recommendations
│   ├── board_simulator.py       # ttrm replay → board state simulator
│   ├── cold_clear_engine.py     # Cold Clear bot wrapper (optional)
│   ├── collect_top_players.py   # TETR.IO leaderboard data collector
│   ├── train_from_kaggle.py     # Kaggle dataset training pipeline
│   └── models/                  # Pre-trained model artifacts (.pkl, .json)
├── sample_replay.ttrm           # Example .ttrm replay for testing
├── requirements.txt             # Python dependencies
├── LICENSE                      # MIT License
└── README.md
```

---

## ML Model Performance

Evaluated on 4,000 test samples (stratified 80/20 split from 20,000 games):

| Class | Precision | Recall | F1-Score | Support |
|-------|-----------|--------|----------|---------|
| attack | 1.00 | 1.00 | 1.00 | 252 |
| balanced | 0.76 | 0.62 | 0.68 | 26 |
| defense | 0.99 | 1.00 | 0.99 | 1,128 |
| speed | 1.00 | 1.00 | 1.00 | 12 |
| tspin | 1.00 | 1.00 | 1.00 | 2,582 |
| **Overall** | | | **0.996** | **4,000** |

**Top feature importances**: `tspin_rate` (73.9%), `apm_est` (24.3%), `pps` (0.8%)

---

## Training Data

The ML model was trained on the [Tetr.io Top Players Replays](https://www.kaggle.com/datasets/n3koasakura/tetr-io-top-players-replays) dataset by n3koasakura (2024), containing 61,935 match replays and 7,716,524 individual piece placements from the top 500 Tetra League players. The raw dataset (1.4 GB) is not included in this repository — download from Kaggle to retrain.

---

## Citation

If you use TetrioCoach in your research, please cite:

```bibtex
@software{lee2026tetriocoach,
  author       = {Lee, ChangHo},
  title        = {{TetrioCoach}: An Adaptive Tetris {AI} Coaching System
                  Based on Large-Scale Replay Data Analysis},
  year         = {2026},
  url          = {https://github.com/DameDeveloper/tetrio-coach},
  license      = {MIT}
}
```

---

## AI Disclosure

The development of this system utilized Anthropic's Claude as an assistive tool for code implementation support, literature search, and document structuring. All research design decisions, experimental design, result interpretation, and academic claims were made solely by the author (LeeChangHo). This disclosure follows the AI usage transparency guidelines recommended by IEEE, ACM, and Nature.

---

## License

This project is licensed under the MIT License — see [LICENSE](LICENSE) for details.

## Acknowledgments

- [TETR.IO](https://tetr.io/) — Game platform and public API
- [n3koasakura](https://www.kaggle.com/datasets/n3koasakura/tetr-io-top-players-replays) — Kaggle replay dataset
- [Hard Drop Wiki](https://harddrop.com/wiki/Opener) & [FOUR.lol](https://four.lol/) — Build pattern references
- [Cold Clear](https://github.com/MinusKelvin/cold-clear) by MinusKelvin — Tetris bot engine reference
