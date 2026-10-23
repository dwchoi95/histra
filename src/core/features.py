import ast, math
from collections import Counter


class Featurizer:
    """Skip-gram code features for AC retrieval; identifier-free (operators, builtins, methods, constant kinds)."""

    _OPS = (ast.operator, ast.unaryop, ast.boolop, ast.cmpop)
    _BUILTINS = {"range", "len", "int", "str", "map", "list", "sum", "max", "min", "abs",
                 "sorted", "print", "input", "set", "dict", "enumerate", "zip", "float",
                 "round", "pow", "ord", "chr"}

    @classmethod
    def features(cls, code):
        try:
            tree = ast.parse(code)
        except Exception:
            return Counter()
        g = Counter()
        es = cls._enriched_stream(tree)
        L = len(es)
        for i in range(L - 1):
            g["E2:" + es[i] + "/" + es[i + 1]] += 1
        for i in range(L - 2):
            g["E3:" + es[i] + "/" + es[i + 1] + "/" + es[i + 2]] += 1
        for i in range(L - 2):                       # 1-skip bigrams survive a single insertion
            g["Es1b:" + es[i] + "/" + es[i + 2]] += 1
        for tk in es:
            g["EU:" + tk] += 2
        fseq = cls._type_stream(tree)
        for i in range(len(fseq) - 3):
            g["F4:" + "/".join(fseq[i:i + 4])] += 1
        g.update(cls._val_tokens(tree))
        return g

    @classmethod
    def idf(cls, pool):
        P = len(pool)
        df = Counter()
        for f in pool:
            for k in f:
                df[k] += 1
        return {k: math.log((P + 1) / (c + 1)) + 1 for k, c in df.items()}

    @staticmethod
    def wjaccard(a, b, idf):
        num = den = 0.0
        for k in set(a) | set(b):
            w = idf.get(k, 1.0)
            av = a.get(k, 0); bv = b.get(k, 0)
            num += w * (av if av < bv else bv)
            den += w * (av if av > bv else bv)
        return num / den if den else 0.0

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
        """Statement type + its operators/builtin calls/methods/constant kinds (not of nested statements)."""
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
