# Floats — 그림·표·알고리즘·수식 디자인 분석

[skeleton.md](skeleton.md)의 하위 문서지만, 섹션 문서가 아니라 **논문 전체에 걸친 시각 디자인 규칙**을 다룬다.
각 섹션 문서의 §5는 그 섹션에 **무엇을** 넣는지를, 이 문서는 그것을 **어떻게 보이게** 만드는지를 다룬다.

**측정 방법.** 4편의 모든 플로트를 200–1200 dpi로 렌더링해 하나씩 잘라 보았다. 폰트 이름·크기는 `pdffonts`·PyMuPDF·`pdftotext -bbox`, 색은 픽셀 샘플, 선 두께는 고해상도 픽셀 폭으로 쟀다 (±0.1 pt). §8의 LaTeX 예시는 IEEEtran으로 직접 컴파일해 원 논문과 같은 모양이 나오는지 확인했다.

---

## 0. 핵심 규칙

1. **가이드라인 4편은 모든 플로트를 페이지·단 상단(`[t]`)에 둔다. 우리 논문은 `[h]`를 기본으로, 처음 언급하는 문단 바로 위에 둔다** (§1.3의 우리 논문 규칙). 캡션은 **표는 위, 그림은 아래**다. 본문에서는 항상 "Figure N / Table N / Algorithm N"으로 풀어 쓰고, 문장의 주어로 참조한다 ("Table 5 shows that ...").
2. **표의 시그니처는 세로선이다.** 라벨 열 뒤(또는 나란히 붙인 두 반쪽 사이)에 **이중 세로선 ‖**, 열 그룹 사이에 단일 세로선을 넣고, **바깥 테두리 세로선은 넣지 않는다.** 4편 모두 같다.
3. 표 헤더는 **2단**이다. 위 단은 **도구명(small caps) + [인용]**, 아래 단은 설정·지표(small caps)이고, 그 사이에 `\cline`을 긋는다. 맨 아래에 **Total 행**을 선으로 구분해 둔다. 숫자는 오른쪽 정렬, 천 단위 쉼표, 평균값은 소수 1자리, 부가 값은 괄호("3,198(1)"), 0은 "-"로 쓴다.
4. **강조는 굵게만 쓴다** (색·음영·밑줄 없음). 가장 흔한 방식은 **제안 기법 열 전체를 굵게** 하는 것이다. 다만 4편 모두 표마다 기준이 달랐다. **한 가지 기준을 정하고 본문에 밝힐 것.**
5. **overview 그림은 흑백 상자-화살표 다이어그램**이다. 도구 경계(굵은 둥근 테두리, 테두리를 끊고 들어간 도구명) 안에 단계 상자를 두고, 기존 도구 상자와 **데이터 이름이 붙은 화살표**로 연결한다. 입력은 왼쪽, 출력은 오른쪽이다.
6. **결과 그림은 baseline vs 제안 기법의 대비**로 만든다. 세 편이 두 집합 Venn 다이어그램으로 고유 커버리지를 보여 준다. baseline은 회색·차가운 색, 제안 기법은 노랑·초록 또는 해칭이다.
7. **알고리즘은 4편이 완전히 같은 양식**이다 (ruled 0.8/0.4/0.4 pt, 7–8 pt 본문, `n:` 번호, 굵은 키워드, ▷ 오른쪽 주석, `/* Step k */` 블록 주석).
8. **표·그림·본문 수치는 하나의 산출물에서 만든다.** 4편 모두 표 합계 오류, 본문-표 불일치, 백분율 계산 규약 혼용이 있었다 (§7).

---

## 1. 인벤토리

### 1.1 개수

| ID | 포맷 | 그림 | 표 | 알고리즘 | display 수식 (번호) | 래스터 그림 |
|---|---|---|---|---|---|---|
| ICSE25 | IEEE 2단 | 4 | 10 | 3 | 21 (3) | 0 |
| ICSE26 | ACM sigconf 2단 | 6 | 6 | 2 | 17 (2) | 2 (Fig. 2 overview, Fig. 6 Venn) |
| ASE26 | ACM sigconf 2단 | 3 | 10 | 2 (+ 캡션 없는 절차 1) | 16 (0) | 2 (Fig. 1 코드, Fig. 3 Venn) |
| FSE26 | ACM 저널 1단 | 4 | 6 | 2 | 9 (0) + 번호 붙은 코드형 display 5 | 0 |
| **합계** | | **17** | **32** | **9** | | |

### 1.2 섹션별 분포

| 섹션 | 그림 | 표 | 알고리즘 |
|---|---|---|---|
| §1 Introduction | 1 (ICSE26 설정 예시) | — | — |
| §2 Preliminaries | 1 (ASE26 코드) | 4 (한계 측정) | 3 (일반 알고리즘) + 1 (ICSE25 단순 대안) |
| §3 Our Approach | 5 (overview 4, 예제 1) | 2 (ICSE25 정의표) | 5 (메인 4, 보조 1) |
| §4 Experiments | 10 | **26 (81%)** | — |

### 1.3 배치와 폭

- **모든 플로트가 `[t]`다** (4/4). 페이지 중간·하단 배치는 없다.
- **IEEE 2단 (ICSE25):** 여러 패널로 된 그림 2개와 가장 큰 결과표(Table V) 1개만 양단 폭(`figure*`·`table*`)이다. 나머지는 한 단 폭이다.
- **ACM sigconf (ICSE26, ASE26):** **모든 플로트가 한 단 폭이다.** 큰 표도 `\resizebox{\columnwidth}`로 줄인다.
- **ACM 저널 1단 (FSE26):** 텍스트 폭의 0.79–1.0이다. 뒤로 갈수록 표가 넓어지고 글자가 작아진다.
- 같은 단에 표 두 개나 표와 그림을 위아래로 쌓는 경우가 많다 (ICSE25 p9, ASE26 p3·p8·p9).

> **우리 논문 규칙 (사용자 지정, 가이드라인보다 우선)**
>
> 1. 그림·표·알고리즘은 **`[h]`를 기본**으로 쓰고, 소스에서 **처음 언급하는 문단 바로 앞**에 둔다. 그러면 출력에서도 언급하는 문단 바로 위에 온다.
> 2. 페이지 경계나 크기 때문에 플로트가 **언급보다 뒤로 밀리면 위치를 조정해 항상 언급보다 위에 오게** 한다.
>    - 먼저 플로트를 소스에서 한두 문단 앞으로 옮긴다.
>    - 그래도 밀리면 앞쪽 페이지·단의 `[t]`로 바꾼다.
>    - 크기가 원인이면 줄이거나(열·행 정리, 한 단 폭 유지) 나눈다.
> 3. 컴파일할 때마다 렌더링에서 **플로트가 첫 언급보다 위(같은 단 위쪽, 또는 앞 단·앞 페이지)**에 있는지 확인한다. LaTeX 로그의 `'h' float specifier changed to 'ht'` 경고는 밀렸다는 신호다.

### 1.4 제작 도구 (PDF 폰트로 추정)

| 대상 | 도구 | 근거 | 본문 폰트와의 관계 |
|---|---|---|---|
| overview 다이어그램 | **PowerPoint** (벡터 PDF 또는 PNG) | Times New Roman, DengXian, Cascadia Code, MS-PMincho(원 숫자 ①②③)가 들어 있음 | IEEE는 Times라 맞음. ACM(Libertine)에서는 어긋남 |
| 그래프 | **matplotlib** | DejaVu Sans·Serif (matplotlib 기본) | 어긋남 |
| 그래프 (FSE26) | matplotlib + `usetex` | Computer Modern (CMR·CMTT·CMCSC) | 서체는 다르지만 small caps 도구명, 타자체 벤치마크명으로 본문 표기 규칙은 맞춤 |
| Venn | matplotlib-venn (원 크기가 개수에 비례하지 않음) | DejaVu / 래스터 | |
| 코드 | minted(Pygments 기본 색) / listings / 일반 verbatim | Inconsolata(ACM), Courier(IEEE) | 맞음 |
| 유도 트리 | LaTeX 직접 조판 | Inconsolata + 벡터 선 | 맞음 |

---

## 2. 캡션

### 2.1 포맷별 캡션 모양

| 포맷 | 표 라벨 | 그림 라벨 | 굵기 | 서체·크기 | 정렬 | 끝 마침표 |
|---|---|---|---|---|---|---|
| IEEE (ICSE25) | `TABLE I:` (대문자, 로마 숫자) | `Fig. 1:` | 일반 | Times, 본문과 같은 10 pt | 한 줄이면 가운데, 여러 줄이면 양쪽 정렬 | 없음 (Table V만 있음) |
| ACM sigconf (ICSE26, ASE26) | `Table 1:` | `Figure 1:` | **캡션 전체 굵게** | Libertine, 본문과 같은 9 pt | 같음 (여러 줄이면 하이픈 허용) | 있음 (논문마다 예외 1개) |
| ACM 저널 (FSE26) | `Table 1.` + 1em 간격 | `Fig. 1.` | 일반 | Biolinum(sans) 9 pt (본문 10 pt) | 같음 | 표는 있음. 그림은 명사구면 없음, 문장이면 있음 |
| 알고리즘 (4편 공통) | **Algorithm 1** Title | | 라벨만 굵게, 제목은 일반 | 본문 크기 | 왼쪽 정렬, 콜론 없음 | 없음 |

- 대부분 템플릿 기본값이다. ICSE25만 IEEEtran 기본(라벨을 따로 한 줄에 쓰는 small caps 캡션)을 `caption` 패키지로 바꿔 **"TABLE I: 본문"** 한 줄 형태로 썼다 (§8 레시피).
- 하위 그림 캡션 "(a) ...": ICSE26은 굵게 8 pt, 각 하위 그림 아래 가운데. FSE26은 Libertine 8 pt. 본문에서는 **"Figure 1-(a)"**로 참조한다.

### 2.2 캡션 문장

- **명사구 한 문장**으로, 무엇을 · 누가 · 어디서 · 조건 순서다.
  - "Average branch coverage achieved by four baselines under three different settings across 17 benchmarks."
  - "The average number of candidate seed inputs on open-source C programs (time budget: 10h)"
  - "Number of bugs detected by ParaSuit and baselines."
  - "Impact of Construct stage in Orbis." / "Efficacy evaluation of each stage in TopSeed"
  - "Overview of RSFuzz" / "The overview of Orbis."
- **도구명은 small caps**로 쓴다.
- **약어·셀 형식 정의** — FSE26만 체계적으로 한다:
  - "*Cover*: The number of covered lines. *#Inputs*: The number of generated inputs (Values are shown in millions (M)), Δ%: The percentage change ..."
  - "R: Crashes detected by the random fuzzer. P: ... R+RS, P+RS and T+RS: Crashes detected when RSFuzz is integrated."
  - ASE26 Table 10: "... Format: unique branches(bugs)"
  - 나머지는 괄호 안 값, "-", 굵게 표시의 의미를 캡션에서 **설명하지 않는다** → 우리는 본문에서 밝힌다.
- **우리 논문 규칙 (IEEE): 캡션은 제목(명사구)만 쓴다** — "Overview of \tool{}", "Running example (p02742)", "Repair rate and skeleton loss of each repairer on our benchmark (\%)". 4편 중 3편(ICSE25·ICSE26·ASE26)이 이렇게 쓰고, 정의를 넣은 것은 FSE26뿐이다. 약어·기호·열 이름·"--"·굵게의 의미는 **그 플로트를 처음 설명하는 본문 문단**에서 밝힌다. 캡션 끝에 마침표를 찍지 않는다 (ICSE25).

### 2.3 본문 참조 문형

| 대상 | 동사 |
|---|---|
| 표 | Table N **shows / demonstrates / presents / displays / reveals / reports / illustrates** that ... |
| 그림 | Figure N **illustrates / shows / displays / provides an overview of / presents** ... |
| 알고리즘 | Algorithm N **describes / details / offers a detailed description of / provides** ... |
| 수식 | "Equation (1)" (ICSE26) / "the equation (3)" (ICSE25) / "(1)" (FSE26) |
| 하위 그림 | "Figure 1-(a)" (대부분), "Figure 1(a)"가 섞임 → 한 가지로 통일 |
| 복수 | "Tables 7 and 8 show that ..." |

- 캡션이 "Fig."여도 본문에서는 "Figure"로 쓴다 (4/4).
- **처음 참조하는 문장이 곧 그 플로트의 핵심 주장이다.** 예: "Table V shows that integrating TopSeed into each of the four baselines significantly increased branch coverage ..." (결과 서술 패턴은 experiments.md에서 다룬다)

---

## 3. 표

### 3.1 역할별 유형

| 유형 | 위치 | 예 | 전형적 형태 |
|---|---|---|---|
| **한계 측정** | §2.2 | ICSE25 I, ASE26 1, FSE26 1·2 | 벤치마크 일부(5–8개) × 기존 도구, %, 강조 없음 |
| **정의표** | §3 | ICSE25 II (features), III (policies) | `Feature ‖ Description` 2열, 설명은 마침표 있는 완전한 문장, 행마다 선 |
| **벤치마크** | §4.1 | ICSE25 IV, ICSE26 1, ASE26 2, FSE26 3 | **2–3단으로 접은 표**(반쪽 사이 ‖), Program-version, LoC(K), #Branches, 강조 없음 |
| **주 결과** | §4.2 | ICSE25 V, ICSE26 2, ASE26 3·4, FSE26 5 | 벤치마크 행 × (도구 × 설정) 열, 2단 헤더, Total 행, **제안 기법 열 굵게** |
| **버그** | §4.3 | ICSE25 VI, ICSE26 3, ASE26 5, FSE26 4 | 버그가 나온 벤치마크만(3–7행), "-" = 0, 최댓값·동률 굵게 |
| **ablation** | §4.4 | ICSE25 VII, ICSE26 4·5, ASE26 6–9, FSE26 6 | 변형을 열로 ("TopSeed − (Group)", RandP, RandConst), 셀은 "커버리지(버그)" |
| **일반성·외부 비교** | §4.5+ | ICSE25 VIII, ASE26 10 | "branches(bugs)" 셀, 도구 쌍 비교 |
| **하이퍼파라미터** | §4 | ICSE25 IX | 위 단 헤더 = 파라미터(η), 아래 단 = 값, 그룹마다 최댓값 굵게 |
| **분석** | §4 | ICSE26 6 (Top-5 순위), ICSE25 X (평균) | 순위·평균 1열 |

### 3.2 선 (rule)

**가로선 — 두 계열이 있다.**

| 계열 | 논문 | 구성 |
|---|---|---|
| booktabs | ICSE25, FSE26 | 위·아래 굵은 선(~0.6 pt), 헤더 아래 가는 선(~0.36 pt). **ICSE25는 헤더 아래에 가는 선을 두 줄**(`\midrule\midrule`) 긋는다 |
| 균일 `\hline` | ICSE26, ASE26 | 모든 가로선이 같은 굵기(~0.4 pt, 축소 후 0.24–0.36 pt) |

공통:

- **Total 행 위에 선 1개**를 긋는다 (ICSE25 Table VI만 이중선).
- 2단 헤더 사이에 **`\cline`**을 긋는다. `\cline`은 여백이 없으므로 아래 단 첫 칸에 `\rule{0pt}{2.6ex}`를 넣어 글자가 선에 붙지 않게 한다. 그룹마다 끊는 `\cmidrule`이 아니라 세로선을 가로지르는 연속선이다.
- 그룹이 있는 표(프로그램별 여러 행, 입력 포맷별)는 **그룹 사이에 가는 선**을 긋는다. 일반 결과표는 데이터 행 사이에 선을 긋지 않는다.

**세로선 — 연구실 시그니처.**

| 위치 | 선 | 출현 |
|---|---|---|
| 라벨 열(Benchmark / Program) 뒤 | **이중 ‖** | ICSE25 모든 표, ICSE26 모든 표, ASE26 대부분 (6·8·10만 단일) |
| 접은 표의 반쪽 사이 | **이중 ‖** | 4/4 (벤치마크 표) |
| 도구 계열·지표 블록 사이 | **이중 ‖** | FSE26 4–6, ASE26 9 |
| 같은 계열 안의 도구·설정 그룹 사이 | 단일 \| | 4/4 |
| 그룹 안 (설정 사이, 지표 사이) | 없음 | 대부분 (ASE26 Table 2만 모든 열 사이) |
| 바깥 테두리 | **없음** | 4/4 |

- booktabs와 세로선을 함께 쓰면 세로선이 가로선에서 살짝 끊긴다. 원 논문들은 이를 그대로 두었다.

### 3.3 헤더

```text
┌──────────────┬───────────────────────────────┬───────────────────────────────┐
│              ║        KLEE [4] +             │        LEARCH [11] +          │   ← 그룹: 도구명(small caps) + [인용] (+ "+")
│  Benchmark   ║───────────────────────────────┼───────────────────────────────│   ← \cline (연속)
│  (multirow)  ║  BASE   RANDSEED   TOPSEED    │  BASE   RANDSEED   TOPSEED    │   ← 하위: 설정·지표 (small caps)
╞══════════════╬═══════════════════════════════╪═══════════════════════════════╡   ← (ICSE25) 이중 가는 선
│ sqlite-3.33.0║  4,281    4,053   **6,448**   │  5,112    5,251   **5,944**   │
│ ...          ║                               │                               │
├──────────────╫───────────────────────────────┼───────────────────────────────┤   ← Total 위 선
│ Total        ║ 18,736   18,924  **24,913**   │ 16,908   18,593  **23,342**   │
└──────────────┴───────────────────────────────┴───────────────────────────────┘
```

- **라벨 열 머리**("Benchmark", "Program")는 `\multirow`로 헤더 두 단을 걸친다.
- **그룹 머리 = 도구명 + 인용**: "KLEE [4] +", "Learch [22]", "ProbF [37]". 인용 앞에 공백을 넣는다 ("CREST[28]"처럼 붙인 경우도 있지만 섞여 있음).
- **하위 머리**:
  - 설정: Base / RandSeed / TopSeed, Pure / Orbis
  - 지표: Opt / OB, *Cover* / # Inputs / Δ%, OB / B (Bug)
- **ablation 머리**: "TopSeed / − (Group, Learn)", "RSFuzz / − (C, S)" 두 줄, 또는 RandP / AllP / SymP 같은 변형 이름
- **단위**는 헤더 둘째 줄 괄호 안에 쓴다: "Saved Time (sec)", "Hit Ratio (%)", "Programs (LoC)". 같은 단위를 셀에 반복하지 않는다 (ASE26 Table 9는 반복).
- 헤더 굵기: ICSE25는 굵게, ACM 논문은 일반이다.

### 3.4 셀과 숫자

| 항목 | 규칙 | 예 |
|---|---|---|
| 정렬 | 이름은 왼쪽, 숫자는 오른쪽, 그룹 라벨(multirow)은 가운데 | |
| 벤치마크명 | 이름-버전 | sqlite-3.33.0, xorriso-1.5.2, Jsish-2.0 (77.4K) |
| 천 단위 | 쉼표 | 18,736 / 6,109.4 |
| 소수 | **5회 평균은 소수 1자리**, 개수는 정수 | 2,148.0 / 10,372.8 |
| 큰 수 | K(LoC), M(입력 수) | 251K, 77.4K, 116.7M |
| 백분율 | 소수 1자리 + %, 부호 없음 | 21.2%, 94.3% |
| 부가 값 | 괄호 (공백 없음이 다수) | 3,198(1) / 6,109(0) / 10,372.8 (0) |
| 0·해당 없음 | "-" | (ASE26·FSE26 일부는 "(0)" 또는 Total에서 "0") |
| 요약 행 | Total / total / Average, 선으로 구분, 라벨은 가운데 또는 왼쪽 | |

- 4편 모두 이 규칙을 대체로 따르지만, 한 논문 안에서도 공백·쉼표 누락("1046.8", "1003")과 "-"/"(0)" 혼용이 있었다.

### 3.5 강조

| 방식 | 의미 | 사용 |
|---|---|---|
| **제안 기법 열 전체 굵게** | "우리 것" (실제로 항상 최고일 때) | ICSE25 V·VII·VIII, ICSE26 2·4·5, ASE26 3·4·6·7·8, FSE26 5 |
| 행마다 최댓값 굵게 (동률 포함) | 최고 | ICSE26 3, ASE26 5, ASE26 9 (버그 열) |
| 쌍마다 큰 값 굵게 | with vs without | FSE26 4, ICSE25 VI (본문 행) |
| 그룹마다 최댓값 굵게 | 파라미터별 최적 | ICSE25 IX |
| 모든 값 굵게 | (의미 없음) | FSE26 1 |
| 없음 | 기술·벤치마크·분석 표 | ICSE25 I·IV·X, ICSE26 1·6, ASE26 1·2·10, FSE26 2·3·6 |

- **색·음영·밑줄·이탤릭 강조는 한 번도 쓰지 않는다** (32/32).
- 어느 논문도 캡션에서 굵게의 의미를 설명하지 않는다.
- **권장:** 주 결과·ablation 표는 "제안 기법 열 굵게", 버그 표는 "행 최댓값(동률 포함) 굵게"로 고정하고, 그 표를 처음 설명하는 본문 문단에 "bold marks ..."로 밝힌다.

### 3.6 크기와 글자 크기

| ID | 표 글자 크기 (본문 대비) | 크기 범위 |
|---|---|---|
| ICSE25 | 5.9–8.6 pt (대부분 7–8, 본문 10) | 2–19행 × 2–13열 |
| ICSE26 | 6–7 pt (본문 9) | 5–14행 × 5–7열 |
| ASE26 | 5.1–6.2 pt (본문 9) | 5–17행 × 9–12열 |
| FSE26 | 4.9–7.7 pt (본문 10) | 5–17행 × 6–22열 |

- **모든 표를 `\resizebox`로 단(또는 텍스트) 폭에 맞춘다.** 그래서 글자 크기가 표마다 다르다.
- 5 pt 이하는 인쇄에서 읽기 어렵다 (FSE26 Table 6 4.9 pt). **6 pt 아래로 내려가면 표를 나눌 것.**
- **짧고 넓은 표는 접는다**: 벤치마크 목록은 4편 모두 2–3단으로 접고 반쪽 사이에 ‖를 넣는다. ASE26은 짧은 ablation 표(6, 8)도 두 반쪽으로 접는다.

---

## 4. 그림

### 4.1 Overview 다이어그램 (4/4)

| 요소 | 규칙 | 예 |
|---|---|---|
| 크기 | 한 단 폭의 0.8–1.0, 높이 59–94 pt (가로:세로 ≈ 3–4:1) | ICSE25 242×94 pt, ASE26 213×59 pt |
| 색 | **흑백** (FSE26만 강조색 1개: 금색 #FFC000) | |
| 서체 | Times New Roman 5–9 pt (본문보다 작음). 단계 이름은 굵게(ICSE25) | |
| 도구 경계 | **굵은(2배) 둥근 테두리**, 불규칙한 외곽도 허용. **도구명이 위 테두리를 끊고** 들어간다 (small caps 또는 굵게) | ICSE25, ICSE26, ASE26 |
| 단계 상자 | 둥근 사각형, 흰 바탕, 가는 검은 선 (FSE26만 각진 상자) | Extract / Construct / Guide / Update |
| 하위 상자 | 단계 상자 안의 전략 (각진 작은 상자) | Exploration·Exploitation, Score·Select, Explore·Exploit |
| 단계 번호 | 원 숫자 ①②③ (ICSE25), 또는 없음 | "① Data Gathering" |
| 외부 도구 | 경계 밖의 별도 상자 | Symbolic Executor, Grammar-based Fuzzer |
| 화살표 | 가는 실선 + 채운 삼각 머리. 직각 꺾임 또는 곡선 피드백. **화살표마다 주고받는 데이터 이름** | "Inputs", "Seed", "parameter values", "covered branch set", "an option argument" |
| 아이콘 | 입력 = 문서 아이콘("C", "JS"), 출력 = 트리·체인 아이콘 + 라벨 | "program", "total coverage", "Total recurrent sequences" |
| 흐름 | 입력은 왼쪽, 출력은 오른쪽. 도구 ↔ 외부 도구는 위아래 루프 | |
| 캡션 | "Overview of X" / "The overview of X" | |

- 상자 이름은 **§3의 단계 이름과 글자 하나까지 같다** ([approach.md](approach.md) §0 규칙 2).

### 4.2 코드 그림·리스팅

| 형태 | 예 | 디자인 |
|---|---|---|
| 캡션 있는 코드 그림 (색 있음) | ICSE25 Fig. 4, ASE26 Fig. 1 | minted의 **Pygments 기본 색**(키워드 초록 굵게 #008000, 타입 #B00040, 문자열 #BA2121, 함수 파랑 #0000FF, 주석 청록 이탤릭). 줄 번호는 왼쪽 밖, 작은 serif. ASE26은 위아래 선(`frame=lines`)을 긋고 **핵심 줄을 연한 청록(#E0FFFF) 바탕**으로 강조 |
| 캡션 있는 코드 그림 (흑백) | ICSE26 Fig. 1 (a)(b) | 고정폭 7 pt, 테두리·색 없음, 생략은 `... (24 more parameters)` |
| 캡션 없는 인라인 리스팅 | ICSE26 help 출력·C++, ASE26 help 출력·사례 연구 코드 | 문장 끝 콜론 뒤에 놓는다. 위아래 가는 선만 있거나 없음. 키워드만 굵게 또는 문자열만 진빨강(#b41e1e) |
| 생략 표기 | 4/4 | 코드 주석으로: `/* Total 19 case statements and 12 functions */`, `/* ... Define other 48 case statements ... */` |

### 4.3 그래프

| 종류 | 예 | 디자인 요점 |
|---|---|---|
| **두 집합 Venn** (연구실 단골, 3/4) | ICSE25 Fig. 3, ICSE26 Fig. 6, ASE26 Fig. 3 | baseline vs (baseline + 제안 기법). **원 크기는 같고 개수에 비례하지 않는다.** baseline은 회색(#A9A9A9) 또는 연파랑(#B2D4EC), 제안 기법은 연두(#9ACD32) 또는 연노랑(#FFFFB2), 겹침은 섞인 색. 영역마다 개수(괄호 안에 버그 수). 패널 제목은 벤치마크명. 원 아래 라벨은 small caps. 패널 4–8개를 한 줄 또는 2×4로 |
| 막대 (그룹·누적·정렬) | ICSE26 Fig. 3(a)·4, FSE26 Fig. 3·4 | **baseline은 회색 단색, 제안 기법은 파스텔 + 해칭(///)** (FSE26). 검은 막대 테두리. 눈금 라벨은 45–60° 회전. 범례는 축 위쪽 한 줄 |
| 선 | ICSE25 Fig. 2 | 시간축 변화. 계열마다 다른 마커. 0 기준선. 회색 격자 |
| 범위 (dumbbell) | ICSE26 Fig. 3(b)·5 | 최소-최대를 선 + 원 마커로, 기본값은 점선 |
| 축 끊기 | FSE26 Fig. 4 | x축 왼쪽을 "//" 표시로 끊어 차이를 확대 |

공통 규칙 (지킬 것):

- **패널마다 벤치마크 이름을 제목으로 단다.** (a)(b) 라벨 대신 쓰기도 한다 (ICSE25, ASE26).
- **축 제목에 단위를 괄호로**: "Time (sec)", "Equivalent Ratio(%)", "# of Covered Lines", "# Tuned Params".
- 격자는 연회색 점선 또는 실선이다. 범례는 축 위쪽이나 안쪽 빈 곳에 두고 데이터를 가리지 않게 한다.
- **도구명 표기를 본문과 맞춘다**: FSE26은 범례에 small caps, 벤치마크명에 타자체를 썼다.

원 논문의 약점 (따라 하지 말 것):

- **그림 안 글자가 너무 작다**: 4–6 pt (ICSE25 Fig. 2 ≈ 4 pt). 최소 6–7 pt를 지킬 것.
- **matplotlib 기본 서체(DejaVu)가 본문과 다르다.** `usetex` 또는 본문 서체(Times/Libertine)를 지정할 것.
- **색의 의미가 그림마다 다르다** (ICSE26: 초록이 Fig. 3에서는 Symtuner, Fig. 4에서는 "선택됨", Fig. 5에서는 gcal). baseline·제안 기법 색을 논문 전체에서 고정할 것.
- 범례가 데이터를 가리거나(ICSE25 Fig. 2), 색 의미를 설명하지 않는 그림(ICSE26 Fig. 4)이 있다.

> **우리 논문 규칙 (사용자 지정, 2026-10-16)**
>
> 1. 실험 결과는 **글과 표만으로 채우지 않고 그래프를 섞는다.** 문제별 상세 수치처럼 정확한 값이 중요한 결과는 표로 두고, 분포·변형 비교·선호처럼 크기나 경향을 보여 주는 결과는 그래프로 그린다. 그래프로 보여 준 수치는 본문에서 다시 나열하지 않는다.
> 2. 그래프는 **pgfplots**로 그린다. 본문과 같은 글꼴이 들어가고 벡터로 나온다. 좌표는 `summarize.py`가 `tables.tex`의 `% FIG-<name>` 절로 쓰고, `fill_tables.py`가 `% rows:fig<name>` 표시 사이에 채운다. 손으로 수치를 넣지 않는다.
> 3. 색은 논문 전체에서 고정한다. \tool{}는 해칭한 연파랑(`histra`), 변형은 연회색, 대조군과 baseline은 진회색이다. skeleton loss 구간은 연한 색(손실 적음)에서 진한 색(손실 많음)으로 간다. 스타일은 preamble의 `\pgfplotsset`에 있다.
> 4. 한 단 폭, `[h]`, 캡션은 제목만 쓴다. 눈금 글자는 `\scriptsize`, 축 제목은 `\footnotesize`, 단위는 괄호에 넣는다. 값 라벨은 막대 안에 들어가지 않으면 생략하고 본문에서 말한다.

### 4.4 예제 그림

- **FSE26 Fig. 2**: 유도 트리 두 개를 LaTeX로 직접 조판했다. Inconsolata 노드, 벡터 선, (a)(b) 라벨, 두 패널 사이에 세로 구분선이 있다.
- 본문 중간의 캡션 없는 트리 display도 같은 스타일이다. 단, 선 길이가 그림과 본문에서 달랐다.

---

## 5. 알고리즘

4편이 사실상 같은 양식이다 (algorithm + algpseudocode/algorithmicx, `ruled`).

| 요소 | 규칙 |
|---|---|
| 선 | 위 0.8 pt, 캡션 아래 0.4 pt, 맨 아래 0.4 pt. 옆선 없음 |
| 캡션 | **Algorithm N**(굵게) + 제목(일반). 메인 알고리즘 제목은 도구명(small caps) |
| 본문 크기 | 7–8 pt (`\footnotesize` / `\scriptsize`), 한 단 폭 |
| Input / Output | 굵은 라벨 + "영어 명사 (기호)" 목록. 번호 없음 |
| 줄 번호 | `1:` 형식, 오른쪽 정렬, 빈 줄에도 번호 |
| 키워드 | 굵은 소문자 (procedure, repeat, until, for each, if, then, else, return). end 줄 없음 (noend) |
| 함수명 | **절차·외부 오라클 = small caps** (SymbolicExecutor, Execute, Sat, Solve, Run), **보조·단계 함수 = sans-serif** (Choose, Gather, Select, Construct, Generate) |
| 변수 | 이탤릭 (`\mathit`, 여러 글자 이름을 띄우지 않음) |
| 주석 | ▷ 오른쪽 끝 정렬 (`\Comment`): 하이퍼파라미터 기본값, 원소 형태, 부분집합 관계 |
| 블록 주석 | `/* Step 1. Extraction stage */` (ICSE25만 굵게). 단계 사이에 **번호 붙은 빈 줄** |
| 길이 | 일반 알고리즘 8–18줄, 메인 17–28줄 |

원 논문의 흠 (피할 것):

- 대입 기호 혼용: `←`와 `=` (ASE26 Alg. 1 10행, FSE26 Alg. 2 25행).
- 같은 기호의 서체 혼용: Φ 이탤릭/정체, 아래첨자 정체/이탤릭.
- 함수 서체 혼용: Seeding은 roman, 다른 절차는 small caps.
- 주석 끝 마침표, "=120"과 "= 120" 띄어쓰기 혼용.
- ICSE26 Alg. 2는 `procedure` 아래 들여쓰기를 하지 않았다.
- 캡션 없는 인라인 절차(ASE26 Seeding)는 가는 선 두 줄만 있고 Input/Output이 없다. 꼭 필요할 때만 쓸 것.

---

## 6. 수식 조판

| 항목 | 규칙 | 비고 |
|---|---|---|
| 배치 | display는 가운데. 목록 안에서는 목록 폭 기준 가운데 | |
| 번호 | **다시 참조하는 식에만** `(n)`, 오른쪽 끝 | 논문당 0–3개 (FSE26은 코드형 display에 (1)–(5)) |
| 도입 | 앞 문장이 콜론으로 끝난다 ("as follows:", "defined as:", "computed as:") | 4/4 |
| 끝 구두점 | 대체로 없음 (ICSE25는 전부 없음, ICSE26·ASE26은 섞임) | **하나로 통일할 것** |
| 식별자 | 여러 글자 변수는 `\mathit` (inp, TotalB, AllG) | |
| 함수 | small caps(Score, Eval, Feasible, Execute) / sans(Freq, Cov, Simple, Trace) | 논문 안에서 고정할 것 |
| 와일드카드 | `_` (ICSE25는 기준선 위 짧은 선, 나머지는 밑줄 문자) | (_, B, _, _) ∈ G |
| "where" | display 안에서 쉼표 뒤 (ICSE25는 굵게, ASE26은 정체) | |
| 큰 연산자 | Σ, argmax, ⋀는 display에서 **첨자를 아래에**. ⋃는 옆에 (ICSE26·ASE26) | |
| 분수 | `\frac`. 분모에 Σ가 있으면 첨자를 옆으로 | |
| 집합 | {x \| cond}, 조건은 ∧로 잇는다. 멀티셋은 {{ }}, 크기는 \|·\| | |
| 수치 예제 | 계산 과정도 display로 (27/34, ≈ 2.48GB) | ICSE26 |
| 코드형 display | 문법·기호 시퀀스는 Inconsolata 블록으로 왼쪽 정렬해 두고, 블록은 가운데. 필요하면 번호 | FSE26 |
| 크기 | display는 본문 크기로 | FSE26은 display를 8 pt로 줄였다 (피할 것) |
| 괄호 짝 | — | ICSE26 식 2개에 ")"가 남는다 (검산할 것) |

---

## 7. 원 논문의 수치 불일치 (반면교사)

| ID | 위치 | 불일치 |
|---|---|---|
| ICSE25 | §2 본문 vs Table I | "gawk ... 18,512" ↔ 표 25,124 (18,512는 5개 평균) |
| ICSE25 | Fig. 3 vs Table V | grep 1,019 + 2,086 = 3,105 ↔ 3,104 |
| ICSE25 | Table VII 설명 | "13.9% more"는 비율, "11.3% / 5.8% lower"는 다른 규약 (실제 감소율 10.1% / 5.5%) |
| ICSE25 | Table IX | 캡션 오타 "hyper-parmeter", "10.9% drop" 재현 불가 |
| ICSE26 | Table 4 vs 본문 | 60.2 / 89.9 / 34.2% ↔ 표 합계로는 59.6 / 91.6 / 32.6% |
| ICSE26 | Table 5 | 본문 "six methods" ↔ 캡션 "five" ↔ 표 5개, "four sampling algorithms" ↔ 3개 나열 |
| ICSE26 | Fig. 4 설명 | "remaining 77 parameters" ↔ 90 − 12 = 78 |
| ASE26 | Table 9 | SMT Skip 합계 3,840,978 = 앞 6행 합 (실제 8,902,371). Hit Ratio 16.3% ↔ 본문 16.8% |
| ASE26 | §4.1 vs Table 2 | OB 범위 "30 to 8,080" ↔ 표 최댓값 16,616 |
| ASE26 | Table 10 | 열 합 37,409 ↔ Total 37,419 |
| ASE26 | Abstract vs 본문 | 8.0% ↔ 7.9% |
| FSE26 | Table 5 | LoC 합계 207,230 ↔ 216,169. Tribble 입력 합계 394.9M ↔ 391.7M. 헤더에 "deltaratio" 문자열이 그대로 찍힘. 캡션 "Δ% relative to RSFuzz" ↔ 실제로는 baseline 기준 |
| FSE26 | Table 6 | 같은 값(273 vs 273)인데 Δ% "-3%" |
| FSE26 | §4.2 평균 | "On average ... 6.0%"는 합계 비율. 프로그램별 평균은 3.3% |

**교훈 (우리 논문 규칙으로):**

1. 표·그림·본문 수치를 **같은 스크립트 산출물**에서 생성한다 (LaTeX 표를 코드로 출력).
2. 백분율 규약을 하나로 고정한다. **비율(ours/base − 1)인지 감소율인지, 합계의 비율인지 평균의 평균인지** 정하고 캡션이나 §4.1에 밝힌다.
3. Abstract·Intro에 옮긴 수치는 원본 표에서 다시 확인한다 (반올림 규칙 포함).

---

## 8. LaTeX 레시피 (IEEEtran 기준, 컴파일 확인)

`paper/main.tex`(IEEEtran conference)에서 ICSE25 스타일을 재현하는 설정이다. TeX Live 2024에서 컴파일해 렌더링을 원 논문과 비교했다.
`caption` 패키지는 IEEEtran에서 "Unknown document class" 경고를 내지만 동작한다.

> **주의 (우리 제출 대상):** CFP가 "템플릿의 간격·폰트·기타 요소를 바꾸면 desk reject"라고 명시하므로, `\usepackage[labelsep=colon]{caption}`은 **쓰지 않는다**. 캡션은 IEEEtran 기본값("TABLE I" 줄 + small caps 캡션, "Fig. 1.")을 그대로 둔다. 아래 예시에서 caption 패키지 줄만 빼고 나머지(booktabs, ‖ 세로선, algorithm/algpseudocode, 매크로)는 그대로 써도 템플릿을 바꾸지 않는다.

```latex
% --- preamble ---
\usepackage{graphicx,booktabs,multirow}
% \usepackage[labelsep=colon]{caption}    % ICSE25 재현용. 우리 제출(IEEE 엄격 템플릿)에서는 쓰지 않음
\usepackage{algorithm}
\usepackage[noend]{algpseudocode}          % end 줄 없음, \Comment = ▷ 오른쪽 정렬
\renewcommand{\algorithmicrequire}{\textbf{Input:}}
\renewcommand{\algorithmicensure}{\textbf{Output:}}

\newcommand{\tool}{\textsc{Histra}}         % 도구명은 항상 small caps
\newcommand{\Fn}[1]{\textsc{#1}}            % 절차·외부 오라클 함수
\newcommand{\aux}[1]{\mathsf{#1}}           % 보조·단계 함수
\newcommand{\V}[1]{\mathit{#1}}             % 여러 글자 변수
\newcommand{\WC}{\rule{0.4em}{0.4pt}}       % 튜플 와일드카드 "_"
```

```latex
% --- 주 결과표: 2단 헤더, ‖ 세로선, booktabs, Total 행, 제안 기법 열 굵게 ---
\begin{table}[h]   % 우리 논문 규칙: [h], 처음 언급하는 문단 바로 앞
\caption{Average branch coverage achieved by two baselines under three settings}
\label{tab:main}
\centering
\resizebox{\columnwidth}{!}{%
\begin{tabular}{l||rrr|rrr}
\toprule
\multirow{2}{*}{\textbf{Benchmark}} & \multicolumn{3}{c|}{\textbf{KLEE [4] +}} & \multicolumn{3}{c}{\textbf{\textsc{Learch} [11] +}} \\
\cline{2-7}
\rule{0pt}{2.6ex} & \textsc{Base} & \textsc{RandSeed} & \textsc{TopSeed} & \textsc{Base} & \textsc{RandSeed} & \textsc{TopSeed} \\
\midrule\midrule
sqlite-3.33.0 & 4,281 & 4,053 & \textbf{6,448} & 5,112 & 5,251 & \textbf{5,944} \\
\midrule
Total & 7,560 & 7,405 & \textbf{10,502} & 8,045 & 8,337 & \textbf{9,170} \\
\bottomrule
\end{tabular}}
\end{table}
```

```latex
% --- 알고리즘: ruled, 8 pt, 블록 주석, ▷ 주석 ---
\begin{algorithm}[h]
\caption{\textsc{Histra}}\label{alg:main}
\footnotesize
\begin{algorithmic}[1]
\Require Trajectory ($\V{traj}$), tests ($\V{tests}$).
\Ensure Repaired program ($\V{patch}$)
\State $\langle D, \V{ref}\rangle \gets \langle \emptyset, \langle\rangle\rangle$ \Comment{$\eta_{\V{time}} = 120$}
\Repeat
  \State \textbf{/* Step 1. Sketch */}
  \State $S \gets \aux{Sketch}(\V{traj})$ \Comment{$(s, h, \WC) \in S$}
  \State
\Until{$\V{time}$ expires}
\end{algorithmic}
\end{algorithm}
```

```latex
% --- 수식: \mathit 변수, small caps / sans 함수, 와일드카드, 아래 첨자 argmax ---
\[ \Fn{Score}(B, \V{TotalB}) = \sum_{b \in B} \frac{1}{\aux{Freq}(b, \V{TotalB})},\ \textbf{where}\ (\WC, B, \WC) \in G \]
\begin{equation} G_{\V{top}} = \operatorname*{argmax}_{G \in \V{AllG}} \Fn{Score}(G, w) \end{equation}
```

- **양단 폭 플로트**는 `table*`·`figure*`로 쓴다. ICSE25는 가장 큰 결과표와 여러 패널 그래프에만 썼다.
- **ACM 템플릿**(acmart)을 쓰게 되면 캡션 모양(굵게, 마침표)은 템플릿 기본값을 따르고, 표·알고리즘·수식 규칙은 그대로 적용한다.

---

## 9. 작성 체크리스트

**공통**

- [ ] 모든 플로트가 `[h]`이고 처음 언급하는 문단 바로 위에 있는가. 밀렸다면 언급보다 위로 옮겼는가 (§1.3 우리 논문 규칙)
- [ ] 본문에서 처음 참조하는 문장이 핵심 주장인가 ("Table N shows that ...")
- [ ] 캡션이 명사구이고 도구명이 small caps인가. 표는 위, 그림은 아래인가
- [ ] 캡션은 제목만 있고, 약어·괄호 안 값·"-"·굵게의 의미는 처음 설명하는 본문 문단에서 밝혔는가

**표**

- [ ] 라벨 열 뒤에 ‖, 그룹 사이에 단일 세로선, 바깥 세로선 없음인가
- [ ] 2단 헤더(도구명 + [인용] / 설정·지표 small caps)와 `\cline`, Total 행 위 선이 있는가
- [ ] 숫자가 오른쪽 정렬이고 천 단위 쉼표, 평균은 소수 1자리인가. 0은 "-"로 통일했는가
- [ ] 강조 기준이 표 유형별로 하나이고, 본문에 적었는가
- [ ] 글자 크기가 6 pt 이상인가 (아니면 표를 나누거나 접었는가)
- [ ] 표 합계, 본문 백분율, Abstract 수치를 스크립트로 다시 계산했는가

**그림**

- [ ] overview가 흑백이고, 단계 상자 이름이 §3 단계 이름과 같고, 화살표에 데이터 이름이 붙어 있는가
- [ ] 그래프 글자가 6–7 pt 이상이고 서체가 본문과 맞는가 (usetex 또는 Times 지정)
- [ ] baseline·제안 기법 색을 논문 전체에서 고정했는가 (baseline 회색 계열, 제안 기법 강조색 + 해칭)
- [ ] 축 제목에 단위를 괄호로 넣었고, 범례가 데이터를 가리지 않는가
- [ ] 코드 그림에서 핵심 줄을 강조하고, 생략은 코드 주석으로 표시했는가

**알고리즘·수식**

- [ ] ruled 양식, `n:` 번호, 굵은 키워드, ▷ 주석, `/* Step k */` 블록 주석인가
- [ ] 대입은 ← 하나로, 함수 서체는 small caps(절차·오라클) / sans(보조)로 고정했는가
- [ ] 번호는 다시 참조하는 식에만 붙였고, 끝 구두점 규칙을 하나로 정했는가
