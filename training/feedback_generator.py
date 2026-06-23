"""
Phase 4: 피드백 생성기 — LLM 없이 규칙 기반 코칭 텍스트 생성

평가 엔진의 WeaknessReport + 빌드 패턴 분석 결과를 조합하여
구체적이고 실행 가능한 코칭 피드백을 생성한다.
"""

from training.evaluator import (
    PlayerProfile, WeaknessReport, evaluate_profile,
    classify_tier, BENCHMARKS,
)
from training.build_patterns import (
    analyze_build_usage, get_build_info, BUILD_DATABASE,
    get_recommendations_for_tier, TIER_RECOMMENDATIONS,
)


def generate_coaching_report(profile: PlayerProfile, weaknesses: list[WeaknessReport],
                              build_analysis: list[dict] | None = None) -> str:
    """전체 코칭 리포트 생성."""
    sections = []
    tier, tier_label = classify_tier(0)

    # 1. 플레이어 요약
    sections.append(_section_summary(profile, tier_label))

    # 2. 강점 분석
    sections.append(_section_strengths(profile))

    # 3. 약점 분석 (최대 4개)
    if weaknesses:
        sections.append(_section_weaknesses(weaknesses[:4]))

    # 4. 빌드/오프닝 피드백
    if build_analysis:
        sections.append(_section_builds(build_analysis, profile))
    elif profile.data_source == 'local':
        sections.append(_section_build_suggestions(profile))

    # 5. 훈련 플랜
    sections.append(_section_training_plan(weaknesses[:3], profile))

    # 6. 한줄 총평
    sections.append(_section_verdict(profile, weaknesses))

    return '\n\n'.join(sections)


def _section_summary(p: PlayerProfile, tier_label: str) -> str:
    lines = [
        '[플레이어 분석 요약]',
        f'닉네임: {p.username}',
        f'분석 데이터: {p.total_rounds}라운드, {p.total_pieces}피스',
        f'평균 APM: {p.avg_apm} | PPS: {p.avg_pps} | VS: {p.avg_vs}',
        f'승률: {p.win_rate}%',
    ]
    if p.data_source == 'local':
        lines.append(f'T-Spin: {p.tspin_rate}% (TSD {p.tspin_doubles}회 / TST {p.tspin_triples}회)')
        lines.append(f'Quad: {p.quad_count}회 | 퍼펙트클리어: {p.allclear_count}회')
        lines.append(f'Finesse Fault: {p.finesse_fault_rate}%')
    return '\n'.join(lines)


def _section_strengths(p: PlayerProfile) -> str:
    bm = BENCHMARKS
    strengths = []

    if p.avg_pps >= bm['pps']['advanced']:
        strengths.append(f'빠른 속도 (PPS {p.avg_pps}) — 상위권 수준의 배치 속도를 보유하고 있습니다.')
    elif p.avg_pps >= bm['pps']['intermediate']:
        strengths.append(f'안정적인 속도 (PPS {p.avg_pps}) — 중급 이상의 배치 속도입니다.')

    if p.avg_apm >= bm['apm']['advanced']:
        strengths.append(f'높은 공격력 (APM {p.avg_apm}) — 적극적인 공격을 잘 전개합니다.')

    if p.tspin_rate >= bm['tspin_rate']['advanced']:
        strengths.append(f'T-Spin 활용 우수 ({p.tspin_rate}%) — T-Spin을 효과적으로 사용합니다.')

    if p.data_source == 'local' and p.finesse_fault_rate <= bm['fault_rate']['good']:
        strengths.append(f'높은 배치 정확도 (Fault {p.finesse_fault_rate}%) — 최적에 가까운 키 입력.')

    if p.avg_garbage_sent > 0 and p.avg_garbage_sent / max(p.avg_garbage_recv, 1) >= 1.3:
        strengths.append(f'공격 우세 (어택 {p.avg_garbage_sent}L > 수신 {p.avg_garbage_recv}L)')

    if p.win_rate >= 60:
        strengths.append(f'높은 승률 ({p.win_rate}%) — 전반적 실력이 상대보다 우위.')

    if not strengths:
        strengths.append('데이터가 충분히 쌓이면 강점이 표시됩니다. 더 많은 경기를 플레이하세요.')

    return '[강점]\n' + '\n'.join(f'• {s}' for s in strengths)


def _section_weaknesses(reports: list[WeaknessReport]) -> str:
    lines = ['[약점 및 개선점]']
    for i, r in enumerate(reports, 1):
        severity_icon = {'critical': '!!!', 'major': '!!', 'minor': '!', 'info': ''}[r.severity]
        lines.extend([
            f'{i}. {r.title} {severity_icon}',
            f'   현재: {r.current_value} → 목표: {r.target_value}',
            f'   {r.description}',
            f'   연습: {r.drill}',
        ])
    return '\n'.join(lines)


def _section_builds(build_analysis: list[dict], p: PlayerProfile) -> str:
    lines = ['[빌드/오프닝 분석]']
    if not build_analysis:
        lines.append('감지된 빌드 패턴이 없습니다.')
        return '\n'.join(lines)

    for ba in build_analysis:
        name = ba.get('name', '?')
        conf = ba.get('confidence', 0)
        phase = ba.get('phase', '?')
        info = get_build_info(name)
        if info:
            lines.append(f'• {info["full_name"]} (감지 확률: {conf*100:.0f}%)')
            lines.append(f'  공격: {info["attack"]} | 난이도: {info["difficulty"]}')
            lines.append(f'  강점: {info["strength"]}')
            lines.append(f'  약점: {info["weakness"]}')
        else:
            lines.append(f'• {name} ({phase}, 확률 {conf*100:.0f}%)')

    return '\n'.join(lines)


def _section_build_suggestions(p: PlayerProfile) -> str:
    lines = ['[추천 빌드/오프닝]']

    est_tier = _estimate_tier(p)
    recs = get_recommendations_for_tier(est_tier)

    if recs:
        lines.append(f'추정 티어 "{est_tier}" 기준 추천 빌드:')
        for b in recs[:4]:
            lines.append(f'  - {b["full_name"]} [{b["category"]}]')
            lines.append(f'    공격: {b["attack"]} ({b.get("output_lines", "?")}줄)')
            lines.append(f'    {b["description"][:60]}')
            if b.get('ref'):
                lines.append(f'    참고: {b["ref"]}')
        lines.append('')

    # 플레이어 수준에 맞는 구체적 조언
    if p.tspin_rate < 2:
        lines.append(f'! T-Spin 비율 {p.tspin_rate}%: TKI 오프닝부터 시작하세요. I피스가 초반에 오면 사용 가능.')
    if p.avg_apm < 60:
        lines.append(f'! APM {p.avg_apm}: DT Cannon으로 11줄 스파이크를 연습하세요.')
    if p.avg_pps >= 2.0 and p.tspin_rate < 3:
        lines.append('! 속도는 좋지만 T-Spin 부족: STSD를 중반에 반복 적용하세요.')

    return '\n'.join(lines)


import json as _json
from pathlib import Path as _Path

_TIER_BENCH_CACHE = None


def _load_tier_benchmarks() -> dict:
    """Load empirical per-tier benchmarks (1,080 players across 11 tiers)."""
    global _TIER_BENCH_CACHE
    if _TIER_BENCH_CACHE is not None:
        return _TIER_BENCH_CACHE
    path = _Path(__file__).parent / 'models' / 'tier_benchmarks_all.json'
    try:
        _TIER_BENCH_CACHE = _json.loads(path.read_text(encoding='utf-8'))
    except Exception:
        _TIER_BENCH_CACHE = {}
    return _TIER_BENCH_CACHE


# Fallback thresholds (used only if empirical benchmarks are unavailable),
# recalibrated against the collected all-tier means.
_FALLBACK_TIER_THRESHOLDS = [
    ('X+', 3.27, 169.8), ('X', 2.82, 130.8), ('U', 2.49, 107.8),
    ('SS', 2.04, 79.2), ('S+', 1.79, 57.5), ('S', 1.63, 46.4),
    ('A+', 1.37, 33.8), ('A', 1.24, 27.2), ('B+', 1.11, 20.9),
    ('B', 1.04, 18.9), ('C', 0.87, 13.0),
]


def _estimate_tier(p: PlayerProfile) -> str:
    """Estimate the player's tier by nearest-centroid match against the
    empirical per-tier means of (PPS, APM, VS) collected from the TETR.IO
    leaderboard (100 random players per tier across 11 tiers)."""
    apm = p.avg_apm
    pps = p.avg_pps
    vs = p.avg_vs

    bench = _load_tier_benchmarks()
    if bench:
        best_tier, best_dist = 'C', float('inf')
        for tier, b in bench.items():
            d_pps = (pps - b['pps']['mean']) / 0.5
            d_apm = (apm - b['apm']['mean']) / 25.0
            d_vs = (vs - b['vs']['mean']) / 60.0 if vs else 0.0
            dist = d_pps * d_pps + d_apm * d_apm + d_vs * d_vs
            if dist < best_dist:
                best_dist, best_tier = dist, tier
        return best_tier

    # Fallback: nearest centroid on (PPS, APM) using calibrated means.
    best_tier, best_dist = 'C', float('inf')
    for tier, t_pps, t_apm in _FALLBACK_TIER_THRESHOLDS:
        dist = ((pps - t_pps) / 0.5) ** 2 + ((apm - t_apm) / 25.0) ** 2
        if dist < best_dist:
            best_dist, best_tier = dist, tier
    return best_tier


def _section_training_plan(top_weaknesses: list[WeaknessReport], p: PlayerProfile) -> str:
    lines = ['[맞춤 훈련 플랜]']

    if not top_weaknesses:
        lines.extend([
            '1. (5분) 40L 스프린트 3회 — 속도 유지 및 워밍업',
            '2. (10분) T-Spin Double 패턴 반복 — 공격 효율 향상',
            '3. (5분) 실전 2판 — 배운 패턴 적용',
        ])
        return '\n'.join(lines)

    total_time = 0
    for i, w in enumerate(top_weaknesses[:3], 1):
        if w.category == 'speed':
            time = 7
            drill = '40L 스프린트 3회 + Blitz 2회로 속도 감각 올리기'
        elif w.category == 'attack':
            time = 8
            drill = 'TKI/DT Cannon 오프닝 패턴 10회 반복 + 실전 적용 2판'
        elif w.category == 'tspin':
            time = 8
            drill = 'STSD 패턴 연습 10분 → 실전에서 의식적으로 T-Spin 기회 찾기'
        elif w.category == 'finesse':
            time = 6
            drill = '느린 속도에서 각 피스 2키 배치 연습. Finesse 트레이너 활용'
        elif w.category == 'defense':
            time = 7
            drill = '가비지 5줄 상태에서 다운스택 연습 + 선제 공격 타이밍 연습'
        elif w.category == 'build':
            time = 8
            drill = w.drill
        else:
            time = 5
            drill = w.drill

        total_time += time
        lines.append(f'{i}. ({time}분) {w.title} 집중 드릴')
        lines.append(f'   {drill}')

    remaining = max(20 - total_time, 3)
    lines.append(f'{len(top_weaknesses[:3])+1}. ({remaining}분) 실전 연습 — 위 드릴에서 배운 것을 적용하며 플레이')

    return '\n'.join(lines)


def _section_verdict(p: PlayerProfile, weaknesses: list[WeaknessReport]) -> str:
    if not weaknesses:
        return f'[한줄 총평]\n전반적으로 안정적인 플레이를 보이고 있습니다. 꾸준히 경기를 하면서 감각을 유지하세요.'

    top = weaknesses[0]
    pps_level = '빠른' if p.avg_pps >= 2.0 else '보통' if p.avg_pps >= 1.5 else '느린'
    attack_level = '공격적' if p.avg_apm >= 60 else '수비적'

    verdicts = {
        'speed': f'{attack_level} 성향이지만 속도({p.avg_pps} PPS)가 발목을 잡고 있습니다. 스프린트 연습이 가장 효과적.',
        'attack': f'{pps_level} 속도를 공격으로 전환하지 못하고 있습니다. 오프닝 빌드를 익히면 APM이 크게 오릅니다.',
        'tspin': f'기본기는 있지만 T-Spin 미활용으로 공격 효율이 낮습니다. TSD 하나만 익혀도 체감 변화가 큽니다.',
        'finesse': f'속도와 공격력 이전에 배치 정확도({p.finesse_fault_rate}%)부터 잡아야 합니다. 최적 이동 경로를 외우세요.',
        'defense': f'받는 쓰레기를 감당하지 못하고 있습니다. 다운스택 효율을 높이고 선제 공격을 연습하세요.',
    }

    verdict = verdicts.get(top.category,
        f'현재 가장 시급한 문제는 "{top.title}"입니다. 이것부터 집중적으로 개선하세요.')

    return f'[한줄 총평]\n{verdict}'


def _section_matchup_advice(profile: PlayerProfile, ml_result: dict | None) -> str:
    """상대 빌드 대응 방법 + 연습해야 할 빌드 + 미흡한 점 보충 피드백."""
    lines = ['[종합 전략 조언]']

    primary = ml_result.get('primary', '') if ml_result else ''
    conf = ml_result.get('confidence', 0) if ml_result else 0

    if ml_result and conf >= 0.5:
        lines.append(f'ML 분석: 주요 약점 유형 = "{primary}" (확신도 {conf*100:.0f}%)')
        lines.append('')

    # 상대 빌드 대응법
    lines.append('상대 빌드 대응:')
    if profile.avg_pps < 2.0:
        lines.append('- 상대가 4-wide 콤보를 시작하면: 빠르게 2~3줄을 보내 콤보를 끊으세요. 속도가 부족하면 선제 TSD가 효과적.')
    else:
        lines.append('- 상대가 4-wide 콤보를 시작하면: 속도를 살려 빠르게 라인을 보내 콤보 타이밍을 끊으세요.')

    if profile.tspin_rate < 2:
        lines.append('- 상대가 T-Spin 연속 공격을 하면: 다운스택에 집중하고, Quad로 한 번에 반격하세요.')
    else:
        lines.append('- 상대가 T-Spin 연속 공격을 하면: 같은 T-Spin으로 맞대응하거나, 타이밍 차이를 노려 선제 공격.')

    lines.append('- 상대가 PCO를 시도하면: 초반 10피스에서 빠르게 2줄 이상을 보내 타이밍을 무너뜨리세요.')
    lines.append('')

    # 연습해야 할 빌드
    lines.append('연습 권장 빌드:')
    if primary == 'speed' or profile.avg_pps < 1.8:
        lines.append('- 40L 스프린트: 순수 속도 향상. 하루 10회씩 기록 경신 도전.')
        lines.append('- Blitz: 2분 내 최대 점수. 속도 + 효율 동시 훈련.')
    if primary == 'attack' or profile.avg_apm < 55:
        lines.append('- TKI 오프닝: 첫 백에서 TSD 1회 보장. 가장 실용적인 오프닝.')
        lines.append('- DT Cannon: TSD+TST 11줄 스파이크. 공격력 극대화.')
    if primary == 'tspin' or profile.tspin_rate < 2:
        lines.append('- STSD 패턴: S/Z 위에 T 구멍 → T-Spin Double. 중반 핵심 기술.')
        lines.append('- TKI → STSD 연계: 오프닝에서 중반까지 T-Spin을 이어가는 연습.')
    if primary == 'finesse' or profile.finesse_fault_rate > 30:
        lines.append('- Finesse 트레이너: 각 피스의 최적 2키 배치 경로를 외우세요.')
        lines.append('- 느린 속도 연습: DAS/ARR을 높이고 정확하게 배치하는 연습.')
    if primary == 'defense':
        lines.append('- 다운스택 연습: 가비지 10줄 상태에서 시작하여 효율적으로 제거.')
        lines.append('- Cheese Race: 쓰레기 줄 제거 속도 훈련.')
    lines.append('')

    # 미흡한 점 보충
    lines.append('핵심 개선 포인트:')
    if profile.data_source == 'local':
        if profile.finesse_fault_rate > 40:
            lines.append(f'- Finesse 정확도 {profile.finesse_fault_rate}% → 목표 15% 이하. 가장 시급한 개선점입니다.')
        if profile.tspin_doubles == 0 and profile.total_pieces > 100:
            lines.append('- TSD(T-Spin Double)를 한 번도 사용하지 않았습니다. 가장 효율적인 공격 수단을 놓치고 있습니다.')
        if profile.max_combo < 3:
            lines.append(f'- 최대 콤보 {profile.max_combo}. 콤보 연쇄를 의식적으로 시도해보세요.')
        if profile.max_b2b < 2:
            lines.append(f'- 최대 B2B {profile.max_b2b}. T-Spin과 Quad를 연속으로 사용하면 공격력이 50% 증가합니다.')
    else:
        if profile.avg_apm < 50:
            lines.append(f'- APM {profile.avg_apm}이 낮습니다. 오프닝 빌드를 하나 익히면 즉시 개선됩니다.')
        pressure = profile.avg_garbage_sent / max(profile.avg_garbage_recv, 1)
        if pressure < 0.8:
            lines.append(f'- 어택/수신 비율 {pressure:.2f}. 공격보다 방어에 치우쳐 있습니다.')

    return '\n'.join(lines)


def _generate_roadmap(profile: PlayerProfile, weaknesses: list[WeaknessReport],
                      ml_result: dict | None, source_label: str) -> str:
    """자체 AI 기반 훈련 로드맵 생성."""
    lines = [
        f'훈련 로드맵 — {profile.username}',
        f'분석 소스: {source_label}',
        '',
    ]

    # 현재 스타일 요약
    lines.append('[현재 스타일 요약]')
    est_tier = _estimate_tier(profile)
    lines.append(f'추정 티어: {est_tier}')
    lines.append(f'평균 APM {profile.avg_apm}, PPS {profile.avg_pps}, VS {profile.avg_vs}')

    style_tags = []
    if profile.avg_pps >= 2.3: style_tags.append('고속')
    elif profile.avg_pps <= 1.5: style_tags.append('저속')
    else: style_tags.append('중속')
    if profile.avg_apm >= 80: style_tags.append('공격적')
    elif profile.avg_apm < 40: style_tags.append('수비적')
    else: style_tags.append('균형형')
    if profile.tspin_rate >= 4: style_tags.append('T-Spin 활용형')
    if profile.data_source == 'local' and profile.finesse_fault_rate > 30: style_tags.append('Finesse 개선 필요')
    lines.append(f'플레이 스타일: {" / ".join(style_tags)}')

    if ml_result:
        lines.append(f'ML 약점 분석: {ml_result.get("primary", "?")} (확신도 {ml_result.get("confidence", 0)*100:.0f}%)')
    lines.append('')

    # 최우선 개선 항목
    lines.append('[최우선 개선 항목]')
    if weaknesses:
        for i, w in enumerate(weaknesses[:4], 1):
            lines.append(f'{i}. {w.title}')
            lines.append(f'   이유: {w.description}')
            lines.append(f'   현재: {w.current_value} → 목표: {w.target_value}')
            lines.append(f'   훈련: {w.drill}')
            lines.append('')
    else:
        lines.append('뚜렷한 약점이 없습니다. 현재 수준을 유지하면서 다음 티어를 목표로 하세요.')
        lines.append('')

    # 추천 빌드
    lines.append('[추천 빌드/오프닝]')
    recs = get_recommendations_for_tier(est_tier)
    for b in recs[:4]:
        lines.append(f'- {b["full_name"]}: {b["attack"]} ({b.get("output_lines", "?")}줄)')
        lines.append(f'  {b["description"][:70]}')
        if b.get('ref'):
            lines.append(f'  참고: {b["ref"]}')
    lines.append('')

    # 20분 훈련 루틴
    lines.append('[오늘의 20분 루틴]')
    if weaknesses:
        top = weaknesses[0]
        if top.category == 'speed':
            lines.extend([
                '1) 5분: 40L 스프린트 3회 — 속도 감각 워밍업',
                '2) 8분: 스프린트 기록 경신 도전 + Blitz 2회',
                '3) 5분: 실전 2판 — 속도를 의식하며 플레이',
                '4) 2분: 가장 느렸던 배치를 복기',
            ])
        elif top.category == 'attack':
            lines.extend([
                f'1) 5분: {recs[0]["name"] if recs else "TKI"} 오프닝 패턴 10회 반복',
                '2) 8분: 실전에서 오프닝 적용 연습 3판',
                '3) 5분: DT Cannon 또는 Hachispin 패턴 연습',
                '4) 2분: 공격이 잘 된 라운드 복기',
            ])
        elif top.category == 'tspin':
            lines.extend([
                '1) 5분: STSD 패턴 연습 — S/Z 위 T구멍 만들기 반복',
                '2) 7분: TKI 오프닝 → STSD 이어붙이기 연습',
                '3) 5분: 실전 2판 — T-Spin 기회를 의식적으로 찾기',
                '4) 3분: T-Spin 성공/실패 분석',
            ])
        elif top.category == 'finesse':
            lines.extend([
                '1) 5분: 느린 속도로 각 피스 최적 경로 연습',
                '2) 7분: DAS/ARR 설정 올리고 정확 배치 반복',
                '3) 5분: 40L 스프린트 — 정확도 유지하면서 속도 올리기',
                '4) 3분: Fault가 많았던 피스 유형 분석',
            ])
        elif top.category == 'defense':
            lines.extend([
                '1) 5분: 가비지 10줄 상태에서 다운스택 연습',
                '2) 7분: 실전에서 선제 공격 → 다운스택 전환 연습',
                '3) 5분: Cheese Race 모드로 쓰레기 제거 속도 훈련',
                '4) 3분: 수비 실패 라운드 복기',
            ])
        else:
            lines.extend([
                '1) 5분: 워밍업 스프린트 + 배치 감각 점검',
                '2) 7분: 약점 항목 집중 드릴',
                '3) 5분: 실전 2판',
                '4) 3분: 복기',
            ])
    else:
        lines.extend([
            '1) 5분: 40L 스프린트 워밍업',
            '2) 7분: 새로운 오프닝 패턴 학습 (추천 빌드 참고)',
            '3) 5분: 실전 적용 2판',
            '4) 3분: 복기 및 개선점 정리',
        ])
    lines.append('')

    # 권장 학습 방식
    lines.append('[권장 학습 방식]')
    if est_tier in ('C', 'B', 'B+'):
        lines.append('- 속도보다 정확도를 먼저 잡으세요. 느리더라도 정확한 배치가 기본입니다.')
        lines.append('- 6-3 스태킹으로 안정적인 Quad 쌓기를 연습하세요.')
        lines.append('- TKI 오프닝 하나만 확실히 외우면 승률이 크게 오릅니다.')
    elif est_tier in ('A', 'A+', 'S'):
        lines.append('- 오프닝 2~3개를 피스 순서에 따라 선택할 수 있도록 연습하세요.')
        lines.append('- STSD를 중반에 자연스럽게 적용하는 연습이 중요합니다.')
        lines.append('- 상대 빌드에 대한 대응 전략을 의식적으로 연습하세요.')
    else:
        lines.append('- 다양한 오프닝의 이어붙이기를 최적화하세요.')
        lines.append('- LST Stacking 등 고급 연속 T-Spin 기술을 연습하세요.')
        lines.append('- 상대의 공격 타이밍을 읽고 카운터하는 연습이 필요합니다.')

    return '\n'.join(lines)


def generate_full_feedback(agg: dict, username: str,
                            placements: list[dict] | None = None,
                            source_label: str = '') -> tuple[str, str]:
    """통합 피드백 생성. (코칭 텍스트, 로드맵 텍스트) 튜플 반환."""
    from training.evaluator import build_profile_from_agg

    profile = build_profile_from_agg(agg, username)
    weaknesses = evaluate_profile(profile)

    build_analysis = None
    if placements:
        build_analysis = analyze_build_usage(placements)

    ml_result = None
    try:
        from training.ml_model import predict_weakness
        ml_result = predict_weakness(agg)
    except Exception:
        pass

    coaching = generate_coaching_report(profile, weaknesses, build_analysis)
    matchup = _section_matchup_advice(profile, ml_result)
    coaching = coaching + '\n\n' + matchup

    roadmap = _generate_roadmap(profile, weaknesses, ml_result, source_label or username)

    return coaching, roadmap
