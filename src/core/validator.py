"""Test validation: each test's input is the program's stdin, and the whitespace-normalized stdout must equal the
expected output within the time limit."""
import subprocess
import sys


def passes(src, tests, timeout):
    for t in tests:
        try:
            p = subprocess.run([sys.executable, "-c", src], input=t["input"], capture_output=True, text=True,
                               timeout=timeout)
        except subprocess.TimeoutExpired:
            return False
        if p.returncode != 0 or p.stdout.split() != t["output"].split():
            return False
    return True
