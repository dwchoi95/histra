# HISTRA 논문 최종 검토 v3 (2026-10-15)

- **대상:** `main.en.tex`(아래 L번호의 기준), `main.tex`(한국어 원고, KR L로 표기), `main.en.pdf`(11쪽, 본문 9쪽)
- **방식:** 다섯 관점으로 나눠 병렬 검토했습니다.
  1. 논리·방법·실험
  2. 관련 연구·인용 (원문과 Crossref 대조)
  3. 숫자·표·그림·수식
  4. 용어·문법·한영 대응
  5. **알고리즘 표기 일관성** (이번에 새로 추가)
- **이전 판:** v2는 `scratchpad/review3/final_review_v2.md`에 보관했습니다.
- **표시 규칙:**
  - **(재실험)**: 재실험이 끝난 뒤 수치와 서술을 고칠 항목입니다.
  - **결정 필요**: 재실험 범위가 달라지는 항목입니다.

---

## [Critical Issues]

| # | 위치 | 문제 | 이유 | 수정안 |
|---|---|---|---|---|
| K1 | §III-E L292, L362, L366 / 코드 histra.py:43-45, repair.py:21-22, merge.py:221 | **hole-only phase에서 hole 안의 연산자가 고정됩니다** (직접 재현함) | 연산자 노드는 tree 전체에서 공유하는 싱글턴이라 holed에서 빠지고 frozen에 들어갑니다. 그래서 hole 안의 `n + 1`이 r의 `n - 1`로 바뀌지 않습니다(free merge에서는 바뀝니다). BinOp, UnaryOp, BoolOp, AugAssign이 해당하고, Compare는 리스트 경로를 타서 바뀝니다. 본문의 "takes the operators … of r"와 어긋나며, \tool{}에 불리한 결함입니다. | **결정 필요.** repair.py에서 frozen 집합에 싱글턴을 넣지 않게 한 줄 고치고, hole-only phase를 쓰는 변형(min, plain, nostd, nokept, sizemin, randhole)을 다시 실행합니다. |
| K2 | Abstract, I7, §IV-D, Table IV | **RQ3("history guidance가 LLM을 개선한다")에 혼동 변수가 있습니다** | LLM_G+\tool{}는 hole 프롬프트가 실패하면 LLM_G의 원래 패치로 대체합니다. 그래서 두 번 시도한 효과가 섞입니다. 또 프롬프트에 이력과 무관한 "keep every other line exactly as written" 지시가 들어 있습니다. 42.2→34.4 감소와 52건 추가 수정을 이력의 효과로 단정할 수 없습니다. | **결정 필요.** 대조군 LLM_G+Keep(줄 목록 없이 "change as few lines as possible", 대체 방식 동일)과 LLM_G+Rand(같은 개수의 무작위 줄)을 실행합니다. 실행하지 않으면 RQ3 주장을 낮추고 Abstract에서 RQ3 수치를 뺍니다. |
| K3 | L105, L509 | **Refactory와 Brafar를 사실과 다르게 서술했습니다** | Refactory는 맞는 reference가 없으면 학생 프로그램의 제어 흐름을 변형합니다(README, Brafar 초록). Brafar도 학생 프로그램을 리팩터링합니다. 그런데 L509의 "keep the student's control flow uniformly"는 바로 앞 절과도 모순됩니다. 이 서술은 CLARA와 Sarfgen에만 맞습니다. | L105와 L509를 고칩니다. CLARA와 Sarfgen은 제어 흐름이 같은 reference를 요구합니다. Refactory와 Brafar는 학생 코드를 변형하거나 리팩터링해 이 제약을 완화하는데, 학생이 확정한 부분을 고려하지 않습니다. 이렇게 쓰면 논지가 오히려 강해집니다. |
| K4 | L503 Threats (2) | **본문에 없는 지표를 "보고한다"고 썼습니다** (v2-C6) | §IV-B에서 skeleton과 무관한 지표는 Fixed뿐입니다. 관련 연구는 모두 근접성 지표를 씁니다(Koutcheme'23 거리 척도, AdaPatcher Consistency, PyDex token edit distance, Phung'23 EditTokens). | edit-size 지표(TED, growth, own-fix-kept)와 token edit distance를 보고하고, skeleton loss를 "이 거리들을 history로 가중한 것"으로 위치를 잡습니다. **(재실험)** |
| K5 | L431, L503 | **Merge를 Sarfgen의 "재구현"이라 부르고 "differs only in ignoring the history"라고 씁니다** (v2-C1) | 제어 흐름 일치 조건이 없고, 첫 통과 패치를 쓰며, 예산 10회의 greedy revert로 축소합니다. 같은 문단에 적힌 축소기 차이와도 모순됩니다. | "Sarfgen-inspired"로 고치고 RefMerge로 이름을 바꿉니다. merge-min과 nohist 결과로 다시 씁니다. **(재실험)** |

## [Major Issues]

| # | 위치 | 문제 | 이유 | 수정안 |
|---|---|---|---|---|
| J1 | L140-142, L336-338, L341 | **skeleton의 형식 정의가 둘이고, 구현과도 다릅니다** | stable은 정규화된 트리 \hat P_n에서 정의되는데 표기는 Skel(P_n)과 U(P_n)입니다. 실제 지표는 원본 트리의 Skel(b^□)로 잽니다(skel.py:68). 또 수식은 stmt/expr가 아닌 조상(keyword, comprehension 등)까지 stable하기를 요구하지만, 코드는 stmt/expr 조상만 봅니다(sketch.py:48-59). | §II-B에는 비형식 정의만 두고, §III-C에서 Skel(b^□) = U(b) \ (hole들의 투영)으로 정의합니다. 조상 정량화는 ∩U로 제한합니다. retention은 Skel(b^□) 위에서 정의하고, relabel 비용(값까지 같아야 0)을 명시합니다. |
| J2 | L62, L292, L341 / L37, L71, L521 | **"hole만 바뀐다", "skeleton을 고정한다"는 서술이 과장입니다** | hole을 포함한 노드는 다른 타입의 노드로 통째로 교체될 수 있고, 삽입도 일어납니다(L366이 이를 인정합니다). running example도 `s = 0`을 삽입합니다. | "the retrieved code goes mainly into the holes", "the frozen nodes are copied verbatim; skeleton nodes containing holes may still change" |
| J3 | L62, L37, L71, L521 | **"merges without this restriction only when no such patch passes"가 Alg. 2와 다릅니다** | Alg. 2는 두 phase의 후보를 모두 미리 병합하고, 검증 순서만 다릅니다. | "only when no hole-only candidate passes does it validate the candidates merged without this restriction" |
| J4 | Alg. 1 L91 대 Alg. 2 L275, L289, L362 | **Merge의 인자 수(2개와 4개) 관계를 설명하지 않습니다** | L295의 보장 논증("free candidates are exactly the history-agnostic merges")이 이 대응 관계에 기대고 있습니다. | "Merge(b^□, r, m, o) extends Merge of Algorithm 1 with a phase m and an order mode o; Algorithm 1's merge corresponds to m = free." L362는 "Given the sketch b^□, a retrieved program r, a phase m, and an order mode o" |
| J5 | Alg. 2 L10-11, L371, L453 | **후보 집합 C가 집합이라 동점 처리 규칙을 표현할 수 없습니다** | 코드는 순서가 있는 리스트입니다. 정렬 키는 (phase, −Kept, 삽입 순서)이고, 같은 소스 코드는 중복 제거합니다(repair.py:36-45). | C를 시퀀스로 바꾸고("append (m, c) unless c ∈ C"), L11은 안정 정렬(stable sort)로 씁니다. |
| J6 | L437, minimize.py:65·72 | **"Merge and \tool{} are deterministic"이 사실이 아닙니다** | Minimize는 동점일 때 `id(pn)`(메모리 주소)로 순서를 정합니다. 테스트 결과도 시스템 부하에 따라 달라집니다(그래서 p02686을 다시 실행했습니다). | 남은 재실험 전에 동점 처리를 전위 순회 인덱스로 바꿉니다(한 줄). 본문은 "deterministic except for timeouts under load"로 고칩니다. |
| J7 | histra_eval.py:24-34 | **random-hole 대조군 설계가 같은 조건이 아닙니다** | 탐욕적으로 "at most" 채우므로 덮는 범위가 이력 hole보다 작아집니다. 잎 수준의 작은 hole이 흩어져 frozen 노드가 크게 줄어드니, 위치뿐 아니라 성격도 다른 대조군이 됩니다. 시드도 하나뿐입니다. | 이력 hole과 개수, 크기, 종류(stmt/expr)를 맞추고 서로 겹치지 않게 hole 루트를 뽑습니다. 덮은 비율과 frozen 비율을 함께 보고하고, 시드는 3개를 씁니다. **실행 전에 반영해야 합니다** (그래서 대기열을 멈춰 두었습니다). |
| J8 | L503 Threats, L80, L434 | **평가 시나리오가 실제 배포 상황과 다른 점을 밝히지 않았습니다** | R에는 P_n 이후에 제출된 AC도 들어 있습니다. 문제당 100명 이상이 필요합니다. AC 직전의 마지막 WA만 수리합니다. TLE/RE/CE 제출은 trajectory에서 빠집니다. | Threats에 추가합니다. (선택) 시간 순서를 지킨 R 변형, 중간 WA 표본 실험 |
| J9 | L431, L503 | **AdaPatcher, Brafar, CLARA를 비교하지 않은 이유가 없습니다** | AdaPatcher는 CodeNet Python과 공개 모델을 쓰고, 근접성 지표도 있어 가장 가까운 기법입니다. 학습 데이터 누출 가능성도 따져야 합니다. Brafar는 Refactory와 같은 함수 단위 Python을 대상으로 합니다. | 제외 이유를 한 문장씩 씁니다(AdaPatcher: 미세조정과 데이터 분할, 누출 위험). **(재실험, Baselines 재작성 때)** |
| J10 | I3 L53, Abstract | **연구 공백이 최소 수정형 repairer를 무시하는 형태로 쓰여 있습니다** | 같은 논문의 L105와 L515가 Qlose, Sarfgen, AdaPatcher, DRO 등이 근접성을 선호한다고 씁니다. | "existing repairers either ignore closeness or treat every part of the program as equally costly to change; none knows which parts the student has settled on" |
| J11 | L147, L503 | **대리 지표의 타당성을 과대 해석합니다** ("largely reflects code that the students chose to keep") | 학생은 skeleton 밖 노드도 81.8%를 그대로 둡니다. 데이터가 지지하는 것은 상대적 차이(9.5% 대 18.2%)입니다. | "students changed a skeleton node about half as often as a non-skeleton node (9.5% vs 18.2%)" **(수치 재측정)** |
| J12 | L515 | **차별 문장이 두 계열을 섞었습니다** | AdaPatcher에는 hole이 없습니다(줄 위치를 조건으로 전체를 생성합니다). "every part equally costly"는 거리 기반 기법에만 맞습니다. | "the holes or edit locations come from an error model or a fault localizer, and the distance-based objectives charge every part of the program alike" |
| J13 | §V | **2023–2026 연구가 빠졌습니다** | Phung et al. ICER'23(LLM이 튜터보다 약 2배 많이 수정한다는 EditTokens 결과, L509 주장의 직접 근거). HAFix(EMSE 2026, 수리 대상 코드 자신의 blame 이력, novelty 문장의 범위를 정하려면 대비 필요). Koutcheme AIED'23(교육용 infilling 수리, xia2022보다 적합). | 세 편을 한 문장씩 추가합니다. |
| J14 | L102, L156 (첫 명시는 L253) | **b = P_n 관계를 §III-A에서야 밝힙니다** | §II에서 P_n과 b가 섞여 나옵니다. | L102에 "a buggy program (b), i.e., the incorrect submission P_n to be repaired"를 넣습니다. |
| J15 | L50, L102, L256, L498, L509 | **같은 repairer 계열에 이름이 넷입니다** (data-driven, reference-guided, structure-matching, merge-based) | 서로 다른 계열로 읽힐 수 있습니다. | "reference-guided"로 통일합니다. |
| J16 | L80, L147, L437 / L37, L509 / L47, L53, L289 | **"reference"가 R 말고도 세 가지 뜻으로 쓰입니다** | "as a reference point", "the references", 교수자의 "reference solution"이 핵심 기호 R과 겹칩니다. | "for comparison", "the reference programs", "instructors' reference solutions" |
| J17 | L374, KR L423 | **"keeps an edit"의 뜻이 반대로 읽힙니다** (실제로는 되돌림을 확정한다는 뜻) | "edits"는 같은 문단에서 되돌릴 대상으로 정의됩니다. | "tries to undo the edits one at a time, keeps an undo whenever the result still passes T" |
| J18 | L380 | **"without any input beyond the student's own history"가 R과 T도 없는 것처럼 읽힙니다** (지난 수정에서 생긴 오류) | 한국어본("추가 입력 없이")은 맞습니다. | "requiring no input beyond those of existing repairers except the student's own history" |
| J19 | L366/L448 "62.6%" | **비율과 손실의 분모가 다릅니다** | 62.6%는 1,065/1,702로 skeleton이 빈 51건을 포함하지만, 8.6과 34.1은 1,651건 기준(61.4%)입니다. 그래서 가중 평균이 18.1이 되어 18.4가 재현되지 않습니다. | 분모를 통일합니다. **(재실험)** |
| J20 | 전반 | **40단어가 넘는 문장이 약 39개입니다** (재작성 구간 밖 31개) | 가독성 문제입니다. | 분할합니다(분할안 S1–S31은 용어 검토 보고에 있음). |
| P | Abstract, I7, §IV, Conclusion | v2에서 남은 결과 관련 항목: "repairs the most", 1,644 설명, Wilcoxon 효과 크기와 Holm 보정, fallback 해석(46.6% 대 30.0%), RQ3 짝지은 비교, 표본과 전체 수치 혼용, 학생 손실의 세 가지 집계, 인과 서술 "because …", "We expect" | 이미 정리된 항목입니다. | **(재실험, 결과 재작성 때 일괄 반영)** |

## [Minor Issues]

| 위치 | 문제 | 수정안 |
|---|---|---|
| L362 | "keeps the student's identifiers"가 부정확합니다. 실제로 유지하는 것은 변수, 인자, keyword 이름뿐이고 attribute 이름은 r을 따릅니다. | "keeps the student's variable names and takes other scalar fields, such as operators, constants, and attribute names, from r" |
| L362, L503 | NW 정렬은 모든 AST 리스트에 적용되고, 임계값 0.34가 본문에 없습니다. Threats의 "alignment thresholds"는 정의되지 않았습니다. | 임계값을 한 구로 적거나, Threats에서 이 표현을 삭제합니다. |
| L362 | "for the same reason … or that add code to a block that is empty": 빈 블록 제약은 원인이 다릅니다. | 문장을 둘로 나눕니다. |
| L371 대 L142 | Kept의 레이블 ℓ에는 연산자가 없고 retention에는 있습니다. "leaves untouched"는 과장입니다. | "unlike retention, Kept ignores operators" 또는 "whose labels c leaves unchanged" |
| L333 | "semantics-preserving rules": `x += e`는 가변 객체에서, 비교 뒤집기는 평가 순서에서 의미가 다를 수 있습니다. | "intent-preserving rewrites" |
| L292 | "At line 11, it validates": 검증은 12행입니다. | "At lines 11–12" |
| L292, L374 | η_v가 정의(L374)보다 먼저 Alg. 2 주석에 나옵니다. 본문에서 c와 C를 소개하지 않습니다. | 워크스루에서 "candidates C", "candidate c", "at most η_v validations"를 소개합니다. |
| L349 | Rank의 정의가 없습니다. | "Rank(R, b) sorts R by descending Sim(b, ·)" |
| L359 | "three parts"인데 Fig. 1에는 상자가 4개입니다. "into b"는 "into b^□"여야 합니다. | 문구를 맞춥니다. |
| Fig. 1 | (a) Search는 Sketch를 거치지 않고 원본 b를 받습니다. (b) T→Minimize, ⊥ 출구가 없습니다. (c) 글꼴이 \scriptsize이고 "pass" 레이블이 상자 테두리에 붙어 있습니다. (d) Kept만 \mathsf입니다. | (a) b를 입력 버스에서 Search로 직접 연결합니다. (b) 화살표와 출구를 추가합니다(선택). (c) 레이블 위치를 조정합니다. (d) 서체를 통일합니다. |
| L453 | \tool{}_size "by subtree size alone"이 부정확합니다(삽입문은 여전히 마지막에 시도). | "ignores the holes (larger edits first; insertions last)" **(재실험)** |
| L498 | "replacing the merges at lines 8–10 with model calls"가 실제 구현과 다릅니다(R_k와 o 루프가 없고 phase당 한 번 호출). "asked it to change only those lines"에서 실제 프롬프트는 "if possible"입니다. | 실제 구현대로 씁니다. **(재실험)** |
| L105 | CLARA는 대표 하나가 아니라 클러스터 전체의 식을 ILP로 고르고, Refactory는 병합이 아니라 synthesis로 고칩니다. | 표현을 고칩니다(K3과 함께). |
| L50 | Verifix를 data-driven 계열에 넣었습니다(실제로는 강사 reference를 씀). | 표기를 분리합니다. |
| L512 | AsanasAssist는 거리 임계치에 따라 힌트를 새로 만들지, 상세 수준을 올릴지, 다음 차이로 넘어갈지를 정합니다. "Most of these techniques"로 범위를 좁혀야 합니다(Piech는 다른 성격). | "only to decide whether to restart, escalate, or advance its hints" |
| L53 | "therefore"의 인과 연결이 약합니다. | "Accordingly," |
| 기호 | r(효과 크기)과 r(참조 프로그램), c(후보)와 c_p(f)(개수), p(프로그램)와 p-value, `a > b`와 b, Figure 2(b)와 b가 겹칩니다. | c_p(f)를 n_q(f)로, 효과 크기는 "effect size"로, 예시는 `x > y`로 바꿉니다. |
| bib (인쇄본) | 콜론 뒤 첫 글자가 소문자입니다([7] data-driven, [13] a neural, [16] an efficient, [42] a self-improving, [46] revisiting). Verifix는 "pp. 1–31"이고 실제로는 Art. no. 74입니다. art. no.의 위치와 대소문자가 어긋납니다. [28] "no. 1-3" | 중괄호로 보호하고 형식을 통일합니다. |
| KR | L59 "참조 프로그램을 받게 될 수 있다"는 R과 혼동됩니다. L162에 연산자가 빠졌습니다. L71 "검색된 제출/실패한 제출". L388 smoothed가 빠졌습니다. L281 "η_k개 R_k"는 비문입니다. \tool{} 뒤 조사 54곳("은/을/이/과", HISTRA는 모음으로 끝나므로 "는/를/가/와"가 맞음). "정렬"이 rank, align, order 세 뜻으로 쓰입니다. | 각각 고칩니다. |

## [Consistency Check]

**숫자** (재측정 전 기준)

| 항목 | 위치 | 판정 |
|---|---|---|
| Table II 모든 셀, 굵은 표시 | 전체 | 일치 |
| 2.7–4.7배, 1.4–5.3배, 91.3%, 48.5/13.7/18.2/9.5/35.6 | Abstract, I3, §II | 원고 안에서는 일치. 다만 표본과 전체가 섞임 **(재측정)** |
| 1,644 "fixed by both" | L445 | 실제는 둘 다 고친 1,695건 중 skeleton이 비어 있지 않은 건수(0이 아닌 쌍 840) |
| 62.6%와 8.6/34.1 | L366, L448 | 분모 불일치(J19) |
| 2.7pp, 2.9pp, 4.7배 | L476, L498, L37 | 표에 표시된 값으로 계산하면 2.8, 3.0, 4.8 |
| 학생 손실 8.7 / 7.7 / 9.5 | Table I, Table II, L147 | 집계 방식이 섞임 |

**알고리즘 표기**

| 항목 | 판정 |
|---|---|
| 본문의 Alg. 1·2 줄 참조 20개 | 모두 일치(L292 "line 11 validates"만 11–12행으로) |
| Alg. 2 루프 순서, 정렬 키, 동점 처리 | 코드와 일치(C의 집합 표기만 J5) |
| 옛 표기(pgm, S, F, Φ, φ, Refs, sk, τ, w(f), Step) | 렌더링되는 본문에는 0건(주석에 "frozen set" 하나) |
| 함수 서체 | Alg.와 본문은 \mathsf로 통일. Fig. 1만 섞임 |
| Merge의 인자 수, C의 의미, Skel의 이중 정의, 조상 정량화 | J4, J5, J1 |
| 기호 충돌 | r, c, p, b(Minor) |

**용어**

| 개념 | 판정 |
|---|---|
| buggy program b / reference programs R / history programs H / sketch b^□ / R_k / hole-only·free phase | Alg., Fig., §III에서 일관됨. 남은 변형: "the references"(L37, L509), "fallback patches"(L448), "statement orders"(L431), repairer 계열 이름 넷(J15), "reference"의 세 가지 뜻(J16) |
| 한국어 | \tool{} 조사, "정렬" 다의어, 일부 대응 누락(Minor) |

## [Citation Verification] (문제가 있는 행만. 나머지 인용은 원문과 대조해 OK)

| 줄 | 문장 | citation | 적절성 | 문제점 |
|---|---|---|---|---|
| L105 | "These techniques keep the control flow of b uniformly … cannot repair it when no reference program matches" | gulwani, wang, hu | **WRONG** | Refactory는 학생 코드를 변형합니다(K3). |
| L509 | "These repairers keep the student's control flow uniformly" | gulwani, wang, hu, xie, ahmed | **WRONG** | Refactory와 Brafar에 맞지 않고, 앞 절과도 모순됩니다(K3). |
| L431 | "our Python reimplementation of … Sarfgen … delta debugging of up to 10 trials" | wang, zeller | **WRONG** | K5 **(재실험)** |
| L105 | CLARA "toward a cluster representative", Refactory "before merging them" | gulwani, hu | PARTIAL | 실제로는 ILP 최소 비용, synthesis입니다. |
| L50 | Verifix를 data-driven 계열에 넣음 | ahmed | PARTIAL | 강사 reference를 씁니다. |
| L515 | "holes come from … a fault localizer [singh, orvalho, dai2025], and every part … equally costly" | — | PARTIAL | AdaPatcher에는 hole이 없습니다(J12). |
| L512 | AsanasAssist "only to decide how much detail" | paiva2025 | PARTIAL(경미) | restart, escalate, advance 세 가지입니다. |
| L503 | "did not compare with PaR and LSGen" | zhao, dai2026 | PARTIAL | AdaPatcher 언급이 빠졌습니다(J9). |
| L512 | "To our knowledge, the first …" | — | UNVERIFIED | 반례는 없습니다. HAFix와 대비하면 범위가 분명해집니다(J13). |

- 인용 키 47개는 모두 bib에 있고 중복이 없습니다.
- 새로 넣은 인용(AdaPatcher, HDRepair, Phung'24, Roest, Koutcheme ×2, Pitts, Orvalho)은 원문 문장으로 확인해 OK입니다.

## [Potential Reviewer Comments]

| # | 예상 지적 | 대응 |
|---|---|---|
| 1 | "지표가 순환적이다. \tool{} 자신의 Sketch로 재고, 삽입은 세지 않는다." | 연산자를 반영해 재측정하고, edit-size와 token edit distance를 함께 보고합니다(K4). |
| 2 | "Merge는 Sarfgen이 아니라 약화판이다." | RefMerge로 이름을 바꾸고, merge-min과 nohist로 공정하게 비교합니다(K5). |
| 3 | "이력이 아니라 그냥 hole의 효과 아닌가." | 개수와 크기를 맞춘 random-hole 대조군을 시드 3개로 실행합니다(J7). |
| 4 | "RQ3는 두 번째 시도와 최소 수정 지시의 효과일 뿐이다." | LLM_G+Keep, LLM_G+Rand 대조군을 실행합니다(K2). |
| 5 | "AdaPatcher와 비교해야 한다." | 비교하거나 제외 이유를 씁니다(J9). |
| 6 | "Refactory 서술이 틀렸다." | K3을 수정합니다. |
| 7 | "효과가 작다(RR +0.4pp)." | McNemar 검정, 효과 크기, 조건부 주장으로 답합니다. |
| 8 | "평가 시나리오가 비현실적이다(미래 AC, 마지막 WA, 100명 이상)." | Threats에 쓰고, (선택) 시간 순서를 지킨 R 변형을 실행합니다(J8). |
| 9 | "교육적 이득이 검증되지 않았다." | 대리 지표임을 명시하고 "We hope"로 씁니다. 사용자 연구는 향후 과제입니다. |
| 10 | "결정적이지 않고, 실행 시간을 보고하지 않았다." | 동점 처리를 고치고(J6), trajectory당 시간의 중앙값과 최댓값을 보고합니다. |
| 11 | "정규화와 region 순서는 효과가 없다." | 기여에서 낮추고, provenance는 공학적 장치로 위치를 잡습니다. |
| 12 | "왜 타입 수준이고 모든 이전 제출인가." | Threats로 답합니다. (선택) 직전 제출만 쓰는 변형과 value-aware 변형을 ablation으로 추가합니다. |

## [Final Submission Checklist]

| 항목 | 결과 |
|---|---|
| IEEE 형식, 분량(본문 9쪽 + 참고문헌 2쪽), 익명성, 폰트 | PASS |
| 캡션 형식(제목만), 플로트가 첫 언급보다 위 | PASS |
| TODO 없음 | **FAIL** (artifact URL, running example의 대조군 비교) |
| 인용 키와 메타데이터 | PASS (인쇄본 대소문자, art. no.만 Minor) |
| 인용과 주장 일치 | **FAIL** (Refactory/Brafar K3, Sarfgen K5, AdaPatcher J12) |
| 관련 연구 범위 | **FAIL** (Phung'23, HAFix, Koutcheme AIED'23, AdaPatcher 비교 사유) |
| 방법 서술과 코드 일치 | **FAIL** (K1 연산자, J1 skeleton 정의, J2, J3, J4, J5) |
| 알고리즘 표기와 줄 참조 | PASS (구조 문제는 J4, J5) |
| 표 수치와 굵은 표시 | PASS |
| 숫자 일관성 | **FAIL** (재측정 후 일괄 재작성) |
| baseline 공정성, 대조군 | **FAIL** (재실험 중, K2, J7) |
| 통계 보고 | **FAIL** (재작성 때 summarize.py의 McNemar, Holm, r 값 사용) |
| 주장과 근거 | **FAIL** (J2, J3, J10, J11, "repairs the most") |
| Threats 완전성 | **FAIL** (J8, J9, K2) |
| 용어와 약어 | **FAIL** (J15, J16, KR 조사) |
| 문법·문체 | **FAIL** (40단어 초과 문장 약 39개, J17, J18) |
