from dataclasses import dataclass, field
from typing import List

from .results import Results


@dataclass
class Trajectory:
    id:str = field(metadata={"desc":"User ID"})
    was:List[str] = field(metadata={"desc":"List of wrong attempts (WA) codes"})
    ac:str = field(metadata={"desc":"Accepted code (AC)"})
    results:Results = field(default=None, metadata={"desc":"Run Results after execution"})
