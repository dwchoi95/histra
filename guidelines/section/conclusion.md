# Conclusion — guidelines 4편 분석

[skeleton.md](skeleton.md)의 하위 문서. §6 Conclusion을 문장(move) 단위로 분석하고, 뒤따르는 Acknowledgments와 Data Availability도 함께 다룬다.
원문 전체는 move 태그를 붙여 부록 A에 실었다.

---

## 0. 핵심 규칙

1. Conclusion은 **1단락, 3–6문장, 74–125 words**다. 순서는 **현황 → 한계 → 목표 → 방법(동사 3개) → 결과 → (기대 효과)**다.
2. **Abstract를 줄인 거울**이다. Abstract와 같은 순서·같은 용어를 쓰되, 도전과제와 수치를 빼고 결과를 정성적으로 쓴다.
3. 방법 문장의 **동사 3개는 Abstract·Intro·§3.1의 단계 이름과 같아야 한다.** ICSE25는 정확히 같고, FSE26은 동의어가 섞였다(selects → identifies).
4. 결과는 **"Experimental results demonstrate that integrating X with N ... substantially improves A and B"**로 쓴다. 숫자를 쓰지 않는다 (0/4).
5. **향후 연구, 한계, 인용, 새로운 정보는 넣지 않는다** (4/4). 기대 효과 문장은 선택이다 (1/4).

---

## 1. 분량

| ID | 문장 수 | 단어 수 | 평균 문장 길이 | 문장별 단어 수 |
|---|---|---|---|---|
| ICSE25 | 5 | 95 | 19.0 | 11 · 12 · 26 · 25 · 21 |
| ICSE26 | 6 | 125 | 20.8 | 13 · 14 · 18 · 22 · 32 · 26 |
| ASE26 | 4 | 74 | 18.5 | 16 · 16 · 20 · 22 |
| FSE26 | 3 | 79 | 26.3 | 17 · 35 · 27 |
| **평균** | **~4.5** | **~93** | **~20.6** | |

- Abstract(평균 8문장, ~207 words, 문장당 ~26 words)의 **절반 이하 길이**이고 문장도 더 짧다.
- 단어 수는 본문 문장만 셌다. 제목과 Acknowledgments는 제외해서 [skeleton.md](skeleton.md) §1.2 표와 조금 다르다.

---

## 2. 구조

### 2.1 Move 정의

| Move | 역할 | 출현 |
|---|---|---|
| **C1 Context** | 분야 현황·발전 인정 | 3/4 |
| **C2 Gap** | 한계 (신조어·핵심 문제) | 3/4 |
| **C3 Goal / Present** | 논문의 목표 또는 제안 | 3/4 (ASE26은 C4에 합침) |
| **C4 Approach** | 방법 요약 (동사 2–3개) | 4/4 |
| **C5 Results** | 정성적 결과 | 4/4 (항상 끝 또는 끝에서 둘째) |
| C6 Impact | 기대 효과 | 1/4 (ICSE26) |

### 2.2 논문별 배치

| ID | S1 | S2 | S3 | S4 | S5 | S6 |
|---|---|---|---|---|---|---|
| ICSE25 | C1 | C2 | C3 Goal | C4 | C5 | |
| ICSE26 | C1 | C2 | C3 Present | C4 | C5 | C6 |
| ASE26 | C1 | C2 | C3 + C4 | C5 | | |
| FSE26 | C3 Present | C4 | C5 | | | |

**정형 순서:** C1 → C2 → C3 → C4 → C5 → (C6). 순서가 바뀐 경우는 없다. FSE26은 앞의 C1·C2를 생략하고 제안부터 시작한다.

### 2.3 Move 그룹별 비중

| ID | 문제 (C1–C2) | 목표 (C3) | 방법 (C4) | 결과 (C5) | 기대 효과 (C6) |
|---|---|---|---|---|---|
| ICSE25 | 24% | 27% | 26% | 22% | — |
| ICSE26 | 22% | 14% | 18% | 26% | 21% |
| ASE26 | 43% | (C4에 포함) | 27% | 30% | — |
| FSE26 | — | 22% | 44% | 34% | — |
| **평균** | **~22%** | **~16%** | **~29%** | **~28%** | ~5% |

### 2.4 Abstract와 비교

| Move | Abstract ([abstract.md](abstract.md)) | Conclusion |
|---|---|---|
| "We present X" 첫 문장 | 4/4 | 1/4 (FSE26 "We introduce ...") |
| 현황 + 한계 | 4/4 | 3/4 |
| 한계 수치 | 1/4 | **0/4** |
| 목표·아이디어 | 4/4 | 3/4 |
| 도전과제 | 2/4 | **0/4** |
| 방법 (동사 3개) | 4/4 | 4/4 |
| 실험 설정 문장 | 2/4 | 0/4 (결과 문장의 "integrating X with four advanced techniques"에 흡수) |
| 결과 | 4/4, **수치 3/4** | 4/4, **수치 0/4** |
| 기대 효과 | 0/4 | 1/4 |

→ Conclusion = **Abstract − (도전과제 + 수치 + 설정) + (선택: 기대 효과)**. 순서와 용어는 그대로 유지한다.

---

## 3. 단위별 분석

### C1 Context — 발전을 인정

- "State-of-the-art symbolic execution techniques **undoubtedly enhance performance** through various unique methods." (ICSE25)
- "**Modern** symbolic execution tools incorporate a variety of parameters to boost their performance." (ICSE26)
- "**Recent advancements** in symbolic execution **have improved** its ability to uncover hard-to-reach bugs and code regions." (ASE26)
- Abstract M2와 같은 역할이다. 인용 없이 한 문장으로 쓴다.

### C2 Gap — 한계를 한 문장으로

- "**However, we note that** these performance gains are often achieved without seeding." (ICSE25)
- "**Paradoxically**, as the number of parameters grows, configuring them becomes increasingly complex for users." (ICSE26)
- "**However**, these techniques **still struggle to** explore option-related code regions, which correspond to core program functionalities." (ASE26)
- 전환어(However / Paradoxically) + **논문의 핵심 용어**(seeding, parameters, option-related code regions)를 쓴다.
- Intro Gap 단락(I3)을 한 문장으로 줄인 것이다.

### C3 Goal / Present

- "**This paper aims to** automatically select promising seeds from inputs generated during interactions with these advanced techniques, **without any prior knowledge, thereby further boosting** their effectiveness." (ICSE25)
- "**This paper presents** a specialized algorithm designed to fully automate the program-aware parameter tuning process for symbolic execution." (ICSE26)
- "**We introduce** RSFuzz, a novel approach designed to minimize the generation of coverage-equivalent inputs during grammar-based fuzzing." (FSE26)
- Abstract M4(Goal)나 M1(Present)을 다시 쓴다. **"without any prior knowledge"** 같은 논문 전체 키워드를 여기서 한 번 더 반복한다.

### C4 Approach — 동사 3개

| ID | Conclusion | Abstract M6 |
|---|---|---|
| ICSE25 | "Our approach, TopSeed, **involves iteratively grouping** generated inputs, **ranking** each group, **and selecting** the most promising seed from the top-ranked group **based on accumulated data**." | "iteratively groups ..., ranks ..., and selects ... based on data accumulated during symbolic execution" — **일치** |
| ICSE26 | "This algorithm autonomously **selects** impactful parameters, **constructs** their sampling spaces, **and updates** sampling probabilities, **while iteratively interacting with** the symbolic execution tool." | "iteratively select ..., construct ..., and update ..." — **일치** |
| ASE26 | "Orbis **addresses this limitation by** automatically **constructing** effective option arguments **and optimizing** initial states, **while reducing** unnecessary SMT solver invocations." | "iteratively constructs ..., directs ..., and refines ... while simultaneously reducing ..." — 부분 일치 (directs → optimizing) |
| FSE26 | "Our approach employs a specialized algorithm that **repeatedly groups** coverage-equivalent inputs, **identifies** key groups responsible for generating them, **and extracts** recurrent sequences ... **based on accumulated data while interacting with** a grammar-based fuzzer." | "iteratively groups ..., selects ..., and extracts ..." — 동의어 섞임 (selects → identifies, iteratively → repeatedly) |

- 주어: "Our approach, X," / "This algorithm" / "X addresses this limitation by ..." / "Our approach employs a specialized algorithm that ..."
- 동명사(involves V-ing, by V-ing) 또는 3인칭 현재형으로 쓴다.
- **"based on accumulated data", "while (iteratively) interacting with <tool>"** 꼬리가 반복된다 (3/4).

### C5 Results — 정성적 결과

| ID | 문장 |
|---|---|
| ICSE25 | "**Experimental results demonstrated that integrating** TopSeed **with four advanced techniques substantially improves performance in terms of** bug detection and code coverage." |
| ICSE26 | "**The experimental results demonstrate that** our approach (ParaSuit) **outperforms** both manual and user-configured approaches **in terms of** code coverage and the discovery of unique bugs, **while eliminating the need for** user-driven tuning." |
| ASE26 | "**Experimental results show that integrating** Orbis **with five advanced techniques yields significant gains in** branch coverage and bug detection **beyond existing approaches**." |
| FSE26 | "**Experimental results demonstrate that integrating** RSFuzz **with** random, probabilistic, and grammar-coverage based fuzzers **leads to noticeable improvements in** line coverage and crash-finding **while reducing** coverage-equivalent input generation." |

- 틀: **"Experimental results demonstrate / show that integrating X with <N / 범주> <techniques> <substantially improves / yields significant gains in / leads to noticeable improvements in> <지표 1> and <지표 2>."**
- **지표 2개**(coverage + bugs)를 모두 쓴다. 이는 §4 RQ1–RQ2와 대응한다.
- 비교 대상은 개수·범주로만 쓴다 ("four advanced techniques", "both manual and user-configured approaches").
- 덧붙이는 이점 꼬리: "while eliminating the need for user-driven tuning", "while reducing coverage-equivalent input generation", "beyond existing approaches"
- 시제: ICSE25만 "demonstrated"(과거), 나머지는 현재형이다.

### C6 Impact (ICSE26만)

> "**We expect our approach to offer substantial benefits to both** end users **and** researchers **by simultaneously enhancing** the performance **and** usability of practical symbolic execution tools."

Intro에서 제기한 문제(사용자 부담)로 돌아가 **누구에게 무엇이 좋아지는지**로 닫는다. 넣는다면 한 문장으로 쓴다.

### 뒤따르는 부분 (Back matter)

| 요소 | ICSE25 | ICSE26 | ASE26 | FSE26 |
|---|---|---|---|---|
| 감사의 글 제목 | ACKNOWLEDGEMENT | Acknowledgments | Acknowledgments | Acknowledgments |
| Data Availability | — | — | Ack 뒤 bold run-in: "**Data Availability.** Orbis is accessible at: https://doi.org/10.5281/zenodo.21767392." | Conclusion 바로 뒤 독립 제목: "Our tool (RSFuzz) is publicly available at the following URL: https://github.com/skkusal/rsfuzz" |
| 도구 URL 위치 | Intro Contributions 각주 | Intro Contributions 본문 | Contributions + Data Availability (Zenodo DOI) | Contributions 각주 + Data Availability (GitHub) |

- **감사의 글은 연구비 지원 문구만** 쓴다 (4/4). 개인·심사위원에 대한 감사는 없다.
  - 틀: "This work was (partly / also) supported by the <기관>(<약어>) grant funded by the Korea government(MSIT) (No. <과제번호>, <과제명>)."
  - 기관마다 한 문장씩 쓴다 (NRF, IITP).
  - FSE26은 과제마다 기여 비율을 적는다 ("30%", "35%").
- **도구 공개 위치는 두 군데**다: Intro Contributions bullet 3("We make X publicly available")과 Data Availability. 최근 논문(ASE26, FSE26)은 Data Availability를 따로 둔다.
- ICSE26은 최종본에도 심사용 익명 URL(`unknownicse2026`)이 남아 있다. 최종본에서는 실제 URL로 바꿀 것.

---

## 4. 문체 특징

| 항목 | 관찰 |
|---|---|
| 주어 | 분야(C1–C2), This paper / We (C3), Our approach / This algorithm / 도구명 (C4), Experimental results (C5), We (C6) |
| 시제 | 현황·한계·방법·결과 모두 현재형 (ICSE25 결과만 과거형). 분야 발전은 현재완료 가능 |
| 전환어 | However, / Paradoxically, — 한계 문장에만 |
| 강조어 | undoubtedly, substantially, significant, noticeable, autonomously, fully |
| 반복 키워드 | without any prior knowledge / based on accumulated data / while iteratively interacting with / integrating X with |
| 길이 | 문장당 ~20 words로, Abstract(~26)보다 짧다 |
| **넣지 않는 것** | 수치, 인용, 그림·표 참조, 향후 연구, 한계·Threats, 새로운 정보, RQ 나열 |

---

## 5. 수식·알고리즘·플로트

해당 없음 (4/4). 수식·기호·플로트가 없다. 도구명만 small caps로 쓴다.

---

## 6. 섹션 간 연결

| Conclusion 요소 | 대응 위치 | 관계 |
|---|---|---|
| C1–C2 | Abstract M2–M3, Intro I2–I3 | 같은 한계를 같은 용어로 한 문장에 담는다 |
| C3 | Abstract M1·M4, Intro I4 | 같은 목표 문장을 다시 쓴다 ("without any prior knowledge") |
| C4 동사 3개 | Abstract M6, Intro I6, §3.1 Overview, Contributions bullet 2 | **같은 동사·같은 순서**. 다섯 곳 중 마지막이므로 동의어로 바뀌지 않게 대조할 것 |
| C5 지표 2개 | Abstract M8, §4 RQ1–RQ2 | 수치는 빼고 지표 이름만 남긴다 |
| C6 기대 효과 | Intro I3 (사용자 부담) | 문제 제기로 돌아가 닫는다 (ICSE26) |
| Data Availability URL | Intro Contributions bullet 3 | 같은 URL·같은 표현 ("publicly available") |

---

## 7. 템플릿

```text
[C1] <Recent advancements in | State-of-the-art> <domain> <have improved | undoubtedly enhance> <...>.
[C2] However, these techniques still struggle to <gap with the paper's key term>.
[C3] This paper <aims to | presents> <goal> without any prior knowledge, thereby <benefit>.
[C4] Our approach, <Tool>, involves iteratively <V1>-ing ..., <V2>-ing ..., and <V3>-ing ... based on accumulated data.
[C5] Experimental results demonstrate that integrating <Tool> with <N> <techniques> substantially improves <metric 1> and <metric 2>
     (, while <additional benefit>).
[C6] (opt.) We expect our approach to offer substantial benefits to both <users> and <researchers> by <...>.

Acknowledgments
This work was supported by the <agency> (<acronym>) grant funded by the Korea government (MSIT) (No. <grant id>, <project title>).

Data Availability
<Tool> is publicly available at: <DOI or URL>.
```

---

## 8. 작성 체크리스트

- [ ] 1단락, 3–6문장, 75–125 words인가
- [ ] 순서가 현황 → 한계 → 목표 → 방법 → 결과 → (기대 효과)인가
- [ ] 한계 문장에 논문의 핵심 용어(신조어)가 들어갔는가
- [ ] 방법 문장의 동사 3개가 Abstract·Intro·§3.1·Contributions와 글자 그대로 같은가
- [ ] 결과 문장에 지표 2개(coverage + bugs 등)가 있고, 숫자가 없는가
- [ ] 수치, 인용, 그림·표 참조, 향후 연구, 한계가 없는가
- [ ] 키워드("without any prior knowledge", "based on accumulated data")를 Abstract와 같은 표현으로 반복했는가
- [ ] 감사의 글이 연구비 지원 문구 형식이고, Data Availability에 실제(비익명) URL·DOI가 있는가

---

## 부록 A. 원문 (move 태그)

**ICSE25 — TopSeed**

> [C1] State-of-the-art symbolic execution techniques undoubtedly enhance performance through various unique methods. [C2] However, we note that these performance gains are often achieved without seeding. [C3] This paper aims to automatically select promising seeds from inputs generated during interactions with these advanced techniques, without any prior knowledge, thereby further boosting their effectiveness. [C4] Our approach, TopSeed, involves iteratively grouping generated inputs, ranking each group, and selecting the most promising seed from the top-ranked group based on accumulated data. [C5] Experimental results demonstrated that integrating TopSeed with four advanced techniques substantially improves performance in terms of bug detection and code coverage.

**ICSE26 — ParaSuit**

> [C1] Modern symbolic execution tools incorporate a variety of parameters to boost their performance. [C2] Paradoxically, as the number of parameters grows, configuring them becomes increasingly complex for users. [C3] This paper presents a specialized algorithm designed to fully automate the program-aware parameter tuning process for symbolic execution. [C4] This algorithm autonomously selects impactful parameters, constructs their sampling spaces, and updates sampling probabilities, while iteratively interacting with the symbolic execution tool. [C5] The experimental results demonstrate that our approach (ParaSuit) outperforms both manual and user-configured approaches in terms of code coverage and the discovery of unique bugs, while eliminating the need for user-driven tuning. [C6] We expect our approach to offer substantial benefits to both end users and researchers by simultaneously enhancing the performance and usability of practical symbolic execution tools.

**ASE26 — Orbis**

> [C1] Recent advancements in symbolic execution have improved its ability to uncover hard-to-reach bugs and code regions. [C2] However, these techniques still struggle to explore option-related code regions, which correspond to core program functionalities. [C3 + C4] Orbis addresses this limitation by automatically constructing effective option arguments and optimizing initial states, while reducing unnecessary SMT solver invocations. [C5] Experimental results show that integrating Orbis with five advanced techniques yields significant gains in branch coverage and bug detection beyond existing approaches.
>
> **Data Availability.** Orbis is accessible at: https://doi.org/10.5281/zenodo.21767392.

**FSE26 — RSFuzz**

> [C3] We introduce RSFuzz, a novel approach designed to minimize the generation of coverage-equivalent inputs during grammar-based fuzzing. [C4] Our approach employs a specialized algorithm that repeatedly groups coverage-equivalent inputs, identifies key groups responsible for generating them, and extracts recurrent sequences of production rules based on accumulated data while interacting with a grammar-based fuzzer. [C5] Experimental results demonstrate that integrating RSFuzz with random, probabilistic, and grammar-coverage based fuzzers leads to noticeable improvements in line coverage and crash-finding while reducing coverage-equivalent input generation.
>
> **Data Availability.** Our tool (RSFuzz) is publicly available at the following URL: https://github.com/skkusal/rsfuzz

(원문 FSE26은 "We introudce RSFuzz a novel approach"로 오타와 쉼표 누락이 있다. 위에서는 고쳐 옮겼다.)

**Acknowledgments 예 (ICSE25)**

> This work was supported by the National Research Foundation of Korea(NRF) grant funded by the Korea government(MSIT) (No. NRF-2021R1C1C2006410, No. RS-202300208094). This work was supported by the Institute of Information & Communications Technology Planning & Evaluation(IITP) grant funded by the Korea government(MSIT) (No.RS-2024-00438686, Development of software reliability improvement technology through identification of abnormal open sources and automatic application of DevSecOps). This work was partly supported by the Institute of Information & communications Technology Planning & Evaluation(IITP) grant funded by the Korea government(MSIT) (RS-2019-II190421, AI Graduate School Support Program(Sungkyunkwan University)).
