from typing import List

from .testcase_result import TestcaseResult
from .status import Status
from .testcase import TestCase


class Results:
    def __init__(self, ts:List[TestcaseResult]=None):
        self.ts = list(ts) if ts is not None else []
        self.current_index = 0
        
    def __iter__(self):
        self.current_index = 0
        return self

    def __next__(self):
        if self.current_index < len(self.ts):
            tr = self.ts[self.current_index]
            self.current_index += 1
            return tr
        raise StopIteration
    
    def __len__(self):
        return len(self.ts)
    
    def __getitem__(self, idx):
        if isinstance(idx, slice):
            return Results(self.ts[idx])
        return self.ts[idx]

    def update(self, testcase:TestCase, result):
        for tr in self.ts:
            if tr.testcase.id == testcase.id:
                tr.result = result
                return
        self.ts.append(TestcaseResult(testcase=testcase, result=result))
    
    def delete(self, testcase:TestCase):
        self.ts = [tr for tr in self.ts if tr.testcase.id != testcase.id]
    
    def passed(self) -> bool:
        for tr in self.ts:
            if tr.result is None or tr.result.status != Status.PASSED:
                return False
        return True
