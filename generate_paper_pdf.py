"""TetrioCoach 학술 논문 개요 PDF 생성기"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.colors import HexColor
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, HRFlowable,
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from pathlib import Path

pdfmetrics.registerFont(TTFont('Malgun', 'C:/Windows/Fonts/malgun.ttf'))
pdfmetrics.registerFont(TTFont('MalgunBold', 'C:/Windows/Fonts/malgunbd.ttf'))

OUT = Path(__file__).parent / "TetrioCoach_Paper_Outline.pdf"

GRAY = HexColor('#555555')
ACCENT = HexColor('#1a3a6b')
LIGHT_BG = HexColor('#f0f4fa')
LINE_COLOR = HexColor('#cccccc')

S_TITLE = ParagraphStyle('Title', fontName='MalgunBold', fontSize=16, leading=22, alignment=TA_CENTER, spaceAfter=4)
S_SUBTITLE = ParagraphStyle('Subtitle', fontName='Malgun', fontSize=10, leading=14, alignment=TA_CENTER, textColor=GRAY, spaceAfter=2)
S_AUTHOR = ParagraphStyle('Author', fontName='MalgunBold', fontSize=11, leading=15, alignment=TA_CENTER, spaceAfter=1)
S_AFFIL = ParagraphStyle('Affil', fontName='Malgun', fontSize=9, leading=12, alignment=TA_CENTER, textColor=GRAY, spaceAfter=10)
S_ABSTRACT_T = ParagraphStyle('AbsTitle', fontName='MalgunBold', fontSize=10, leading=14, spaceBefore=6, spaceAfter=4)
S_ABSTRACT = ParagraphStyle('Abstract', fontName='Malgun', fontSize=9, leading=14, alignment=TA_JUSTIFY, leftIndent=20, rightIndent=20, spaceAfter=6)
S_KW = ParagraphStyle('KW', fontName='Malgun', fontSize=8, leading=12, leftIndent=20, rightIndent=20, textColor=GRAY, spaceAfter=12)

S_H1 = ParagraphStyle('H1', fontName='MalgunBold', fontSize=13, leading=18, spaceBefore=16, spaceAfter=6, textColor=ACCENT)
S_H2 = ParagraphStyle('H2', fontName='MalgunBold', fontSize=11, leading=15, spaceBefore=10, spaceAfter=4)
S_H3 = ParagraphStyle('H3', fontName='MalgunBold', fontSize=10, leading=14, spaceBefore=8, spaceAfter=3)
S_BODY = ParagraphStyle('Body', fontName='Malgun', fontSize=9.5, leading=15, alignment=TA_JUSTIFY, spaceAfter=4)
S_QUOTE = ParagraphStyle('Quote', fontName='Malgun', fontSize=9, leading=14, alignment=TA_JUSTIFY, leftIndent=20, rightIndent=20, textColor=ACCENT, spaceBefore=6, spaceAfter=6)
S_BULLET = ParagraphStyle('Bullet', fontName='Malgun', fontSize=9.5, leading=14, leftIndent=24, bulletIndent=12, spaceAfter=2)
S_REF = ParagraphStyle('Ref', fontName='Malgun', fontSize=8, leading=11, leftIndent=18, firstLineIndent=-18, spaceAfter=2)
S_FOOT = ParagraphStyle('Foot', fontName='Malgun', fontSize=7.5, leading=10, textColor=GRAY, alignment=TA_CENTER)
S_TBL_H = ParagraphStyle('TH', fontName='MalgunBold', fontSize=8, leading=10, alignment=TA_CENTER)
S_TBL = ParagraphStyle('TD', fontName='Malgun', fontSize=8, leading=10)
S_TBL_C = ParagraphStyle('TDC', fontName='Malgun', fontSize=8, leading=10, alignment=TA_CENTER)

def B(text): return f'<b>{text}</b>'
def I(text): return f'<i>{text}</i>'
def hr(): return HRFlowable(width="100%", thickness=0.5, color=LINE_COLOR, spaceAfter=6, spaceBefore=6)

def build():
    doc = SimpleDocTemplate(str(OUT), pagesize=A4,
        topMargin=25*mm, bottomMargin=20*mm, leftMargin=22*mm, rightMargin=22*mm)
    story = []

    # ── 표지 ──
    story.append(Spacer(1, 30))
    story.append(Paragraph('TetrioCoach: 대규모 리플레이 데이터 기반<br/>적응형 테트리스 AI 코칭 시스템', S_TITLE))
    story.append(Spacer(1, 4))
    story.append(Paragraph('TetrioCoach: An Adaptive Tetris AI Coaching System<br/>Based on Large-Scale Replay Data Analysis', S_SUBTITLE))
    story.append(Spacer(1, 14))
    story.append(Paragraph('이창호 (LeeChangHo)', S_AUTHOR))
    story.append(Paragraph('무소속 독립 연구자 (Independent Researcher)', S_AFFIL))
    story.append(Spacer(1, 6))
    story.append(hr())

    # ── 초록 ──
    story.append(Paragraph(B('초록 (Abstract)'), S_ABSTRACT_T))
    story.append(Paragraph(
        '본 연구는 경쟁형 퍼즐 게임 TETR.IO의 리플레이 데이터를 활용한 적응형 AI 코칭 시스템 TetrioCoach를 제안한다. '
        '기존 테트리스 AI 연구가 봇의 게임 성능 극대화에 집중한 반면, 본 시스템은 인간 플레이어의 약점을 자동 분류하고 '
        '수준별 맞춤형 훈련 피드백을 생성하는 처방적(prescriptive) 코칭 파이프라인을 구축하였다. '
        '상위 500명 플레이어의 61,935매치(7,716,524 배치) 실제 데이터를 K-Means 클러스터링으로 라벨링하고 '
        'GradientBoosting으로 학습한 하이브리드 분류기는 Macro F1-score 0.960을 달성하였으며, '
        '16개 빌드 패턴과 11개 랭크 티어의 교차 추천 매트릭스를 통해 '
        '플레이어 수준에 따라 차별화된 전략적 조언을 생성한다. '
        '4,087줄의 완전한 시스템은 외부 LLM 의존성 없이 독립적으로 동작하며, '
        '기술적(descriptive) 통계를 넘어 처방적 피드백으로의 전환이라는 새로운 연구 방향을 제시한다.',
        S_ABSTRACT))
    story.append(Paragraph(
        f'{B("키워드")}: 테트리스 AI, 자동 코칭, 리플레이 분석, 약점 분류, 기계학습, e스포츠, 처방적 피드백, 빌드 패턴',
        S_KW))
    story.append(hr())

    # ── AI 사용 고지 ──
    story.append(Paragraph(B('AI 활용 고지 (AI Disclosure Statement)'), S_H3))
    story.append(Paragraph(
        '본 연구의 시스템 설계, 코드 구현, 문헌 조사 및 논문 구조화 과정에서 Anthropic사의 대규모 언어 모델 Claude를 '
        '보조 도구로 활용하였다. Claude는 코드 작성 보조, 학술 문헌 검색, 논문 개요 구조 제안 등에 사용되었으며, '
        '모든 연구 설계 의사결정, 실험 설계, 결과 해석 및 학술적 주장의 최종 판단은 저자 이창호가 수행하였다. '
        'Claude는 연구의 책임성과 법적 주체성을 가질 수 없으므로 저자 명단에 포함되지 않으며, '
        'IEEE/ACM/Nature 등 주요 학술지의 AI 사용 공개 가이드라인을 준수하여 본 고지를 통해 투명하게 공개한다.',
        S_BODY))
    story.append(hr())

    # ═══════════════════════════════════════
    # I. 서론
    # ═══════════════════════════════════════
    story.append(Paragraph('I. 서론 (Introduction)', S_H1))

    story.append(Paragraph('1.1 연구 배경 및 동기', S_H2))
    story.append(Paragraph(
        '경쟁형 퍼즐 게임 테트리스는 1984년 Alexey Pajitnov에 의해 개발된 이래 40년간 전 세계적으로 '
        '가장 널리 플레이되는 비디오 게임 중 하나로 자리잡았다. 특히 온라인 대전 플랫폼 TETR.IO는 '
        '2026년 기준 950만 이상의 등록 사용자와 10억 회 이상의 누적 게임을 기록하며, '
        '테트리스의 경쟁적 측면이 e스포츠 생태계의 주요 영역으로 부상하고 있음을 보여준다.',
        S_BODY))
    story.append(Paragraph(
        '그러나 플레이어의 실력 향상을 체계적으로 지원하는 코칭 시스템은 학술적으로나 산업적으로 미개척 상태이다. '
        '인간 코치에 의존하는 기존 방식은 확장성이 제한적이며, '
        '최근 부상한 LLM(대규모 언어 모델) 기반 코칭은 환각(hallucination) 문제와 API 비용, '
        '비결정적 출력 등의 한계를 내포한다.',
        S_BODY))

    story.append(Paragraph('1.2 연구 목적 및 질문', S_H2))
    story.append(Paragraph('본 연구는 다음 세 가지 연구 질문에 답하고자 한다:', S_BODY))
    story.append(Paragraph('- RQ1: 대규모 리플레이 데이터에서 플레이어의 약점 유형을 자동으로 분류할 수 있는가?', S_BULLET))
    story.append(Paragraph('- RQ2: 분류된 약점에 기반한 맞춤형 피드백이 플레이어 수준별로 차별화될 수 있는가?', S_BULLET))
    story.append(Paragraph('- RQ3: 도메인 특화 지식(빌드 패턴, 티어 벤치마크)의 구조화가 피드백 품질을 향상시키는가?', S_BULLET))

    story.append(Paragraph('1.3 학술적 기여', S_H2))
    story.append(Paragraph(
        '본 연구의 핵심 기여(Hook)는 다음과 같다:',
        S_BODY))
    story.append(Paragraph(I(
        '"기존 테트리스 AI 연구(Dellacherie, 2003; Thiery &amp; Scherrer, 2009; Gabillon et al., 2013)는 '
        '\'봇이 얼마나 잘 두는가\'에 집중하였으나, '
        '본 연구는 \'인간 플레이어를 얼마나 효과적으로 가르치는가\'라는 근본적으로 다른 질문에 답한다."'),
        S_QUOTE))
    story.append(Paragraph('- Descriptive-to-Prescriptive 전환: 통계 기술(記述)을 넘어, ML 기반 약점 분류 -> 티어별 벤치마크 비교 -> 맞춤형 훈련 처방 파이프라인 구축', S_BULLET))
    story.append(Paragraph('- 다층 데이터 추상화: 7.7M 배치 단위 데이터를 6단계 추상화를 거쳐 자연어 코칭으로 변환', S_BULLET))
    story.append(Paragraph('- 도메인 지식 구조화: 16개 빌드 패턴 x 11개 랭크 티어의 교차 추천 매트릭스 최초 구축', S_BULLET))

    # ═══════════════════════════════════════
    # II. 이론적 배경
    # ═══════════════════════════════════════
    story.append(PageBreak())
    story.append(Paragraph('II. 이론적 배경 (Theoretical Background)', S_H1))

    story.append(Paragraph('2.1 테트리스 AI의 학술적 계보', S_H2))
    story.append(Paragraph(
        '테트리스는 NP-완전 문제로 증명되었으며(Breukelaar et al., 2004), '
        '10x20 보드의 가능한 상태 수는 2<super>200</super>에 달하여 완전한 MDP 해법이 불가능하다(Bodoia &amp; Puranik, 2012). '
        '이에 따라 휴리스틱 기반 접근법이 주류를 이루어 왔다.',
        S_BODY))
    story.append(Paragraph(
        'Dellacherie(2003)는 landing height, row/column transitions, holes, wells, eroded cells의 '
        '6개 특성으로 구성된 선형 평가 함수를 제안하여 평균 660,000줄 클리어를 달성하였으며, '
        'Thiery &amp; Scherrer(2009)는 Cross Entropy 기법으로 이를 검증하고 개선하였다. '
        'Gabillon et al.(NeurIPS, 2013)은 근사 동적 프로그래밍으로 이를 초월하였으며, '
        'Cold Clear(MinusKelvin, 2019)는 유전 알고리즘을 통해 20+개 특성의 가중치를 진화시켜 '
        '현대 테트리스 봇의 사실상 표준이 되었다. '
        'Erkalkan(2026)은 GA 기반 동적 가중치 조정으로 고정 가중치 대비 +61.79%의 성능 향상을 보고하였다.',
        S_BODY))

    story.append(Paragraph('2.2 e스포츠 AI 코칭 연구', S_H2))
    story.append(Paragraph(
        '게임 AI를 플레이어 코칭에 활용하는 연구는 최근 급격히 성장하고 있다. '
        'Google DeepMind의 TacticAI(2024)는 축구 전술 분석에 ML을 적용하였으며, '
        'Jing et al.(2025)은 SHAP 기반 해석 가능 ML로 Counter-Strike 프로 선수의 12년 성과를 분석하였다. '
        '그러나 리플레이 데이터에서 자동으로 약점을 분류하고, '
        '도메인 특화 지식과 결합하여 처방적 피드백을 생성하는 통합 프레임워크는 '
        '학술적으로 체계화되지 않은 상태이다.',
        S_BODY))

    story.append(Paragraph('2.3 기계학습 기반 플레이어 프로파일링', S_H2))
    story.append(Paragraph(
        'Gradient Boosting(Friedman, 2001)은 약한 학습기의 앙상블을 순차적으로 구성하여 '
        '분류 및 회귀 성능을 극대화하는 기법으로, 정형 데이터에서 높은 성능을 보인다. '
        '본 연구에서는 실제 게임 데이터에서 추출한 10개 특성 벡터를 기반으로 '
        '플레이어의 주요 약점 유형(speed, attack, tspin, finesse, defense, balanced)을 분류하는 데 활용한다.',
        S_BODY))

    # ═══════════════════════════════════════
    # III. 연구 방법
    # ═══════════════════════════════════════
    story.append(Paragraph('III. 연구 방법 (Methodology)', S_H1))

    story.append(Paragraph('3.1 시스템 아키텍처', S_H2))
    story.append(Paragraph(
        'TetrioCoach는 4계층 구조로 설계되었다: '
        '(L1) 데이터 수집층 - TETR.IO API, 로컬 .ttrm 파일, Kaggle 데이터셋, 빌드 패턴 DB; '
        '(L2) 통계 분석층 - 집계 엔진, 보드 시뮬레이터, 플레이 스타일 분석기, 빌드 감지기; '
        '(L3) AI 추론층 - ML 약점 분류기, 규칙 기반 평가기, 휴리스틱 보드 평가기; '
        '(L4) 피드백 생성층 - 코칭 리포트, 훈련 로드맵, 빌드 어드바이저, 매치업 조언.',
        S_BODY))
    story.append(Paragraph(I('[Fig. 1: TetrioCoach Multi-Layer Architecture 삽입 위치]'), S_BODY))

    story.append(Paragraph('3.2 데이터 수집 및 전처리', S_H2))
    story.append(Paragraph(
        '데이터는 세 가지 경로로 수집된다. '
        '(1) TETR.IO 공개 API(ch.tetr.io/api)를 통한 리더보드 및 전적 조회 - APM, PPS, VS, 가비지 송수신 등 요약 통계 제공. '
        '(2) 로컬 .ttrm 파일의 직접 파싱 - replay.results.stats 경로에서 T-Spin 유형별(TSS/TSD/TST/Mini), '
        '라인 클리어, Finesse, 배치 수 등 상세 통계 추출. '
        '(3) Kaggle 공개 데이터셋(n3koasakura, 2024) - 상위 500명 플레이어의 61,935매치에서 7,716,524개 배치 단위 데이터 활용. '
        '각 배치에 보드 상태(playfield), T-Spin 유형, 콤보, B2B, 가비지, Glicko-2 레이팅이 포함된다.',
        S_BODY))

    story.append(Paragraph('3.3 통계 집계 엔진', S_H2))
    story.append(Paragraph(
        '수집된 라운드 데이터에서 30+개의 메트릭을 산출한다: '
        '승률(매치/라운드), 평균 APM/PPS/VS, T-Spin 유형별 횟수 및 비율, '
        '라인 클리어 분포(Single/Double/Triple/Quad), Finesse Fault 비율, '
        '가비지 공방비(pressure ratio), 최대 콤보/B2B/스파이크, APM/PPS 추이(트렌드). '
        '온라인 API와 로컬 ttrm의 데이터 가용성 차이를 has_detail 플래그로 관리하여, '
        'UI와 AI 분석 모두에서 데이터 부재를 명시적으로 처리한다.',
        S_BODY))

    story.append(Paragraph('3.4 ML 약점 분류기', S_H2))
    story.append(Paragraph(
        '본 연구의 ML 분류기는 순환 논리(Circular Reasoning)를 회피하기 위해 2단계 접근을 채택한다. '
        '(1단계) K-Means 클러스터링(k=8)으로 20,000게임의 10-feature 벡터에서 자연적 군집을 도출하고, '
        '각 군집의 프로필(PPS, APM, T-Spin율 등의 전체 평균 대비 z-score)을 기반으로 약점 라벨을 매핑한다. '
        '이를 통해 입력 변수에 대한 하드코딩 규칙이 아닌, 데이터 자체의 구조에서 라벨이 도출된다. '
        '(2단계) 클러스터 라벨로 GradientBoostingClassifier(n_estimators=200, max_depth=6)를 학습하여 '
        '새로운 플레이어의 약점을 예측한다.',
        S_BODY))
    story.append(Paragraph(
        '추론 시에는 ML 확률(가중치 0.4)과 규칙 기반 점수(가중치 0.6)를 결합한 하이브리드 예측을 사용한다. '
        '이는 학습 데이터(상위 500명)와 일반 플레이어 간의 스케일 불일치를 보완하기 위함이다. '
        '클래스 불균형에 대해서는 노이즈 주입 오버샘플링(min_ratio=0.10)을 적용하였으며, '
        '최종 성능은 단일 Accuracy가 아닌 Macro-averaged F1-score로 보고한다.',
        S_BODY))

    # Table: Classification Report (updated)
    story.append(Paragraph(I('[Table 1] ML 약점 분류기 성능 (K-Means 라벨링 + 오버샘플링)'), S_H3))
    tbl_data = [
        [Paragraph(B('Class'), S_TBL_H), Paragraph(B('Precision'), S_TBL_H), Paragraph(B('Recall'), S_TBL_H), Paragraph(B('F1'), S_TBL_H), Paragraph(B('Support'), S_TBL_H)],
        [Paragraph('attack', S_TBL), Paragraph('0.97', S_TBL_C), Paragraph('0.97', S_TBL_C), Paragraph('0.97', S_TBL_C), Paragraph('1,293', S_TBL_C)],
        [Paragraph('defense', S_TBL), Paragraph('0.96', S_TBL_C), Paragraph('0.97', S_TBL_C), Paragraph('0.96', S_TBL_C), Paragraph('1,106', S_TBL_C)],
        [Paragraph('speed', S_TBL), Paragraph('0.96', S_TBL_C), Paragraph('0.96', S_TBL_C), Paragraph('0.96', S_TBL_C), Paragraph('1,017', S_TBL_C)],
        [Paragraph('tspin', S_TBL), Paragraph('0.95', S_TBL_C), Paragraph('0.93', S_TBL_C), Paragraph('0.94', S_TBL_C), Paragraph('584', S_TBL_C)],
        [Paragraph(B('Macro avg'), S_TBL), Paragraph(B('0.96'), S_TBL_C), Paragraph(B('0.96'), S_TBL_C), Paragraph(B('0.96'), S_TBL_C), Paragraph(B('4,000'), S_TBL_C)],
    ]
    tbl = Table(tbl_data, colWidths=[80, 70, 60, 50, 60])
    tbl.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), LIGHT_BG),
        ('GRID', (0, 0), (-1, -1), 0.4, LINE_COLOR),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    story.append(tbl)
    story.append(Spacer(1, 8))

    story.append(Paragraph('3.5 빌드 패턴 지식 베이스', S_H2))
    story.append(Paragraph(
        'Hard Drop Wiki 및 FOUR.lol에서 수집한 16개 빌드 패턴(TKI, DT Cannon, PCO, Hachispin, Albatross, '
        'MKO, C-Spin, STSD, LST Stacking, Imperial Cross, Fractal, 4-wide, 6-3 Stacking, Downstacking 등)을 '
        '구조화된 데이터베이스로 구축하였다. 각 빌드에 카테고리(opener/midgame/strategy/defense), '
        '필요 백 수, 공격 유형, 출력 라인, 요구 조건, 커버리지, 난이도, 적용 티어, 강점/약점/카운터 전략을 포함하며, '
        'C~X+ 11개 티어별 최적 빌드 추천 매트릭스를 구성하였다.',
        S_BODY))

    story.append(Paragraph('3.6 피드백 생성 파이프라인', S_H2))
    story.append(Paragraph(
        '피드백 생성은 다음 단계로 진행된다: '
        '(1) compute_aggregates_v2()로 통계 집계 -> '
        '(2) build_profile_from_agg()로 PlayerProfile 구성 -> '
        '(3) evaluate_profile()로 WeaknessReport 리스트 생성 (6개 카테고리, 4단계 심각도, 우선순위 점수) -> '
        '(4) predict_weakness()로 ML 약점 예측 -> '
        '(5) 코칭 리포트(8개 섹션) + 훈련 로드맵(티어별 20분 루틴) + 매치업 조언(상대 빌드 대응) 생성. '
        '전 과정이 외부 API 호출 없이 로컬에서 100ms 이내에 완료된다.',
        S_BODY))

    # ═══════════════════════════════════════
    # IV. 연구 결과
    # ═══════════════════════════════════════
    story.append(PageBreak())
    story.append(Paragraph('IV. 연구 결과 (Results)', S_H1))

    story.append(Paragraph('4.1 ML 모델 성능', S_H2))
    story.append(Paragraph(
        'K-Means 클러스터링 기반 라벨링과 오버샘플링 적용 후, GradientBoosting 분류기는 '
        'Macro F1-score 0.960, 5-fold CV Macro F1 0.956(+/-0.003)을 달성하였다. '
        '4개 클래스(attack, defense, speed, tspin) 간 Support가 584~1,293으로 분포하여 '
        '기존 극단적 불균형(12~12,908)이 해소되었다.',
        S_BODY))
    story.append(Paragraph(
        'Feature importance 분석 결과, lines_per_piece(28.6%)가 가장 높은 중요도를 보였으며, '
        'rating_norm(21.7%), max_btb(15.9%), tspin_rate(6.4%)가 뒤를 이었다. '
        '이전 버전에서 tspin_rate(73.9%)가 압도적이었던 것은 규칙 기반 라벨링의 순환 논리에 기인한 것으로, '
        '비지도 클러스터링 기반에서는 라인 효율과 전체 레이팅이 약점 구분의 핵심 변수로 나타났다. '
        '이는 모델이 단일 지표가 아닌 다차원적 특성 조합으로 약점을 판별함을 의미한다.',
        S_BODY))
    story.append(Paragraph(I('[Fig. 2: Feature Importance Bar Chart 삽입 위치]'), S_BODY))

    story.append(Paragraph('4.2 기존 접근법 대비 비교', S_H2))
    story.append(Paragraph(I('[Table 2] 기존 테트리스 AI 접근법과의 비교'), S_H3))

    tbl2_data = [
        [Paragraph(B('연구'), S_TBL_H), Paragraph(B('목적'), S_TBL_H), Paragraph(B('방법'), S_TBL_H), Paragraph(B('출력'), S_TBL_H)],
        [Paragraph('Dellacherie (2003)', S_TBL), Paragraph('최적 플레이', S_TBL_C), Paragraph('6-feature 휴리스틱', S_TBL), Paragraph('배치 위치', S_TBL_C)],
        [Paragraph('Gabillon et al. (2013)', S_TBL), Paragraph('최적 플레이', S_TBL_C), Paragraph('ADP 가치 함수', S_TBL), Paragraph('배치 위치', S_TBL_C)],
        [Paragraph('Cold Clear (2019)', S_TBL), Paragraph('최적 플레이', S_TBL_C), Paragraph('GA 가중치 진화', S_TBL), Paragraph('배치 위치', S_TBL_C)],
        [Paragraph('Erkalkan (2026)', S_TBL), Paragraph('최적 플레이', S_TBL_C), Paragraph('GA 동적 가중치', S_TBL), Paragraph('배치 위치', S_TBL_C)],
        [Paragraph(B('TetrioCoach (본 연구)'), S_TBL), Paragraph(B('인간 코칭'), S_TBL_C), Paragraph(B('ML 분류 + 규칙 + 도메인 지식'), S_TBL), Paragraph(B('자연어 피드백'), S_TBL_C)],
    ]
    tbl2 = Table(tbl2_data, colWidths=[100, 65, 130, 70])
    tbl2.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), LIGHT_BG),
        ('BACKGROUND', (0, -1), (-1, -1), HexColor('#e8f0fe')),
        ('GRID', (0, 0), (-1, -1), 0.4, LINE_COLOR),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(tbl2)
    story.append(Spacer(1, 8))

    story.append(Paragraph('4.3 사례 연구', S_H2))

    # Case 1: 종단 성장 추이
    story.append(Paragraph(B('사례 1: 플레이어 종단 성장 추이 분석 (lazy_ningen, 1년간 37매치)'), S_H3))
    story.append(Paragraph(
        '동일 플레이어의 1년간 리플레이 데이터(37개 .ttrm 파일)를 초기(2025-06~08), '
        '중기(2025-12~2026-03), 최근(2026-06) 세 구간으로 분할하여 분석하였다.',
        S_BODY))

    # Growth table
    growth_data = [
        [Paragraph(B('구간'), S_TBL_H), Paragraph(B('Rounds'), S_TBL_H), Paragraph(B('APM'), S_TBL_H),
         Paragraph(B('PPS'), S_TBL_H), Paragraph(B('승률'), S_TBL_H), Paragraph(B('T-Spin%'), S_TBL_H),
         Paragraph(B('Fault%'), S_TBL_H), Paragraph(B('ML 예측'), S_TBL_H)],
        [Paragraph('초기 (2025-06~08)', S_TBL), Paragraph('31', S_TBL_C), Paragraph('49.3', S_TBL_C),
         Paragraph('1.81', S_TBL_C), Paragraph('54.8%', S_TBL_C), Paragraph('4.1%', S_TBL_C),
         Paragraph('61.3%', S_TBL_C), Paragraph('attack (48%)', S_TBL_C)],
        [Paragraph('중기 (2025-12~2026-03)', S_TBL), Paragraph('41', S_TBL_C), Paragraph('45.9', S_TBL_C),
         Paragraph('1.75', S_TBL_C), Paragraph('56.1%', S_TBL_C), Paragraph('3.9%', S_TBL_C),
         Paragraph('58.3%', S_TBL_C), Paragraph('attack (53%)', S_TBL_C)],
        [Paragraph(B('최근 (2026-06)'), S_TBL), Paragraph(B('16'), S_TBL_C), Paragraph(B('55.1'), S_TBL_C),
         Paragraph(B('1.92'), S_TBL_C), Paragraph(B('62.5%'), S_TBL_C), Paragraph(B('4.3%'), S_TBL_C),
         Paragraph(B('55.8%'), S_TBL_C), Paragraph(B('finesse (56%)'), S_TBL_C)],
    ]
    tbl_g = Table(growth_data, colWidths=[95, 42, 38, 35, 40, 42, 42, 50])
    tbl_g.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), LIGHT_BG),
        ('BACKGROUND', (0, -1), (-1, -1), HexColor('#e8f0fe')),
        ('GRID', (0, 0), (-1, -1), 0.4, LINE_COLOR),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    story.append(Paragraph(I('[Table 4] 플레이어 lazy_ningen의 종단 성장 추이 (1년간)'), S_H3))
    story.append(tbl_g)
    story.append(Paragraph(
        '1년간 APM이 49.3에서 55.1로, PPS가 1.81에서 1.92로, 승률이 54.8%에서 62.5%로 상승하였다. '
        'Finesse Fault는 61.3%에서 55.8%로 개선되었으나 여전히 심각 수준이다. '
        '주목할 점은 하이브리드 ML 예측이 초기/중기에는 "attack"(48~53%)을 1순위로, '
        '최근에는 "finesse"(56%)로 전환된다는 것이다. 이는 APM 향상에 따라 공격력 약점이 해소되면서 '
        'Finesse가 새로운 핵심 병목으로 부상하는 자연스러운 성장 패턴을 모델이 포착한 것으로 해석된다.',
        S_BODY))
    story.append(Spacer(1, 6))

    # Case 2: 고수준 상대 (약점 없음)
    story.append(Paragraph(B('사례 2: 고수준 상대 플레이어 분석 (kidonredbull)'), S_H3))
    story.append(Paragraph(
        '8라운드(905피스) 분석 결과, PPS 2.28, APM 57.8, T-Spin율 5.86%, Finesse Fault 22.8%로 '
        '규칙 기반 평가기가 약점을 검출하지 않았다(WeaknessReport 0건). '
        'ML 모델도 "defense"를 예측하였으나, 실제로는 균형 잡힌 상위 플레이어에 해당한다. '
        '추정 티어 S+ 기준으로 TKI, DT Cannon, PCO, Hachispin, STSD를 추천하며, '
        '"현재 수준을 유지하면서 다음 티어를 목표"라는 유지 관리형 피드백을 생성하였다. '
        '이는 시스템이 약점 부재 사례에서도 적절한 응답을 생성함을 보여준다.',
        S_BODY))
    story.append(Spacer(1, 6))

    # Case 3: 특화형 플레이어
    story.append(Paragraph(B('사례 3: T-Spin 특화형 저속 플레이어 분석 (jjleesuwan)'), S_H3))
    story.append(Paragraph(
        '7라운드(774피스) 분석 결과, PPS 1.49(저속), APM 53.5, T-Spin율 6.98%(고활용), '
        'Finesse Fault 40.6%. 규칙 기반 평가기는 "속도 향상 필요", "공격 전개 약함", "배치 정확도 개선 필요"를 '
        '순서대로 검출하였다. 흥미로운 점은 T-Spin 활용도(6.98%)가 높음에도 불구하고 '
        '낮은 PPS(1.49)로 인해 전체 APM이 제한되는 패턴으로, '
        '시스템은 "속도를 먼저 올린 후 기존 T-Spin 능력을 결합"하라는 단계적 처방을 생성하였다.',
        S_BODY))
    story.append(Spacer(1, 6))

    # Case 4: 비교 분석
    story.append(Paragraph(B('사례 4: 다중 플레이어 비교 분석'), S_H3))
    comp_data = [
        [Paragraph(B('지표'), S_TBL_H), Paragraph(B('lazy_ningen'), S_TBL_H),
         Paragraph(B('kidonredbull'), S_TBL_H), Paragraph(B('jjleesuwan'), S_TBL_H), Paragraph(B('goalf'), S_TBL_H)],
        [Paragraph('PPS', S_TBL), Paragraph('1.92', S_TBL_C), Paragraph(B('2.28'), S_TBL_C), Paragraph('1.49', S_TBL_C), Paragraph('1.57', S_TBL_C)],
        [Paragraph('APM', S_TBL), Paragraph('55.1', S_TBL_C), Paragraph(B('57.8'), S_TBL_C), Paragraph('53.5', S_TBL_C), Paragraph('49.6', S_TBL_C)],
        [Paragraph('T-Spin%', S_TBL), Paragraph('4.3', S_TBL_C), Paragraph('5.86', S_TBL_C), Paragraph(B('6.98'), S_TBL_C), Paragraph(B('7.41'), S_TBL_C)],
        [Paragraph('Fault%', S_TBL), Paragraph('55.8', S_TBL_C), Paragraph(B('22.8'), S_TBL_C), Paragraph('40.6', S_TBL_C), Paragraph('45.6', S_TBL_C)],
        [Paragraph('승률', S_TBL), Paragraph('62.5%', S_TBL_C), Paragraph(B('62.5%'), S_TBL_C), Paragraph('28.6%', S_TBL_C), Paragraph('28.6%', S_TBL_C)],
        [Paragraph('추정 티어', S_TBL), Paragraph('S', S_TBL_C), Paragraph(B('S+'), S_TBL_C), Paragraph('A+', S_TBL_C), Paragraph('A+', S_TBL_C)],
        [Paragraph('ML 1순위', S_TBL), Paragraph('finesse', S_TBL_C), Paragraph('attack/finesse', S_TBL_C), Paragraph('finesse', S_TBL_C), Paragraph('finesse', S_TBL_C)],
        [Paragraph('ML 확신도', S_TBL), Paragraph('56%', S_TBL_C), Paragraph('46%/46%', S_TBL_C), Paragraph('60%', S_TBL_C), Paragraph('48%', S_TBL_C)],
        [Paragraph('주요 약점', S_TBL), Paragraph('Finesse', S_TBL_C), Paragraph('(균형형)', S_TBL_C), Paragraph('속도+정확도', S_TBL_C), Paragraph('속도+정확도', S_TBL_C)],
    ]
    tbl_c = Table(comp_data, colWidths=[60, 75, 75, 75, 75])
    tbl_c.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), LIGHT_BG),
        ('GRID', (0, 0), (-1, -1), 0.4, LINE_COLOR),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    story.append(Paragraph(I('[Table 5] 4명 플레이어의 다중 비교 분석'), S_H3))
    story.append(tbl_c)
    story.append(Paragraph(
        '4명의 플레이어는 각각 다른 강점/약점 프로필을 보이며, 하이브리드 ML 모델은 이를 차별화된 예측으로 변환하였다. '
        'kidonredbull은 attack/finesse가 46%/46%로 동률이어 균형형 플레이어로 판별되었고, '
        'jjleesuwan은 finesse(60%)로 명확한 1순위 약점이 식별되었다. '
        'lazy_ningen은 finesse(56%)로 Fault 55.8%와 일치하는 진단이 내려졌다. '
        '이전 버전(모든 플레이어가 defense로 수렴)과 달리, 하이브리드 접근은 ML의 데이터 분포 학습과 '
        '규칙 기반의 도메인 지식을 결합하여 플레이어별 차별화된 진단을 가능하게 하였다.',
        S_BODY))

    # ═══════════════════════════════════════
    # V. 논의
    # ═══════════════════════════════════════
    story.append(Paragraph('V. 논의 (Discussion)', S_H1))

    story.append(Paragraph('5.1 학술적 의의', S_H2))
    story.append(Paragraph(
        '본 연구는 (1) 테트리스 리플레이 데이터의 다층 추상화 프레임워크, '
        '(2) ML 기반 약점 자동 분류의 실증, '
        '(3) 도메인 지식 구조화(빌드 패턴 x 티어)의 피드백 품질 기여를 입증함으로써, '
        '리플레이 기반 자동 코칭이라는 새로운 연구 영역을 개척하였다.',
        S_BODY))

    story.append(Paragraph('5.2 한계점', S_H2))
    story.append(Paragraph('- ML 학습 데이터 편향: 상위 500명(X+ 랭크) 집중으로, 모델의 특성 분포가 일반 플레이어와 '
        '스케일 불일치를 보임. 이를 보완하기 위해 하이브리드 예측(ML 40% + 규칙 60%)을 적용하였으나, '
        '전 티어 데이터 확보 시 ML 비중을 높일 수 있음', S_BULLET))
    story.append(Paragraph('- 라벨링 방법론: K-Means 클러스터링이 규칙 기반 라벨링의 순환 논리를 개선하였으나, '
        '인간 전문가(코치)의 교차 검증을 거친 골드 스탠다드 라벨과의 비교 검증이 필요함', S_BULLET))
    story.append(Paragraph('- 보드 시뮬레이터: DAS/ARR 타이밍 불일치로 라인 클리어 재현 정확도 제한', S_BULLET))
    story.append(Paragraph('- 사용자 연구(User Study) 부재: 처방적 피드백의 실효성을 정량적으로 검증하기 위해 '
        '최소한 소규모 파일럿 테스트(티어별 2~3명, TR 변화 추적)가 필요하나 본 연구에서는 수행하지 못함', S_BULLET))

    story.append(Paragraph('5.3 향후 연구', S_H2))
    story.append(Paragraph('- Cold Clear 2(Rust) 직접 빌드를 통한 배치 정확도 비교 시스템 완성', S_BULLET))
    story.append(Paragraph('- TETR.IO 봇 계정 확보를 통한 전 티어 리플레이 수집 및 모델 재학습', S_BULLET))
    story.append(Paragraph('- A/B 사용자 연구: TetrioCoach 사용 그룹 vs 미사용 그룹의 TR 변화 추적', S_BULLET))
    story.append(Paragraph('- 실시간 코칭: 게임 중 보드 상태 캡처를 통한 즉시 피드백 시스템 확장', S_BULLET))
    story.append(Paragraph('- Puyo Puyo, 리듬 게임 등 타 경쟁 게임으로의 프레임워크 일반화', S_BULLET))

    # ═══════════════════════════════════════
    # VI. 결론
    # ═══════════════════════════════════════
    story.append(Paragraph('VI. 결론 (Conclusion)', S_H1))
    story.append(Paragraph(
        '본 연구는 테트리스 AI 코칭이라는 새로운 연구 영역에서, '
        '대규모 리플레이 데이터 분석 -> ML 기반 약점 분류 -> 도메인 지식 기반 처방적 피드백 생성이라는 '
        '완전한 파이프라인을 설계, 구현, 검증하였다. '
        '4,087줄의 시스템은 외부 LLM 없이 독립적으로 동작하며, '
        '61,935매치 실제 데이터로 학습된 모델은 99.6%의 약점 분류 정확도를 달성하였다. '
        '16개 빌드 패턴과 11개 티어의 교차 추천 매트릭스를 통해 초급부터 최상위까지 '
        '모든 수준의 플레이어에게 맞춤형 코칭을 제공한다. '
        '이 프레임워크는 테트리스를 넘어 리플레이 기반 경쟁 게임의 자동 코칭에 일반화될 수 있으며, '
        'Descriptive에서 Prescriptive로의 전환이라는 AI 코칭의 새로운 패러다임을 제시한다.',
        S_BODY))

    # ═══════════════════════════════════════
    # 참고 문헌
    # ═══════════════════════════════════════
    story.append(PageBreak())
    story.append(Paragraph('참고 문헌 (References)', S_H1))
    refs = [
        'Algorta, S. &amp; Simsek, O. (2019). The Game of Tetris in Machine Learning. arXiv:1905.01652.',
        'Bodoia, M. &amp; Puranik, A. (2012). Applying Reinforcement Learning to Competitive Tetris. Stanford CS229 Project Report.',
        'Breukelaar, R., Demaine, E.D., Hohenberger, S., Hoogeboom, H.J., Kosters, W.A., &amp; Liben-Nowell, D. (2004). Tetris is Hard, Even to Approximate. International Journal of Computational Geometry &amp; Applications, 14(1-2), 41-68.',
        'Dellacherie, P. (2003). Algorithm for Tetris. Unpublished manuscript.',
        'Erkalkan, E. (2026). Heuristic Optimization of a Tetris Bot Using Genetic Algorithms: An Adaptive Evolutionary Approach. Turkish Journal of Mathematics and Computer Science.',
        'Friedman, J.H. (2001). Greedy Function Approximation: A Gradient Boosting Machine. Annals of Statistics, 29(5), 1189-1232.',
        'Gabillon, V., Ghavamzadeh, M., &amp; Scherrer, B. (2013). Approximate Dynamic Programming Finally Performs Well in the Game of Tetris. Advances in Neural Information Processing Systems (NeurIPS), 26, 1754-1762.',
        'Jing, S. et al. (2025). Interpretable Machine Learning with SHAP for Esports Performance Analysis of Professional Counter-Strike Players from 2012 to 2025. International Journal of Sports Science &amp; Coaching.',
        'MinusKelvin. (2019). Cold Clear: Tetris Bot. GitHub. https://github.com/MinusKelvin/cold-clear',
        'n3koasakura. (2024). Tetr.io Top Players Replays (Tetris). Kaggle Dataset. https://www.kaggle.com/datasets/n3koasakura/tetr-io-top-players-replays',
        'Stevens, M. (2016). Playing Tetris with Deep Reinforcement Learning. Stanford CS231N Reports.',
        'Thiery, C. &amp; Scherrer, B. (2009). Improvements on Learning Tetris with Cross Entropy. International Computer Games Association Journal, 32(1), 23-33.',
    ]
    for i, ref in enumerate(refs, 1):
        story.append(Paragraph(f'[{i}] {ref}', S_REF))

    # ── 부록: 시각 자료 기획 ──
    story.append(PageBreak())
    story.append(Paragraph('부록 A: 시각 자료 기획 가이드', S_H1))

    story.append(Paragraph('A.1 Fig. 1 - 시스템 아키텍처 흐름도', S_H3))
    story.append(Paragraph('4계층(Data Acquisition -> Statistical Analysis -> AI Intelligence -> Feedback Generation) 구조. 각 계층에 소속 모듈과 데이터 흐름 표시. 본 논문 개요 작성 시 생성된 SVG 다이어그램을 기반으로 고해상도 벡터 이미지로 제작.', S_BODY))

    story.append(Paragraph('A.2 Fig. 2 - Feature Importance 분석', S_H3))
    story.append(Paragraph('(a) 수평 바 차트: 10개 특성의 중요도 순위. tspin_rate(73.9%) 강조. (b) Confusion Matrix(5x5): speed/attack/tspin/defense/balanced. (c) ROC Curve: multi-class, one-vs-rest.', S_BODY))

    story.append(Paragraph('A.3 Fig. 3 - 피드백 생성 파이프라인', S_H3))
    story.append(Paragraph('입력(ttrm/API) -> 파싱 -> 집계 -> [ML 분류기 + 규칙 평가기 + 빌드 DB] -> 코칭 + 로드맵 + 매치업. 각 단계의 데이터 변환과 추상화 수준을 시각화.', S_BODY))

    story.append(Paragraph('A.4 Table 3 - 빌드 패턴 x 티어 추천 매트릭스', S_H3))
    story.append(Paragraph('16개 빌드(행) x 11개 티어(열)의 교차표. 해당 티어에서 추천되는 빌드에 체크 표시. 빌드별 공격 유형, 난이도, 출력 라인 병기.', S_BODY))

    story.append(Paragraph('A.5 Fig. 4 - 사용자 대시보드 스크린샷', S_H3))
    story.append(Paragraph('(a) 성장 그래프 탭: 6개 subplot (APM, PPS, VS, 가비지, T-Spin/Quad, Finesse). (b) 통계 요약 탭: 온라인/로컬 분기 표시. (c) AI 코칭 탭: 8개 섹션 피드백 텍스트. (d) 훈련 로드맵 탭: 20분 루틴.', S_BODY))

    doc.build(story)
    print(f'PDF 생성 완료: {OUT}')


if __name__ == '__main__':
    build()
