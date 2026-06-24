from dataclasses import dataclass
from typing import Optional


@dataclass
class CaseResult:
    passed: bool = False
    empty: bool = False
    injected: bool = False
    skip: Optional[str] = None
    fail_reason: Optional[str] = None  # wrong_output | timeout | runtime_error | no_tests
    ted: Optional[int] = None
    intent: Optional[float] = None
    seconds: float = 0.0
