from dataclasses import dataclass

from .testcase import TestCase
from .result import Result


@dataclass
class TestcaseResult:
    testcase: TestCase
    result: Result = None
