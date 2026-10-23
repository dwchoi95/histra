"""Tables, figure data, and the numbers in the text of the paper, from ../output/{approaches,ablation,expert}.
Repair rates count every trajectory; skeleton metrics average over passing patches with a non-empty skeleton.
Usage: python paper/src/summarize.py   -> paper/tables.tex and paper/numbers.txt"""
import ast
import csv
import json
import os
import statistics
import sys
from collections import defaultdict

PAPER = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # <repo>/paper/
sys.path.insert(0, os.path.join(os.path.dirname(PAPER), "src", "experiments"))
from common import DATA, OUT, rows  # noqa: E402

EXPERT = os.path.join(OUT, "expert", "ratings.csv")
BASE = [("refactory", "Refactory"), ("brafar", "Brafar"), ("lsgen", "LSGen")]   # one per group of Section II-A
MAIN = BASE + [("histra", "\\tool{}")]
PRELIM = [("refactory", "Refactory"), ("lsgen", "LSGen")]                     # Fig. 1 (Section II-B)
ABL = [("histra", "\\tool{}"), ("nostd", "\\tool{}$-$Norm"), ("nohole", "\\tool{}$-$Hole"),
       ("nokept", "\\tool{}$-$Kept"), ("plain", "\\tool{}$-$Min"), ("sizemin", "\\tool{}$_{\\mathit{size}}$"),
       ("randhole0", "\\tool{}$_{\\mathit{rand}}$"), ("randfrac", "\\tool{}$_{\\mathit{frac}}$"),
       ("fl", "\\tool{}$_{\\mathit{FL}}$"), ("nohist", "\\tool{}$_{\\emptyset}$")]
RAND = ["randhole0", "randhole1", "randhole2"]                  # three draws, averaged
POINTS = {"p02694": 200, "p02742": 200, "p03324": 200, "p02686": 600}                 # others: 300-point problems
GROUPS = [("Easy", 200), ("Medium", 300), ("Hard", 600)]
CONCEPTS = {
    "p02623": "Prefix sums, two pointers", "p02659": "Floating-point precision",
    "p02686": "Greedy ordering of strings", "p02694": "Simulation, integer arithmetic",
    "p02742": "Parity, edge cases", "p02743": "Precision of square roots",
    "p02761": "Digit constraints, leading zero", "p02823": "Parity, boundary moves",
    "p02891": "Runs across repetitions", "p02975": "Counting, XOR",
    "p03240": "Exhaustive search", "p03324": "Arithmetic with an exception",
    "p03438": "Counting operations", "p03838": "Case analysis on signs"}
EXP_BINS = [("-70--0", -1e9, -1e-6), ("0", -1e-6, 1e-6), ("0--10", 1e-6, 10), ("10--30", 10, 30), ("30--70", 30, 1e9)]

_cache = {}


def load(name):
    if name not in _cache:
        _cache[name] = rows(name)
    return _cache[name]


def stats(name, keys=None):
    """(#trajectories, #fixed, skeleton loss %, intact %) over `keys` (default: all)."""
    raw = ret = load(name)
    ks = [k for k in raw if keys is None or k in keys]
    fixed = [k for k in ks if raw[k]["patch"] is not None]
    rets = [ret[k]["ret_patch"] for k in fixed if ret[k]["ret_patch"] is not None]
    if not rets:
        return len(ks), len(fixed), None, None
    return len(ks), len(fixed), 100 * (1 - sum(rets) / len(rets)), 100 * sum(r == 1.0 for r in rets) / len(rets)


def student(keys=None, intact=False):
    """Skeleton loss (%) of the students' own accepted submissions, or the share (%) of intact ones."""
    xs = [r["ret_oracle"] for k, r in load("histra").items() if r["ret_oracle"] is not None and (keys is None or k in keys)]
    return 100 * sum(x == 1.0 for x in xs) / len(xs) if intact else 100 * (1 - sum(xs) / len(xs))


def group(points):
    return {k for k in load("histra") if POINTS.get(k[0], 300) == points}


def abl_stats(name):
    """(Fixed %, Loss %, Intact %); the matched random holes average their three draws."""
    ss = [stats(n) for n in (RAND if name == RAND[0] else [name])]
    return tuple(sum(x) / len(ss) for x in zip(*[(100 * s[1] / s[0], s[2], s[3]) for s in ss]))


def identifiers(src):
    try:
        t = ast.parse(src)
    except (SyntaxError, ValueError):
        return None
    return {n.id for n in ast.walk(t) if isinstance(n, ast.Name)} | {a.arg for a in ast.walk(t) if isinstance(a, ast.arg)}


def ident_kept(name):
    """Ident: {trajectory: share of b's identifiers that the passing patch keeps}; 'student' uses P_ac."""
    out = {}
    for k, r in load("histra" if name == "student" else name).items():
        f = r["oracle"] if name == "student" else r["patch"]
        b, fi = identifiers(r["was"][-1]), identifiers(f) if f else None
        if b and fi is not None:
            out[k] = len(b & fi) / len(b)
    return out


def close_set(em):
    """RQ2: trajectories fixed by all MAIN techniques, with every metric defined."""
    idk = {n: ident_kept(n) for n, _ in MAIN + [("student", "")]}
    key = lambda k: tuple(k.split("/"))
    ks = [k for k, v in em.items() if all(n in v and v[n]["kept"] is not None and key(k) in idk[n] for n, _ in MAIN)]
    return ks, idk, key


def rel(x, b):
    return 100 * (x / b - 1)


def bench_rows():
    """Table I: problem, concept, #trajectories, #buggy programs, #tests, mean non-blank lines of the buggy programs."""
    out, tot, tests_all, locs_all, buggy_all, prev = ["% rows:bench"], 0, 0, [], 0, None
    for pid in sorted(CONCEPTS, key=lambda p: (POINTS.get(p, 300), p)):
        ts = [json.loads(l) for l in open(os.path.join(DATA, pid, "trajectories.jsonl"))]
        tests = sum(1 for _ in open(os.path.join(DATA, pid, "tests.jsonl")))
        locs = [len([l for l in s["code"].splitlines() if l.strip()]) for t in ts for s in t["submissions"]
                if s["verdict"] != "Accepted"]
        tot, tests_all, locs_all, buggy_all = tot + len(ts), tests_all + tests, locs_all + locs, buggy_all + len(locs)
        rule = "\\midrule\n" if prev is not None and POINTS.get(prev, 300) != POINTS.get(pid, 300) else ""
        out.append(f"{rule}{pid} & {CONCEPTS[pid]} & {len(ts)} & {len(locs):,} & {tests} & {statistics.mean(locs):.1f} \\\\")
        prev = pid
    return out + [f"\\midrule\nTotal & & {tot:,} & {buggy_all:,} & {tests_all} & {statistics.mean(locs_all):.1f} \\\\"]


def limit_rows():
    """Fig. 1: per difficulty, skeleton loss and intact share of the students' own fixes and of the prior repairers."""
    out = []
    for key in ("loss", "intact"):
        out.append(f"% rows:figlimit{key}")
        out.append("\\addplot[lim stu] coordinates {" + " ".join(
            f"({x},{student(group(pt), intact=key == 'intact'):.1f})" for x, (_, pt) in enumerate(GROUPS)) + "};")
        for (n, _), style in zip(PRELIM, ("lim ref", "lim lsg")):
            pts = [(stats(n, group(pt)), x) for x, (_, pt) in enumerate(GROUPS)]
            out.append(f"\\addplot[{style}] coordinates {{" + " ".join(
                f"({x},{st[2 if key == 'loss' else 3]:.1f})" for st, x in pts if st[2] is not None) + "};")
    return out


def rq1_rows():
    """Table II: Fixed, Loss, and Intact (%) per difficulty and overall; bold = best; "--" = nothing passed."""
    out = ["% rows:rq1"]
    for m, (label, better) in enumerate((("Fixed", max), ("Loss", min), ("Intact", max))):
        for g, (name, ks) in enumerate([(n, group(pt)) for n, pt in GROUPS] + [("Overall", None)]):
            vs = [stats(n, ks) for n, _ in MAIN]
            xs = [100 * v[1] / v[0] if m == 0 else v[1 + m] for v in vs]
            best = f"{better(x for x in xs if x is not None):.1f}"
            cells = ["--" if x is None else f"\\textbf{{{x:.1f}}}" if f"{x:.1f}" == best else f"{x:.1f}" for x in xs]
            stu = "" if m == 0 else f"{student(ks, intact=m == 2):.1f}"
            head = ("\\midrule\n" if m and g == 0 else f"\\cline{{2-{len(MAIN) + 3}}}\n" if g == 3 else "") + \
                (f"\\multirow{{4}}{{*}}{{\\rotatebox[origin=c]{{90}}{{{label}}}}}" if g == 0 else "")
            out.append(f"{head} & {chr(92) + 'rule{0pt}{2.6ex}' if g == 3 else ''}{name} & " + " & ".join(cells) + f" & {stu} \\\\")
    return out


def close_rows(em):
    """Fig. 4: Kept and Ident (%) as bars, the students' own Ident as a dashed line, and Dist as a line."""
    ks, idk, key = close_set(em)
    mean = lambda f: [sum(f(k, n) for k in ks) / len(ks) for n, _ in MAIN]
    pts = lambda xs: " ".join(f"({i},{x:.1f})" for i, x in enumerate(xs))
    kept, ident = mean(lambda k, n: 100 * em[k][n]["kept"]), mean(lambda k, n: 100 * idk[n][key(k)])
    dist, stu = mean(lambda k, n: em[k][n]["dist"]), 100 * sum(idk["student"][key(k)] for k in ks) / len(ks)
    return ["% rows:figclosebar", f"\\addplot[close kept] coordinates {{{pts(kept)}}};",
            f"\\addplot[close ident] coordinates {{{pts(ident)}}};",
            f"\\addplot[close stu] coordinates {{(-0.5,{stu:.1f}) ({len(MAIN) - 0.5},{stu:.1f})}};",
            "% rows:figclosedist", f"\\addplot[close dist] coordinates {{{pts(dist)}}};"]


def abl_rows():
    """Table III: HISTRA, then the variants and the controls, each sorted by the relative increase of the loss."""
    h = abl_stats("histra")
    def cell(x, b):
        r = rel(x, b)
        return f"{x:.1f} (0.0\\%)" if abs(r) < 0.05 else f"{x:.1f} ({r:+.1f}\\%)".replace("-", "$-$").replace("+", "$+$")
    out = ["% rows:rq2", f"\\tool{{}} & {h[0]:.1f} & {h[1]:.1f} & {h[2]:.1f} \\\\"]
    first = [n for n, _ in ABL].index(RAND[0])
    for title, part in (("Design choice removed or replaced", ABL[1:first]), ("Source of holes", ABL[first:])):
        vs = sorted(((l, abl_stats(n)) for n, l in part), key=lambda t: -t[1][1])
        out += ["\\midrule", f"\\multicolumn{{4}}{{l}}{{\\textit{{{title}}}}} \\\\"]
        out += [f"{l} & {v[0]:.1f} & {cell(v[1], h[1])} & {cell(v[2], h[2])} \\\\" for l, v in vs]
    return out


def expert():
    """RQ4 pairs: (skeleton kept by HISTRA minus HISTRA_empty in pp, chose HISTRA for P-Feedback, for P-Intent)."""
    rh, rn = load("histra"), load("nohist")
    out = []
    for r in csv.DictReader(open(EXPERT, newline="")):
        t = r["pid"], r["user"]
        out.append((100 * (rh[t]["ret_patch"] - rn[t]["ret_patch"]), r["feedback"] == "histra", r["intent"] == "histra"))
    return out


def expert_rows():
    """Fig. 5: pairs per bin of the skeleton gap (bars) and the share (%) in which instructors chose HISTRA (line)."""
    bins = [[p for p in expert() if lo < p[0] <= hi] for _, lo, hi in EXP_BINS]
    return ["% rows:figexpcount", "\\addplot[exp count] coordinates {" + " ".join(f"({x},{len(b)})" for x, b in enumerate(bins)) + "};",
            "% rows:figexprate", "\\addplot[exp rate] coordinates {" + " ".join(
                f"({x},{100 * sum(p[1] for p in b) / len(b):.1f})" for x, b in enumerate(bins)) + "};"]


def numbers(em):
    out = []
    say = out.append
    h = stats("histra")
    say("== Section II-B (Fig. 1)")
    say(f"students' own fixes: skeleton loss {student():.1f}%, intact {student(intact=True):.1f}%; by difficulty loss " +
        ", ".join(f"{n} {student(group(pt)):.1f}%" for n, pt in GROUPS))
    for n, _ in PRELIM:
        s = stats(n)
        say(f"{n}: loss {s[2]:.1f}% ({s[2] / student():.2f}x the students'), intact {s[3]:.1f}% "
            f"(patches changing the skeleton {100 - s[3]:.1f}%); by difficulty loss " +
            ", ".join(f"{name} {stats(n, group(pt))[2]:.1f}%" for name, pt in GROUPS if stats(n, group(pt))[2] is not None))
    say("(run fixregion.py for the shares of code inside and outside the skeleton that the students' fixes change)")

    say("\n== Section III-E")
    hm = load("histra")
    fixed = [r for r in hm.values() if r["patch"] is not None]
    say(f"passing patches from the hole-only phase: {sum(r['phase'] == 'hole' for r in fixed)}/{len(fixed)} = "
        f"{100 * sum(r['phase'] == 'hole' for r in fixed) / len(fixed):.1f}%")

    say("\n== RQ1 (Table II)")
    say(f"HISTRA fixed {h[1]}/{h[0]} = {100 * h[1] / h[0]:.1f}%, loss {h[2]:.1f}%, intact {h[3]:.1f}%")
    ret = {n: load(n) for n, _ in MAIN}
    for n, _ in BASE:
        s = stats(n)
        both = [k for k in hm if hm[k]["patch"] and load(n)[k]["patch"] and ret["histra"][k]["ret_patch"] is not None
                and ret[n][k]["ret_patch"] is not None]
        lh = 1 - sum(ret["histra"][k]["ret_patch"] for k in both) / len(both)
        lb = 1 - sum(ret[n][k]["ret_patch"] for k in both) / len(both)
        say(f"vs {n} ({100 * s[1] / s[0]:.1f}% / {s[2]:.1f}% / {s[3]:.1f}%): fixed {rel(h[1] / h[0], s[1] / s[0]):+.1f}%, "
            f"loss {rel(h[2], s[2]):+.1f}%, intact {rel(h[3], s[3]):+.1f}% | on the {len(both)} trajectories both fixed: "
            f"loss {100 * lh:.1f}% vs {100 * lb:.1f}% ({rel(lh, lb):+.1f}%)")
        for name, pt in GROUPS:
            g, sg = stats("histra", group(pt)), stats(n, group(pt))
            if sg[1]:
                say(f"   {name}: fixed {rel(g[1] / g[0], sg[1] / sg[0]):+.1f}%, loss {rel(g[2], sg[2]):+.1f}%, intact " +
                    (f"{rel(g[3], sg[3]):+.1f}%" if sg[3] else f"{g[3]:.1f}% vs {sg[3]:.1f}%"))
    rf = rr = load("refactory")
    mut = [k for k, r in rf.items() if r["status"] == "success_w_mut"]
    loss = lambda ks: 100 * (1 - statistics.mean(rr[k]["ret_patch"] for k in ks if rr[k]["ret_patch"] is not None))
    say(f"Refactory mutated the control flow of b in {len(mut)}/{sum(r['patch'] is not None for r in rf.values())} = "
        f"{100 * len(mut) / sum(r['patch'] is not None for r in rf.values()):.1f}% of its passing patches; they changed "
        f"{loss(mut):.1f}% of the skeleton vs {loss([k for k, r in rf.items() if r['patch'] and k not in mut]):.1f}% for the others")
    for phase in ("hole", "free"):
        ks = [k for k, r in hm.items() if r["patch"] and r["phase"] == phase and ret["histra"][k]["ret_patch"] is not None]
        xs = [ret["histra"][k]["ret_patch"] for k in ks]
        line = f"HISTRA {phase}-phase patches: loss {100 * (1 - statistics.mean(xs)):.1f}%, intact {100 * sum(x == 1 for x in xs) / len(xs):.1f}%"
        for n, _ in BASE:
            ys = [ret[n][k]["ret_patch"] for k in ks if load(n)[k]["patch"] and ret[n][k]["ret_patch"] is not None]
            line += f" | {n} on the same {len(ys)}: {100 * (1 - statistics.mean(ys)):.1f}%"
        say(line)
    p = [r for r in fixed if r["pid"] == "p02686"]
    say(f"p02686: passing patches from the hole-only phase {100 * sum(r['phase'] == 'hole' for r in p) / len(p):.1f}%")

    say("\n== RQ2 (Fig. 4)")
    ks, idk, key = close_set(em)
    say(f"trajectories fixed by all techniques: {len(ks)}")
    m = {n: (100 * statistics.mean(em[k][n]["kept"] for k in ks), 100 * statistics.mean(idk[n][key(k)] for k in ks),
             statistics.mean(em[k][n]["dist"] for k in ks)) for n, _ in MAIN}
    say(f"students' own Ident {100 * statistics.mean(idk['student'][key(k)] for k in ks):.1f}%")
    for n, _ in MAIN:
        say(f"{n}: Kept {m[n][0]:.1f}%, Ident {m[n][1]:.1f}%, Dist {m[n][2]:.1f}" + ("" if n == "histra" else
            f" | HISTRA: Kept {rel(m['histra'][0], m[n][0]):+.1f}%, Ident {rel(m['histra'][1], m[n][1]):+.1f}%, "
            f"Dist {rel(m['histra'][2], m[n][2]):+.1f}%"))
    fb = [k for k in ks if hm[key(k)]["phase"] == "free"]
    say(f"Ident of HISTRA's fallback patches: {100 * statistics.mean(idk['histra'][key(k)] for k in fb):.1f}% ({len(fb)} trajectories)")
    for label, part in (("the student's fix keeps the skeleton", [k for k in ks if ret["histra"][key(k)]["ret_oracle"] == 1.0]),
                        ("the student's fix changes the skeleton", [k for k in ks if ret["histra"][key(k)]["ret_oracle"] is not None
                                                            and ret["histra"][key(k)]["ret_oracle"] < 1.0])):
        mm = {n: (statistics.mean(em[k][n]["kept"] for k in part), statistics.mean(em[k][n]["dist"] for k in part)) for n, _ in MAIN}
        say(f"{label} ({len(part)}): " + ", ".join(f"{n} Kept {100 * mm[n][0]:.1f}% Dist {mm[n][1]:.1f}" for n, _ in MAIN) +
            " | HISTRA vs baselines: Kept " + ", ".join(f"{rel(mm['histra'][0], mm[n][0]):+.1f}%" for n, _ in BASE) +
            "; Dist " + ", ".join(f"{rel(mm['histra'][1], mm[n][1]):+.1f}%" for n, _ in BASE))

    say("\n== RQ3 (Table III)")
    for n in RAND:
        s = stats(n)
        say(f"{n}: loss {s[2]:.1f}%, intact {s[3]:.1f}%")
    for n in ("histra", "fl"):
        rs = [r for r in load(n).values() if r.get("units")]
        say(f"{n}: the whole program is holed in {100 * sum(r['cover'] == r['units'] for r in rs) / len(rs):.1f}% of the trajectories")
    say("(run std_effect.py for the share of the trajectories whose skeleton normalization changes)")

    say("\n== RQ4 (Fig. 5; run expert_analyze.py for the shares, the sign tests, and the agreement)")
    ps = expert()
    say(f"pairs in which HISTRA kept more / the same / less of the skeleton: {sum(p[0] > 1e-6 for p in ps)} / "
        f"{sum(abs(p[0]) <= 1e-6 for p in ps)} / {sum(p[0] < -1e-6 for p in ps)}")
    for label, lo, hi in EXP_BINS:
        b = [p for p in ps if lo < p[0] <= hi]
        say(f"   gap {label} pp: {len(b)} pairs, chose HISTRA as feedback {100 * sum(p[1] for p in b) / len(b):.1f}%, "
            f"as preserving the intent {100 * sum(p[2] for p in b) / len(b):.1f}%")

    say("\n== Threats to validity")
    one = {k for k, r in hm.items() if len(r["was"]) == 2}
    say(f"trajectories with one earlier submission (|H| = 1): {len(one)}/{len(hm)} = {100 * len(one) / len(hm):.1f}%; loss there " +
        ", ".join(f"{n} {stats(n, one)[2]:.1f}%" for n, _ in MAIN))
    return out


if __name__ == "__main__":
    em = {f"{p}/{u}": {n: load(n)[p, u] for n, _ in MAIN} for p, u in load("histra")}
    tables = bench_rows() + limit_rows() + rq1_rows() + close_rows(em) + abl_rows() + expert_rows()
    open(os.path.join(PAPER, "tables.tex"), "w").write("\n".join(tables) + "\n")
    text = numbers(em)
    open(os.path.join(PAPER, "numbers.txt"), "w").write("\n".join(text) + "\n")
    print("\n".join(text))
    print(f"\nwrote {os.path.join(PAPER, 'tables.tex')} and {os.path.join(PAPER, 'numbers.txt')}")
