"""
테트리스 빌드/오프닝 패턴 데이터베이스.

출처: harddrop.com/wiki/Opener, four.lol, howtotetris.com
상위 랭커들이 실전에서 사용하는 주요 빌드를 포괄적으로 수록.
"""

BUILD_DATABASE = [
    # ── 오프닝 (1st bag) ──
    {
        'name': 'TKI', 'full_name': 'TKI Opener (TKI-3)',
        'category': 'opener', 'bag': 1,
        'description': 'I피스 기반 TSD 오프닝. 가장 널리 사용되며, 첫 백에서 TSD를 보낸 후 평탄한 지형 확보.',
        'attack': 'TSD → 이어붙이기', 'output_lines': 4,
        'requirement': 'early I', 'coverage': '~50%',
        'difficulty': 'easy', 'tier': 'all',
        'strength': '빠른 첫 공격, 평탄 지형, 이어붙이기 자유',
        'weakness': 'I피스가 늦으면 사용 불가',
        'counter': 'TKI 사용 후 2nd bag에서 빠르게 공격하면 대응 가능',
        'ref': 'https://four.lol/openers/tki/',
    },
    {
        'name': 'DT Cannon', 'full_name': 'DT Cannon (Double-Triple Cannon)',
        'category': 'opener', 'bag': 2,
        'description': 'TSD+TST 연계. 2백 걸쳐 11줄 스파이크. LS/JZ 베이스.',
        'attack': 'TSD → TST', 'output_lines': 11,
        'requirement': 'early L+S or J+Z', 'coverage': '~40%',
        'difficulty': 'medium', 'tier': 'A+',
        'strength': '11줄 대량 스파이크, B2B 확보',
        'weakness': '2백 소요(느린 전개), 상대 선제공격에 취약',
        'counter': '1st bag에서 빠르게 2~4줄을 보내 DT 구축을 방해',
        'ref': 'https://four.lol/methods/dt-cannon/',
    },
    {
        'name': 'PCO', 'full_name': 'Perfect Clear Opener',
        'category': 'opener', 'bag': 1,
        'description': 'I홀드 후 첫 백에서 퍼펙트 클리어를 노림. 84.6% 확률.',
        'attack': 'Perfect Clear', 'output_lines': 10,
        'requirement': 'I hold', 'coverage': '~85%',
        'difficulty': 'hard', 'tier': 'S+',
        'strength': '10줄 대량 공격, 깨끗한 보드',
        'weakness': '실패 시 불안정 지형, 15% 확률로 실패',
        'counter': '초반 2줄만 보내면 PC 조건이 깨짐',
        'ref': 'https://four.lol/openers/pco/',
    },
    {
        'name': 'Hachispin', 'full_name': 'Hachispin (にはち砲)',
        'category': 'opener', 'bag': 1,
        'description': 'O피스 기반 TSS→TST→PC 오프닝. 높은 커버리지와 PC 연계.',
        'attack': 'TSS → TST → PC', 'output_lines': 14,
        'requirement': 'early O', 'coverage': '~70%',
        'difficulty': 'medium', 'tier': 'S',
        'strength': 'O만 있으면 사용 가능, PC 연계, 높은 공격력',
        'weakness': '암기량이 많음, TSS 시작이라 첫 공격이 약함',
        'counter': 'TSS 전에 선제공격으로 방해',
        'ref': 'https://four.lol/openers/hachispin/',
    },
    {
        'name': 'Albatross', 'full_name': 'Albatross SP (アルバトロスSP)',
        'category': 'opener', 'bag': 2,
        'description': 'Air-TSD → TST → TSD "새" 오프닝. 강력한 연쇄 공격.',
        'attack': 'Air-TSD → TST → TSD', 'output_lines': 15,
        'requirement': 'specific bag order', 'coverage': '~30%',
        'difficulty': 'hard', 'tier': 'X',
        'strength': '연속 T-Spin 3회, 극강 스파이크',
        'weakness': '커버리지 낮음, 높은 실행 난이도',
        'counter': '구축 중 선제공격이 효과적',
        'ref': 'https://four.lol/openers/albatross/',
    },
    {
        'name': 'MKO', 'full_name': 'MKO Stacking',
        'category': 'opener', 'bag': 1,
        'description': 'M자 모양 스태킹 후 다양한 T-Spin 연계. 유연한 이어붙이기.',
        'attack': 'TSD variants', 'output_lines': 4,
        'requirement': 'flexible', 'coverage': '~60%',
        'difficulty': 'medium', 'tier': 'A',
        'strength': '유연한 이어붙이기, 다양한 상황 대응',
        'weakness': '첫 공격이 느릴 수 있음',
        'counter': '빠른 선제공격으로 스태킹 방해',
        'ref': 'https://harddrop.com/wiki/MKO_Stacking',
    },
    {
        'name': 'C-Spin', 'full_name': 'C-Spin',
        'category': 'opener', 'bag': 2,
        'description': 'TST → TSD 연계. DT Cannon의 변형.',
        'attack': 'TST → TSD', 'output_lines': 11,
        'requirement': 'specific pieces', 'coverage': '~25%',
        'difficulty': 'hard', 'tier': 'SS',
        'strength': 'TST 선제 공격으로 압박',
        'weakness': '커버리지 낮음',
        'counter': '1st bag에서 빠르게 공격',
        'ref': 'https://harddrop.com/wiki/C-Spin',
    },
    # ── 중반 기술 ──
    {
        'name': 'STSD', 'full_name': 'Super T-Spin Double',
        'category': 'midgame', 'bag': 0,
        'description': 'S/Z 위에 T-Spin Double 구멍을 만드는 중반 핵심 기술. 반복 적용 가능.',
        'attack': 'TSD', 'output_lines': 4,
        'requirement': 'S/Z + T', 'coverage': 'any',
        'difficulty': 'medium', 'tier': 'A',
        'strength': '반복 가능, 중반 내내 공격 유지',
        'weakness': 'S/Z+T 조합 필요',
        'counter': '지속적 공격으로 STSD 구축 시간을 빼앗기',
        'ref': 'https://harddrop.com/wiki/STSD',
    },
    {
        'name': 'LST Stacking', 'full_name': 'LST Stacking',
        'category': 'midgame', 'bag': 0,
        'description': 'L/S/T로 연속 T-Spin 구멍을 만드는 고급 기술.',
        'attack': '연속 TSD', 'output_lines': 4,
        'requirement': 'L/S/T 조합', 'coverage': 'any',
        'difficulty': 'hard', 'tier': 'SS',
        'strength': '높은 공격 효율, 연속 B2B',
        'weakness': '높은 실행 난이도, 지형 관리 어려움',
        'counter': '가비지로 지형을 무너뜨리기',
        'ref': 'https://harddrop.com/wiki/LST_Stacking',
    },
    {
        'name': 'Imperial Cross', 'full_name': 'Imperial Cross',
        'category': 'midgame', 'bag': 0,
        'description': '+ 모양 T-Spin 셋업. 안정적인 TSD 생성.',
        'attack': 'TSD', 'output_lines': 4,
        'requirement': 'T + overhang', 'coverage': 'any',
        'difficulty': 'medium', 'tier': 'S',
        'strength': '안정적, 직관적 형태',
        'weakness': '특정 지형에서만 가능',
        'counter': '지형을 불규칙하게 만들기',
        'ref': 'https://harddrop.com/wiki/Imperial_Cross',
    },
    {
        'name': 'Fractal', 'full_name': 'Fractal (연속 T-Spin)',
        'category': 'midgame', 'bag': 0,
        'description': '무한 T-Spin Double 반복 패턴. 프렉탈 구조.',
        'attack': '무한 TSD', 'output_lines': 4,
        'requirement': '안정적 지형 + T피스', 'coverage': 'any',
        'difficulty': 'expert', 'tier': 'X',
        'strength': '이론적 무한 공격',
        'weakness': '실전 유지 극난',
        'counter': '대량 가비지로 구조 파괴',
        'ref': 'https://harddrop.com/wiki/Fractal',
    },
    # ── 전략 ──
    {
        'name': '4-wide', 'full_name': '4-Wide Combo',
        'category': 'strategy', 'bag': 0,
        'description': '4열을 비우고 나머지에 쌓으며 연속 콤보 생성. 대량 가비지.',
        'attack': '연속 콤보', 'output_lines': '10+',
        'requirement': '안정적 쌓기', 'coverage': 'any',
        'difficulty': 'medium', 'tier': 'B+',
        'strength': '대량 가비지, 초보~중급에서 강력',
        'weakness': '구축 중 무방비, 상급자에게 쉽게 카운터 당함',
        'counter': '쌓는 동안 빠르게 2~3줄 보내면 구조 붕괴',
        'ref': 'https://harddrop.com/wiki/Combo',
    },
    {
        'name': '6-3 Stacking', 'full_name': '6-3 Stacking',
        'category': 'strategy', 'bag': 0,
        'description': '6열 쌓기 + 3열 Quad 웰. 안정적인 다운스택 형태.',
        'attack': 'Quad', 'output_lines': 4,
        'requirement': 'I피스', 'coverage': 'any',
        'difficulty': 'easy', 'tier': 'all',
        'strength': '안정적, 초보자도 사용 가능',
        'weakness': 'T-Spin 활용 어려움',
        'counter': 'T-Spin 사용자에게 효율에서 밀림',
        'ref': 'https://harddrop.com/wiki/6-3_Stacking',
    },
    # ── 수비 ──
    {
        'name': 'Downstacking', 'full_name': 'Downstacking',
        'category': 'defense', 'bag': 0,
        'description': '가비지 라인을 효율적으로 제거하는 수비 기술.',
        'attack': '라인 클리어', 'output_lines': 'variable',
        'requirement': 'none', 'coverage': 'any',
        'difficulty': 'medium', 'tier': 'all',
        'strength': '생존력 향상, 역전 가능',
        'weakness': '공격 전환 타이밍 어려움',
        'counter': '연속 공격으로 다운스택할 시간 주지 않기',
        'ref': 'https://harddrop.com/wiki/Downstacking',
    },
    {
        'name': 'Cheese Race', 'full_name': 'Cheese Race Style',
        'category': 'defense', 'bag': 0,
        'description': '쓰레기 줄 제거에 특화된 플레이 스타일.',
        'attack': '라인 클리어', 'output_lines': 'variable',
        'requirement': 'none', 'coverage': 'any',
        'difficulty': 'medium', 'tier': 'B',
        'strength': '쓰레기 제거 속도 향상',
        'weakness': '공격보다 수비에 치우침',
        'counter': '공격 전환 시 지형이 불안정',
        'ref': '',
    },
]

# 랭크별 추천 빌드
TIER_RECOMMENDATIONS = {
    'C':  ['6-3 Stacking', 'Downstacking'],
    'B':  ['6-3 Stacking', 'TKI', '4-wide'],
    'B+': ['TKI', '4-wide', 'PCO'],
    'A':  ['TKI', 'STSD', 'DT Cannon'],
    'A+': ['TKI', 'DT Cannon', 'STSD', 'PCO'],
    'S':  ['TKI', 'DT Cannon', 'Hachispin', 'STSD', 'LST Stacking'],
    'S+': ['TKI', 'DT Cannon', 'PCO', 'Hachispin', 'STSD', 'Imperial Cross'],
    'SS': ['TKI', 'DT Cannon', 'Hachispin', 'Albatross', 'LST Stacking', 'C-Spin'],
    'U':  ['TKI', 'DT Cannon', 'Albatross', 'Hachispin', 'LST Stacking', 'Fractal'],
    'X':  ['Albatross', 'TKI', 'DT Cannon', 'Hachispin', 'LST Stacking', 'Fractal'],
    'X+': ['Albatross', 'Hachispin', 'LST Stacking', 'Fractal', 'TKI', 'DT Cannon'],
}


def detect_4wide(placements: list[dict], start: int = 0, window: int = 15) -> bool:
    if len(placements) < start + 5:
        return False
    for begin in range(start, min(start + window, len(placements) - 4)):
        combo_streak = sum(1 for p in placements[begin:begin+10] if p.get('lines', p.get('lines_cleared', 0)) > 0)
        if combo_streak >= 4:
            return True
    return False


def detect_opener_tspin(placements: list[dict], max_pieces: int = 10) -> dict | None:
    tspins = []
    for p in placements[:max_pieces]:
        if p.get('tspin', p.get('is_tspin')) and p.get('piece') == 't':
            tspins.append({
                'index': p.get('i', p.get('index', 0)),
                'lines': p.get('lines', p.get('lines_cleared', 0)),
            })
    if not tspins:
        return None
    first = tspins[0]
    if first['index'] <= 7 and first['lines'] == 2:
        if len(tspins) >= 2 and tspins[1]['lines'] == 3:
            return {'name': 'DT Cannon', 'confidence': 0.8}
        return {'name': 'TKI', 'confidence': 0.6}
    if first['index'] <= 7 and first['lines'] == 1:
        if len(tspins) >= 2 and tspins[1]['lines'] == 3:
            return {'name': 'Hachispin', 'confidence': 0.7}
    return {'name': 'Unknown TSpin Opener', 'confidence': 0.3}


def detect_perfect_clear(placements: list[dict], max_pieces: int = 12) -> bool:
    return any(p.get('allclear', p.get('is_allclear')) for p in placements[:max_pieces])


def analyze_build_usage(placements: list[dict]) -> list[dict]:
    detected = []
    if detect_perfect_clear(placements):
        detected.append({'name': 'PCO', 'phase': 'opener', 'confidence': 0.9})
    opener = detect_opener_tspin(placements)
    if opener:
        detected.append({**opener, 'phase': 'opener'})
    if detect_4wide(placements):
        detected.append({'name': '4-wide', 'phase': 'midgame', 'confidence': 0.7})
    for i in range(7, len(placements) - 1):
        if placements[i].get('piece') in ('s', 'z'):
            for j in range(i + 1, min(i + 4, len(placements))):
                lines = placements[j].get('lines', placements[j].get('lines_cleared', 0))
                if (placements[j].get('tspin', placements[j].get('is_tspin')) and lines == 2):
                    detected.append({'name': 'STSD', 'phase': 'midgame', 'confidence': 0.5, 'at_piece': i})
                    break
    return detected


def get_build_info(name: str) -> dict | None:
    for b in BUILD_DATABASE:
        if b['name'].lower() == name.lower():
            return b
    return None


def get_recommendations_for_tier(tier: str) -> list[dict]:
    names = TIER_RECOMMENDATIONS.get(tier, TIER_RECOMMENDATIONS.get('A', []))
    return [b for b in BUILD_DATABASE if b['name'] in names]


def get_all_builds() -> list[dict]:
    return BUILD_DATABASE
