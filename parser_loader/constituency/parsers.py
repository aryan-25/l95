import abc
import os

import stanza  # type: ignore
from nltk.parse.corenlp import CoreNLPParser  # type: ignore
from nltk.tokenize.treebank import TreebankWordTokenizer  # type: ignore
from nltk.tree import Tree

from gold_standard.gold_standard_loader import Sentence


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
        # Remove the `TOP` node since the gold standard trees do not have it
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

    def cleanup(self):
        os.system("rm input.txt output.txt")

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
            "java -jar ./parser_tools/berkeleyparser/BerkeleyParser-1.7.jar -gr ./parser_tools/berkeleyparser/eng_sm6.gr < input.txt > output.txt"
        )

        with open("output.txt", "r") as f:
            out = self.post_process(Tree.fromstring(f.readline()))

        self.cleanup()
        return out

    def parse_multiple(self, sentences):
        with open("input.txt", "w") as f:
            for sentence in sentences:
                f.write(self.ptb_tokenise(sentence.text) + "\n")

        os.system(
            "java -jar ./parser_tools/berkeleyparser/BerkeleyParser-1.7.jar -gr ./parser_tools/berkeleyparser/eng_sm6.gr < input.txt > output.txt"
        )

        with open("output.txt", "r") as f:
            out = [self.post_process(Tree.fromstring(line)) for line in f.readlines()]

        self.cleanup()
        return out

    def post_process(self, tree: Tree) -> Tree:
        # Remove the root node since the gold standard trees do not have it
        return tree[0]


class BerkeleyNeuralConstituencyParser(Parser):
    def __init__(self):
        # import benepar only if we use it --- takes several seconds to load
        import benepar  # type: ignore

        self.parser = benepar.Parser("benepar_en3")

    def parse(self, text: str) -> Tree:
        return self.post_process(self.parser.parse(text))

    def post_process(self, tree: Tree) -> Tree:
        # Remove the `ROOT` node since the gold standard trees do not have it
        return tree[0]
