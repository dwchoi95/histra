from .testcase import TestCase


class TestCases:
    def __init__(self, testcases:list):
        self.testcases = [TestCase(**tc) if not isinstance(tc, TestCase) else tc for tc in sorted(testcases, key=lambda x: x['id'] if isinstance(x, dict) else x.id)]
        self.current_index = 0
        
    def __iter__(self):
        self.current_index = 0
        return self

    def __next__(self):
        if self.current_index < len(self.testcases):
            tc = self.testcases[self.current_index]
            self.current_index += 1
            return tc
        raise StopIteration
    
    def __len__(self):
        return len(self.testcases)
    
    def __getitem__(self, idx):
        if isinstance(idx, slice):
            return TestCases(self.testcases[idx])
        return self.testcases[idx]
    
    def get_tc_id_list(self) -> list:
        return [tc.id for tc in self.testcases]
    
    def get_tc_by_id(self, id:int) -> TestCase:
        for tc in self.testcases:
            if tc.id == id:
                return tc
        raise IndexError
