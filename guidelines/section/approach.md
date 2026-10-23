# Our Approach — guidelines 4편 분석

[skeleton.md](skeleton.md)의 하위 문서. §3 Our Approach를 하위절 → 단락 단위로 분석한다.
본문의 약 31%를 차지하는 가장 긴 기술 섹션이며, **수식·알고리즘이 가장 많이 나오는 섹션**이므로 §5를 특히 자세히 다룬다.
수식·알고리즘·그림은 PDF 페이지 이미지로 직접 확인했다. 원문 발췌는 부록 A에 실었다.

---

## 0. 핵심 규칙

1. Approach는 **~2,500 words, ~25단락**이다. 구성은 **3.1 Overview(그림) → 3.2 [Tool](메인 알고리즘) → 단계별 하위절**로 고정이다. 플로트는 overview 그림 1개, 메인 알고리즘 1개(17–28줄), display 수식 ~15–20개다.
2. **단계 이름 3–4개를 모든 곳에서 똑같이 쓴다.** overview 그림의 상자, 알고리즘 주석(`/* Step 1. ... */`), 알고리즘이 호출하는 함수 이름, 하위절 제목이 모두 같은 단어다.
3. 단계 하위절은 **목표 문장 → 줄 번호를 따라가는 절차 → 형식 정의(display) → "Intuitively, ..." → 수치 예제 → 설계 근거** 순으로 쓴다.
4. 수식 관용구가 정해져 있다. 데이터 레코드는 튜플(와일드카드 `_`), 점수는 set-builder 함수, 선택은 argmax, 확률은 정규화 비율이다. **번호는 뒤에서 다시 참조하는 식에만** 붙인다(0–5개). 수식 뒤에는 거의 항상 **"Intuitively, ..."** 한 문장을 단다.
5. 하이퍼파라미터는 **η**로 이름 짓고 알고리즘 주석에 기본값을 적으며, 본문에서 **"set ... by trial and error"**라고 밝힌다. 설계 선택은 **§4.4 ablation을 forward ref**해서 정당화한다.

---

## 1. 분량

| ID | 하위절 구성 (단어 수, 비율) | 합계 | 단락 수 (추정) | 평균 단락 |
|---|---|---|---|---|
| ICSE25 | 리드 71 (3%) · A. Overview 180 (8%) · B. TopSeed 276 (12%) · C. Data Gathering 160 (7%) · **D. Seed Selecting 1,056 (47%)** · E. Distribution Learning 513 (23%) | 2,256 | ~23 | ~98 |
| ICSE26 | 3.1 Overview 269 (12%) · 3.2 ParaSuit (+Extract) 688 (29%) · 3.3 Parameter Selection 477 (20%) · **3.4 Value Sampling 905 (39%)** | 2,339 | ~26 | ~90 |
| ASE26 | 3.1 Overview 185 (7%) · 3.2 Orbis 170 (6%) · **Extract 827 (31%)** · Construct 569 (21%) · Guide 446 (17%) · Update 484 (18%) | ~2,500 | ~25 | ~100 |
| FSE26 | 3.1 Overview 239 (8%) · 3.2 RSFuzz 50 (2%) · 3.2.1 Collecting 161 (6%) · 3.2.2 Grouping 502 (17%) · 3.2.3 Selecting 409 (14%) · **3.2.4 Capturing 1,227 (42%)** · 3.3 Fuzzing with RS 303 (10%) | 2,891 | ~27 | ~107 |
| **평균** | Overview **~9%**, 메인 알고리즘 **~12%**, 단계별 **~79%** | **~2,500** | **~25** | **~100** |

- 2단 논문은 단(column) 단위로 잘라 다시 추출한 텍스트로 셌다. ASE26은 이 방식에서 알고리즘 일부가 섞여 [skeleton.md](skeleton.md) 표(2,502)보다 약간 많게 나와 ~2,500으로 적었다.
- **가장 긴 단계가 단계 전체의 40–50%를 차지한다** (ICSE25 Seed Selecting, ICSE26 Value Sampling, ASE26 Extract, FSE26 Capturing). 대개 논문의 핵심 신규성이 있는 단계다.

| ID | 메인 알고리즘 | 보조 알고리즘 | display 수식 (번호) | 그림 | 표 | 코드형 display | 예제 블록 |
|---|---|---|---|---|---|---|---|
| ICSE25 | Algorithm 3 (27줄) | — | ~20 (3) | Fig. 1 overview | Table II, III (정의표) | — | — |
| ICSE26 | Algorithm 1 (25줄) | Algorithm 2 (10줄) | ~16 (2) | Fig. 2 overview | — | 2 (help 출력, C++ 소스) | 수치 계산 2 |
| ASE26 | Algorithm 2 (17줄) | Seeding procedure (11줄, 캡션 없음) | ~15 (0) | Fig. 2 overview | — | 1 (help 출력) | — |
| FSE26 | Algorithm 2 (28줄) | — | ~16 (5) | Fig. 1 overview, Fig. 2 유도 트리 | — | 다수 (기호 시퀀스) | Example 3.1–3.3 |

---

## 2. 구조

### 2.1 하위절 유형

| 유형 | 내용 | 출현 |
|---|---|---|
| A-0 리드 | "In this section, we introduce ..." + 단계 이름 예고 | 1/4 (ICSE25) |
| **A-1 Overview** | overview 그림 + 단계당 1–2문장 | 4/4 (항상 3.1) |
| **A-2 [Tool]** | 메인 알고리즘 해설 (입출력, 초기화, 하이퍼파라미터, 루프) | 4/4 (항상 3.2, 제목 = 도구명) |
| **A-3 단계별** | 단계마다 하나씩 | 4/4 (하위절 2편, bold run-in 1편, 3.2.x 1편) |
| A-4 산출물 사용 | 제안 기법의 출력이 §2 Algorithm 1의 훅으로 들어가는 방식 | 1/4 (FSE26 3.3 Fuzzing with Recurrent Sequences) |

**단계 하위절의 형식은 논문마다 다르다.**

- ICSE25: 독립 하위절 (C. Data Gathering / D. Seed Selecting / E. Distribution Learning). 하위절 안에서 다시 bold run-in(**Exploration Strategy.** / **Exploitation Strategy.**)
- ICSE26: 1회성 단계(Extract)는 3.2 안의 bold run-in, 반복 단계는 독립 하위절 (3.3 / 3.4). 3.4 안에서 다시 bold run-in(**Explore.** / **Exploit.**)
- ASE26: 모든 단계를 3.2 안의 bold run-in으로 (**Extract.** / **Construct.** / **Guide.** / **Update.**)
- FSE26: 3.2.1–3.2.4 소하위절(이탤릭 run-in 제목). 그 안에서 다시 bold run-in(**Selecting NewG.** / **Capturing from ReG.**)

→ **2단계 계층(하위절 → bold run-in)**이 공통이다. 전략·분기(Explore/Exploit, NewG/ReG)는 bold run-in으로 나눈다.

### 2.2 단계 하위절의 단락 역할

| 기호 | 역할 | 대표 표현 |
|---|---|---|
| **G** | 단계 목표 | The goal / aim / objective of the X stage is to ... |
| **L** | 줄 번호를 따라가는 절차 | At line 4, ... / (lines 15–17) |
| **F** | 형식 정의 (display) | Formally, ... is defined as: / as follows: |
| **I** | 직관 | Intuitively, ... / The intuition behind ... is that ... |
| **E** | 구체 예제 | For example, consider ... / Example 3.1. |
| **R** | 설계 근거·대안·하이퍼파라미터 | We selected X because ... / We also considered ... However, ... / set to 120 by trial and error |
| **A** | 평가로 forward ref | as demonstrated in Section 4.4 / Empirically, ... |
| **X** | 전환·마무리 | Now, we proceed to ... / In this manner, X ... |

### 2.3 논문별 배치 (대표 단계 하나씩)

| ID · 단계 | 단락 흐름 |
|---|---|
| ICSE25 · D. Seed Selecting | G → L(Explore) → F(G_i) + I → F(π, Score, argmax) → F(features 1–5) + Table II → L(Select) + Table III → L(Exploit) → F(B_seed, Freq′ (1), Eval (2)) → R(k-means) |
| ICSE26 · 3.3 Parameter Selection | G + I("we define promising parameters as ...") → L → F(Frequency) → E(TotalB 예) → F(Score (1)) + I → F(bs_p, S_p) + I(penalty) → L(확률 선택) + E → X |
| ASE26 · Construct | G → L → F(feat : 𝕆 → ℝ) → F(feat1–3 목록) + I → E(확률로 "-Rn" 조합) + A(Empirically, 평균 4개) → I(조합이 좋을수록 자주 선택) → L |
| FSE26 · 3.2.4 Capturing | G → F(G_θ) → E(단순 방법) + N(overly general) → 3단계 예고 → **Capturing from NewG.** E(1)(2)(3) + R(DBSCAN·OPTICS 대신 MeanShift) → **Capturing from ReG.** F(rs_prev) + R → Example 3.2 (4)(5) → L → X |

**정형 순서:** G → L → F → I → E → R → (A) → X. 이 순서를 단계마다 반복한다.

---

## 3. 단위별 분석

### A-0 리드 (ICSE25만)

> "In this section, we introduce a novel approach named TopSeed, designed to automatically learn seed selection strategies based on data accumulated from interactions with a symbolic executor. **Initially, we outline the overall process of** TopSeed. **We then provide a detailed description of** our data-driven seed selection strategies, **encapsulated in Algorithm 3, which consist of three stages: Gather, Select, and Learn.**"

나머지 3편(ACM 포맷)은 리드 없이 바로 3.1 Overview로 시작한다.

### A-1 Overview — 그림 + 단계별 한 문장

| ID | 첫 문장 | 단계 예고 |
|---|---|---|
| ICSE25 | "**Figure 1 illustrates how** TopSeed automatically selects promising seeds **while interacting with a symbolic executor**." | "TopSeed identifies the optimal seed **through three phases: Gather, Select, and Learn**." |
| ICSE26 | "**Figure 2 provides an overview of** ParaSuit, **which operates in three main stages: Extraction, Selection, and Sampling**." | (첫 문장에 포함) |
| ASE26 | "**Figure 2 illustrates the interaction between** Orbis **and the symbolic executor**." | "Orbis coordinates symbolic execution **through four stages: Extract, Construct, Guide, and Update**." |
| FSE26 | "**Figure 1 illustrates an overview of how** our approach, RSFuzz, **interacts with a grammar-based fuzzer**." | "RSFuzz performs **four main steps: (1) collecting ..., (2) grouping ..., (3) selecting ..., and (4) capturing ...**" |

- 흐름: 그림 소개(기존 도구와 **상호작용**하는 구도) → 단계 이름 나열 → 1회성 단계("Initially, ... / The first stage, Extraction, ...") → 반복 단계("Once ... is complete, X iteratively executes the subsequent two stages ... until the allocated total budget expires") → 단계마다 1–2문장 → 반복·반환("This process repeats until the entire budget is exhausted. Finally, X returns ...")
- 단계 설명에 직관을 한 구절 덧붙인다: "**Intuitively,** parameters receive higher scores if they tend to cover many of the rarely reached branches and work synergistically with others" (ICSE26)
- **신규성 위치를 밝힌다** (FSE26): "**The key novelty of RSFuzz lies in addressing two significant challenges in the "selecting" and "capturing" steps.** ... An extreme approach—... —has been shown to be inefficient, **as demonstrated in Section 4.4**."
- **사용 시나리오** (FSE26): "A typical usage scenario is to first run RSFuzz (Algorithm 2) to generate recurrent sequences for half of the total budget, and then ..."
- 분량은 180–270 words, 2–3단락이다.

### A-2 [Tool] — 메인 알고리즘 해설

- **도입:** "We now explain how TopSeed iteratively selects ... **by following Algorithm 3 step by step**." / "Algorithm 1 **offers a detailed description of how** ParaSuit iteratively ..." / "Algorithm 2 **details how** Orbis guides ..." / "Algorithm 2 **provides a detailed explanation of how** our approach generates ..."
- **입출력:** "ParaSuit **accepts only two inputs**: the program (pgm) to be tested and the total time budget (time). Once time is exhausted, Algorithm 1 outputs the total set of covered branches (UnionB)." 입력이 적다는 점(사용자 개입 없음)을 강조한다.
- **§2의 단순 대안과 비교:** "**Similar to Algorithm 2**, our approach (Algorithm 3) takes as input ..." (ICSE25)
- **초기화:** "At line 1, it initializes three sets—D, BaseD and TotalB—as empty sets."
- **하이퍼파라미터 + 이유 + 값:**
  - 이유: "Since ParaSuit aims to find suitable parameters ... without prior knowledge, it **inevitably needs to** run the symbolic execution tool multiple times ..."
  - 값: "In our experiments, the initial small time budget (η_time) **was set to 120 seconds by trial and error**."
  - 관찰 근거: "we set the probabilities for Explore and Exploit to 75% and 25% ... **This distribution is based on our observation that** ..."
- **예산 보장** (ASE26): "If the doubled value of time_s exceeds the remaining testing budget, Orbis sets time_s to the remaining budget ... **Consequently, the cumulative execution time never exceeds the total testing budget (time).**"
- **다음 하위절 예고:** "The roles of w and p will be further discussed in Section III-D."
- 분량은 50–280 words. FSE26은 50 words로 짧고 나머지를 3.2.x로 넘긴다.

### A-3 단계별 하위절

#### G — 목표 문장 (단계마다 첫 문장)

- "**The aim of the Gather stage is to** obtain informative data, which will be used to refine and apply our seed selection strategies in subsequent stages."
- "**The goal of the Selection stage is to** choose from all available parameters promising ones that are essential for effectively testing the target program (lines 15–17)."
- "**The goal of the Construct stage is to** form a new option argument (Arg_new) from the set ArgD ..."
- "**The first step aims to** gather the data D, which will be used to generate recurrent sequences in subsequent steps."
- "**The objective of the Capture step is to** extract effective recurrent sequences from each group G_θ ..."
- 목표 문장 끝에 **해당 알고리즘 줄 범위**를 붙이는 경우가 많다 ("(lines 15–17)").
- 목표 바로 뒤에서 핵심 개념을 정의하기도 한다: "**Intuitively, we define** promising parameters **as those that (1)** reach many branches, **(2)** cover infrequently reached branches, **and (3)** produce synergy when combined with other parameters."

#### L — 줄 번호를 따라가는 절차

- 거의 모든 단락에 줄 번호가 있다: "(line 16)", "At lines 3–9, for each parameter p, ...", "at line 25".
- 개괄 → 상세 순서: "At a high-level, the Explore strategy aims to ... Conversely, ..." → "More specifically, we partition the set D into subsets ... (line 16)."
- 다른 단계·알고리즘을 다시 짚는다: "**Recall that** Algorithm 1 adds a singleton set containing B to TotalB (line 11) to track ..."

#### F + I — 형식 정의와 직관

- 정의 직후 **직관 문장**을 단다 (4/4):
  - "**Intuitively,** this function assigns a higher score when the set B is larger and each branch b in B has a lower occurrence frequency."
  - "**Intuitively,** this feature estimates the potential of Arg based on how many of its associated branches remain uncovered."
  - "**Intuitively,** UG denotes the subset of TotalG that has not been utilized for generating recurrent sequences."
  - "**This scoring quantifies** a seed's ability to cover branches and the rarity with which these branches are typically reached."
  - "**This formula implies that** clusters with higher average scores are more likely to be selected."
  - "**The intuition behind this penalty is that** if p performs worse when tuned simultaneously with others compared to tuning it alone, then p likely does not contribute positively in combination."
- 정의 대상의 **개수와 설계 의도**를 함께 밝힌다: "In this work, we developed five features to effectively characterize input groups ... **These features aim to capture simplistic yet meaningful attributes** of each group **without incurring burdensome feature extraction costs.**" / "we define three atomic features that estimate ... **while keeping feature extraction lightweight**."

#### E — 구체 예제

- **수치 예제** (가장 흔함): "For instance, consider the set TotalB containing two sets of covered branches: TotalB = {{b1, b2, b3}, {b1, b4}}. In this set, the frequency of b1 ... is 2 while the frequency of b2 is 1."
- **계산 과정을 display로**: P(C_1) = 27/34, v′_mem ≈ 2.48GB (ICSE26)
- **§2의 예제를 재사용**: ASE26은 §2 Figure 1의 `ls -l`로 trace를 계산하고, FSE26은 §2의 JSON 문법 𝔾_J와 "[]", "[[]]"를 계속 쓴다.
- **실제 산출물**: KLEE `--help` 출력, KLEE C++ 소스 코드(ICSE26), help 스크립트(ASE26)
- **예제 블록** (FSE26, ACM 저널 포맷): "*Example 3.1.* Assume that the set UG consists of four uncaptured groups, ... In this example, we choose ..."
- **확률 예제**: "consider three individual option arguments in ArgD: "{-R}", "{-n}", "{-w}", with probabilities of 27.3%, 65.5%, and 7.2%, respectively. If the first two arguments are sampled ..., the resulting combined option argument becomes "{-Rn}"."

#### R — 설계 근거, 대안, 하이퍼파라미터

- **선택 이유:** "**We selected** line coverage as the grouping criterion **because it provides a practical balance between** overly fine-grained metrics, such as path coverage, **and** coarser metrics, such as method coverage, ..."
- **기각한 대안:** "In this work, **we also considered alternative** clustering algorithms, such as DBSCAN [12] and OPTICS [1]. **However, we observed that these methods were generally less effective than** MeanShift, since ..."
- **단순 방법이 실패하는 이유:** "A simple approach is to ... **Unfortunately, this recurrent sequence is overly general**, preventing ..." / "This approach allows for a more accurate estimation ... **rather than** choosing randomly from a vast pool of candidate values."
- **차용한 기법은 인용과 한 줄 설명:** "we use mean shift clustering [25], a well-known non-parametric method that identifies clusters without requiring the number of clusters in advance" / "the silhouette coefficient [72]" / "the k-means clustering algorithm [25] (where k to 2)"
- **한계를 먼저 인정:** "**We acknowledge that** some hidden options may not appear in the help script. **However, as discussed in Section 4.8**, these constitute only 0.9% of all options ..., Therefore, our approach adopts the cost-effective strategy of ..."
- **예외 처리:** "Exceptionally, if the distributions derived from TopW^i and BotW^i are similar, values are sampled from a uniform distribution ..."

#### A — 평가로 forward ref

- "... has been shown to be inefficient, **as demonstrated in Section 4.4**."
- "**Empirically**, this procedure enables Orbis to derive effective initial states ... within only 9.6% of the total time budget on average, resulting in a 21.5% branch coverage improvement, **as shown in Section 4.4**."
- "**Empirically, across our benchmark suite**, Orbis generated option arguments combining 4 individual options on average (up to 13.2 options)."
- "**As discussed in Section 4.4**, this solver cost-reduction method using ArgD reduced the overall number of solver calls by about 16.8% ..."

#### X — 전환·마무리

- 단계 사이: "**Now, we proceed to the second iterative stage:** assigning an appropriate value for each chosen parameter." / "**After completing the Extraction stage,** Algorithm 1 enters an iterative process of ..." / "**Before proceeding to the next stage,** the Sample function determines ..."
- 섹션 끝 (4/4):
  - "**In this manner, without prior knowledge,** TopSeed intelligently selects promising seeds based on 𝒫_w and 𝒫_p, which are continuously updated based on the accumulated data D during symbolic execution."
  - "**In this way,** ParaSuit selects appropriate parameters ... **Ultimately,** ParaSuit enables more effective testing of each program without any user-driven configuration."
  - "Through this update, ... The process repeats until the time budget is exhausted, gradually converging on the most effective option arguments and promising states."
  - "Algorithm 2 (RSFuzz) iteratively performs the process of collecting, grouping, selecting, and capturing stages until the allotted time budget (time) is exhausted. Upon completion, it returns the set RS ..."
- 마무리 문장에서 **단계 이름을 다시 나열**하고 **"without prior knowledge / without any user-driven configuration"**을 반복한다.

### A-4 산출물 사용 (FSE26 3.3)

§2 Algorithm 1에 넣어 둔 훅(RS)을 여기서 채운다.

- "After obtaining recurrent sequences from Algorithm 2, we now perform grammar-based fuzzing (Algorithm 1), using these sequences to guide rule expansion decisions ... **Let us delve into how** the Generate function in Algorithm 1 generates each input while utilizing both grammar 𝔾 and recurrent sequences RS."
- 집합 I(훅 없이 만들 수 있는 입력)와 I_R(훅을 썼을 때의 입력)을 정의해 차이를 보인다 → *Example 3.3*

다른 논문은 별도 하위절 없이 메인 알고리즘의 호출(SymbolicExecutor(pgm, time_s, seed), Execute(pgm, time_s, Arg_new, S_P))이나 Guide 단계에서 훅을 채운다.

---

## 4. 문체 특징

| 항목 | 관찰 |
|---|---|
| 주어 | **도구명**(TopSeed, ParaSuit, Orbis, RSFuzz), **Algorithm N / the algorithm**, **this function / feature / strategy**. 설계 결정은 **we**(we define, we set, we developed, we also considered) |
| 시제 | 기법 동작은 **현재형**. 설정값과 관찰은 **과거형**("was set to 120 seconds", "we observed that") |
| 연결어 | Specifically, / More specifically, / To achieve this, / To do so, / Formally, / Intuitively, / Recall that / Note that / Conversely, / Finally, / In this manner, |
| 줄 번호 | 거의 모든 단락에 1개 이상 ("(line 16)", "at lines 15–16") |
| 인용 | **차용한 기법에만** 단다 (k-means, mean shift, silhouette, Tree-sitter, DBSCAN, OPTICS). 선행 연구 비교는 거의 없다 ("more accurately and efficiently than other existing techniques [33, 71]" 정도) |
| 수치 | 결과표는 없다. 수치는 하이퍼파라미터 값, 예제 값, "Empirically, ..." 근거만 쓴다 |
| hedging | 직관 설명에서 약하게 쓴다 ("may possess similar potential", "likely does not contribute"). 나머지는 단정형이다 |
| 따옴표 용어 | 의미를 새로 부여하는 일반어: "promising", "meaningful", "help" command |
| **넣지 않는 것** | 실험 결과표, Related Work식 비교, 섹션 로드맵(ICSE25 리드 제외) |

---

## 5. 수식·알고리즘·플로트

> 캡션·선 두께·서체·색 같은 시각 디자인 상세와 LaTeX 레시피는 [floats.md](floats.md)에 모아 두었다. 여기서는 이 섹션에 **무엇을** 넣는지를 다룬다.

### 5.1 수식 개수와 번호 규칙

| ID | display 수식 | 번호 붙은 식 | 참조 방식 |
|---|---|---|---|
| ICSE25 | ~20 | 3 — Freq′ (1), Eval(seed) (2), Eval(w) (3) | "using the equations (1) and (2)", "(the equation (3))" |
| ICSE26 | ~16 | 2 — Score (1), 예제 집합 C (2) | "the Score function in Equation (1)", "from Equation (2)" |
| ASE26 | ~15 | 0 | — |
| FSE26 | ~16 | 5 — 기호 시퀀스 집합 (1)–(5) | "the sequences in (1) and (2)" |

- **번호는 뒤에서 다시 참조하는 식에만 붙인다.** 다시 쓰는 점수 함수(ICSE25, ICSE26)나 예제(ICSE26 (2), FSE26 (1)–(5))가 대상이다.
- 참조 표기는 논문마다 다르다 ("the equation (3)" / "Equation (1)" / "(1)"). 한 논문 안에서는 일관된다.
- display는 단락 안에 끼워 넣는다. 콜론으로 열고, 뒤에 "where ..." 절이나 "Intuitively, ..." 문장으로 닫는다.

### 5.2 수식 관용구

| 관용구 | 쓰임 | 예 |
|---|---|---|
| **데이터 레코드 = 튜플** | 누적 데이터 원소를 n-튜플로 정의하고, 원소 의미를 문장으로 하나씩 설명 | (inp, B, bug, seed, w, p) ∈ D′ — "each element d in D′ consists of a 6-tuple: an input inp, a set B of branches that inp covers, a boolean value bug ..." / (p, v_d, V) ∈ P / (Arg, OB, CovOB) ∈ ArgD / (tree, L) |
| **와일드카드 `_`** | 튜플 패턴에서 안 쓰는 원소 생략 | π1(G) = \|B\|, where (_, B, _, _, _, _) ∈ G / {inp \| (inp, _, _, _, _, _) ∈ D} |
| **set-builder 함수** | 개수 세기, 필터 | Freq(b, D) = \|{inp \| (b ∈ B) ∧ (inp, B, _, _, _, _) ∈ D}\| / Frequency(b, TotalB) = \|{B \| (b ∈ B) ∧ (B ∈ TotalB)}\| |
| **역빈도 합 점수** | 희귀한 대상을 많이 덮을수록 높은 점수 (연구실 공통 관용구) | Score(B, TotalB) = Σ_{b∈B} 1 / Frequency(b, TotalB) (ICSE26 (1)), π2, Eval (ICSE25) |
| **타입 선언** | feature를 함수로 정의 | π_i : 𝔾 → ℝ, "where 𝔾 represents the set of all possible groups" / feat : 𝕆 → ℝ |
| **feature 벡터·내적** | 점수 = feature × 가중치 | π(G) = ⟨π1(G), ..., π5(G)⟩, Score(G, w) = π(G) · w |
| **argmax 선택** | 최고 점수 대상 고르기 | G_top = argmax_{G∈AllG} Score(G, w) / argmax_{t∈T_o} \|B ∩ UnionOB\| |
| **정규화 확률** | 점수 비례 샘플링 | 𝒫_p^i = Eval(p_i, PB) / Σ_{1≤i≤4} Eval(p_i, PB) / 𝒫(C_i) = mean(...) / Σ mean(...) |
| **조건 분기 (cases)** | 패널티 | s′ = s if s ≥ bs_p; 0 otherwise |
| **비율 feature** | 0–1 정규화 | feat1(Arg) = \|OB \ ⋃_{B∈CovOB} B\| / \|OB\| |
| **멀티셋 {{ }}** | 중복 허용 집합. 처음 쓸 때 설명 | "where the {{}} indicates a multiset that allows duplicated elements" |
| **분포** | 학습되는 확률 분포 | 𝒫_w, 𝒫_p (calligraphic), 𝒰[−1, 1]^5, truncated normal μ(TopW^i), σ(TopW^i) |
| **범위 정의** | 샘플링 공간 | V = {v_d × r}, (0.5 ≤ r ≤ 1.5) ∧ (r ≠ 1) / SP_p = 0.5 × v_rand ≤ v′ ≤ 1.5 × v_rand |
| **수치 계산 display** | 공식에 예제 값을 넣어 계산 | 𝒫(C_1) = ... = 27/34 / v′_mem = (2GB × 28 + 3GB × 26) / (28 + 26) ≈ 2.48GB |

### 5.3 기호 명명 (§2 규칙의 확장)

| 대상 | 규칙 | 예 |
|---|---|---|
| 누적·파생 집합 | 의미를 줄인 **CamelCase 이탤릭** | BaseD, ParamS, SelectP, ValueS, ArgD, CovOB, UnionOB, AllArgs, NewG, ReG, UG, CL, PrevL, NewL, TotalG |
| 짧은 보조 집합 | 대문자 약어 | SD, TB, WB, PB, SB |
| 역할 구분 | 아래첨자 단어 | G_top, S_good / S_bad, Arg_new, rs_prev / rs_new, v_rand, v_d, bs_p, B_seed |
| 상·하위 그룹 | CamelCase 접두 | TopW / BotW |
| 하이퍼파라미터 | **η + 아래첨자 이름** | η_time, η_Learn, η_r, η_clust, η_num |
| 분포 | calligraphic | 𝒫_w, 𝒫_p, 𝒰 |
| 함수·절차 | §2와 같음: 알고리즘·외부 오라클은 small caps(Score, Eval, Sample, Execute, Run), 단계·보조 함수는 sans-serif(Gather, Group, Rank, Select, Cluster, Learn, Construct, Guide, Update, Freq) | |
| 수식 안의 일반어 | 이탤릭 단어 그대로 | inp, tree, bug, seed, cmd, var, Val, Traces |

- **단계 이름 = 알고리즘이 호출하는 함수 이름**이다: Gather / Select / Learn, Extract / Construct / Guide / Update, Collecting → Generate·Execute, Grouping, Selecting → Select, Capturing → Capture.

### 5.4 수식 도입·마무리 문형

- **도입:** "defined as:" / "as follows:" / "calculated as follows:" / "is computed as:" / "expressed as:" / "as:" / "**Formally,** the i-th subset G_i is defined as:" / "**To formally define** the Score function, we introduce the Frequency function as:" / "can be formally defined as:"
- **뒤따르는 설명:** "where B_i denotes the set of covered branches of i-th element in D." → "**This function counts / This approach is based on the intuition that / Intuitively, ...**"
- **목록형 정의** (feature 정의, 2/4):
  - "1) **coverage** (π1): Calculates the number of branches covered by inputs in a group G as: [display]" (ICSE25)
  - "(1) **uncovered OB** (feat1): This feature computes the ratio of ..., defined as: [display] Intuitively, this feature estimates ..." (ASE26)
  - 형식: 번호 → **굵은 이름** → (기호) → 한 문장 설명 → display → (직관)
- **정의표**를 함께 둔다 (ICSE25): "TABLE II: Five features for group selection" / "TABLE III: Four policies for seed selection" — `Feature | Description` 2열 표

### 5.5 메인 알고리즘 표기

| 요소 | 규칙 | 예 |
|---|---|---|
| 캡션 | **도구명**(small caps) 또는 "Our ... Strategy" | "Algorithm 1 ParaSuit", "Algorithm 2 Orbis", "Algorithm 2 RSFuzz", "Algorithm 3 Our Seeding Strategy for Symbolic Execution" |
| Input / Output | §2 Algorithm 1과 같은 형식. 입력은 최소(프로그램, 예산[, 문법]) | Input: Program (pgm), budget (time). Output: A total set of covered branches (UnionB) |
| 초기화 | 튜플 동시 대입 + 하이퍼파라미터 주석 | ⟨D, BaseD, TotalB, time_s⟩ ← ⟨∅, ∅, ∅, η_time⟩ ▷ η_time = 120 |
| **단계 블록 주석** | `/* Step k. <Stage> stage */`, 블록 사이 빈 번호 줄 | /* Data Gathering */, /* Step 1. Extraction stage */, /* Step 2: Construct Stage */, /* Step 3: Selecting */ |
| 단계 = 함수 호출 1줄 | 단계마다 같은 이름의 함수를 호출하고, 그 함수를 하위절에서 설명 | D′ ← Gather(I) / SelectP ← Select(ParamS, BaseS) / Arg_new ← Construct(ArgD) / RS = Capture(NewG, ReG, RS) |
| §2 Algorithm 1 호출 | 루프 안에서 일반 알고리즘을 서브루틴으로 | I ← SymbolicExecutor(pgm, time_s, seed) / B ← Execute(pgm, time_s, PV) / B, T ← Execute(pgm, time_s, Arg_new, S_P) |
| ▷ 주석 | 하이퍼파라미터 기본값, 원소 형태, 부분집합 관계, 동작 설명 | ▷ (inp, B, bug, seed, w, p) ∈ D′ / ▷ G_i ⊆ D / ▷ NewG, ReG ⊆ TotalG / ▷ Check if L is newly covered. |
| return | 반환값 정의를 주석으로 | return TotalI ▷ TotalI = {inp \| (inp, _, _, _, _, _) ∈ D} / return UnionB ▷ UnionB = ⋃_{B∈TotalB} B |
| 길이 | 17–28줄 | |
| 보조 알고리즘 | 복잡한 단계 하나만 별도 알고리즘 | ICSE26 Algorithm 2 Value Sampling Stage (procedure Sample), ASE26 Seeding procedure(캡션 없는 줄번호 목록) |
| 배치 | 3.2 근처 페이지 상단 float | |

### 5.6 그림·표·코드

- **Overview 그림 (4/4).**
  - 캡션: "Fig. 1: Overview of TopSeed" / "Figure 2: Overview of ParaSuit." / "Figure 2: The overview of Orbis." / "Fig. 1. Overview of RSFuzz"
  - 구성: 도구 상자 안에 단계 상자(ICSE25는 ①②③ 번호), 그 안에 전략 하위 상자(Exploration/Exploitation, Score/Select, Explore/Exploit). 기존 도구 상자(Symbolic Executor, Grammar-based Fuzzer)와 **오가는 화살표에 데이터 이름**(Inputs, Seed, parameter values, covered branch set)을 붙인다. 입력(Program, Grammar)은 왼쪽, 출력(Total Inputs, total coverage, Total recurrent sequences)은 오른쪽이다.
  - 번호: Intro·§2에 그림이 있으면 그다음 번호(Figure 2)다. overview가 첫 그림이면 Figure 1이다.
- **예제 그림** (FSE26 Figure 2): 유도 트리 (a)(b)를 나란히 놓고, 본문에서 "Figure 2-(a)"로 참조한다.
- **정의표** (ICSE25 Table II, III): 결과가 아니라 feature·policy **정의**를 담는다.
- **코드형 display**: 실제 도구 출력(`$ ./klee --help`), 실제 소스 코드(줄 번호 + 문자열 강조), 문법·기호 시퀀스(타자체)

---

## 6. 섹션 간 연결

| §3 요소 | 대응 위치 | 관계 |
|---|---|---|
| 단계 이름 | Abstract M6, Intro I6, Contributions bullet 2, Conclusion | 같은 단어·같은 순서 |
| 단계 하나하나 | §4 ablation | 단계마다 제거형·대체형 변형이 하나 이상 있다. ICSE25 TopSeed−(Group), −(Learn) / ICSE26 RandP·AllP·SymP(Selection), Bayesian·Genetic·CMA-ES·RandV·SymV(Sampling) / ASE26 Orbis-Extract, RandConst·FuzzConst·CitConst, RandGuide, CallAll / FSE26 without Select, without Capture, NewG only |
| 기각한 대안 | §4 ablation 대체형 | §3에서 "we also considered ..."로 언급한 대안이 §4에서 대체 변형으로 다시 나온다 (FSE26 Capture의 단순 방법 = "RSFuzz without the Capture step") |
| §2 훅 인자 | §3 메인 알고리즘 호출, FSE26 §3.3 | §2에서 미뤄 둔 인자를 §3에서 채운다 |
| §2 예제 | §3 예제 | 같은 예제를 이어서 쓴다 (ASE26 ls -l, FSE26 𝔾_J와 "[]", ICSE26 max-memory) |
| 하이퍼파라미터 η | §4 Hyperparameter RQ, Threats to Validity | "set by trial and error" → ICSE25 §IV-E 민감도 분석, ICSE25·ICSE26 Threats (1)·(2) |
| "Empirically, ..." 수치 | §4.4 | Approach에 미리 쓴 수치가 §4.4 결과와 같아야 한다 (ASE26 9.6%, 21.5%, 16.8%) |
| 한계 인정 | §4 Threats | "We acknowledge ... as discussed in Section 4.8" (ASE26 hidden options 0.9% ↔ Threats (1)의 0.7개/프로그램 — 표현 단위가 다르다) |
| 메인 알고리즘 출력 | §2.3 Goal | ICSE26: 반환 UnionB = ⋃ B가 §2 목표식 ⋃ Execute(...)와 같다 |

---

## 7. 템플릿

```text
## 3 Our Approach
(opt.) In this section, we introduce <Tool>, designed to <...>. Initially, we outline the overall process of <Tool>.
       We then provide a detailed description of <...>, encapsulated in Algorithm N, which consists of three stages: <A>, <B>, and <C>.

### 3.1 Overview
Figure N illustrates how <Tool> <does ...> while interacting with <existing tool>. <Tool> operates in three stages: <A>, <B>, and <C>.
Initially, in the <A> stage, <Tool> <one-time step>. Once the <A> stage is complete, <Tool> iteratively performs the remaining
two stages until the total budget expires. In the <B> stage, .... Intuitively, .... In the <C> stage, ....
This process repeats until the budget is exhausted. Finally, <Tool> returns ....
(opt.) The key novelty of <Tool> lies in addressing two challenges in the <B> and <C> stages. A straightforward approach—...—was
       found to be ineffective, as demonstrated in Section 4.4.

### 3.2 <Tool>
Algorithm N details how <Tool> <...>. <Tool> accepts only two inputs: <noun> (pgm) and <noun> (time), and returns <...>.
At line 1, it initializes .... It also sets a small time budget (time_s) to a hyper-parameter value (η_time).
Since <Tool> aims to <...> without prior knowledge, it inevitably needs to <...>. In our experiments, η_time was set to 120 seconds by trial and error.

<Stage A>. The goal of the <A> stage is to <...> (lines x–y). To achieve this, Algorithm N <...> (line z).
Formally, each element of D is defined as a tuple (a, b, c), where a is ..., b is ..., and c is ....
For example, consider <toy input from §2>. ....

### 3.3 <Stage B>
The goal of the <B> stage is to <...> (lines x–y). Intuitively, we define <promising X> as those that (1) ..., (2) ..., and (3) ....
Specifically, at line x, .... To formally define the Score function, we introduce the Freq function as:
    Freq(b, D) = |{ ... | ... }|
This function counts .... For instance, consider D = {...}. In this set, ....
Leveraging the Freq function, we define the Score function as:
    Score(B, D) = Σ_{b∈B} 1 / Freq(b, D)                                   (1)
Intuitively, this function assigns a higher score when ....
We selected <X> because it provides a practical balance between <...> and <...>.
We also considered <alternative> [..]. However, we observed that <...>, as demonstrated in Section 4.4.
Now, we proceed to the next stage: <...>.

### 3.4 <Stage C>
...
In this manner, without prior knowledge, <Tool> <A>s, <B>s, and <C>s based on the accumulated data D.
```

---

## 8. 작성 체크리스트

- [ ] 3.1 Overview(그림) → 3.2 [Tool](메인 알고리즘) → 단계별 하위절 순이고 ~2,500 words인가
- [ ] 단계 이름이 overview 그림, 알고리즘 주석, 호출 함수명, 하위절 제목, Abstract·Intro·Conclusion에서 모두 같은가
- [ ] overview 그림이 기존 도구와의 상호작용을 보여 주고, 화살표에 주고받는 데이터 이름이 붙어 있는가
- [ ] 메인 알고리즘이 §2 Algorithm 1을 서브루틴으로 호출하고, §2에서 미뤄 둔 훅 인자를 채우는가
- [ ] 알고리즘에 `/* Step k. <Stage> */` 블록 주석과 ▷ 하이퍼파라미터 기본값이 있는가
- [ ] 단계마다 첫 문장이 "The goal of the X stage is to ... (lines a–b)"인가
- [ ] 모든 display 수식 뒤에 "where ... denotes ..." 또는 "Intuitively, ..."가 있는가
- [ ] 번호는 뒤에서 다시 참조하는 식에만 붙였는가
- [ ] 데이터 레코드는 튜플로 정의하고 원소를 하나씩 설명했는가 (안 쓰는 원소는 `_`)
- [ ] 단계마다 구체 예제(가능하면 §2 예제의 연장)가 있는가
- [ ] 설계 선택에 이유("because ... practical balance ...")나 기각한 대안이 있는가
- [ ] 하이퍼파라미터를 η로 이름 짓고 값과 "by trial and error"를 밝혔는가
- [ ] 설계 정당화를 §4.4 ablation forward ref로 뒷받침했고, 미리 쓴 "Empirically" 수치가 §4와 일치하는가
- [ ] 섹션 끝이 "In this manner, without prior knowledge, ..."로 단계 이름을 다시 나열하며 마무리되는가

---

## 부록 A. 원문 발췌 (역할 태그)

수식과 기호는 PDF 원문 표기를 따라 옮겼다 (아래첨자는 `_`, 합은 Σ로 표시).

**ICSE25 — TopSeed**

> **[리드 A-0]** In this section, we introduce a novel approach named TopSeed, designed to automatically learn seed selection strategies based on data accumulated from interactions with a symbolic executor. Initially, we outline the overall process of TopSeed. We then provide a detailed description of our data-driven seed selection strategies, encapsulated in Algorithm 3, which consist of three stages: Gather, Select, and Learn.
>
> **[A. Overview · A-1]** Figure 1 illustrates how TopSeed automatically selects promising seeds while interacting with a symbolic executor. Initially, TopSeed generates inputs by performing symbolic execution on a given program without any seeds. It then iteratively selects the most suitable seed from these inputs using the exploration and exploitation strategies and conducts further symbolic execution with the chosen seed. This iterative process enables TopSeed to effectively utilize various seeds, even without prior knowledge. Hence, our approach divides the total time budget into smaller intervals, repeatedly performing symbolic execution within these periods.
>
> TopSeed identifies the optimal seed through three phases: Gather, Select, and Learn. In the Gather phase, it constructs useful data, such as branch coverage, from inputs generated during symbolic execution. This data is then utilized in the subsequent phases. The Select stage involves choosing the most promising seed based on two strategies: Explore and Exploit. The Explore strategy selects new seeds from the generated candidates, whereas the Exploit strategy reuses previously selected seeds. In the final Learn stage, TopSeed refines these strategies by updating the corresponding probability distributions.
>
> **[D. Seed Selecting · F + I]** More specifically, we partition the set D into subsets, {G_1, G_2, ···, G_n}, where each subset contains inputs that cover the same set of branches (line 16). Formally, the i-th subset G_i is defined as:
>
> &nbsp;&nbsp;&nbsp;&nbsp;G_i = {(inp, B, bug, seed, w, p) ∈ D | (B_i = B)}
>
> where B_i denotes the set of covered branches of i-th element in D. Grouping inputs by the set of covered branches simplifies the seed selection process by reducing the challenge from selecting a single seed from all inputs to choosing one group from all groups. This approach is based on the intuition that inputs with identical branch coverage may possess similar potential as seeds.
>
> **[E. Distribution Learning · X]** In this manner, without prior knowledge, TopSeed intelligently selects promising seeds based on 𝒫_w and 𝒫_p, which are continuously updated based on the accumulated data D during symbolic execution.

**ICSE26 — ParaSuit**

> **[3.2 ParaSuit · A-2]** Algorithm 1 offers a detailed description of how ParaSuit iteratively selects promising parameters and samples their values tailored for the target program, requiring no user effort. ParaSuit accepts only two inputs: the program (pgm) to be tested and the total time budget (time). Once time is exhausted, Algorithm 1 outputs the total set of covered branches (UnionB). At line 1, it initializes three sets—D, BaseD and TotalB—as empty sets. It also sets a small time budget (time_s) to a hyper-parameter value (η_time). Since ParaSuit aims to find suitable parameters and their values for the target program without prior knowledge, it inevitably needs to run the symbolic execution tool multiple times, each with newly defined parameter values and a small time budget. This iterative process enables ParaSuit to explore diverse parameter settings based on accumulated data. In our experiments, the initial small time budget (η_time) was set to 120 seconds by trial and error.
>
> **[3.3 Parameter Selection · G + I + L]** The goal of the Selection stage is to choose from all available parameters promising ones that are essential for effectively testing the target program (lines 15–17). Intuitively, we define promising parameters as those that (1) reach many branches, (2) cover infrequently reached branches, and (3) produce synergy when combined with other parameters. To achieve this, Algorithm 1 calculates two distinct scores from two sets, BaseD and D, using a customized scoring function (lines 15–16). BaseD quantifies the effect of tuning a parameter while keeping all others at their default values. In contrast, D measures its performance when tuned simultaneously with others during the iterative process. After calculating scores using the two sets, the Select function determines which parameters to tune based on their scores (line 17).
>
> **[3.3 · F + E + I]** Specifically, at lines 15–16, the Score function evaluates each parameter p based on two coverage-related aspects: (1) the number of branches covered when adjusting p, and (2) its ability to reach branches that are rarely covered by other parameters. To formally define the Score function, we introduce the Frequency function as:
>
> &nbsp;&nbsp;&nbsp;&nbsp;Frequency(b, TotalB) = |{B | (b ∈ B) ∧ (B ∈ TotalB)}|
>
> This function counts the number of times that a branch b appears in the accumulated set TotalB of covered branches. Recall that Algorithm 1 adds a singleton set containing B to TotalB (line 11) to track the frequency of each covered branch. For instance, consider the set TotalB containing two sets of covered branches:
>
> &nbsp;&nbsp;&nbsp;&nbsp;TotalB = {{b_1, b_2, b_3}, {b_1, b_4}}
>
> In this set, the frequency of b_1—Frequency(b_1, TotalB)—is 2 while the frequency of b_2 is 1. Leveraging the Frequency function, we define the Score function as:
>
> &nbsp;&nbsp;&nbsp;&nbsp;Score(B, TotalB) = Σ_{b∈B} 1 / Frequency(b, TotalB) &nbsp;&nbsp;&nbsp;&nbsp;(1)
>
> Intuitively, this function assigns a higher score when the set B is larger and each branch b in B has a lower occurrence frequency.
>
> **[3.3 · I + X]** The intuition behind this penalty is that if p performs worse when tuned simultaneously with others compared to tuning it alone, then p likely does not contribute positively in combination. This penalty guides the process away from selecting such parameters. ... Now, we proceed to the second iterative stage: assigning an appropriate value for each chosen parameter.
>
> **[3.4 · X (섹션 끝)]** In this way, ParaSuit selects appropriate parameters and assigns their plausible values tailored to the target program based on the accumulated data while interacting with the symbolic execution tool. Ultimately, ParaSuit enables more effective testing of each program without any user-driven configuration.

**ASE26 — Orbis**

> **[Construct · F + I (목록형)]** (1) **uncovered OB** (feat_1): This feature computes the ratio of option-related branches that are not yet covered within the total set OB corresponding to Arg, defined as:
>
> &nbsp;&nbsp;&nbsp;&nbsp;feat_1(Arg) = |OB \ ⋃_{B∈CovOB} B| / |OB|, where (Arg, OB, CovOB) ∈ ArgD
>
> Intuitively, this feature estimates the potential of Arg based on how many of its associated branches remain uncovered.
>
> **[Extract · R (한계 인정)]** We acknowledge that some hidden options may not appear in the help script. However, as discussed in Section 4.8, these constitute only 0.9% of all options across our benchmark suite, and even if extracted, their impact on improving symbolic execution performance is negligible. Therefore, our approach adopts the cost-effective strategy of extracting options solely from the help script.
>
> **[Guide · A]** Empirically, this procedure enables Orbis to derive effective initial states from the delicately selected seeds within only 9.6% of the total time budget on average, resulting in a 21.5% branch coverage improvement, as shown in Section 4.4.

**FSE26 — RSFuzz**

> **[3.1 Overview · 신규성 위치]** The key novelty of RSFuzz lies in addressing two significant challenges in the "selecting" and "capturing" steps. The first challenge is deciding which groups to target for capturing recurrent sequences. An extreme approach—capturing recurrent sequences from every group—has been shown to be inefficient, as demonstrated in Section 4.4. The second challenge involves determining how to extract recurrent sequences from the selected groups. A straightforward approach—identifying sequences of production rules commonly used to generate all inputs in each group—was also found to be cost-ineffective, as shown in Section 4.4.
>
> **[3.2.2 Grouping · R (선택 이유)]** We selected line coverage as the grouping criterion because it provides a practical balance between overly fine-grained metrics, such as path coverage, and coarser metrics, such as method coverage, thereby enabling the formation of meaningful groups for recurrent-sequence extraction.
>
> **[3.2.3 Selecting · Example]** *Example 3.1.* Assume that the set UG consists of four uncaptured groups, {UG_1, UG_2, UG_3, UG_4}, with the following sizes:
>
> &nbsp;&nbsp;&nbsp;&nbsp;|UG_1| = 100, |UG_2| = 90, |UG_3| = 20, |UG_4| = 10
>
> In this example, we choose the top two groups, UG_1 and UG_2, as NewG, since the largest gap exists between UG_2 and the next group.
>
> **[3.2.4 Capturing · R (기각한 대안)]** In this work, we also considered alternative clustering algorithms, such as DBSCAN [12] and OPTICS [1]. However, we observed that these methods were generally less effective than MeanShift, since their noise filtering mechanisms often discarded meaningful symbol sequences as noise.
