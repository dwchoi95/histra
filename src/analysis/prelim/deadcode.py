"""Paper §4 (RQ2): residual student code in passing patches. Lower-bound proxy: a module-level statement is dead if it
has no observable effect (no print/input/exit/unknown call) and none of the names it stores or mutates is read by a later
module-level statement or by any function body. Reports, per repairer, the share of passing patches in which a statement
of P_n that was live in P_n became dead, and HISTRA's skeleton loss with those trajectories excluded.
Usage: python deadcode.py results/eval NAME ..."""
import ast, json, sys
SAFE = {"abs", "int", "str", "float", "len", "range", "map", "list", "sorted", "sum", "max", "min", "set", "dict",
        "tuple", "enumerate", "zip", "round", "pow", "divmod", "bool", "ord", "chr", "reversed", "any", "all", "bin",
        "hex", "oct", "filter", "frozenset", "isinstance", "type"}
MUT = {"append", "extend", "add", "insert", "pop", "sort", "remove", "update", "reverse", "clear", "discard",
       "setdefault", "appendleft", "popleft", "count", "index", "split", "join", "strip", "replace", "get", "keys",
       "values", "items", "copy", "lower", "upper", "rstrip", "lstrip", "find", "startswith", "endswith"}

def stores(s):
    out = set()
    for n in ast.walk(s):
        if isinstance(n, ast.Name) and isinstance(n.ctx, (ast.Store, ast.Del)):
            out.add(n.id)
        elif isinstance(n, (ast.Subscript, ast.Attribute)) and isinstance(n.ctx, ast.Store):
            b = n.value
            while isinstance(b, (ast.Subscript, ast.Attribute)):
                b = b.value
            if isinstance(b, ast.Name): out.add(b.id)
        elif isinstance(n, ast.Call):
            f = n.func
            if isinstance(f, ast.Name) and f.id in SAFE: continue
            if isinstance(f, ast.Attribute) and f.attr in MUT and isinstance(f.value, ast.Name):
                out.add(f.value.id); continue
            if isinstance(f, ast.Attribute) and f.attr in MUT: continue
            return None                      # unknown or effectful call
        elif isinstance(n, (ast.Raise, ast.Assert, ast.Import, ast.ImportFrom, ast.Global, ast.Nonlocal,
                            ast.FunctionDef, ast.ClassDef, ast.Return, ast.Break, ast.Continue, ast.Try, ast.With)):
            return None
    return out

def dead(src):
    tree = ast.parse(src)
    body = tree.body
    loads = [{n.id for n in ast.walk(s) if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load)} for s in body]
    infn = {n.id for f in ast.walk(tree) if isinstance(f, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda, ast.ClassDef))
            for n in ast.walk(f) if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load)}
    res = []
    for i, s in enumerate(body):
        st = stores(s)
        if st and not st & (infn | set().union(*loads[i + 1:])):
            res.append(ast.unparse(s))
    return res

def newly_dead(r):
    """True if the patch leaves a statement of P_n dead that was live in P_n."""
    db = dead(r["was"][-1])
    bstm = {ast.unparse(s) for s in ast.walk(ast.parse(r["was"][-1])) if isinstance(s, ast.stmt)}
    return any(d in bstm and d not in db for d in dead(r["patch"]))


def check():
    assert dead("x = 1\ny = 2\nprint(y)") == ["x = 1"]
    assert dead("def f():\n    return x\nx = 5\nprint(f())") == []
    assert dead("a = []\na.append(input())\nprint(1)") == []          # input() is an effect
    assert dead("s = []\ns.append(1)\nprint(2)") == ["s.append(1)"]     # conservative: s is read by s.append


if __name__ == "__main__":
    check()
    D = sys.argv[1]
    for name in sys.argv[2:]:
        rows = [json.loads(l) for l in open(f"{D}/{name}.jsonl")]
        n = k = kb = kac = resid = 0
        for r in rows:
            if not r.get("patch"): continue
            try:
                dp, db, da, nd = dead(r["patch"]), dead(r["was"][-1]), dead(r["oracle"]), newly_dead(r)
            except Exception:
                continue
            n += 1; k += bool(dp); kb += bool(db); kac += bool(da); resid += nd
        print(f"{name:18s} n={n:5d} | patch with dead stmt {100*k/n:5.1f}% | b {100*kb/n:5.1f}% | P_ac {100*kac/n:5.1f}% | newly dead student stmt {100*resid/n:5.1f}%")
    # does residual code drive HISTRA's skeleton advantage over HISTRA with H = {}?
    rows = {n: {(r["pid"], r["user"]): r for r in map(json.loads, open(f"{D}/{n}.jsonl"))} for n in ("histra_min",)}
    ret = {n: {(r["pid"], r["user"]): r for r in map(json.loads, open(f"{D}/{n}.ret.jsonl")) if r} for n in ("histra_min", "histra_nohist")}
    flag = set()
    for k, r in rows["histra_min"].items():
        try:
            if r.get("patch") and newly_dead(r): flag.add(k)
        except Exception:
            pass
    H, N = ret["histra_min"], ret["histra_nohist"]
    both = [k for k in H if k in N and H[k]["ret_patch"] is not None and N[k]["ret_patch"] is not None]
    for lab, ks in (("all", both), ("excluding residual", [k for k in both if k not in flag])):
        print(f"skeleton loss on {lab:18s} n={len(ks):5d} | HISTRA {100 * sum(1 - H[k]['ret_patch'] for k in ks) / len(ks):5.1f}%"
              f" vs H = {{}} {100 * sum(1 - N[k]['ret_patch'] for k in ks) / len(ks):5.1f}%")
