import ast, csv, json, os, re
from collections import defaultdict
from tqdm import tqdm
import warnings
warnings.filterwarnings("ignore")


class DatasetBuilder:
    AC = "Accepted"
    WA = "Wrong Answer"
    MIN_TRAJ = 100 # keep only problems with >= 100 qualifying trajectories

    CN = "/Users/cdw/VSCode/aria/data/Project_CodeNet"
    META = os.path.join(CN, "metadata")
    TESTS = os.path.join(CN, "test_cases")
    PLIST = os.path.join(META, "problem_list.csv")
    BENCH = os.path.join(CN, "derived", "benchmarks", "Project_CodeNet_Python800")
    OUT_ROOT = "data"

    _CONTEST = re.compile(r"AtCoder (Beginner|Regular|Grand) Contest (\d+)")
    _TYPE = {"Beginner": "ABC", "Regular": "ARC", "Grand": "AGC"}
    # 9 non-ABC/ARC/AGC AtCoder contests that have a test dir: contest name -> dir
    SPECIAL = {
        "DISCO Presents Discovery Channel Code Contest 2020 Qual": "2019ddccqual",
        "ExaWizards 2019": "2019exa",
        "NIKKEI Programming Contest 2019": "2019nikkei_qual",          # not "2019-2"
        "Yahoo Programming Contest 2019": "2019yahoo_qual",
        "Dwango Programming Contest 6th": "2020_dwango_qual",
        "Social Infrastructure Information Systems Division  Hitachi Programming Contest 2020": "2020_hitachi",
        "Panasonic Programming Contest 2020": "2020_panasonic",
        "ACL Contest 1": "ACL1",
        "AtCoder Petrozavodsk Contest 001": "APC001",
    }

    # ----------------------------------------------------------- problem selection
    def benchmark_pids(self):
        return {d for d in os.listdir(self.BENCH) if d.startswith("p")}

    def benchmark_sids(self, pid):
        """Submission ids sampled into Python800 for this problem (all Accepted)."""
        d = os.path.join(self.BENCH, pid)
        if not os.path.isdir(d):
            return set()
        return {os.path.splitext(f)[0] for f in os.listdir(d) if f.endswith(".py")}

    def problem_limits(self):
        """pid -> {'time_limit_ms', 'memory_limit_kb'} from problem_list.csv (cols time_limit/memory_limit)."""
        out = {}
        with open(self.PLIST, encoding="utf-8", errors="replace") as f:
            r = csv.reader(f); next(r, None)
            for row in r:
                if len(row) >= 5 and row[0].startswith("p"):
                    try:
                        out[row[0]] = {"time_limit_ms": int(row[3]), "memory_limit_kb": int(row[4])}
                    except ValueError:
                        pass
        return out

    def atcoder_problems(self):
        """AtCoder problems that are also in the Python800 benchmark."""
        bench = self.benchmark_pids()
        out = []
        with open(self.PLIST, encoding="utf-8", errors="replace") as f:
            r = csv.reader(f); next(r, None)
            for row in r:
                if len(row) >= 3 and row[2] == "AtCoder" and row[0] in bench:
                    out.append((row[0], row[1]))
        return out

    def contest_letter_map(self, rows):
        """pid -> contest code (ABC141/.../APC001) and pid -> task letter (by pid order)."""
        groups = defaultdict(list)
        pid_code = {}
        for pid, name in rows:
            prefix = name.split(" - ")[0]
            if prefix in self.SPECIAL:
                code = self.SPECIAL[prefix]
            else:
                m = self._CONTEST.search(name)
                if not m:
                    continue
                code = self._TYPE[m.group(1)] + f"{int(m.group(2)):03d}"
            groups[code].append(pid); pid_code[pid] = code
        pid_letter = {}
        for code, pids in groups.items():
            for i, pid in enumerate(sorted(pids)):
                pid_letter[pid] = chr(ord("A") + i)
        return pid_code, pid_letter

    # ----------------------------------------------------------- tests
    def test_pairs(self, testdir):
        """(in_path, out_path) pairs, handling both layouts: '<letter>/in + out'
        and ABC163-style 'inputs flat in <letter>/ + outputs in out/'."""
        outdir = os.path.join(testdir, "out")
        if not os.path.isdir(outdir):
            return []
        outs = {f for f in os.listdir(outdir) if not f.startswith(".")}
        indir = os.path.join(testdir, "in")
        if os.path.isdir(indir):
            in_src = indir
            ins = {f for f in os.listdir(indir) if not f.startswith(".")}
        else:
            in_src = testdir
            ins = {f for f in os.listdir(testdir)
                   if os.path.isfile(os.path.join(testdir, f)) and not f.startswith(".")}
        return [(os.path.join(in_src, k), os.path.join(outdir, k)) for k in sorted(ins & outs)]

    def resolve_testdir(self, code, letter):
        for c in (code, code.lower()):
            d = os.path.join(self.TESTS, c, letter)
            if self.test_pairs(d):
                return d
        return None

    # ----------------------------------------------------------- submissions
    def src(self, pid, sid):
        try:
            with open(os.path.join(self.CN, "data", pid, "Python", sid + ".py"),
                      encoding="utf-8", errors="replace") as f:
                return f.read()
        except OSError:
            return None

    def qualifying(self, pid):
        """Per user: {AC,WA} sequence truncated at first AC with >=2 WA before it.
        Returns list of (user_id, [(sid, ts, verdict), ...]) ending in the AC."""
        csvp = os.path.join(self.META, pid + ".csv")
        if not os.path.exists(csvp):
            return []
        by_user = defaultdict(list)
        with open(csvp, newline="") as f:
            r = csv.reader(f); next(r, None)
            for row in r:
                if len(row) < 8 or row[4] != "Python":
                    continue
                if row[7] in (self.AC, self.WA):
                    by_user[row[2]].append((int(row[3]), row[7], row[0]))   # ts, verdict, sid
        out = []
        for uid, subs in by_user.items():
            subs.sort(key=lambda x: x[0])
            st = [s[1] for s in subs]
            first_ac = next((i for i, s in enumerate(st) if s == self.AC), None)
            if first_ac is None or first_ac < 2:
                continue
            traj = [(sid, ts, verdict) for (ts, verdict, sid) in subs[:first_ac + 1]]
            out.append((uid, traj))
        return out

    def problem_html(self, pid):
        """Raw problem statement HTML, stored verbatim (no processing)."""
        p = os.path.join(self.CN, "problem_descriptions", pid + ".html")
        if not os.path.exists(p):
            return ""
        with open(p, encoding="utf-8", errors="replace") as f:
            return f.read()

    @staticmethod
    def _read(path):
        with open(path, encoding="utf-8", errors="replace") as f:
            return f.read()

    @staticmethod
    def _parses(code):
        """True iff the source is valid Python 3 (filters Python-2 / broken submissions)."""
        try:
            ast.parse(code)
            return True
        except (SyntaxError, ValueError):
            return False

    # ----------------------------------------------------------- build
    def build(self):
        rows = self.atcoder_problems()
        pid_code, pid_letter = self.contest_letter_map(rows)
        limits = self.problem_limits()
        built = []
        for pid, name in tqdm(rows, desc="building", unit="prob"):
            code, letter = pid_code.get(pid), pid_letter.get(pid)
            if not code or not letter:
                continue
            td = self.resolve_testdir(code, letter)
            if not td:
                continue
            pairs = self.test_pairs(td)
            if not pairs:                       # a problem with no tests is unusable
                continue
            bench_sids = self.benchmark_sids(pid)   # Python800 ACs for this problem
            # keep parseable trajectories (final AC in Python800; drop unparsable / all-WA-identical)
            recs = []
            for uid, traj in self.qualifying(pid):
                if traj[-1][0] not in bench_sids:   # last submission = AC; require it in Python800
                    continue
                subs, ok = [], True
                for sid, ts, verdict in traj:
                    c = self.src(pid, sid)
                    if c is None or not self._parses(c):   # drop traj if any submission unreadable/unparsable
                        ok = False
                        break
                    subs.append({"sid": sid, "ts": ts, "verdict": verdict, "code": c})
                if not ok:
                    continue
                wa_codes = [s["code"] for s in subs if s["verdict"] == self.WA]
                if len(set(wa_codes)) <= 1:   # all WA identical -> no real revision, skip traj
                    continue
                recs.append({"problem_id": pid, "user_id": uid, "submissions": subs})
            if len(recs) < self.MIN_TRAJ:
                continue
            pdir = os.path.join(self.OUT_ROOT, pid)
            os.makedirs(pdir, exist_ok=True)
            with open(os.path.join(pdir, "trajectories.jsonl"), "w", encoding="utf-8") as f:
                for r in recs:
                    f.write(json.dumps(r, ensure_ascii=False) + "\n")
            with open(os.path.join(pdir, "tests.jsonl"), "w", encoding="utf-8") as f:
                for inp, outp in pairs:
                    f.write(json.dumps({"input": self._read(inp), "output": self._read(outp)},
                                       ensure_ascii=False) + "\n")
            with open(os.path.join(pdir, "problem.html"), "w", encoding="utf-8") as f:
                f.write(self.problem_html(pid))
            if pid in limits:
                with open(os.path.join(pdir, "meta.json"), "w", encoding="utf-8") as f:
                    json.dump(limits[pid], f)
            built.append({"n_traj": len(recs),
                          "n_subs": sum(len(r["submissions"]) for r in recs)})
        self._write_readme(built)
        n_traj = sum(b["n_traj"] for b in built)
        n_subs = sum(b["n_subs"] for b in built)
        print(f"{len(built)} problems, {n_traj} trajectories, {n_subs} submissions SAVED.")

    def _write_readme(self, built):
        n_traj = sum(b["n_traj"] for b in built)
        n_subs = sum(b["n_subs"] for b in built)
        sizes = sorted(b["n_traj"] for b in built) or [0]
        L = [
            "# Dataset",
            "",
            "Sources:",
            "- Submissions & problems: https://github.com/IBM/Project_CodeNet",
            "- Test cases (AtCoder_testcases.zip): https://github.com/mahimanzum/FixEval#download-test-cases",
            "",
            "## Selection criteria",
            "- Language: Python",
            "- Benchmark: Project_CodeNet_Python800",
            "- Verdicts: AC (Accepted) / WA (Wrong Answer);",
            "- Trajectory: {AC, WA} submissions up to the first AC, with >=2 WA before it "
            "(length >=3); last = AC (oracle), last WA = buggy",
            "- Parsability: every submission in a trajectory must parse with ast.parse "
            "(Python 3); trajectories with any unparsable submission are dropped",
            "- Benchmark AC: the trajectory's final AC (oracle) must be one of the Python800 "
            "sampled submissions for that problem (caps trajectories per problem at the sample size)",
            "- Non-trivial revision: trajectories whose WA submissions are ALL byte-identical "
            "(no real revision before the AC) are dropped",
            f"- Problems kept: >= {self.MIN_TRAJ} trajectories",
            "",
            "## Layout",
            "```",
            "data/<problem_id>/",
            "  trajectories.jsonl   {problem_id, user_id, submissions:[{sid, ts, verdict, code}]}",
            "  tests.jsonl          {input, output}",
            "  problem.html         original problem statement",
            "```",
            "",
            "## Statistics",
            "| metric | value |",
            "|---|---|",
            f"| problems | {len(built)} |",
            f"| trajectories | {n_traj} |",
            f"| submissions | {n_subs} |",
            f"| trajectories per problem (min/median/max) | "
            f"{sizes[0]} / {sizes[len(sizes)//2]} / {sizes[-1]} |",
            "",
        ]
        os.makedirs(self.OUT_ROOT, exist_ok=True)
        with open(os.path.join(self.OUT_ROOT, "README.md"), "w", encoding="utf-8") as f:
            f.write("\n".join(L))


if __name__ == "__main__":
    DatasetBuilder().build()
