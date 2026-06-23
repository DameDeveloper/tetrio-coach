"""
Phase 3: 평가 엔진 — 통계 기반 약점 분석 + 빌드 패턴 피드백

ttrm의 results.stats(정확한 통계)와 시뮬레이터의 배치 추적을 결합하여
플레이어의 강약점을 분석하고 점수를 매긴다.
"""

from dataclasses import dataclass, field


@dataclass
class PlayerProfile:
    username: str = ''
    total_rounds: int = 0
    total_pieces: int = 0
    total_lines: int = 0
    avg_apm: float = 0
    avg_pps: float = 0
    avg_vs: float = 0
    win_rate: float = 0
    avg_garbage_sent: float = 0
    avg_garbage_recv: float = 0
    tspin_rate: float = 0
    tspin_singles: int = 0
    tspin_doubles: int = 0
    tspin_triples: int = 0
    tspin_minis: int = 0
    quad_count: int = 0
    allclear_count: int = 0
    finesse_fault_rate: float = 0
    max_combo: int = 0
    max_b2b: int = 0
    max_spike: int = 0
    data_source: str = ''


@dataclass
class WeaknessReport:
    category: str
    severity: str  # 'critical', 'major', 'minor', 'info'
    title: str
    description: str
    current_value: str
    target_value: str
    drill: str
    priority: int = 0


# 상위 랭커 기준치 (TR 20000+ 기준)
BENCHMARKS = {
    'apm': {'beginner': 30, 'intermediate': 55, 'advanced': 80, 'expert': 120},
    'pps': {'beginner': 1.2, 'intermediate': 1.8, 'advanced': 2.3, 'expert': 3.0},
    'vs': {'beginner': 50, 'intermediate': 90, 'advanced': 130, 'expert': 200},
    'tspin_rate': {'beginner': 0.5, 'intermediate': 2.0, 'advanced': 4.0, 'expert': 7.0},
    'fault_rate': {'good': 5, 'acceptable': 15, 'poor': 30, 'critical': 50},
    'quad_per_100': {'low': 2, 'medium': 5, 'high': 10, 'expert': 15},
}

SKILL_TIERS = [
    (24000, 'X+', '최상위 랭커'),
    (22000, 'X', '상위 랭커'),
    (20000, 'U', '고급'),
    (18000, 'SS', '준고급'),
    (16000, 'S+', '중상급'),
    (14000, 'S', '중급'),
    (12000, 'A+', '준중급'),
    (10000, 'A', '초중급'),
    (8000, 'B+', '초급 상위'),
    (5000, 'B', '초급'),
    (0, 'C', '입문'),
]


def classify_tier(tr: float) -> tuple[str, str]:
    for threshold, tier, label in SKILL_TIERS:
        if tr >= threshold:
            return tier, label
    return 'C', '입문'


def evaluate_profile(profile: PlayerProfile) -> list[WeaknessReport]:
    """플레이어 프로필을 분석하여 약점 리포트 생성."""
    reports: list[WeaknessReport] = []
    bm = BENCHMARKS

    # 속도 평가
    pps = profile.avg_pps
    if pps < bm['pps']['beginner']:
        reports.append(WeaknessReport(
            category='speed', severity='critical', priority=100,
            title='속도 심각 부족',
            description=f'PPS {pps}는 입문자 수준입니다. 기본적인 피스 배치 속도를 먼저 올려야 합니다.',
            current_value=f'PPS {pps}',
            target_value=f'PPS {bm["pps"]["intermediate"]}+',
            drill='40L 스프린트를 반복하세요. 목표: 2분 이내. 빠르게 놓되 정확하게 놓는 연습.',
        ))
    elif pps < bm['pps']['intermediate']:
        reports.append(WeaknessReport(
            category='speed', severity='major', priority=85,
            title='속도 향상 필요',
            description=f'PPS {pps}로 경쟁에서 속도 열세입니다.',
            current_value=f'PPS {pps}',
            target_value=f'PPS {bm["pps"]["advanced"]}',
            drill='40L 스프린트 + Blitz를 교대로. 스프린트에서 서브 1분을 목표.',
        ))

    # 공격력 평가
    apm = profile.avg_apm
    if apm < bm['apm']['beginner']:
        reports.append(WeaknessReport(
            category='attack', severity='critical', priority=95,
            title='공격력 심각 부족',
            description=f'APM {apm}은 거의 공격을 하지 못하고 있습니다.',
            current_value=f'APM {apm}',
            target_value=f'APM {bm["apm"]["intermediate"]}+',
            drill='T-Spin Double 패턴 학습 + Quad(4줄) 쌓기 연습. FOUR.lol에서 오프닝 연습.',
        ))
    elif apm < bm['apm']['intermediate']:
        reports.append(WeaknessReport(
            category='attack', severity='major', priority=80,
            title='공격 전개 약함',
            description=f'APM {apm}로 공격 효율이 낮습니다. T-Spin이나 콤보를 활용하세요.',
            current_value=f'APM {apm}',
            target_value=f'APM {bm["apm"]["advanced"]}',
            drill='TKI 또는 DT Cannon 오프닝을 익혀서 경기 초반 공격력을 확보하세요.',
        ))

    # T-Spin 활용도
    tsr = profile.tspin_rate
    if tsr < bm['tspin_rate']['beginner']:
        reports.append(WeaknessReport(
            category='tspin', severity='major', priority=75,
            title='T-Spin 미활용',
            description=f'T-Spin 비율 {tsr}%로 거의 사용하지 않고 있습니다. T-Spin은 효율적인 공격의 핵심입니다.',
            current_value=f'{tsr}%',
            target_value=f'{bm["tspin_rate"]["intermediate"]}%+',
            drill='STSD(Super T-Spin Double) 패턴부터 연습. S/Z 피스 위에 T 구멍을 만드는 형태를 익히세요.',
        ))
    elif tsr < bm['tspin_rate']['intermediate']:
        reports.append(WeaknessReport(
            category='tspin', severity='minor', priority=60,
            title='T-Spin 활용 개선 여지',
            description=f'T-Spin 비율 {tsr}%로 기본은 되지만 더 적극적으로 활용하면 공격력이 올라갑니다.',
            current_value=f'{tsr}%',
            target_value=f'{bm["tspin_rate"]["advanced"]}%+',
            drill='다운스택 시 T-Spin 기회를 의식적으로 찾아보세요. LST 스태킹 연습도 도움됩니다.',
        ))

    # Finesse (정확도)
    fr = profile.finesse_fault_rate
    if fr > bm['fault_rate']['critical']:
        reports.append(WeaknessReport(
            category='finesse', severity='critical', priority=90,
            title='배치 정확도 심각',
            description=f'Finesse Fault {fr}%로 절반 이상의 배치가 최적이 아닙니다.',
            current_value=f'{fr}%',
            target_value=f'{bm["fault_rate"]["acceptable"]}% 이하',
            drill='느린 속도에서 각 피스를 2키 이내로 배치하는 연습. Finesse 가이드를 참고하세요.',
        ))
    elif fr > bm['fault_rate']['poor']:
        reports.append(WeaknessReport(
            category='finesse', severity='major', priority=70,
            title='배치 정확도 개선 필요',
            description=f'Finesse Fault {fr}%로 불필요한 키 입력이 많습니다.',
            current_value=f'{fr}%',
            target_value=f'{bm["fault_rate"]["acceptable"]}% 이하',
            drill='각 피스의 최적 이동 경로를 외우세요. SRS 킥을 활용한 2키 배치를 연습.',
        ))

    # 수비력
    sent = profile.avg_garbage_sent
    recv = profile.avg_garbage_recv
    if recv > 0 and sent / max(recv, 1) < 0.7:
        reports.append(WeaknessReport(
            category='defense', severity='major', priority=65,
            title='수비 과다 / 공격 부족',
            description=f'어택 {sent}L vs 수신 {recv}L로 받는 쓰레기가 보내는 것보다 훨씬 많습니다.',
            current_value=f'어택 {sent}L / 수신 {recv}L',
            target_value='어택 ≥ 수신',
            drill='다운스택 효율을 높이고, 가비지를 받기 전에 선제 공격을 시도하세요.',
        ))

    # 승률
    wr = profile.win_rate
    if wr < 40 and profile.total_rounds >= 10:
        reports.append(WeaknessReport(
            category='overall', severity='minor', priority=50,
            title='승률 저조',
            description=f'승률 {wr}%로 상대에게 밀리고 있습니다.',
            current_value=f'{wr}%',
            target_value='50%+',
            drill='패배 리플레이를 복기하고 마지막 20초의 판단을 분석하세요.',
        ))

    # 빌드 활용도 (T-Spin 세부)
    if profile.tspin_doubles == 0 and profile.total_pieces > 200:
        reports.append(WeaknessReport(
            category='build', severity='major', priority=78,
            title='TSD(T-Spin Double) 미사용',
            description='가장 효율적인 공격 수단인 TSD를 사용하지 않고 있습니다.',
            current_value='TSD 0회',
            target_value='경기당 TSD 3회+',
            drill='TKI 오프닝(첫 백에서 TSD)부터 시작하세요. FOUR.lol의 TKI 가이드 참고.',
        ))

    reports.sort(key=lambda r: r.priority, reverse=True)
    return reports


def build_profile_from_agg(agg: dict, username: str = '') -> PlayerProfile:
    """compute_aggregates_v2의 결과로 PlayerProfile 생성."""
    return PlayerProfile(
        username=username,
        total_rounds=agg.get('rounds', 0),
        total_pieces=agg.get('total_pieces', 0),
        total_lines=agg.get('total_lines', 0),
        avg_apm=agg.get('avg_apm', 0),
        avg_pps=agg.get('avg_pps', 0),
        avg_vs=agg.get('avg_vs', 0),
        win_rate=agg.get('round_win_rate', 0),
        avg_garbage_sent=agg.get('avg_garbage_sent', 0),
        avg_garbage_recv=agg.get('avg_garbage_recv', 0),
        tspin_rate=agg.get('tspin_rate', 0),
        tspin_singles=agg.get('total_tspin_single', 0),
        tspin_doubles=agg.get('total_tspin_double', 0),
        tspin_triples=agg.get('total_tspin_triple', 0),
        tspin_minis=agg.get('total_tspin_mini', 0),
        quad_count=agg.get('total_quads', 0),
        allclear_count=agg.get('total_allclear', 0),
        finesse_fault_rate=agg.get('finesse_fault_rate', 0),
        max_combo=agg.get('max_combo', 0),
        max_b2b=agg.get('max_btb', 0),
        max_spike=agg.get('max_spike', 0),
        data_source='local' if agg.get('has_detail') else 'online',
    )
