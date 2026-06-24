import ast


class Standardizer(ast.NodeTransformer):
    _FLIP = {ast.Gt: ast.Lt, ast.GtE: ast.LtE}
    
    def __init__(self):
        self._tmp = 0
        
    @staticmethod
    def _carry(new: ast.AST, origin: ast.AST) -> ast.AST:
        """Provenance: tag created node (+ descendants) with its origin node."""
        for n in ast.walk(new):
            if not hasattr(n, "_origin"):
                n._origin = origin
        return new

    @staticmethod
    def _org(node: ast.AST) -> ast.AST:
        return getattr(node, "_origin", node)

    # ---- Empty container normalization: list()/tuple()/dict() -> []/()/{} ----
    def visit_Call(self, node: ast.Call):
        self.generic_visit(node)
        if isinstance(node.func, ast.Name):
            fn = node.func.id
            # Canonicalize any range(...) to range(start, stop, step) with no keywords
            if fn == "range":
                pos = list(node.args)
                kw = {k.arg: k.value for k in node.keywords or [] if k.arg in ("start", "stop", "step")}
                start = stop = step = None
                if len(pos) == 1:
                    start, stop, step = ast.Constant(value=0), pos[0], ast.Constant(value=1)
                elif len(pos) == 2:
                    start, stop, step = pos[0], pos[1], ast.Constant(value=1)
                elif len(pos) >= 3:
                    start, stop, step = pos[0], pos[1], pos[2]
                elif len(pos) == 0 and ("stop" in kw or "start" in kw):
                    start = kw.get("start", ast.Constant(value=0))
                    stop = kw.get("stop", None)
                    step = kw.get("step", ast.Constant(value=1))
                # apply keyword overrides when present
                if "start" in kw:
                    start = kw["start"]
                if "stop" in kw:
                    stop = kw["stop"]
                if "step" in kw:
                    step = kw["step"]
                if start is not None and stop is not None and step is not None:
                    new_call = ast.Call(func=ast.Name(id="range", ctx=ast.Load()), args=[start, stop, step], keywords=[])
                    return self._carry(new_call, self._org(node))
            # empty container constructors -> literals
            if not node.args and not node.keywords:
                if fn == "list":
                    return self._carry(ast.List(elts=[], ctx=ast.Load()), self._org(node))
                if fn == "tuple":
                    return self._carry(ast.Tuple(elts=[], ctx=ast.Load()), self._org(node))
                if fn == "dict":
                    return self._carry(ast.Dict(keys=[], values=[]), self._org(node))
        return node

    # --- Comparison normalization: flip descending comparisons to ascending ---
    def visit_Compare(self, node: ast.Compare):
        self.generic_visit(node)
        nops = len(node.ops)
        if nops == 1 and type(node.ops[0]) in self._FLIP:
            node.ops[0] = self._FLIP[type(node.ops[0])]()
            node.left, node.comparators[0] = node.comparators[0], node.left
            return node

        if nops >= 2:
            # check if all ops are descending (Gt/GtE)
            desc_types = (ast.Gt, ast.GtE)
            if all(isinstance(op, desc_types) for op in node.ops):
                # ensure all operands are side-effect free simple nodes
                operands = [node.left] + list(node.comparators)
                if all(isinstance(x, (ast.Name, ast.Constant)) for x in operands):
                    # reverse operands and flip ops to ascending (Lt/LtE)
                    rev_ops = [self._FLIP[type(op)]() for op in reversed(node.ops)]
                    rev_operands = list(reversed(operands))
                    node.left = rev_operands[0]
                    node.comparators = rev_operands[1:]
                    node.ops = rev_ops
        return node

    # ---- AugAssign expansion: x += y  ->  x = x + y ----
    def visit_AugAssign(self, node: ast.AugAssign):
        self.generic_visit(node)
        if isinstance(node.target, ast.Name):
            tgt = node.target.id
            new = ast.Assign(
                targets=[ast.Name(id=tgt, ctx=ast.Store())],
                value=ast.BinOp(left=ast.Name(id=tgt, ctx=ast.Load()), op=node.op, right=node.value),
            )
            return self._carry(new, self._org(node))
        return node

    # ---- While normalization: while cond: body -> while True: if not cond: break; body ----
    def visit_While(self, node: ast.While):
        self.generic_visit(node)
        # keep while-else as is
        if node.orelse:
            return node
        # while True stays
        if isinstance(node.test, ast.Constant) and node.test.value is True:
            return node
        guard = ast.If(test=ast.UnaryOp(op=ast.Not(), operand=node.test), body=[ast.Break()], orelse=[])
        new = ast.While(test=ast.Constant(value=True), body=[guard] + node.body, orelse=[])
        return self._carry(new, self._org(node))

    # ---- For normalization: for t in it -> itN=iter(it); while True: try: t=next(itN); except StopIteration: break; body ----
    def visit_For(self, node: ast.For):
        self.generic_visit(node)
        # keep for-else as is
        if node.orelse:
            return node
        self._tmp += 1
        itn = ast.Name(id=f"_it{self._tmp}", ctx=ast.Store())
        assign_it = ast.Assign(
            targets=[itn],
            value=ast.Call(func=ast.Name(id="iter", ctx=ast.Load()), args=[node.iter], keywords=[]),
        )
        try_next = ast.Try(
            body=[ast.Assign(
                targets=[node.target],
                value=ast.Call(func=ast.Name(id="next", ctx=ast.Load()), args=[ast.Name(id=itn.id, ctx=ast.Load())], keywords=[]),
            )],
            handlers=[ast.ExceptHandler(type=ast.Name(id="StopIteration", ctx=ast.Load()), name=None, body=[ast.Break()])],
            orelse=[],
            finalbody=[],
        )
        wh = ast.While(test=ast.Constant(value=True), body=[try_next] + node.body, orelse=[])
        org = self._org(node)
        return [self._carry(assign_it, org), self._carry(wh, org)]
    
    @classmethod
    def standardize(cls, code: str) -> tuple[ast.AST, ast.AST]:
        org = ast.parse(code)
        std = ast.parse(code)
        for o, w in zip(ast.walk(org), ast.walk(std)):
            w._origin = o
        std = cls().visit(std)
        return std, org

    @classmethod
    def run(cls, traj: list[str]) -> list[tuple[ast.AST, ast.AST]]:
        out = []
        for code in traj:
            std, org = cls.standardize(code)
            out.append((std, org))
        return out
