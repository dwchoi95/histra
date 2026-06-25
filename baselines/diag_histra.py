import sys, ast, difflib, statistics
sys.path.insert(0, '.')
import warnings; warnings.filterwarnings('ignore')
from src.utils import DataLoader
from src.core.standardizer import Standardizer
from src.core.sketch import Sketcher
from src.core.reformat import Reformatter
from src.core.searcher import Searcher
from src.core.repair import Repair
from src.core.validator import Validator


def count_holes(node):
    return sum(1 for n in ast.walk(node) if isinstance(n, ast.Name) and n.id == '__HOLE__')

def hole_lines(node):
    out = set()
    for n in ast.walk(node):
        if isinstance(n, ast.Name) and n.id == '__HOLE__':
            ln = getattr(n, 'lineno', None)
            if ln:
                out.add(ln)
    return out

def diff_lines(buggy, oracle):
    b = buggy.splitlines(); o = oracle.splitlines()
    sm = difflib.SequenceMatcher(a=b, b=o)
    changed = set()
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag != 'equal':
            for i in range(i1, i2):
                changed.add(i + 1)
            if i1 == i2:
                changed.add(i1)
    return changed


for pid in sys.argv[1:]:
    _, timeout, tests, trajs, refs = DataLoader.run('data/' + pid)[0]
    Validator.init_globals(tests, timeout)
    uids = sorted(trajs)[:50]
    cat = {'no_holes': 0, 'fill_fail': 0, 'validate_fail': 0, 'pass': 0, 'error': 0}
    bug_frozen = 0; bug_frozen_den = 0; nholes = []
    for u in uids:
        was = trajs.get(u) or []
        if not was:
            continue
        buggy = was[-1]; oracle = refs.get(u)
        try:
            std = Standardizer.run(was); anchor = std[-1]
            skt = Sketcher.run(std)
            h = count_holes(skt); nholes.append(h)
            skt_org = Reformatter.run(anchor, skt)
            if oracle:
                hl = hole_lines(skt_org); dl = diff_lines(buggy, oracle)
                if hl:
                    bug_frozen_den += 1
                    if dl and not (hl & dl):
                        bug_frozen += 1
            if h == 0:
                cat['no_holes'] += 1; continue
            refpool = [v for k, v in refs.items() if k != u]
            nm = Searcher(refpool, anchor).run(skt_org)
            patch = Repair(nm).run(skt_org)
            if patch is None:
                cat['fill_fail'] += 1; continue
            if Validator.run(patch).passed():
                cat['pass'] += 1
            else:
                cat['validate_fail'] += 1
        except Exception:
            cat['error'] += 1
    n = len(uids)
    print(f"\n=== {pid} (n={n}) ===")
    print(f"  no_holes(sketch produced 0 holes): {cat['no_holes']}")
    print(f"  fill_fail(hole unfilled -> None) : {cat['fill_fail']}")
    print(f"  validate_fail(patch fails tests) : {cat['validate_fail']}")
    print(f"  pass                             : {cat['pass']}")
    print(f"  error                            : {cat['error']}")
    print(f"  mean holes={statistics.mean(nholes):.1f}, zero-hole frac={nholes.count(0)/len(nholes):.0%}")
    print(f"  bug-frozen(holes miss true fix region): {bug_frozen}/{bug_frozen_den}")
