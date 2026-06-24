from dataclasses import dataclass


@dataclass
class Config:
    """Pipeline configuration; the default is the full method. Ablations flip one
    field (see run.py --ablation presets)."""
    standardize: bool = True          # D1: canonicalize WAs/buggy (off -> raw AST)
    reformat: bool = True             # D1: project holes onto WAn's original surface
    ref: str = "cosine"               # D2: cosine | random | oracle | none
    sketch: str = "was+ac"            # D3: was+ac | wan+ac | was
    repair: str = "sketch"            # D4: sketch | plain
