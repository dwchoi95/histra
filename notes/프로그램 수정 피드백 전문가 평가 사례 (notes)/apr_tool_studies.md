# Human evaluation in repair and hint tools for student programs (per-paper extraction)

Method note: full texts were read for Yi FSE'17 (author copy in the ITSP GitHub repo), CLARA (arXiv v4), Sarfgen (arXiv v1, "under review at PLDI 2018"), Refactory (UCL accepted version), Verifix (arXiv v1), Brafar (PolyU author copy), PyDex (OOPSLA'24 camera-ready from Microsoft Research; MMAPR arXiv v1 also checked), PaR (arXiv v1, 2024), LSGen (arXiv 2601.08545), AdaPatcher (arXiv 2503.06510), FastFixer (arXiv 2410.21285), and CREF (arXiv 2406.13972 v2). Each was keyword-searched (user study, participant, human, expert, survey, Likert, IRB/ethics, TA, manual inspection) and the matching sections were read. The ITAP (IJAIED) and Hint Factory (ITS 2008) full texts could not be retrieved because Springer blocked access. Only their abstracts are used.

## Q1. Was there any human evaluation, and how was it designed (raters/participants, items, measures, design, agreement, ethics, findings)?

### Takeaway
Only 2 of the 12 repair-tool papers ran a study with real users: Yi et al. FSE'17, a between-subjects student study plus a crossover TA grading study, and CLARA, a self-selected online study with one 1–5 usefulness item. Two LLM-era papers (AdaPatcher, LSGen) ran small "human studies" with 2 evaluators. Those studies validated an intermediate artifact (bug locations, bug descriptions), not repair usefulness, and reported no agreement statistic. No paper reported IRB or ethics approval, blinding, or inter-rater agreement (kappa).

### Cited findings

**Yi et al., ESEC/FSE 2017 (GenProg/AE/Angelix/Prophet applied to IIT Kanpur intro-C submissions). §7.3 "User Study"**
- Scope: the feasibility study covers 661 student programs. Out-of-the-box APR repairs about 30%. A partial-repair, hint-style policy gave an "84% improvement of repair rate". The user study had "more than 250 novice students and 35 graders" — [Yi et al. FSE'17, abstract](https://raw.githubusercontent.com/jyi/ITSP/master/ITSP-FSE17.pdf)
- Two research questions: whether generated feedback helps students solve problems on their own, and whether it helps TAs grade "efficiently (faster grading) and effectively (only small variation in the marks for similar submissions)" — [Yi et al. §7.3](https://raw.githubusercontent.com/jyi/ITSP/master/ITSP-FSE17.pdf)
- Student study design, between-subjects:
  - 5 problems were selected, each with buggy submissions plus generated partial repairs.
  - Students were split into an experimental group (repairs shown) and a control group (repairs not shown). Repairs were "presented in the form of a comment around the repaired lines of the buggy submission".
  - Each student fixed one randomly chosen buggy submission.
  - The study was "unannounced": it was given as a low-weight bonus question alongside regular assignments, and participation was voluntary.
  - 263 students submitted: 140 without repairs, 123 with repairs.
  - Source: [Yi et al. §7.3](https://raw.githubusercontent.com/jyi/ITSP/master/ITSP-FSE17.pdf)
- Student measures: time taken (Figure 4, in seconds per problem) and correctness.
  - Students solved problems more slowly when repairs were shown ("problem solving time of the students tends to increase in the group where repairs are shown").
  - Correctness was about the same in both groups: 94% without repairs vs 95% with repairs.
  - Source: [Yi et al. §7.3](https://raw.githubusercontent.com/jyi/ITSP/master/ITSP-FSE17.pdf)
- TA study design, crossover/counterbalanced:
  - 35 TAs took part. Their background (programming experience; C skill rated 1 = Novice to 5 = Expert) came from a pre-study survey.
  - The items were 43 buggy submissions randomly drawn from cases where the tool produced a complete or partial repair, covering 8 problems.
  - Group 1 graded set A (22 tasks) without repairs and set B (21 tasks) with repairs. Group 2 had the reverse.
  - Reference marks came from an instructor who did not take part and did not see the repairs.
  - Measures: grading time and marks (0–20). A post-study survey asked whether the repairs were useful, "how do you categorize the errors of the program based on the suggested repair?", and "what kind of modifications are necessary in the suggested repair to obtain a correct solution?"
  - Source: [Yi et al. §7.3, Fig. 3, Fig. 6](https://raw.githubusercontent.com/jyi/ITSP/master/ITSP-FSE17.pdf)
- TA results (Table 5):
  - Mean grading time was 173.76 s without repairs vs 135.41 s with them. Median: 150.95 vs 133.68. SD: 96.70 vs 40.88.
  - Half of the TAs said repairs were useful ("Yes" group: 155.08 vs 124.83 s). The other half said they were not ("No" group: 191.40 vs 145.39 s).
  - The difference in marks between groups was ≤1 for 22/43 submissions and ≤2 for 30/43.
  - Conclusion: "novice students do not seem to know how to effectively make use of suggested repairs, unlike TAs. Post-processing of repairs would be necessary for novice students."
  - Source: [Yi et al. §7.3, Table 5, Fig. 7](https://raw.githubusercontent.com/jyi/ITSP/master/ITSP-FSE17.pdf)
- Not reported in §7.3: significance tests, effect sizes, IRB/consent statement, blinding, inter-rater agreement. A keyword search of the full text found none of these. — [Yi et al.](https://raw.githubusercontent.com/jyi/ITSP/master/ITSP-FSE17.pdf)
- Participant-count discrepancy: the artifact README says 38 TAs volunteered, 37 were assigned tasks, and 35 responded to each survey. The paper says 35. The README also says "250+" students. — [jyi/ITSP README](https://github.com/jyi/ITSP)
- Study materials (submission lists, pre- and post-survey question PDFs, survey response CSVs) are released in `user_study/`. — [jyi/ITSP README](https://github.com/jyi/ITSP)

**CLARA (Gulwani, Radiček, Zuleger, PLDI 2018). §6.3 "User Study on Usefulness"**
- Recruitment: participants were recruited by advertising "on programming forums, mailing lists, and social networks". Each solved 6 introductory C problems with CLARA feedback, plus one warm-up problem. — [CLARA arXiv §6.3](https://arxiv.org/abs/1603.03165)
- Measure: one absolute Likert item after each problem, "How useful was the feedback provided on this problem?", from 1 ("Not useful at all") to 5 ("Very useful"). Optional free-text comments were allowed per feedback and per problem. Self-rated experience used "Your overall programming experience (your own, subjective, assessment)", from 1 ("Beginner") to 5 ("Expert"). — [CLARA §6.3](https://arxiv.org/abs/1603.03165)
- Participants and results:
  - 52 participants gave 191 grades. The mean was 3.4 out of 5.
  - Self-rated experience: 22 rated 5, 19 rated 4, 9 rated 3, 0 rated 2, and 2 rated 1. In other words, the sample was mostly experienced programmers.
  - Authors' caveat: "a study with beginner programmers is an important future work."
  - Per-problem grade distributions (1/2/3/4/5) are in Table 2.
  - Source: [CLARA §6.3, Table 2](https://arxiv.org/abs/1603.03165)
- Feedback coverage in the study:
  - Feedback was generated for 1,503 incorrect attempts (88.52%), with an average generation time of 8 s.
  - Repairs with cost > 100 were replaced by a generic strategy message, which happened in 403 cases.
  - Grades were collected only when feedback was generated.
  - Source: [CLARA §6.3](https://arxiv.org/abs/1603.03165)
- Not reported: control group, blinding, ethics/IRB, statistical tests. — [CLARA](https://arxiv.org/abs/1603.03165)
- Separate from the user study, the authors manually inspected repair quality. They framed this judgment as one that "mirrors a human teacher helping a student: the teacher has to guess the student's idea".
  - They inspected 100 randomly selected repairs on MOOC data.
  - Results: 72 were "the smallest, most natural repair"; 9 were almost smallest but had one extra change; 11 were correct but "different from the student's idea"; for 8, the student's idea could not be determined. The authors counted 81% as "good quality".
  - Who inspected and how disagreements were resolved is not reported. The text uses "we".
  - Source: [CLARA §6.2 (3)](https://arxiv.org/abs/1603.03165)
- The authors also manually compared CLARA with AutoGrader on 100 random cases where both produced a repair:
  - 61 were the same; 19 were different but of equal quality; AutoGrader was better in 9; CLARA was better in 5; AutoGrader's repair was incorrect in 6.
  - In 100 cases where only AutoGrader failed, CLARA produced a good-quality repair in 74.
  - Source: [CLARA §6.2.1](https://arxiv.org/abs/1603.03165)

**AdaPatcher (Dai et al., AAAI 2025). RQ4 "Human Study for Bug Localization"**
- Items and raters: "900 samples are provided to 2 experienced evaluators". Each evaluator independently determined bug locations, and "the first author is then involved in leading a discussion when they have disagreements". — [AdaPatcher arXiv RQ4](https://arxiv.org/abs/2503.06510)
- Measure: the model's predicted locations were compared with the human-identified locations in four categories: Accurate (AL), Partial (PL), Erroneous (EL), and No Localization (NL).
  - CodeLlama trained with the framework, compared with GPT-4o, had +35.0% AL and +3.0% PL, and −15.7% EL and −22.3% NL.
  - Source: [AdaPatcher RQ4, Fig. 4](https://arxiv.org/abs/2503.06510)
- Not reported: evaluator background beyond "experienced", sampling procedure, agreement statistics, time spent, ethics. The study evaluates bug localization, not the quality or usefulness of the repair. — [AdaPatcher](https://arxiv.org/abs/2503.06510)

**LSGen (Dai et al., AAAI 2026). RQ3 "Human Study for Bug Descriptions"**
- Items: 189 randomly selected GPT-4o samples. Each generated bug description was paired with the ground truth, giving 1,390 pairs. — [LSGen arXiv RQ3](https://arxiv.org/abs/2601.08545)
- Raters and procedure: "two experienced evaluators, who independently judge whether each generated description matches the ground truth". The first author led discussion to resolve disagreements. — [LSGen RQ3](https://arxiv.org/abs/2601.08545)
- Purpose and results: the study validated the paper's LLM-based automatic metric.
  - The metric agreed with the human judgment in 67.72% of samples and 93.02% of points.
  - Inconsistency: 21.16% (sample) and 5.11% (point). Indeterminate: 11.12% and 1.87%.
  - Pearson r = 0.848.
  - Source: [LSGen RQ3, Table 4](https://arxiv.org/abs/2601.08545)
- Ground-truth bug descriptions for the benchmark were drafted by an LLM and then "reviewed and refined by three programmers with five years of" experience. The three calibrated on 50 samples before agreeing on a unified annotation standard. — [LSGen Appendix](https://arxiv.org/abs/2601.08545)
- Not reported: inter-rater kappa, rater identities, ethics. No human rating of repaired code. — [LSGen](https://arxiv.org/abs/2601.08545)

**CREF (Yang et al., ISSTA 2024). §5.2 "Industrial Application" (a deployment, not a user study)**
- Setup: deployed on a company's C++ education platform. Tutors give brief guidance, CREF completes the repair, and tutors review the output before replying to the student. — [CREF arXiv §5.2](https://arxiv.org/abs/2406.13972)
- Outcome: "The two-month deployment" cut average response time per debugging request "from 26.7 minutes to 7.7 minutes" and labor costs by 71.2%, which they equate to "3.5 times more debugging requirements".
- Not reported: student or tutor ratings, surveys, number of tutors or students, controls.
- Source: [CREF §5.2](https://arxiv.org/abs/2406.13972)
- The TutorCode benchmark includes guidance written by human tutors. The benchmark has 1,239 defective C++ programs from 427 students. This is input data, not an evaluation. — [CREF §1, §3](https://arxiv.org/abs/2406.13972)

**FastFixer (Liu et al., ASE 2024). Author manual inspection only (§5.2, strategy comparison)**
- "We conducted a manual inspection of 50 randomly-sampled repairs" that were fixed by both strategies M3 and M4. M3 produced 6 (12%) "excessively aggressive modification[s]", and M4 produced 2 (4%).
- Inspectors, criteria, and agreement are not reported.
- Source: [FastFixer arXiv](https://arxiv.org/abs/2410.21285)

**Sarfgen (Wang, Singh, Su, PLDI 2018)**
- No user study, survey, or expert rating in arXiv v1.
- The only human-related claim is about deployment: Sarfgen "has also been integrated with the Microsoft-DEV204.1X edX course and the early feedback obtained from online students demonstrates its practicality and usefulness". No method, counts, or numbers are given.
- Source: [Sarfgen arXiv abstract, §1, Conclusion](https://arxiv.org/abs/1711.07148)

**Refactory (Hu et al., ASE 2019)**
- No human evaluation.
- Conclusion: "In future work, we plan to conduct detailed user studies where the feedback from our tool can be generated live during tutorial or recitation sessions, so as to gauge the possible improvement in meeting learning outcomes."
- Source: [Refactory, Conclusion](https://discovery.ucl.ac.uk/10091878/1/ase19.pdf)

**Verifix (Ahmed et al., TOSEM 2022)**
- No human evaluation. "The human acceptability of our verified feedback can be further investigated via future user-studies."
- The paper cites ITSP (Yi et al.) as showing "negative results on providing semantic repair feedback for student programs".
- Source: [Verifix arXiv §9 Related Work](https://arxiv.org/abs/2106.16199)

**Papers with no human evaluation**
- **Brafar (Xie et al., ISSTA 2024):** RQ1–RQ3 are all automatic (repair rate, time, RPS). A keyword search found no user study, survey, or rater study. — [Brafar author copy](https://ira.lib.polyu.edu.hk/bitstream/10397/114193/1/Xie_BRAFAR_Bidirectional_Refactoring.pdf)
- **PyDex/MMAPR (Zhang et al., OOPSLA 2024):** No user study. §6 argues pedagogical benefit in prose instead ("Automatically fixing students' submissions is not the same as providing an explanation for their mistakes…"). — [PyDex OOPSLA CR](https://www.microsoft.com/en-us/research/uploads/prodnew/2024/03/PyDex-OOPSLA-2024-CR.pdf)
- **PaR (Zhao et al., arXiv v1 2024):** No human evaluation. Its threats-to-validity section relies on test pass rates as the correctness proxy. — [PaR arXiv](https://arxiv.org/abs/2404.01754)

### Inferences
- Across these 12 repair-tool papers (2017–2026), a controlled user study is rare (only Yi et al.) and an expert rating of repair quality is essentially absent. CLARA's "is it the student's idea?" judgment is the closest precedent, but it was done by the authors on 100 samples, with no stated protocol or agreement.
- The LLM-era "human study" template (AdaPatcher, LSGen) is: 2 "experienced evaluators", independent judgments, first-author adjudication, no kappa, and the target is an intermediate artifact. This bar is low. A study with stated rater expertise, blinding, pairwise comparison, and Cohen's/Fleiss' kappa would be above typical practice in this sub-field.
- CLARA's manual categories (smallest/natural, extra change, "different from the student's idea", idea undeterminable) are directly reusable as a rubric for intent-preservation judgments.
- Yi et al.'s negative result for novices (slower when shown repairs, no gain in correctness) is the standard citation for "raw repairs ≠ useful feedback". Verifix cites it this way.

### Gaps
- Sarfgen: only arXiv v1 (pre-PLDI) was read. Whether the PLDI'18 camera-ready adds deployment numbers was not verified, because the ACM DL returned 403.
- PaR: the EMSE 2026 journal version was not accessible. Findings are from arXiv v1 (April 2024), and the journal version may add evaluations.
- LSGen and AdaPatcher: arXiv versions were read. Whether the AAAI proceedings versions differ was not checked.
- Yi et al.: the per-problem student solving times (Fig. 4) are only shown in the figure; no numbers were extracted. No statistical test is reported for any comparison.
- No paper reported time spent per rating, rater compensation, or IRB/ethics approval. The keyword search found no such statements, so these are "not reported".

## Q2. Where there was no human evaluation, what proxy metrics were used?

### Takeaway
The near-universal proxies are test-based repair rate plus a patch-size measure: Relative Patch Size, which is AST tree-edit distance divided by AST size (introduced by CLARA), or token/line edit distance. Time is often added. LLM papers add partial-repair or improvement rates and "consistency" (the share of lines preserved).

### Cited findings
- **CLARA:**
  - Repair rate on 4,293 incorrect attempts from an MITx Python MOOC (with 12,973 correct attempts) was 97.44%, vs 19.29% for AutoGrader.
  - It introduced "relative repair size", the tree-edit distance of the repair divided by the AST size. 68% of repairs were < 0.3, 53% < 0.2, and 25% < 0.1.
  - Source: [CLARA §6.2](https://arxiv.org/abs/1603.03165)
- **Sarfgen:**
  - Two metrics: "performance (i.e. how long does Sarfgen take to generate feedback), and (2) capability (i.e. how many incorrect" programs get minimal fixes).
  - It produced minimal fixes for 4,311 of 4,806 incorrect programs (about 90%) on edX plus CodeHunt (17 problems), and "all the minimal fixes modify up to three lines only".
  - CLARA comparison on 883 programs.
  - Source: [Sarfgen §4.2–4.6](https://arxiv.org/abs/1711.07148)
- **Refactory:**
  - Repair rate of 90.8% on 1,783 buggy Python programs.
  - RPS = TED(AST_b, AST_r)/Size(AST_b), with smaller patches argued to be "more likely to help students".
  - Repair rate as the share of correct solutions is varied (sampling-rate experiment).
  - Source: [Refactory §RQ1–RQ2](https://discovery.ucl.ac.uk/10091878/1/ase19.pdf)
- **Verifix:**
  - Verified repair for 58.4% of incorrect submissions across 28 assignments.
  - RPS vs Clara on 104 commonly repaired cases: Verifix was smaller in 56, Clara in 33, and they were equal in 15. KDE plot of RPS.
  - Source: [Verifix §8–9](https://arxiv.org/abs/2106.16199)
- **Brafar:** Table 3 reports "repair rate (RR), average repair time (Time), and relative patch size (RPS)" on the 1,783-program Refactory benchmark (5 assignments), using the formula RPS = Dist(AST_r, AST_b)/Size(AST_b). — [Brafar §4.2](https://ira.lib.polyu.edu.hk/bitstream/10397/114193/1/Xie_BRAFAR_Bidirectional_Refactoring.pdf)
- **PyDex:**
  - Dataset: 286 student programs, 15 tasks, from an Indian university's Python course.
  - Repair rate was 86.71% without few-shots and 96.5% with few-shots. Baselines: BIFI+Refactory 67.13%, PyDex+Refactory 83.57%, PyDex+GenProg 49.30%.
  - Average token edit distance was 28.59 (no few-shot) and 29.68 (few-shot).
  - Significance tests: PyDex is "statistically significant higher repair rate than 2 of our 3 baselines".
  - Source: [PyDex §1, §5](https://www.microsoft.com/en-us/research/uploads/prodnew/2024/03/PyDex-OOPSLA-2024-CR.pdf)
- **PaR:**
  - Pass rate is decided by majority vote (≥3 of 5 independent runs must pass all tests).
  - A "Partial Repair Rate" counts runs where all previously passing tests still pass and at least one failing test now passes.
  - Construct validity: "Utilizing the tests as a proxy for correctness is common in the educational domain".
  - Source: [PaR §Metrics, Threats](https://arxiv.org/abs/2404.01754)
- **AdaPatcher:** Uses CodeNet-derived triplets (52,168 samples) and four metrics:
  - Code Accuracy Rate (Acc).
  - Code Improvement Rate (additional tests passed).
  - Failed Repair Rate (FR: the share of fixes that break previously passing tests).
  - Code Consistency Rate (the share of lines preserved).
  - Source: [AdaPatcher §Evaluation Metrics](https://arxiv.org/abs/2503.06510)
- **LSGen:** Acc and Improve for code. Edit distance is reported in result tables. Bug descriptions are scored with point-level Precision/Recall/F1 from an LLM-based automatic metric, which was validated by the human study in Q1. — [LSGen §Evaluation Metrics](https://arxiv.org/abs/2601.08545)
- **FastFixer:** "Number of Fixed Programs" and "Fix Rate" (passes all tests), average Line-level Edit Distance (LED), and inference-efficiency metrics. — [FastFixer §4.3](https://arxiv.org/abs/2410.21285)
- **CREF:** Correctness via TOP-5 and AVG-5. Patch precision via a new Relative Patch Size Ratio (RPSR), which normalizes RPS against the ground-truth corrected code. — [CREF §4 Evaluation Metrics](https://arxiv.org/abs/2406.13972)

### Inferences
- RR + RPS/TED is the de facto evaluation contract that reviewers expect for this line of work (CLARA → Refactory → Verifix → Brafar → CREF's RPSR). Measuring how far a patch stays from the student's own code is the field's accepted proxy for "student-friendliness" in place of human judgment.
- AdaPatcher's "Code Consistency Rate" (share of preserved lines) is the closest automatic metric to "intent preservation" among the LLM papers.

### Gaps
- Refactory and Brafar claim "less overfitting". The exact overfitting measure was not located in the extracted text and is not reported here.

## Q3. How were the generated hints evaluated in Hint Factory (Barnes & Stamper 2008) and ITAP (Rivers & Koedinger 2017)?

### Takeaway
Both original papers used offline, data-driven technical evaluations (hint availability/coverage on historical student data), not human ratings. Classroom or experimental evaluations of the Hint Factory came in later, separate papers. The full texts of the two papers could not be retrieved, so the details are limited to abstracts.

### Cited findings
- **ITAP (IJAIED 27(1), 2017; online 2015):**
  - The abstract says the authors "perform a technical evaluation on a small set of data to determine the effectiveness of the component algorithms and ITAP's potential for self-improvement". Results: "ITAP is capable of producing hints for almost any given state after being given only a single reference solution, and … it can improve its performance by collecting data over time".
  - The abstract mentions no user study or expert rating.
  - Source: [Semantic Scholar record of Rivers & Koedinger](https://api.semanticscholar.org/graph/v1/paper/DOI:10.1007/s40593-015-0070-z?fields=title,abstract) (DOI [10.1007/s40593-015-0070-z](https://doi.org/10.1007/s40593-015-0070-z))
  - Secondary description: ITAP hints were evaluated "based on whether they eventually reached a correct solution and the length of the hint sequence". This is a survey's summary and was not verified against the full text. — [Hint-generation survey, arXiv 2404.04728](https://arxiv.org/pdf/2404.04728)
- **Hint Factory (ITS 2008, LNCS pp. 373–382):**
  - Markov decision processes (MDPs) were extracted from four semesters of student solutions in a logic-proof tutor, and the authors estimated how often hints could be given at any point in a problem.
  - The 2010 journal version says "extracted MDPs and our proposed hint-generating functions will be able to provide hints over 80% of the time".
  - This is a hint-availability measure, not a learning or quality measure.
  - Source: [JETS 2010 record, learntechlib](https://learntechlib.org/p/75238); [Springer chapter](https://doi.org/10.1007/978-3-540-69132-7_41)
- **Later Hint Factory evaluations** were published separately:
  - "A pilot study on logic proof tutoring using hints generated from historical student data" (EDM 2008).
  - "Experimental Evaluation of Automatic Hint Generation for a Logic Tutor" (AIED 2011; IJAIED 22(1–2), 2013).
  - "Enhancing the Automatic Generation of Hints with Expert Seeding".
  - Source: [dblp Barnes](https://dblp.org/pid/69/6233); [Croy publications](https://pages.charlotte.edu/marvin-croy/publications)

### Inferences
- In the data-driven hint lineage, the founding papers evaluated coverage offline. Controlled classroom experiments came later as separate publications. This matches the APR-for-education pattern in Q1, where human studies are deferred to "future work".

### Gaps
- The ITAP and Hint Factory 2008 full texts were not retrievable (Springer and the CMU KiltHub returned 403 or a redirect to login). Dataset sizes, exact coverage numbers, and section-level details are therefore not reported.
- One secondary source claims Rivers' thesis reports hints for "100% of student submissions". This could not be verified, so it is excluded from the findings.
- The design and results of the 2011/2013 Hint Factory experiment (groups, N, outcomes) were not retrieved.
