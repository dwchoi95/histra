# Abstract — guidelines 4편 분석

[skeleton.md](skeleton.md)의 하위 문서. Abstract를 문장(move) 단위로 분석한다.
Title·Keywords는 [skeleton.md](skeleton.md) §2에서 다룬다. 원문 전체는 move 태그를 붙여 부록 A에 실었다.

---

## 0. 핵심 규칙

1. Abstract는 **1단락, 7–10문장, 160–240 words**이다. 첫 문장은 항상 **"We present X, a ... that ..."**, 마지막 문장은 항상 **실험 결과**다.
2. 분량은 **문제 제기 ~40%**, 해법 ~27%, 결과 ~23%, 도입 ~9%다. 해법보다 문제 설명에 더 많은 단어를 쓴다.
3. Gap 문장에서 **논문이 새로 만든 용어**를 소개하고 바로 정의한다. 예: "seeding", self-configuring, option-related branch (OB), "coverage-equivalent".
4. 해법은 **"iteratively V1, V2, and V3 ... based on data accumulated during ..."**처럼 동사 3개를 나열하는 문장으로 쓴다 (4/4).
5. 인용, 경쟁 도구 이름, URL, RQ, 한계, 향후 연구는 넣지 않는다. hedging(may/might)도 없다.

---

## 1. 분량

| ID | 문장 수 | 단어 수 | 평균 문장 길이 | 최장 문장 |
|---|---|---|---|---|
| ICSE25 | 7 | 163 | 23.3 | 33 (해법) |
| ICSE26 | 10 | 241 | 24.1 | 54 (Gap-2) |
| ASE26 | 7 | 193 | 27.6 | 42 (해법) |
| FSE26 | 8 | 230 | 28.8 | 46 (결과) |
| **평균** | **8** | **~207** | **~26** | |

---

## 2. 구조

### 2.1 Move 정의

| Move | 역할 | 출현 |
|---|---|---|
| **M1 Present** | 도구 소개 + 한 줄 정의 | 4/4 (항상 S1) |
| **M2 Context** | 분야 현황·발전 | 4/4 (ASE26은 M3과 한 문장) |
| **M3 Gap** | 기존 기법의 한계 + 신조어 정의 | 4/4 |
| M3′ Evidence | 한계를 수치로 보임 | 1/4 (ASE26) |
| **M4 Goal / Idea** | 논문 목표 또는 핵심 아이디어 | 4/4 (형태는 다양) |
| M5 Challenge | 해결이 어려운 이유 (규모) | 2/4 (ICSE25, FSE26) |
| **M6 Solution** | 알고리즘 단계 (동사 3개 나열) | 4/4 |
| M7 Setup | 구현·평가 대상 | 2/4는 독립 문장, 2/4는 M8에 합침 |
| **M8 Results** | 결과 (주로 수치) | 4/4 (항상 마지막) |

### 2.2 논문별 배치

| ID | S1 | S2 | S3 | S4 | S5 | S6 | S7 | S8 | S9 | S10 |
|---|---|---|---|---|---|---|---|---|---|---|
| ICSE25 | M1 | M2 | M3 | M4 Goal | M5 | M6 | M7+M8 | | | |
| ICSE26 | M1 | M2 | M3 | M3 | M4 Goal | M6 (초기 단계) | M6 (반복 단계) | M7 | M8 | M8 (하이라이트) |
| ASE26 | M1 | M2+M3 | M3′ | M4 Idea | M6 (초기 단계) | M6 (반복 단계) | M7+M8 | | | |
| FSE26 | M1 | M2 | M3 | M4 Idea | M5 | M6 | M7 | M8 | | |

**정형 순서:** M1 → M2 → M3 → (M3′) → M4 → (M5) → M6 → (M7) → M8. 순서가 바뀐 경우는 없다.

### 2.3 Move 그룹별 비중

| ID | 도입 (M1) | 문제 (M2–M5, 단 FSE26의 Idea 문장 제외) | 해법 (M6 + Idea 문장) | 결과 (M7–M8) |
|---|---|---|---|---|
| ICSE25 | 9% | 52% | 20% | 19% |
| ICSE26 | 9% | 47% | 24% | 20% |
| ASE26 | 9% | 31% | 39% | 21% |
| FSE26 | 8% | 36% | 24% | 31% |
| **평균** | **~9%** | **~42%** | **~27%** | **~23%** |

---

## 3. Move별 분석

### M1 Present — "We present X, a [수식어] [approach|technique] that [동사] ..."

| ID | 동격 명사구 | 동사구 |
|---|---|---|
| ICSE25 | a **new approach** | that automatically selects optimal seeds to enhance symbolic execution |
| ICSE26 | a **self-configuring technique** | that enhances symbolic execution by autonomously adjusting its parameters tailored to each program under test |
| ASE26 | a **complementary approach** | that guides symbolic execution techniques toward maximizing option-related branch (OB) coverage |
| FSE26 | a **new technique** | to enhance grammar-based fuzzing by reducing the generation of coverage-equivalent inputs during testing |

- 구조: `X` + 동격 `a [new/novel/complementary/신조어] approach/technique` + `that/to [동사] [분야]` + `by/toward [수단/목표]`.
- 동사는 분야를 목적어로 받는 개선 동사다 (enhance / guide). 무엇을 하는지(수단)와 왜 하는지(목표)를 한 문장에 담는다.
- 약어는 이 문장에서 처음 정의한다: "option-related branch (OB)".

### M2 Context — 분야가 발전해 왔음을 인정

- ICSE25: "**Recently**, the performance of symbolic execution has **significantly improved** through various state-of-the-art techniques, including search strategies and state-pruning heuristics."
- ICSE26: "**Modern** symbolic execution tools are typically equipped with various external parameters to effectively test real-world programs."
- ASE26: "**Although** state-of-the-art symbolic execution techniques have **substantially improved** code coverage and bug detection, ..." (뒤에 바로 M3)
- FSE26: "Grammar-based fuzzers apply production rules from a given grammar (e.g., forming a derivation tree) to generate well-structured inputs for the target program." (동작 원리 설명형)

패턴: 현재완료 *has (significantly/substantially) improved*로 SOTA의 진전을 인정한 뒤, 다음 문장을 *However*로 뒤집는다.
SOTA를 범주명으로 나열할 수 있으나(search strategies, state-pruning heuristics) **인용은 하지 않는다**.

### M3 Gap — 한계 + 신조어 정의

| ID | 전환어 | 신조어 | 정의 방식 |
|---|---|---|---|
| ICSE25 | However, | "seeding" (따옴표) | `, which efficiently initializes program states for exploration` |
| ICSE26 | However, / Despite recent efforts ..., | self-configuring | 부정형 정의: `are not self-configuring; they cannot ..., and ...` |
| ASE26 | Although ..., | option-related branch (OB) | M1에서 약어 정의 → `which are accessible only through specific options` |
| FSE26 | However, a key limitation is that | "coverage-equivalent" (따옴표) | 대시 삽입: `—those that revisit already explored program paths—` |

- **결과절(consequence)로 마무리**하는 경우가 많다: "thereby restricting their ability to ...", "makes these tools harder to use and limits their potential benefits".
- 기존 연구를 "these techniques", "existing techniques/fuzzers"처럼 **익명 집합**으로 지칭한다.
- ICSE26은 Gap을 두 문장으로 나눈다. 첫 문장은 사용자 부담, 둘째는 기존 기법의 한계이며, 둘째가 54 words로 가장 길다.

### M3′ Evidence — 한계 수치 (ASE26만)

> "To quantify this limitation, we evaluate how effectively current techniques cover option-related branches and find that they reach **only 8.0%** of the targeted OBs, ..."

이 move는 선택이다. 넣는다면 **"To quantify this limitation, we evaluate ... and find that ... only N%"** 형태로 쓴다.

### M4 Goal / Idea — 두 가지 변형

- **Goal형** (ICSE25, ICSE26): 문제를 목표로 다시 진술한다.
  - "**This paper aims to** select valuable seeds ... without the need for a predefined seed corpus, **thereby** maximizing the technique's effectiveness."
  - "**The goal of this paper is to** automatically configure symbolic execution parameters **from scratch** for each program."
- **Idea형** (ASE26, FSE26): 해법을 한 줄로 요약한다. 주어는 도구명이다.
  - "**Orbis overcomes this challenge by** systematically guiding symbolic execution to improve OB coverage."
  - "**To address this issue, RSFuzz** automatically identifies recurrent sequences ... and prevents their reuse during fuzzing."

목표 문장에는 사전 지식이 필요 없다는 한정어가 자주 붙는다: *from scratch*, *without the need for ...*.

### M5 Challenge — 규모 때문에 어렵다

- ICSE25: "**One major challenge is** the vast number of candidates, **making it difficult to** identify promising seeds."
- FSE26: "**A key challenge lies in** the large number of coverage-equivalent input groups, each with many inputs and corresponding derivation trees, **making it difficult to** identify underlying recurrent sequences."

고정 틀: **`One major/A key challenge is/lies in the (vast/large) number of X, making it difficult to Y.`**
두 편 모두 "개수가 많다"는 **규모**를 도전과제로 든다. Abstract에서는 수치를 생략한다 (Intro에서 제시).

### M6 Solution — 동사 3개를 나열하는 반복 알고리즘

| ID | 도입부 | 동사 3개 | 꼬리 |
|---|---|---|---|
| ICSE25 | To address this, we introduce a **customized** online learning algorithm that **iteratively** | groups ..., ranks ..., and selects ... | based on **data accumulated during** symbolic execution |
| ICSE26 | It then applies a **specialized** algorithm to **iteratively** | select ..., construct ..., and update ... | based on **data accumulated from** symbolic execution runs ... |
| ASE26 | It then **iteratively** | constructs ..., directs ..., and refines ... | **using data accumulated during** symbolic execution |
| FSE26 | RSFuzz tackles this challenge with a **customized** algorithm that **iteratively** | groups ..., selects ..., and extracts ... | **based on accumulated data** while running any grammar-based fuzzer |

- 4편 모두 **customized/specialized + iteratively + 동사 3개 + accumulated data** 조합이다.
- 반복 전에 1회성 초기 단계가 있으면 문장을 둘로 나눈다 (ICSE26, ASE26):
  "To this end, X **begins by** automatically identifying ... / For a given program, X automatically identifies ..." → "**It then** iteratively ..."
- 여기서 쓴 동사 3개는 Intro·Overview·Conclusion의 단계 이름과 일치한다 (§6 참고).

### M7 Setup — 구현·평가 대상

- 독립 문장형: "**We implemented** ParaSuit on KLEE **and assessed it across** 12 open-source C programs." / "**We integrated** RSFuzz with existing random, probabilistic, and grammar-coverage based fuzzers **and evaluated it on** 12 real-world programs using JavaScript, JSON, CSV, and Markdown input formats."
- 결과에 합친 형: "Experimental results **on 17 open-source C programs** show that ..."
- 평가 대상은 **개수 + 종류**로 쓴다 (17 open-source C programs). baseline은 **개수 + 범주**로 쓴다 (four distinct cutting-edge techniques / random, probabilistic, and grammar-coverage based fuzzers).

### M8 Results — 마지막 문장

| ID | 형태 | 수치 |
|---|---|---|
| ICSE25 | "show that TopSeed **significantly enhances** four distinct cutting-edge techniques ... in terms of branch coverage and bug-finding abilities." | **없음** (정성) |
| ICSE26 | "**The results demonstrate that** ParaSuit **significantly outperforms** the state-of-the-art method ..., achieving an average of 26% higher branch coverage." + "**Remarkably**, ParaSuit identified 11 unique bugs, four of which were **exclusively** discovered by ParaSuit." | 26%, 11, 4 |
| ASE26 | "show that integrating Orbis with four independent state-of-the-art techniques **significantly increases** OB coverage to 323.0%, **boosts** total branch coverage by 112.1%, and **detects** five additional unique bugs on average compared to the standalone techniques." | 323.0%, 112.1%, 5 |
| FSE26 | "show that incorporating RSFuzz into the three fuzzers **detects** 121, 46, and 17 additional crashes ..., **increases** line coverage by 6.0%, 4.8%, and 3.0%, and **reduces** duplicate-coverage input generation by 23.3%, 28.7% and 14.9%, **respectively**, compared to their performance without RSFuzz." | baseline별 3×3 |

- 도입부는 **"Experimental results (on N ...) show that" / "The results demonstrate that"**로 고정된다.
- **significantly**는 4/4에서 쓴다. 결과 동사도 3개를 나열하는 경우가 많다 (increases / boosts / detects).
- 비교 기준은 **"compared to [도구 없는 버전]"**(complementary 도구) 또는 **"the state-of-the-art method"**다.
- 수치는 주 지표 %와 버그 개수를 함께 쓴다. 소수점은 한 자리다 (8.0%, 112.1%). ICSE26만 반올림해서 26%로 썼다 (본문은 25.8%).
- 결과 뒤에 의의나 함의를 덧붙이는 문장은 없다. **결과 문장으로 끝난다.**

---

## 4. 문체 특징

| 항목 | 관찰 |
|---|---|
| 주어 | 연구자 행위(present, introduce, implemented)는 **We**, 기법 동작(overcomes, tackles, begins by)은 **도구명**, 연결 문장은 **It then**을 주어로 쓴다 |
| 시제 | 기법 설명과 결과 보고(show, demonstrate)는 **현재형**, 수행한 실험 행위(implemented, evaluated, identified)는 **과거형**, 분야 발전은 **현재완료** |
| 전환어 | However (3/4), Although, Despite / To address this, To this end, tackles/overcomes this challenge / It then / thereby |
| 부사 | automatically (4/4, 편당 여러 번), iteratively (4/4), significantly (4/4), systematically, substantially, autonomously, stochastically, Remarkably |
| 병렬 구조 | 동사 3개를 나열하는 문장이 해법과 결과에 반복된다 |
| 신조어 | 따옴표("seeding", "coverage-equivalent") 또는 약어 정의(OB) 직후 정의절(which / — — / ; they cannot) |
| 단정 | hedging(may, might, could)은 0회다. 모든 주장을 단정형으로 쓴다 |
| **넣지 않는 것** | 인용, 경쟁 도구 이름(구현 기반 KLEE는 예외), URL, RQ, 한계/위협, 향후 연구, 결론적 함의 문장 |

---

## 5. 수식·알고리즘·플로트

해당 없음. Abstract에는 수식, 기호, 플로트가 없다. 약어는 M1에서 한 번 정의한다 (option-related branch (OB)).

---

## 6. 섹션 간 연결

Abstract의 각 move는 본문 어딘가에서 더 자세히 반복된다. 용어, 정의, 수치가 서로 맞아야 한다.

| Abstract move | 대응 위치 | 관계 |
|---|---|---|
| M1 동격 명사구 | Intro "In this paper, we present X, a ..." | 같은 정의를 다시 쓰고 수식어만 바꾼다. 예: a new approach → a novel seeding approach (ICSE25), a complementary approach → a new complementary approach (ASE26) |
| M3 신조어 | Title, Intro Gap 단락, §2.2 | Abstract에서는 한 절로 정의하고, Intro에서 "In this work, we (newly) define ..."로 다시 정의한 뒤, §2.2에서 예제와 함께 정식으로 정의한다 |
| M3′ 한계 수치 | Intro Gap 단락, §2.2 Table 1 | ASE26은 Abstract 8.0%, Intro·§2.2 7.9%로 값이 다르다. 따라 하지 말 것 |
| M4 Goal / Idea | Intro 제안 단락, §2.2–2.3 Goal | "The goal of this paper is ..." 문장이 §2의 Goal 단락에서 형식화된다 (ICSE26, FSE26) |
| M5 Challenge | Intro 도전과제 단락, §2.3 | Abstract는 "the vast number of ..."까지만 쓰고, 수치(tens of thousands, 19,729 groups)는 Intro와 §2에서 제시한다 |
| M6 동사 3개 | Intro 알고리즘 문장, §3.1 Overview 단계 이름, Conclusion | 같은 동사를 같은 순서로 쓴다. 예: TopSeed는 Abstract "groups, ranks, and selects" → Conclusion "grouping ..., ranking ..., and selecting ..." / ParaSuit는 "select, construct, update" → Conclusion "selects, constructs, updates" |
| M8 결과 수치 | Intro 결과 단락, §4 | 같은 수치를 쓴다. ICSE26은 Abstract 26%, Intro 25.8%로 반올림만 다르다 |

---

## 7. 템플릿

```text
[M1]  We present <Tool>, a <new|novel|complementary> <approach|technique> that <enhances|guides> <domain> <by <mechanism>|toward <goal>>.
[M2]  <Recently|Although> <domain/SOTA techniques> <have significantly improved> <...>,
[M3]  However, <existing techniques> <still/often fail to ...|produce "<coined term>">, <which|—those that> <definition>, thereby <negative consequence>.
[M3'] (opt.) To quantify this limitation, we evaluate <...> and find that they <reach only N%> <...>.
[M4]  This paper aims to <goal> <from scratch|without ...>.   |   <Tool> overcomes this challenge by <one-line idea>.
[M5]  (opt.) One major challenge is the vast number of <X>, making it difficult to <Y>.
[M6]  To address this, <we introduce|<Tool> applies> a customized algorithm that iteratively <V1> ..., <V2> ..., and <V3> ... based on data accumulated during <process>.
      (초기 단계가 있으면) For a given <input>, <Tool> first <...>. It then iteratively <V1>, <V2>, and <V3> ...
[M7]  (opt.) We implemented <Tool> on <platform> and evaluated it on <N> <subjects>.
[M8]  Experimental results on <N> <subjects> show that <Tool> significantly <V-a> <metric> by <x%>, <V-b> <...>, and <V-c> <...> compared to <baseline without Tool|SOTA>.
```

---

## 8. 작성 체크리스트

- [ ] S1이 "We present X, a ... that ..."인가
- [ ] Gap 문장에 신조어가 있고 그 자리에서 정의했는가
- [ ] 문제 제기(M2–M5)가 전체의 35–50%인가
- [ ] 해법 문장이 "iteratively V1, V2, and V3 ... accumulated data" 구조이고, 그 동사가 Intro/Overview의 단계 이름과 같은가
- [ ] 평가 대상을 개수+종류로, baseline을 개수+범주로 썼는가
- [ ] 마지막 문장이 수치를 포함한 결과 문장인가 (주 지표 % + 부 지표 개수)
- [ ] 인용·URL·한계·hedging이 없는가
- [ ] 신조어 정의, 단계 동사, 수치가 Intro·본문과 일치하는가 (§6)
- [ ] 7–10문장, 160–240 words인가

---

## 부록 A. 원문 (move 태그)

**ICSE25 — TopSeed**
> [M1] We present TopSeed, a new approach that automatically selects optimal seeds to enhance symbolic execution.
> [M2] Recently, the performance of symbolic execution has significantly improved through various state-of-the-art techniques, including search strategies and state-pruning heuristics.
> [M3] However, these techniques have typically demonstrated their effectiveness without considering "seeding", which efficiently initializes program states for exploration.
> [M4] This paper aims to select valuable seeds from candidate inputs generated during interactions with any symbolic execution technique, without the need for a predefined seed corpus, thereby maximizing the technique's effectiveness.
> [M5] One major challenge is the vast number of candidates, making it difficult to identify promising seeds.
> [M6] To address this, we introduce a customized online learning algorithm that iteratively groups candidate inputs, ranks each group, and selects a seed from the top-ranked group based on data accumulated during symbolic execution.
> [M7+M8] Experimental results on 17 open-source C programs show that TopSeed significantly enhances four distinct cutting-edge techniques, implemented on top of two symbolic executors, in terms of branch coverage and bug-finding abilities.

**ICSE26 — ParaSuit**
> [M1] We present ParaSuit, a self-configuring technique that enhances symbolic execution by autonomously adjusting its parameters tailored to each program under test.
> [M2] Modern symbolic execution tools are typically equipped with various external parameters to effectively test real-world programs.
> [M3] However, the need for users to fine-tune a multitude of parameters for optimal testing outcomes makes these tools harder to use and limits their potential benefits.
> [M3] Despite recent efforts to improve this tuning process, existing techniques are not self-configuring; they cannot dynamically identify which parameters to tune for each target program, and for each manually selected parameter, they sample a value from a fixed, user-defined set of candidate values that is specific to that parameter and remains unchanged across programs.
> [M4] The goal of this paper is to automatically configure symbolic execution parameters from scratch for each program.
> [M6] To this end, ParaSuit begins by automatically identifying all available parameters in the symbolic execution tool and evaluating each parameter's impact through interactions with the tool.
> [M6] It then applies a specialized algorithm to iteratively select promising parameters, construct sampling spaces for each, and update their sampling probabilities based on data accumulated from symbolic execution runs using sampled parameter values.
> [M7] We implemented ParaSuit on KLEE and assessed it across 12 open-source C programs.
> [M8] The results demonstrate that ParaSuit significantly outperforms the state-of-the-art method without self-configuring parameters, achieving an average of 26% higher branch coverage.
> [M8] Remarkably, ParaSuit identified 11 unique bugs, four of which were exclusively discovered by ParaSuit.

**ASE26 — Orbis**
> [M1] We present Orbis, a complementary approach that guides symbolic execution techniques toward maximizing option-related branch (OB) coverage.
> [M2+M3] Although state-of-the-art symbolic execution techniques have substantially improved code coverage and bug detection, existing techniques often fail to exercise core program functionalities, which are frequently exposed as program options.
> [M3′] To quantify this limitation, we evaluate how effectively current techniques cover option-related branches and find that they reach only 8.0% of the targeted OBs, which are accessible only through specific options.
> [M4] Orbis overcomes this challenge by systematically guiding symbolic execution to improve OB coverage.
> [M6] For a given program, Orbis automatically identifies all defined options and determines their associated branches by analyzing dynamic execution traces.
> [M6] It then iteratively constructs target option arguments by stochastically combining identified options according to their estimated potential, directs symbolic execution to explore states influenced by these arguments, and refines their potential while simultaneously reducing SMT-solver invocations using data accumulated during symbolic execution.
> [M7+M8] Experimental results on 15 open-source C programs show that integrating Orbis with four independent state-of-the-art techniques significantly increases OB coverage to 323.0%, boosts total branch coverage by 112.1%, and detects five additional unique bugs on average compared to the standalone techniques.

**FSE26 — RSFuzz**
> [M1] We present RSFuzz, a new technique to enhance grammar-based fuzzing by reducing the generation of coverage-equivalent inputs during testing.
> [M2] Grammar-based fuzzers apply production rules from a given grammar (e.g., forming a derivation tree) to generate well-structured inputs for the target program.
> [M3] However, a key limitation is that many existing fuzzers still produce a large number of "coverage-equivalent" inputs—those that revisit already explored program paths—thereby restricting their ability to uncover new bugs and improve coverage.
> [M4] To address this issue, RSFuzz automatically identifies recurrent sequences of production rules that lead to coverage-equivalent inputs and prevents their reuse during fuzzing.
> [M5] A key challenge lies in the large number of coverage-equivalent input groups, each with many inputs and corresponding derivation trees, making it difficult to identify underlying recurrent sequences.
> [M6] RSFuzz tackles this challenge with a customized algorithm that iteratively groups coverage-equivalent inputs, selects promising groups, and extracts recurrent sequences by abstracting derivation trees based on accumulated data while running any grammar-based fuzzer.
> [M7] We integrated RSFuzz with existing random, probabilistic, and grammar-coverage based fuzzers and evaluated it on 12 real-world programs using JavaScript, JSON, CSV, and Markdown input formats.
> [M8] Experimental results show that incorporating RSFuzz into the three fuzzers detects 121, 46, and 17 additional crashes with distinct stack traces, increases line coverage by 6.0%, 4.8%, and 3.0%, and reduces duplicate-coverage input generation by 23.3%, 28.7% and 14.9%, respectively, compared to their performance without RSFuzz.
