import ast
from dataclasses import dataclass
from typing import Optional


@dataclass
class Hole:
    id: int
    std_stmt: str
    origin: Optional[ast.AST] = None
    kind: str = "replace"             # replace | delete | insert
    ref_hint: Optional[str] = None     # aligned code hint from reference
