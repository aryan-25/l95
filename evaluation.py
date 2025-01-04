from nltk import Tree  # type: ignore
from PYEVALB import parser, scorer  # type: ignore


class ParseEvalbResult:
    def __init__(self, recall: float, precision: float):
        self.recall = recall
        self.precision = precision
        self.fscore = (2 * (recall * precision)) / (recall + precision)

    def __str__(self):
        return f"({self.recall:.2f}, {self.precision:.2f}, {self.fscore:.2f})"

    def __repr__(self):
        return self.__str__()


def pyevalb_score(*trees: Tree) -> list[list[ParseEvalbResult]]:
    pyeval_trees = [parser.create_from_bracket_string(str(tree)) for tree in trees]

    matrix: list[list[ParseEvalbResult]] = []

    for i in range(len(pyeval_trees)):
        row: list[ParseEvalbResult] = []
        for j in range(len(pyeval_trees)):
            if i == j:
                row.append(ParseEvalbResult(1, 1))
                continue
            score = scorer.Scorer().score_trees(pyeval_trees[i], pyeval_trees[j])
            row.append(ParseEvalbResult(score.recall, score.prec))
        matrix.append(row)

    return matrix
