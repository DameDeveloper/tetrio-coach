# TETR.IO AI Coach — Training Pipeline

## Phase 1: 데이터 수집 및 시뮬레이터

### 파일 구조
```
training/
├── collect_top_players.py   # 상위 랭커 전적 수집기
├── board_simulator.py       # ttrm → 보드 상태 시뮬레이터
├── build_patterns.py        # 빌드/오프닝 패턴 DB
└── data/                    # 수집된 데이터 저장 (gitignore)
```

### 사용법

#### 1. 상위 랭커 데이터 수집
```bash
python training/collect_top_players.py --top 100 --records 50
```
- `--top`: 수집할 상위 플레이어 수 (기본 100)
- `--records`: 플레이어당 수집할 매치 수 (기본 50)
- 결과: `training/data/leaderboard.json`, `training/data/match_records.json`

#### 2. ttrm 리플레이 시뮬레이션
```bash
python training/board_simulator.py <path_to_ttrm>
```
- 각 라운드/플레이어의 배치별 보드 상태 출력
- 피스 수는 정확, 라인/T-Spin 감지는 SRS 교정 필요 (Phase 2)

#### 3. 빌드 패턴 DB 확인
```bash
python training/build_patterns.py
```

### 빌드 패턴 데이터베이스
| 빌드 | 카테고리 | 공격 | 난이도 |
|------|----------|------|--------|
| TKI | 오프닝 | TSD → 이어붙이기 | 중 |
| DT Cannon | 오프닝 | TSD → TST (11라인) | 중 |
| PCO | 오프닝 | Perfect Clear (10라인) | 상 |
| STSD | 중반 | TSD | 중 |
| LST Stacking | 중반 | 연속 TSD | 상 |
| Hachispin | 오프닝 | TSS → PC | 중 |
| 4-wide | 전략 | 연속 콤보 (10+라인) | 중 |
| Downstacking | 수비 | 라인 클리어 | 중 |

### Phase 2 예정 작업
- [ ] SRS 좌표계 정밀 교정 (TETR.IO 역공학)
- [ ] Cold Clear 바인딩 통합
- [ ] 배치 정확도 평가 로직
- [ ] Kaggle 데이터셋 통합
- [ ] 빌드 패턴 보드 매칭 알고리즘 구현
