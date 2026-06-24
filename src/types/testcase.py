from dataclasses import dataclass


@dataclass(eq=True, frozen=False)
class TestCase:
    id: int
    input: str
    output: str

    def __hash__(self):
        return hash((self.id, self.input, self.output))
