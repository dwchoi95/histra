# 논문 골격 (Skeleton) — guidelines 4편 분석

스타일 분석의 **최상위 문서**. 여기서는 전체 골격(섹션 구성·분량·플로트 배치·공통 규칙)만 다룬다.
섹션 내부의 단락 흐름과 문체는 섹션별 상세 분석 파일에서 다룬다 (§6 참고).

---

## 0. 분석 대상

| ID | 제목 | 학회 / 포맷 | 본문 단어 | Fig / Tab / Alg / RQ / Ref |
|---|---|---|---|---|
| ICSE25 | TopSeed: Learning Seed Selection Strategies for Symbolic Execution from Scratch | ICSE'25 / IEEE 2단 | 7,134 | 4 / 10 / 3 / 4 / ~42 |
| ICSE26 | Enhancing Symbolic Execution with Self-Configuring Parameters | ICSE'26 / ACM 2단 | 8,133 | 6 / 6 / 2 / 5 / 93 |
| ASE26 | Orbis: Guiding Symbolic Execution Techniques to Maximize Option-Related Branch Coverage | ASE'26 / ACM 2단 | 8,338 | 3 / 10 / 2(+1) / 4 / 50 |
| FSE26 | Reducing Coverage-Equivalent Inputs in Grammar-Based Fuzzing by Avoiding Recurrent Rule Sequences | FSE'26 / PACMSE 1단 | 8,743 | 4 / 6 / 2 / 4 / 47 |

4편 모두 같은 연구실(SKKU SAL, 교신 Sooyoung Cha) 논문이다. 주제(symbolic execution, fuzzing)는 달라도 **골격이 거의 동일한 house template**을 따른다.

---

## 1. 전체 골격 (공통 템플릿)

```text
Title            [Tool]: [Verb-ing] [대상 기술] [목표/수단]
Abstract         1단락, ~210 words
1 Introduction   관찰 → 도전과제 → 맞춤 알고리즘 → 결과 → Contributions(3 bullets)
2 Preliminaries  배경 형식화 + Algorithm 1(일반 알고리즘) → Limitation(측정 Table) → (Goal)
3 Our Approach   Overview(Figure) → [Tool](메인 Algorithm) → 단계별 상세
4 Experiments    RQ 목록 → Settings → RQ별 하위절 → (Case study / Discussion) → Threats to Validity
5 Related Work   bold 주제 단락 2–3개
6 Conclusion     1단락
Acknowledgments / Data Availability / References
```

### 1.1 섹션 구성 규칙

- 섹션 이름은 4편 모두 **Preliminaries / Our Approach / Experiments**로 같다.
- Background·Motivation 섹션을 따로 두지 않는다. 배경과 한계(motivation)는 모두 **Preliminaries** 안에 들어간다.
- **Threats to Validity는 Experiments의 마지막 하위절**이다 (4편 공통).
- Discussion 섹션을 따로 두지 않는다. 필요하면 Experiments 하위절로 넣는다 (ICSE25 IV-F).
- Related Work는 **Experiments 뒤**에 둔다.

### 1.2 분량 (단어 수)

1단 포맷과 2단 포맷이 섞여 있어 쪽수 대신 **산문 단어 수**로 비교한다.
본문 산문만 셌다 (표·알고리즘·캡션·머리글·CCS 블록 제외, 오차 약 ±5%).
섹션별 비율은 Abstract를 뺀 본문 기준이다.

| 섹션 | ICSE25 | ICSE26 | ASE26 | FSE26 | **평균 비율** |
|---|---|---|---|---|---|
| Abstract | 169 | 241 | 191 | 230 | (~210 words) |
| 1 Introduction | 742 (10.4%) | 1,043 (12.8%) | 722 (8.7%) | 977 (11.2%) | **10.8%** |
| 2 Preliminaries | 977 (13.7%) | 976 (12.0%) | 1,006 (12.1%) | 922 (10.5%) | **12.1%** |
| 3 Our Approach | 2,256 (31.6%) | 2,339 (28.8%) | 2,502 (30.0%) | 2,891 (33.1%) | **30.9%** |
| 4 Experiments | 2,719 (38.1%) | 3,106 (38.2%) | 3,562 (42.7%) | 3,464 (39.6%) | **39.7%** |
| └ Threats to Validity | 111 | 108 | 174 | 146 | (1.7%) |
| 5 Related Work | 339 (4.8%) | 544 (6.7%) | 472 (5.7%) | 410 (4.7%) | **5.4%** |
| 6 Conclusion | 101 (1.4%) | 125 (1.5%) | 74 (0.9%) | 79 (0.9%) | **1.2%** |
| **본문 합계** | 7,134 | 8,133 | 8,338 | 8,743 | 평균 ~8,100 |

#### 관찰

- 포맷과 무관하게 본문은 **7,100–8,700 words**이고, 섹션 비율은 편차 ±3%p 안에서 안정적이다.
- **Approach + Experiments ≈ 71%.** 기법 설명과 실험이 본문의 2/3 이상을 차지한다.
- Intro와 Preliminaries의 분량이 비슷하다 (각 ~900–1,000 words). Preliminaries가 motivation 역할까지 맡기 때문이다.
- Related Work(~440)와 Conclusion(~100)은 매우 짧다. Threats도 ~135 words로 한 단락이다.

#### 본문 8,000 words 기준 예산 (평균 비율 적용)

| Abstract | Intro | Prelim | Approach | Experiments (Threats 포함) | Related Work | Conclusion |
|---|---|---|---|---|---|---|
| ~210 | ~860 | ~970 | ~2,470 | ~3,180 (~140) | ~430 | ~100 |

### 1.3 하위절 구성

| | ICSE25 (TopSeed) | ICSE26 (ParaSuit) | ASE26 (Orbis) | FSE26 (RSFuzz) |
|---|---|---|---|---|
| §2 | A. Symbolic Execution / B. Seeding for SE | 2.1 SE and Its Parameters / 2.2 Existing Parameter Tuning Approaches (+ **Goal.** 단락) | 2.1 Symbolic Execution / 2.2 Limitation of SE | 2.1 Basic Grammar-based Fuzzing / 2.2 Limitation / 2.3 Goal |
| §3 | A. Overview / B. TopSeed / C. Data Gathering / D. Seed Selecting / E. Distribution Learning | 3.1 Overview / 3.2 ParaSuit / 3.3 Parameter Selection / 3.4 Value Sampling | 3.1 Overview / 3.2 Orbis (Extract·Construct·Guide·Update = bold 단락) | 3.1 Overview / 3.2 RSFuzz (3.2.1 Collecting ~ 3.2.4 Capturing) / 3.3 Fuzzing with RS |
| §4 | A. Settings / B. Effectiveness / C. Efficacy of Each Stage / D. Generality / E. Hyperparameters / F. Discussions / G. Threats | 4.1 Settings / 4.2 Branch Coverage / 4.3 Bug-Finding / 4.4 Efficacy of Two Stages / 4.5 Analysis of Self-configuration / 4.6 Generality / 4.7 Threats | 4.1 Settings / 4.2 Branch Coverage / 4.3 Bug-finding / 4.4 Effectiveness of Stages / 4.5 Generality / 4.6 Case Study / 4.7 Comparison with Fuzzing / 4.8 Threats | 4.1 Settings / 4.2 Effectiveness / 4.3 Ratio of CE Inputs / 4.4 Efficacy of Each Step / 4.5 Reusability / 4.6 Threats |
| §5 | bold 3주제 | bold 3주제 | bold 3주제 | 5.1–5.3 하위절 3개 |

---

## 2. Title & Keywords

### 2.1 Title

| ID | Title | 단어 | 구조 |
|---|---|---|---|
| ICSE25 | **TopSeed:** Learning Seed Selection Strategies for Symbolic Execution from Scratch | 11 | Tool: V-ing + 대상 + *for* 분야 + 한정어 |
| ICSE26 | Enhancing Symbolic Execution with Self-Configuring Parameters | 6 | V-ing + 분야 + *with* 수단(신조어) |
| ASE26 | **Orbis:** Guiding Symbolic Execution Techniques to Maximize Option-Related Branch Coverage | 11 | Tool: V-ing + 분야 + *to* 목표(신조어) |
| FSE26 | Reducing Coverage-Equivalent Inputs in Grammar-Based Fuzzing by Avoiding Recurrent Rule Sequences | 12 | V-ing(문제) + *in* 분야 + *by* V-ing(수단) |

- **동명사로 시작한다** (도구명 접두가 있으면 그 바로 뒤). 동사는 개선 동사다: Learning / Enhancing / Guiding / Reducing.
- **분야명을 그대로 넣는다** (Symbolic Execution, Grammar-Based Fuzzing).
- **논문의 핵심 신조어를 넣는다** (Self-Configuring, Option-Related Branch, Coverage-Equivalent, Recurrent Rule Sequences).
- 도구명 접두 `Tool:`는 2/4에서만 쓴다. 쓰지 않은 두 편은 서술형 제목이다.
- Title Case, 6–12 words. 의문형이나 말장난은 없다.
- 도구 이름은 핵심 개념에서 따온다. TopSeed(Top+Seed), ParaSuit(Parameters+Suitable, 각주로 설명), Orbis(Option-Related Branch), RSFuzz(Recurrent Sequence+Fuzz).

### 2.2 Keywords / CCS (ACM 포맷)

| ID | CCS Concepts | Keywords |
|---|---|---|
| ICSE25 (IEEE) | — | (추출 텍스트에 없음) |
| ICSE26 | Software and its engineering → Software testing and debugging; Computing methodologies → Machine learning | Symbolic execution, Parameter configuring, Software testing |
| ASE26 | (ICSE26과 동일) | Symbolic execution, Program-option based testing, Software testing |
| FSE26 | Software and its engineering → Software testing and debugging | Grammar-based Fuzzing, Software Testing |

- Keywords는 **[분야], [논문 고유 개념], [상위 분야]** 2–3개로 구성한다.
- 학습 기반 기법이면 CCS에 Machine learning을 추가한다.

---

## 3. 플로트 배치 패턴

| 위치 | 플로트 | 내용 |
|---|---|---|
| §1 | (선택) Figure 1 | 기존 방식의 설정/예시 (ICSE26만) |
| §2.1 | **Algorithm 1** | 일반 baseline 알고리즘 (제안 기법이 끼어들 훅 포함) |
| §2.2–2.3 | **Table 1(, 2)**, Figure(예제 코드) | 기존 기법의 한계 측정 / 도전과제 규모 |
| §3.1 | **Figure: Overview** | 단계 파이프라인 |
| §3.2 | **Algorithm 2(3)** | 제안 알고리즘 전체 |
| §3.3~ | 소형 Table (feature/policy 정의), 보조 Algorithm | 단계 내부 정의 |
| §4.1 | Table: Benchmarks | 이름·규모 |
| §4.2~ | Table: 주 결과(가장 큰 표), Table: bug, Table: ablation, Figure: 분석 그래프/Venn | RQ마다 1개 이상 |
| §4 case study | Figure: 코드 스니펫 | |

표가 그림보다 많다. 주 결과는 거의 항상 **표**(벤치마크 × baseline × 설정)로 보여 준다.

캡션·선·정렬·강조·색·서체 같은 **디자인 상세는 [floats.md](floats.md)**에서 다룬다.

---

## 4. 전체를 관통하는 골격 규칙

1. **서사 축:** 정량 관찰 → 도전과제(규모도 정량) → 맞춤형(customized/specialized) 반복 알고리즘 → 대규모 평가. 4편 모두 같다.
2. **단계 이름 반복:** 기법의 단계 이름 3–4개(예: Gather · Select · Learn)를 Abstract, Introduction, Overview, Conclusion에서 같은 단어·같은 순서로 반복한다.
3. **수치 선행:** Introduction에서 이미 한계 수치(§2를 forward ref)와 결과 수치를 모두 보여 준다.
4. **Algorithm 1 → Algorithm 2 구조:** 일반 알고리즘을 먼저 보이고 제안 기법을 그 위에 얹는다 ("complementary", "integrated with").
5. **반복 키워드:** from scratch / without prior knowledge / complementary / orthogonal / customized·specialized algorithm / accumulated data.
6. **Forward reference를 자주 쓴다:** "as shown in Section 2", "as demonstrated in Section 4.4".
7. **이름 표기:** IEEE판은 도구명을 small caps(`\textsc{TopSeed}`)로 쓴다. baseline 변형은 `Tool+X`, `Tool-(Stage)`, `RandX` 식으로 이름 붙인다.

---

## 5. 측정 방법 (재현용)

- `pdftotext`(raw 모드)로 텍스트를 추출하고, 최상위 섹션 제목 사이 구간의 산문 줄만 단어 수를 센다.
- 산문 줄 판정 기준: 토큰 5개 이상, 알파벳 토큰 비율 60% 이상(인용 토큰 `[8,` `10,` 등은 비율 계산에서 제외), 캡션·알고리즘 I/O·러닝 헤더/푸터·CCS/ACM Reference 블록 제외.
- ACM 포맷은 Introduction 제목이 CCS 블록 뒤에 나온다. 그래서 Introduction 구간은 본문 첫 문장부터 센다.

---

## 6. 섹션별 상세 분석 파일

### 6.1 공통 목차

모든 섹션 문서는 아래 목차를 따른다. 해당 내용이 없는 항목은 "해당 없음"으로 남긴다.

```text
# <Section> — guidelines 4편 분석
0. 핵심 규칙       이 섹션을 쓸 때 지킬 규칙 3–5개 (문서 전체 요약)
1. 분량           단어 수, 문장·단락·하위절 수, 평균 문장 길이, 플로트 수
2. 구조           분석 단위 정의 → 논문별 배치 → 단위별 비중
3. 단위별 분석     단위마다 역할, 4편 예문, 반복 패턴
4. 문체 특징       주어·시제·전환어·어휘·단정 수준, 넣지 않는 것
5. 수식·알고리즘·플로트  기호 체계, 기호·수식 도입 방식, 알고리즘·표·그림 표기
6. 섹션 간 연결    다른 섹션에서 반복되거나 대응되는 요소 (용어, 수치, 단계 이름, forward ref)
7. 템플릿         문장·단락 템플릿
8. 작성 체크리스트
부록 A. 원문       분석 단위 태그를 붙인 원문 (긴 섹션은 발췌)
```

### 6.2 파일 목록과 분석 단위

| 파일 | 분석 단위 (목차 2–3의 "단위") | 주요 범위 |
|---|---|---|
| [abstract.md](abstract.md) | 문장 (move) | Abstract 구성 |
| [introduction.md](introduction.md) | 단락 | 단락 흐름, Contributions 문형 |
| [preliminaries.md](preliminaries.md) | 하위절 → 단락 | 형식화, Algorithm 1 서술법, Limitation 측정 방식 |
| [approach.md](approach.md) | 하위절 → 단락 | Overview, 메인 알고리즘 해설, 단계별 정의·예제·직관 서술법 |
| [experiments.md](experiments.md) | 하위절(RQ) → 단락 | RQ 문형, Settings, 결과 단락 패턴, ablation 명명, Threats |
| [floats.md](floats.md) | (섹션 공통) 플로트 유형 | 그림·표·알고리즘·수식의 시각 디자인, LaTeX 레시피 |
| [related_work.md](related_work.md) | 주제 단락 | 주제 구성, 대비 문형 |
| [conclusion.md](conclusion.md) | 문장 (move) | 결론 단락 구조 |
