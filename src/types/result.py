from dataclasses import dataclass, field


@dataclass
class Result:
    status:str = field(metadata={"desc":"Status of the execution (e.g., passed, failed, timeout, error)"})
    stdout:str = field(metadata={"desc":"Standard output from the execution"})
    stderr:str = field(metadata={"desc":"Standard error from the execution"})
