import ast, math
from collections import Counter


class Featurizer:
    """Skip-gram code features for AC retrieval. Insertion/deletion-robust skip-grams over an
    enriched statement stream (statement type + a local signature of operators / builtin calls /
    method names / constant kinds), a type-4-gram backbone, and canonical value/operator tokens.
    Identity-safe: only operators, builtins, method names, constant kinds, and canonical
    (alpha-renamed v0,v1,...) variable structure -- never an original identifier spelling."""

    _OPS = (ast.operator, ast.unaryop, ast.boolop, ast.cmpop)
    _BUILTINS = {"range", "len", "int", "str", "map", "list", "sum", "max", "min", "abs",
                 "sorted", "print", "input", "set", "dict", "enumerate", "zip", "float",
                 "round", "pow", "ord", "chr"}

    @classmethod
    def features(cls, code):
        """Parse a source string and return its skip-gram feature Counter (empty if unparsable)."""
        try:
            tree = ast.parse(code)
        except Exception:
            return Counter()
        g = Counter()
        es = cls._enriched_stream(tree)
        L = len(es)
        for i in range(L - 1):                       # contiguous statement bigrams
            g["E2:" + es[i] + "/" + es[i + 1]] += 1
        for i in range(L - 2):                       # contiguous statement trigrams
            g["E3:" + es[i] + "/" + es[i + 1] + "/" + es[i + 2]] += 1
        for i in range(L - 2):                       # 1-skip bigrams: survive a single insertion
            g["Es1b:" + es[i] + "/" + es[i + 2]] += 1
        for tk in es:                                # enriched unigrams (strongest single signal)
            g["EU:" + tk] += 2
        fseq = cls._type_stream(tree)                # type 4-gram structural backbone
        for i in range(len(fseq) - 3):
            g["F4:" + "/".join(fseq[i:i + 4])] += 1
        g.update(cls._val_tokens(tree))
        return g

    @classmethod
    def idf(cls, pool):
        """IDF weights over a pool of feature Counters (smoothed)."""
        P = len(pool)
        df = Counter()
        for f in pool:
            for k in f:
                df[k] += 1
        return {k: math.log((P + 1) / (c + 1)) + 1 for k, c in df.items()}

    @staticmethod
    def wjaccard(a, b, idf):
        """IDF-weighted weighted-Jaccard: sum_k w_k*min / sum_k w_k*max."""
        num = den = 0.0
        for k in set(a) | set(b):
            w = idf.get(k, 1.0)
            av = a.get(k, 0); bv = b.get(k, 0)
            num += w * (av if av < bv else bv)
            den += w * (av if av > bv else bv)
        return num / den if den else 0.0

    # ---- internals ----
    @staticmethod
    def _kids(n):
        return [c for c in ast.iter_child_nodes(n) if not isinstance(c, ast.expr_context)]

    @classmethod
    def _type_stream(cls, t):
        seq = []
        def r(n):
            seq.append(type(n).__name__)
            for c in cls._kids(n):
                r(c)
        r(t)
        return seq

    @classmethod
    def _enriched_stream(cls, t):
        seq = []
        def r(n):
            if isinstance(n, ast.stmt):
                seq.append(cls._local_sig(n))
            for c in cls._kids(n):
                r(c)
        r(t)
        return seq

    @classmethod
    def _local_sig(cls, stmt):
        """Statement-local intent signature (operators / builtin calls / method names / constant
        kinds / subscripting), without descending into nested statements. No identifiers."""
        toks = set()
        def walk(n, top):
            if isinstance(n, ast.stmt) and not top:
                return
            if isinstance(n, cls._OPS):
                toks.add(type(n).__name__)
            elif isinstance(n, ast.Compare):
                for op in n.ops:
                    toks.add(type(op).__name__)
            elif isinstance(n, ast.Call):
                f = n.func
                if isinstance(f, ast.Name):
                    toks.add("call:" + f.id if f.id in cls._BUILTINS else "call")
                elif isinstance(f, ast.Attribute):
                    toks.add("meth:" + f.attr)
                else:
                    toks.add("call")
            elif isinstance(n, ast.Constant):
                v = n.value
                if isinstance(v, bool): toks.add("kB")
                elif isinstance(v, int): toks.add("k" + (str(v) if -2 <= v <= 2 else "I"))
                elif isinstance(v, float): toks.add("kF")
                elif isinstance(v, str): toks.add("kS")
            elif isinstance(n, ast.Subscript):
                toks.add("sub")
            for c in cls._kids(n):
                walk(c, False)
        walk(stmt, True)
        sig = ",".join(sorted(toks))
        return type(stmt).__name__ + ("|" + sig if sig else "")

    @classmethod
    def _val_tokens(cls, tree):
        """Canonical value / operator tokens over the whole tree (no identifiers)."""
        out = Counter()
        for n in ast.walk(tree):
            if isinstance(n, cls._OPS):
                out["OP:" + type(n).__name__] += 1
            elif isinstance(n, ast.Constant):
                v = n.value
                if isinstance(v, bool): out["C:bool=" + str(v)] += 1
                elif isinstance(v, int): out["C:int=" + (str(v) if -2 <= v <= 2 else "big")] += 1
                elif isinstance(v, float): out["C:float"] += 1
                elif isinstance(v, str): out["C:str" + ("=empty" if v == "" else "")] += 1
                else: out["C:" + type(v).__name__] += 1
            elif isinstance(n, ast.Compare):
                for op in n.ops:
                    out["CMP:" + type(op).__name__] += 1
        return out
