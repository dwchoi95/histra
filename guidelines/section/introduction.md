# Introduction — guidelines 4편 분석

[skeleton.md](skeleton.md)의 하위 문서. Introduction을 단락 단위로 분석한다.
원문 전체는 단락·역할 태그를 붙여 부록 A에 실었다.

---

## 0. 핵심 규칙

1. Introduction은 **본문 단락 4–7개 + Contributions(3 bullets)**, 700–1,000 words다. 논문 구성을 안내하는 로드맵 단락("The rest of this paper is organized as follows")은 4편 모두 없다.
2. 흐름은 **Domain → SOTA → Gap → Proposal → (Challenge) → Algorithm → Results → Contributions**로 고정이다. 단락 첫머리도 거의 고정이다: *However* → *In this paper, we present* → *Experimental results demonstrate* → *Contributions.*
3. **배경(Domain+SOTA)과 Gap을 합치면 약 절반(~47%)**이다. 배경을 짧게 쓴 논문은 Gap을 길게 쓴다.
4. Gap 단락에서 **신조어를 "In this work, we (newly) define ..."로 정의**하고, §2를 forward ref하며 **수치**로 뒷받침한다.
5. 인용은 앞쪽 배경 단락에 몰린다. **Proposal·Algorithm·Contributions에는 인용이 없고**, Results에서는 baseline만 인용한다.

---

## 1. 분량

| ID | 단락 수 | 단어 수 | 평균 단락 길이 (Contributions 제외) | 문장 수 | 평균 문장 길이 |
|---|---|---|---|---|---|
| ICSE25 | 5 + C | 726 | 126 | 32 | 22.7 |
| ICSE26 | 6 + C | 1,005 | 151 | 40 | 25.1 |
| ASE26 | 4 + C | 699 | 142 | 26 | 26.9 |
| FSE26 | 7 + C | 926 | 115 | 38 | 24.4 |
| **평균** | **5.5 + C** | **~840** | **~134** | **~34** | **~24.8** |

- C = Contributions 단락. bullet은 문장 하나로 셌다.
- 단어 수는 플로트·각주를 걷어낸 정제 텍스트 기준이라 [skeleton.md](skeleton.md) §1.2 표보다 2–5% 적다.
- 플로트는 ICSE26만 Figure 1(기존 도구의 파라미터 설정 예시)을 Introduction에 둔다.

---

## 2. 구조

### 2.1 단락 역할 정의

| 역할 | 내용 | 출현 |
|---|---|---|
| **I1 Domain** | 분야 정의 + 동작 원리 | 4/4 (항상 P1) |
| **I2 SOTA** | 알려진 난제 + 이를 다룬 SOTA를 범주별로 나열 | 4/4 (ASE26은 P1 끝과 P2 첫 절에 걸침) |
| **I3 Gap** | 간과된 문제 + 신조어 정의 + 수치 근거 + 귀결 | 4/4 (ICSE26은 2단락) |
| **I4 Proposal** | "In this paper, we present X" + 핵심 아이디어 | 4/4 |
| I5 Challenge | 해결이 어려운 이유 (규모 수치) | 2/4 (ICSE25는 P4 안, FSE26은 독립 단락) |
| **I6 Algorithm** | 알고리즘 단계 | 4/4 (FSE26만 독립 단락, 나머지는 Proposal 단락 안) |
| **I7 Results** | 실험 설정 + 결과 수치 + 추가 평가 | 4/4 |
| **I8 Contributions** | 3 bullets | 4/4 (항상 마지막) |

### 2.2 논문별 배치

| ID | P1 | P2 | P3 | P4 | P5 | P6 | P7 | P8 |
|---|---|---|---|---|---|---|---|---|
| ICSE25 | I1 | I2 | I3 | I4+I5+I6 | I7 | I8 | | |
| ICSE26 | I1 | I2 | I3 (사용자 부담) | I3 (기존 기법 한계, Fig. 1) | I4+I6 | I7 | I8 | |
| ASE26 | I1 (+I2 난제) | I2+I3 | I4+I6 | I7 | I8 | | | |
| FSE26 | I1 | I2 | I3 | I4 | I5 | I6 | I7 | I8 |

순서가 바뀐 경우는 없다. 차이는 역할을 한 단락에 합치는지 나누는지뿐이다.
FSE26(1단 포맷)은 역할마다 단락을 나눴고, 2단 포맷 논문은 I4–I6을 한 단락에 합치는 경향이 있다.

### 2.3 역할 그룹별 비중

| ID | 배경 (I1–I2) | Gap (I3) | 제안 (I4–I6) | 결과 (I7) | Contributions (I8) |
|---|---|---|---|---|---|
| ICSE25 | 38.7% | 15.0% | 16.3% | 16.9% | 13.1% |
| ICSE26 | 17.0% | 35.8% | 21.4% | 16.0% | 9.8% |
| ASE26 | 20.2% | 20.2% | 19.7% | 21.3% | 18.6% |
| FSE26 | 27.6% | 13.7% | 28.3% | 17.2% | 13.2% |
| **평균** | **~26%** | **~21%** | **~21%** | **~18%** | **~14%** |

- 배경+Gap = 54% / 53% / 40% / 41%. 문제 설명이 약 절반을 차지한다 (Abstract의 문제 비중 ~42%와 비슷).
- 결과 단락은 16–21%로 4편 모두 비슷하다.

---

## 3. 단락별 분석

### I1 Domain — "X is a [representative] software testing method that ..."

| ID | 첫 문장 |
|---|---|
| ICSE25 | Symbolic execution [1]–[4] is a **representative software testing method** designed to automatically generate promising inputs that increase code coverage or trigger bugs in a target program. |
| ICSE26 | Symbolic execution [15, 16, 38, 73] is **undoubtedly one of the prominent software testing methods**, actively researched in both academia and industry [14, 39, 40]. |
| ASE26 | Symbolic execution [5, 6, 20, 38] is a **sophisticated software testing method** that automatically generates test-cases, achieving high code coverage of the target program and uncovering diverse hidden bugs. |
| FSE26 | Grammar-based fuzzing is a **mainstream software testing technique** to effectively increase code coverage and find subtle bugs [2, 22, 29, 34, 37–39, 42]. |

- 첫 문장 틀: `<분야> [인용 묶음] is a <평가 형용사> software testing <method|technique> <that|designed to> <목표: coverage·bugs>.` (4/4)
- 이어서 **동작 원리를 3–5문장**으로 설명한다. "This method replaces ... / More specifically, ... / In particular, ..." 순으로 점점 구체화한다.
  이 설명은 §2.1의 형식화와 Algorithm 1로 이어진다.
- FSE26은 형제 기법과 대비해 분야를 정의한다: "Unlike mutation-based fuzzing [6, 7, 13, 32], which ..., grammar-based fuzzing can ..."
- 길이 86–152 words. 인용은 정의 문장의 대표 문헌 묶음과 도구(SMT solver 등)에만 단다.

### I2 SOTA — 난제 2개 → SOTA 범주 나열 → 칭찬으로 마무리

- **난제 2개 제시** (SE 논문 3편): "faces two **open / well-known open / notorious** challenges: A and B."
  ICSE25는 "The former denotes ... The latter refers to ..."로 하나씩 풀어 쓴다.
  FSE26은 대신 핵심 설계 결정을 제시한다: "A key component of grammar-based fuzzers is determining which production rules to apply ..."
- **SOTA를 범주명 + 인용 묶음으로 나열한다.**
  - "These include search strategies [..], state-pruning strategies [..], state-merging strategies [..], and constraint-solving cost reduction strategies [..], among others." (ICSE25)
  - "In response to these challenges, various techniques have been proposed, including search strategy [..], path-pruning [..], constraints solving [..], and state-merging [..]." (ICSE26)
  - FSE26은 대표 도구를 이름으로 든다: "Some basic grammar-based fuzzers, such as Grammarinator [21], randomly select ... More recent fuzzers [37, 38, 47] adopt more sophisticated methods: Soremekun et al. [37] use ..."
- **SOTA를 칭찬하며 끝낸다** (다음 단락의 *However*를 위한 포석):
  "Recent advances ... have significantly improved its performance" / "As a result, the effectiveness of modern ... has seen marked improvement." / "It is widely recognized that intelligently selecting production rules is crucial ..."
- **인용 밀도가 가장 높은 단락이다** (단락당 14–16개 문헌).

### I3 Gap — 관찰 → 신조어 정의 → 왜 문제인가 → 수치 → 선행 연구 지목 → 귀결

대체로 아래 6단계 순서를 따른다 (일부 생략·순서 교환 있음).

| 단계 | ICSE25 | ICSE26 | ASE26 | FSE26 |
|---|---|---|---|---|
| (a) 전환 + 관찰 | "**However**, these recent techniques have typically demonstrated their effectiveness without considering "seeding"." | "**Yet, despite** their notable performance enhancements, it has **paradoxically** become more challenging for users ..." | "**Although** SOTA techniques [..] ... have remarkably enhanced its performance, **we observed that** these recent techniques still fail to ..." | "**However, our observation is that** both random and probabilistic grammar-based fuzzers often generate a substantial number of "coverage-equivalent" inputs." |
| (b) 신조어 정의 | "When given a seed, the seeding process initializes ..." | "the need for users to determine the "parameter values" ..." / "they are **not self-configuring**: they cannot ..." | "**In this work, we newly define** option-related branches (OBs) as ..." | "**In this work, we define** an input as coverage-equivalent if ..." |
| (c) 왜 문제인가 | "Seeding offers an advantageous starting point ..., thus serving as a complementary approach ..." | "Thus, adjusting these parameter values ... imposes a considerable burden on users." | "Since a program's core functionalities are typically implemented as program options, ..." | "Generating such inputs is undesirable, as they are less likely to ..." |
| (d) 수치 근거 | (없음) | "exceeds a hundred" + Figure 1 + "**As we show in Section 4.5**, ..." | "**as demonstrated in Section 2**, ... covered **only 7.9%** of the targeted total OBs" | "**As shown in Section 2**, ... **80.3%** ... Similarly, ... **81.0%**" |
| (e) 선행 연구 지목 | "Existing techniques have predominantly shown their capabilities assuming no initial seeding [10], [11], [15] or ... with a predefined seed corpus [19], [20], [21]." | "many previous works [..] have depended on ... Other works [..] have manually adjusted ..." / "**For example, SymTuner [20]** relies on manually defined parameter spaces ..." | "four independent SOTA techniques—search heuristic [22], state-pruning [10], SMT solving cost reduction [42], and external parameter tuning [8]—exhibited unsatisfactory performance." | "the random fuzzer [21] ... the probabilistic fuzzer [37] ..." |
| (f) 귀결 | "**Unfortunately**, this complementary factor has often been overlooked ..." | "Without such self-configuration, ... users must manually ..., adding complexity." | "..., **leaving** a significant portion of program functionalities untested." | "**Consequently**, these fuzzers tend to spend valuable testing time ..." |

- Abstract와 달리 **선행 연구를 이름과 인용으로 지목한다**. 가장 가까운 SOTA는 실명으로 쓴다 (SymTuner).
- 수치 근거는 **§2의 측정 결과를 미리 가져온다** ("As shown in Section 2").
- ICSE26은 Gap을 두 단락으로 나눈다: (1) 사용자 부담 → (2) 기존 튜닝 기법의 한계. 둘째 단락에 Figure 1을 둔다.

### I4 Proposal — "In this paper, we present X, a novel ... approach that ..."

| ID | 첫 문장 | 둘째 문장 |
|---|---|---|
| ICSE25 | In this paper, we present TopSeed, **a novel seeding approach** designed to enhance diverse symbolic execution techniques **from scratch, thereby maximizing** their performance. | Our method iteratively selects seeds from inputs generated during symbolic execution on the target program, without relying on a predefined seed corpus. |
| ICSE26 | We present ParaSuit, **a new self-configuring approach** that autonomously selects suitable parameters and determines their values in a program-aware way **from scratch, thereby maximizing** the performance of symbolic execution. | (바로 알고리즘 설명) |
| ASE26 | In this paper, we present Orbis, **a new complementary approach** for existing symbolic execution techniques that guides their exploration toward maximizing OB coverage **without prior knowledge**. | By doing so, Orbis improves both total branch coverage and bug-finding capability. |
| FSE26 | In this paper, we present RSFuzz, **a novel approach** that enhances grammar-based fuzzers by preventing the generation of coverage-equivalent inputs during testing. | **The core idea is to** iteratively identify recurrent sequences ..., **defined as** ... |

- 첫 문장 틀: `In this paper, we present <Tool>, a <novel|new> [<유형 형용사>] approach <that|designed to|for ...> ..., <from scratch|without prior knowledge>, thereby maximizing <...>.`
- 둘째 문장은 핵심 아이디어나 기대 효과다. FSE26은 가설로 제시한다: "Since ..., **our hypothesis is that** examining this information allows us to ..."
- 인용이 없다.

### I5 Challenge — 규모 수치 (2/4)

- ICSE25 (P4 안, 한 문장): "**A major challenge is the vast number of** candidate seeds—**often tens of thousands** for real-world programs—which complicates the selection of promising seeds."
- FSE26 (독립 단락): "**However, a key challenge is the sheer scale of** coverage-equivalent inputs. **As reported in Section 2**, ... about **19,729** distinct groups ... **Even when** focusing only on the 200 largest groups, each group **still** contained over **388** inputs on average. **Thus**, identifying why ... requires analyzing hundreds of ..."
- 틀: `A major/key challenge is the vast number / sheer scale of X` → 수치 (대시 삽입 또는 §2 ref) → `Even when ..., still ...` (범위를 좁혀도 여전히 큼) → `Thus, ... requires ...`
- 다음 문장은 항상 **"To overcome/address this challenge, we (have) developed a customized/specialized algorithm"**이다 (2/2).
- ICSE26·ASE26은 Introduction에 도전과제가 없다. ASE26은 §2.2 끝에서 "Our work thus tackles two key challenges"로 대신 제시한다.

### I6 Algorithm — 두 가지 서술 방식

- **(A) 동사 나열형** (ICSE25, FSE26) — 단계 이름 없이 동사를 나열한다.
  - "To overcome this challenge, we have developed a customized online learning algorithm. This algorithm **iteratively groups** candidate inputs, **ranks** each group, **and selects** a promising seed from the top-ranked group. It also continuously updates ..."
  - "To address this challenge, we developed a specialized algorithm that **iteratively collects** informative data ..., **groups** inputs by code coverage, **selects** key groups, **and captures** the recurrent sequences ..."
- **(B) 단계 명명형** (ICSE26, ASE26) — 1회성 초기 단계 뒤에 반복 단계를 이름 붙여 하나씩 설명한다.
  - "**First**, Orbis automatically extracts useful data ... **It then iteratively performs three stages: (1) Construct**, which ...; **(2) Guide**, which ...; **and (3) Update**, which ... In addition, Orbis leverages ..."
  - "ParaSuit **begins by** automatically extracting ... **Once this extraction stage is complete**, ParaSuit enters two iterative stages: parameter selection and value sampling. **In the selection stage**, ... **In the sampling stage**, ..."
- 마무리 문장 (2/4): "**As these two stages repeat**, ParaSuit continually refines the dataset, enabling it to provide increasingly effective parameter values **tailored to the target program**." / "**By repeating these stages**, RSFuzz produces recurrent sequences **tailored to each program** and its grammar, thereby improving ..."
- 단계마다 직관을 한 구절씩 덧붙인다. 예: "a customized scoring function that captures both its ability to reach rarely explored branches and its synergy with others"
- 수식과 인용은 없다.

### I7 Results — "Experimental results demonstrate that X ..."

순서: (a) 헤드라인 → (b) baseline → (c) 설정 → (d) 주 지표 → (e) 부 지표 → (f) 추가 평가

| 단계 | 대표 표현 |
|---|---|
| (a) 헤드라인 | "**Experimental results demonstrate that** X **remarkably / effectively / markedly** enhances ..." (3/4), "Our experimental results demonstrate ParaSuit's ability to significantly enhance ..." |
| (b) baseline | 범주 + 이름 + 인용: "search strategy (Learch) [22], state-pruning strategy (Homi) [10], SMT-solving strategy (AAQC) [42], and parameter-tuning strategy (SymTuner) [8]" |
| (c) 설정 | "We integrated X with each technique and evaluated ... on **15 open-source C programs ranging from 4K to 48K branches**" — 대상 개수와 **규모 범위**를 쓴다 (8K–251K LoC, up to 77K LOC) |
| (d) 주 지표 | "**In terms of** branch coverage, ... covered **35.5% more** branches on average **than** the techniques alone." |
| (e) 부 지표 | "**Regarding** bug-finding / **For** bug detection / **In the realm of** bug detection, ... identified ten bugs in total, **whereas** ... seven" / "**while ensuring that none** detected by the pure techniques were missed" |
| (f) 추가 평가 | "**We further demonstrate** X's efficacy **by comparing it with** a random seeding approach, **and its generality by applying** X to concolic testing ..." (3/4) / FSE26은 원인 설명: "This improvement **is attributed to** ..." |

- Abstract와 달리 **baseline을 실명으로** 쓰고, baseline별 수치를 자세히 쓴다.
- (f)의 추가 평가 문장은 §4의 RQ(비교, Generality)와 1:1로 대응한다.

### I8 Contributions — 3 bullets

- 도입: "**Contributions.** We summarize our contributions below/as follows:" (bold run-in)
- bullet 이름표: ASE26 *Underexplored problem / New technique / Extensive evaluation*, FSE26 *Observation / New Technique / Evaluation*. ICSE25·ICSE26은 이름표가 없다.

| bullet | 역할 | 대표 표현 |
|---|---|---|
| 1 | 관찰 / 문제 / 최초성 | "We show that SOTA ... do not effectively cover ..., **motivating the need for** ..." / "We demonstrate that **approximately 80%** of inputs ... are coverage-equivalent" / "**To our knowledge, ParaSuit is the first** self-configuring technique ..." |
| 2 | 기술 | "**Our core / key / main technical contribution is a specialized / customized / domain-specific algorithm that** ..." (3/4) |
| 3 | 평가 + 공개 | "**We demonstrate / show the effectiveness of** X **by integrating it into** N ... **and comparing** their performance with the original ... across N programs. **We make X publicly available**." (4/4, URL은 각주 또는 인라인) |

- bullet 2의 동사는 I6과 같아야 한다. ICSE25는 P4에서 "groups, ranks, selects", bullet 2에서 "groups, prioritizes, chooses"로 동의어가 섞였다. 따라 하지 말 것.

---

## 4. 문체 특징

### 4.1 단락 첫머리

| 역할 | 첫머리 표현 |
|---|---|
| I1 | `<Domain> [cites] is a ...` |
| I2 | In practice, ... / However, due to ... / A key component of ... |
| I3 | However, ... / Yet, despite ... / Although ..., we observed that ... / However, our observation is that ... |
| I4 | In this paper, we present ... |
| I5 | A major challenge is ... / However, a key challenge is ... |
| I6 | To overcome / address this challenge, we (have) developed ... / First, ... It then ... |
| I7 | Experimental results demonstrate that ... |
| I8 | Contributions. |

### 4.2 인용 분포 (단락별 고유 문헌 수)

| ID | P1 | P2 | P3 | P4 | P5 | P6 | P7 | P8 |
|---|---|---|---|---|---|---|---|---|
| ICSE25 | 6 | 14 | 6 | 0 | 5 | 0 | | |
| ICSE26 | 9 | 16 | 9 | 19* | 0 | 3 | 0 | |
| ASE26 | 17 | 6 | 0 | 9 | 0 | | | |
| FSE26 | 21 | 5 | 2 | 0 | 0 | 0 | 3 | 0 |

\* Figure 1 캡션 인용 포함. 배경(I1–I2) > Gap(I3) > Results(I7)이고, Proposal·Algorithm·Contributions는 0이다.

### 4.3 기타

| 항목 | 관찰 |
|---|---|
| 주어 | **we**: observed, define, present, developed, integrated / **도구명**: begins by, enters, improves |
| 시제 | 분야·기법 설명은 현재, SOTA 진전은 현재완료(have significantly improved, has seen marked improvement), 실험 결과는 과거(covered, identified)이고 "Experimental results demonstrate"만 현재 |
| 관찰 표현 | we observed that / our observation is that / we evaluate how effectively ... |
| 강조 부사 | remarkably, markedly, significantly, substantially, undoubtedly, paradoxically, Unfortunately, Consequently |
| 신조어 표기 | 따옴표("seeding", "coverage-equivalent", "parameter values") 또는 약어 정의(option-related branches (OBs)) |
| forward ref | Gap·Challenge → "Section 2", Gap의 주장 → "Section 4.5" (ICSE26) |
| **넣지 않는 것** | 로드맵 단락, RQ 목록, 수식, Threats, Related Work식 장문 비교 |

---

## 5. 수식·알고리즘·플로트

- **수식·기호 없음** (4/4). 기호는 §2에서 처음 도입한다. 약어만 정의한다: option-related branches (OBs), probabilistic context-free grammars (PCFGs).
- **알고리즘 없음** (4/4).
- **플로트는 ICSE26 Figure 1 하나뿐**이다. (a) 선행 연구가 쓴 KLEE 명령줄, (b) SymTuner의 파라미터 공간(JSON)을 나란히 보여 주는 코드형 그림이다.
  Gap 단락에서 "Figure 1-(a)", "Figure 1-(b)"로 하위 그림을 나눠 참조하고, 같은 그림을 §2.2와 §4.1에서 재사용한다.

---

## 6. 섹션 간 연결

| Intro 요소 | 대응 위치 | 관계 |
|---|---|---|
| I1 동작 원리 | §2.1 형식화 + Algorithm 1 | Intro의 서술(choose → execute → fork)을 §2.1이 튜플과 알고리즘으로 형식화한다 |
| I2 SOTA 범주 | §2.1 끝 (ASE26), §5 Related Work | 같은 범주명(search strategy, state-pruning, ...)을 Related Work 주제 단락에서 다시 쓴다 |
| I3 신조어·수치 | Abstract M3/M3′, §2.2 Table 1 | 수치를 공유한다. FSE26 80.3%/81.0% = Table 1, ASE26 7.9% = Table 1 (단 Abstract는 8.0%) |
| I3 Figure 1 (ICSE26) | §2.2, §4.1 Baselines | 한 그림을 Intro, §2.2(기존 접근 설명), §4.1(Kleefix = Figure 1-(a))에서 재사용한다 |
| I4 제안 문장 | Abstract M1 | 같은 정의를 쓰고 수식어만 바꾼다 |
| I5 도전과제 수치 | §2.3 Table 2 | FSE26은 Intro 19,729 groups / 388 inputs, §2.3 17,567·13,143 sets / 387 inputs로 집계 기준이 달라 값이 다르다. 맞추는 편이 안전하다 |
| I6 단계 이름 | Abstract M6, §3.1 Overview, Conclusion, Contributions bullet 2 | 같은 동사·같은 순서를 유지한다 |
| I7 baseline·수치 | §4.1 Baselines, §4.2~ 결과, Abstract M8 | 수치를 공유한다. 추가 평가 문장이 §4의 RQ와 대응한다 |
| I8 bullet 1 / 2 / 3 | §2.2 / §3 / §4 + Data Availability | bullet 순서가 논문 섹션 순서와 같다 |

---

## 7. 템플릿

```text
[I1] <Domain> [cites] is a <representative|mainstream> software testing <method|technique> that <goal>.
     <동작 원리 3–4문장: This method ... More specifically, ... In particular, ...>
[I2] In practice, <Domain> faces two open challenges: <A> and <B>. The former ... The latter ...
     Recent advances have significantly improved <...>. These include <category1> [..], <category2> [..], and <category3> [..], among others.
[I3] However, our observation is that <SOTA> still <fail to ...|produce "<term>">. In this work, we define <term> as <definition>.
     <Why undesirable>. As shown in Section 2, <prior work [x]> <only N%>. Consequently, <negative consequence>.
[I4] In this paper, we present <Tool>, a novel <complementary> approach that <...> without prior knowledge, thereby <goal>.
     The core idea is to <idea>. (opt.) Our hypothesis is that <...>.
[I5] (opt.) However, a key challenge is the sheer scale of <X>. As reported in Section 2, <N ...>.
     Even when <restricting ...>, <still ...>. Thus, <consequence>.
[I6] To address this challenge, we developed a specialized algorithm that iteratively <V1> ..., <V2> ..., and <V3> ....
     (또는) First, <Tool> <initial stage>. It then iteratively performs three stages: (1) <S1>, which ...; (2) <S2>, which ...; and (3) <S3>, which ....
     By repeating these stages, <Tool> produces <...> tailored to each <program>.
[I7] Experimental results demonstrate that <Tool> markedly enhances <...>. We integrated <Tool> with <category (Name) [..]>, ...
     and evaluated it on <N> <programs> ranging from <a> to <b> <LoC>. In terms of <metric>, ... <x%> more ... than ....
     Regarding <metric2>, ..., whereas .... We further demonstrate <Tool>'s efficacy by comparing it with <...>, and its generality by applying it to <...>.
[I8] Contributions. We summarize our contributions below:
     • Observation: We show that <SOTA> <limitation + number>, motivating the need for <...>.
     • New technique: We present <Tool>, .... Our core technical contribution is a specialized algorithm that <V1>, <V2>, and <V3> ....
     • Evaluation: We demonstrate the effectiveness of <Tool> by integrating it into <N> <techniques> and comparing ... across <N> <programs>. We make <Tool> publicly available.
```

---

## 8. 작성 체크리스트

- [ ] 본문 단락 4–7개 + Contributions, 700–1,000 words이고 로드맵 단락이 없는가
- [ ] 첫 문장이 "<Domain> [cites] is a ... software testing method/technique ..."인가
- [ ] SOTA를 범주명 + 인용 묶음으로 나열하고, 칭찬으로 끝내 다음 단락의 However로 넘어가는가
- [ ] Gap에서 신조어를 "In this work, we define ..."로 정의하고, §2를 forward ref한 수치로 뒷받침했는가
- [ ] Gap에서 가장 가까운 선행 연구를 이름으로 지목했는가
- [ ] Proposal 첫 문장이 "In this paper, we present X, a novel ... approach that ..."인가
- [ ] 도전과제가 있으면 규모 수치 → "To address this challenge, we developed a specialized algorithm"으로 이어지는가
- [ ] 알고리즘 단계 동사/이름이 Abstract·§3.1·Conclusion·Contributions bullet 2와 같은가
- [ ] Results에 baseline(범주+이름), 벤치마크 개수·규모 범위, 주/부 지표 수치, 추가 평가(비교·일반성)가 있는가
- [ ] Contributions가 관찰/기술/평가 3 bullets이고, 2번은 "Our core technical contribution is ...", 3번은 공개 URL로 끝나는가
- [ ] Proposal·Algorithm·Contributions 단락에 인용이 없는가
- [ ] 수치가 Abstract·§2·§4와 일치하는가

---

## 부록 A. 원문 (단락·역할 태그)

열 경계에서 잘린 문장 끝과 하이픈 누락은 원문 PDF로 복원했고, 단락 사이에 끼어든 그림·알고리즘·각주 텍스트는 제거했다.

**ICSE25 — TopSeed**

> **[P1 · I1 Domain]** Symbolic execution [1], [2], [3], [4] is a representative software testing method designed to automatically generate promising inputs that increase code coverage or trigger bugs in a target program. This method replaces program inputs with symbolic variables and explores distinct paths by executing the program both concretely and symbolically with these variables. More specifically, symbolic execution cycles through three core processes: choosing, executing, and forking a program state from a set of states maintained during its testing period. In particular, if the selected state encounters a branch condition containing the symbolic variables, the forking process checks whether both sides of the condition are satisfiable through the SMT solver [5], [6]. If both sides are satisfiable, it forks the state into two independent states. Through these iterative processes, when the state reaches the endpoint of the program, symbolic execution systematically generates an input by solving the conjunction of the accumulated symbolic branch conditions.
>
> **[P2 · I2 SOTA]** In practice, the forking process in symbolic execution faces two open challenges: state explosion and high constraint-solving costs. The former denotes the exponential increase in the number of states to be maintained during testing as the number of branch conditions in the program grows, complicating the decision of which state to explore first. The latter refers to the cost of checking the feasibilities of both sides of each branch using the SMT solver, which consumes the majority of the total testing budget. Recent advances in symbolic execution have significantly improved its performance by addressing these challenges through various state-of-the-art techniques. These include search strategies [4], [7], [8], [9], [10], [11], state-pruning strategies [12], [13], [14], [15], state-merging strategies [16], [17], and constraint-solving cost reduction strategies [18], [19], among others.
>
> **[P3 · I3 Gap]** However, these recent techniques have typically demonstrated their effectiveness without considering “seeding”. When given a seed, the seeding process initializes program states for exploration without the need for costly feasibility checks on each branch encountered during the regeneration of the seed. Seeding offers an advantageous starting point for state exploration and effectively reduces the cost of checks, thus serving as a complementary approach to various independent symbolic execution techniques. Unfortunately, this complementary factor has often been overlooked in state-of-the-art symbolic execution techniques. Existing techniques have predominantly shown their capabilities assuming no initial seeding [10], [11], [15] or have only demonstrated effectiveness with a predefined seed corpus [19], [20], [21].
>
> **[P4 · I4 Proposal + I5 Challenge + I6 Algorithm]** In this paper, we present TopSeed, a novel seeding approach designed to enhance diverse symbolic execution techniques from scratch, thereby maximizing their performance. Our method iteratively selects seeds from inputs generated during symbolic execution on the target program, without relying on a predefined seed corpus. A major challenge is the vast number of candidate seeds—often tens of thousands for real-world programs—which complicates the selection of promising seeds. To overcome this challenge, we have developed a customized online learning algorithm. This algorithm iteratively groups candidate inputs, ranks each group, and selects a promising seed from the top-ranked group. It also continuously updates two probabilistic distributions related to group ranking and seed selection, leveraging the data accumulated during symbolic execution.
>
> **[P5 · I7 Results]** Experimental results demonstrate that TopSeed remarkably enhances three advanced symbolic execution techniques: search strategy [11], state-pruning strategy [15], and constraint-solving strategy [18]. For our evaluation, we applied TopSeed to each technique and evaluated its performance against these techniques operating without seeding across 17 open-source C programs, ranging from 8K to 251K LoC. In terms of branch coverage, the techniques integrated with TopSeed covered 35.5% more branches on average than the techniques alone. Regarding bug-finding, the integrated techniques identified ten bugs in total, whereas the techniques without seeding detected seven of these bugs. We further demonstrate TopSeed’s efficacy by comparing it with a random seeding approach, and its generality by applying TopSeed to concolic testing [1], [3], a significant variant of dynamic symbolic execution.
>
> **[P6 · I8 Contributions]** Contributions. We summarize our contributions below:
> - We introduce a new synergistic approach that automatically selects promising seeds for enhancing arbitrary symbolic execution techniques further from scratch.
> - We present a learning-based algorithm that continuously groups the inputs, prioritizes the groups, and chooses a seed from a high-priority group based on data accumulated while interacting with any symbolic execution technique.
> - We demonstrate the effectiveness of TopSeed by applying it to three symbolic execution techniques and comparing their performance with the original techniques across 17 open-source C programs. We make our tool, TopSeed*, publicly available.

**ICSE26 — ParaSuit**

> **[P1 · I1 Domain]** Symbolic execution [15, 16, 38, 73] is undoubtedly one of the prominent software testing methods, actively researched in both academia and industry [14, 39, 40]. Its primary goal is to efficiently generate valuable test-cases that cover hard-to-reach execution paths in the target program or reveal hidden bugs within a time budget. To achieve this, symbolic execution translates program inputs into symbolic variables, runs the target program with those variables, accumulates symbolic branch conditions, and generates test-cases that satisfy these conditions using an SMT solver [30, 37].
>
> **[P2 · I2 SOTA]** However, due to the need to gather symbolic branch conditions and generate test-cases via the SMT solver, symbolic execution faces two well-known open challenges: the path-explosion problem and the high cost of constraint solving. In response to these challenges, various techniques have been proposed, including search strategy [19, 44, 57, 93], path-pruning [8, 22, 90, 91], constraints solving [54, 60, 78, 81], and state-merging [3, 55, 74, 82]. As a result, the effectiveness of modern symbolic execution tools incorporating these techniques has seen marked improvement.
>
> **[P3 · I3 Gap (사용자 부담)]** Yet, despite their notable performance enhancements, it has paradoxically become more challenging for users to utilize symbolic execution tools effectively. This challenge stems from the need for users to determine the "parameter values" that influence the effectiveness of these tools to achieve the desired testing outcomes. Specifically, given a target program, users choose which parameters to use from the total parameters provided by a symbolic execution tool, and then assign a suitable value to each selected parameter. Unfortunately, the number of adjustable parameters in practical symbolic execution tools, like KLEE [14], exceeds a hundred, including boolean, string, and integer types. Thus, adjusting these parameter values for testing each program imposes a considerable burden on users. This burden often leads users to settle for the default parameter settings offered by symbolic execution tools. For example, many previous works [22, 23, 35, 87] have depended on the parameter settings in Figure 1-(a) provided by the original authors of KLEE. Other works [54, 57, 69, 90] have manually adjusted only a handful of parameters to effectively test the program.
>
> **[P4 · I3 Gap (기존 기법의 한계)]** Although recent techniques have aimed to effectively tune either a specific parameter [18, 44] or multiple parameters [20], given the importance of parameter tuning for symbolic execution tools, they are not self-configuring: they cannot dynamically select which parameters to tune for each target program, and even for each manually chosen parameter, they sample a value from a fixed, predefined set of candidate values that is specific to that parameter and remains unchanged across programs. For example, SymTuner [20] relies on manually defined parameter spaces to adjust multiple parameters of symbolic execution. Figure 1-(b) illustrates SymTuner’s hand-crafted parameter spaces, constructed by selecting 20 parameters from over a hundred available for tuning and defining 5 to 10 possible candidate values for each. As we show in Section 4.5, effective parameters and their value ranges vary greatly depending on the target program. Therefore, these non-self-configuring techniques fail to realize the true benefits of parameter tuning for symbolic execution, highlighting the importance of program-aware parameter tuning. Without such self-configuration, for each program, users must manually select relevant parameters and assign plausible values for each chosen parameter, adding complexity.
>
> **[P5 · I4 Proposal + I6 Algorithm]** We present ParaSuit, a new self-configuring approach that autonomously selects suitable parameters and determines their values in a program-aware way from scratch, thereby maximizing the performance of symbolic execution. To eliminate the need for user intervention, ParaSuit begins by automatically extracting all available parameters from the abstract syntax tree (AST) of the symbolic execution tool’s source code and assessing the potential impact of each parameter through interactions with the tool. Once this extraction stage is complete, ParaSuit enters two iterative stages: parameter selection and value sampling. In the selection stage, ParaSuit assigns a score to each parameter using a customized scoring function that captures both its ability to reach rarely explored branches and its synergy with others, selecting the most promising ones for tuning. In the sampling stage, ParaSuit collects data by systematically exploring and evaluating diverse values for the selected parameters. Based on the collected data, ParaSuit constructs sampling spaces and assigns their probabilities for each selected parameter. It then samples parameter values according to these probabilities and runs the symbolic execution tool on the target program using these values. The results from each run are added to the accumulated dataset. As these two stages repeat, ParaSuit continually refines the dataset, enabling it to provide increasingly effective parameter values tailored to the target program.
>
> **[P6 · I7 Results]** Our experimental results demonstrate ParaSuit’s ability to significantly enhance the performance of symbolic execution tools when integrated. This improvement is evident in both branch coverage and the identification of unique bugs. We built ParaSuit atop KLEE [14], a well-engineered symbolic execution tool replete with diverse parameters. For our evaluation, we used 12 open-source C programs and compared ParaSuit against two baselines: KLEE with manually tuned parameter values (as shown in Figure 1(a)) and the state-of-the-art Symtuner [20], a non-self-configuring method that utilizes user-defined spaces (as illustrated in Figure 1(b)). In terms of branch coverage, ParaSuit outperformed the non-self-configuring method by 25.8% and the manual tuning approach by a substantial 97.4%. In the realm of bug detection, ParaSuit identified 11 unique bugs, outperforming the next best method, which found only seven. Furthermore, the results highlight the efficiency of ParaSuit through comparisons with three generic value sampling algorithms and demonstrate its generality by applying it to another dynamic symbolic execution tool, CREST [29].
>
> **[P7 · I8 Contributions]** Contributions Our contributions are summarized as follows:
> - To our knowledge, ParaSuit is the first self-configuring technique for tuning symbolic execution parameters from scratch in a program-aware manner without any user intervention.
> - Our key contribution is to develop a customized algorithm that, without any prior knowledge, automatically identifies program-specific effective parameters and derives suitable values through iterative refinement informed by symbolic execution feedback.
> - We demonstrate the effectiveness of ParaSuit by comparing it against both a manual approach and a state-of-the-art non-self-configuring approach across 12 open-source C programs. We make the implementation of ParaSuit publicly accessible: https://github.com/unknownicse2026/parasuit

**ASE26 — Orbis**

> **[P1 · I1 Domain (+ I2 난제)]** Symbolic execution [5, 6, 20, 38] is a sophisticated software testing method that automatically generates test-cases, achieving high code coverage of the target program and uncovering diverse hidden bugs. To generate such test-cases, this method maps program inputs into symbolic variables and systematically explores each program path, which consists of exercised symbolic branch conditions containing these variables. Specifically, symbolic execution follows an iterative process that selects, executes, and forks a “state” from the total set of states, which are continuously updated during testing. In particular, due to this fork process, which splits a state into two separate states when both sides of a symbolic branch condition are feasible using the SMT solver [15, 17, 37], symbolic execution faces two notorious challenges: the state-explosion problem [1, 3, 10, 22, 43] and the high cost of SMT solving [24, 30, 34, 39, 42].
>
> **[P2 · I2 SOTA + I3 Gap]** Although state-of-the-art techniques [8, 10, 22, 39, 41, 42] aim to address these challenges of symbolic execution and have remarkably enhanced its performance, we observed that these recent techniques still fail to effectively execute the core functionalities of the program. Since a program’s core functionalities are typically implemented as program options, we evaluate how effectively these techniques cover branches related to program options. In this work, we newly define option-related branches (OBs) as branches associated with specific options, meaning they can be reached by utilizing these options. However, as demonstrated in Section 2, four independent state-of-the-art techniques for symbolic execution—search heuristic [22], state-pruning [10], SMT solving cost reduction [42], and external parameter tuning [8]—exhibited unsatisfactory performance. Despite their advancements, these techniques covered only 7.9% of the targeted total OBs across open-source C programs, leaving a significant portion of program functionalities untested.
>
> **[P3 · I4 Proposal + I6 Algorithm]** In this paper, we present Orbis, a new complementary approach for existing symbolic execution techniques that guides their exploration toward maximizing OB coverage without prior knowledge. By doing so, Orbis improves both total branch coverage and bug-finding capability. First, Orbis automatically extracts useful data (e.g., options, option-related branches) by comparing dynamic execution traces with and without each option. It then iteratively performs three stages: (1) Construct, which builds a target option argument by estimating the potential of each option and stochastically combining them; (2) Guide, which sets the technique’s initial states to steer exploration toward branches influenced by the constructed argument; and (3) Update, which refines the argument’s potential based on generated test-cases and feeds back more promising arguments and states into symbolic execution. In addition, Orbis leverages this updated information to reduce SMT-solver calls, further enhancing efficiency.
>
> **[P4 · I7 Results]** Experimental results demonstrate that Orbis effectively guides four distinct state-of-the-art techniques for symbolic execution toward maximizing OB coverage: search strategy (Learch) [22], state-pruning strategy (Homi) [10], SMT-solving strategy (AAQC) [42], and parameter-tuning strategy (SymTuner) [8]. We integrated Orbis with each technique and evaluated its effectiveness on 15 open-source C programs ranging from 4K to 48K branches. In terms of coverage, the Orbis-guided techniques covered 323.0% more option-related branches, leading to a 112.1% increase in total branch coverage compared to their standalone versions. For bug detection, Orbis enabled the pure techniques to discover an average of five additional unique bugs while ensuring that none detected by the pure techniques were missed. We further evaluated Orbis by comparing it with three state-of-the-art fuzzers specialized in testing program options [26, 44, 45], and assessed its generality by integrating it with concolic testing [9, 13], a widely used variant of dynamic symbolic execution.
>
> **[P5 · I8 Contributions]** Contributions. We summarize our contributions below:
> - Underexplored problem: We show that state-of-the-art symbolic execution techniques do not effectively cover option-related branches, motivating the need for techniques that systematically guide symbolic execution toward option-related branches.
> - New technique: We introduce Orbis, a novel technique that enables diverse symbolic execution methods to maximize OB coverage. Our core contribution is a specialized algorithm that iteratively constructs target option arguments, sets the symbolic executor’s initial states to focus on these arguments, and refines their potential while simultaneously reducing SMT-solving invocations based on data accumulated during testing.
> - Extensive evaluation: We demonstrate the effectiveness of Orbis by integrating it with four distinct symbolic execution techniques and comparing their performance with the pure techniques across 15 open-source C programs. We make Orbis publicly available: https://doi.org/10.5281/zenodo.21767392.

**FSE26 — RSFuzz**

> **[P1 · I1 Domain]** Grammar-based fuzzing is a mainstream software testing technique to effectively increase code coverage and find subtle bugs [2, 22, 29, 34, 37–39, 42]. This technique uses a grammar specifying the input format of the target program under test, and aims to automatically generate highly-structured inputs by iteratively applying production rules in the grammar. Unlike mutation-based fuzzing [6, 7, 13, 32], which is another major fuzzing method that relies on initial seed inputs to generate new inputs, grammar-based fuzzing can produce valid inputs from the specified grammar that pass the syntax parsing stage without requiring initial seed inputs. As a result, it has been actively studied for testing programs with complex input formats such as JavaScript [22, 30, 35, 43], JSON [18, 20, 34, 37], and even for grammar generation itself [5, 14–16].
>
> **[P2 · I2 SOTA]** A key component of grammar-based fuzzers is determining which production rules to apply from a grammar (e.g., context-free grammar) to generate useful inputs. More specifically, these fuzzers need to decide the sequence of production rules for each input, represented as a derivation tree. Some basic grammar-based fuzzers, such as Grammarinator [21], randomly select these rules as a cost-effective strategy. More recent fuzzers [37, 38, 47] adopt more sophisticated methods: Soremekun et al. [37] use probabilistic context-free grammars (PCFGs), where the selection probability of each rule is learned offline from a set of inputs. It is widely recognized that intelligently selecting production rules is crucial for the performance of grammar-based fuzzers, since the input space defined by the grammar is typically infinite [30, 37, 38].
>
> **[P3 · I3 Gap]** However, our observation is that both random and probabilistic grammar-based fuzzers often generate a substantial number of "coverage-equivalent" inputs. In this work, we define an input as coverage-equivalent if it executes the same set of lines as a previously generated one, even when its concrete values differ. Generating such inputs is undesirable, as they are less likely to expose new bugs or cover previously unseen code regions. As shown in Section 2, when testing real-world JavaScript engines, 80.3% of the total inputs produced by the random fuzzer [21] were coverage-equivalent. Similarly, the probabilistic fuzzer [37], which utilizes a learned PCFG, generated 81.0% unproductive inputs. Consequently, these fuzzers tend to spend valuable testing time generating inputs that contribute little to uncovering new bugs or exploring additional code regions.
>
> **[P4 · I4 Proposal]** In this paper, we present RSFuzz, a novel approach that enhances grammar-based fuzzers by preventing the generation of coverage-equivalent inputs during testing. The core idea is to iteratively identify recurrent sequences of grammar production rules, defined as sequences of production-rule applications that repeatedly appear across multiple coverage-equivalent inputs during fuzzing. Since every generated input has its own sequence of applied production rules explaining how it was produced, our hypothesis is that examining this information allows us to effectively identify patterns associated with the generation of coverage-equivalent inputs. By pinpointing these patterns, RSFuzz ensures that such sequences are not reapplied during fuzzing.
>
> **[P5 · I5 Challenge]** However, a key challenge is the sheer scale of coverage-equivalent inputs. As reported in Section 2, when the fuzzer generated 100,000 inputs on real-world JavaScript benchmarks, grouping inputs by identical line coverage resulted in about 19,729 distinct groups, each corresponding to a potential source of recurrent sequences. Even when focusing only on the 200 largest groups, each group still contained over 388 inputs on average. Thus, identifying why these inputs are coverage-equivalent requires analyzing hundreds of production rule sequences within each group.
>
> **[P6 · I6 Algorithm]** To address this challenge, we developed a specialized algorithm that iteratively collects informative data (e.g. coverage, derivation trees) from inputs generated by the fuzzer, groups inputs by code coverage, selects key groups, and captures the recurrent sequences responsible for executing the same code regions within each selected group by abstracting their derivation trees into simplified symbol sequences. By repeating these stages, RSFuzz produces recurrent sequences tailored to each program and its grammar, thereby improving the efficiency of grammar-based fuzzing.
>
> **[P7 · I7 Results]** Experimental results demonstrate that RSFuzz markedly enhances the performance of existing grammar-based fuzzers in terms of crash-finding capability and line coverage. We integrated RSFuzz with a random fuzzer [21], a probabilistic fuzzer [37] and a grammar-coverage based fuzzer [18]. To evaluate its effectiveness, we tested RSFuzz on 12 real-world benchmarks, each with up to 77K LOC, using four input formats: JavaScript, JSON, CSV, and Markdown. The results indicate that when integrated with RSFuzz, the random, probabilistic, and grammar-coverage based fuzzers were able to exclusively detect 121, 46, and 17 crashes having distinct stack traces, respectively, which were not found without RSFuzz. Furthermore, integration of RSFuzz improved line coverage by 6.0% for the random fuzzer, 4.8% for the probabilistic fuzzer, and 3.0% for the grammar-coverage based fuzzer. This improvement is attributed to RSFuzz reducing the proportion of coverage-equivalent inputs generated by the random, probabilistic, and grammar-based fuzzers by averages of 23.3% and 28.7%, and 14.9%, respectively, across our benchmark suite.
>
> **[P8 · I8 Contributions]** Contributions. We summarize our contributions as follows:
> - Observation: We demonstrate that approximately 80% of inputs generated by existing grammar-based fuzzers are coverage-equivalent, repeatedly executing the same set of lines.
> - New Technique: We present RSFuzz, a complementary technique that enhances grammar-based fuzzers by automatically identifying factors associated with coverage-equivalent inputs. Our main technical contribution is a domain-specific algorithm that selects key groups from numerous coverage-equivalent input groups and derives recurrent sequences that should not be applied in certain orders, thereby reducing the likelihood of generating such inputs.
> - Evaluation: We show the effectiveness of RSFuzz by integrating it into three grammar-based fuzzers and comparing their performance with the original fuzzers on 12 real-world programs. We make our tool (RSFuzz) publicly available.
