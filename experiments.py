import abc
import os

import spacy
import stanza  # type: ignore
from nltk import Tree  # type: ignore
from nltk.draw.tree import TreeView, TreeWidget  # type: ignore
from nltk.draw.util import CanvasFrame  # type: ignore
from nltk.parse.corenlp import CoreNLPParser  # type: ignore
from nltk.tokenize.treebank import TreebankWordTokenizer  # type: ignore
from PYEVALB import parser, scorer  # type: ignore

import parse
from parse import Sentence


class Parser(abc.ABC):
    @abc.abstractmethod
    def parse(self, text: str) -> Tree:
        pass

    def parse_multiple(self, sentences: list[Sentence]) -> list[Tree]:
        return [self.parse(sentence.text) for sentence in sentences]


class CoreNLPConstituencyParser(Parser):
    def __init__(self):
        os.environ["CLASSPATH"] = r"/opt/homebrew/Cellar/stanford-parser/4.2.0/libexec/"
        self.parser = CoreNLPParser(url="http://localhost:9000")

    def parse(self, text: str) -> Tree:
        return self.post_process(next(self.parser.raw_parse(text)))

    def post_process(self, tree: Tree) -> Tree:
        # Remove the root node since the gold standard trees do not have it
        return tree[0]


class StanzaConstituencyParser(Parser):
    def __init__(self):
        self.nlp = stanza.Pipeline(lang="en", processors="tokenize,pos,constituency,lemma,depparse")

    def parse(self, text: str) -> Tree:
        return self.post_process(Tree.fromstring(str(self.nlp(text).sentences[0].constituency)))

    def post_process(self, tree: Tree) -> Tree:
        # Remove the root node since the gold standard trees do not have it
        return tree[0]


class BerkeleyConstituencyParser(Parser):
    def __init__(self):
        # Berkeley parser is a Java program that accepts input from stdin and writes output to stdout
        # Whenever we need to use it, we will write the input to a file, run the parser with piped input/output, and read the output from a file
        # No initialisation is needed here
        pass

    def ptb_tokenise(self, text):
        """
        Tokenise the input text using the Penn Treebank tokeniser.
        The Berkeley parser expects input in this format:
        - In the README of `berkeleyparser`:
        - "By default, it will read in *PTB tokenized sentences* from STDIN (one per line) and write parse trees to STDOUT."
        """
        tokenizer = TreebankWordTokenizer()
        return " ".join(tokenizer.tokenize(text))

    def parse(self, text):
        with open("input.txt", "w") as f:
            f.write(self.ptb_tokenise(text))

        os.system(
            "java -jar berkeleyparser/BerkeleyParser-1.7.jar -gr berkeleyparser/eng_sm6.gr < input.txt > output.txt"
        )

        with open("output.txt", "r") as f:
            return self.post_process(Tree.fromstring(f.readline()))

    def parse_multiple(self, sentences):
        with open("input.txt", "w") as f:
            for sentence in sentences:
                f.write(self.ptb_tokenise(sentence.text) + "\n")

        os.system(
            "java -jar berkeleyparser/BerkeleyParser-1.7.jar -gr berkeleyparser/eng_sm6.gr < input.txt > output.txt"
        )

        with open("output.txt", "r") as f:
            return [self.post_process(Tree.fromstring(line)) for line in f.readlines()]

    def post_process(self, tree: Tree) -> Tree:
        # Remove the root node since the gold standard trees do not have it
        return tree[0]


class BerkeleyNeuralConstituencyParser(Parser):
    def __init__(self):
        # import benepar only if we use it --- takes several seconds to load
        import benepar  # type: ignore

        self.parser = benepar.Parser("benepar_en3_large")

    def parse(self, text: str) -> Tree:
        return self.post_process(self.parser.parse(text))

    def post_process(self, tree: Tree) -> Tree:
        # Remove the root node since the gold standard trees do not have it
        return tree[0]


class SpacyDependencyParser:
    def __init__(self):
        self.nlp: spacy.Language = spacy.load("en_core_web_sm")

    def parse(self, text: str) -> None:
        doc = self.nlp(text)
        for token in doc:
            print(token.text, token.dep_, token.head.text, token.head.pos_, [child for child in token.children])

    def parse_multiple(self, sentences: list[str]) -> None:
        for sentence in sentences:
            self.parse(sentence)


class ParseEvalbResult:
    def __init__(self, recall: float, precision: float):
        self.recall = recall
        self.precision = precision
        self.fscore = (2 * (recall * precision)) / (recall + precision)

    def __str__(self):
        return f"({self.recall:.2f}, {self.precision:.2f}, {self.fscore:.2f})"

    def __repr__(self):
        return self.__str__()


def score(*trees: Tree) -> list[list[ParseEvalbResult]]:
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


def get_sentences() -> list[parse.Sentence]:
    return parse.parse("gold_standard.txt")


def display_parses(*parses: list[Tree]):
    PADDING = 75

    cf = CanvasFrame(width=4000, height=4000)

    for i, sentence_parses in enumerate(zip(*parses)):
        for j, tree in enumerate(sentence_parses):
            tree_canvas = TreeWidget(cf.canvas(), tree)
            tree_canvas["node_font"] = "Helvetica 10 bold"
            tree_canvas["leaf_font"] = "Helvetica 10"
            tree_canvas["line_width"] = 2
            tree_canvas["xspace"] = 10
            tree_canvas["yspace"] = 10

            cf.add_widget(tree_canvas, (1000 * j) + PADDING, (300 * i) + PADDING)

    cf.mainloop()


def main():
    sentences = get_sentences()

    coreNLP_parses = CoreNLPConstituencyParser().parse_multiple(sentences)
    stanza_parses = StanzaConstituencyParser().parse_multiple(sentences)
    berkeley_parses = BerkeleyConstituencyParser().parse_multiple(sentences)
    berkeley_neural_parses = BerkeleyNeuralConstituencyParser().parse_multiple(sentences)
    gold_parses = [sentence.constituency_parse.nltk_tree for sentence in sentences]

    for i in range(len(sentences)):
        matrix = score(
            coreNLP_parses[i], stanza_parses[i], berkeley_parses[i], berkeley_neural_parses[i], gold_parses[i]
        )

        print(sentences[i].text)

        for i, row in enumerate(matrix):
            print(row)
        print("\n")

    display_parses(coreNLP_parses, stanza_parses, berkeley_parses, berkeley_neural_parses, gold_parses)


if __name__ == "__main__":
    main()
