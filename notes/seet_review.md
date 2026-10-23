# ICSE-SEET 2027 모의 리뷰 (2026-10-15)

**방식**
- 리뷰어 에이전트 8명에게 PDF 한 편씩만 주고 블라인드로 리뷰를 받았습니다. 논문 4편을 각각 2명이 봤습니다.
- 리뷰어는 웹 검색이나 다른 파일을 볼 수 없었고, 어느 논문이 우리 것인지, 어느 논문이 accepted인지 몰랐습니다.
- 평가 기준은 CFP의 Relevance, Significance, Soundness, Verifiability, Presentation(각 1–5점)과 종합 추천입니다.
- 우리 PDF는 재실험 **전** 원고(숫자 갱신 전)입니다.

| 논문 | 실제 결과 | Rel | Sig | Sound | Verif | Pres | 추천 (R1 / R2) | 종합 |
|---|---|---|---|---|---|---|---|---|
| A: AI-generated code detectors (arXiv 2401.03676) | **SEET'24 accepted** | 3.0 | 2.0 | 2.0 | 3.5 | 2.0 | Weak Reject / Reject | 2.5 |
| **B: HISTRA (우리)** | — | 3.0 | **3.0** | **3.0** | **4.5** | **4.0** | **Borderline / Weak Reject** | **3.5** |
| C: GenAI tools in SE education (arXiv 2512.04256) | **SEET'26 accepted** | 4.5 | 2.0 | 2.0 | 3.0 | 3.0 | Weak Reject / Weak Reject | 3.0 |
| D: LLMs on OOP assignments (arXiv 2403.06254) | **SEET'24 accepted** | 4.5 | 2.0 | 2.0 | 3.0 | 3.5 | Reject / Weak Reject | 2.5 |

종합 점수는 Strong Accept 7, Accept 6, Weak Accept 5, Borderline 4, Weak Reject 3, Reject 2, Strong Reject 1로 환산해 두 리뷰어의 평균을 낸 값입니다.

## 보정(calibration)
- 에이전트 리뷰어는 실제 PC보다 확실히 엄격합니다. accepted 3편이 모두 Weak Reject에서 Reject 사이(2.5–3.0)를 받았습니다.
- 같은 잣대로 보면 **우리 논문은 4편 중 가장 높습니다(3.5).** Significance, Soundness, Verifiability, Presentation 모두 accepted 논문보다 높습니다.
- **유일하게 뒤지는 항목은 Relevance입니다** (우리 3.0, accepted 3.0–4.5). 두 리뷰어 모두 "학생, 과목, 피드백 전달 방식이 없는 APR/PL 논문으로 읽힌다"고 지적했습니다.
- accepted 논문 A도 같은 지적을 받았습니다(학생 데이터 없이 도구만 평가). 즉 SEET에서 치명적인 결함은 아니지만, 가장 쉽게 깎이는 지점입니다.

## 우리 논문의 공통 지적 (두 리뷰어 모두, [major])

| # | 지적 | 대응 | 상태 |
|---|---|---|---|
| 1 | 교육적 전제(의도를 보존한 패치가 더 나은 피드백)에 대한 증거가 없음. 패치를 피드백으로 어떻게 전달하는지도 설명하지 않음 | (a) skeleton과 무관한, 학생 자신의 수정 P_ac에 근거한 지표를 추가합니다: P_ac까지의 거리, P_ac와 같은 비율, own-fix-kept. (b) 패치를 피드백으로 전달하는 방식을 논의합니다: hole 위치 강조, diff, 힌트 생성의 입력(Phung et al.과 연결). (c) 선택 사항으로 소규모 전문가 평가(TA 2–3명이 패치 쌍 30–50개를 평가)를 할 수 있지만, 마감 8일 안에는 빠듯합니다. | (a) 지표 코드 추가 완료, 재실험 마지막 단계에서 계산됨. (b) 원고 작업. (c) **결정 필요** |
| 2 | 주 지표가 순환적임 (HISTRA 자신의 skeleton으로 잼) | 1(a)의 P_ac 기반 지표, TED, growth | 재실험 중 |
| 3 | LLM baseline이 약하고 최소 수정 지시가 없음 | LLM_G+Keep("change as few lines as possible") 대조군을 실행 중입니다. 더 강한 모델은 Threats에서 다룹니다. | 재실험 중 |
| 4 | 대상 집단과 상황이 다름 (대회 참가자, 이력이 필요함, 동료 정답 100개 이상 필요, cold start) | (a) CodeNet에서 "이전 WA가 1개 이상 있는 WA 제출"의 비율을 계산해 적용 범위를 보고합니다. (b) H가 비면 HISTRA가 Merge와 같아진다는 점(보장)을 명시합니다. (c) (선택) 참조 프로그램 수를 줄였을 때의 민감도를 표본으로 실험합니다. | 원고와 간단한 분석 |

## 그 밖의 지적 (한 리뷰어, 또는 [minor])
- **이점이 hole-only 경우에 집중됨:** free phase에서 Merge와의 비교값을 보고해야 합니다. summarize.py의 phase_report로 계산합니다(이전 값: Merge 36.0 대 HISTRA 34.1).
- **최소화 예산이 다름(10 대 20):** merge-min 대조군(예산 20)이 이미 실행됐습니다.
- **trajectory당 지연 시간 미보고:** histra_eval.py가 기록하는 sec의 중앙값과 최댓값을 보고합니다.
- **하이퍼파라미터를 평가셋에서 튜닝함:** Threats에서 인정합니다.
- **타입 수준 skeleton이 버그를 포함할 수 있음:** Threats와 fallback 설명으로 답합니다.
- **Merge가 우리 재구현임:** RefMerge로 이름을 바꾸고 Sarfgen과의 차이를 명시합니다.

## 비교 논문들이 받은 지적 (참고: 리뷰어의 기본 성향)
- 세 편 모두 공통으로 Significance 2, Soundness 2를 받았습니다. 지적은 "참신성 부족", "분석이 얕음", "교육적 주장과 데이터의 연결 부족", "한계 논의가 얕음"이었습니다.
- 우리 논문은 Soundness(통계, ablation, 대조군)와 Verifiability(아티팩트, 공개 모델)에서 확실히 앞섭니다.
