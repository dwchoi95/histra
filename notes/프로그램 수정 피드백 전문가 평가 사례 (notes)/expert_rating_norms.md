# Expert/TA rating studies of generated repairs, hints and feedback on student code (CS-ed / SE-ed venues, 2022–2026): protocols, scale, rubrics, ethics, agreement

Scope note: I read the full text (arXiv or the authors' repository PDF) for every paper listed under Q1, except where marked "snippet only". The ACM policy was read in full through a Wayback Machine copy, because acm.org returned HTTP 403 to direct fetches.

## Q1. Per-paper protocols (venue/year, raters, items, rubric, scale, blinding, agreement, resolution, effort, ethics, statistics)

### Takeaway
Eight papers in the target venues (SIGCSE TS, ITiCSE, ICER) and one closely related TOCE paper show the same pattern. The usual design is 1–4 author-experts rating every item on a set of **binary yes/no criteria**, with Cohen's kappa reported on a calibration subset or on the full set. Only one paper (TOCE 2025) used external educators and pairwise comparative judgement, and it is also the only one with a formal ethics-approval number. I found no qualifying papers from ICSE-SEET or Koli Calling (see Gaps).

### Cited Findings

**(1) Leinonen et al., "Using Large Language Models to Enhance Programming Error Messages" (arXiv 2210.11630; SIGCSE TS 2023 per the paper's DOI listing, which I did not verify in the fetched text)**
- Raters: "two researchers, both of whom have experience from teaching introductory programming." — [arXiv 2210.11630](https://arxiv.org/abs/2210.11630)
- Items: 9 error messages × 3 program categories × 3 Codex generations (temperature 0, plus two at 0.7) = 81 unique combinations. Percentages are "calculated out of the full set of 162", which appears to be 81 × 2 raters. — [arXiv 2210.11630](https://arxiv.org/abs/2210.11630)
- Rubric: 7 binary (yes/no) aspects:
  - Comprehensible ("proper English, not nonsensical")
  - Unnecessary content
  - Has explanation
  - Explanation correct
  - Has fix
  - Fix correct
  - "Improvement over the original: did the explanation provide added value (from a novice programmer standpoint) when compared to the original programming error message"

  Source: [arXiv 2210.11630](https://arxiv.org/abs/2210.11630)
- Calibration procedure: the researchers "first had a brief discussion to ensure a shared understanding … and jointly evaluated three examples", then "separately analyzed the full set." — [arXiv 2210.11630](https://arxiv.org/abs/2210.11630)
- Agreement: Cohen's kappa = 0.83 over all aspects, called "almost perfect agreement". — [arXiv 2210.11630](https://arxiv.org/abs/2210.11630)
- Not found in the text: an ethics statement, blinding, or a disagreement-resolution step. The statistics are descriptive only (% "yes" per error message and per condition). — [arXiv 2210.11630](https://arxiv.org/abs/2210.11630)

**(2) Hellas et al., "Exploring the Responses of Large Language Models to Beginner Programmers' Help Requests" (ICER 2023 V1, DOI 10.1145/3568813.3600139)**
- Items: from the 15 exercises with the most help requests, 10 requests were randomly sampled per exercise, giving 150 help requests. Model comparison used a pilot subset of 2 requests per exercise, giving 120 responses (2 models × 2 languages). — [arXiv 2306.05715](https://arxiv.org/abs/2306.05715)
- Rater: the issues in student code were annotated by "one of the researchers, who is the teacher responsible for the course, has more than a decade of experience in teaching introductory programming". The follow-up ITiCSE'24 paper describes the response annotations as made by a single "human evaluator with extensive experience in teaching programming". — [arXiv 2306.05715](https://arxiv.org/abs/2306.05715); [arXiv 2405.05253](https://arxiv.org/abs/2405.05253)
- Rubric: 7 binary aspects. Does the response:
  - "identif[y] and mention at least one actual issue"
  - "identif[y] and mention all actual issues"
  - "identif[y] any non-existent issues"
  - include "duplicate or superfluous content"
  - "include code"
  - include code that "can be considered a model solution"
  - include "any automated tests"

  Each was categorized "as either 'yes' or 'no'". Free-form notes were also thematically analyzed (109 of 150 responses received at least one note). — [arXiv 2306.05715](https://arxiv.org/abs/2306.05715)
- Ethics (verbatim): "The research was conducted in compliance with the local ethical principles and guidelines. To avoid leaking any personal information to third-party services, we manually vetted the inputs that we fed to the LLMs". — [arXiv 2306.05715](https://arxiv.org/abs/2306.05715)
- No inter-rater agreement is reported, since there was a single rater. — [arXiv 2306.05715](https://arxiv.org/abs/2306.05715)

**(3) Phung et al., "Generative AI for Programming Education: Benchmarking ChatGPT, GPT-4, and Human Tutors" (ICER 2023 V2 poster; full version on arXiv)**
- Venue: "This article is a full version of the poster (extended abstract) from ICER'23." — [arXiv 2306.17156](https://arxiv.org/abs/2306.17156)
- Items: 25 instances per scenario (5 Python problems × 5 real buggy programs) and 3 methods (ChatGPT, GPT-4, Tutor). — [arXiv 2306.17156](https://arxiv.org/abs/2306.17156)
- Raters: "nevals = 2 human evaluators", who are the same two experts that produced the Tutor outputs. "Each … independently annotates the quality of generated outputs for ChatGPT, GPT-4, and Tutor (only for the nTutor − 1 human experts by excluding the evaluator themselves)". This means raters knew which method produced each output, so there was no blinding by design. — [arXiv 2306.17156](https://arxiv.org/abs/2306.17156)
- Repair rubric:
  - Correct (binary, checked by automated test suites)
  - EditTokens (token-based edit distance to the buggy program)
  - These attributes were "computed … using automated scripts without requiring manual annotation"

  Source: [arXiv 2306.17156](https://arxiv.org/abs/2306.17156)
- Hint rubric (all binary):
  - HCorrect
  - HInformative ("useful information to help the student resolve bug(s)")
  - HConceal ("not too detailed, so the student would also have to reason about implementing the fixes")
  - HComprehensible ("easy to understand, presented in a readable format, and doesn't contain redundant information")
  - HOverall (= all four above)
  - ECorrect (the explanation's reasoning is correct)
  - Overall (= HOverall AND ECorrect)

  Attributes default to 0 when the hint is incorrect. — [arXiv 2306.17156](https://arxiv.org/abs/2306.17156)
- Program-completion rubric includes **ContextKept** (binary, manually annotated): "whether the completed program keeps the context of the partial program, e.g., variable names". This is an explicit "preserve the student's code" dimension. — [arXiv 2306.17156](https://arxiv.org/abs/2306.17156)
- Statistics: results are aggregated over instances, then averaged across the 2 evaluators and reported as "mean (stderr)". No kappa is reported and no ethics statement was found. — [arXiv 2306.17156](https://arxiv.org/abs/2306.17156)

**(4) Koutcheme et al., "Open Source Language Models Can Provide Feedback: Evaluating LLMs' Ability to Help Students Using GPT-4-As-A-Judge" (ITiCSE 2024, DOI 10.1145/3649217.3653612)**
- Items: the same 150 help requests and GPT-3.5 responses as Hellas et al., with the single expert's labels reused as ground truth. — [arXiv 2405.05253](https://arxiv.org/abs/2405.05253)
- Rubric (binary):
  - completeness: "Identifies and mentions all actual issues"
  - perceptivity: "Identifies and mentions at least one actual issue"
  - selectivity: "Does not identify non-existent issues"

  Source: [arXiv 2405.05253](https://arxiv.org/abs/2405.05253)
- Agreement between GPT-4 and the human expert (Cohen's kappa): completeness 0.48, perceptivity 0.22, selectivity 0.40, described as "moderate" (completeness, selectivity) and "fair" (perceptivity). GPT-4 showed a positive bias: it labelled 113/150 complete vs 82 by the human, and 106 selective vs 78. — [arXiv 2405.05253](https://arxiv.org/abs/2405.05253)
- Ethics: "We acquired the data from the authors of [6] for our study, following the national protocols for ethical research." — [arXiv 2405.05253](https://arxiv.org/abs/2405.05253)
- Authors' stance: "automated evaluation of feedback is not yet ready to rely exclusively on LLM evaluation – human judgment is still necessary". — [arXiv 2405.05253](https://arxiv.org/abs/2405.05253)

**(5) Azaiz, Kiesler & Strickroth, "Feedback-Generation for Programming Exercises With GPT-4" (ITiCSE 2024 V.1)**
- Items: 55 Java submissions. 33 were "pseudo-randomly sampled" for task 1 and 22 "randomly" for task 2. Each was submitted to GPT-4 Turbo 3 times "in randomized order", giving 165 feedback texts. — [arXiv 2403.04449](https://arxiv.org/abs/2403.04449)
- Method: "qualitative thematic analysis" with "deductive-inductive category-building" (Mayring), starting from a prior classification and producing a codebook (Table 1). — [arXiv 2403.04449](https://arxiv.org/abs/2403.04449)
- Raters: "Three computing education researchers with extensive expertise in correction and providing feedback as well as qualitative analysis." Reliability was handled through consensus rather than kappa: "To ensure an intersubjective understanding and reliability, all three authors were involved in the classification." — [arXiv 2403.04449](https://arxiv.org/abs/2403.04449)
- Ethics/consent: "This research utilizes submissions from students who explicitly consented to their use (695 out of about 900 students). Consent was fully voluntary, with no negative consequences or disadvantages." The consent covers the student data, not the raters. — [arXiv 2403.04449](https://arxiv.org/abs/2403.04449)

**(6) Koutcheme et al., "Evaluating Language Models for Generating and Judging Programming Feedback" (SIGCSE TS 2025 per the repository record)**
- Venue: the record lists the Proceedings of the 56th ACM SIGCSE TS. — [JYX record](https://jyx.jyu.fi/jyx/Record/jyx_123456789_100319)
- Items: 8 models × 57 benchmark programs = 456 outputs. All 456 were annotated. — [arXiv 2407.04873](https://arxiv.org/abs/2407.04873)
- Raters: "two annotators (two paper authors who are expert Python programmers)". — [arXiv 2407.04873](https://arxiv.org/abs/2407.04873)
- Procedure:
  - Both annotators independently annotated a calibration subset of 8 × 11 = 88 outputs (11 of the 57 problems).
  - Cohen's kappa on that subset was 0.54 ("moderate").
  - "After comparing annotations and resolving conflicts, the remaining feedback examples were split equally between the two annotators", so each remaining item was single-rated.

  Source: [arXiv 2407.04873](https://arxiv.org/abs/2407.04873)
- Rubric (binary, 6 criteria):
  - EA, Explanation Accurate
  - ES, Explanation Selective: "does not mention non-existent (or non-relevant) bugs"
  - EC, Explanation Clear: "easy to understand for a novice programmer … independent of the correctness"
  - FA, Fixes Accurate
  - FS, Fixes Selective: "no unnecessary or irrelevant changes are outlined"
  - FC, Fixes Clear: "succinct and mention the unique changes to perform in the code"

  Guideline: match each ground-truth bug to the generated explanations; any unmatched generated bug sets ES = false. — [arXiv 2407.04873](https://arxiv.org/abs/2407.04873)
- Self-reported limitation: "a moderate inter-rater reliability score (0.54), and our grading criteria did not use actual students (the intended audience) to rate the clarity of the outputs." No ethics statement was found. — [arXiv 2407.04873](https://arxiv.org/abs/2407.04873)

**(7) Koutcheme, Sarsa, Leinonen, Haaranen & Hellas, "Evaluating Distance Measures for Program Repair" (ICER 2023 V1, DOI 10.1145/3568813.3600130)**
- This study had experts *produce* reference repairs rather than rate them. "A team of five experts annotated a subset of the Dublin [dataset]". Each expert, for their assigned exercises, "was tasked to write the repair to the buggy solution that passes the unit tests while requiring minimal amounts of changes … our goal was to keep as much of the student strategy as possible." — [ICER'23 paper (DOI)](https://doi.org/10.1145/3568813.3600130)
- Sampling and exclusions:
  - Near-duplicates were collapsed by AST-structure grouping, and one representative was annotated per group.
  - Programs that were "partial", that showed a misunderstood scope, or whose strategy was "incomprehensible or … extremely complex" (cases where "instructors would generally recommend rewriting … from scratch") were marked and omitted.
  - Expert repairs were re-executed against the unit tests.

  Source: [ICER'23 paper](https://doi.org/10.1145/3568813.3600130)
- Use: distance measures were evaluated by whether they rank the expert repair closer to the buggy program than a Refactory repair ("Ranking Error", "classification error"). The authors acknowledge "multiple annotations or corrections were possible … different annotators might have come up with different solutions." — [ICER'23 paper](https://doi.org/10.1145/3568813.3600130)

**(8) Pitts, Pandya, Rank, Bhatt, Hoq & Akram, "Automated Program Repair of Uncompilable Student Code" (SIGCSE TS 2026 V.2, 2-page poster/abstract)**
- Items: 2 problems randomly selected from 50 CodeWorkout problems, then 100 uncompilable Java submissions randomly sampled. These were run under 3 LLMs × 2 prompt contexts, giving 600 repaired outputs. — [SIGCSE TS 2026 V.2](https://doi.org/10.1145/3770761.3777323)
- Raters: "four experts independently annotated all repaired outputs". — [SIGCSE TS 2026 V.2](https://doi.org/10.1145/3770761.3777323)
- Rubric (binary):
  - **Structural Preservation (SP)**: "1 if the repaired code maintained the original control flow"
  - **Logical Preservation (LP)**: "1 if the repair consisted only of syntactic edits … 0 if the repair changed the logical or semantic structure"

  Source: [SIGCSE TS 2026 V.2](https://doi.org/10.1145/3770761.3777323)
- Agreement procedure: experts "coded an initial subset (10% of the repaired programs) jointly to align on definitions, then proceeded independently, calculating Cohen's Kappa (κ) after each round. When agreement fell below 0.80 … disagreements were resolved and the codebook was refined. Inter-rater agreement exceeding κ = 0.80 was achieved on the second round". — [SIGCSE TS 2026 V.2](https://doi.org/10.1145/3770761.3777323)
- Statistics: chi-square tests of independence. Example: SP by model χ²(2, N=579) = 18.10, p < 0.001. Normalized Levenshtein edit distance was also reported. — [SIGCSE TS 2026 V.2](https://doi.org/10.1145/3770761.3777323)

**(9) Adjacent venue, closest design to pairwise preference: Brown et al., "Howzat? Appealing to Expert Judgement for Evaluating Human and AI Next-Step Hints for Novice Programmers" (ACM TOCE 2025)**
- Raters: external Java educators recruited "via mailing lists, forums and social media", with "no reward for participation". 85 signed up and 41 completed the task (the abstract says 44 were recruited). — [arXiv 2411.18151](https://arxiv.org/abs/2411.18151)
- Items: 4 student "Snapshots" × 25 hints = 100 hints. The hints came from LLMs and 5 experienced human educators. — [arXiv 2411.18151](https://arxiv.org/abs/2411.18151)
- Method: adaptive comparative judgement (pairwise "which of these two hints is better") on the No More Marking platform. About 250 comparisons per Snapshot, split across 8 judges at 31 comparisons each. Each judge saw only one Snapshot to limit load. — [arXiv 2411.18151](https://arxiv.org/abs/2411.18151)
- Blinding: participants ranked hints without being told how they were generated. — [arXiv 2411.18151](https://arxiv.org/abs/2411.18151)
- No detailed rubric was given. The prompt to judges was "Imagine that you are helping a student … We want you to determine which is the best hint to give in each circumstance." — [arXiv 2411.18151](https://arxiv.org/abs/2411.18151)
- Rationale for pairwise over absolute ratings: "Is everything just 7/10? Can participants remain internally consistent, and can the scale be consistent between participants?" — [arXiv 2411.18151](https://arxiv.org/abs/2411.18151)
- Agreement: comparative-judgement "Reliability" per Snapshot was 0.73, 0.76, 0.76 and 0.60, and "A reliability of 0.7 is generally considered sufficient". Infit was used per judge and per item. — [arXiv 2411.18151](https://arxiv.org/abs/2411.18151)
- Effort and quality checks: left/right choice bias, and time per judgement (≈75 s for the first and ≈50 s for the second, then falling). — [arXiv 2411.18151](https://arxiv.org/abs/2411.18151)
- Ethics and pre-registration: "The study was approved according to the ethics procedures of King's College London, approval number MRA-23/24-41449." The design was pre-registered on OSF and deviations are listed. — [arXiv 2411.18151](https://arxiv.org/abs/2411.18151)
- Analysis: hint ranks were analysed against extracted characteristics (length, reading level, sentiment, correctness, feedback type) with a random forest. — [arXiv 2411.18151](https://arxiv.org/abs/2411.18151)

**Additional (snippet only, venue unconfirmed): TAMIGO (arXiv 2407.16805)**
- Two researchers rated LLM-generated code feedback. After calibration reached ICC3K > 0.75, "a total of 66 code snippets (33 per researcher)" were assessed. — [arXiv 2407.16805 (search snippet)](https://arxiv.org/pdf/2407.16805)

### Inferences
- The modal protocol in SIGCSE/ITiCSE/ICER papers has these parts:
  - 2 author-raters with teaching experience
  - a short calibration (joint discussion of 3 items, or 10–20% of the set)
  - independent binary coding
  - Cohen's kappa reported once
  - descriptive percentages, sometimes with a χ² test
- Full double-rating of every item is not universal. The ITiCSE/SIGCSE 2025 Koutcheme design double-rated only a calibration subset and then split the remaining items, and it was accepted with κ = 0.54.
- Single-rater studies (Hellas, ICER'23) were accepted when the rater was a highly experienced course teacher. Later work (Koutcheme ITiCSE'24) reused those labels as ground truth.
- Blinding is rarely described. Phung et al. were explicitly unblinded, since raters also authored the Tutor outputs and only excluded their own. The only clearly blinded study is the external-judge pairwise study (Howzat).

### Gaps
- I found no qualifying ICSE-SEET (2022–2026) or Koli Calling paper with a rating study of generated repairs or hints. The searches surfaced none, and I could not access program pages to enumerate them. This does not establish that none exist.
- The Leinonen et al. venue (SIGCSE TS 2023) comes from the paper's known publication record, not from the fetched arXiv text.
- None of the eight venue papers reports rater time or effort in hours. Only Howzat reports per-judgement timings.
- I did not verify the published ACM versions for differences from the arXiv versions (e.g., added ethics statements).

## Q2. Typical minimum scale: raters × items in accepted papers

### Takeaway
Accepted CS-ed papers use **1–4 raters** and **25–600 rated outputs**. Raters are usually authors, items are usually tens to a few hundred outputs drawn from 25–150 student programs, and binary criteria are applied to each. "2 raters × ~80–160 items, with kappa on all or a calibration subset" is well inside accepted practice. ICER posters/V2 and SIGCSE V.2 abstracts accept even smaller designs (2 raters × 25 instances per scenario).

### Cited Findings
| Paper (venue) | Raters | Rated items | Double-rated? | Agreement reported |
|---|---|---|---|---|
| Leinonen et al. (SIGCSE TS'23) | 2 researchers (teaching experience) | 81 explanations (9 PEMs × 3 categories × 3 generations) | yes, all | Cohen κ = 0.83 |
| Hellas et al. (ICER'23 V1) | 1 (course teacher, >10 yrs) | 150 GPT-3.5 responses (+120 in model-comparison pilot) | no | none |
| Phung et al. (ICER'23 V2 poster) | 2 experts (also the Tutor authors) | 25 instances × 3 methods per scenario | yes (each rates others) | none; mean (stderr) over raters |
| Koutcheme et al. (ITiCSE'24) | 1 human expert (reused) vs GPT-4 | 150 | n/a | κ(GPT-4, human) 0.48/0.22/0.40 |
| Azaiz et al. (ITiCSE'24) | 3 authors (consensus coding) | 165 feedback texts (55 submissions × 3 runs) | consensus | none |
| Koutcheme et al. (SIGCSE TS'25) | 2 authors | 456 outputs; 88 double-rated | calibration subset only | κ = 0.54 |
| Koutcheme et al. (ICER'23 V1) | 5 experts (wrote reference repairs) | subset of Dublin dataset (deduplicated by AST) | no | none |
| Pitts et al. (SIGCSE TS'26 V.2) | 4 experts | 600 repairs (100 submissions × 6 conditions) | yes, all | κ > 0.80 after 2 rounds |
| Brown et al. (TOCE'25, adjacent) | 41 external educators (≈8 per snapshot) | 100 hints, ≈250 pairwise comparisons per snapshot | pairwise by many judges | CJ reliability 0.60–0.76 |

Sources:
- Leinonen et al.: [arXiv 2210.11630](https://arxiv.org/abs/2210.11630)
- Hellas et al.: [arXiv 2306.05715](https://arxiv.org/abs/2306.05715)
- Phung et al.: [arXiv 2306.17156](https://arxiv.org/abs/2306.17156)
- Koutcheme et al. (ITiCSE'24): [arXiv 2405.05253](https://arxiv.org/abs/2405.05253)
- Azaiz et al.: [arXiv 2403.04449](https://arxiv.org/abs/2403.04449)
- Koutcheme et al. (SIGCSE TS'25): [arXiv 2407.04873](https://arxiv.org/abs/2407.04873)
- Koutcheme et al. (ICER'23): [DOI 10.1145/3568813.3600130](https://doi.org/10.1145/3568813.3600130)
- Pitts et al.: [DOI 10.1145/3770761.3777323](https://doi.org/10.1145/3770761.3777323)
- Brown et al.: [arXiv 2411.18151](https://arxiv.org/abs/2411.18151)

- In comparative judgement, a meta-analysis (Verhavert & De Maeyer, as cited by Howzat) "found that the number of judges did not impact reliability". For expert judges, "26 to 37 presentations per item are needed" for 90% reliability, which means ranking N items needs ≈13N judgements. The platform used recommends 10 comparisons per item. — [arXiv 2411.18151](https://arxiv.org/abs/2411.18151)
- In CSCW/HCI qualitative papers from 2016–2018, IRR was reported in only "around 1/9 of qualitative papers". Where it was reported, Cohen's kappa was the most common statistic (17/32, 53.1%), followed by Fleiss' kappa (9%) and Krippendorff's alpha (9%). — [McDonald, Schoenebeck & Forte, CSCW 2019](https://yardi.people.si.umich.edu/pubs/Schoenebeck_Reliability_CSCW19.pdf)

### Inferences
- A defensible design for a full paper (e.g., ICSE-SEET or ITiCSE) would be 2 independent expert raters on all items, with N ≈ 50–150 repairs per condition, plus a calibration round and kappa. This is at or above what the accepted papers above report. A poster or V2 track accepts less.
- Reviewers in these venues appear to accept a moderate κ (0.5) when it is reported transparently and listed as a limitation (Koutcheme SIGCSE'25). The strongest repair-specific precedent (Pitts SIGCSE'26) used κ ≥ 0.80 as its target.

### Gaps
- None of the venue papers reports a formal sample-size or power justification for the number of rated items. Only Howzat justifies its number of comparisons, citing the CJ meta-analysis.

## Q3. Common rubric dimensions for repairs and hints as feedback

### Takeaway
The recurring dimensions are:
- **correctness/accuracy** (often test-based for repairs)
- **selectivity**, i.e. no spurious or unnecessary changes or issues, which is the closest analogue to minimality
- **completeness** (all issues addressed)
- **clarity/comprehensibility for a novice**
- **not giving away the solution** (conceal / no model solution)
- for repairs specifically, **preservation of the student's code**: control flow/structure, logic, context and variable names, minimal edits

"Would you show this to a student" is used as a holistic pairwise question (Howzat) or as an "improvement over original" judgement (Leinonen), not as a Likert item.

### Cited Findings
- Correctness:
  - "Correct (binary) … we use automated test suites" — [Phung et al.](https://arxiv.org/abs/2306.17156)
  - "Fix correct" — [Leinonen et al.](https://arxiv.org/abs/2210.11630)
  - "FA – Fixes Accurate" — [Koutcheme et al. SIGCSE'25](https://arxiv.org/abs/2407.04873)
- Minimality / closeness:
  - EditTokens (token edit distance to the buggy program) and EditLines — [Phung et al.](https://arxiv.org/abs/2306.17156)
  - normalized Levenshtein — [Pitts et al.](https://doi.org/10.1145/3770761.3777323)
  - "FS – Fixes Selective: no unnecessary or irrelevant changes are outlined" — [Koutcheme et al. SIGCSE'25](https://arxiv.org/abs/2407.04873)
  - expert reference repairs written to require "minimal amounts of changes … keep as much of the student strategy as possible" — [Koutcheme et al. ICER'23](https://doi.org/10.1145/3568813.3600130)
- Preservation of the student's approach:
  - Structural Preservation ("maintained the original control flow") and Logical Preservation ("only … syntactic edits") — [Pitts et al. SIGCSE TS'26](https://doi.org/10.1145/3770761.3777323)
  - ContextKept ("keeps the context of the partial program, e.g., variable names") — [Phung et al.](https://arxiv.org/abs/2306.17156)
  - The ICER'23 distance paper frames it as "the need to ensure that the found fixes remain understandable for the student who wrote the code … a reference solution [is] … not always an understandable fix due to e.g. using a different approach". — [Koutcheme et al. ICER'23](https://doi.org/10.1145/3568813.3600130)
- Issue coverage and hallucination:
  - perceptivity (≥1 actual issue), completeness (all issues), selectivity ("Does not identify non-existent issues") — [Koutcheme et al. ITiCSE'24](https://arxiv.org/abs/2405.05253); [Hellas et al. ICER'23](https://arxiv.org/abs/2306.05715)
- Understandability:
  - HComprehensible — [Phung et al.](https://arxiv.org/abs/2306.17156)
  - EC/FC "easy to understand for a novice programmer … independent of the correctness" — [Koutcheme et al. SIGCSE'25](https://arxiv.org/abs/2407.04873)
  - "Comprehensible" — [Leinonen et al.](https://arxiv.org/abs/2210.11630)
- Usefulness for learning / not revealing the answer:
  - HInformative and HConceal ("not too detailed, so the student would also have to reason about implementing the fixes") — [Phung et al.](https://arxiv.org/abs/2306.17156)
  - "includes code that can be considered a model solution" — [Hellas et al.](https://arxiv.org/abs/2306.05715)
  - "Improvement over the original … added value (from a novice programmer standpoint)" — [Leinonen et al.](https://arxiv.org/abs/2210.11630)
- Holistic "best to show a student" judgement: "Imagine that you are helping a student … determine which is the best hint to give". — [Howzat, TOCE'25](https://arxiv.org/abs/2411.18151)
- Gating convention: dependent attributes are set to 0 when the primary attribute fails (e.g., HInformative = 0 if the hint is incorrect), and an "Overall" score requires all criteria. — [Phung et al.](https://arxiv.org/abs/2306.17156)

### Inferences
- For a test-validated, LLM-free repair tool, correctness can be automated, as Phung did. Human ratings would then focus on:
  1. structural/logic preservation of the student's approach (Pitts SP/LP)
  2. selectivity or unnecessary changes (Koutcheme FS)
  3. understandability of the diff for the student
  4. a holistic "would show to student" or pairwise preference vs a baseline (Howzat-style)
- Binary criteria dominate. I found no venue paper in this set that used Likert scales for repair or feedback quality.

### Gaps
- I found no paper in these venues that rates *automated program repairs as feedback* with a "would you show this to a student" Likert item. Phrasings had to be assembled from the hint and feedback studies.

## Q4. Ethics: when expert-rating studies need IRB/ethics approval, the ACM policy, and how papers phrase it

### Takeaway
The ACM policy (approved 15 Aug 2021) applies to all ACM venues. It adopts the NIH definition of human-subjects research and requires review "where local ethical review boards are required". Where no such regulations exist, authors must show compliance with the listed principles.
- Author-raters annotating artifacts: papers typically give **no IRB statement**, or a generic compliance line.
- Studies recruiting external educators: report formal approval (Howzat: KCL approval number).
- Student data: the ethics language mostly concerns its use (consent, national protocols, vetting before sending to third-party LLMs).

### Cited Findings
- "ACM Publications Policy on Research Involving Human Participants and Subjects — Approved by ACM Publications Board on August 15, 2021." — [ACM policy](https://www.acm.org/publications/policies/research-involving-human-participants-and-subjects)
- Definition: "ACM adopts the definition of Human Subjects Research used by the US National Institutes of Health as 'Research involving a living individual about whom data or biospecimens are obtained/used/studied/analyzed through interaction/intervention, or identifiable, private information is used/studied/analyzed/generated'". — [ACM policy](https://www.acm.org/publications/policies/research-involving-human-participants-and-subjects)
- Required principles:
  - "minimization of potential harms"
  - "protection for the privacy and right to self-determination"
  - "adhering to the principle of informed consent"
  - "adhering to the principle of justice"
  - alignment with "the ACM Code of Ethics … The Declaration of Helsinki, The Belmont Report, and The Common Rule"

  Source: [ACM policy](https://www.acm.org/publications/policies/research-involving-human-participants-and-subjects)
- "Where such research is conducted in countries where no such local governing laws and regulations related to human participant and subject research exist, Authors must at a bare minimum be prepared to show compliance with the above detailed principles." — [ACM policy](https://www.acm.org/publications/policies/research-involving-human-participants-and-subjects)
- "Where local ethical review boards are required, authors are responsible for having their research reviewed and approved by such boards … ACM may require documentary evidence of such approval at any time following submission of the Work and prior to or after publication." — [ACM policy](https://www.acm.org/publications/policies/research-involving-human-participants-and-subjects)
- Program chairs may add stricter, venue-specific rules, which "must be clearly communicated in the Instructions for Authors … and … Calls for Papers". Penalties range up to "a 'Note of Concern' … or a Retraction". — [ACM policy](https://www.acm.org/publications/policies/research-involving-human-participants-and-subjects)
- The SIGCSE TS 2026 policies page only links to the ACM policy and the ACM Code of Ethics. I found no stricter SIGCSE-specific human-subjects rule there. — [SIGCSE TS 2026 policies](https://sigcse2026.sigcse.org/info/policies)
- Phrasing examples:
  - Hellas et al. (ICER'23): "The research was conducted in compliance with the local ethical principles and guidelines. To avoid leaking any personal information to third-party services, we manually vetted the inputs…" — [arXiv 2306.05715](https://arxiv.org/abs/2306.05715)
  - Koutcheme et al. (ITiCSE'24): "We acquired the data … following the national protocols for ethical research." — [arXiv 2405.05253](https://arxiv.org/abs/2405.05253)
  - Azaiz et al. (ITiCSE'24): "submissions from students who explicitly consented to their use (695 out of about 900 students). Consent was fully voluntary, with no negative consequences or disadvantages." — [arXiv 2403.04449](https://arxiv.org/abs/2403.04449)
  - Brown et al. (TOCE'25, external educators recruited online): "approved according to the ethics procedures of King's College London, approval number MRA-23/24-41449" plus OSF pre-registration. — [arXiv 2411.18151](https://arxiv.org/abs/2411.18151)
  - Leinonen (SIGCSE'23), Phung (ICER'23 V2) and Koutcheme (SIGCSE'25) had author-raters only, and I found no ethics statement in their arXiv texts. — [arXiv 2210.11630](https://arxiv.org/abs/2210.11630); [arXiv 2306.17156](https://arxiv.org/abs/2306.17156); [arXiv 2407.04873](https://arxiv.org/abs/2407.04873)

### Inferences
- Under the NIH definition the ACM adopts, author-experts rating anonymized code artifacts are arguably not "living individual[s] about whom data … are obtained". This matches the absence of IRB statements in author-rater papers.
- Recruiting non-author TAs or instructors and collecting their judgements, timings or survey answers moves closer to the definition. Howzat sought formal approval for exactly that.
- For a histra-style study (public CodeNet/AtCoder submissions plus a few TA raters), a safe phrasing would combine:
  - the source and public/anonymized status of the student code
  - a statement that the raters are authors, or that external raters gave informed consent
  - the local IRB determination ("exempt" or "not human-subjects research"), or for Korea the relevant institutional review
- This is inference, not something stated by a source.

### Gaps
- I could not retrieve an authoritative IRB or Common Rule guidance document stating that expert opinions about artifacts are "not human subjects research". The search returned only index pages, so this point rests on the NIH definition quoted in the ACM policy.
- I did not find whether ICSE (IEEE/ACM co-sponsored) or the SEET track adds stricter ethics-statement requirements.

## Q5. Methodological guidance: agreement thresholds, agreement on pairwise preferences, sample-size reasoning

### Takeaway
Thresholds cited in practice:
- Landis & Koch bands (0.41–0.60 moderate, 0.61–0.80 substantial, >0.80 almost perfect), which their authors call "clearly arbitrary"
- Krippendorff's α ≥ 0.800, with 0.667 as the "lowest conceivable limit"
- McHugh's stricter reading (κ < 0.60 inadequate, ≥ 0.80 strong)
- the CS-ed repair precedent (Pitts) of iterating calibration until κ > 0.80

For pairwise preferences, the CS-ed precedent is comparative judgement with scale-separation "Reliability" ≥ 0.7 and per-judge infit. Sample-size reasoning appears only for CJ (26–37 presentations per item).

### Cited Findings
- Landis & Koch's 1977 scale ("0.0–0.2 Slight; 0.21–0.4 Fair; 0.41–0.6 Moderate; 0.61–0.8 Substantial; 0.81–1 Almost Perfect") "has been cited roughly 46,000 times … but they acknowledge that their scale is 'clearly arbitrary'". — [McDonald et al., CSCW 2019](https://yardi.people.si.umich.edu/pubs/Schoenebeck_Reliability_CSCW19.pdf)
- Krippendorff (quoted): "it is customary to require α ≥ .800. Where tentative conclusions are still acceptable, α ≥ .667 is the lowest conceivable limit". — [McDonald et al., CSCW 2019](https://yardi.people.si.umich.edu/pubs/Schoenebeck_Reliability_CSCW19.pdf)
- McHugh's interpretation table: κ 0–.20 None; .21–.39 Minimal; .40–.59 Weak; .60–.79 Moderate; .80–.90 Strong; >.90 Almost Perfect. She argues "Cohen's suggested interpretation may be too lenient for health related studies because it implies that a score as low as 0.41 might be acceptable." — [McHugh 2012, Biochemia Medica (PMC)](https://pmc.ncbi.nlm.nih.gov/articles/PMC3900052/)
- When IRR is and isn't appropriate:
  - IRR is useful "for ensuring consistency across multiple coders, for applying existing codebooks, and when researchers aim to report quantitative results".
  - IRR is not desirable "when developing codes is part of the process, when there is a single researcher … or when coding requires little interpretation".

  Source: [McDonald et al., CSCW 2019](https://yardi.people.si.umich.edu/pubs/Schoenebeck_Reliability_CSCW19.pdf)
- Measure choice: one coding study (as reported by McDonald et al.) used Fleiss for nominal/categorical data and Krippendorff for ordinal data. — [McDonald et al., CSCW 2019](https://yardi.people.si.umich.edu/pubs/Schoenebeck_Reliability_CSCW19.pdf)
- CS-ed repair precedent: calibration on 10% jointly, then independent rounds with κ computed after each; below 0.80 "disagreements were resolved and the codebook was refined"; >0.80 was reached on round 2. — [Pitts et al., SIGCSE TS 2026](https://doi.org/10.1145/3770761.3777323)
- Pairwise agreement: comparative judgement offers "two measures for inter-rater reliability … Reliability (a per-task measure) and Infit (a per-judge or per-item measure)", and "A reliability of 0.7 is generally considered sufficient". Further checks: left-option bias against a binomial null, and time per judgement. — [Howzat, TOCE'25](https://arxiv.org/abs/2411.18151)
- Human–human agreement as a ceiling for LLM judges: Koutcheme et al. cite prior work (Zheng et al.) that "GPT-4 can reach over 80% agreement with humans, matching the level of inter-agreement between humans", i.e. raw pairwise percent agreement. — [arXiv 2405.05253](https://arxiv.org/abs/2405.05253)
- Skewed labels: with skewed binary labels, kappa can be low even when accuracy is high. Perceptivity accuracy was 0.85 with κ = 0.22, and the authors compare against a majority-class dummy model. — [arXiv 2405.05253](https://arxiv.org/abs/2405.05253)
- Sample size for comparative judgement: "for 90% reliability, 26 to 37 presentations per item are needed … ranking of N items requires 13N judgements". The adaptive CJ platform recommends 10 comparisons per item. — [Howzat, TOCE'25](https://arxiv.org/abs/2411.18151)

### Inferences
- Reporting expectations in these venues:
  - per-criterion κ (not only pooled)
  - prevalence of each label, because kappa is sensitive to skew
  - the calibration/resolution procedure
- If the study is pairwise (patch A vs patch B, e.g., histra vs a baseline, randomized left/right and blinded to method), the precedents are:
  - percent agreement (and κ on the 3-way A/B/tie label) between 2 raters
  - with many judges, Bradley–Terry / comparative-judgement reliability ≥ 0.7

### Gaps
- None of the venue papers states a principled sample-size calculation for kappa or for the number of rated repairs. I did not retrieve a kappa sample-size reference (e.g., Sim & Wright 2005), so no number can be cited for it here.
- Apart from comparative judgement, I found no CS-ed source that prescribes how to compute agreement on 2-rater pairwise preferences with ties (e.g., weighted κ on {A, tie, B}).
