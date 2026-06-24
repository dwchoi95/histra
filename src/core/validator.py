import os, re, subprocess, sys, tempfile
from functools import cache
from src.types import TestCases, TestCase, Results, Result, TestcaseResult, Status

class Validator:

    @classmethod
    def init_globals(cls, tests, timeout: int):
        # accept either a raw list of dicts or a TestCases instance
        cls.tests = tests if isinstance(tests, TestCases) else TestCases(tests)
        cls.timeout = timeout

    @classmethod
    def _norm(cls, text:str) -> str:
        _WS = re.compile(r"\s+")
        return _WS.sub(" ", text or "").strip()
    
    @classmethod
    def run_case(cls, path:str, testcase: TestCase) -> Result:
        try:
            proc = subprocess.run(
                [sys.executable, path], input=testcase.input, capture_output=True,
                text=True, timeout=cls.timeout,
                env={**os.environ, "PYTHONIOENCODING": "utf-8"})
            out = cls._norm(proc.stdout)
            if proc.returncode != 0:
                return Result(status=Status.ERROR, stdout=out, stderr=proc.stderr)
            if out != cls._norm(testcase.output):
                return Result(status=Status.FAILED, stdout=out, stderr="Output mismatch")
            return Result(status=Status.PASSED, stdout=out, stderr=proc.stderr)
        except subprocess.TimeoutExpired:
            return Result(status=Status.ERROR, stdout="", stderr="Timeout expired")

    @classmethod
    @cache
    def run(cls, code:str) -> Results:
        with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as fh:
            fh.write(code)
            path = fh.name
        rs = Results([])
        try:
            for t in cls.tests:
                rs.update(t, cls.run_case(path, t))
        finally:
            try:
                os.unlink(path)
            except OSError:
                pass
        return rs
