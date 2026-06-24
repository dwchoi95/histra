from dataclasses import dataclass, field
from typing import Optional, List, Tuple, Any

from .hole import Hole


@dataclass
class SketchResult:
    std: list                    # standardized WA sequence (strings)
    std_sn: str                  # standardized buggy (canonical)
    sketched: str                # canonical sketch (holes in canonical space)
    holes: list                  # list[Hole]
    frozen_sigs: set             # canonical subtree signatures kept frozen
    sketched_original: Optional[str] = None  # original-surface sketch (filled by Reformatter)
    filled_original: Optional[str] = None    # deterministic fill
    insert_entries: List[Tuple[Any, str, int]] = field(default_factory=list)  # (origin_parent, field, idx)

    @property
    def n_holes(self) -> int:
        return len(self.holes)
