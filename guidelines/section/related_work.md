# Related Work — guidelines 4편 분석

[skeleton.md](skeleton.md)의 하위 문서. §5 Related Work를 주제 단락 단위로 분석한다.
Related Work는 짧고(~440 words) 4편 모두 주제 단락 3개뿐이라, 원문 전체(12단락)를 태그를 붙여 부록 A에 실었다.

---

## 0. 핵심 규칙

1. Related Work는 **Experiments 뒤**에 둔다. **~440 words, 주제 단락 3개**이고, 각 단락은 bold run-in 제목으로 시작한다 (FSE26만 5.1–5.3 하위절). 섹션 리드나 마무리 단락은 없다.
2. 주제는 세 축이다. **① 같은 목표**(같은 기술을 개선하는 기법들, 항상 첫째), **② 같은 대상·자원**(seed, 파라미터, 옵션 인자, 문법), **③ 같은 방법·틀 또는 인접 목표**(기계학습, SBST, directed testing, 문법 생성).
3. 단락은 **위치 선언 → (최초 주장) → 하위 범주·대표 도구 개관 → 대조 → 통합 가능성** 순이다. 첫 문장은 **"Our work shares a common goal with / belongs to / is rooted in / falls within / relates to / aligns with / is orthogonal to [인용 묶음]."**이다.
4. 대조는 결함 지적이 아니라 **목표·가정의 차이**로 쓴다. 가장 자주 쓰는 대조 축은 **"사전 지식·수동 설정이 필요한가 vs 자동(from scratch)인가"**다. 가장 가까운 SOTA는 **일대일로** 대조한다 ("The key difference is that ...").
5. **인용 밀도가 가장 높은 섹션**이다 (주제당 고유 문헌 4–19개). 수치·표·그림은 넣지 않는다.

---

## 1. 분량

| ID | 주제 단락 (단어 / 문장 / 고유 인용) | 합계 |
|---|---|---|
| ICSE25 | Boosting Symbolic Execution 149 / 7 / 13 · Symbolic Execution with Machine Learning 118 / 7 / 6 · Symbolic Execution with Seeding 63 / 4 / 4 | 330 words, 18문장 |
| ICSE26 | Enhancing Symbolic Execution 170 / 10 / 16 · Tuning External Parameters 193 / 9 / 19 · Search-based Software Testing 181 / 7 / 10 | 544 words, 26문장 |
| ASE26 | Boosting Symbolic Execution 209 / 9 / 16 · Software Testing with Option Arguments 124 / 6 / 8 · Software Testing for Specific Code Regions 139 / 7 / 9 | 472 words, 22문장 |
| FSE26 | 5.1 Probabilistic Approach 182 / 7 / 8 · 5.2 Grammar-Aware Approach 125 / 6 / 5 · 5.3 Grammar Generation Approach 103 / 6 / 9 | 410 words, 19문장 |
| **평균** | **주제 3개, 주제당 ~147 words, ~7문장, ~10개 인용** | **~440 words, ~21문장** |

- 본문의 약 5%다 ([skeleton.md](skeleton.md) §1.2).
- **첫 주제가 대개 가장 길다** (ICSE25, ASE26, FSE26). 하위 범주를 가장 많이 나열하기 때문이다.

---

## 2. 구조

### 2.1 주제 축

| 축 | 내용 | ICSE25 | ICSE26 | ASE26 | FSE26 |
|---|---|---|---|---|---|
| **① 같은 목표** | 같은 기술(SE, grammar-based fuzzing)의 성능을 높이는 기법들 | Boosting Symbolic Execution | Enhancing Symbolic Execution | Boosting Symbolic Execution | Probabilistic Approach |
| **② 같은 대상·자원** | 제안 기법이 다루는 대상을 쓰는 기법들 | Symbolic Execution with Seeding | Tuning External Parameters | Software Testing with Option Arguments | Grammar-Aware Approach |
| **③ 같은 방법·틀 / 인접 목표** | 같은 방법론이나 문제 틀, 비슷한 목표의 인접 분야 | Symbolic Execution with Machine Learning | Search-based Software Testing | Software Testing for Specific Code Regions | Grammar Generation Approach |
| 배치 순서 | | ① → ③ → ② | ① → ② → ③ | ① → ② → ③ | ① → ② → ③ |

- **①은 항상 첫째**다 (4/4). 범주명은 Intro I2의 SOTA 범주와 같다.
- 주제 제목 형식:
  - 동명사 + 분야: "Boosting / Enhancing Symbolic Execution", "Tuning External Parameters"
  - 분야 + with/for + 대상: "Symbolic Execution with Seeding", "Software Testing with Option Arguments", "Software Testing for Specific Code Regions"
  - 계열명: "Search-based Software Testing", "Probabilistic / Grammar-Aware / Grammar Generation Approach"

### 2.2 단락 안의 move

| 기호 | 역할 | 대표 표현 |
|---|---|---|
| **P** | 위치 선언 + 인용 묶음 | Our work shares a common goal with ... [..] |
| **F** | 최초 주장 | To our knowledge, X is the first to ... |
| **S** | 하위 범주·대표 도구 개관 | Search strategies [..] prioritize ..., such as ... [n] and ... [n]. / For example, A [n] and B [n] employ ... |
| **C** | 대조 | In contrast, / Unlike these, / Distinguished from these, / The key difference is that ... |
| **O** | 직교성·통합 가능성 | X is orthogonal to these ..., enabling it to be integrated to further enhance their performance. |
| Q | 정량 대조 (드묾) | irace [58] typically requires around 5,000 evaluations—equivalent to 167 hours ... |

### 2.3 논문별 배치

| ID · 주제 | 흐름 |
|---|---|
| ICSE25 · Boosting SE | P → F → S (3 범주) → O |
| ICSE25 · SE with ML | P → ("However, the specific aims ... differ") → S (도구 4개) → C + F ("Distinguished from these, TopSeed is the first to ...") |
| ICSE25 · SE with Seeding | P + C ("Although several techniques ... —they rely on predefined seeds.") → C ("In contrast, ...") |
| ICSE26 · Enhancing SE | P → 자기 소개 한 문장 → C + S ("Unlike ours, previous works on search heuristics ...") → S → S ("Beyond these, ...") |
| ICSE26 · Tuning External Parameters | P → 맥락(왜 중요한가) → S (분야별) → C ("However, unlike ParaSuit, ...") → Q (irace) → C (SymTuner 일대일) |
| ICSE26 · SBST | P → S (SBST 정의) → C (목표 차이) → 자기 정식화 재진술 |
| ASE26 · Boosting SE | F → P → S (4 범주: Search heuristics / Second / Third / Lastly SymTuner) → C → O |
| ASE26 · Option Arguments | P + C ("relates to ..., but differs in how ...") → S (2 계열) → C ("In contrast, ...") |
| ASE26 · Specific Code Regions | P → C ("However, Orbis differs in both the target regions and the methodology.") → S (도구 4개) → C + F |
| FSE26 · 5.1 | P → S (도구 5개) → O |
| FSE26 · 5.2 | P → S (도구 4개) → C ("Unlike these techniques, which focus on ..., our approach addresses a different problem: ...") |
| FSE26 · 5.3 | P (orthogonal) → S (도구 5개) → O ("We anticipate ...") |

**정형 순서:** P → (F) → S → C → (O). 12개 단락 모두 P로 시작하거나(11개) F로 시작한다(1개). C 또는 O 없이 끝나는 단락은 없다.

---

## 3. 단위별 분석

### P — 위치 선언

| 관계 동사 | 예 |
|---|---|
| shares a common goal with | "Our work **shares a common goal with** various existing techniques aimed at enhancing symbolic execution [8], [11], [15], ..." |
| belongs to | "Our approach **belongs to** the techniques that utilize machine learning to enhance symbolic execution [..]." / "Our work **belongs to a line of research that** introduces unique techniques to improve ..." |
| is rooted in | "Our approach **is rooted in** automatic parameter tuning methods [..]." |
| falls within the scope of | "Our approach **falls within the scope of** search-based software testing (SBST) [..]." |
| relates to ..., but differs in | "Our work **relates to** software testing techniques that construct valid option arguments for target programs [..], **but differs in** how option arguments are defined and utilized." |
| aligns with | "Our approach **aligns with** techniques designed to reach specific code regions within a program [..]." |
| is orthogonal to | "Our work **is orthogonal to** approaches that generate input grammars [..]." |
| (주어를 상대 기법으로) | "Several techniques have focused on learning grammars with probabilistic production rules to enhance performance [..]." / "**Another line of work** [..] integrates grammar awareness into mutation-based fuzzing." / "Existing approaches improve symbolic execution through various methodologies [..]." |

- 첫 문장 끝에 **5–14개 인용 묶음**을 단다.
- 관계 동사의 강도로 거리를 표현한다: shares a common goal / belongs to (가장 가까움) → relates to / aligns with (부분적으로 겹침) → is orthogonal to (겹치지 않고 결합 가능).

### F — 최초 주장

- "**To our knowledge, it is the first to** achieve this goal by adaptively selecting optimal seeds without the need for a predefined seed corpus." (ICSE25 ①)
- "**Distinguished from these, TopSeed is the first to** implement an online learning algorithm that automatically identifies useful seeds from scratch." (ICSE25 ③)
- "**To our knowledge, Orbis is the first technique to** improve symbolic execution by guiding it to reach option-related branches." (ASE26 ①, 단락 첫 문장)
- "**Unlike these approaches, Orbis is the first** symbolic execution technique that specifically targets option-related branches ..." (ASE26 ③)
- 쓰는 논문은 2/4 (ICSE25, ASE26)이고, 쓸 때는 단락 하나에 한 번이다. 대개 **"To our knowledge"**로 범위를 한정한다.
- ICSE26·FSE26은 최초 주장을 Contributions(Intro)에만 두고 Related Work에서는 반복하지 않는다.

### S — 하위 범주·대표 도구 개관

**범주 단위 개관** (주제 ①에서 주로 쓴다):

- "**Search strategies** [8], [11], [33], [37] **prioritize** which states to explore, focusing on unique criteria **such as** less-traveled paths [8] **and** minimal distance to uncovered codes [37]. **In contrast, state-pruning strategies** [15], [34], [35] **aim to** eliminate redundant states, guided by specific pruning criteria, **including** previously explored basic blocks [12] and executed path suffixes [14]. **Constraint-solving techniques** [..] have developed methods for ..."
- 틀: `<범주> [인용들] <동사> ..., such as / including <기준 예> [n] and <기준 예> [n].`
- 범주 나열 연결어: In contrast, / Second, / Third, / Lastly, / Beyond these,
- 범주는 Intro I2와 같은 이름·같은 순서다: search → state-pruning → constraint-solving (→ state-merging, parameter tuning)

**도구 단위 개관** (주제 ②③에서 주로 쓴다):

- "**For example, Learch [11] and ParadySE [33] employ** offline learning algorithms to ... **Leo [40] aims to** learn how to transform ... **Homi [15] uses** learned discrete and continuous probability distributions to ..."
- "**EvoGFuzz [10] introduced** an evolutionary algorithm that ... **Similarly, Soremekun et al. [37] presented** a technique that ... **Kifetew et al. [26] proposed** a novel approach that ..."
- 틀: `<도구명 | 저자 et al.> [n] <동사> <무엇을> to <목적>.` 도구 하나에 한 문장이다.
- 동사 시제: 도구의 동작은 현재형(employs, aims, uses, prioritizes), 논문의 기여는 과거형(introduced, presented, proposed — FSE26).

**맥락 문장** (드묾): "Automatically tuning external parameters is growing in importance as tools in various fields evolve and become more sophisticated. As these tools incorporate more parameters ..., users often find it challenging to configure them." (ICSE26 ②)

### C — 대조

| 문형 | 예 |
|---|---|
| In contrast, X ... | "**In contrast**, TopSeed does not require a predefined seed corpus. Instead, it automatically selects effective seeds ... without prior knowledge." |
| Unlike ours / Unlike these, | "**Unlike ours**, previous works on search heuristics [..] have aimed to enhance symbolic execution by prioritizing which states to explore ..." / "**Unlike these techniques, which focus on** how to mutate inputs effectively while preserving their grammars, **our approach addresses a different problem:** determining which production rules ..." |
| Distinguished from these, | "Distinguished from these, TopSeed is the first to ..." |
| However, unlike X, which ..., existing ... | "**However, unlike ParaSuit, which** configures parameters using an online learning algorithm, **existing approaches** for tuning configurable systems **rely on offline strategies that require substantial prior information** for learning." |
| differs in | "However, Orbis **differs in both the target regions and the methodology**." / "but **differs in how** option arguments are defined and utilized" |
| 일대일 대조 | "**Both our approach, ParaSuit, and Symtuner [20] aim to** adjust the external parameters of symbolic execution tools. **The key difference is that** ParaSuit automatically identifies and configures parameters in a program-specific manner, **whereas** Symtuner relies on manually defined spaces that are fixed and do not vary across programs." |
| 목표 차이 | "However, within the SBST framework, ParaSuit and prior techniques **differ substantially in the goals they target**. ParaSuit aims to maximize exploration ..., **whereas** prior approaches [..] focus on quickly converging to a single efficient setting ..." |

**대조 축 (무엇이 다른가):**

| 축 | 예 |
|---|---|
| **사전 지식·수동 설정 vs 자동** (가장 흔함) | "they rely on predefined seeds" / "rely on offline strategies that require substantial prior information" / "relies on manually defined spaces" / "manually define option arguments for each program" ↔ "requiring no prior knowledge", "from scratch" |
| 목표 | "differ substantially in the goals they target" / "addresses a different problem" |
| 대상 | "differs in both the target regions and the methodology" |
| 방법 | "configures parameters using an online learning algorithm" vs offline |

- 대조는 상대의 **결함이 아니라 다른 목표·가정**으로 쓴다. "fail", "poor" 같은 평가어는 쓰지 않는다.
- 대조 문장에서는 **우리 기법을 주어로** 다시 한 줄 요약한다: "In contrast, Orbis automatically constructs option arguments while interacting with a symbolic executor, requiring no prior knowledge. It further leverages these arguments to ..."

### O — 직교성·통합 가능성

- "TopSeed **is orthogonal to these existing methods, enabling it to be integrated to further enhance their performance**."
- "**Since Orbis is a complementary technique, integrating it with existing approaches improves their performance**."
- "Our work, RSFuzz, **can be integrated with these probabilistic techniques to further enhance** grammar-based fuzzing."
- "**We anticipate that** grammar-based fuzzers can be further improved if RSFuzz uses grammars produced by these works."
- 주로 주제 ①(같은 목표) 끝에 둔다. "경쟁"이 아니라 "결합"으로 끝내며, 이것이 §4의 "baseline + X" 실험 구도와 맞물린다.

### Q — 정량 대조 (ICSE26만)

> "For example, irace [58] typically requires around 5,000 evaluations—equivalent to 167 hours of symbolic execution—to converge, which makes it unsuitable for our setting."

상대 기법이 **우리 설정에 맞지 않는 이유**를 수치로 보여 준다. baseline에서 왜 뺐는지를 정당화하는 역할도 한다.

### 자기 정식화 재진술 (ICSE26만)

> "In this context, we formulate an optimization problem that identifies sets of parameters and values (PV_1, PV_2, ···, PV_n) such that the union of symbolic execution outcomes (e.g., branch coverage) is maximized within a fixed testing budget. We propose a specialized algorithm, tailored for symbolic execution, that dynamically selects promising parameters, ..."

틀(SBST) 안에서 우리 문제를 다시 정의한다. §2.2 Goal 식과 같은 내용이다.

---

## 4. 문체 특징

| 항목 | 관찰 |
|---|---|
| 주어 | 위치 선언은 **Our work / Our approach**, 개관은 **범주명·도구명**, 대조는 **도구명(X)** |
| 시제 | 범주·도구의 동작은 현재형, 논문 기여는 과거형(introduced, proposed), 연구 흐름은 현재완료(have aimed, have been proposed, have emerged) |
| 연결어 | In contrast, / However, / Unlike these, / Distinguished from these, / Similarly, / For example, / For instance, / Second, Third, Lastly, / Beyond these, / Another line of work |
| 인용 | 문장마다 있다. 단락 첫 문장에 5–14개 묶음, 이후 예시마다 개별 인용 |
| 도구 표기 | 도구명 [n] (small caps는 본문 규칙대로) 또는 "저자 et al. [n]" (도구명이 없을 때) |
| 어조 | 중립. 차이를 목표·가정으로 설명하고 평가어를 피한다 |
| hedging | "To our knowledge"(최초 주장), "We anticipate"(통합 전망) 정도 |
| **넣지 않는 것** | 섹션 리드·마무리 단락, 실험 수치(irace 예외), 표·그림, 우리 기법의 상세(한 줄 요약만) |

---

## 5. 수식·알고리즘·플로트

해당 없음 (4/4). 수식, 알고리즘, 표, 그림이 없다. 약어는 처음 쓸 때 정의한다: "search-based software testing (SBST)", "probabilistic context-sensitive grammar (PCSG)", "abstract syntax trees (ASTs)".

---

## 6. 섹션 간 연결

| Related Work 요소 | 대응 위치 | 관계 |
|---|---|---|
| 주제 ①의 범주 | Intro I2 SOTA 범주, §2.1 SOTA 대응 | 같은 범주명·같은 순서 (search strategies → state-pruning → constraint-solving) |
| 주제 ①의 도구 | §4.1 Baselines | Learch, Homi, AAQC, SymTuner 같은 baseline이 여기서 범주의 대표로 다시 나온다 |
| 대조 축 (사전 지식 vs 자동) | Abstract M4, Intro I3·I4, Conclusion | "from scratch / without prior knowledge"라는 논문 전체의 키워드를 Related Work의 대조 기준으로 쓴다 |
| 가장 가까운 SOTA 일대일 대조 | Intro I3 (실명 지목), §4 baseline | ICSE26·ASE26 SymTuner: Intro에서 한계를 지적하고, §4에서 이기고, Related Work에서 차이를 정리한다 |
| 최초 주장 | Contributions bullet 1 | 표현을 맞춘다 (ICSE26은 Contributions에만 둔다) |
| O (통합 가능성) | Abstract M1 "complementary", §4 "baseline + X" 실험 | 결합을 주장한 기법과 실제로 결합 실험을 한다 (FSE26 ProbF + RSFuzz) |
| 자기 정식화 재진술 | §2.2 Goal 식 | ICSE26 |

---

## 7. 템플릿

```text
## 5 Related Work
**<Improving the same technique>.** Our work shares a common goal with various existing techniques aimed at enhancing <domain> [c1–c9].
  (opt.) To our knowledge, it is the first to <unique claim> without <prior knowledge / manual effort>.
  <Category 1> [..] <verb> ..., focusing on criteria such as <criterion> [n] and <criterion> [n].
  In contrast, <category 2> [..] aim to ..., including <example> [n].
  <Category 3> [..] have developed methods for ..., such as <example> [n].
  <Tool> is orthogonal to these existing methods, enabling it to be integrated to further enhance their performance.

**<Domain> with <same object/resource>.** Our work relates to techniques that <use the same object> [..], but differs in how <object> is <obtained/used>.
  Several techniques [..] <manually define / rely on predefined> <object> to achieve <goal>. <Tool A> [n] ...; <Tool B> [n] ....
  In contrast, <Tool> automatically <...> without prior knowledge. It further <...>.

**<Same method / adjacent goal>.** Our approach belongs to / falls within the scope of <method family> [..].
  For example, <Tool C> [n] and <Tool D> [n] employ <method> to <purpose>. <Tool E> [n] aims to ....
  However, unlike <Tool>, which <...>, existing approaches <...>. (opt.) For example, <Tool F> [n] requires <quantity>, which makes it unsuitable for our setting.
  Both <Tool> and <closest SOTA> [n] aim to <...>. The key difference is that <Tool> <...>, whereas <closest SOTA> <...>.
```

---

## 8. 작성 체크리스트

- [ ] Experiments 뒤에 두었고, 주제 단락 3개(~440 words)이며 리드·마무리 단락이 없는가
- [ ] 주제 ①(같은 목표)이 첫째이고, ②(같은 대상) ③(같은 방법·인접 목표)를 모두 다뤘는가
- [ ] 단락 첫 문장이 관계 동사 + 인용 묶음인가 (shares a common goal with / belongs to / relates to ..., but differs in / is orthogonal to)
- [ ] 범주 이름·순서가 Intro I2와 같은가
- [ ] 예시를 "<도구> [n] <동사> ..." 한 문장씩, 기준 예를 "such as ... [n] and ... [n]"으로 들었는가
- [ ] 단락마다 대조(C) 또는 통합(O)으로 끝나는가
- [ ] 대조가 결함이 아니라 목표·가정의 차이로 쓰였고, 주된 축이 "사전 지식·수동 vs 자동"인가
- [ ] 가장 가까운 SOTA를 "Both ... aim to ... The key difference is that ..., whereas ..."로 일대일 대조했는가
- [ ] 최초 주장은 "To our knowledge"로 한정하고, Contributions와 표현이 같은가
- [ ] "결합 가능"이라고 쓴 기법과 실제 결합 실험(§4)이 대응하는가
- [ ] 수치·표·그림이 없는가

---

## 부록 A. 원문 (주제 단락 12개, move 태그)

**ICSE25 — TopSeed**

> **[① Boosting Symbolic Execution.]** [P] Our work shares a common goal with various existing techniques aimed at enhancing symbolic execution [8], [11], [15], [18], [19], [33], [34], [35], [36]. [F] To our knowledge, it is the first to achieve this goal by adaptively selecting optimal seeds without the need for a predefined seed corpus. [S] Search strategies [8], [11], [33], [37] prioritize which states to explore, focusing on unique criteria such as less-traveled paths [8] and minimal distance to uncovered codes [37]. In contrast, state-pruning strategies [15], [34], [35] aim to eliminate redundant states, guided by specific pruning criteria, including previously explored basic blocks [12] and executed path suffixes [14]. Constraint-solving techniques [18], [19], [36], [38] have developed methods for effectively solving expensive and complex constraints, such as floating-point calculation [36], to increase the overall effectiveness of symbolic execution. [O] TopSeed is orthogonal to these existing methods, enabling it to be integrated to further enhance their performance.
>
> **[③ Symbolic Execution with Machine Learning.]** [P] Our approach belongs to the techniques that utilize machine learning to enhance symbolic execution [11], [15], [33], [39], [40], [41]. However, the specific aims of applying machine learning differ among these techniques. [S] For example, Learch [11] and ParadySE [33] employ offline learning algorithms to automatically develop effective search strategies for symbolic execution. Leo [40] aims to learn how to transform the target program under test for boosting the efficacy of symbolic execution. Homi [15] uses learned discrete and continuous probability distributions to retain only valuable program states while minimizing the total state count. [C + F] Distinguished from these, TopSeed is the first to implement an online learning algorithm that automatically identifies useful seeds from scratch.
>
> **[② Symbolic Execution with Seeding.]** [P + C] Although several techniques [20], [22], [24], [42] utilize seed inputs in symbolic execution to achieve specific goals—such as reaching patch codes [20], generating highly-structured inputs [24], and prioritizing inputs [42]—they rely on predefined seeds. [C] In contrast, TopSeed does not require a predefined seed corpus. Instead, it automatically selects effective seeds from inputs generated during symbolic execution without prior knowledge.

**ICSE26 — ParaSuit**

> **[① Enhancing Symbolic Execution.]** [P] Our work belongs to a line of research that introduces unique techniques to improve the effectiveness of symbolic execution [6, 9, 10, 19, 44, 51, 57, 75, 84, 89, 91]. ParaSuit automates parameter configuration for symbolic execution, removing manual intervention. [C + S] Unlike ours, previous works on search heuristics [10, 19, 44, 57, 75, 84] have aimed to enhance symbolic execution by prioritizing which states to explore from a vast pool of candidates. Each heuristic has its own criteria for selecting specific program states. For instance, the Subpath-Guided Search heuristic [57] is to prioritize states with fewer explored subpaths. Space reduction heuristics [6, 9, 51, 89, 91] aim to address the state-explosion problem by minimizing redundant program paths or states. Each heuristic introduces an approach to efficiently identify non-essential program paths. For example, post-conditioned symbolic execution [89] terminates redundant states based on already explored path suffixes. [S] Beyond these, various methods like state-merging [27, 32, 56] and constraint solving reduction [32, 54, 69] have been proposed to optimize symbolic execution.
>
> **[② Tuning External Parameters.]** [P] Our approach is rooted in automatic parameter tuning methods [2, 4, 5, 20, 47–50, 58, 59, 62, 64, 83]. Automatically tuning external parameters is growing in importance as tools in various fields evolve and become more sophisticated. As these tools incorporate more parameters to optimize performance, users often find it challenging to configure them. [S] Consequently, numerous automatic tuning techniques, informed by domain knowledge, have emerged in fields like robotics [5, 59], machine learning models [61, 65, 86], big data processing systems [34, 45], static analysis [85], and symbolic execution [20]. [C] However, unlike ParaSuit, which configures parameters using an online learning algorithm, existing approaches for tuning configurable systems rely on offline strategies that require substantial prior information for learning. [Q] For example, irace [58] typically requires around 5,000 evaluations—equivalent to 167 hours of symbolic execution—to converge, which makes it unsuitable for our setting. [C 일대일] Both our approach, ParaSuit, and Symtuner [20] aim to adjust the external parameters of symbolic execution tools. The key difference is that ParaSuit automatically identifies and configures parameters in a program-specific manner, whereas Symtuner relies on manually defined spaces that are fixed and do not vary across programs.
>
> **[③ Search-based Software Testing.]** [P] Our approach falls within the scope of search-based software testing (SBST) [1, 17, 26, 36, 42, 52, 53, 70, 76, 92]. [S] At a high-level, each specific testing task in SBST—such as improving coverage [36], usability [1], or fault detection [70]—is formulated as an optimization problem and addressed using a domain-specific algorithm tailored to the task. [C] However, within the SBST framework, ParaSuit and prior techniques differ substantially in the goals they target. ParaSuit aims to maximize exploration by applying multiple efficient parameter values to the target program, whereas prior approaches [17, 52, 53] focus on quickly converging to a single efficient setting within a predefined space and generally remain fixed thereafter without further adjustment. [재진술] In this context, we formulate an optimization problem that identifies sets of parameters and values (PV_1, PV_2, ···, PV_n) such that the union of symbolic execution outcomes (e.g., branch coverage) is maximized within a fixed testing budget. We propose a specialized algorithm, tailored for symbolic execution, that dynamically selects promising parameters, constructs program-specific value sampling spaces for those selected, and defines two distinct sampling strategies based on data accumulated during interaction with the symbolic execution tool.

**ASE26 — Orbis**

> **[① Boosting Symbolic Execution.]** [F] To our knowledge, Orbis is the first technique to improve symbolic execution by guiding it to reach option-related branches. [P] Existing approaches improve symbolic execution through various methodologies [4, 8, 10, 11, 22–24, 34, 39, 41, 42, 46, 49]. [S] Search heuristics [4, 22, 41, 49] prioritize states to maximize code coverage and trigger bugs based on predefined criteria, such as states containing less exercised subpaths [27] or states with the shortest distance to uncovered code regions [4]. Second, state-pruning strategies [3, 10, 11, 23] improve symbolic execution efficiency by eliminating redundant states using unique criteria, such as states executing the same code blocks as previously explored ones [3], states that are likely to generate invalid inputs [46], and states that fail to reach annotated bug locations [23]. Third, constraint-solving methods [24, 34, 39, 42] focus on reducing the computational cost of solving specific constraint types, including array constraints [34] and floating-point constraints [28]. Lastly, SymTuner [8] automatically tunes the external parameters of a symbolic executor (e.g., KLEE) from a manually specified parameter space. [C] In contrast, Orbis improves symbolic execution by constructing option arguments for the target program and guiding exploration toward OBs. [O] Since Orbis is a complementary technique, integrating it with existing approaches improves their performance.
>
> **[② Software Testing with Option Arguments.]** [P + C] Our work relates to software testing techniques that construct valid option arguments for target programs [22, 24–26, 40, 44, 45, 50], but differs in how option arguments are defined and utilized. [S] Several symbolic execution techniques [22, 24] manually define option arguments for each program and concatenate them with generated inputs to enhance coverage. Some grey-box fuzzing techniques [25, 26, 40, 44, 45, 50] attempt to test a wide range of option arguments by mutating options extracted from the program's manual pages and source code. [C] In contrast, Orbis automatically constructs option arguments while interacting with a symbolic executor, requiring no prior knowledge. It further leverages these arguments to initialize the symbolic executor states and reduce SMT-solver invocations, maximizing option-related coverage.
>
> **[③ Software Testing for Specific Code Regions.]** [P] Our approach aligns with techniques designed to reach specific code regions within a program [2, 14, 16, 31, 33, 35, 36, 47, 48]. [C] However, Orbis differs in both the target regions and the methodology. [S] For instance, directed symbolic execution [31] prioritizes code lines associated with bugs (e.g., failing assertions) and quickly reaches them using specialized search heuristics. Oasis [14] and KATCH [33] focus on covering newly added patch codes by leveraging heuristics based on static and dynamic analysis. AFLGo [2] prioritizes user-defined target regions using seeds with the shortest distance, while AFLSmart++ [35] targets hard-to-reach input chunks by delicately mutating the seed that can reach those chunks. [C + F] Unlike these approaches, Orbis is the first symbolic execution technique that specifically targets option-related branches by automatically constructing option arguments and initializing the corresponding symbolic states.

**FSE26 — RSFuzz**

> **[① 5.1 Probabilistic Approach]** [P] Several techniques have focused on learning grammars with probabilistic production rules to enhance performance [10, 26, 28, 37, 42]. [S] EvoGFuzz [10] introduced an evolutionary algorithm that iteratively updates the probabilities of a probabilistic context-free grammar (PCFG) to effectively find many defects. Similarly, Soremekun et al. [37] presented a technique that learns the probabilities of PCFG from a given set of inputs and inverted the learned probabilities to increase method coverage and produce many failure-inducing inputs. Kifetew et al. [26] proposed a novel approach that learns a probabilistic grammar from a corpus and evolves inputs based on this grammar with the evolutionary guidance of genetic programming, resulting in high branch coverage. Skyfire [42] learns a probabilistic context-sensitive grammar (PCSG) from a large corpus of inputs to generate syntactically and semantically valid seeds, enabling mutation fuzzers to achieve greater coverage. Falcon [46] aims to efficiently discover hidden bugs in Satisfiability Modulo Theories (SMT) solvers, such as CVC4 [3] and Z3 [9], using a PCFG model for the SMT-LIB2 language. [O] Our work, RSFuzz, can be integrated with these probabilistic techniques to further enhance grammar-based fuzzing.
>
> **[② 5.2 Grammar-Aware Approach]** [P] Another line of work [2, 22, 36, 42, 43] integrates grammar awareness into mutation-based fuzzing. [S] LangFuzz [22] recombines fragments of real-world inputs to implicitly preserve grammatical structure. TypeFuzz [36] uses the SMT-LIB type system as grammar-like constraints to ensure well-formed formulas. Superion [43] mutates abstract syntax trees (ASTs) to preserve syntactic validity during coverage-guided fuzzing. Nautilus [2] extends this line of work by generating an initial seed corpus from a probabilistic context-free grammar (PCFG) and then applying grammar-aware, feedback-guided mutations to explore programs more effectively. [C] Unlike these techniques, which focus on how to mutate inputs effectively while preserving their grammars, our approach addresses a different problem: determining which production rules of a grammar should not be derived in a particular order, thereby reducing coverage-equivalent inputs.
>
> **[③ 5.3 Grammar Generation Approach]** [P] Our work is orthogonal to approaches that generate input grammars [4, 5, 14–16, 23, 25, 33, 45]. [S] Learn&Fuzz [14] uses recurrent neural networks to automatically generate input grammars for PDF objects from sample inputs, while REINAM [45] synthesizes probabilistic context-free grammars via reinforcement learning. Mimid [15] mines more precise and readable input grammars by tracking dynamic control flow during program executions. CLIFuzzer [16] extracts grammars of command-line options from getopt() calls. Bettscheider et al. [5] propose symbolic parsing to derive grammars from parser code without sample inputs. [O] We anticipate that grammar-based fuzzers can be further improved if RSFuzz uses grammars produced by these works.
