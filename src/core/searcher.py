from .features import Featurizer


class Searcher:
    """Rank other students' ACs by IDF-weighted skip-gram weighted Jaccard similarity to the student's program."""

    def __init__(self, refs: list[str]):
        self.refs = refs
        self.feats = [Featurizer.features(r) for r in refs]
        self.idf = Featurizer.idf(self.feats)

    def run(self, code: str, k: int = 20) -> list[str]:
        f = Featurizer.features(code)
        order = sorted(range(len(self.refs)), key=lambda i: -Featurizer.wjaccard(f, self.feats[i], self.idf))
        return [self.refs[i] for i in order[:k]]
