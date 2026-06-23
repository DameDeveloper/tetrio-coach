"""TetrioCoach academic paper outline — English PDF generator."""

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.colors import HexColor
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, HRFlowable,
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from pathlib import Path

OUT = Path(__file__).parent / "TetrioCoach_Paper_Outline_EN.pdf"

# Embed true Times New Roman (TTF) so that em-dash, multiplication sign,
# and a serifed capital I all render unambiguously in every PDF viewer.
pdfmetrics.registerFont(TTFont('TNR', 'C:/Windows/Fonts/times.ttf'))
pdfmetrics.registerFont(TTFont('TNR-Bold', 'C:/Windows/Fonts/timesbd.ttf'))
pdfmetrics.registerFont(TTFont('TNR-Italic', 'C:/Windows/Fonts/timesi.ttf'))

GRAY = HexColor('#555555')
ACCENT = HexColor('#1a3a6b')
LIGHT_BG = HexColor('#f0f4fa')
LINE_COLOR = HexColor('#cccccc')

SERIF = 'TNR'
SERIF_B = 'TNR-Bold'
SERIF_I = 'TNR-Italic'
SANS_B = 'TNR-Bold'

S_TITLE = ParagraphStyle('Title', fontName=SERIF_B, fontSize=16, leading=21, alignment=TA_CENTER, spaceAfter=4)
S_SUBTITLE = ParagraphStyle('Subtitle', fontName=SERIF_I, fontSize=10, leading=14, alignment=TA_CENTER, textColor=GRAY, spaceAfter=2)
S_AUTHOR = ParagraphStyle('Author', fontName=SERIF_B, fontSize=11, leading=15, alignment=TA_CENTER, spaceAfter=1)
S_AFFIL = ParagraphStyle('Affil', fontName=SERIF, fontSize=9, leading=12, alignment=TA_CENTER, textColor=GRAY, spaceAfter=10)
S_ABSTRACT_T = ParagraphStyle('AbsTitle', fontName=SERIF_B, fontSize=10, leading=14, spaceBefore=6, spaceAfter=4)
S_ABSTRACT = ParagraphStyle('Abstract', fontName=SERIF, fontSize=9, leading=13.5, alignment=TA_JUSTIFY, leftIndent=20, rightIndent=20, spaceAfter=6)
S_KW = ParagraphStyle('KW', fontName=SERIF, fontSize=8.5, leading=12, leftIndent=20, rightIndent=20, textColor=GRAY, spaceAfter=12)

S_H1 = ParagraphStyle('H1', fontName=SANS_B, fontSize=13, leading=18, spaceBefore=16, spaceAfter=6, textColor=ACCENT)
S_H2 = ParagraphStyle('H2', fontName=SANS_B, fontSize=11, leading=15, spaceBefore=10, spaceAfter=4)
S_H3 = ParagraphStyle('H3', fontName=SERIF_B, fontSize=10, leading=14, spaceBefore=8, spaceAfter=3)
S_BODY = ParagraphStyle('Body', fontName=SERIF, fontSize=9.7, leading=14.5, alignment=TA_JUSTIFY, spaceAfter=4)
S_QUOTE = ParagraphStyle('Quote', fontName=SERIF_I, fontSize=9.3, leading=14, alignment=TA_JUSTIFY, leftIndent=20, rightIndent=20, textColor=ACCENT, spaceBefore=6, spaceAfter=6)
S_BULLET = ParagraphStyle('Bullet', fontName=SERIF, fontSize=9.5, leading=13.5, leftIndent=22, spaceAfter=2)
S_REF = ParagraphStyle('Ref', fontName=SERIF, fontSize=8.3, leading=11, leftIndent=18, firstLineIndent=-18, spaceAfter=2)
S_TBL_H = ParagraphStyle('TH', fontName=SERIF_B, fontSize=8, leading=10, alignment=TA_CENTER)
S_TBL = ParagraphStyle('TD', fontName=SERIF, fontSize=8, leading=10)
S_TBL_C = ParagraphStyle('TDC', fontName=SERIF, fontSize=8, leading=10, alignment=TA_CENTER)


def B(t): return f'<b>{t}</b>'
def I(t): return f'<i>{t}</i>'
def hr(): return HRFlowable(width="100%", thickness=0.5, color=LINE_COLOR, spaceAfter=6, spaceBefore=6)


def build():
    doc = SimpleDocTemplate(str(OUT), pagesize=A4,
        topMargin=25*mm, bottomMargin=20*mm, leftMargin=22*mm, rightMargin=22*mm)
    story = []

    # ── Title page ──
    story.append(Spacer(1, 30))
    story.append(Paragraph('TetrioCoach: An Adaptive Tetris AI Coaching System<br/>Based on Large-Scale Replay Data Analysis', S_TITLE))
    story.append(Spacer(1, 14))
    story.append(Paragraph('ChangHo Lee', S_AUTHOR))
    story.append(Paragraph('Independent Researcher', S_AFFIL))
    story.append(Spacer(1, 6))
    story.append(hr())

    # ── Abstract ──
    story.append(Paragraph(B('Abstract'), S_ABSTRACT_T))
    story.append(Paragraph(
        'This study presents TetrioCoach, an adaptive AI coaching system that leverages replay data from the '
        'competitive puzzle game TETR.IO. Whereas prior research on Tetris AI has concentrated on maximizing the '
        'in-game performance of autonomous bots, the proposed system establishes a prescriptive coaching pipeline '
        'that automatically classifies a human player&#39;s weaknesses and generates skill-adapted training feedback. '
        'A hybrid classifier&#8212;trained by labeling 61,935 real matches (7,716,524 piece placements) from the '
        'top 500 ranked players via K-Means clustering and learning these labels with Gradient Boosting&#8212;achieved '
        'a Macro F1-score of 0.960. Through a cross-recommendation matrix of 16 build patterns and 11 rank tiers, '
        'the system produces strategic advice differentiated by player skill level. The complete 4,087-line system '
        'operates independently without any external LLM dependency, and articulates a new research direction: the '
        'transition from descriptive statistics to prescriptive feedback.',
        S_ABSTRACT))
    story.append(Paragraph(
        f'{B("Keywords")}: Tetris AI, automated coaching, replay analysis, weakness classification, machine learning, '
        'esports, prescriptive feedback, build patterns',
        S_KW))
    story.append(hr())

    # ── AI Disclosure ──
    story.append(Paragraph(B('AI Disclosure Statement'), S_H3))
    story.append(Paragraph(
        'Anthropic&#39;s large language model Claude was used as an assistive tool during system design, code '
        'implementation, literature search, and structuring of this manuscript. Claude assisted with code drafting, '
        'academic literature retrieval, and suggesting the outline structure of the paper; however, all research-design '
        'decisions, experimental design, interpretation of results, and final judgment of academic claims were made by '
        'the author, ChangHo Lee. Because Claude cannot bear research accountability or legal responsibility, it is not '
        'included in the author list. This disclosure is provided transparently in accordance with the AI-use guidelines '
        'of major venues such as IEEE, ACM, and Nature.',
        S_BODY))
    story.append(hr())

    # ═══ I. Introduction ═══
    story.append(Paragraph('I. Introduction', S_H1))

    story.append(Paragraph('1.1 Background and Motivation', S_H2))
    story.append(Paragraph(
        'Since its creation by Alexey Pajitnov in 1984, the competitive puzzle game Tetris has remained, for four '
        'decades, one of the most widely played video games worldwide. The online versus platform TETR.IO, in '
        'particular, recorded more than 9.5 million registered users and over one billion cumulative games as of 2026, '
        'illustrating how the competitive dimension of Tetris has grown into a significant segment of the esports '
        'ecosystem.',
        S_BODY))
    story.append(Paragraph(
        'Nevertheless, coaching systems that systematically support player improvement remain underexplored, both '
        'academically and commercially. Approaches that rely on human coaches scale poorly, while the recently emerging '
        'LLM-based coaching carries inherent limitations such as hallucination, API cost, and non-deterministic output.',
        S_BODY))

    story.append(Paragraph('1.2 Research Objectives and Questions', S_H2))
    story.append(Paragraph(
        'Prior to any clinical validation of coaching efficacy, the objective of this study is to demonstrate the '
        'algorithmic validity and computational efficiency (&lt;100 ms) of a comprehensive pipeline that converts 7.7M '
        'fragmented placement-level play records into natural-language feedback. In other words, this paper constitutes a '
        'proposal of a system architecture and data-abstraction framework rather than a clinical study; a quantitative '
        'user study of the efficacy of the prescriptive feedback is explicitly designated as future work (Section 5.2).',
        S_BODY))
    story.append(Paragraph('Within this scope, this study seeks to answer the following three research questions:', S_BODY))
    story.append(Paragraph('RQ1. Can player weakness types be automatically classified from large-scale replay data?', S_BULLET))
    story.append(Paragraph('RQ2. Can feedback grounded in the classified weaknesses be differentiated across player skill levels?', S_BULLET))
    story.append(Paragraph('RQ3. Does structuring domain-specific knowledge (build patterns, tier benchmarks) improve feedback quality?', S_BULLET))

    story.append(Paragraph('1.3 Contributions', S_H2))
    story.append(Paragraph('The central contribution (hook) of this work is as follows:', S_BODY))
    story.append(Paragraph(I(
        '"Whereas prior Tetris AI research (Dellacherie, 2003; Thiery &amp; Scherrer, 2009; Gabillon et al., 2013) '
        'focused on how well a bot plays, this study addresses a fundamentally different question: how effectively '
        'a human player can be taught."'),
        S_QUOTE))
    story.append(Paragraph('&#8226; Descriptive-to-prescriptive shift: beyond descriptive statistics, we build a pipeline of ML-based weakness classification &#8594; tier benchmark comparison &#8594; tailored training prescription.', S_BULLET))
    story.append(Paragraph('&#8226; Multi-level data abstraction: 7.7M placement-level records are transformed into natural-language coaching through six abstraction stages.', S_BULLET))
    story.append(Paragraph('&#8226; Structured domain knowledge: the first cross-recommendation matrix of 16 build patterns &#215; 11 rank tiers.', S_BULLET))

    # ═══ II. Theoretical Background ═══
    story.append(PageBreak())
    story.append(Paragraph('II. Theoretical Background', S_H1))

    story.append(Paragraph('2.1 Academic Lineage of Tetris AI', S_H2))
    story.append(Paragraph(
        'Tetris has been proven NP-complete (Breukelaar et al., 2004), and the number of possible states on a 10&#215;20 '
        'board reaches 2<super>200</super>, rendering an exact MDP solution intractable (Bodoia &amp; Puranik, 2012). '
        'Heuristic-based approaches have therefore dominated the field.',
        S_BODY))
    story.append(Paragraph(
        'Dellacherie (2003) proposed a linear evaluation function composed of six features&#8212;landing height, row and '
        'column transitions, holes, wells, and eroded cells&#8212;achieving an average of 660,000 cleared lines; '
        'Thiery &amp; Scherrer (2009) subsequently validated and improved this line of work using the Cross-Entropy method. '
        'Gabillon et al. (NeurIPS, 2013) surpassed these results with approximate dynamic programming, and Cold Clear '
        '(MinusKelvin, 2019) evolved the weights of more than 20 features via a genetic algorithm, becoming the de facto '
        'standard for modern Tetris bots. Erkalkan (2026) reported a +61.79% performance gain over fixed weights through '
        'GA-based dynamic weight adjustment.',
        S_BODY))

    story.append(Paragraph('2.2 AI Coaching in Esports', S_H2))
    story.append(Paragraph(
        'Research applying game AI to player coaching has grown rapidly in recent years. Google DeepMind&#39;s TacticAI '
        '(2024) applied ML to football tactical analysis, and Jing et al. (2025) analyzed twelve years of professional '
        'Counter-Strike performance using SHAP-based interpretable ML. However, an integrated framework that '
        'automatically classifies weaknesses from replay data and combines them with domain-specific knowledge to '
        'generate prescriptive feedback has not yet been systematically established in the literature.',
        S_BODY))

    story.append(Paragraph('2.3 Machine-Learning-Based Player Profiling', S_H2))
    story.append(Paragraph(
        'Gradient Boosting (Friedman, 2001) sequentially constructs an ensemble of weak learners to maximize '
        'classification and regression performance, and is known to perform strongly on tabular data. In this study, '
        'it is used to classify a player&#39;s principal weakness type (speed, attack, tspin, finesse, defense, balanced) '
        'from a 10-dimensional feature vector extracted from real game data.',
        S_BODY))

    # ═══ III. Methodology ═══
    story.append(Paragraph('III. Methodology', S_H1))

    story.append(Paragraph('3.1 System Architecture', S_H2))
    story.append(Paragraph(
        'TetrioCoach is designed as a four-layer architecture: '
        '(L1) Data Acquisition&#8212;TETR.IO API, local .ttrm files, the Kaggle dataset, and the build-pattern database; '
        '(L2) Statistical Analysis&#8212;the aggregation engine, board simulator, play-style analyzer, and build detector; '
        '(L3) AI Intelligence&#8212;the ML weakness classifier, rule-based evaluator, and heuristic board evaluator; '
        '(L4) Feedback Generation&#8212;the coaching report, training roadmap, build advisor, and matchup advice.',
        S_BODY))
    story.append(Paragraph(I('[Fig. 1: TetrioCoach Multi-Layer Architecture &#8212; insertion point]'), S_BODY))

    story.append(Paragraph('3.2 Data Collection and Preprocessing', S_H2))
    story.append(Paragraph(
        'Data are collected through three channels. '
        '(1) The public TETR.IO API (ch.tetr.io/api) provides leaderboard and match-record queries, yielding summary '
        'statistics such as APM, PPS, VS, and garbage sent/received. '
        '(2) Direct parsing of local .ttrm files extracts detailed statistics&#8212;T-Spin types (TSS/TSD/TST/Mini), line '
        'clears, finesse, and placement counts&#8212;from the replay.results.stats path. '
        '(3) The public Kaggle dataset (n3koasakura, 2024) supplies 7,716,524 placement-level records from 61,935 matches '
        'of the top 500 players; each placement includes the board state (playfield), T-Spin type, combo, B2B, garbage, '
        'and Glicko-2 rating.',
        S_BODY))

    story.append(Paragraph('3.2.1 All-Tier Benchmark Collection', S_H3))
    story.append(Paragraph(
        'Because placement-level detail (T-Spin, finesse, etc.) exists only in the Kaggle dataset (top 500 players), the '
        'ML style classifier is trained on elite data. To let the evaluation/feedback layer assess lower-tier players '
        'against the distribution of their own tier rather than against absolute thresholds, we randomly sampled 100 '
        'players from each of 11 tiers (C, B, B+, A, A+, S, S+, SS, U, X, X+; the X+ tier contains only 80 players in '
        'total) from the public TETR.IO leaderboard API, collecting the APM/PPS/VS/TR distributions of 1,080 players in '
        'all (Table 3). This separation is a central methodological decision of this work: style archetypes are learned '
        'most cleanly from low-noise elite data, whereas skill-level calibration is performed using the empirical '
        'distributions of every tier.',
        S_BODY))
    tier_rows = [
        ('X+', '24,317', '169.8', '3.27', '339.8'), ('X', '23,209', '130.8', '2.82', '266.3'),
        ('U', '22,229', '107.8', '2.49', '223.0'), ('SS', '19,928', '79.2', '2.04', '163.3'),
        ('S+', '17,879', '57.5', '1.79', '122.1'), ('S', '16,223', '46.4', '1.63', '98.8'),
        ('A+', '13,248', '33.8', '1.37', '72.3'), ('A', '11,466', '27.2', '1.24', '59.2'),
        ('B+', '8,145', '20.9', '1.11', '45.3'), ('B', '6,435', '18.9', '1.04', '40.5'),
        ('C', '2,539', '13.0', '0.87', '27.0'),
    ]
    tb3 = [[Paragraph(B('Tier'), S_TBL_H), Paragraph(B('TR (mean)'), S_TBL_H), Paragraph(B('APM'), S_TBL_H),
            Paragraph(B('PPS'), S_TBL_H), Paragraph(B('VS'), S_TBL_H)]]
    for t, tr, apm, pps, vs in tier_rows:
        tb3.append([Paragraph(t, S_TBL_C), Paragraph(tr, S_TBL_C), Paragraph(apm, S_TBL_C),
                    Paragraph(pps, S_TBL_C), Paragraph(vs, S_TBL_C)])
    t3 = Table(tb3, colWidths=[55, 72, 55, 50, 55])
    t3.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), LIGHT_BG), ('GRID', (0, 0), (-1, -1), 0.4, LINE_COLOR),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'), ('TOPPADDING', (0, 0), (-1, -1), 2.5), ('BOTTOMPADDING', (0, 0), (-1, -1), 2.5),
    ]))
    story.append(Paragraph(I('[Table 3] Empirical all-tier benchmark (1,080 players; 100 per tier, 80 for X+)'), S_H3))
    story.append(t3)
    story.append(Paragraph(
        'APM/PPS/VS increase monotonically with tier, and tier estimation is performed by nearest-centroid matching '
        '(normalized Euclidean distance) against these 11 tier means. In a self-consistency check, the mean profile of '
        'every one of the 11 tiers was classified back to its own tier.',
        S_BODY))

    story.append(Paragraph('3.3 Statistical Aggregation Engine', S_H2))
    story.append(Paragraph(
        'More than 30 metrics are computed from the collected round data: win rate (match/round), mean APM/PPS/VS, counts '
        'and ratios by T-Spin type, line-clear distribution (Single/Double/Triple/Quad), finesse fault ratio, garbage '
        'pressure ratio, maximum combo/B2B/spike, and APM/PPS trends. Differences in data availability between the online '
        'API and local .ttrm files are managed via a has_detail flag, so that missing data are handled explicitly in both '
        'the UI and the AI analysis.',
        S_BODY))

    story.append(Paragraph('3.4 ML Weakness Classifier', S_H2))
    story.append(Paragraph(
        'To avoid circular reasoning, the ML classifier adopts a two-stage approach. '
        '(Stage 1) K-Means clustering (k=8) derives natural clusters from the 10-dimensional feature vectors of 20,000 '
        'games. The ten features are: (1) PPS, (2) estimated APM (attack/piece &#215; 60), (3) T-Spin rate (%), '
        '(4) Quad rate (%), (5) lines per piece, (6) maximum combo, (7) maximum B2B, (8) maximum board height, '
        '(9) defense ratio (garbage cleared/received), and (10) rating_norm (TR/1000). Weakness labels are then mapped '
        'from each cluster&#39;s profile (the z-scores of these features relative to the global mean). In this way, labels '
        'are derived from the structure of the data itself rather than from hard-coded rules over the input variables. '
        '(Stage 2) A GradientBoostingClassifier (n_estimators=200, max_depth=6) is trained on the cluster labels to '
        'predict the weaknesses of new players.',
        S_BODY))
    story.append(Paragraph(
        'At inference time, a hybrid prediction combines the ML probability (weight 0.4) with a rule-based score '
        '(weight 0.6). This compensates for the scale mismatch between the training data (top 500 players) and general '
        'players. Class imbalance is addressed with noise-injection oversampling (min_ratio=0.10), and final performance '
        'is reported with the Macro-averaged F1-score rather than plain accuracy.',
        S_BODY))
    story.append(Paragraph(
        B('Rationale for the two-stage pipeline (K-Means &#8594; Gradient Boosting):') + ' '
        'This structure performs surrogate learning of the geometric decision boundary of K-Means with a supervised model, '
        'so a high F1-score is mathematically expected. The benefits of nonetheless adopting the two-stage structure are: '
        '(1) whereas K-Means assigns a discrete label to new data based solely on the distance to the nearest centroid, '
        'Gradient Boosting provides a probability distribution (predict_proba) that enables soft judgments on borderline '
        'cases; (2) when ML probabilities are weighted and fused with rule-based scores during hybrid inference, a '
        'supervised model that yields continuous probabilities permits more flexible fusion than discrete cluster '
        'assignment; and (3) inference proceeds immediately with the pre-trained classifier without re-running K-Means, '
        'securing the computational efficiency suited to the real-time response (&lt;100 ms) of the GUI application.',
        S_BODY))

    story.append(Paragraph(I('[Table 1] Performance of the ML Weakness Classifier (K-Means labeling + oversampling)'), S_H3))
    tbl1 = [
        [Paragraph(B('Class'), S_TBL_H), Paragraph(B('Precision'), S_TBL_H), Paragraph(B('Recall'), S_TBL_H), Paragraph(B('F1'), S_TBL_H), Paragraph(B('Support'), S_TBL_H)],
        [Paragraph('attack', S_TBL), Paragraph('0.97', S_TBL_C), Paragraph('0.97', S_TBL_C), Paragraph('0.97', S_TBL_C), Paragraph('1,293', S_TBL_C)],
        [Paragraph('defense', S_TBL), Paragraph('0.96', S_TBL_C), Paragraph('0.97', S_TBL_C), Paragraph('0.96', S_TBL_C), Paragraph('1,106', S_TBL_C)],
        [Paragraph('speed', S_TBL), Paragraph('0.96', S_TBL_C), Paragraph('0.96', S_TBL_C), Paragraph('0.96', S_TBL_C), Paragraph('1,017', S_TBL_C)],
        [Paragraph('tspin', S_TBL), Paragraph('0.95', S_TBL_C), Paragraph('0.93', S_TBL_C), Paragraph('0.94', S_TBL_C), Paragraph('584', S_TBL_C)],
        [Paragraph(B('Macro avg'), S_TBL), Paragraph(B('0.96'), S_TBL_C), Paragraph(B('0.96'), S_TBL_C), Paragraph(B('0.96'), S_TBL_C), Paragraph(B('4,000'), S_TBL_C)],
    ]
    t1 = Table(tbl1, colWidths=[80, 70, 60, 50, 60])
    t1.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), LIGHT_BG), ('GRID', (0, 0), (-1, -1), 0.4, LINE_COLOR),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'), ('TOPPADDING', (0, 0), (-1, -1), 3), ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    story.append(t1)
    story.append(Spacer(1, 8))

    story.append(Paragraph('3.5 Build-Pattern Knowledge Base', S_H2))
    story.append(Paragraph(
        'A structured database of 16 build patterns&#8212;collected from the Hard Drop Wiki and FOUR.lol (TKI, DT Cannon, '
        'PCO, Hachispin, Albatross, MKO, C-Spin, STSD, LST Stacking, Imperial Cross, Fractal, 4-wide, 6-3 Stacking, '
        'Downstacking, etc.)&#8212;was constructed. Each build records its category (opener/midgame/strategy/defense), '
        'required bag count, attack type, output lines, prerequisites, coverage, difficulty, applicable tier, and '
        'strength/weakness/counter strategy; from these, a matrix of optimal build recommendations across 11 tiers '
        '(C&#8211;X+) was assembled.',
        S_BODY))
    story.append(Paragraph(
        'To ensure the objectivity of the build-tier mapping, the applicable tier for each build was determined by '
        'cross-referencing (1) the per-build difficulty and prerequisites specified in the Hard Drop Wiki and FOUR.lol, '
        'and (2) community statistics and open-source guides on the TR ranges in which each build is used in practice '
        '(e.g., 4-wide is effective at intermediate ranges but is countered at higher ranges, whereas continuous T-Spin '
        'builds such as Albatross/Fractal are mainly used in the X+ range). The mapping rules thus rest on publicly '
        'available domain knowledge and community consensus rather than the author&#39;s arbitrary judgment. Quantitative '
        'validation of this mapping by an expert panel remains future work.',
        S_BODY))

    story.append(Paragraph('3.6 Feedback Generation Pipeline', S_H2))
    story.append(Paragraph(
        'Feedback generation proceeds as follows: (1) statistical aggregation via compute_aggregates_v2() &#8594; '
        '(2) construction of a PlayerProfile via build_profile_from_agg() &#8594; (3) generation of a WeaknessReport list '
        'via evaluate_profile() (6 categories, 4 severity levels, priority scores) &#8594; (4) ML weakness prediction via '
        'predict_weakness() &#8594; (5) generation of a coaching report (8 sections) + training roadmap (tier-specific '
        '20-minute routine) + matchup advice (counters to opponent builds). The entire process completes locally within '
        '100 ms without any external API call.',
        S_BODY))

    # ═══ IV. Results ═══
    story.append(PageBreak())
    story.append(Paragraph('IV. Results', S_H1))

    story.append(Paragraph('4.1 ML Model Performance', S_H2))
    story.append(Paragraph(
        'After K-Means-based labeling and oversampling, the Gradient Boosting classifier achieved an Accuracy of 0.962, '
        'a Macro F1-score of 0.960, and a 5-fold CV Macro F1 of 0.956 (&#177;0.003) on the test set (n=4,000). To avoid '
        'the well-known problem whereby plain accuracy is inflated by majority classes under class imbalance, this study '
        'adopts the Macro F1-score as the primary evaluation metric. Oversampling balanced the support across the four '
        'classes (attack, defense, speed, tspin) to a range of 584&#8211;1,293 (improved from the previously extreme '
        'imbalance of 12&#8211;12,908), so that Accuracy (0.962) and Macro F1 (0.960) converge to within 0.002. This '
        'indicates that classification performance is uniformly secured across all classes, and the small gap between the '
        'two metrics attests to the success of the balancing.',
        S_BODY))
    story.append(Paragraph(
        'Feature-importance analysis showed that lines_per_piece (28.6%) was the most important variable, followed by '
        'rating_norm (21.7%), max_btb (15.9%), and tspin_rate (6.4%). The dominance of tspin_rate (73.9%) in the previous '
        'version was attributable to the circular reasoning of rule-based labeling; under unsupervised clustering, line '
        'efficiency and overall rating emerged as the key variables for weakness discrimination. This implies that the '
        'model discriminates weaknesses through a multi-dimensional combination of features rather than a single metric.',
        S_BODY))
    story.append(Paragraph(
        B('A note on the rating_norm variable.') + ' In this study, rating_norm is a scale-normalized variable defined as '
        'the Kaggle dataset&#39;s TR (Tetra Rating) divided by 1000 (mean &#8776; 24.9 for the top 500 players). Because '
        'the training data are concentrated in the single X+ band, its standard deviation is small (0.095); the model '
        'uses subtle inter-cluster rating differences as an auxiliary signal during training, but at inference time the '
        'new player&#39;s TR is unknown and is therefore fixed to the training mean (24.9). Consequently, the 21.7% '
        'importance of rating_norm reflects a contribution within the training distribution; in actual inference it acts '
        'as a population-level anchor rather than a discriminative variable distinguishing individual players. Replacing '
        'rating_norm with measured values once all-tier data are obtained is a future improvement that would restore its '
        'discriminative power.',
        S_BODY))
    story.append(Paragraph(I('[Fig. 2: Feature Importance Bar Chart &#8212; insertion point]'), S_BODY))

    story.append(Paragraph('4.2 Comparison with Prior Approaches', S_H2))
    story.append(Paragraph(I('[Table 2] Comparison with prior Tetris AI approaches'), S_H3))
    tbl2 = [
        [Paragraph(B('Study'), S_TBL_H), Paragraph(B('Objective'), S_TBL_H), Paragraph(B('Method'), S_TBL_H), Paragraph(B('Output'), S_TBL_H)],
        [Paragraph('Dellacherie (2003)', S_TBL), Paragraph('Optimal play', S_TBL_C), Paragraph('6-feature heuristic', S_TBL), Paragraph('Placement', S_TBL_C)],
        [Paragraph('Gabillon et al. (2013)', S_TBL), Paragraph('Optimal play', S_TBL_C), Paragraph('ADP value function', S_TBL), Paragraph('Placement', S_TBL_C)],
        [Paragraph('Cold Clear (2019)', S_TBL), Paragraph('Optimal play', S_TBL_C), Paragraph('GA weight evolution', S_TBL), Paragraph('Placement', S_TBL_C)],
        [Paragraph('Erkalkan (2026)', S_TBL), Paragraph('Optimal play', S_TBL_C), Paragraph('GA dynamic weights', S_TBL), Paragraph('Placement', S_TBL_C)],
        [Paragraph(B('TetrioCoach (this work)'), S_TBL), Paragraph(B('Human coaching'), S_TBL_C), Paragraph(B('ML classification + rules + domain knowledge'), S_TBL), Paragraph(B('Natural-language feedback'), S_TBL_C)],
    ]
    t2 = Table(tbl2, colWidths=[100, 70, 130, 80])
    t2.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), LIGHT_BG), ('BACKGROUND', (0, -1), (-1, -1), HexColor('#e8f0fe')),
        ('GRID', (0, 0), (-1, -1), 0.4, LINE_COLOR), ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 4), ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(t2)
    story.append(Spacer(1, 8))

    story.append(Paragraph('4.3 Case Studies', S_H2))

    # Case 1
    story.append(Paragraph(B('Case 1: Longitudinal Growth Analysis (Subject P, 37 matches over one year)'), S_H3))
    story.append(Paragraph(
        'One year of replay data (37 .ttrm files) from a single player was partitioned into three periods and analyzed: '
        'early (2025-06 to 08), mid (2025-12 to 2026-03), and recent (2026-06).',
        S_BODY))
    growth = [
        [Paragraph(B('Period'), S_TBL_H), Paragraph(B('Rounds'), S_TBL_H), Paragraph(B('APM'), S_TBL_H),
         Paragraph(B('PPS'), S_TBL_H), Paragraph(B('Win%'), S_TBL_H), Paragraph(B('T-Spin%'), S_TBL_H),
         Paragraph(B('Fault%'), S_TBL_H), Paragraph(B('ML pred.'), S_TBL_H)],
        [Paragraph('Early (2025-06~08)', S_TBL), Paragraph('31', S_TBL_C), Paragraph('49.3', S_TBL_C),
         Paragraph('1.81', S_TBL_C), Paragraph('54.8%', S_TBL_C), Paragraph('4.1%', S_TBL_C),
         Paragraph('61.3%', S_TBL_C), Paragraph('attack (0.48)', S_TBL_C)],
        [Paragraph('Mid (2025-12~2026-03)', S_TBL), Paragraph('41', S_TBL_C), Paragraph('45.9', S_TBL_C),
         Paragraph('1.75', S_TBL_C), Paragraph('56.1%', S_TBL_C), Paragraph('3.9%', S_TBL_C),
         Paragraph('58.3%', S_TBL_C), Paragraph('attack (0.52)', S_TBL_C)],
        [Paragraph(B('Recent (2026-06)'), S_TBL), Paragraph(B('16'), S_TBL_C), Paragraph(B('55.1'), S_TBL_C),
         Paragraph(B('1.92'), S_TBL_C), Paragraph(B('62.5%'), S_TBL_C), Paragraph(B('4.3%'), S_TBL_C),
         Paragraph(B('55.8%'), S_TBL_C), Paragraph(B('finesse (0.56)'), S_TBL_C)],
    ]
    tg = Table(growth, colWidths=[98, 40, 36, 34, 38, 42, 42, 56])
    tg.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), LIGHT_BG), ('BACKGROUND', (0, -1), (-1, -1), HexColor('#e8f0fe')),
        ('GRID', (0, 0), (-1, -1), 0.4, LINE_COLOR), ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 3), ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    story.append(Paragraph(I('[Table 4] Longitudinal growth trajectory of Subject P (over one year)'), S_H3))
    story.append(tg)
    story.append(Paragraph(
        'Over one year, APM rose from 49.3 to 55.1, PPS from 1.81 to 1.92, and the win rate from 54.8% to 62.5%. The '
        'finesse fault improved from 61.3% to 55.8% but remained at a critical level. Notably, the hybrid ML prediction '
        'ranked &quot;attack&quot; first in the early and mid periods (0.48&#8211;0.52) and shifted to &quot;finesse&quot; '
        '(0.56) in the recent period (with the secondary weakness also alternating between attack and finesse). This is '
        'interpreted as the model capturing a growth pattern in which, as APM improved from 49.3 to 55.1, the attack '
        'weakness was relatively resolved while finesse emerged as the new principal bottleneck. The fact that the weakness '
        'diagnosis migrates over time within a single subject&#39;s longitudinal data demonstrates that the model does not '
        'simply converge to a fixed label but responds to changes in the input metrics.',
        S_BODY))
    story.append(Spacer(1, 6))

    # Case 2
    story.append(Paragraph(B('Case 2: A High-Level, Balanced Player (Player A, anonymized)'), S_H3))
    story.append(Paragraph(
        'With PPS 2.36 (fast), APM 54.1, a T-Spin rate of 4.33%, and a finesse fault of 6.8% (excellent), all core '
        'metrics are balanced and accuracy is particularly strong. The hybrid ML model predicted &quot;balanced&quot; as '
        'the top label (confidence 0.58), and the rule-based evaluator likewise drove the finesse weakness score nearly '
        'to zero. Based on an estimated S tier, the system recommended TKI, DT Cannon, Hachispin, and STSD, and generated '
        'maintenance-oriented feedback to &quot;sustain the current level while targeting the next tier.&quot; This shows '
        'that the system correctly identifies a balanced player with no salient weakness.',
        S_BODY))
    story.append(Spacer(1, 6))

    # Case 3
    story.append(Paragraph(B('Case 3: A Slow, Low-T-Spin Player (Player C, anonymized)'), S_H3))
    story.append(Paragraph(
        'With PPS 1.56 (slow), APM 50.9, a T-Spin rate of 1.55% (low), and a finesse fault of 17.9% (sound), the hybrid '
        'ML model predicted &quot;speed&quot; as the top label (confidence 0.58), and the rule-based evaluator likewise '
        'detected the low PPS as the principal weakness. Accuracy (fault 17.9%) is relatively sound, but the player '
        'exhibits a pattern of insufficient speed and T-Spin utilization; the system, based on an estimated A tier, '
        'recommended TKI/DT Cannon/STSD and placed &quot;three 40L sprints as a speed-sense warm-up&quot; first in the '
        '20-minute routine, generating a prescription that prioritizes speed improvement above all.',
        S_BODY))
    story.append(Spacer(1, 6))

    # Case 4
    story.append(Paragraph(B('Case 4: Multi-Player Comparative Analysis'), S_H3))
    comp = [
        [Paragraph(B('Metric'), S_TBL_H), Paragraph(B('Subject P'), S_TBL_H),
         Paragraph(B('Player A'), S_TBL_H), Paragraph(B('Player B'), S_TBL_H), Paragraph(B('Player C'), S_TBL_H)],
        [Paragraph('PPS', S_TBL), Paragraph('1.83', S_TBL_C), Paragraph(B('2.36'), S_TBL_C), Paragraph('1.62', S_TBL_C), Paragraph('1.56', S_TBL_C)],
        [Paragraph('APM', S_TBL), Paragraph('51.0', S_TBL_C), Paragraph('54.1', S_TBL_C), Paragraph('53.9', S_TBL_C), Paragraph('50.9', S_TBL_C)],
        [Paragraph('T-Spin%', S_TBL), Paragraph('4.82', S_TBL_C), Paragraph('4.33', S_TBL_C), Paragraph('4.54', S_TBL_C), Paragraph('1.55', S_TBL_C)],
        [Paragraph('Fault%', S_TBL), Paragraph('57.7', S_TBL_C), Paragraph(B('6.8'), S_TBL_C), Paragraph('36.6', S_TBL_C), Paragraph('17.9', S_TBL_C)],
        [Paragraph('Est. tier', S_TBL), Paragraph('S', S_TBL_C), Paragraph('S', S_TBL_C), Paragraph('A+', S_TBL_C), Paragraph('A', S_TBL_C)],
        [Paragraph('ML top-1', S_TBL), Paragraph('attack/finesse', S_TBL_C), Paragraph(B('balanced'), S_TBL_C), Paragraph(B('attack'), S_TBL_C), Paragraph(B('speed'), S_TBL_C)],
        [Paragraph('Confidence', S_TBL), Paragraph('0.46/0.46', S_TBL_C), Paragraph('0.58', S_TBL_C), Paragraph('0.41', S_TBL_C), Paragraph('0.58', S_TBL_C)],
        [Paragraph('Rx focus', S_TBL), Paragraph('accuracy+attack', S_TBL_C), Paragraph('maintenance', S_TBL_C), Paragraph('attack builds', S_TBL_C), Paragraph('speed', S_TBL_C)],
    ]
    tc = Table(comp, colWidths=[62, 78, 72, 72, 72])
    tc.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), LIGHT_BG), ('GRID', (0, 0), (-1, -1), 0.4, LINE_COLOR),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'), ('TOPPADDING', (0, 0), (-1, -1), 3), ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    story.append(Paragraph(I('[Table 5] Multi-player comparative analysis (reproducible data)'), S_H3))
    story.append(tc)
    story.append(Paragraph(
        'For four players with distinct metric profiles, the hybrid ML model predicted four different top-1 weaknesses: '
        'Player A (excellent accuracy at 6.8% fault, PPS 2.36) was &quot;balanced&quot; (0.58); Player B (fault 36.6%, '
        'medium speed) was &quot;attack&quot; (0.41); Player C (slow at PPS 1.56, T-Spin 1.55%) was &quot;speed&quot; '
        '(0.58); and Subject P (fault 57.7%) showed a tie between &quot;attack&quot; and &quot;finesse&quot; at 0.46. The '
        'predictions thus differentiate clearly according to differences in the input profile (accuracy, speed, T-Spin '
        'utilization).',
        S_BODY))
    story.append(Paragraph(
        B('Error analysis of weakness convergence.') + ' In a preliminary analysis, when only players from the same '
        'narrow skill band (S&#8211;SS) with similarly high finesse faults (54&#8211;58%) were considered, the predictions '
        'were observed to converge to finesse. Rather than a bias of the model itself, this is a consequence of the input '
        'group&#39;s shared weakness being faithfully reflected under a structure in which the rule-based score (weight '
        '0.6) is dominant in the hybrid prediction. As shown in Table 5, when players with heterogeneous accuracy, speed, '
        'and T-Spin utilization are provided as input, the predictions normally diverge into balanced/attack/speed/finesse; '
        'the convergence phenomenon is therefore confirmed to stem from the homogeneity of the input sample. That said, a '
        'structural characteristic remains whereby, because the rule-based weight (0.6) exceeds that of the ML model (0.4), '
        'the rule score prevails in borderline cases; securing all-tier training data would allow the ML weight to be '
        'raised to strengthen data-driven classification.',
        S_BODY))
    story.append(Paragraph(
        B('Qualitative contrast of final prescriptions.') + ' Between players with different ML top-1 labels, the '
        'downstream prescriptions diverge clearly. For Player A (judged &quot;balanced&quot;), the first step of the '
        '20-minute routine was &quot;10 repetitions of the TKI opener pattern&quot; (mastering attack builds), whereas for '
        'Player C (judged &quot;speed&quot;), &quot;three 40L sprints as a speed-sense warm-up&quot; was placed first. '
        'In addition, the build-recommendation set varied by estimated tier (S/S/A+/A): high-difficulty openers such as '
        'PCO and Hachispin were presented to Players A and B, while a foundational STSD-centered build set was presented '
        'to Player C. This demonstrates that the combination of ML label &#8594; tier estimation &#8594; build matrix '
        '&#8594; weakness priority generates qualitatively distinct training prescriptions per player.',
        S_BODY))

    # Case 5
    story.append(Paragraph(B('Case 5: Subject P&#39;s Growth Against the S&#8211;U Tier Benchmark'), S_H3))
    story.append(Paragraph(
        'Ten players were randomly sampled from each of the S, S+, SS, and U tiers via the public TETR.IO leaderboard API, '
        'their mean statistics were computed, and they were compared against Subject P&#39;s longitudinal growth trajectory.',
        S_BODY))
    bench = [
        [Paragraph(B('Group/Tier'), S_TBL_H), Paragraph(B('TR'), S_TBL_H), Paragraph(B('APM'), S_TBL_H),
         Paragraph(B('PPS'), S_TBL_H), Paragraph(B('VS'), S_TBL_H), Paragraph(B('Win%'), S_TBL_H), Paragraph(B('n'), S_TBL_H)],
        [Paragraph('S tier avg', S_TBL), Paragraph('14,996', S_TBL_C), Paragraph('39.7', S_TBL_C), Paragraph('1.45', S_TBL_C), Paragraph('86.5', S_TBL_C), Paragraph('45.3%', S_TBL_C), Paragraph('10', S_TBL_C)],
        [Paragraph('S+ tier avg', S_TBL), Paragraph('16,276', S_TBL_C), Paragraph('42.9', S_TBL_C), Paragraph('1.43', S_TBL_C), Paragraph('96.7', S_TBL_C), Paragraph('24.8%', S_TBL_C), Paragraph('10', S_TBL_C)],
        [Paragraph('SS tier avg', S_TBL), Paragraph('17,861', S_TBL_C), Paragraph('58.0', S_TBL_C), Paragraph('1.74', S_TBL_C), Paragraph('121.6', S_TBL_C), Paragraph('30.7%', S_TBL_C), Paragraph('10', S_TBL_C)],
        [Paragraph('U tier avg', S_TBL), Paragraph('20,163', S_TBL_C), Paragraph('79.9', S_TBL_C), Paragraph('2.05', S_TBL_C), Paragraph('167.0', S_TBL_C), Paragraph('33.5%', S_TBL_C), Paragraph('10', S_TBL_C)],
        [Paragraph(I('Subject P early'), S_TBL), Paragraph('-', S_TBL_C), Paragraph(I('49.3'), S_TBL_C), Paragraph(I('1.81'), S_TBL_C), Paragraph(I('108.7'), S_TBL_C), Paragraph(I('54.8%'), S_TBL_C), Paragraph('31R', S_TBL_C)],
        [Paragraph(I('Subject P mid'), S_TBL), Paragraph('-', S_TBL_C), Paragraph(I('45.9'), S_TBL_C), Paragraph(I('1.75'), S_TBL_C), Paragraph(I('94.1'), S_TBL_C), Paragraph(I('56.1%'), S_TBL_C), Paragraph('41R', S_TBL_C)],
        [Paragraph(B('Subject P recent'), S_TBL), Paragraph(B('-'), S_TBL_C), Paragraph(B('55.1'), S_TBL_C), Paragraph(B('1.92'), S_TBL_C), Paragraph(B('119.4'), S_TBL_C), Paragraph(B('62.5%'), S_TBL_C), Paragraph(B('16R'), S_TBL_C)],
    ]
    tb = Table(bench, colWidths=[82, 50, 42, 40, 42, 45, 30])
    tb.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), LIGHT_BG), ('BACKGROUND', (0, 5), (-1, 7), HexColor('#f5f0ff')),
        ('GRID', (0, 0), (-1, -1), 0.4, LINE_COLOR), ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 3), ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    story.append(Paragraph(I('[Table 6] Position of Subject P against the S&#8211;U tier benchmark'), S_H3))
    story.append(tb)
    story.append(Paragraph(
        'Subject P&#39;s recent metrics (APM 55.1, PPS 1.92, VS 119.4) are close to the SS tier averages (APM 58.0, PPS '
        '1.74, VS 121.6), exceeding the SS average in PPS. APM, however, falls slightly short of the SS average, so the '
        'tier benchmark objectively supports the system&#39;s diagnosis that &quot;attack-conversion efficiency&quot; is '
        'the next growth point. The one-year trajectory shows a rise from the S level (early) to near-SS (recent), '
        'providing indirect corroborating evidence consistent with the improvement direction suggested by TetrioCoach&#39;s '
        'feedback.',
        S_BODY))
    story.append(Spacer(1, 6))

    # ═══ V. Discussion ═══
    story.append(Paragraph('V. Discussion', S_H1))

    story.append(Paragraph('5.1 Academic Significance', S_H2))
    story.append(Paragraph(
        'By demonstrating (1) a multi-level abstraction framework for Tetris replay data, (2) the empirical viability of '
        'ML-based automatic weakness classification, and (3) the contribution of structured domain knowledge (build '
        'patterns &#215; tiers) to feedback quality, this study opens up a new research area of replay-based automated '
        'coaching.',
        S_BODY))
    story.append(Paragraph(
        B('Justification of the data design by separation of concerns.') + ' '
        'The system trains its ML style classifier on the curated placement-level data of the top 500 players. This is a '
        'deliberate choice: rather than contaminating the classification boundary with noisy lower-tier data, it learns '
        'the geometric decision boundary of the most idealized build efficiency and play styles more precisely. At the '
        'same time, skill-level calibration is carried out separately using the empirically collected distributions of '
        'all 11 tiers (1,080 players, Table 3), so that lower-tier players are also assessed against the norms of their '
        'own tier. By separating style classification (elite data) from level calibration (all-tier data), the design '
        'structurally prevents the bias of any single dataset from contaminating both. The fixing of rating_norm at '
        'inference time, discussed in Section 4.1, is a consistent corollary of this separation.',
        S_BODY))

    story.append(Paragraph('5.2 Limitations', S_H2))
    story.append(Paragraph('&#8226; Tier range of the ML training data: because placement-level detail exists only for the '
        'Kaggle top 500, the ML style classifier is trained on elite data. The evaluation/tier-calibration layer is '
        'complemented with the empirical distributions of all 11 tiers (1,080 players, Section 3.2.1); however, '
        'placement-level data (T-Spin, finesse, etc.) for lower tiers are collectable only with a bot account, so '
        'retraining the classifier itself on all-tier data remains future work.', S_BULLET))
    story.append(Paragraph('&#8226; Labeling methodology: although K-Means clustering improves upon the circular reasoning of '
        'rule-based labeling, comparison against a gold-standard label set cross-validated by human experts (coaches) is '
        'still needed.', S_BULLET))
    story.append(Paragraph('&#8226; Board simulator: DAS/ARR timing mismatches limit the fidelity of line-clear reconstruction.', S_BULLET))
    story.append(Paragraph('&#8226; Hybrid prediction structure: because the rule-based weight (60%) exceeds that of the ML '
        'model (40%), a tendency to converge to the same label was observed when the analyzed group shares a common '
        'weakness (high finesse fault). This can be improved by raising the ML weight once all-tier training data are '
        'obtained.', S_BULLET))
    story.append(Paragraph('&#8226; Absence of a user study: to quantitatively verify the efficacy of the prescriptive '
        'feedback, at minimum a small-scale pilot study (2&#8211;3 players per tier, tracking TR change) is required but was '
        'not conducted here. The case analyses in this paper constitute indirect, post-hoc consistency verification.', S_BULLET))

    story.append(Paragraph('5.3 Ethical Considerations', S_H2))
    story.append(Paragraph(
        'Individual consent was not obtained from the players whose replay data were used in the case analyses of this '
        'study. Accordingly, the nicknames of all players, including the author, were anonymized as Subject P, Player A, '
        'Player B, and Player C. The Kaggle dataset used to train the ML model (n3koasakura, 2024) is a public dataset '
        'collected through TETR.IO&#39;s public API and contains no personally identifying information. Any future user '
        'study will proceed through IRB (Institutional Review Board) approval.',
        S_BODY))

    story.append(Paragraph('5.4 Future Work', S_H2))
    story.append(Paragraph('&#8226; Complete a placement-accuracy comparison system via a direct build of Cold Clear 2 (Rust).', S_BULLET))
    story.append(Paragraph('&#8226; Collect all-tier replays and retrain the model by securing a TETR.IO bot account.', S_BULLET))
    story.append(Paragraph('&#8226; Conduct an A/B user study tracking TR change between TetrioCoach users and non-users.', S_BULLET))
    story.append(Paragraph('&#8226; Extend to real-time coaching with an instant-feedback system via in-game board-state capture.', S_BULLET))
    story.append(Paragraph('&#8226; Generalize the framework to other competitive games such as Puyo Puyo and rhythm games.', S_BULLET))

    # ═══ VI. Conclusion ═══
    story.append(Paragraph('VI. Conclusion', S_H1))
    story.append(Paragraph(
        'In the new research area of Tetris AI coaching, this study designed and implemented a complete pipeline&#8212;'
        'large-scale replay data analysis &#8594; ML-based weakness classification &#8594; domain-knowledge-based '
        'prescriptive feedback generation&#8212;and indirectly verified the system&#39;s consistency through case analyses. '
        'The 4,087-line system operates independently without any external LLM, and the classifier&#8212;trained by labeling '
        '61,935 real matches via K-Means clustering&#8212;achieved a Macro F1-score of 0.960. Through a cross-recommendation '
        'matrix of 16 build patterns and 11 tiers, the system delivers tailored coaching to players at all levels, from '
        'beginner to top tier. This framework can generalize beyond Tetris to automated coaching for replay-based '
        'competitive games, and articulates a new paradigm for AI coaching: the transition from descriptive to '
        'prescriptive.',
        S_BODY))

    # ═══ References ═══
    story.append(PageBreak())
    story.append(Paragraph('References', S_H1))
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

    # ═══ Appendix ═══
    story.append(PageBreak())
    story.append(Paragraph('Appendix A: Visual-Material Planning Guide', S_H1))

    story.append(Paragraph('A.1 Fig. 1 &#8212; System Architecture Flowchart', S_H3))
    story.append(Paragraph('A four-layer structure (Data Acquisition &#8594; Statistical Analysis &#8594; AI Intelligence '
        '&#8594; Feedback Generation), with the constituent modules and data flow shown for each layer. To be produced as '
        'a high-resolution vector image based on the SVG diagram generated while drafting this outline.', S_BODY))

    story.append(Paragraph('A.2 Fig. 2 &#8212; Feature-Importance Analysis', S_H3))
    story.append(Paragraph('(a) Horizontal bar chart: importance ranking of the 10 features, emphasizing '
        'lines_per_piece (28.6%), rating_norm (21.7%), and max_btb (15.9%) in order. Visually contrasted against the '
        'previous version&#39;s tspin_rate (73.9%) overfitting to convey the improvement toward a multi-dimensional '
        'distribution. (b) Confusion matrix (4&#215;4): attack/defense/speed/tspin. (c) ROC curve: multi-class, '
        'one-vs-rest.', S_BODY))

    story.append(Paragraph('A.3 Fig. 3 &#8212; Feedback Generation Pipeline', S_H3))
    story.append(Paragraph('Input (.ttrm/API) &#8594; parsing &#8594; aggregation &#8594; [ML classifier + rule evaluator '
        '+ build DB] &#8594; coaching + roadmap + matchup. Visualizing the data transformation and abstraction level at '
        'each stage.', S_BODY))

    story.append(Paragraph('A.4 Table 3 &#8212; Build-Pattern &#215; Tier Recommendation Matrix', S_H3))
    story.append(Paragraph('A cross-tabulation of 16 builds (rows) &#215; 11 tiers (columns), with check marks for builds '
        'recommended at each tier, annotated with each build&#39;s attack type, difficulty, and output lines.', S_BODY))

    story.append(Paragraph('A.5 Fig. 4 &#8212; User Dashboard Screenshots', S_H3))
    story.append(Paragraph('(a) Growth-graph tab: 6 subplots (APM, PPS, VS, garbage, T-Spin/Quad, Finesse). (b) '
        'Statistics-summary tab: showing the online/local branch. (c) AI-coaching tab: 8-section feedback text. (d) '
        'Training-roadmap tab: the 20-minute routine.', S_BODY))

    doc.build(story)
    print(f'PDF generated: {OUT}')


if __name__ == '__main__':
    build()
