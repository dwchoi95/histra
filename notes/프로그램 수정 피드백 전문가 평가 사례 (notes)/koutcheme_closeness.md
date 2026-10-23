# Human/expert evaluation of repair "closeness" and feedback quality: the Koutcheme/Hellas/Leinonen line, plus Pitts et al. (SIGCSE TS 2026)

Full texts read (all primary sources): ICER'23 [ICER23](https://acris.aalto.fi/ws/portalfiles/portal/122216612/Evaluating_Distance_Measures_for_Program_Repair.pdf) · AIED'23 [AIED23](https://aaltodoc.aalto.fi/items/b3f949b0-efa5-4a61-8cf9-6fce7fc17a8d) (self-archived; DOI 10.1007/978-3-031-36272-9_74) · GAIED'23/arXiv [Bench](https://arxiv.org/pdf/2405.05347) · ITiCSE'24 [ITiCSE24](https://arxiv.org/pdf/2405.05253) · BEA'24 [BEA24](https://aclanthology.org/2024.bea-1.15.pdf) · SIGCSE TS'25 [SIGCSE25](https://arxiv.org/pdf/2407.04873) · BEA'25 [BEA25](https://aclanthology.org/2025.bea-1.41.pdf) · SIGCSE TS'26 poster [Pitts26](https://arxiv.org/pdf/2510.06187) (v3).

Quick map (details and citations below):

| Paper | Human/expert involvement | Closeness measure |
|---|---|---|
| ICER'23 distance measures | 5 experts each **wrote** one minimal repair per buggy program (reference); no rating, no pairwise judgments, no IAA | Evaluated 10 metrics by how well each retrieves the expert repair; ROUGE best |
| AIED'23 infilling | None | Avg. sequence edit distance vs Refactory |
| Benchmarking (GAIED'23) | None ("did not necessitate manual annotations") | rouge@k |
| ITiCSE'24 GPT-4-as-judge | Reused 1 expert's binary labels on 150 GPT-3.5 feedbacks; GPT-4 validated against them | n/a (feedback) |
| BEA'24 repair-as-proxy | None (GPT-4 judge, unvalidated here) | ROUGE-L |
| SIGCSE TS'25 generate/judge | 2 author-annotators, 456 outputs, 6 binary criteria, κ=0.54 calibration | n/a (feedback; "selective"= no unnecessary changes) |
| BEA'25 DRO | None (2-LLM jury, unanimity); explicit limitation | ROUGE (as RL reward) |
| Pitts SIGCSE TS'26 | 4 experts, all 600 repairs, binary Structural/Logic Preservation, κ>0.80 | Normalized Levenshtein + human SP/LP |

## Q1. Raters: who, how many, recruitment; LLM-as-judge and its validation

### Takeaway
Only two papers in scope used multiple human raters on outputs: Pitts et al. (4 experts) and Koutcheme et al. SIGCSE TS'25 (2 author-annotators). ICER'23 used 5 experts as *repair writers*, not raters. ITiCSE'24 validated GPT-4-as-judge against one prior expert's labels. BEA'24 and BEA'25 rely only on LLM judges and say human evaluation is lacking.

### Cited Findings
- **ICER'23**: "A team of five experts annotated a subset of the Dublin dataset, creating solutions for over a thousand erroneous programs written by students" (Abstract, p.495). Elsewhere they are called "educators" and "instructor corrections" (§4.1, §5.2.4). Recruitment and identity (e.g., whether they are the five authors) are not reported. The paper has five authors, but it does not say they were the annotators. — [ICER23](https://acris.aalto.fi/ws/portalfiles/portal/122216612/Evaluating_Distance_Measures_for_Program_Repair.pdf)
- **ICER'23**: "each expert was assigned one or multiple exercises to annotate" ("to keep consistency within assignments"), so each assignment was handled by one expert (§3.1, p.498). — [ICER23](https://acris.aalto.fi/ws/portalfiles/portal/122216612/Evaluating_Distance_Measures_for_Program_Repair.pdf)
- **AIED'23**: no human evaluation. The metrics are success rate and average sequence distance, compared with Refactory (§3–4). — [AIED23](https://aaltodoc.aalto.fi/items/b3f949b0-efa5-4a61-8cf9-6fce7fc17a8d)
- **Benchmarking (arXiv 2405.05347)**: "our evaluation procedure operates without assuming the existence of a single ground truth repair, and, in fact, did not necessitate manual annotations". The authors "focus on a fully automated evaluation approach" (§2). — [Bench](https://arxiv.org/pdf/2405.05347)
- **ITiCSE'24**: the human labels come from the prior study (Hellas et al.). Responses "were qualitatively analyzed and annotated by a human evaluator with extensive experience in teaching programming" (§3.1). That is one rater. GPT-4 was "applying the same rubric as the expert human rater" (§1). — [ITiCSE24](https://arxiv.org/pdf/2405.05253)
- **BEA'24**: "Given the scale of our dataset and the multitude of language models to assess, conducting human evaluation would be impractical. Therefore, we rely on automated evaluation using language models". GPT-4 gives binary labels (§3.3). Limitation: "Human evaluation is necessary to strengthen our results." — [BEA24](https://aclanthology.org/2024.bea-1.15.pdf)
- **SIGCSE TS'25**: "two annotators (two paper authors who are expert Python programmers) annotated all 456 model outputs" (§3.2). — [SIGCSE25](https://arxiv.org/pdf/2407.04873)
- **SIGCSE TS'25 (LLM-judge validation)**: each judge or jury was compared with the human labels, using weighted F0.5 and Cohen's κ (§3.3, Table 2). Without ground-truth bug descriptions (SAG), κ = 0.36 for Llama-3.1-70B, 0.34 for GPT-4o, 0.25 for GPT-4o-mini, 0.02 for GPT-3.5-turbo and 0.06 for the ensemble. With ground truth (GAG), κ rises by +0.29, +0.26, +0.27, +0.08 and +0.20 respectively. The authors write: "The low kappa scores in the SAG setting indicate that most model results could be due to random chance … models tend to be overly positive" (§4). — [SIGCSE25](https://arxiv.org/pdf/2407.04873)
- **BEA'25**: a 2-LLM jury (GPT-4o-mini and Gemini-2.0-flash) gives "binary decisions across all quality criteria" with "a strict unanimity policy: a criterion is marked correct only if both judges agree" (§4.6). The jury was not validated against humans in this paper. Its justification cites prior work: "GPT-4o-mini has been shown to perform on par with GPT-4o for evaluating feedback quality (Koutcheme et al., 2025)". Limitation: "our evaluation lacks human annotations, expert assessment, or qualitative analysis". — [BEA25](https://aclanthology.org/2025.bea-1.41.pdf)
- **Pitts et al.**: "four experts independently annotated all repaired outputs for Structural Preservation (SP) and Logical Preservation (LP)" (§2.2). Who the experts are and how they were recruited is not reported. — [Pitts26](https://arxiv.org/pdf/2510.06187)

### Inferences
- In this line of work the closeness of a repair to student code has never been rated by humans as a judged attribute. ICER'23 operationalises it as "expert writes the minimal repair". Pitts is the only paper with an explicit human rubric on preserving the student's structure and logic.
- 2–4 raters drawn from the authors or domain experts is the accepted norm for a small expert evaluation in this venue family. Recruitment details are routinely omitted.

### Gaps
- ICER'23 does not give the annotators' identities, recruitment or expertise beyond "experts", "educators" and "instructor".
- Pitts does not describe the expertise or recruitment of the four experts.
- I did not open the original Hellas et al. help-request study (the source of the ITiCSE'24 labels), so its single-rater protocol details are second-hand via ITiCSE'24.

## Q2. Items: how many, how sampled

### Takeaway
Item counts range from 88 calibration outputs to 1,854 expert-repaired programs. Every human study in scope used random or representative sampling at the program level, crossed with models or conditions.

### Cited Findings
- **ICER'23**: 10 Dublin assignments were chosen as single-function, "average level of complexity (i.e. involving looping or recursion and one or multiple conditional statements, excluding sorting algorithms)". The pool was 6,670 submissions (3,719 correct, 2,951 buggy). To avoid duplicates, variable names were normalised and programs grouped "based on an exact matching in their Abstract Syntax Tree (AST) structure". One representative per group (the most common original string) was annotated, and annotations were then "matched … to all other programs having the same structure". The final set is 1,854 buggy programs with instructor corrections from 305 students (§3.1, §4.1, Table 1). Some assignments were only partially annotated (footnote 2). Experiment 2 involves the 755 programs that Refactory repaired (Table 3). — [ICER23](https://acris.aalto.fi/ws/portalfiles/portal/122216612/Evaluating_Distance_Measures_for_Program_Repair.pdf)
- **ICER'23 exclusions**: "partial" programs, programs where the student "misunderstood the scope", and strategies that were "incomprehensible or unnecessarily – or even extremely – complex" were marked and omitted (§3.1). — [ICER23](https://acris.aalto.fi/ws/portalfiles/portal/122216612/Evaluating_Distance_Measures_for_Program_Repair.pdf)
- **ITiCSE'24**: "ten randomly sampled help requests for the top 15 programming exercises with the most help requests (150 help requests in total)". The course is a Dart MOOC at Aalto, and the labels cover GPT-3.5 responses only (§3.1). — [ITiCSE24](https://arxiv.org/pdf/2405.05253)
- **SIGCSE TS'25**: Socratic guidance benchmark, 57 assignments each with one incorrect program and a ground-truth bug description. 8 models × 57 = 456 outputs, with 11 problems (88 outputs) used for calibration (§3.1–3.2). — [SIGCSE25](https://arxiv.org/pdf/2407.04873)
- **BEA'25**: FalconCode test split of 711 incorrect programs from 62 assignments, evaluated by the LLM jury only (§4.1). — [BEA25](https://aclanthology.org/2025.bea-1.41.pdf)
- **Pitts et al.**: "two problems were randomly selected from a pool of 50 … From these, 100 uncompilable Java submissions were randomly sampled". 3 LLMs × 2 prompt contexts = 600 repaired outputs, and all were human-annotated (§2.2). The χ² tests use N = 579 for SP and N = 549 for LP (§3), so some outputs were apparently excluded. The paper does not explain why. — [Pitts26](https://arxiv.org/pdf/2510.06187)

### Inferences
- Deduplicating by normalised AST and propagating annotations to identical structures (ICER'23) is a cheap way to cover many trajectories with few expert hours.
- A full crossing of 100 programs × 6 systems (Pitts) yields 600 items per rater, which they report was feasible with 4 raters.

### Gaps
- Pitts does not explain the 600 → 579/549 drop. It may be non-compilable outputs or missing labels, but this is not stated.

## Q3. Rating dimensions, scales, exact rubric wording

### Takeaway
Every scale in scope is binary (yes/no per criterion). The closeness-related criteria are Pitts' SP/LP and SIGCSE'25's "Fixes Selective" (no unnecessary changes). ICER'23 has no scale: its instruction to experts defines closeness as minimal change that keeps the student's strategy.

### Cited Findings
- **ICER'23 expert instruction**: "each expert was tasked to write the repair to the buggy solution that passes the unit tests while requiring minimal amounts of changes. In other words, our goal was to keep as much of the student strategy as possible." Correctness check: "we re-executed each expert solution against the example unit tests … and re-repaired the ones that failed" (§3.1, pp.498–499). — [ICER23](https://acris.aalto.fi/ws/portalfiles/portal/122216612/Evaluating_Distance_Measures_for_Program_Repair.pdf)
- **ICER'23 problem framing**: the goal is to "find a working solution which best captures the student's intention from a pool of candidate solutions … we select the candidate repair which has the minimum distance to the buggy program". Evaluating metrics is cast "as an information retrieval problem" (§3.2.1). — [ICER23](https://acris.aalto.fi/ws/portalfiles/portal/122216612/Evaluating_Distance_Measures_for_Program_Repair.pdf)
- **Pitts et al. rubric (verbatim)**: "SP was coded as 1 if the repaired code maintained the original control flow and 0 otherwise. LP was coded as 1 if the repair consisted only of syntactic edits, such as adding missing delimiters or correcting variable names, and 0 if the repair changed the logical or semantic structure of the code." Other criteria: compilation success, and "Edit distance, computed using normalized Levenshtein distance, measured how closely the repair aligned with the original code" (§2.2). — [Pitts26](https://arxiv.org/pdf/2510.06187)
- **SIGCSE TS'25 rubric (verbatim, binary)**:
  - "EA - Explanation Accurate: the explanation identifies and correctly explains the bug in the student program."
  - "ES - Explanation Selective: the explanation does not mention non-existent (or non-relevant) bugs or issues."
  - "EC - Explanation Clear: … easy to understand for a novice programmer, presented in a readable format and contains the right amount of information."
  - "FA - Fixes Accurate: the required bug fixes are laid out and explained."
  - "FS - Fixes Selective: no unnecessary or irrelevant changes are outlined."
  - "FC - Fixes Clear: the proposed fixes are succinct and mention the unique changes to perform in the code."
  - Guideline: match each ground-truth bug to the model's explanations. An unmatched model bug makes ES false "unless the model explicitly noted the irrelevance". Clarity is judged independently of correctness (§3.2). — [SIGCSE25](https://arxiv.org/pdf/2407.04873)
- **ITiCSE'24 rubric (binary)**: "completeness Identifies and mentions all actual issues"; "perceptivity Identifies and mentions at least one actual issue"; "selectivity Does not identify non-existent issues" (§3.1). In the GPT-4 prompt, criteria are answered "(CRITERIA_NUMBER): Yes/No" in a fixed order, because "an answer to the completeness criteria influences selectivity" (Fig. 2, §3.2). — [ITiCSE24](https://arxiv.org/pdf/2405.05253)
- **BEA'25 rubric (Table 3, Appendix A)**, binary via the LLM jury:
  - Accuracy: "All issues in the student's code (or all required fixes) are correctly identified."
  - Selectiveness: "No non-existent or irrelevant issues are mentioned; no unnecessary changes are proposed."
  - Clarity.
  - Hint Correctness, Informativeness and Concealment ("avoids revealing the full solution and encourages reasoning"), taken from Phung et al. 2024.
  - The judge prompt asks for "reasoning" and then a "grading" dictionary of true/false (Fig. 6). — [BEA25](https://aclanthology.org/2025.bea-1.41.pdf)
- **BEA'25 definition of a high-quality repair**: "functional correctness and closeness to the student's original incorrect program … closeness ensures the repair preserves the student's original approach, making the solution more interpretable and educationally meaningful (Price et al., 2017)" (§3.1.2). — [BEA25](https://aclanthology.org/2025.bea-1.41.pdf)

### Inferences
- For an intent-preserving repair study, Pitts' SP ("maintained the original control flow") and LP ("only syntactic edits" vs "changed the logical or semantic structure") are the closest ready-made wording. LP is defined for *syntax* repair, so semantic-bug repair would need an adapted LP (e.g., "changes confined to the faulty region"). That adaptation is my suggestion, not something a source proposes.
- SIGCSE'25's FS ("no unnecessary or irrelevant changes") is a ready-made minimality criterion.

### Gaps
- No Likert or graded closeness scale exists in any of these papers.
- No paper defines a rubric item for "preserves the student's approach/intent" for semantic repairs.

## Q4. Pairwise vs absolute; blinding; order randomization

### Takeaway
All human protocols in scope are absolute binary judgments per output. None reports pairwise preference judgments, blinding of raters to system or model, or randomised presentation order.

### Cited Findings
- **ICER'23**: no human comparison of repairs. The metric "comparison" is automatic: Experiment 1 ranks the expert repair within a pool of all correct submissions and computes a Normalized Ranking Error. Experiment 2 is a binary "classification error": "the number of times the ART candidate repair was favored over the expert annotation" (§3.2.2–3.2.3). — [ICER23](https://acris.aalto.fi/ws/portalfiles/portal/122216612/Evaluating_Distance_Measures_for_Program_Repair.pdf)
- **ICER'23**: on comparing automated and expert repairs qualitatively, "we only conducted a surface-level manual analysis of the automated repairs … we did not conduct an in-depth qualitative analysis" (§5.3). — [ICER23](https://acris.aalto.fi/ws/portalfiles/portal/122216612/Evaluating_Distance_Measures_for_Program_Repair.pdf)
- **SIGCSE TS'25**: absolute binary labels per output. Blinding of annotators to the generating model is not reported. — [SIGCSE25](https://arxiv.org/pdf/2407.04873)
- **Pitts et al.**: absolute binary SP/LP per output. Blinding to model or prompt condition is not reported, nor is order randomisation. — [Pitts26](https://arxiv.org/pdf/2510.06187)
- **BEA'25**: absolute binary LLM-jury decisions. An appendix note says the reward design works "without relying on pairwise comparisons" (in reference to GRPO, not to human evaluation). — [BEA25](https://aclanthology.org/2025.bea-1.41.pdf)

### Inferences
- A blinded, order-randomised pairwise expert judgment ("which repair is closer to / better preserves the student's approach?") would go beyond anything in this line of work. ICER'23 approximates it only through a metric's binary preference between expert and Refactory repairs.

### Gaps
- Blinding and order randomisation are not reported in any of the papers.

## Q5. Agreement measure, values, disagreement resolution

### Takeaway
The procedure in this line is to calibrate on a subset, compute Cohen's κ, resolve disagreements, and then split or proceed. Pitts iterated until κ > 0.80, citing Landis and Koch. SIGCSE'25 stopped at a "moderate" κ = 0.54 and admitted it as a limitation. ICER'23 did no cross-validation of expert repairs.

### Cited Findings
- **Pitts et al. (verbatim)**: "experts coded an initial subset (10% of the repaired programs) jointly to align on definitions, then proceeded independently, calculating Cohen's Kappa (κ) after each round. When agreement fell below 0.80, in line with [Landis & Koch 1977], disagreements were resolved and the codebook was refined. Interrater agreement exceeding κ = 0.80 was achieved on the second round, after which the full set was coded and analysis conducted" (§2.2). The exact final κ value is not given. With four raters, the paper does not say whether κ is pairwise-averaged or Fleiss-style. — [Pitts26](https://arxiv.org/pdf/2510.06187)
- **SIGCSE TS'25**: the two annotators independently labelled the 88-output calibration subset, giving "a moderate inter-rater agreement of 0.54" (Cohen's κ). "After comparing annotations and resolving conflicts, the remaining feedback examples were split equally between the two annotators" (§3.2). Limitation: "we only used two raters, which resulted in a moderate inter-rater reliability score (0.54)" (§5). — [SIGCSE25](https://arxiv.org/pdf/2407.04873)
- **ICER'23**: "we did not cross-validate the annotations between educators. In effect, individual educator's views on the 'optimal' strategy for correcting the submission might be biased" (§5.3). On multiple valid repairs: "different annotators might have come up with different solutions … such alternatives were present only in relatively few cases" (§5.2.4). — [ICER23](https://acris.aalto.fi/ws/portalfiles/portal/122216612/Evaluating_Distance_Measures_for_Program_Repair.pdf)
- **ITiCSE'24 (human vs GPT-4, Table 2)**, completeness / perceptivity / selectivity:

  | Metric | Completeness | Perceptivity | Selectivity |
  |---|---|---|---|
  | Precision | 0.70 | 0.84 | 0.65 |
  | Recall | 0.95 | 1.00 | 0.94 |
  | F0.5 | 0.74 | 0.87 | 0.69 |
  | Accuracy | 0.75 | 0.85 | 0.71 |
  | Cohen's κ | 0.48 | 0.22 | 0.40 |

  The text calls this "moderate agreement" (completeness, selectivity) and "fair agreement" (perceptivity, given as 0.21 in the text vs 0.22 in Table 2, a minor internal inconsistency). GPT-4 rated more positively: "Complete" was labelled True 113 times vs 82 by the human, and selectivity 106 vs 78 (Table 1). The conclusion: "automated evaluation of feedback is not yet ready to rely exclusively on LLM evaluation – human judgement is still necessary" (§4). — [ITiCSE24](https://arxiv.org/pdf/2405.05253)

### Inferences
- A defensible small-study protocol in this community's terms combines both approaches. Jointly code about 10%, compute Cohen's κ per round, refine the codebook until κ ≥ 0.80 (Pitts), then either double-code everything (Pitts) or split the rest (SIGCSE'25). Report κ per criterion.
- If an LLM judge is used to scale up, this line expects it to be validated against human labels with κ and F0.5. Positive bias of the judge is the documented failure mode.

### Gaps
- Neither Pitts nor SIGCSE'25 reports κ per criterion. Pitts does not report the final κ value.

## Q6. Effort/time; ethics/IRB

### Takeaway
No paper reports annotation time or effort. Ethics coverage is generic: "national/institutional ethical guidelines" in ITiCSE'24, BEA'24 and BEA'25. No IRB approval number or protocol is reported, and the human-annotation papers say nothing about rater consent or compensation.

### Cited Findings
- **ITiCSE'24**: "We acquired the data from the authors of [6] for our study, following the national protocols for ethical research" (§3.1). — [ITiCSE24](https://arxiv.org/pdf/2405.05253)
- **BEA'24**: has an Ethics Statement saying the work followed "national and institutional ethics guidelines" (Ethics Statement). — [BEA24](https://aclanthology.org/2024.bea-1.15.pdf)
- **BEA'25**: "This work has been conducted in accordance with national and institutional ethical guidelines … The dataset used in this study is publicly available" (Ethics Statement). — [BEA25](https://aclanthology.org/2025.bea-1.41.pdf)
- **ICER'23**: uses a public dataset (Dublin, Azcona et al.) and releases annotations publicly (GitHub `edmpr`; the README points to the Hugging Face dataset `koutch/intro_prog`). It notes that "privacy concerns have often limited the possibility of sharing such data" (§5.3). — [ICER23](https://acris.aalto.fi/ws/portalfiles/portal/122216612/Evaluating_Distance_Measures_for_Program_Repair.pdf); [edmpr repo](https://github.com/KoutchemeCharles/edmpr)
- **SIGCSE TS'25**: releases "the models' outputs and the annotators' responses" (GitHub `feed_genju`). — [SIGCSE25](https://arxiv.org/pdf/2407.04873)
- **Pitts et al.**: public CodeWorkout dataset of "57,670 anonymized Java submissions from 368 students". NSF Grant #2418658 is acknowledged. No ethics or IRB statement (2-page poster). — [Pitts26](https://arxiv.org/pdf/2510.06187)

### Inferences
- In this line, expert evaluation of model outputs on public, anonymised student data is treated as not needing an IRB statement beyond "national guidelines". A paper on a public benchmark such as CodeNet could follow the same norm. This is my inference, not a stated rule.

### Gaps
- Annotation hours or person-effort are not reported anywhere.
- ICER'23 has no explicit ethics statement in the text I read.

## Q7. Main findings: which distance metrics track expert/human notions of closeness

### Takeaway
ICER'23 is the empirical basis for the whole line's use of ROUGE. Among 10 measures, ROUGE-1 and ROUGE-LCS best retrieved expert-written minimal repairs and best preferred them over Refactory repairs. Tree edit distance was the worst and least consistent at retrieval. Later papers paraphrase this as ROUGE-L "correlat[ing] well with human judgement", which overstates the design: there was no correlation with human ratings.

### Cited Findings
- **ICER'23, Experiment 1** (mean Average Normalized Ranking Error, lower is better, Table 2):

  | Measure | Mean ANRE |
  |---|---|
  | TED | 0.166 |
  | SEQ | 0.018 |
  | STR | 0.018 |
  | NTED | 0.223 |
  | NSEQ | 0.017 |
  | NSTR | 0.016 |
  | BLEU | 0.011 |
  | CodeBLEU | 0.017 |
  | ROUGE | 0.008 |
  | ROUGE-LCS | 0.007 |

  "The ROUGE-based measures perform consistently better than all others across all assignments". Tree edit distance "has consistently higher errors than all other metrics". Normalization "does not bring significant benefits … and can even be detrimental" (§4.2.1). — [ICER23](https://acris.aalto.fi/ws/portalfiles/portal/122216612/Evaluating_Distance_Measures_for_Program_Repair.pdf)
- **ICER'23, Experiment 2**: the number of times a metric judged the Refactory repair closer to the buggy code than the expert repair, out of 755 programs (Table 3).

  | Measure | Errors / 755 |
  |---|---|
  | TED | 94 |
  | SEQ | 119 |
  | STR | 119 |
  | NTED | 102 |
  | NSEQ | 117 |
  | NSTR | 108 |
  | BLEU | 111 |
  | CodeBLEU | 93 |
  | ROUGE | 91 |
  | ROUGE-LCS | 90 |

  TED does well here but "fluctuates heavily between assignments", and ROUGE stays "the most consistent" (§4.2.2). The authors acknowledge an "inherent bias in this experiment towards the Automated Repair Tool" (the tool was given the solution pool) (§4.2.2). — [ICER23](https://acris.aalto.fi/ws/portalfiles/portal/122216612/Evaluating_Distance_Measures_for_Program_Repair.pdf)
- **ICER'23, why ROUGE works**: "edit distances measure the number of operations needed to transform the buggy program into the candidate repair, while the ROUGE-based measure … measures the proportion of the words/elements in the buggy program that can be found in the candidate (independently of whether the position of these elements has changed) … what matters the most is that the measure captures the extent to which a correct solution retains elements from the original program". Buggy code is used as the reference and the repair as the candidate. An ablation shows BLEU matches ROUGE when the operands are swapped (§3.2.6, §5.1.3). — [ICER23](https://acris.aalto.fi/ws/portalfiles/portal/122216612/Evaluating_Distance_Measures_for_Program_Repair.pdf)
- **ICER'23, ECDF**: "around 82% (respectively 86 %) of the repairs found by the Refactory tool (respectively our educators) have on average 80% of the words/token in the original students' buggy programs". The ECDF is proposed as a "success rate against a threshold" view of how much student code a repair technique retains (§4.2.3, §5.2.2). — [ICER23](https://acris.aalto.fi/ws/portalfiles/portal/122216612/Evaluating_Distance_Measures_for_Program_Repair.pdf)
- **ICER'23, students' own corrections as reference**: the relative ranking of metrics holds, but "absolute errors were all higher (meaning that the expert annotations are closer to the students' buggy code than the students' corrections)", because students "completely change their approach … if they are not able to make their original strategy work" (§5.2.4). — [ICER23](https://acris.aalto.fi/ws/portalfiles/portal/122216612/Evaluating_Distance_Measures_for_Program_Repair.pdf)
- **ICER'23 caveat**: "Our results are only valid for evaluation … These results might not hold for other aspects of the feedback pipeline, including constructing repairs" (§5.2.1). — [ICER23](https://acris.aalto.fi/ws/portalfiles/portal/122216612/Evaluating_Distance_Measures_for_Program_Repair.pdf)
- **How later papers cite ICER'23**:
  - BEA'24: "the ROUGE-L score has been shown to correlate well with human judgement of high-quality repairs (Koutcheme et al., 2023b)" (§3.3). — [BEA24](https://aclanthology.org/2024.bea-1.15.pdf)
  - Bench: "Rouge score serves as a better repair quality indicator compared to sequence edit distance". Its rouge@k is described with "Rouge1" in the main text but a footnote says "we use the Rouge-L score", an internal inconsistency (§3.1). — [Bench](https://arxiv.org/pdf/2405.05347)
  - BEA'25: ROUGE "has been shown to be an effective and efficient measure for selecting high-quality repairs (Koutcheme et al., 2023a)". It is used as a reward only when the repair passes all tests (§3.1.2, §3.2.2). — [BEA25](https://aclanthology.org/2025.bea-1.41.pdf)
- **BEA'24 finding**: "as language models become more and more proficient in generating repairs, these repairs become closer to students' original programs". This is a pass-rate vs ROUGE-L scaling across models (§4.1, Fig. 2). — [BEA24](https://aclanthology.org/2024.bea-1.15.pdf)
- **Benchmarking limitation**: "assessing qualitative performance based solely on code closeness may introduce biases and may not always align with instructors' pedagogical objectives" (§6). — [Bench](https://arxiv.org/pdf/2405.05347)
- **AIED'23**: closeness is reported as average sequence edit distance (SD) per assignment against Refactory. On QuixBugs, InCoder repaired 13 of 28 programs vs 23 for Codex. On student assignments InCoder is "competitive with the Refactory repair tool (RF), both in terms of the number of repairs found and in terms of distance". Examples, as success rate / SD (Refactory vs InCoder):
  - DB fibonacci_iter: 1.00 / 56.03 vs 0.94 / 33.81.
  - NC mean: 0.77 / 33.29 vs 0.99 / 20.61.

  Source: §4, Tables 1–2. — [AIED23](https://aaltodoc.aalto.fi/items/b3f949b0-efa5-4a61-8cf9-6fce7fc17a8d)
- **Pitts et al.** (human SP/LP alongside edit distance):
  - SP by model: GPT-5 190/197 (96.4%), Gemini 2.5 Flash 186/190 (97.9%), Claude 3.5 Haiku 170/192 (88.5%); χ²(2, N=579)=18.10, p<0.001.
  - LP by model: GPT-5 166/192 (86.5%), Gemini 156/186 (83.9%), Claude 116/171 (67.8%); χ²(2, N=549)=22.36, p<0.001.
  - Average edit distance: GPT-5 11.4, Gemini 13.8, Claude 24.4; F(2,594)=16.22, p<0.001.
  - Compilation: 98.5% / 95.5% / 96%, not significant.
  - Prompt context had no significant effect on any measure.
  - The model ranking by edit distance matches the ranking by LP, but no correlation between the human labels and edit distance is reported.
  - Edit distance is called "normalized Levenshtein", yet the averages (11.4–24.4) look like raw counts. This is unexplained.

  Source: §2.2, §3. — [Pitts26](https://arxiv.org/pdf/2510.06187)

### Inferences
- When citing ROUGE as "validated", the accurate wording is: ROUGE best *retrieves expert-written minimal repairs* (ICER'23). It was not correlated with human closeness ratings. A human closeness judgment (e.g., pairwise "which repair keeps more of the student's approach") would test what BEA'24 claims but ICER'23 did not measure.
- ICER'23's TED result is relevant to histra's TED-based metrics. Plain APTED-style TED was the worst at retrieval (mean ANRE 0.166), though better in the expert-vs-Refactory binary test. Pairing TED with ROUGE-1 or ROUGE-LCS (buggy code as reference) would align with this line's evidence. Note the distinction: histra uses value-aware APTED, while ICER'23 used the `python_edit_dist` package on a Python AST.
- ICER'23 found that students' own later corrections are farther from their buggy code than expert minimal repairs. This supports excluding the student's own AC as a reference, which histra already does. It also suggests an expert-written minimal repair could serve as a "closeness gold" baseline for a small subset.

### Gaps
- I found no paper in this line reporting a correlation (Spearman, Kendall, etc.) between any distance metric and human ratings of closeness.
- ICER'23 Experiment 2 per-assignment variance and statistical tests are not reported beyond the counts.
- AIED'23 full-paper results beyond Table 2 excerpts (e.g., overall averages) were not checked in detail.
