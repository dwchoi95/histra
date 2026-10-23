# Experiments — guidelines 4편 분석

[skeleton.md](skeleton.md)의 하위 문서. §4 Experiments를 하위절(RQ) → 단락 단위로 분석한다.
본문의 약 40%를 차지하는 가장 긴 섹션이다. 표·그림의 **디자인**은 [floats.md](floats.md)에서 다루고, 여기서는 RQ 구성, 실험 설정, 결과를 **서술하는 문형**에 집중한다.
원문 발췌는 부록 A에 실었다.

---

## 0. 핵심 규칙

1. Experiments는 **~3,200 words, RQ 4–5개**다. 구성은 **리드(RQ 목록 + 구현·장비) → 4.1 Experimental Settings → RQ별 하위절 → (추가 분석) → Threats to Validity**다.
2. RQ 원형은 **① 주 지표(coverage) ② 부 지표(bugs) ③ 단계별 효과(ablation) ④ 일반성(다른 도구 계열)**이고, 여기에 하이퍼파라미터·분석·재사용성 중 하나를 더한다. **RQ 이름 = 하위절 제목**이다.
3. Settings는 **Baselines. / Benchmarks. / Other Settings.** bold run-in 세 단락이다. 벤치마크는 선행 연구에서 가져오고 **명시적 필터 기준**을 둔다. 예산·반복 횟수·장비·**공정성 장치**("we ran each baseline in two ways ... and reported the better")를 밝힌다.
4. 결과 단락은 **"Table N shows that ..." → 전체 평균 % → baseline별 수치(respectively) → Notably(최대) → Interestingly/Surprisingly(이상치 + 원인) → 통계 검정 + 표준편차 → "These results indicate ..."** 순이다.
5. Threats to Validity는 **한 단락, (1)(2)(3)**이다. 도구 일반성·벤치마크 대표성·하이퍼파라미터를 다루고, 항목마다 **완화 근거**를 붙인다. "may"가 집중적으로 나오는 유일한 곳이다.
6. **우열은 표로, 원인은 그림으로 보인다.** §4 플로트 36개 중 표가 26개(72%)다. 주 결과·버그·ablation·하이퍼파라미터는 **모두 표**이고, 그림은 내부 동작·집합 겹침(Venn)·분포처럼 **왜 좋아졌는지**를 설명하는 데 쓴다 (§1, §5).
7. **평가 문장의 81%가 장점, 12%가 baseline의 약점, 6%가 도구의 단점**이다. 인정하는 단점은 논문당 1–9개이고 **모두 비임계적**이며, 같은 문장이나 다음 문장에서 바로 방어한다. 표에는 도구가 지거나 비긴 셀이 더 있지만 본문은 그중 일부만 다룬다 (§4.1–4.4).
8. 규모는 **벤치마크 12–17개 × baseline 3–5개 × 10–24시간 × 5회**다. 계산량은 곱셈식으로 밝히고("24 hours × 5 trials × ..."), 통계 검정은 **주 결과표에만** 한다 (§3 E-1).

---

## 1. 분량

| ID | 하위절 (단어 수, 비율) | 합계 |
|---|---|---|
| ICSE25 | 리드 134 (5%) · A. Settings 409 (15%) · **B. Effectiveness 626 (23%)** · C. Each Stage 507 (18%) · D. Generality 215 (8%) · E. Hyperparameters 249 (9%) · F. Discussions 495 (18%) · G. Threats 111 (4%) | 2,746 |
| ICSE26 | 리드 103 (3%) · 4.1 Settings 352 (11%) · **4.2 Branch Coverage 758 (24%)** · 4.3 Bug-Finding 154 (5%) · 4.4 Two Stages 649 (21%) · 4.5 Self-configuration 660 (21%) · 4.6 Generality 322 (10%) · 4.7 Threats 108 (3%) | 3,106 |
| ASE26 | 리드 90 (3%) · 4.1 Settings 506 (15%) · **4.2 Branch Coverage 655 (19%)** · 4.3 Bug-finding 184 (5%) · **4.4 Stages 917 (27%)** · 4.5 Generality 307 (9%) · 4.6 Case Study 244 (7%) · 4.7 vs Fuzzing 306 (9%) · 4.8 Threats 174 (5%) | 3,383 |
| FSE26 | 리드 115 (3%) · 4.1 Settings 700 (20%) · **4.2 Effectiveness (crash + coverage) 1,374 (40%)** · 4.3 CE Ratio 252 (7%) · 4.4 Each Step 523 (15%) · 4.5 Reusability 354 (10%) · 4.6 Threats 146 (4%) | 3,464 |

역할 그룹별 평균 비중:

| 리드 | Settings | 주 결과 (coverage + bug) | Ablation | 추가 분석 (일반성·하이퍼파라미터·사례·비교) | Threats |
|---|---|---|---|---|---|
| ~4% | **~15%** | **~29%** | **~20%** | **~27%** | ~4% |

- 2단 논문은 단 단위로 다시 추출해 셌다. 하위절 경계에서 수십 단어 정도 오차가 있다.
- 주 결과와 ablation을 합치면 약 절반이다. 추가 분석(~27%)도 적지 않다. **RQ 목록에 없는 분석 하위절**도 둔다 (ICSE25 Discussions, ASE26 Case Study·Comparison with Fuzzing).
- 플로트: §4에 표 26개(논문 전체 표의 81%)와 그림 10개(전체 그림의 59%)가 있다. 논문당 표 4–9개, 그림 1–4개다.

§4 플로트를 보여 주는 결과의 종류로 나눴다 (캡션 있는 것 기준):

| 종류 | 표 | 그림 | 합계 | ICSE25 / ICSE26 / ASE26 / FSE26 |
|---|---|---|---|---|
| 벤치마크 설명 | 4 | 0 | 4 | 1 / 1 / 1 / 1 |
| 주 결과 비교 | 5 | 0 | 5 | 1 / 1 / 2 / 1 |
| 부 지표 (버그·크래시) | 4 | 0 | 4 | 1 / 1 / 1 / 1 |
| Ablation | 8 | 0 | 8 | 1 / 2 / 4 / 1 |
| 하이퍼파라미터 | 1 | 0 | 1 | 1 / 0 / 0 / 0 |
| 일반성·재사용성 | 1 | 3 | 4 | 표 / Venn / Venn / 막대 |
| 내부 동작 분석 | 2 | 5 | 7 | 2 / 4 / 0 / 1 |
| 다른 비교 (연속 실행, 다른 계열 기법) | 1 | 1 | 2 | Venn (ICSE25) / 표 (ASE26) |
| 사례 연구 코드 | 0 | 1 | 1 | ICSE25 Fig. 4 (ASE26은 캡션 없는 코드) |
| **합계** | **26 (72%)** | **10 (28%)** | **36** | 10 / 10 / 10 / 6 |

- 우열을 주장하는 플로트(벤치마크~하이퍼파라미터, 22개)는 **전부 표**다. 그림으로 주 결과를 보인 논문은 없다.
- 그림 10개 중 8개가 일반성·내부 동작·겹침 분석이다. 즉 그림은 "얼마나 좋은가"가 아니라 "**왜·어디서** 좋은가"를 보인다.

---

## 2. 구조

### 2.1 하위절 유형

| 유형 | 내용 | 출현 |
|---|---|---|
| **E-0 리드** | "In this section, we evaluate X ... research questions:" + RQ 목록 + 구현·장비 1–2문장 | 4/4 |
| **E-1 Settings** | Baselines / Benchmarks / Other Settings | 4/4 (항상 4.1) |
| **E-2 주 지표** | coverage 결과 + 통계 | 4/4 |
| **E-3 부 지표** | 버그·크래시 결과 | 4/4 (독립 하위절 2편, 주 지표 안의 bold run-in 2편) |
| **E-4 Ablation** | 단계마다 변형과 비교 | 4/4 |
| **E-5 일반성** | 다른 도구 계열에 적용 (concolic testing) 또는 다른 프로그램에 재사용 | 4/4 |
| E-6 추가 분석 | 하이퍼파라미터, 파라미터 분석, 사례 연구, 외부 기법 비교, 연속 실행 비교 | 4/4 (형태는 다양) |
| **E-7 Threats** | (1)(2)(3) 한 단락 | 4/4 (항상 마지막 하위절) |

### 2.2 논문별 RQ와 하위절 대응

| ID | RQ (굵은 이름) | 하위절 | RQ 밖 하위절 |
|---|---|---|---|
| ICSE25 | 1) Effectiveness · 2) Efficacy of Each Stage · 3) Generality · 4) Impact of Hyperparameters | B · C · D · E | F. Discussions (연속 실행 비교, 좋은 seed의 특징, SMT 호출 절감) |
| ICSE26 | Branch coverage · Bug-finding ability · Efficacy of two stages · Analysis of self-configuration · Generality | 4.2 · 4.3 · 4.4 · 4.5 · 4.6 | — (4.2 안에 bold run-in 분석 2개) |
| ASE26 | (1) Branch Coverage · (2) Bug-finding Ability · (3) Effectiveness of Stages · (4) Generality | 4.2 · 4.3 · 4.4 · 4.5 | 4.6 Case Study, 4.7 Comparison with Fuzzing Techniques |
| FSE26 | (1) Effectiveness · (2) Reduction of coverage-equivalent inputs · (3) Efficacy of each step · (4) Reusability | 4.2 · 4.3 · 4.4 · 4.5 | — (4.2 안에 Case study 2개) |

**정형 순서:** 리드 → Settings → 주 지표 → 부 지표 → ablation → 일반성 → (추가 분석) → Threats. 순서가 바뀐 경우는 없다.

### 2.3 결과 하위절의 단락 역할

| 기호 | 역할 | 대표 표현 |
|---|---|---|
| **H** | 헤드라인 (표·그림 + 주장) | Table N shows / demonstrates that X significantly ... |
| **Q** | 수치 (전체 → baseline별) | Overall, ... X% more ... / ..., respectively |
| **N** | 두드러진 사례 | Notably, / Particularly, ... the largest ... |
| **S** | 이상치·의외 결과 + 원인 | Interestingly, / Surprisingly, ... The fundamental reason is ... |
| **T** | 통계 검정·변동 | statistically significant ... Mann-Whitney U test ... p < 0.05 / standard deviations ... |
| **D** | 심층 분석 (bold run-in) | **Comparison with ...** / **Case study.** |
| **C** | 함의 | These results indicate / demonstrate / highlight that ... |

**정형 순서:** H → Q → N → S → T → (D) → C.

---

## 3. 단위별 분석

### E-0 리드 — RQ 목록

| ID | 도입 문장 | RQ 형식 |
|---|---|---|
| ICSE25 | "In this section, we evaluate the effectiveness of TopSeed based on the following research questions:" | `1) **Effectiveness:** How effectively can ...?` (번호 목록) |
| ICSE26 | "We evaluate ParaSuit to answer the following research questions:" | `• **Branch coverage**: To what extent does ...?` (글머리표) |
| ASE26 | "In this section, we evaluate the efficiency of Orbis by addressing the following research questions:" | `(1) **Branch Coverage**: To what extent does ...?` |
| FSE26 | "In this section, we experimentally evaluate RSFuzz to answer the following four research questions:" | `(1) **Effectiveness**: How effectively does ...?` |

**RQ 문형** (17개 RQ 기준):

- "**How effectively** can / does X enhance ... in terms of A and B?" (4)
- "**To what extent** does X improve / reduce ...?" (3)
- "**How** does each stage of X **contribute to** performance improvement?" / "How significantly does each step ... contribute ...?" (ablation, 3)
- "**Is** X (generally) **applicable to** ...?" / "**Can** X **be applied to** ...?" (일반성, 3)
- "How do hyperparameter values affect ...?" / "Which parameters are most impactful? How do they ... vary by program?" / "Are the ... applicable to different programs ...?"
- ICSE26처럼 한 RQ에 질문 2–3개를 붙이기도 한다: "Does our parameter selection algorithm outperform naive approaches? Is our value sampling stage more effective than generic sampling methods?"

**RQ 이름**은 2–4단어 명사구다: Effectiveness / Branch Coverage / Bug-finding Ability / Efficacy of Each Stage / Generality / Reusability. **같은 이름을 하위절 제목으로 쓴다.**

**구현·장비 문장** (리드 끝 또는 Settings 끝):

- "We implemented TopSeed on top of KLEE-2.1 [4], an actively maintained symbolic executor that incorporates diverse techniques [11], [15], [17], [18], [26]. All experiments were conducted on a single Linux machine equipped with two Intel Xeon Gold 6230R processors."
- "We conducted our experiments using KLEE-2.1 [5], a widely used symbolic executor. All experiments were performed on a system with two Intel Xeon Gold 6230R processors and 256GB RAM."
- 틀: **"We implemented X on top of <도구-버전> [cite], <도구에 대한 한 구절>. All experiments were conducted on <장비>."**

### E-1 Experimental Settings

bold run-in 세 단락이 기본이다 (ICSE25·ASE26: **Baselines.** / **Benchmarks.** / **Other Settings.**, ICSE26: Baselines. / Other Settings., FSE26: 4.1.1 Baselines / 4.1.2 Benchmarks and Time Budgets).

#### Baselines

- **개수와 범주를 먼저** 밝힌다: "We compared the performance of four baselines integrated with TopSeed against their performance without TopSeed integration. The four baselines are: (1) base symbolic executor (KLEE [4]), (2) search strategy (Learch [11]), (3) state-pruning strategy (Homi [15]), and (4) constraint-solving strategy (KLEE-Array [18])."
- 각 baseline을 **한 문장으로 설명**한다: "Learch [11] is a novel learning-based search strategy that prioritizes states for exploration. Homi [15] is a cutting-edge state-pruning strategy that automatically eliminates redundant states while keeping promising ones."
- **비교 설정에 이름을 붙인다**: "the baseline without seeding (Base), the baseline with a random seed selection strategy (RandSeed), corresponding to Algorithm 2, and the baseline integrated with our approach (TopSeed), corresponding to Algorithm 3." / "(1) a pure implementation without modifications, as publicly available (Pure), and (2) an integration of Orbis with each technique (Orbis)."
- **baseline 구성 원형:**
  - SOTA ("the state-of-the-art approach ... It requires 20 user-configured parameter spaces")
  - SOTA의 변형 (Symtuner_AllP: 모든 파라미터를 쓰도록 바꾼 SymTuner)
  - **제안 기법의 단순판** (RandSeed, RandSuit: "a naive version of ParaSuit that randomly selects ...") — §2의 단순 대안이 여기서 baseline이 된다
  - 기본 도구 그대로 (KLEE, Kleefix)
- **강한 baseline임을 강조**한다: "Given that Symtuner is an arguably strong baseline, this choice ensures a rigorous evaluation for ParaSuit." / "Each enhances symbolic execution through an independent approach and has shown superior performance over its own baselines."
- **baseline 설정의 근거**를 밝힌다: "we set k to 5, the best-performing value reported in Tribble's evaluation" / "The probabilistic fuzzer was executed with both PCFGs, and the best result was reported as ProbF."

#### Benchmarks

- **출처 = baseline들이 쓴 벤치마크의 합집합**: "we initially collected all available programs used in the experiments by the four baselines [4], [11], [15], [18]."
- **필터 기준 (1)(2)를 예시와 함께**:
  - "(1) we filtered out smaller programs with fewer than 1,000 total branches, as the baselines achieved high code coverage for these programs even without seeding (e.g., tty-8.31). (2) we also omitted programs (e.g., objcopy-2.36) where all baselines managed to cover less than 2.0% of total branches over 10 hours, indicating that the baselines failed to test the core functionality ..."
  - "First, we chose JavaScript, JSON, CSV and Markdown, which are the most commonly used input formats in previous works on fuzzing [..]. Second, among benchmarks using these formats, we included only those used at least twice in prior work."
- **다양성·대표성을 수치로**: "the number of options in our 15 benchmarks ranges from 15 to 158 (10×), and the number of option-related branches ranges from 30 to 8,080 (269×), ensuring a diverse and representative benchmark set." / "most benchmarks (8 out of 12) are not standalone parsers but non-trivial functionality beyond parsing."
- **선행 연구에서 쓰였음**: "these benchmarks have also been widely used in existing works [12, 13, 18, 44, 54, 80]"
- 끝에 벤치마크 표를 참조한다: "Table 2 presents the 15 open-source C programs used in our evaluation, along with the number of options in each program (Opt), ..."

#### Other Settings

| 항목 | 예 |
|---|---|
| 예산 | "we allocated a total testing budget of 10 hours per benchmark program" / 24 hours |
| 반복 | "Each experiment was conducted five times, and the average results were reported." (4/4, 5회) |
| **공정성 장치** | "to ensure a fair comparison, we ran each baseline without seeding (Base) in two ways: (1) by running it once for the total testing budget (10 hours) without termination, or (2) by running it multiple times within a shorter budget (120 seconds), similar to TopSeed (Algorithm 3). The better result between the two approaches was reported as Base." (ICSE25·ICSE26·ASE26) / "We also configured all baselines to potentially generate the same command-line arguments as Orbis." |
| 규모 강조 | "generating the coverage results reported in Table 3 required 18,000 hours when using a single CPU core (i.e., 24 hours × 5 trials × 15 benchmarks × 5 baselines, each tested with and without Orbis)" / "which exceeds the durations used in evaluations with three baseline fuzzers" |
| 측정 도구 | "We obtained branch coverage results using gcov [19], a widely used code coverage measurement tool." / jacoco [40] |
| 지표 정의 | "We evaluated the effectiveness of our approach using two metrics: option-related branch coverage, which Orbis primarily targets, and total branch coverage, a main objective of symbolic execution techniques." |

#### 실험 규모

| ID | 벤치마크 | 비교 대상 | 예산 × 반복 | 계산량 (명시 / 추정) | 통계 검정 | 부분집합 실험 |
|---|---|---|---|---|---|---|
| ICSE25 | C 17개 (8K–251K LoC) + concolic 3개 | baseline 4 × {Base, RandSeed, TopSeed} = 12 | 10h × 5 | 명시 없음 / ~1.6만 시간 | Wilcoxon, 주 결과만 (16/17, 예외 factor) | ablation·하이퍼파라미터·Venn·SMT 분석을 가장 큰 5개에서 (이유 없음) |
| ICSE26 | C 12개 (5K–161K) + 일반성 4개 | baseline 4 + 변형·비교 대상 포함 20개 구성 | 24h × 5 | "over 120 hours (i.e., 24 hours × 5 trials)" / ~2.1만 시간 | Mann-Whitney, 주 결과만 (48/48) | ablation·Sobol을 5개에서 ("the three largest programs ... and the three programs where bugs were identified") |
| ASE26 | C 15개 (옵션 15–158) + 일반성 4개 | baseline 5 × {Pure, Orbis} = 10, 변형 8, fuzzer 3 | 24h × 5 | "Table 3 required 18,000 hours when using a single CPU core" / ~4.0–4.9만 시간 | Mann-Whitney, 주 결과만 (평균 p 0.015, 0.010) | ablation·fuzzer 비교를 KLEE에서만 |
| FSE26 | 4개 포맷 12개 (1.5K–77K) | baseline 3 × {X, X+RSFuzz} = 6, 변형 9 | 24h × 5 | "120 hours per fuzzer (24 hours × 5 repetitions)" / ~2.9만 시간 | Mann-Whitney, line coverage만 (12/12) | 크래시 표 7/12개, 재사용성 4개, 표준편차 2개 |

(추정 계산량은 본문의 설정을 곱해 얻은 값이다. 네 편 모두 전체 합계는 쓰지 않는다.)

- 공통 규모: 벤치마크 12–17개, baseline 3–5개, 실행당 10–24시간, **5회 반복**, 단일 장비(Xeon Gold 6230/6230R 두 개).
- 계산량은 **곱셈식으로 풀어 쓴다** ("24 hours × 5 trials × 15 benchmarks × 5 baselines"). 가장 큰 표 하나나 도구 하나 기준의 시간만 쓰고, 그래도 수만 시간 규모가 드러난다.
- **통계 검정은 주 결과표 하나에만** 한다 (4/4). 버그·ablation·일반성에는 검정이 없다. 표준편차는 pooled 값 몇 개나 큰 프로그램 두 개 정도만 본문에 쓴다.
- 비용이 큰 실험(ablation, 하이퍼파라미터, 분석)은 **가장 큰 프로그램 5개** 같은 부분집합에서 한다. 이유를 쓰기도 하고(ICSE26) 쓰지 않기도 한다(ICSE25).
- 일반성 실험은 **상대 논문(Chameleon)의 벤치마크 3–4개**를 그대로 쓴다 (SE 세 편).

### E-2 주 지표 (coverage)

단락 순서 H → Q → N → S → T → (D) → C를 그대로 따른다.

- **H + Q:** "**Table V shows that** integrating TopSeed into each of the four baselines **significantly increased** branch coverage across all benchmarks, compared to the baselines without TopSeed. **Overall**, TopSeed covered 33.0% more branches than KLEE+Base, ... integrating TopSeed with Learch, Homi, and KLEE-Array, resulted in 38.1%, 31.6%, 40.1% increases in branch coverage, **respectively**, over each baseline without seeding."
- **N (부분집합·최대):** "**Particularly**, TopSeed dramatically increased branch coverage achieved by four baselines on large benchmarks, which have a greater potential for improvement than smaller ones. For the five largest programs, ... **Conversely**, on the five smallest programs, the improvements were modest, ..." / "**For instance**, in the case of the largest program xorriso, ParaSuit achieved 106.6% higher branch coverage than Symtuner, the second-best baseline—making the largest difference across all benchmarks."
- **S (이상치 + 함의):** "**Surprisingly**, for the dd program, Learch+RandSeed covered 63.2% fewer branches than Learch+Base. **This inconsistency of RandSeed underscores the necessity of our approach** (Algorithm 3) to achieve stable and high coverage across various benchmark programs." / "**Interestingly**, in grep, Symtuner even covered 2% fewer branches than RandSuit ... **This finding highlights a key limitation of** Symtuner—its use of a predefined configuration regardless of the target program."
  - 이상치는 **baseline의 약점**을 드러내는 쪽으로 해석한다.
- **T (통계):**
  - "**These results in Table V were statistically significant**: on 16 of the benchmark programs, the p value between Base and TopSeed across the four baselines was less than 0.05 according to the **Wilcoxon signed-rank test**. **An exception occurs** in the factor program, where ..."
  - "The coverage results of ParaSuit are statistically significant. This is confirmed by the **Mann-Whitney U test** [63], with p-values below 0.05 in all 48 cases (12 benchmarks × 4 baselines)."
  - 표준편차는 본문에 괄호로 쓴다: "The standard deviations of branch coverage ... were as follows: Base (38.6), RandSeed (73.1), and TopSeed (52.0). **As expected**, RandSeed showed the highest variability. **While** the standard deviation of TopSeed was slightly higher than Base, **this difference was negligible** given ..."
  - 검정: Wilcoxon signed-rank (1편), Mann-Whitney U (3편). 4편 모두 p < 0.05를 기준으로 하고, **예외를 숨기지 않는다**.
- **D (심층 분석, bold run-in):**
  - ICSE26: "**Comparison with User-configured Approach.** To demonstrate how ParaSuit achieved higher branch coverage than the state-of-the-art approach (Symtuner), we analyzed the differences in selected parameters and values. Figure 3-(a) shows that ..."
  - ICSE26: "**Comparison with 24-Hour Continuous Run.** To examine whether ParaSuit's iterative approach ... limits its ability to explore deeper paths, we compared it with Klee24h ..."
  - ASE26: OB coverage와 전체 coverage의 상관 (Pearson 0.902) — §2에서 미리 인용한 근거를 여기서 제시한다.
  - FSE26: "**Case study.** We conducted a detailed case study to investigate how ..."
- **C (함의):** "These results show that Orbis is complementary to existing symbolic execution techniques despite their different underlying methodologies." / "These results indicate that ParaSuit effectively tailors parameter selection to each program's unique characteristics."

### E-3 부 지표 (bugs / crashes)

- **집계 방법을 먼저 밝힌다** (4/4):
  - "To gather these bug-finding results, we first generated inputs by running each baseline in three modes ... We then selected inputs flagged as bugs by each baseline. Finally, we verified and extracted reproducible bug-triggering inputs by executing the original binary of each program with these selected inputs."
  - "A bug-triggering test-case was considered unique if its error location reported by KLEE differed from others."
  - "Table 4 reports the number of crashes with distinct stack traces detected by each fuzzer, **following previous works** [..]" / "We deliberately filtered out syntax-related errors (e.g., InvalidSyntax), as these are typically considered less critical than semantic errors [24]."
- **결과 문형:**
  - 합계: "In total, ParaSuit succeeded in detecting 11 unique bugs across three of the 12 programs ... This count is 4 more than the state-of-the-art Symtuner"
  - **놓친 것이 없음**: "Notably, ParaSuit did not miss any bugs that other baselines detected, while it successfully identified four additional bugs." / "Orbis not only preserved all bugs detected by the pure techniques but also uncovered additional ones." / "while missing only two"
  - 독점 발견: "exclusively detected", "missed by ... but also by the random seed selection strategy"
- **개발자 확인** (4/4): "the bug in gawk was confirmed by the original developers" / "All bugs discovered by ParaSuit were reported to the program developers" / "we reported these reproducible crashes to the corresponding developers and have received confirmation that one bug ... has been fixed"
- 분량이 적다 (150–250 words). 독립 하위절이 아니면 주 지표 하위절 안의 bold run-in(**Bug-Finding Capability.**, 4.2.1)으로 둔다.

### E-4 Ablation (단계별 효과)

- **리드 = 변형 정의:** "We evaluated the effectiveness of the Select and Learn stages in TopSeed (Algorithm 3). Specifically, for the Select phase, we assessed TopSeed's performance without the grouping and clustering algorithms ... In this variant, **dubbed** 'TopSeed without grouping', each input ... is treated as a separate group."
- **변형 유형:**

| 유형 | 예 | 정의 문형 |
|---|---|---|
| 제거 | TopSeed − (Group), Orbis-Extract, RSFuzz without the Select step | "a variant that omits this stage" / "does not select ... but instead uses all groups" |
| 무작위 대체 | RandP, RandV, RandConst, RandGuide | "randomly selects parameters to be tuned from all available parameters extracted by the Initialize function (line 4 in Algorithm 1)" |
| 전부·하나 | AllP, CallAll, AllConst, OneConst | "selects all available parameters, proceeding directly to the value sampling stage without any filtering" |
| SOTA 부품 대체 | SymP, SymV, FuzzConst (ZigZagFuzz), CitConst (HSCA), Bayesian·Genetic·CMA-ES, ParamILS·OpenTuner | "replaces the Construct function with the option-argument construction mechanism of ZigZagFuzz [26], a state-of-the-art program-option fuzzer" |

- **변형은 알고리즘 줄 번호로 정의**한다: "(the Sample procedure at line 20 of Algorithm 1)", "replaced the set ArgD constructed at line 4 in Algorithm 2 with the following ArgD′:"
- **공정성:** "To ensure fair comparisons, we set each parameter's sampling range to the interval [lv, hv], spanning the smallest to largest values sampled by ParaSuit ..." / "Since both ZigZagFuzz and HSCA are publicly available, we used their original implementations without modification."
- **결과:** "Results in Table VII **confirm the critical roles of** both Select and Learn stages ..." / "Table 4 demonstrates that our parameter selection algorithm **surpasses** the three simpler selection approaches." / "The results in Table 6 confirm that both the Select and Capture steps in RSFuzz **play a crucial role** in its performance."
- **단계 간 비교:** "Although both ... are essential, the grouping algorithm **has a more pronounced impact**." / "We also observed that the relative importance of the Select and Capture steps varied across benchmarks and fuzzers."
- **왜 이겼는지 설명:** "**We investigated why** Orbis notably outperformed CitConst. **The key difference is their objective.** ... In contrast, Orbis continuously evaluates ..."
- **변형이 baseline보다도 나쁜 경우를 짚는다:** "The most naive variant, which lacks both steps, ... performing even worse than the baseline fuzzers alone."
- **마무리:** "These findings demonstrate that both the Select and Capture steps are essential for the effectiveness of RSFuzz."
- 벤치마크: 전체(ASE26, FSE26) 또는 큰 프로그램 5개(ICSE25, ICSE26 — "covering the three largest programs ... and the three programs where bugs were identified").

### E-5 일반성 (Generality / Reusability)

- **SE 세 편은 같은 실험이다**: concolic testing 도구(CREST [..])와 그 위의 SOTA(Chameleon [..])에 적용하고, **Chameleon 논문의 벤치마크**(가장 큰 3–4개)를 같은 예산으로 쓴다.
  - "We examined if our seeding approach is applicable to concolic testing [1], [3], a major variant of symbolic execution. We integrated TopSeed with CREST [28], a popular concolic testing tool ..."
  - **이식 방법을 밝힌다**: "Integrating Orbis into a concolic testing engine corresponds to replacing the Execute procedure (Algorithm 1) with a concolic testing procedure [4, 9]. The main difference is ... To address this, we modified ..."
  - 결과: "On average, TopSeed increased branch coverage by 7.8% compared to CREST and 3.9% compared to Chameleon. **Interestingly**, with the seeding provided by TopSeed, the basic concolic testing tool CREST occasionally outperformed the advanced, unseeded Chameleon ..."
  - 함의: "These results indicate that TopSeed is versatile and can be generalized to other symbolic execution tools ..."
  - 실험 없이 **이식 가능성 논증**을 덧붙이기도 한다: "We also found that integrating ParaSuit with other symbolic execution tools: angr [77] and SPF [68], requires only minor modifications. ... we believe that integration with these tools is straightforward."
- **FSE26은 재사용성**: 한 프로그램에서 얻은 결과를 같은 입력 포맷의 다른 프로그램에 적용한다. 장단점을 함께 쓴다: "**Unquestionably**, RSFuzz achieves the best results when it generates recurrent sequences from a specific program ... **However, if the goal is to reduce the overhead** ..., reusing sequences ... is a practical and effective alternative."

### E-6 추가 분석

| 유형 | 예 | 문형 |
|---|---|---|
| 하이퍼파라미터 | ICSE25 E | "We assessed the impact of varying three hyperparameters—η_time, η_Learn, and η_r—on the effectiveness of TopSeed. Our approach (Algorithm 3) sets these default values to 120, 20, and 0.75, respectively. The first parameter, η_time, dictates ... On the five largest benchmarks, we calculated ... using various values around the default settings." → "Table IX demonstrates that the default hyperparameter values generally achieved the most stable and high branch coverage ..." |
| 연속 실행 비교 | ICSE25 F, ICSE26 4.2 | 짧은 실행을 반복하는 설계가 깊은 탐색을 해치지 않는지: "Results indicate that TopSeed covers, on average, 95% of the branches reached during continuous 10-hour symbolic executions" (Venn) |
| 내부 동작 분석 | ICSE26 4.5 | "**Impact of Selected Parameters.** ... we measured the first-order Sobol indices [79] ..." / "**Tendency of Selections and Sampled Values.**" / "**Efficiency of Self-configured Parameter Sets.**" |
| 사례 연구 | ICSE25 F, ASE26 4.6, FSE26 4.2 | "**To illustrate how** Orbis guides symbolic execution to achieve higher total branch coverage, **we conducted a case study on** the diff program." → 코드 조각 → 메커니즘 → **수치 대비** ("in just 7.1 seconds ... 9,012.7 seconds—approximately 1,269× longer", "the probability of generating this exact sequence is approximately 1 in 4,000,000") |
| 외부 계열 비교 | ASE26 4.7 | 다른 계열(fuzzer)과 비교. **공정성 조건을 길게 쓴다**: "unlike Orbis, which operates fully automatically, these fuzzers require manual intervention ... For a fair comparison, we provided the fuzzers with all information obtained from the Extract stage ..." 그리고 상대가 이긴 부분도 인정한다: "In contrast, these fuzzers exclusively covered 20,193, 6,505, and 6,211 branches, primarily because ..." |
| 메커니즘 지표 | ICSE25 F (SMT 호출 절감), FSE26 4.3 (CE 비율) | 향상의 **원인**이 되는 내부 지표를 따로 측정한다 |

- 사례 연구는 **향상이 가장 컸던 프로그램**을 고른다: "we conducted a case study on the diff program, which showed the highest improvement in terms of branch coverage."

### E-7 Threats to Validity

| ID | 항목 |
|---|---|
| ICSE25 | (1) KLEE·CREST에서만 평가 → 다른 도구에서 다를 수 있음 (2) 하이퍼파라미터를 trial and error로 정함 → "Although Section IV-E demonstrates stable performance ..., these settings may not be optimal ..." (3) 17개 벤치마크 → "While this benchmark suite includes all major programs used in the four baselines, it may not sufficiently evaluate ..." |
| ICSE26 | (1) 하이퍼파라미터 2개 → 같은 방법으로 자동 조정, "only a 1% drop when η_clust is set to 0.9" (2) 12개 C 프로그램 → "may not be representative of all types of programs" |
| ASE26 | (1) help 출력에서만 옵션 추출 → "our manual inspection shows that fewer than one hidden option exists per benchmark program on average (0.7 per program) ... improving branch coverage by only about 1%" (2) 간접 제어 의존성 미고려 → "incorporating more precise control-dependence analysis could further improve performance" (3) KLEE·CREST → 다른 엔진 [12, 21] |
| FSE26 | (1) **Benchmarks**: 12개, 대표성 (2) **Generality**: 더 정교한 fuzzer [..]에서는 다를 수 있음 (3) **Other grammars**: 다른 CFG(XML, CSS)에도 적용될 것으로 기대하지만 보장할 수 없음 |

- 형식: **한 단락, 인라인 (1)(2)(3)** (FSE26은 "(1) Benchmarks:"처럼 이름표를 붙인다). 100–175 words.
- 항목 구성: **사실(우리가 한 것) → 한계("may not ...") → 완화 근거(다른 절의 결과, 수동 조사 수치)**
- 범주: 도구·엔진 일반성 (4/4), 벤치마크 대표성 (3/4), 하이퍼파라미터 (2/4), 방법 자체의 가정 (ASE26 2개, FSE26 1개)
- 완화 근거는 **다른 하위절을 다시 인용**하거나 **수치**로 댄다.

---

## 4. 문체 특징

| 항목 | 관찰 |
|---|---|
| 주어 | **표·그림**(Table N shows ...), **도구 조합**(KLEE+TopSeed, ProbF+RSFuzz), **we**(we evaluated, we observed, we investigated) |
| 시제 | 수행·관찰은 **과거형**(covered, identified, achieved, observed), 표가 보여 주는 것은 **현재형**(Table 2 demonstrates), 함의는 **현재형**(These results indicate) |
| 결론 문장 | "These results / This finding indicate·demonstrate·highlight·underscore·confirm that ..." — 논문당 3–6회, "This indicates/suggests ..." 0–4회 |
| 신호어 (논문당 빈도) | Notably, (0–5) / Interestingly, (0–3) / Surprisingly, (0–2) / Particularly·In particular, (0–3) / Overall·On average, (1–4) / respectively (3–13) |
| 수치 | % 소수 1자리, 큰 배율은 ×("3.5 times", "66.9×"), baseline 나열은 "respectively", 표준편차는 괄호 |
| 통계 | "statistically significant"를 논문마다 정확히 한 번 쓴다. 검정 이름 + 인용 + 기준 p < 0.05 + 예외 |
| 공정성 | "To ensure a fair comparison," / "For a clear comparison," / "without modification" — 4/4 |
| hedging | 결과 서술에는 거의 없다. "may / might"는 논문당 2–3회이고 대부분 Threats와 원인 추정("This might stem from")에 있다 |
| 강조 형용사 | significantly, substantially, dramatically, remarkably, markedly, considerably, noticeably |
| 정직성 | 예외·상대가 이긴 부분·약점을 **일부** 쓴다 ("An exception occurs ...", "while missing only one bug", "these fuzzers exclusively covered ...", "Despite the negative side effect, ..."). 단, 비임계적이고 바로 방어할 수 있는 것만 고른다 (§4.1–4.4) |
| **넣지 않는 것** | 방법 재설명 (§3 참조로 대체), Related Work식 문헌 비교 |

### 4.1 장점·단점 비율

결과 하위절(RQ 목록·Settings·Threats 제외)의 문장을 넷으로 나눴다. **P** 도구의 장점, **B** baseline·단순 변형의 약점, **N** 도구의 단점(손실, 비김, 예외, 비용, 작은 향상, 큰 분산), **M** 설정·정의·서술이다. 장점과 단점이 한 문장에 함께 있으면 주절을 따랐다.

| ID | P | B | N | M | 평가 문장(P+B+N) 중 N |
|---|---|---|---|---|---|
| ICSE25 | 37 | 7 | 4 | 44 | 8.3% |
| ICSE26 | 60 | 6 | 2 | 57 | 2.9% |
| ASE26 | 65 | 10 | 1 | 44 | 1.3% |
| FSE26 | 47 | 9 | 9 | 47 | 13.8% |
| **합계** | **209 (81%)** | **32 (12%)** | **16 (6%)** | 192 | **6.2%** |

- 도구의 단점(N)보다 **baseline의 약점(B)을 두 배 많이** 쓴다. 이상치는 대개 baseline의 한계로 해석한다 (§3 E-2 S).
- "while missing only two"처럼 장점 문장 안에 끼운 양보절까지 세면 FSE26은 20.0%가 된다. FSE26이 가장 많이 인정하지만, 대부분 비김(tie)이나 "only"가 붙은 작은 손실이다.
- 단점 문장은 **결과 하위절의 일부에만** 있다. ASE26은 RQ1–RQ4에 단점 문장이 하나도 없고, 유일한 단점이 RQ 밖의 추가 비교(4.7 fuzzer 비교)에 있다. ICSE26은 둘 다 RQ 밖의 bold run-in 분석에 있다.
- **주 주장을 흔드는(critical) 단점은 0개다.**

### 4.2 단점을 서술하는 방식

본문이 인정한 단점 문장(양보절 포함 약 21개)을 기법별로 나눴다. 한 문장에 여러 기법이 겹친다.

| 기법 | 빈도 | 문형 | 예 |
|---|---|---|---|
| **(a) 바로 상쇄** | 대부분 | 같은 문장의 "while / yet / whereas", 다음 문장의 "However, ..." | "KLEE+TopSeed missed only 15 branches ..., **yet** it exclusively covered 4,281 branches" (ICSE25) / "missed only 7.5 branches on average ..., **while** discovering 1689.4 branches" (ICSE26) |
| **(c) 크기 줄이기** | 매우 흔함 | only, slightly, minimal, negligible, modest, comparable, maintained, less than 1% | "the gap ... was **minimal**" (ICSE25; 실제로는 baseline 4개 중 3개에서 차이 0) / "**maintained** the same coverage in the remaining four" (FSE26; 비김) / "**slightly** higher than BASE" (ICSE25; 실제 +34.7%) |
| **(d) 감수할 비용·예상된 결과** | 3–4 | "This reduction occurs because ...", "Despite the negative side effect, ...", "Unquestionably ... However, if the goal is ..." | FSE26: 입력 수 40% 감소 → 예산 절반을 시퀀스 생성에 쓰는 설계 때문이라고 설명 → "Despite the negative side effect, integrating RSFuzz resulted in noticeably higher line coverage." |
| **(b) 외부 원인** | 2–3 | 벤치마크 특성, 상대의 이점 | "on large benchmarks, which have a greater potential for improvement than smaller ones" (ICSE25; 작은 프로그램에서 향상이 작은 이유를 **앞 문장에서 미리** 깐다) / "primarily because they leverage diverse inputs generated by mutating manually provided seeds" (ASE26) |
| **(e) 장점으로 뒤집기** | 2–3 | 약점이 설계의 필요성을 보여 준다 | "Despite the effectiveness of Kleenew, it still covered 43.1% fewer branches ..." → "This indicates that trying multiple parameter sets over short periods is more efficient ..." (ICSE26) / "the weight for 'uniqueness' fluctuated over time" → 적응성의 증거 (ICSE25) |
| (g) 방어 없이 사실만 | 드묾 | 사소한 비김 | "For Super-CSV, all six fuzzers found the same two unique crashes." (FSE26) |
| (f) Threats로 미루기 | **0** | — | 결과의 약점은 Threats로 넘기지 않는다. Threats는 범위와 가정만 다룬다 (§3 E-7) |

- **위치:** 단점 문장은 대부분 **문단 가운데, 장점 문장 사이**에 둔다. 문단을 단점으로 여는 경우는 하나(FSE26 입력 수)뿐이고, 그 문단도 장점으로 닫는다. **문단과 하위절의 마지막 문장은 언제나 장점이나 함의(C)다.**
- **수치 선택:** 작은 손실은 절댓값("only 15 branches", "only one bug")으로, 큰 이득은 비율이나 배수("3.5 times more", "1,269× longer")로 쓴다. 손실과 이득을 한 문장에 나란히 두어 크기를 대비한다.
- **예외는 이름을 대고 하나만:** "An exception occurs in the factor program" (ICSE25), "An exception was observed for the CSV benchmarks" (FSE26). 원인 설명은 없거나 한 구절이다. 예외를 먼저 밝히는 문장은 나머지 주장을 믿게 하는 장치로 쓰인다.

### 4.3 표에는 있지만 본문이 말하지 않는 것

네 편 모두 **표에는 데이터를 빠짐없이 싣고, 본문은 그중 유리한 것을 골라 말한다**. 표가 감추지 않으므로 거짓은 없지만, 표를 직접 읽어야 보이는 약점이 많다.

| 유형 | 예 | 본문 |
|---|---|---|
| 버그 표의 비김 | ICSE25 Table VI: 7행 중 4행이 TopSeed = Base / ICSE26 Tables 3–5: gawk 1 = 1 = 1 / ASE26 Table 5: 7개 셀이 Pure = Orbis | "improved its bug-finding capabilities", "did not miss any bugs" 같은 총계 문장만 |
| 다른 baseline과의 교차 비교 | ICSE25 Table VIII: CREST+TopSeed가 시드 없는 Chameleon보다 gawk·grep에서 낮다 / ASE26 Table 4: Orbis+X 13개 셀이 같은 행의 최고 Pure 기법보다 낮다 / FSE26 Table 5: ProbF+RSFuzz가 12개 중 8개 벤치마크에서 순수 RandF보다 낮다 | 언급 없음. 이긴 경우만 쓴다 ("CREST occasionally outperformed the advanced, unseeded CHAMELEON on the sed program") |
| 상대만 덮은 영역 | Venn 3개 모두 있다 (ICSE25 KLEE10h만 300개, ICSE26 Chameleon만 288/29/11, ASE26 base만 257/301) | 가장 작은 예 하나("only 15 branches") 또는 비율("10.9x ... more")만 |
| 기본값이 아닌 하이퍼파라미터의 승리 | ICSE25 Table IX: 두 셀에서 기본값보다 좋다 | "generally achieved the most stable and high branch coverage" |
| 다른 계열에 진 총계 | ASE26 Table 10: ZigZagFuzz 단독 20,193 > Orbis 단독 13,395 | 세 fuzzer의 수치를 나열하고 원인("manual seeds")을 붙인다. 졌다고는 쓰지 않는다 |
| 집계 방식 | FSE26 "On average ... 6.0%"는 총합 비율 (벤치마크별 평균은 3.3–4.0%, 계산값) / ICSE25 "95%"도 총합 비율 (벤치마크별 평균 92.3%, 계산값) | 더 큰 쪽을 쓴다 |

네 편 모두 보고하지 않는 것: **도구 자체의 실행 비용(오버헤드)**, **벤치마크별 분산**, **주 결과 밖의 통계 검정**, **시간에 따른 coverage 곡선**.

### 4.4 단점이 덜 보이게 하는 실험 설계

단점은 문장보다 **실험을 설계할 때** 더 많이 걸러진다.

1. **통합(integration) 프레임:** 도구를 baseline *위에* 얹어 "X vs X+Tool"로 비교한다 (4/4). 행마다 자기 자신과 비교하므로 거의 모든 행에서 이기고, 진 셀이 있는 교차 비교는 본문의 질문 밖에 놓인다.
2. **Base를 두 방식으로 돌려 더 좋은 쪽을 보고**한다 (ICSE25·ICSE26·ASE26). 공정성 장치이면서 "baseline을 약하게 돌렸다"는 반론을 미리 막는다.
3. **비용이 큰 분석은 부분집합**에서 한다 (주로 가장 큰 프로그램 5개). 향상이 큰 곳이다 ("which have a greater potential for improvement").
4. **사례 연구는 향상이 가장 큰 대상**을 고른다 ("the diff program, which showed the highest improvement").
5. **통계 검정은 주 결과에만** 하고, "statistically significant"를 논문당 한 번 쓴다.
6. **버그 표에는 버그가 나온 프로그램만** 싣는다 (4/4). 0만 있는 행이 사라진다.
7. **도구 자체의 실행 비용은 따로 재지 않는다** (4/4). 같은 시간 예산 안에서 비교하는 것으로 대신한다.

**정리.** 네 편은 단점을 (1) 평가 문장의 6%에만, (2) 비임계적이고 즉시 방어할 수 있는 것으로, (3) 문단 가운데에 둔다. 더 큰 잠재적 약점(교차 비교의 손실, 오버헤드, 분산)은 문장이 아니라 **비교 프레임과 실험 범위를 고르는 단계**에서 피한다. 다만 표에는 데이터를 다 싣고, 예외 한두 개를 이름을 대고 인정한다. 리뷰어가 표를 직접 읽어도 본문과 모순되지 않는 범위 안에서 장점을 고른다.

---

## 5. 수식·알고리즘·플로트

> 캡션·선·강조·색 같은 디자인은 [floats.md](floats.md) §2–§4를 따른다. 여기서는 하위절마다 **어떤 플로트를 두는지**만 정리한다.

| 하위절 | 플로트 | 예 |
|---|---|---|
| Settings | **벤치마크 표** (2–3단으로 접음) | ICSE25 IV, ICSE26 1, ASE26 2, FSE26 3 |
| 주 지표 | **주 결과표** (벤치마크 × 도구 × 설정, Total 행), 필요하면 분석 그림 | ICSE25 V, ICSE26 2 + Fig. 3, ASE26 3·4, FSE26 5 |
| 부 지표 | **버그 표** (버그가 나온 벤치마크만) | ICSE25 VI, ICSE26 3, ASE26 5, FSE26 4 |
| Ablation | **ablation 표** 1–4개 | ICSE25 VII, ICSE26 4·5, ASE26 6–9, FSE26 6 |
| 일반성 | 작은 표 또는 **Venn 그림** | ICSE25 VIII, ICSE26 Fig. 6, ASE26 Fig. 3, FSE26 Fig. 4 |
| 하이퍼파라미터 | 파라미터 그룹 표 | ICSE25 IX |
| 분석·사례 | 막대·선·범위 그래프, **Venn**(연속 실행 비교), **코드 조각** | ICSE25 Fig. 2–4·X, ICSE26 Table 6·Fig. 4–5, ASE26 사례 코드·Table 10 |

- **수식은 거의 없다** (ASE26 ablation 변형 정의 1개). 변형은 알고리즘 줄 번호로 정의한다.

논문별 §4 플로트와 각 플로트가 보여 주는 결과:

| 논문 | 플로트 (보여 주는 결과) |
|---|---|
| ICSE25 | Table IV 벤치마크 · **Table V 주 결과** (전폭, 17행 × 12열) · Table VI 버그 · Table VII ablation · Fig. 2 feature 가중치의 시간 변화 (선, 전폭) · Table VIII concolic 일반성 · Table IX 하이퍼파라미터 · Fig. 3 10시간 연속 실행과의 겹침 (Venn × 5, 전폭) · Fig. 4 사례 코드 · Table X 건너뛴 SMT 호출 수 |
| ICSE26 | Table 1 벤치마크 · **Table 2 주 결과** · Table 3 버그 · Tables 4–5 ablation (선택 단계·샘플링 단계) · Fig. 3 SymTuner와 고른 파라미터·값 비교 (누적 막대 + 범위) · Table 6 Sobol 상위 파라미터 · Fig. 4 파라미터별 선택 빈도 (막대) · Fig. 5 샘플링 범위 (범위) · Fig. 6 Chameleon 일반성 (Venn × 4) |
| ASE26 | Table 2 벤치마크 · **Tables 3–4 주 결과** (OB coverage, 전체 coverage) · Table 5 버그 · Tables 6–9 ablation (Table 9는 SMT 절감 지표 포함) · Fig. 3 concolic 일반성 (Venn 2 × 4) · 캡션 없는 사례 코드 · Table 10 fuzzer와의 비교 |
| FSE26 | Table 3 벤치마크 · Table 4 크래시 · **Table 5 주 결과** (line coverage) · Fig. 3 coverage-equivalent 비율 (막대 × 3) · Table 6 ablation · Fig. 4 재사용성 (가로 막대, x축 절단) |

그림 유형별 쓰임:

| 유형 | 개수 | 쓰임 |
|---|---|---|
| Venn | 3 | "도구만 / 둘 다 / 상대만" 집합 겹침. 도구가 상대를 **거의 포함함**을 보일 때 (일반성, 연속 실행 비교) |
| 막대 | 4 | 범주별 개수·비율 (선택 빈도, coverage-equivalent 비율, 재사용성) |
| 범위 (dumbbell) | 1 (+ Fig. 3(b)) | 도구가 고른 값의 분포 |
| 선 | 1 | 시간에 따른 내부 값 변화 |
| 코드 | 1 | 사례 연구의 메커니즘 |

- **coverage-over-time 곡선은 네 편 모두 없다.** 결과는 마지막 시점의 평균만 표로 보인다.
- 주 결과표는 **도구 열을 모든 행에서 굵게** 한다. 비긴 행도 도구 쪽을 굵게 하는 경우가 있다 (ICSE25 Table V, FSE26 Table 5).
- **RQ마다 플로트가 최소 1개** 있고, 결과 단락의 첫 문장이 그 플로트를 주어로 삼는다.

---

## 6. 섹션 간 연결

| §4 요소 | 대응 위치 | 관계 |
|---|---|---|
| RQ 목록 | Intro I7 (결과 미리보기), Contributions bullet 3 | Intro의 "We further demonstrate X's efficacy by comparing it with ..., and its generality by applying ..." 문장이 RQ와 일대일로 대응한다 |
| 주 지표 수치 | Abstract M8, Intro I7 | 같은 수치를 쓴다 (반올림 규칙까지 일치시킬 것; [floats.md](floats.md) §7) |
| Baselines | §2.1 SOTA 대응, §2.2 단순 대안, §5 Related Work | 같은 기법이 §2 → §4 → §5에 다시 나온다. §2의 단순 대안이 baseline이 된다 (ICSE25 Algorithm 2 → RandSeed) |
| Benchmarks | §2.2 Table 1 (일부), Intro I7 (개수·규모 범위) | §2.2의 측정은 이 벤치마크의 일부로 한다 |
| Ablation 변형 | §3 단계, §3 forward ref, §3 "we also considered" | §3에서 "as demonstrated in Section 4.4"로 미리 인용한 수치가 여기서 나온다 (ASE26 9.6%, 21.5%, 16.8%) |
| 일반성 | §2.1 Algorithm 1 | 다른 도구로 옮길 때 Algorithm 1(Execute)만 바꾼다 |
| 하이퍼파라미터 | §3 η "by trial and error", Threats | 민감도 분석 → Threats에서 "Although Section IV-E demonstrates ..."로 다시 인용 |
| Threats 완화 근거 | §3 "We acknowledge ..." | ASE26: §3의 hidden options 0.9%와 Threats의 0.7개/프로그램은 표현 단위가 다르다 |
| 사례 연구 | §2 예제 프로그램, §3 메커니즘 | §2·§3의 예제 프로그램(diff, ls)으로 메커니즘을 실측한다 |

---

## 7. 템플릿

```text
## 4 Experiments
In this section, we evaluate <Tool> to answer the following research questions:
  (1) Effectiveness: How effectively does <Tool> improve <metric1> and <metric2> compared to <baselines>?
  (2) Efficacy of Each Stage: How does each stage of <Tool> contribute to its performance?
  (3) Generality: Is <Tool> applicable to <another tool family / setting>?
  (4) <Extra>: <hyperparameters / reusability / analysis question>?
We implemented <Tool> on top of <tool-version> [..], <one-phrase description>. All experiments were conducted on <machine>.

### 4.1 Experimental Settings
Baselines. We compared <Tool> with <N> baselines: (1) <category> (<Name> [..]), (2) .... <Name> [..] is <one-sentence description>.
  We evaluated each baseline in <K> settings: <Base>, <naive variant (Algorithm 2)>, and <Tool>.
Benchmarks. We used <N> <subjects> in Table N. To construct our benchmark suite, we collected all <subjects> used by <baselines> [..].
  We then selected <N> based on two criteria: (1) ... (e.g., <excluded>), and (2) ... (e.g., <excluded>).
Other Settings. We allocated <budget> per <subject>. Each experiment was repeated five times, and we report the average.
  To ensure a fair comparison, we ran each baseline in two ways ... and reported the better result. We measured <metric> using <tool> [..].

### 4.2 <Metric1>
Table N shows that <Tool> significantly improved <metric> across all <subjects>. Overall, <Tool> achieved X% higher <metric> than <SOTA>,
  and A%, B%, and C% higher than <b1>, <b2>, and <b3>, respectively.
Notably, on <largest subject>, .... Interestingly, <baseline> even <worse than naive>. This finding highlights a key limitation of <baseline>: ....
An exception occurs in <subject>, where the gain was small (X%), as <property of subject> leaves little room for improvement.
Although <Tool> <minor loss> (only N <units>), it <larger gain> (M <units>) that <baseline> failed to reach.
Despite <cost> (e.g., X% fewer inputs, because <design reason>), <Tool> still achieved Y% higher <metric>.
These results were statistically significant: the Mann-Whitney U test [..] yielded p-values below 0.05 in <k> of <n> cases. The standard deviations were ... (...).
These results indicate that ....

### 4.3 <Metric2: bugs>
To obtain these results, we collected ..., re-executed ..., and retained only reproducible .... A bug was considered unique if ....
In total, <Tool> detected <N> unique bugs, <k> more than <SOTA>. Notably, <Tool> did not miss any bug detected by other baselines.
All bugs were reported to the developers, and <k> were confirmed.

### 4.4 Efficacy of Each Stage
We compared <Tool> with <k> variants: <Tool>-<Stage>, which omits ...; Rand<Stage>, which replaces <F> (line N of Algorithm M) with ....
Table N confirms the critical role of each stage: <Tool> achieved X%, Y% higher <metric> than .... We investigated why ...: the key difference is ....
These findings demonstrate that both <A> and <B> are essential for the effectiveness of <Tool>.

### 4.5 Generality
We examined whether <Tool> is applicable to <family>. Integrating <Tool> into <engine> corresponds to replacing the Execute procedure (Algorithm 1) ....
On average, <Tool> increased <metric> by X% for <e1> and Y% for <e2>. These results demonstrate the generality of <Tool>.

### 4.6 Threats to Validity
(1) We evaluated <Tool> on <engines>; its performance may vary on other engines. (2) <hyperparameters> were determined by trial and error.
Although Section 4.x shows stable performance ..., these settings may not be optimal for .... (3) Our <N> benchmarks ... may not be representative.
```

---

## 8. 작성 체크리스트

- [ ] 리드에 RQ 4–5개를 "**Name**: question?" 형식으로 두고, RQ 이름과 하위절 제목이 같은가
- [ ] RQ에 주 지표·부 지표·ablation·일반성이 모두 있는가
- [ ] 구현 기반(도구-버전)과 장비를 한두 문장으로 밝혔는가
- [ ] Baselines에 범주·한 줄 설명·인용이 있고, 제안 기법의 단순판(§2 단순 대안)이 baseline에 들어갔는가
- [ ] Benchmarks가 선행 연구의 합집합에서 출발하고, 필터 기준 (1)(2)와 제외 예시가 있는가
- [ ] 예산, 5회 반복 평균, 공정성 장치, 측정 도구를 밝혔는가
- [ ] 결과 단락이 H → Q → N → S → T → C 순이고, 첫 문장이 표·그림을 주어로 하는가
- [ ] 이상치를 숨기지 않고 원인과 함의(대개 baseline의 약점)를 썼는가
- [ ] 통계 검정 이름·인용·p 기준·예외, 표준편차를 썼는가
- [ ] 버그 집계 방법(재현, 고유성 기준)과 개발자 보고·확인을 썼는가
- [ ] ablation 변형을 알고리즘 줄 번호로 정의하고, 왜 이겼는지 설명했는가
- [ ] 일반성 실험에서 이식 방법(Algorithm 1의 어디를 바꿨는지)을 밝혔는가
- [ ] 사례 연구가 향상이 가장 큰 대상을 골라 구체적 수치 대비로 끝나는가
- [ ] Threats가 (1)(2)(3) 한 단락이고, 항목마다 완화 근거가 있는가
- [ ] 본문 수치·표·Abstract·Intro가 모두 같은 산출물에서 나왔는가 ([floats.md](floats.md) §7)
- [ ] 우열 결과는 표로, 원인 분석은 그림으로 나눴는가 (표가 ~70%)
- [ ] 실험 규모(벤치마크 × baseline × 예산 × 5회)를 곱셈식으로 밝혔는가
- [ ] 단점 문장이 평가 문장의 한 자릿수 %이고, 각 단점에 같은/다음 문장의 방어(원인·크기·대가)가 붙어 있는가
- [ ] 단점 문장이 문단 가운데 있고, 문단과 하위절이 장점이나 함의로 끝나는가
- [ ] 예외를 하나 이상 이름을 대고 인정했는가
- [ ] 표에서 도구가 지거나 비긴 셀을 모두 점검했고, 본문이 다루지 않는 셀이 본문의 주장("across all", "each baseline")과 모순되지 않는가 (리뷰어는 표를 직접 읽는다)

---

## 부록 A. 원문 발췌 (역할 태그)

**RQ 목록 (E-0)**

> **[ICSE25]** In this section, we evaluate the effectiveness of TopSeed based on the following research questions:
> 1) **Effectiveness:** How effectively can TopSeed enhance state-of-the-art techniques for symbolic execution in terms of branch coverage and bug-finding capability?
> 2) **Efficacy of Each Stage:** How effectively does each stage in TopSeed contribute to improving the performance?
> 3) **Generality:** Is TopSeed applicable to a concolic testing technique, a variant of dynamic symbolic execution?
> 4) **Impact of Hyperparameters:** How do hyperparameter values affect the performance of TopSeed?
>
> We implemented TopSeed on top of KLEE-2.1 [4], an actively maintained symbolic executor that incorporates diverse techniques [11], [15], [17], [18], [26]. All experiments were conducted on a single Linux machine equipped with two Intel Xeon Gold 6230R processors.

> **[ICSE26]** We evaluate ParaSuit to answer the following research questions:
> - **Branch coverage**: To what extent does ParaSuit improve branch coverage over manual and user-configured tuning methods?
> - **Bug-finding ability**: How effectively can ParaSuit find unique bugs compared to existing tuning approaches?
> - **Efficacy of two stages**: Does our parameter selection algorithm outperform naive approaches? Is our value sampling stage more effective than generic sampling methods?
> - **Analysis of self-configuration**: Which parameters are most impactful? How do they and their values vary by program? Does the new setting sampled by ParaSuit surpass existing baselines?
> - **Generality**: Can ParaSuit be applied to concolic testing tools?

**Settings (E-1)**

> **[ICSE25 · Benchmarks.]** We used 17 open-source C programs in Table IV, which displays the number of lines and branches for each program. To construct our benchmark suite, we initially collected all available programs used in the experiments by the four baselines [4], [11], [15], [18]. From these, we selected 17 program benchmarks for evaluation based on two filtering criteria among them: (1) we filtered out smaller programs with fewer than 1,000 total branches, as the baselines achieved high code coverage for these programs even without seeding (e.g., tty-8.31). (2) we also omitted programs (e.g., objcopy-2.36) where all baselines managed to cover less than 2.0% of total branches over 10 hours, indicating that the baselines failed to test the core functionality of these programs and only test error handing functions. Note that for our 17 programs, at least one of the four baselines was able to cover more than 22.5% of total branches on average within 10 hours.

> **[ASE26 · Other Settings.]** For all experiments, we tested each baseline with and without Orbis's guidance on each benchmark using a 24-hour budget, repeating the same experiment five times. We then reported the average results, which indicate that our experiments were conducted extensively. For instance, generating the coverage results reported in Table 3 required 18,000 hours when using a single CPU core (i.e., 24 hours × 5 trials × 15 benchmarks × 5 baselines, each tested with and without Orbis). Additionally, to ensure a fair comparison with Orbis, we evaluated baselines under both settings: (1) a single uninterrupted 24-hour run and (2) repeated shorter runs whose results were merged, matching the execution setting of Orbis. We reported the better-performing result for each baseline.

**주 지표 (E-2)**

> **[ICSE26 · H + Q + N + S]** Table 2 demonstrates that ParaSuit consistently outperforms both static and user-defined configuration approaches in terms of branch coverage across all 12 benchmarks. We used gcov to collect the covered branches for each benchmark. In summary, ParaSuit covered 25.8% more branches than Symtuner, 97.4% more than Kleefix, 46.8% more than RandSuit, and 95.6% more than SymtunerAllP. Notably, ParaSuit, our self-configuring approach, consistently achieves higher branch coverage than Symtuner, which relies on manually defined configurations. For instance, in the case of the largest program xorriso, ParaSuit achieved 106.6% higher branch coverage than Symtuner, the second-best baseline—making the largest difference across all benchmarks. Interestingly, in grep, Symtuner even covered 2% fewer branches than RandSuit, which naively selects parameters and their corresponding values. This finding highlights a key limitation of Symtuner—its use of a predefined configuration regardless of the target program.

> **[ICSE25 · S + T]** Running each baseline with a random seed selection strategy (RandSeed) typically resulted in higher branch coverage compared to running it without seeds (Base). However, RandSeed sometimes underperformed relative to Base. ... Surprisingly, for the dd program, Learch+RandSeed covered 63.2% fewer branches than Learch+Base. This inconsistency of RandSeed underscores the necessity of our approach (Algorithm 3) to achieve stable and high coverage across various benchmark programs.
>
> These results in Table V were statistically significant: on 16 of the benchmark programs, the p value between Base and TopSeed across the four baselines was less than 0.05 according to the Wilcoxon signed-rank test. An exception occurs in the factor program, where the gap in branch coverage between TopSeed and Base across four baselines was minimal. The standard deviations of branch coverage across four baselines on our benchmarks were as follows: Base (38.6), RandSeed (73.1), and TopSeed (52.0). As expected, RandSeed showed the highest variability. While the standard deviation of TopSeed was slightly higher than Base, this difference was negligible given the significant performance improvements achieved by TopSeed.

**부 지표 (E-3)**

> **[ICSE26]** Table 3 shows the effectiveness of ParaSuit in identifying unique bugs compared to other baselines. To obtain these results, we collected all test-cases flagged by KLEE as bugs, denoted as the "*.err" files. We then re-executed the original binary of each program with these potential bug-triggering test-cases and retained only those that were reproducible. A bug-triggering test-case was considered unique if its error location reported by KLEE differed from others. ... In total, ParaSuit succeeded in detecting 11 unique bugs across three of the 12 programs: gcal, gawk, and combine. This count is 4 more than the state-of-the-art Symtuner; ... Notably, ParaSuit did not miss any bugs that other baselines detected, while it successfully identified four additional bugs. All bugs discovered by ParaSuit were reported to the program developers ...

**Ablation (E-4)**

> **[ASE26 · 왜 이겼는지]** We investigated why Orbis notably outperformed CitConst. The key difference is their objective. As a state-of-the-art CIT technique, CitConst systematically exercises option combinations while minimizing the number of generated option arguments. Consistent with this objective, it selected substantially more options per option argument than Orbis (37.4 on average, 9.4× more). When applied to symbolic execution, however, these large option arguments often resulted in ineffective executions: 68.6% either achieved zero branch coverage or terminated before exhausting the time budget, frequently due to conflicting or ineffective option combinations. ... In contrast, Orbis continuously evaluates the effectiveness of option arguments during symbolic execution and repeatedly reuses those that prove effective in improving exploration.

**일반성 (E-5)**

> **[ICSE25]** We examined if our seeding approach is applicable to concolic testing [1], [3], a major variant of symbolic execution. We integrated TopSeed with CREST [28], a popular concolic testing tool that incorporates diverse techniques [29], [30], [31], [32]. Additionally, we evaluated TopSeed's potential to enhance the performance of Chameleon [32], a state-of-the-art search strategy implemented on CREST. For each baseline, we reported the number of branches covered and bugs identified across the three large benchmarks used in [32]. ... On average, TopSeed increased branch coverage by 7.8% compared to CREST and 3.9% compared to Chameleon. Interestingly, with the seeding provided by TopSeed, the basic concolic testing tool CREST occasionally outperformed the advanced, unseeded Chameleon on the sed program. ... These results indicate that TopSeed is versatile and can be generalized to other symbolic execution tools, significantly enhancing both branch coverage and bug-finding abilities.

**사례 연구 (E-6)**

> **[ASE26 · 4.6 Case Study]** To illustrate how Orbis guides symbolic execution to achieve higher total branch coverage, we conducted a case study on the diff program. Particularly, we analyzed an effective test-case ("diff -p -0") that covers 471 branches in a single execution, accounting for 48.3% of the total coverage achieved by KLEE within a 24-hour budget. We then compared the average time required by KLEE with and without Orbis's guidance to generate this test-case. ... Empirically, KLEE with Orbis generated the test-case "diff -p -0" in just 7.1 seconds. ... In contrast, KLEE alone required 9,012.7 seconds to generate the entire argument "-p -0" symbolically—approximately 1,269× longer.

**단점 서술 (§4.2)**

> **[ICSE25 · b + c]** Particularly, TopSeed dramatically increased branch coverage achieved by four baselines on large benchmarks, which have a greater potential for improvement than smaller ones. ... Conversely, on the five smallest programs, the improvements were modest, with TopSeed integration resulting in coverage increases of 22.8%, 4.3% and 10.3% for Learch, Homi, and KLEE-Array, respectively, highlighting smaller gains compared to larger programs.

> **[ICSE25 · a + c + d]** As expected, RandSeed showed the highest variability. While the standard deviation of TopSeed was slightly higher than Base, this difference was negligible given the significant performance improvements achieved by TopSeed.

> **[ICSE26 · a + e]** Despite the effectiveness of Kleenew, it still covered 43.1% fewer branches and missed seven bugs compared to ParaSuit, which iteratively explores a variety of parameter sets for short durations. This indicates that trying multiple parameter sets over short periods is more efficient than running symbolic execution with a single fixed parameter setting, ...

> **[ASE26 · a + b + d]** In contrast, these fuzzers exclusively covered 20,193, 6,505, and 6,211 branches, primarily because they leverage diverse inputs generated by mutating manually provided seeds, while Orbis operates without such manual seeds and relies on symbolic inputs. ... In terms of bug detection, Orbis detected four, seven, and six additional bugs compared to ZigZagFuzz, OSmart, and CarpetFuzz, respectively, while missing only one bug in objdump.

> **[FSE26 · d + a]** When combined with RSFuzz, the number of inputs generated decreased by 40% for RandF, 33% for ProbF, and 45% for Tribble. This reduction occurs because RSFuzz allocates half of the total testing budget (12 hours) generating recurrent sequences, whereas the baseline fuzzer spends the entire budget generating inputs. Despite the negative side effect, integrating RSFuzz resulted in noticeably higher line coverage.

> **[FSE26 · d + a]** Unquestionably, RSFuzz achieves the best results when it generates recurrent sequences from a specific program and uses them exclusively for testing that program. ... However, if the goal is to reduce the overhead of generating recurrent sequences, reusing sequences from one program to test others with the same input format is a practical and effective alternative.

**Threats (E-7)**

> **[ICSE25 · G. Threats to Validity]** (1) TopSeed was evaluated using KLEE and CREST, which are prominent symbolic executors. Its performance may vary when applied to other symbolic executors. (2) The three hyperparameters in TopSeed, used for running the symbolic execution engine KLEE, were determined through trial and error. Although Section IV-E demonstrates stable performance across our benchmark suite and another symbolic execution engine, CREST, these settings may not be optimal for other programs or symbolic engines. (3) We used 17 carefully selected benchmarks. While this benchmark suite includes all major programs used in the four baselines, it may not sufficiently evaluate the full scope of TopSeed's performance.
