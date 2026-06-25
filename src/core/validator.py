import os, re, subprocess, sys, multiprocessing
from functools import cache
from src.types import TestCases, TestCase, Results, Result, TestcaseResult, Status

class Validator:

    @classmethod
    def init_globals(cls, tests, timeout: int):
        # accept either a raw list of dicts or a TestCases instance
        cls.tests = tests if isinstance(tests, TestCases) else TestCases(tests)
        cls.timeout = timeout
        cls.run.cache_clear()

    @classmethod
    def _norm(cls, text:str) -> str:
        _WS = re.compile(r"\s+")
        return _WS.sub(" ", text or "").strip()
    
    @classmethod
    def run_case(cls, code: str, testcase: TestCase) -> Result:
        try:
            proc = subprocess.run(
                [sys.executable, "-c", code], input=testcase.input, capture_output=True,
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
    def _validation(cls, args: tuple[str, TestCase]) -> TestcaseResult:
        code, testcase = args
        return TestcaseResult(testcase=testcase, result=cls.run_case(code, testcase))

    @classmethod
    @cache
    def run(cls, code:str) -> Results:
        args = [(code, testcase) for testcase in cls.tests]
        processes = min(len(args), multiprocessing.cpu_count())
        ctx = multiprocessing.get_context("fork")
        with ctx.Pool(processes=processes) as pool:
            results = pool.map(cls._validation, args)
        return Results(results)
