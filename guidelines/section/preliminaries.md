# Preliminaries — guidelines 4편 분석

[skeleton.md](skeleton.md)의 하위 문서. §2 Preliminaries를 하위절 → 단락 단위로 분석한다.
논문에서 **기호·수식·알고리즘이 처음 등장하는 섹션**이므로 §5에서 표기 규칙을 자세히 다룬다.
수식과 알고리즘은 PDF 페이지 이미지로 직접 확인했다. 원문 발췌는 부록 A에 실었다.

---

## 0. 핵심 규칙

1. Preliminaries는 **~970 words, 하위절 2–3개**다. 순서는 **2.1 배경 형식화 → 2.2 한계(Limitation / Existing Approaches) → (2.3 Goal)**이고, 배경이 ~46%, 한계·목표가 ~54%다.
2. 2.1은 핵심 객체를 **튜플로 정의**하고 **Algorithm 1(일반 알고리즘)**을 줄 번호를 따라 설명한다. 제안 기법이 쓸 인자를 미리 넣어 두고 **"For now, let us set aside ..."**로 설명을 미룬다.
3. 2.2는 **관찰 → 정밀 정의 → 예제 → Table 1 측정 → 단순 대안의 실패** 순이다. Intro Gap 단락의 수치는 여기서 나온다.
4. 마지막 단락은 **"These observations/limitations motivate ..."**로 §3에 넘기면서 성공 기준이나 도전과제 (1)(2)를 제시한다.
5. 수식은 최소한으로 쓴다. 기호는 **"영어 명사 (기호)"**로 도입하고, display 수식은 0–1개이며 번호를 붙이지 않는다. 설명은 수식보다 **알고리즘·표·구체 예제**에 기댄다.

---

## 1. 분량

| ID | 하위절 | 단어 수 (하위절별) | 단락 수 | 평균 단락 길이 | 플로트·수식 |
|---|---|---|---|---|---|
| ICSE25 | A. Symbolic Execution / B. Seeding for Symbolic Execution | 977 (397 / 580) | 8 (3 / 5) | 122 | Algorithm 1, 2 · Table I · display 1 |
| ICSE26 | 2.1 SE and Its Parameters / 2.2 Existing Parameter Tuning Approaches (+ **Goal.** 단락) | 976 (490 / 336 + 150) | 7 (3 / 3 + 1) | 139 | display 1 (Intro Figure 1 재사용) |
| ASE26 | 2.1 Symbolic Execution / 2.2 Limitation of Symbolic Execution | 1,006 (540 / 466) | 9 (5 / 4) | 112 | Algorithm 1 · Table 1 · Figure 1 (코드) |
| FSE26 | 2.1 Basic Grammar-based Fuzzing / 2.2 Limitation / 2.3 Goal | 922 (352 / 217 / 353) | 10 (4 / 2 / 4) | 92 | Algorithm 1 · Table 1, 2 · 코드형 display 4 |
| **평균** | **2–3개** | **~970** | **~9** | **~116** | |

- 단어 수는 [skeleton.md](skeleton.md) §1.2와 같은 방식으로 셌다 (산문만, 표·알고리즘 제외).
- Introduction(평균 ~134 words/단락)보다 단락이 짧다. 알고리즘 줄 해설이나 예제가 짧은 단락으로 끊기기 때문이다.

---

## 2. 구조

### 2.1 하위절 유형과 단락 역할

| 하위절 유형 | 내용 | 출현 |
|---|---|---|
| **P-A 배경 형식화** | 핵심 객체 정의 + Algorithm 1 + 예제 + SOTA 대응 | 4/4 (항상 §2.1) |
| **P-B 한계 / 기존 접근** | 관찰 + 신조어 정밀 정의 + 예제 + Table 1 측정 + 단순 대안 실패 | 4/4 |
| P-C Goal / 마무리 | 목표 형식화, 핵심 아이디어, 도전과제 규모, §3으로 넘기는 문장 | 독립 2/4 (ICSE26 Goal 단락, FSE26 §2.3), 마무리 단락 2/4 (ICSE25, ASE26) |

단락 역할 기호:

| 기호 | 역할 |
|---|---|
| **D** | 핵심 객체 정의 (튜플) |
| **W** | Algorithm 1 해설 (줄 번호 따라가기) |
| **E** | 구체 예제 (입력값, 코드, 문법) |
| **M** | 메커니즘 / SOTA 대응 (기존 기법이나 제안 기법이 쓸 장치가 Algorithm 1의 어디에 놓이는지) |
| **O** | 관찰 + 신조어 정의 |
| **T** | 표로 한계 측정 |
| **N** | 단순 대안의 실패 |
| **G** | 목표 / 도전과제 / §3으로 넘기는 마무리 |

### 2.2 논문별 배치

| ID | §2.1 | §2.2 | §2.3 / 마무리 |
|---|---|---|---|
| ICSE25 | D → W(훅) → W | M(+수식) → M → O+N(Algorithm 2) → T+N | G |
| ICSE26 | D → W(산문) → M+E | O → M(Manual) → M+N(User-configured) | G(+수식) |
| ASE26 | D → W(훅) → W → W+E → M | O → E(Figure 1) → T+N | G |
| FSE26 | W(훅) → E(문법) → E(유도 트리) → M(PCFG) | O+E → T | G+E → G → T(Table 2) → G |

**정형 순서:** D → W → E → M → O → E → T → N → G. 순서가 뒤집힌 경우는 없고, 논문마다 일부를 생략할 뿐이다.

- ICSE26만 Algorithm 1 없이 산문으로 동작을 설명한다. 이 논문의 Algorithm 1은 §3의 제안 기법이다.
- ICSE25의 §II-B는 제목이 "Seeding for Symbolic Execution"이지만, 앞 두 단락은 메커니즘(M)이고 뒤 세 단락이 한계(O·T·N)다.

### 2.3 하위절 유형별 비중

| ID | 배경 (P-A) | 한계 (P-B) | Goal (P-C 독립) |
|---|---|---|---|
| ICSE25 | 41% | 59% (메커니즘 단락 포함) | — |
| ICSE26 | 50% | 34% | 15% |
| ASE26 | 54% | 46% (마무리 단락 포함) | — |
| FSE26 | 38% | 24% | 38% |
| **평균** | **~46%** | **~41%** | (2편 평균 ~27%) |

---

## 3. 단락별 분석

### P-A 배경 형식화 (§2.1)

#### D — 핵심 객체를 튜플로 정의

| ID | 문장 |
|---|---|
| ICSE25 | The main aim of symbolic execution is to automatically generate inputs that trigger bugs or increase code coverage for a target program. To do so, symbolic execution iteratively selects, executes, and updates so-called "program states". **We define a program state as a triple (stmt, m, Φ), where** 'stmt' **represents** the next statement to be executed, 'm' **denotes** a symbolic memory mapping ..., **and** 'Φ' **indicates** a path condition, a sequence of symbolic branch conditions exercised so far in the state. |
| ICSE26 | Symbolic execution aims to generate test-cases that cover diverse execution paths of the target program. ... **Each state consists of three elements:** the next statement (stmt) to be executed, a symbolic store (store) which maps program inputs to symbolic variables, and a path condition (Φ), a conjunction of symbolic branch conditions. |
| ASE26 | **We define a single state as a tuple of three elements:** (1) the next statement to execute (stmt), (2) a symbolic memory (M) that maps each concrete variable to a symbolic variable, and (3) a path condition (Φ) capturing a sequence of exercised symbolic branch conditions. |
| FSE26 | (튜플 정의 없음. Algorithm 1부터 시작) |

- 틀: **목적 한 문장 → "To do so, X iteratively selects, executes, and updates so-called "states"" → "We define a state as a triple (a, b, c), where a represents ..., b denotes ..., and c indicates ..."**
- 원소 설명 동사를 represents / denotes / indicates로 바꿔 가며 쓴다.
- 분야 용어는 처음 쓸 때 so-called와 따옴표로 감싼다: so-called "program states".

#### W — Algorithm 1 해설

- **도입:** "Algorithm 1 **describes / details** a generic / basic X algorithm. It **takes / accepts** four inputs: A (a), B (b), C (c), and H (h)."
- **훅 미루기** (3/3, Algorithm 1이 있는 논문 전부):
  - "**For now, let us set aside the last input**, seed, and the associated function, Feasible; **their roles will be explained in Section II-B.**" (ICSE25)
  - "**For now, we set aside the last two inputs**, Arg and S_P, which will be explained later; general symbolic execution techniques [5, 7, 10, 22] typically test the target program without taking Arg and S_P as input (i.e., Arg=∅, S_P=∅)." (ASE26)
  - "**For now, let us ignore the last argument**, RS, which will be explained later." (FSE26)
- **줄 번호 따라가기:** "At lines 2–3, the algorithm initializes S and I, two sets representing states and inputs, as a singleton set and an empty set, respectively. After the initialization, Algorithm 1 repeats the loop at lines 4–17 until ..." / "At line 5, ..." / "(lines 11–12)"
- **생략 명시:** "For simplicity, the details of how each statement updates the state are omitted."
- **마무리:** "..., at which point it returns the set I of generated inputs." / "Finally, Algorithm 1 returns ..." / "In summary, performing symbolic execution entails ..." (ICSE26, 산문 해설)
- 분량: ICSE25 ~250 words, ASE26 ~330 words, FSE26 ~100 words.

#### E — 구체 예제

- ASE26: "For example, if the concrete argument (Arg) is "-bc" and the SMT solver returns (Arg′ = "-R") as a model of Φ, the resulting test case (t) is "-bc -R"."
- FSE26: 9개 생성 규칙으로 된 JSON 문법 𝔾_J → 가능한 입력 "[]", "[[]]", "[true]" → 유도 트리 → PCFG 확률 예 `Value → (20%) "true" | (70%) "false" | (10%) ""`
- ICSE26: KLEE 파라미터를 상태 원소에 하나씩 대응시킨다. "The "max-solver-time" parameter, **linked with the first element, stmt**, ... The "sym-args" parameter, **tied to the second element, store**, ..."
- 예제 값은 따옴표나 타자체로 쓴다.

#### M — 메커니즘 / SOTA를 Algorithm 1에 대응

- **SOTA를 Algorithm 1의 줄에 대응** (ASE26):
  "Recent advancements in symbolic execution have significantly improved its effectiveness **based on Algorithm 1**. For instance, search strategies [22, 41], **corresponding to the Choose function at line 5**, ... Some techniques—**such as the Solve function at line 10**—... an orthogonal technique [8] ... (**the Execute procedure**)."
- **제안 기법이 쓸 메커니즘을 미리 설명** (ICSE25 §II-B): Feasible 함수로 seeding이 SMT 호출을 건너뛰는 원리를 display 수식과 함께 설명한다.
- **기존 확장 기법 소개** (FSE26): "A more recent and sophisticated approach [37] employs a probabilistic context-free grammar (PCFG) ... By using this learned PCFG, existing methods have successfully generated ..."
- **범위 정의 + 규모** (ICSE26): "In this work, we define parameters as all adjustable factors influencing the performance of symbolic execution." + "KLEE encompasses 148 parameters, including 27 of integer types, 6 of float types, 24 of string types, and 91 of boolean types."

### P-B 한계 / 기존 접근 (§2.2)

#### O — 관찰 + 신조어 정밀 정의

- ASE26: "**Our key observation is that** recent techniques [8, 10, 22, 42] ... still struggle to ... **In this work, we newly define** option-related branches (OBs) as ... **More precisely**, an OB is a conditional branch whose condition contains a (variable, value) pair that is newly defined or updated only when the corresponding option is enabled."
- FSE26: "Current grammar-based fuzzers often generate a large number of coverage-equivalent inputs during testing. **In this work, we define** coverage-equivalent inputs as those that ..."
- ICSE26: "Current primary approaches ... **share a key limitation**: these approaches are not self-configuring with respect to the program under test, as they ..."
- ICSE25: "Despite the clear benefits of seeding, **we observed that** existing techniques typically operate the symbolic executor (Algorithm 1) without seed inputs [11], [15], [18]."
- Intro에서 한 문장으로 정의한 신조어를 여기서 **"More precisely, ..."**로 조작적(operational)으로 다시 정의한다.

#### E — 예제로 개념 보여 주기

- ASE26 (Figure 1, 코드): "Figure 1 illustrates an example of OBs using code snippets from the ls program. **Suppose we execute** ls with the option "-l" (e.g., ./ls -l). **In this case**, the variable "c" is assigned the value "l", which is then used as a branch condition in the if statement at line 5. **We classify this branch as an OB.**"
- FSE26: "For instance, **let us assume that** two inputs, "[]" and "[[]]", execute the same set of lines despite having distinct values. **In this case, we classify** the second input as coverage-equivalent, since ..."
- 틀: `"Suppose / let us assume ... In this case, ... We classify X as <신조어>."`

#### M — 기존 접근을 범주별로 (ICSE26)

- bold run-in 단락: "**Manual Tuning Approach.**" / "**User-configured Tuning Approach.**"
- 각 단락: 무엇을 하는가 → 근거(인용, Figure 1) → 왜 부족한가 ("Note that ...", "In other words, ... posing a critical hurdle to ...")

#### T — Table 1로 한계 측정

| ID | 첫 문장 | 후속 |
|---|---|---|
| ICSE25 | "**Table I displays** the average number of candidate seed inputs generated by the well-known symbolic executor, KLEE [4], **across five open-source C programs over a period of 10 hours**." | "For example, on the gawk program, ..." |
| ASE26 | "**Table 1 shows that** KLEE [5], ..., and four distinct state-of-the-art techniques covered **only 7.9%** of the targeted total option-related branches on average **across the six programs**." | "**Surprisingly**, all symbolic executors except SymTuner even failed to ... **The fundamental reason is that** ... The column "Opt" represents ..." |
| FSE26 | "**Table 1 displays** the percentage of coverage-equivalent inputs among 100,000 generated by random and probabilistic grammar-based fuzzers **across eight real-world programs, ranging from 1.5K to 77K LoC**, ..." | "**Interestingly**, even the probabilistic fuzzer ... **This might stem from** ..." |

- 틀: `"Table 1 shows/displays <지표> by <도구> across <N programs> (<규모·예산>)"` → 전체 수치 → 도구별 수치 → "Surprisingly / Interestingly" 극단 사례 → 원인 ("The fundamental reason is that ..." / "This might stem from ...")
- 측정 대상은 **실험 벤치마크의 일부**(5 / 6 / 8개)이고, 도구는 §4의 baseline과 같다.
- 원인 추정에서만 hedging("might")을 허용한다.

#### N — 단순 대안의 실패

- ICSE25: "**One alternative is to** utilize all generated inputs as seeds for symbolic execution. **However, this naive approach proved unsatisfactory. For instance**, ... approximately 78.4% lower ..." + 무작위 seed 선택을 **Algorithm 2**로 정식화한다.
- ASE26: "Table 1 also highlights that increasing OBs **is non-trivial; merely** using each program option **is insufficient**. For sqlite, ... (41.2% on average), yet achieved only 1.2% OB coverage."
- ICSE26: "Note that manually defining these parameter spaces is as challenging for users as directly selecting parameter values."

### P-C Goal / 마무리

| ID | 형태 | 핵심 문장 |
|---|---|---|
| ICSE26 | **Goal.** 단락 + display 수식 | "The objective of this paper is to ... **We can formally define our goal** ... our goal is to iteratively identify sets of parameters and values **such that** [⋃ Execute(...)] **is maximized within the total budget (time), where** time_s denotes ..." |
| FSE26 | §2.3 Goal (4단락) | "The goal of this paper is to ..., thereby ... The key idea is to ... **Our hypothesis is that** ... Consequently, we define a *recurrent sequence* as ..." → 예제 → "**However**, efficiently identifying "meaningful" recurrent sequences **is far from straightforward in practice**. As shown in Table 2, ... **Even when** restricting attention to ..., **the challenge remains**: ..." → "**These observations highlight a key challenge**: ..." |
| ASE26 | 마무리 단락 | "**These limitations motivate our complementary approach**, which ... **This is feasible because** ... (Pearson 0.902, as demonstrated in Section 4.2). **Our work thus tackles two key challenges: (1)** ..., **and (2)** ..." |
| ICSE25 | 마무리 단락 | "**These observations motivated us to develop** a novel technique that ... **In this work, we define** a "promising" seed **as one that** ..." |

- §2는 항상 **§3으로 넘기는 문장**으로 끝난다: "These observations / limitations motivate(d) ..."
- 넘길 때 다음 중 하나를 함께 준다: **성공 기준 정의**("promising" seed), **도전과제 목록** (1)(2), **목표식**(⋃).
- ASE26은 목표 대리 지표(OB coverage)가 타당한 이유를 §4 결과로 미리 뒷받침한다 ("This is feasible because ... as demonstrated in Section 4.2").

---

## 4. 문체 특징

| 항목 | 관찰 |
|---|---|
| 주어 | 형식화 부분은 **도메인·알고리즘**("Symbolic execution", "Algorithm 1", "the algorithm"), 정의와 관찰은 **we**("We define", "we observed") |
| 시제 | 정의와 알고리즘 동작은 **현재형**("Algorithm 1 selects"), 측정 결과는 **과거형**("covered only 7.9%", "produced about 81.0%") |
| 정의 동사 | We define X as ... / In this work, we (newly) define ... / X represents · denotes · indicates ... / X is defined as a pair of ... / referred to as ... |
| 구체화 | 괄호 안 e.g. / i.e.: "(e.g., int x ↦ α)", "(i.e., Arg=∅, S_P=∅)", "(e.g., Sat(Φ)==true)", "(e.g., load)" |
| 상호 참조 | 뒤로 미루기 ("will be explained in Section II-B", "explained later"), 앞으로 끌어오기 ("as demonstrated in Section 4.2"), 되짚기 ("as described in Section 2.1", "Recall that ...") |
| hedging | 원인 추정에서만 ("This might stem from ...") |
| 인용 | 정의 대상 도메인, 메커니즘의 근거, SOTA 대응, 표 열 머리(도구명 [5]) |
| 도구명 | §2에서는 거의 쓰지 않는다. ICSE26만 마지막 문장에 "our novel approach, ParaSuit"를 한 번 쓴다. 나머지는 "a novel technique", "our complementary approach" |
| **넣지 않는 것** | 제안 기법의 상세, "we propose" 문형, 실험 전체 결과, 번호 붙은 수식 |

---

## 5. 수식·알고리즘·플로트

> 캡션·선 두께·서체·색 같은 시각 디자인 상세와 LaTeX 레시피는 [floats.md](floats.md)에 모아 두었다. 여기서는 이 섹션에 **무엇을** 넣는지를 다룬다.

### 5.1 개수

| ID | Algorithm | display 수식 | 표 | 그림 | 코드형 display |
|---|---|---|---|---|---|
| ICSE25 | 2 (Alg. 1 일반, Alg. 2 단순 대안) | 1 (번호 없음) | Table I | — | — |
| ICSE26 | 0 | 1 (번호 없음) | — | (Intro Figure 1 참조) | — |
| ASE26 | 1 | 0 | Table 1 | Figure 1 (코드 스니펫) | — |
| FSE26 | 1 | 0 | Table 1, 2 | — | 4 (문법, 유도 트리, PCFG 규칙, 유도 순서) |

- **§2에는 번호 붙은 수식이 하나도 없다** (0/4). 번호는 §3에서 다시 참조하는 수식에만 붙는다 (ICSE25 (1)–(3), ICSE26 (1)–(2)는 모두 §3).
- display 수식은 많아야 1개다. 형식화의 주된 수단은 **알고리즘**이다.

### 5.2 기호 체계

| 대상 | 표기 규칙 | 예 | LaTeX |
|---|---|---|---|
| 입력·일반 변수 | 의미 있는 영단어를 이탤릭으로 | pgm, time, seed, inp, tree, stmt | `\mathit{pgm}` |
| 핵심 객체 | 튜플 | (stmt, m, Φ) · (stmt, store, Φ) · (stmt, M, Φ) | `(\mathit{stmt}, m, \Phi)` |
| 논리식 | Φ = 경로 조건, φ = 분기 조건 | (Φ ∧ φ), (Φ ∧ ¬φ) | `(\Phi \land \phi)` |
| 집합 | 대문자 한 글자 | S(states), I(inputs), T(test-cases), B(branches), L(lines) | `S` |
| 누적 집합 | **Total** 접두 CamelCase | TotalI, TotalB, TotalL, TotalT | `\mathit{TotalI}` |
| 갱신·파생 | prime | m′, s′, stmt′, Arg′ | `m'` |
| 변형·초기값 | 아래첨자 | stmt_t / stmt_f, stmt_1 / stmt_2, stmt_true / stmt_false, stmt_0, Φ_0, s_0 | `\mathit{stmt}_t` |
| 시간 조각 | 아래첨자 s | time_s | `\mathit{time}_s` |
| 하이퍼파라미터 | η + 아래첨자, 기본값은 알고리즘 주석에 | η_time (▷ η_time = 120) | `\eta_{\mathit{time}}` |
| 문법 | 칠판체 | 𝔾, 𝔾_J | `\mathbb{G}` |
| 절차·오라클 함수 | small caps | SymbolicExecutor, Feasible, Sat, Model, Execute, Solve, Run, Fuzzing | `\textsc{Feasible}` |
| 보조 함수 | sans-serif 또는 roman | Choose, RandomSample, Generate | `\mathsf{Choose}` |
| 대입·구조 | ← , ⟨ ⟩ , ∅ , ∪ , \ , ∈ | ⟨TotalI, seed⟩ ← ⟨∅, ⟨⟩⟩ | `\gets`, `\langle\rangle` |
| 구체 값 | 따옴표 또는 타자체 | "-bc", "[]", `Start → Array` | `\texttt{}` |

- 함수 서체(small caps / sans-serif)는 논문마다 조금씩 다르다. 대체로 **알고리즘 이름·외부 오라클(SMT 호출 등)은 small caps, 내부 보조 연산은 sans-serif**다. 한 논문 안에서는 일관된다.
- 같은 연구실 논문끼리 기호가 거의 같다 (stmt, Φ, φ, pgm, time, Total*, η). 분야가 달라도(FSE26) pgm, time, Total*, η 식 명명은 유지된다.

### 5.3 기호·수식 도입 방식

1. **영어 명사 + (기호)** — 모든 기호를 처음 쓸 때 이렇게 도입한다 (4/4).
   "a time budget (time)", "a symbolic memory (M)", "a grammar (𝔾)", "parameter values (PV)", "the time budget (time)".
   이후에는 기호만 쓴다.
2. **튜플 정의** — "We define X as a triple (a, b, c), where 'a' represents ..., 'b' denotes ..., and 'c' indicates ..."
3. **함수 정의 + display** — "We define the Feasible function as one that accepts a seed input and returns all path conditions whose feasibility was confirmed ..., **as follows:**"

   ```latex
   \textsc{Feasible}(\mathit{seed}) = \{\Phi_1, \Phi_2, \cdots, \Phi_n\}
   ```

4. **목표를 최적화식으로** — "our goal is to iteratively identify sets of parameters and values **such that** the union of symbolic execution outcomes"

   ```latex
   \textstyle\bigcup_{i=1}^{n} \textsc{Execute}(\mathit{pgm}, \mathit{time}_s, \mathit{PV}_i)
   ```

   "**is maximized within the total budget (time), where** time_s denotes the smaller, individual time allocations within time."
   display 뒤 **"where ... denotes ..."**로 남은 기호를 정의하고 문장을 이어 간다.
5. **즉석 구체화** — 기호 바로 뒤 괄호에 값을 넣는다: "(e.g., int x ↦ α)", "(i.e., Arg=∅, S_P=∅)", "(e.g., seed=⟨⟩)".
6. **수식 없이 말로 정밀 정의** — "More precisely, an OB is a conditional branch whose condition contains a (variable, value) pair that is newly defined or updated only when the corresponding option is enabled." (ASE26)
7. **display 직전에는 콜론** — "as follows:", "as:", "with nine production rules:"
8. **구체 산출물은 수식 대신 타자체 display** — 문법 규칙, 유도 순서, 명령줄 (FSE26, ICSE26)

### 5.4 알고리즘 표기 (Algorithm 1)

| 요소 | 규칙 | 예 |
|---|---|---|
| 캡션 | **분야 과정 이름** | "Symbolic Execution with A Seed Input" / "Symbolic Execution" / "Grammar-based Fuzzing" |
| Input / Output | 영어 명사 + (기호), 마침표 | **Input:** Program (pgm), budget (time), seed input (seed). **Output:** Inputs (I) |
| 절차 선언 | `procedure Name(args)`, 이름은 small caps | procedure SymbolicExecutor(pgm, time, seed) |
| 키워드 | 굵게 | procedure, repeat, until, if, then, else, return |
| 오른쪽 주석 ▷ | 변수 의미, 구조 분해, 하이퍼파라미터 기본값, 원소 형태 | ▷ A set of states / ▷ s = (stmt, m, Φ) / ▷ η_time = 120 / ▷ (v, Φ) ∈ I |
| 루프 종료 | 예산 소진 + 예외 조건 | until time expires (or S = ∅) |
| **훅 인자** | 일반 기법은 비워 두는 인자를 처음부터 넣는다 | seed (ICSE25), Arg, S_P (ASE26), RS (FSE26) |
| 길이 | 8–18줄 | ICSE25 18 · ASE26 16 · FSE26 8 |
| 배치 | §2 시작 근처 페이지 상단 float | |

- **단순 대안도 알고리즘으로 쓴다.** ICSE25 Algorithm 2(Random Seeding Strategy)는 Algorithm 1을 서브루틴으로 호출하며, 이후 §4 baseline RandSeed가 된다.

### 5.5 표·그림

- **Table 1 = 한계 측정.** 캡션은 측정 대상을 서술하는 명사구에 조건을 덧붙인다.
  - "TABLE I: The average number of candidate seed inputs on open-source C programs (time budget: 10h)"
  - "Table 1: Symbolic execution on option-related code regions."
  - "Table 1. The percentage of coverage-equivalent inputs among the total inputs generated during testing."
- 행은 벤치마크 일부(5–8개), 열은 기존 기법(헤더에 인용 번호, 예: KLEE [5]) 또는 입력 포맷 그룹이다. 수치는 %, 천 단위 쉼표, 소수점 1자리다.
- **Table 2 (FSE26) = 도전과제 규모** (#Sets, Avg. Size).
- **Figure 1 (ASE26) = 코드 스니펫.** 줄 번호를 달고 해당 줄(OB)을 색으로 강조한 뒤, 본문에서 "at line 5", "at line 10"으로 짚는다.

---

## 6. 섹션 간 연결

| §2 요소 | 대응 위치 | 관계 |
|---|---|---|
| §2.1 훅 인자 | §3 | 제안 기법이 이 인자를 채운다. ICSE25 seed → §III Algorithm 3이 공급, ASE26 S_P → §3.2 Guide 단계가 생성, FSE26 RS → §3.3 Generate(𝔾, RS) |
| Algorithm 1 | §3 Algorithm 2/3 | 제안 알고리즘이 Algorithm 1을 서브루틴으로 호출한다 (I ← SymbolicExecutor(pgm, time_s, seed), B, T ← Execute(pgm, time_s, Arg_new, S_P)) |
| Algorithm 1 | §4 Generality | 다른 도구로 일반화할 때 Algorithm 1만 갈아 끼운다 (ASE26: "corresponds to replacing the Execute procedure (Algorithm 1)") |
| §2.1 SOTA 대응 | §4.1 Baselines, §5 Related Work | 같은 기법(Learch, Homi, AAQC, SymTuner)이 baseline과 Related Work 범주로 다시 나온다 |
| §2.2 단순 대안 | §4 baseline | ICSE25 Algorithm 2 → §4 RandSeed |
| §2.2 Table 1 | Intro Gap, Abstract M3′ | 같은 수치를 쓴다 (ASE26 7.9%, FSE26 80.3% / 81.0%) |
| §2.2 신조어 정의 | Intro Gap | Intro는 한 문장, §2.2는 "More precisely" 정밀 정의 + 예제 |
| §2.3 목표식 | §3.2 알고리즘 출력 | ICSE26: 목표 ⋃ Execute(...)가 Algorithm 1의 출력 UnionB = ⋃ B와 같다 |
| §2.3 도전과제 | Intro I5, §3.1, §4 ablation | 도전과제 하나마다 §3 단계 하나, §4 ablation 하나가 대응한다 (FSE26 §3.1: "The key novelty ... lies in addressing two significant challenges in the "selecting" and "capturing" steps") |
| 수치 불일치 | — | ICSE25: 본문 "gawk ... 18,512" vs Table I 25,124. FSE26: Intro 19,729 groups vs §2.3 Table 2 17,567·13,143 sets. 따라 하지 말 것 |

---

## 7. 템플릿

```text
## 2 Preliminaries
### 2.1 <Domain> (basics)
[D] The main aim of <domain> is to <goal>. To do so, <domain> iteratively <V1>, <V2>, and <V3> so-called "<objects>".
    We define a <object> as a triple (a, b, c), where a represents ..., b denotes ..., and c indicates ....
[W] Algorithm 1 describes a generic <domain> algorithm. It takes <noun> (a), <noun> (b), and <noun> (h) as input.
    For now, let us set aside the last input, h, which will be explained in Section <x>.
    At lines 2–3, the algorithm initializes .... At line 5, .... For simplicity, the details of ... are omitted.
    This process repeats until the given budget (time) is exhausted, at which point it returns ....
[E] For example, if <a> is "<v1>" and ... returns "<v2>", the resulting <x> is "<v3>".
[M] Recent advancements have significantly improved <domain> based on Algorithm 1.
    For instance, <category> [..], corresponding to the <F> function at line 5, ....

### 2.2 Limitation (of <existing approaches>)
[O] Our key observation is that <SOTA> [..] still <...>. In this work, we define <term> as <...>.
    More precisely, <operational definition>.
[E] Figure 1 illustrates .... Suppose we execute ... (e.g., <cmd>). In this case, .... We classify <x> as <term>.
[T] Table 1 shows that <tools> covered only N% of ... across <N> programs. Surprisingly, ....
    The fundamental reason is that ....
[N] One alternative is to .... However, this naive approach proved unsatisfactory. For instance, ....

### 2.3 Goal (opt.)
[G] The goal of this paper is to <...>. We can formally define our goal as follows: <display>, where <symbol> denotes ....
    However, <...> is far from straightforward in practice. As shown in Table 2, .... Even when ..., the challenge remains: ....
[close] These observations motivate our approach, which .... Our work thus tackles two key challenges: (1) ..., and (2) ....
```

---

## 8. 작성 체크리스트

- [ ] 하위절이 2.1 배경 → 2.2 한계 → (2.3 Goal) 순이고 ~1,000 words인가
- [ ] §2.1에서 핵심 객체를 튜플로 정의하고, 각 원소를 represents / denotes / indicates로 설명했는가
- [ ] Algorithm 1이 일반 알고리즘이고, 제안 기법이 쓸 훅 인자를 "For now, let us set aside ..."로 미뤄 두었는가
- [ ] 모든 기호를 처음 쓸 때 "영어 명사 (기호)"로 도입했는가
- [ ] 알고리즘 해설이 줄 번호를 따라가는가 ("At line N", "lines a–b")
- [ ] 입력값·코드·문법 같은 구체 예제가 있는가
- [ ] 기존 기법이 Algorithm 1의 어디를 바꾸는지(또는 어떤 범주인지) 보였는가
- [ ] §2.2에서 신조어를 Intro보다 정밀하게 다시 정의했는가 ("More precisely, ...")
- [ ] Table 1로 한계를 측정했고, 측정 범위(벤치마크 일부·예산·도구)를 밝혔는가
- [ ] 단순 대안이 왜 부족한지 보였는가 (가능하면 §4 baseline으로 재사용)
- [ ] §2가 "These observations motivate ..." + 성공 기준 / 도전과제 / 목표식으로 끝나는가
- [ ] display 수식은 0–1개, 번호 없음, 앞에 "as follows:", 뒤에 "where ... denotes ..."인가
- [ ] 함수는 small caps(절차·오라클) / sans-serif(보조)로 일관되게 썼는가
- [ ] 본문 수치와 표 수치가 일치하는가 (§6 불일치 사례 참고)

---

## 부록 A. 원문 발췌 (단락·역할 태그)

수식과 기호는 PDF 원문 표기를 따라 옮겼다 (아래첨자는 `_`로 표시).

**ICSE25 — TopSeed**

> **[§II-A · D]** The main aim of symbolic execution is to automatically generate inputs that trigger bugs or increase code coverage for a target program. To do so, symbolic execution iteratively selects, executes, and updates so-called "program states". We define a program state as a triple (stmt, m, Φ), where 'stmt' represents the next statement to be executed, 'm' denotes a symbolic memory mapping from program variables to symbolic variables, and 'Φ' indicates a path condition, a sequence of symbolic branch conditions exercised so far in the state.
>
> **[§II-A · W]** Algorithm 1 describes a generic symbolic execution algorithm. It takes a target program (pgm), a time budget (time), and a seed input (seed) as input. For now, let us set aside the last input, seed, and the associated function, Feasible; their roles will be explained in Section II-B. At lines 2–3, the algorithm initializes S and I, two sets representing states and inputs, as a singleton set and an empty set, respectively. After the initialization, Algorithm 1 repeats the loop at lines 4–17 until the given time budget (time) expires.
>
> **[§II-B · M + 수식]** A seeding process can skip the feasibility checking of the branches associated with a given seed input, thereby significantly reducing the high checking costs [19], [22], [23] introduced by the SMT solver. Specifically, Algorithm 1 bypasses this checking process through the Feasible function at lines 9–10. We define the Feasible function as one that accepts a seed input and returns all path conditions whose feasibility was confirmed (e.g., Sat(Φ)==true) during seed generation, as follows:
>
> &nbsp;&nbsp;&nbsp;&nbsp;Feasible(seed) = {Φ_1, Φ_2, ···, Φ_n}
>
> **[§II-B · T + N]** However, when testing real-world programs, Algorithm 2 faces the challenge of deciding which of the generated inputs (TotalI) to use as seeds. Table I displays the average number of candidate seed inputs generated by the well-known symbolic executor, KLEE [4], across five open-source C programs over a period of 10 hours. For example, on the gawk program, the average number of candidates is 18,512, highlighting the difficulty of intelligently selecting the most promising seed. One alternative is to utilize all generated inputs as seeds for symbolic execution. However, this naive approach proved unsatisfactory. For instance, we observed that applying this method to the grep program resulted in branch coverage that was approximately 78.4% lower on average than the coverage achieved by performing symbolic execution without any seeds.
>
> **[§II-B · G]** These observations motivated us to develop a novel technique that automatically selects promising seeds from candidate inputs generated while performing an arbitrary symbolic execution technique, even without prior knowledge. In this work, we define a "promising" seed as one that enables the symbolic executor to effectively explore branches not yet covered by initializing the executor's program states in a way that increases the likelihood of reaching unseen code segments.

**ICSE26 — ParaSuit**

> **[§2.2 · G + 수식]** **Goal.** The objective of this paper is to automate program-aware tuning of external parameters for symbolic execution. Specifically, for each program, we autonomously select relevant parameters from the complete set and determine their appropriate values without any prior knowledge. We can formally define our goal of maximizing the benefits of tuning external parameters by using the following symbolic execution procedure (Execute), where it takes target program (pgm), time budget (time), and parameter values (PV) as inputs and returns the branch set B covered until time expires. Using this procedure, our goal is to iteratively identify sets of parameters and values such that the union of symbolic execution outcomes
>
> &nbsp;&nbsp;&nbsp;&nbsp;⋃_{i=1}^{n} Execute(pgm, time_s, PV_i)
>
> is maximized within the total budget (time), where time_s denotes the smaller, individual time allocations within time. Ultimately, our novel approach, ParaSuit, eliminates the need for users to manually adjust parameters while achieving the highest branch coverage through fully self-configured parameters.

**ASE26 — Orbis**

> **[§2.1 · W]** Algorithm 1 details the symbolic execution process. It accepts four inputs: the target program (pgm) to test, the time budget (time), a set of concrete arguments (Arg), and a set of promising states (S_P). For now, we set aside the last two inputs, Arg and S_P, which will be explained later; general symbolic execution techniques [5, 7, 10, 22] typically test the target program without taking Arg and S_P as input (i.e., Arg=∅, S_P=∅). At line 2, the algorithm first initializes the set S of states based on S_P. If S_P is empty, S is initialized as a singleton set containing a state (stmt_0, M_0, true). Otherwise, Algorithm 1 replaces S with the set S_P of promising states. At line 3, the set of test-cases (T) is initialized as an empty set.
>
> **[§2.1 · M]** Recent advancements in symbolic execution have significantly improved its effectiveness based on Algorithm 1. For instance, search strategies [22, 41], corresponding to the Choose function at line 5, prioritize selecting the most promising states first from the set S based on predefined criteria. Conversely, state-pruning strategies [10, 11] aim to eliminate redundant states from S by terminating them early. Some techniques—such as the Solve function at line 10—focus on efficiently reducing constraint solving costs [39, 42]. Additionally, an orthogonal technique [8] attempts to automatically tune external parameters of the symbolic execution engine (the Execute procedure). These techniques significantly improve code coverage and facilitate the discovery of subtle bugs, compared to the generic symbolic execution (Algorithm 1).
>
> **[§2.2 · O]** Our key observation is that recent techniques [8, 10, 22, 42] for symbolic execution still struggle to effectively test the core functionalities of the target program, despite their remarkable enhancement. Specifically, since these core functionalities are typically implemented as program options, we evaluate how effectively these state-of-the-art techniques cover branches related to program options. In this work, we newly define option-related branches (OBs) as branches associated with a specific option and reachable by utilizing that option. More precisely, an OB is a conditional branch whose condition contains a (variable, value) pair that is newly defined or updated only when the corresponding option is enabled.
>
> **[§2.2 · G]** These limitations motivate our complementary approach, which guides symbolic execution techniques towards maximizing OB coverage from scratch, thereby improving total branch coverage and bug-finding capability. This is feasible because OB coverage and total branch coverage are strongly correlated in our benchmark suite, with an average Pearson coefficient of 0.902, as demonstrated in Section 4.2. Our work thus tackles two key challenges: (1) automatically extracting OBs without prior knowledge, and (2) effectively guiding symbolic execution techniques toward these branches.

**FSE26 — RSFuzz**

> **[§2.1 · W]** Algorithm 1 describes a basic grammar-based fuzzing algorithm. The algorithm takes four inputs: a program under test (pgm), a time budget (time), a grammar (𝔾), and recurrent sequences (RS). For now, let us ignore the last argument, RS, which will be explained later. The algorithm first initializes a total set of covered lines, TotalL, as an empty set. It then iteratively generates both the input (inp) and the derivation tree (tree) that includes the used production rules from the grammar 𝔾 (line 4), executes the program with the input, and returns the set L of covered lines (line 5). This fuzzing algorithm repeats this process until the given budget is exhausted and finally returns the total set TotalL of lines covered so far.
>
> **[§2.2 · T]** Table 1 displays the percentage of coverage-equivalent inputs among 100,000 generated by random and probabilistic grammar-based fuzzers across eight real-world programs, ranging from 1.5K to 77K LoC, with two input formats: JavaScript and JSON. The random fuzzer [21] (RandF), which randomly applies the production rules of the grammar, yields approximately 80.3% and 84.6% coverage-equivalent inputs while testing the JavaScript and JSON benchmarks, respectively. Interestingly, even the probabilistic fuzzer [37] (ProbF) with the learned PCFG produced about 81.0% and 92.7% coverage-equivalent inputs on average for the JavaScript and JSON benchmarks, respectively. This might stem from the higher sampling probabilities of certain production rules within the PCFG, leading to the generation of many inputs that cover similar code regions.
>
> **[§2.3 · T + G]** However, efficiently identifying "meaningful" recurrent sequences is far from straightforward in practice. As shown in Table 2, when generating 100,000 inputs for the eight benchmark programs, both the grammar-based fuzzers, RandF and ProbF, produced approximately 17,567 and 13,143 sets, respectively, where each set contained inputs covering the same lines. Each set represents a candidate for capturing recurrent sequences, making it practically infeasible to analyze all of them. Even when restricting attention to the top 200 coverage sets containing the largest numbers of coverage-equivalent inputs, the challenge remains: each set still includes, on average, 387 inputs for RandF and 411 for ProbF.
>
> **[§2.3 · G]** Thus, identifying why these inputs are coverage-equivalent requires analyzing hundreds of production rule sequences within each set. These observations highlight a key challenge: identifying appropriate recurrent sequences is particularly difficult.
