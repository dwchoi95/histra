"""Paper §4 numbers and LaTeX tables from results/eval/ (run run_eval.sh, measure.py, phase_share.py first).
Repair rates use the raw outputs (denominator = every trajectory); skeleton loss = mean of 1 - retention over the
passing patches (*.ret.jsonl from measure.py), as in Table I.
Usage: python summarize.py [results/eval]"""
import ast, csv, json, math, os, sys
from collections import defaultdict

D = sys.argv[1] if len(sys.argv) > 1 else "results/eval"
# Baselines, one per group of Section II-A: alignment (run_refactory.py), localization (run_brafar.py), knowledge
# (run_lsgen.py with GPT-4o, its best configuration; lsgen_qwen stays in the artifact only);
# MENTORED: add ("mentored", "MENTORED") once run_mentored.py has finished
BASE = [("refactory", "Refactory"), ("brafar", "Brafar"), ("lsgen_gpt4o", "LSGen")]
MAIN = BASE + [("histra_min", "\\tool{}")]
PRELIM = [("refactory", "Refactory"), ("lsgen_gpt4o", "LSGen")]      # Fig. limit: prior repairers (Section II-B)
ABL = [("histra_min", "\\tool{}"), ("histra_nostd", "\\tool{}$-$Norm"), ("histra_nohole", "\\tool{}$-$Hole"),
       ("histra_nokept", "\\tool{}$-$Kept"), ("histra_plain", "\\tool{}$-$Min"), ("histra_sizemin", "\\tool{}$_{\\mathit{size}}$"),
       ("histra_randhole0", "\\tool{}$_{\\mathit{rand}}$"), ("histra_randfrac", "\\tool{}$_{\\mathit{frac}}$"),
       ("histra_fltop_srv", "\\tool{}$_{\\mathit{FL}}$"),     # fault-localization holes (run on SuperServer, where histra_min
       ("histra_nohist", "\\tool{}$_{\\emptyset}$")]            # and histra_nohist reproduced every patch of the Mac runs)
RAND = ["histra_randhole0", "histra_randhole1", "histra_randhole2"]   # matched random holes, three draws (averaged)
CLOSE = BASE + [("histra_nohist", "\\tool{}$_{\\emptyset}$"), ("histra_min", "\\tool{}")]   # RQ2 table, from edit_metrics.py
GEN = [("llm_gemma", "LLM$_G$"), ("llm_gemma_min", "LLM$_G$+Min"), ("llm_gemma_keep", "LLM$_G$+Keep"),
       ("llm_gemma_randlines", "LLM$_G$+Rand"), ("llm_gemma_histra", "LLM$_G$+\\tool{}")]


def load(name, suffix=""):
    p = f"{D}/{name}{suffix}.jsonl"
    return {(r["pid"], r["user"]): r for r in map(json.loads, open(p)) if r} if os.path.exists(p) else None


def same(a, b):
    try:
        return ast.dump(ast.parse(a)) == ast.dump(ast.parse(b))
    except (SyntaxError, ValueError):
        return False


def phases():
    """Phase of each HISTRA patch: recorded by histra_eval.py since the final-review re-run, else phase_share.py's file."""
    raw = load("histra_min")
    if raw and any("phase" in r for r in raw.values()):
        return {k: r for k, r in raw.items() if r.get("phase")}
    return load("phases")


def stats(name, keys=None):
    """(n, fixed, loss %, % of passing patches identical to the own AC, % keeping the whole skeleton)."""
    raw, ret = load(name), load(name, ".ret")
    if raw is None or ret is None:
        return None
    ks = [k for k in raw if keys is None or k in keys]
    fixed = [k for k in ks if raw[k]["patch"] is not None]
    rets = [ret[k]["ret_patch"] for k in fixed if k in ret and ret[k]["ret_patch"] is not None]
    exact = sum(same(raw[k]["patch"], raw[k]["oracle"]) for k in fixed)
    intact = 100 * sum(r == 1.0 for r in rets) / max(len(rets), 1)
    return len(ks), len(fixed), 100 * (1 - sum(rets) / len(rets)) if rets else None, 100 * exact / max(len(fixed), 1), intact


def losses(name, keys=None):
    """Skeleton loss (fraction) of each passing patch whose trajectory has a non-empty skeleton."""
    raw, ret = load(name), load(name, ".ret")
    return [1 - ret[k]["ret_patch"] for k in raw if raw[k]["patch"] is not None and k in ret
            and ret[k]["ret_patch"] is not None and (keys is None or k in keys)]


def abl_stats(name):
    """(Fixed %, Loss %, Intact %) of a variant; the matched random holes average their three draws."""
    if name == RAND[0]:
        if not all(load(r) is not None and load(r, ".ret") is not None for r in RAND):
            return None
        ss = [stats(r) for r in RAND]
        return sum(100 * x[1] / x[0] for x in ss) / 3, sum(x[2] for x in ss) / 3, sum(x[4] for x in ss) / 3
    s = stats(name)
    return (100 * s[1] / s[0], s[2], s[4]) if s else None


BINS = [(0, 0), (0, 10), (10, 25), (25, 50), (50, 100)]   # skeleton-loss bins (%) of the RQ1 figure


def student_loss(keys=None, intact=False):
    """Skeleton loss (%) of the students' own accepted submissions, or (intact=True) the % of them keeping the whole skeleton."""
    ret = load("histra_min", ".ret")
    xs = [r["ret_oracle"] for k, r in ret.items() if r["ret_oracle"] is not None and (keys is None or k in keys)]
    return 100 * sum(x == 1.0 for x in xs) / len(xs) if intact else 100 * (1 - sum(xs) / len(xs))


# Fig. limit (Section II-B): on the whole benchmark, problems grouped by their point value in the AtCoder contest;
# x = 0, 1, 2 for 200, 300, and 600 points (the xticks of fig:limit in main.tex).
POINTS = {"p02694": 200, "p02742": 200, "p03324": 200, "p02686": 600}       # all other problems are 300-point problems
LIMIT_GROUPS = [(200, 0), (300, 1), (600, 2)]


def by_difficulty(pids):
    """Problems ordered easy (200 points) -> medium (300) -> hard (600), then by id: the row order of Tables II and III."""
    return sorted(pids, key=lambda p: (POINTS.get(p, 300), p))


def band_rule(prev, pid):
    """A rule between the difficulty groups of a per-problem table."""
    return "\\midrule\n" if prev is not None and POINTS.get(prev, 300) != POINTS.get(pid, 300) else ""


def identifiers(src):
    """Variable, function, and parameter names of a program (None if it does not parse)."""
    try:
        t = ast.parse(src)
    except (SyntaxError, ValueError):
        return None
    return {n.id for n in ast.walk(t) if isinstance(n, ast.Name)} | {a.arg for a in ast.walk(t) if isinstance(a, ast.arg)}


def ident_kept(name):
    """{trajectory: share of the identifiers of b that the passing patch keeps}; name = 'student' uses P_ac."""
    raw = load("histra_min" if name == "student" else name)
    out = {}
    for k, r in raw.items():
        f = r["oracle"] if name == "student" else r["patch"]
        b, fi = identifiers(r["was"][-1]), identifiers(f) if f else None
        if b and fi is not None:
            out[k] = len(b & fi) / len(b)
    return out


def limit_fig_rows():
    """Fig. limit: per point group, the students' own skeleton loss and share of intact fixes, and the same for the
    passing patches of each prior repairer (no point where it fixed nothing); one line per series."""
    keys = set(load("histra_min"))
    group = lambda pt: {k for k in keys if POINTS.get(k[0], 300) == pt}
    for n, _ in PRELIM:                         # the numbers of Section II-B's text
        st = stats(n, keys)
        print(f"Fig. limit {n}: loss {st[2]:.1f}% = {st[2] / student_loss(keys):.2f}x the students' {student_loss(keys):.1f}% | "
              f"intact {st[4]:.1f}% vs the students' {student_loss(keys, intact=True):.1f}%")
    out = []
    for key, idx in (("loss", 2), ("intact", 4)):
        out.append(f"% FIG-limit{key} rows: one line per series over the point groups (x = 0..2)")
        out.append("\\addplot[lim stu] coordinates {" + " ".join(
            f"({x},{student_loss(group(pt), intact=key == 'intact'):.1f})" for pt, x in LIMIT_GROUPS) + "};")
        for n, style in zip([n for n, _ in PRELIM], ("lim ref", "lim lsg")):
            pts = [(stats(n, group(pt)), x) for pt, x in LIMIT_GROUPS]
            out.append(f"\\addplot[{style}] coordinates {{" + " ".join(f"({x},{st[idx]:.1f})" for st, x in pts if st and st[2] is not None) + "};")
    return out


def wilcoxon(xs, ys):
    """Two-sided Wilcoxon signed-rank test, normal approximation with tie correction (zero differences dropped)."""
    d = [x - y for x, y in zip(xs, ys) if x != y]
    n = len(d)
    order = sorted(range(n), key=lambda i: abs(d[i]))
    ranks, i, ties = [0.0] * n, 0, 0.0
    while i < n:
        j = i
        while j + 1 < n and abs(d[order[j + 1]]) == abs(d[order[i]]):
            j += 1
        for k in range(i, j + 1):
            ranks[order[k]] = (i + j) / 2 + 1
        t = j - i + 1
        ties += t ** 3 - t
        i = j + 1
    w = sum(r for r, x in zip(ranks, d) if x > 0)
    var = n * (n + 1) * (2 * n + 1) / 24 - ties / 48
    z = (w - n * (n + 1) / 4) / math.sqrt(var)
    return n, z, math.erfc(abs(z) / math.sqrt(2))


def holm(ps, alpha=0.05):
    """Number of hypotheses rejected by the Holm step-down procedure."""
    k = 0
    for i, p in enumerate(sorted(ps)):
        if p >= alpha / (len(ps) - i):
            break
        k += 1
    return k


def mcnemar(b, c):
    """Exact two-sided McNemar test on the discordant counts b (only A fixed) and c (only B fixed)."""
    n = b + c
    if n == 0:
        return 1.0
    tail = sum(math.comb(n, i) for i in range(min(b, c) + 1)) / 2 ** n
    return min(1.0, 2 * tail)


def paired(a, b, by_pid=True):
    """A vs B: repair rate (McNemar) and skeleton retention on trajectories both fixed (Wilcoxon, r = |z|/sqrt(n))."""
    ra, rb, ea, eb = load(a), load(b), load(a, ".ret"), load(b, ".ret")
    if None in (ra, rb, ea, eb):
        return
    fa = {k for k, r in ra.items() if r["patch"] is not None}
    fb = {k for k, r in rb.items() if r["patch"] is not None}
    common = [k for k in fa & fb if k in ea and k in eb and ea[k]["ret_patch"] is not None and eb[k]["ret_patch"] is not None]
    n, z, p = wilcoxon([ea[k]["ret_patch"] for k in common], [eb[k]["ret_patch"] for k in common])
    la = 100 * (1 - sum(ea[k]["ret_patch"] for k in common) / max(len(common), 1))
    lb = 100 * (1 - sum(eb[k]["ret_patch"] for k in common) / max(len(common), 1))
    line = (f"{a} vs {b}: RR only-A {len(fa - fb)} only-B {len(fb - fa)} McNemar p {mcnemar(len(fa - fb), len(fb - fa)):.3g} | "
            f"loss on {len(common)} both-fixed {la:.1f} vs {lb:.1f}, non-tied {n}, z {z:.2f}, p {p:.2e}, "
            f"r {abs(z) / math.sqrt(max(n, 1)):.2f} (non-tied) / {abs(z) / math.sqrt(max(len(common), 1)):.2f} (all)")
    if by_pid:
        ps = []
        for pid in sorted({k[0] for k in common}):
            c = [k for k in common if k[0] == pid]
            ps.append(wilcoxon([ea[k]["ret_patch"] for k in c], [eb[k]["ret_patch"] for k in c])[2])
        line += f" | per problem p<.05 raw {sum(p < 0.05 for p in ps)}/{len(ps)}, Holm {holm(ps)}/{len(ps)}"
    print(line)


def phase_report(base="refactory"):
    """HISTRA hole-only vs free-phase trajectories: losses of HISTRA, the student, and a baseline on the same keys."""
    ph, h, o = phases(), load("histra_min", ".ret"), load(base, ".ret")
    if ph is None or o is None:
        return
    for phase in ("hole", "free"):
        ks = [k for k, r in ph.items() if r["phase"] == phase and k in h and h[k]["ret_patch"] is not None]
        touch = [k for k in ks if h[k]["ret_oracle"] is not None]
        st = [h[k]["ret_oracle"] for k in touch]
        ob = [o[k]["ret_patch"] for k in ks if o and k in o and o[k]["ret_patch"] is not None]
        print(f"{phase}: {len(ks)} traj | HISTRA loss {100 * (1 - sum(h[k]['ret_patch'] for k in ks) / len(ks)):.1f} | "
              f"student loss {100 * (1 - sum(st) / len(st)):.1f} | student fix touches skeleton {100 * sum(x < 1 for x in st) / len(st):.1f}% | "
              f"{base} loss on same {len(ob)} {100 * (1 - sum(ob) / max(len(ob), 1)):.1f}")


def fmt(x):
    return "--" if x is None else f"{x:.1f}"


if __name__ == "__main__":
    base = load("histra_min")
    pids = sorted({k[0] for k in base})
    by = defaultdict(set)
    for k in base: by[k[0]].add(k)
    avail = [(n, l) for n, l in MAIN if load(n) is not None and load(n, ".ret") is not None]
    print("== RQ1 table rows (Problem & #Traj & per repairer Fixed% Loss% & Student Loss%)")
    for pid in pids + ["Total"]:
        ks = None if pid == "Total" else by[pid]
        cells = []
        for n, _ in avail:
            tot, fx, loss, _, _ = stats(n, ks)
            cells += [fmt(100 * fx / tot), fmt(loss)]
        print(f"{pid} & {len(ks or base):,} & " + " & ".join(cells) + f" & {fmt(student_loss(ks))} \\\\")
    print("columns:", [l for _, l in avail])
    print("\n== RQ1 overall")
    for n, l in avail:
        tot, fx, loss, ex, it = stats(n)
        print(f"{n}: fixed {fx}/{tot} = {100*fx/tot:.1f}% | loss {fmt(loss)}% | whole skeleton kept {it:.1f}% | identical to own AC {ex:.1f}%")
    print(f"student: loss {student_loss():.1f}%")
    for b, _ in BASE:
        paired("histra_min", b)
    ph = phases()
    if ph:
        for phase in ("hole", "free"):
            ks = {k for k, r in ph.items() if r["phase"] == phase}
            _, fx, loss, ex, it = stats("histra_min", ks)
            print(f"HISTRA {phase}-phase patches: {fx} | loss {fmt(loss)}% | whole skeleton kept {it:.1f}%")
    print("\n== RQ2 (ablation) rows")
    for n, l in ABL:
        s = stats(n)
        if s:
            tot, fx, loss, ex, it = s
            print(f"{l} & {100*fx/tot:.1f} & {fmt(loss)} & {it:.1f} \\\\")
    print("\n== RQ3 (generality) rows")
    for n, l in GEN:
        s = stats(n)
        if s:
            tot, fx, loss, ex, it = s
            extra = ""
            raw = load(n)
            if raw and any("phase" in r for r in raw.values()):
                extra = f" | hole-only {sum(r.get('phase') == 'hole' for r in raw.values())}"
            print(f"{l} & {100*fx/tot:.1f} & {fmt(loss)} & {it:.1f} \\\\{extra}")


CONCEPTS = {   # what each problem exercises (from its statement), for the benchmark table
    "p02623": "Prefix sums, two pointers", "p02659": "Floating-point precision",
    "p02686": "Greedy ordering of strings", "p02694": "Simulation, integer arithmetic",
    "p02742": "Parity, edge cases", "p02743": "Precision of square roots",
    "p02761": "Digit constraints, leading zero", "p02823": "Parity, boundary moves",
    "p02891": "Runs across repetitions", "p02975": "Counting, XOR",
    "p03240": "Exhaustive search", "p03324": "Arithmetic with an exception",
    "p03438": "Counting operations", "p03838": "Case analysis on signs"}


def bench_rows():
    """Benchmark table: problem, concept, #trajectories, #buggy submissions, #tests, mean non-blank lines of
    the buggy submissions."""
    import statistics
    data = os.path.join(os.path.dirname(__file__), "..", "..", "..", "data")
    out = ["% BENCH rows: Problem & Concept & #Traj & #Buggy (total buggy submissions) & #Tests & Avg LOC (mean non-blank lines of the buggy submissions)"]
    tot_t, tot_tests, locs_all, buggy_all = 0, [], [], []
    prev = None
    for pid in by_difficulty(CONCEPTS):
        ts = [json.loads(l) for l in open(f"{data}/{pid}/trajectories.jsonl")]
        tests = sum(1 for _ in open(f"{data}/{pid}/tests.jsonl"))
        locs = [len([l for l in x["code"].splitlines() if l.strip()]) for t in ts for x in t["submissions"]
                if x["verdict"] != "Accepted"]
        buggy = [sum(x["verdict"] != "Accepted" for x in t["submissions"]) for t in ts]
        tot_t += len(ts); tot_tests.append(tests); locs_all += locs; buggy_all += buggy
        out.append(f"{band_rule(prev, pid)}{pid} & {CONCEPTS[pid]} & {len(ts)} & {sum(buggy):,} & {tests} & {statistics.mean(locs):.1f} \\\\")
        prev = pid
    out.append(f"\\midrule\nTotal & & {tot_t:,} & {sum(buggy_all):,} & {sum(tot_tests)} & {statistics.mean(locs_all):.1f} \\\\")
    return out


EXP_BINS = [("-70--0", -1e9, -1e-6), ("0", -1e-6, 1e-6), ("0--10", 1e-6, 10), ("10--30", 10, 30), ("30--70", 30, 1e9)]


def expert_rows():
    """RQ4 figure: the rated pairs binned by how much more of the skeleton (pp) HISTRA's patch keeps than the
    history-free one; bars = number of pairs per bin, line = share (%) of them in which the instructors chose HISTRA as
    feedback (adjudicated P-Feedback)."""
    E = "results/expert_eval"
    if not os.path.exists(f"{E}/key.csv"):
        return []
    key = {r["item"]: r for r in csv.DictReader(open(f"{E}/key.csv")) if r["set"] == "rating"}
    adj = {r["item"]: r for r in csv.DictReader(open(f"{E}/ratings_recalibrated_consensus.csv", encoding="utf-8-sig"))}
    rh, rn = load("histra_min", ".ret"), load("histra_nohist", ".ret")
    gap = lambda i: 100 * (rh[key[i]["pid"], key[i]["user"]]["ret_patch"] - rn[key[i]["pid"], key[i]["user"]]["ret_patch"])
    chose = lambda i, q: adj[i][q] == ("A" if key[i]["A"] == "histra_min" else "B")
    bins = [[i for i in key if lo < gap(i) <= hi] for _, lo, hi in EXP_BINS]
    rate = lambda q: " ".join(f"({x},{100 * sum(chose(i, q) for i in g) / len(g):.1f})" for x, g in enumerate(bins))
    return [f"% FIG-expcount rows: pairs per bin ({', '.join(l for l, _, _ in EXP_BINS)}; skeleton kept by HISTRA minus HISTRA-empty, pp)",
            "\\addplot[exp count] coordinates {" + " ".join(f"({x},{len(g)})" for x, g in enumerate(bins)) + "};",
            f"% FIG-exprate rows: % of the pairs per bin in which the instructors chose HISTRA (P-Feedback; P-Intent: {rate('P_Intent')})",
            "\\addplot[exp rate] coordinates {" + rate("P_Feedback") + "};"]


def rq1_rows():
    """RQ1 table: Fixed, Loss, and Intact (%) per difficulty group and overall, per technique (MAIN) and for the students'
    own accepted submissions. Bold = best among the techniques; "--" = no passing patch."""
    groups = defaultdict(set)
    for k in load("histra_min"):
        groups[POINTS.get(k[0], 300)].add(k)
    out = ["% RQ1 rows: metric & difficulty & per technique (MAIN) & Student"]
    for m, (label, better) in enumerate((("Fixed", max), ("Loss", min), ("Intact", max))):
        for g, (name, ks) in enumerate([("Easy", groups[200]), ("Medium", groups[300]), ("Hard", groups[600]), ("Overall", None)]):
            vs = [stats(n, ks) for n, _ in MAIN]
            xs = [100 * v[1] / v[0] if m == 0 else (None if not v[1] else v[2] if m == 1 else v[4]) for v in vs]
            best = f"{better(x for x in xs if x is not None):.1f}"
            cells = ["--" if x is None else f"\\textbf{{{x:.1f}}}" if f"{x:.1f}" == best else f"{x:.1f}" for x in xs]
            stu = "" if m == 0 else f"{student_loss(ks, intact=m == 2):.1f}"
            head = ("\\midrule\n" if m and g == 0 else f"\\cline{{2-{len(MAIN) + 3}}}\n" if g == 3 else "") + \
                (f"\\multirow{{4}}{{*}}{{\\rotatebox[origin=c]{{90}}{{{label}}}}}" if g == 0 else "")
            out.append(f"{head} & {chr(92) + 'rule{0pt}{2.6ex}' if g == 3 else ''}{name} & " + " & ".join(cells) + f" & {stu} \\\\")
    return out


def close_fig_rows(em):
    """RQ2 figure on the trajectories that all MAIN techniques fix (edit_metrics.json + ident_kept): Kept and Ident (%)
    as bars on the left axis with the students' own Ident as a dashed line, and Dist as a line on the right axis."""
    idk = {n: ident_kept(n) for n, _ in MAIN + [("student", "")]}
    key = lambda k: tuple(k.split("/"))
    ks = [k for k, v in em.items() if all(n in v and v[n]["own"] is not None and key(k) in idk[n] for n, _ in MAIN)]
    mean = lambda f: [sum(f(k, n) for k in ks) / len(ks) for n, _ in MAIN]
    pts = lambda xs: " ".join(f"({i},{x:.1f})" for i, x in enumerate(xs))
    kept, ident = mean(lambda k, n: 100 * em[k][n]["own"]), mean(lambda k, n: 100 * idk[n][key(k)])
    dist, stu = mean(lambda k, n: em[k][n]["to_ac"]), 100 * sum(idk["student"][key(k)] for k in ks) / len(ks)
    return [f"% FIG-closebar rows: Kept, Ident (%) per technique (MAIN) on the {len(ks)} trajectories fixed by all, then the students' Ident",
            f"\\addplot[close kept] coordinates {{{pts(kept)}}};", f"\\addplot[close ident] coordinates {{{pts(ident)}}};",
            f"\\addplot[close stu] coordinates {{(-0.5,{stu:.1f}) ({len(MAIN) - 0.5},{stu:.1f})}};",
            "% FIG-closedist rows: Dist per technique (MAIN)", f"\\addplot[close dist] coordinates {{{pts(dist)}}};"]


def abl_rows():
    """RQ3 ablation table: HISTRA, then the variants (design choices) and the controls (source of holes), each group sorted
    by the relative increase of the skeleton loss; cells are Fixed, Loss (relative change), Intact (relative change)."""
    h = abl_stats("histra_min")
    def rel(x, b):
        r = 100 * (x / b - 1)
        return f"{x:.1f} (0.0\\%)" if abs(r) < 0.05 else f"{x:.1f} ({r:+.1f}\\%)".replace("-", "$-$").replace("+", "$+$")
    out = ["% RQ2 rows: ablation: label & Fixed & Loss (rel. change) & Intact (rel. change)",
           f"\\tool{{}} & {h[0]:.1f} & {h[1]:.1f} & {h[2]:.1f} \\\\"]
    first_ctl = [n for n, _ in ABL].index(RAND[0])
    groups = (("Design choice removed or replaced", ABL[1:first_ctl]), ("Source of holes", ABL[first_ctl:]))
    for title, rows in groups:
        vs = sorted(((l, abl_stats(n)) for n, l in rows), key=lambda t: -t[1][1])
        out += ["\\midrule", f"\\multicolumn{{4}}{{l}}{{\\textit{{{title}}}}} \\\\"]
        out += [f"{l} & {v[0]:.1f} & {rel(v[1], h[1])} & {rel(v[2], h[2])} \\\\" for l, v in vs]
    return out


def latex_tables(D):
    """Write tables.tex: Table II (RQ1, by difficulty), Table III (RQ2), Table IV (RQ3). Bold = best among repairers."""
    base = load("histra_min")
    by = defaultdict(set)
    for k in base: by[k[0]].add(k)
    cols = [(n, l) for n, l in MAIN]
    out = rq1_rows()
    out += abl_rows()
    if os.path.exists(f"{D}/edit_metrics.json"):
        out += close_fig_rows(json.load(open(f"{D}/edit_metrics.json")))
    # RQ1 figure: share of passing patches per skeleton-loss bin. Rows (y = 0..6): Student, HISTRA, its hole-only and
    # fallback patches, then the baselines (BASE); one stacked \addplot per bin.
    ph = phases() or {}
    phase = lambda p: {k for k, r in ph.items() if r.get("phase") == p}
    series = [[1 - r["ret_oracle"] for r in load("histra_min", ".ret").values() if r["ret_oracle"] is not None],
              losses("histra_min"), losses("histra_min", phase("hole")), losses("histra_min", phase("free")),
              *[losses(n) for n, _ in BASE]]
    out.append("% FIG-loss rows: one stacked \\addplot per skeleton-loss bin (0, (0,10], (10,25], (25,50], (50,100] %)")
    for b, (lo, hi) in enumerate(BINS):
        inbin = lambda x: round(100 * x, 6) == 0 if hi == 0 else lo < round(100 * x, 6) <= hi
        sh = [100 * sum(map(inbin, xs)) / len(xs) for xs in series]
        # label only the intact (first) segments wide enough to hold their value
        cs = " ".join(f"({x:.1f},{i})" + (f" [{x:.1f}]" if b == 0 and x >= 15 else " []" if b == 0 else "") for i, x in enumerate(sh))
        out.append(f"\\addplot[loss{b}] coordinates {{{cs}}};")
    # RQ3 figure: skeleton loss and intact share per variant (y = 0..5) and control (after a gap of 0.6)
    first_ctl = [n for n, _ in ABL].index(RAND[0])
    bars = {"loss": [], "intact": []}
    for i, (n, _) in enumerate(ABL):
        v = abl_stats(n)
        if not v:
            continue
        y = i if i < first_ctl else i + 0.6
        style = "abl hi" if n == "histra_min" else "abl var" if i < first_ctl else "abl ctl"
        bars["loss"].append(f"\\addplot[{style}] coordinates {{({v[1]:.1f},{y:g})}};")
        bars["intact"].append(f"\\addplot[{style}] coordinates {{({v[2]:.1f},{y:g})}};")
    h = abl_stats("histra_min")
    for key, x in (("loss", h[1]), ("intact", h[2])):
        out.append(f"% FIG-abl{key} rows: one bar per variant/control, dashed line at HISTRA")
        out += [f"\\addplot[abl ref] coordinates {{({x:.1f},-0.6) ({x:.1f},{len(ABL) - 0.4 + 0.6:g})}};"] + bars[key]   # line under the labels
    out += limit_fig_rows() + bench_rows() + expert_rows()
    open(f"{D}/tables.tex", "w").write("\n".join(out) + "\n")
    print(f"wrote {D}/tables.tex")


if __name__ == "__main__":
    print("\n== paired comparisons")
    for a, b in [("histra_min", x) for x in ("histra_nohist", *RAND, "histra_randfrac", "histra_fltop_srv", "histra_flhole_srv",
                                              "histra_nostd", "histra_nohole", "histra_nokept", "histra_plain", "histra_sizemin")]:
        if load(b) is not None:
            paired(a, b, by_pid=b in ("histra_nohist", *RAND, "histra_randfrac", "histra_fltop_srv", "histra_flhole_srv"))
    ih = ident_kept("histra_min")
    print(f"identifiers kept: students' own fixes {100 * sum(ident_kept('student').values()) / len(ident_kept('student')):.1f}%")
    for b, _ in BASE + [("histra_nohist", "")]:
        ib = ident_kept(b)
        ks = [k for k in ih if k in ib]
        n, z, p = wilcoxon([ih[k] for k in ks], [ib[k] for k in ks])
        print(f"identifiers kept, HISTRA vs {b} on {len(ks)} both-fixed: {100 * sum(ih[k] for k in ks) / len(ks):.1f} vs "
              f"{100 * sum(ib[k] for k in ks) / len(ks):.1f}, z {z:.2f}, p {p:.1e}")
    print("\n== phase split")
    for b in [n for n, _ in BASE] + ["histra_nohist"]:
        phase_report(b)
    latex_tables(D)
