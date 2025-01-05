from multiprocessing import Process
from typing import Union

import spacy
import spacy.displacy
from nltk import Tree  # type: ignore
from nltk.draw.tree import TreeWidget  # type: ignore
from nltk.draw.util import CanvasFrame  # type: ignore
from spacy.tokens import Doc

import gold_standard.gold_standard_loader as gold_standard_loader
from evaluation_tools.evaluation import pyevalb_score
from parser_loader.constituency.parsers import (
    BerkeleyConstituencyParser,
    BerkeleyNeuralConstituencyParser,
    CoreNLPConstituencyParser,
    StanzaConstituencyParser,
)
from parser_loader.dependency.parsers import SpacyDependencyParser


def get_sentences() -> list[gold_standard_loader.Sentence]:
    return gold_standard_loader.parse("gold_standard/gold_standard.txt")


def display_constituency_parses(*parses: list[Tree]):
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


def display_dependency_parses(doc: Union[list[Doc], list[dict]], manual=False, port=8000):
    spacy.displacy.serve(doc, style="dep", port=port, manual=manual)


def constituency_parsers():
    sentences = get_sentences()

    coreNLP_parses = CoreNLPConstituencyParser().parse_multiple(sentences)
    stanza_parses = StanzaConstituencyParser().parse_multiple(sentences)
    berkeley_parses = BerkeleyConstituencyParser().parse_multiple(sentences)
    berkeley_neural_parses = BerkeleyNeuralConstituencyParser().parse_multiple(sentences)
    gold_parses = [sentence.constituency_parse.nltk_tree for sentence in sentences]

    for i in range(len(sentences)):
        matrix = pyevalb_score(
            coreNLP_parses[i],
            stanza_parses[i],
            berkeley_parses[i],
            berkeley_neural_parses[i],
            gold_parses[i],
        )

        print(sentences[i].text)
        for row in matrix:
            print(row)
        print("\n")

    display_constituency_parses(
        coreNLP_parses,
        stanza_parses,
        berkeley_parses,
        berkeley_neural_parses,
        gold_parses,
    )


def dependency_parsers():
    sentences = get_sentences()

    spacy_parses = SpacyDependencyParser().parse_multiple([sentence.text for sentence in sentences])
    gold_parses: list[gold_standard_loader.DependencyParse] = [sentence.dependency_parse for sentence in sentences]

    gold_parse_spacy = [gold_parse.spacy_representation() for gold_parse in gold_parses]

    # Display the generated parses in port 8000
    # Run this in a separate process to avoid blocking the main process
    Process(target=display_dependency_parses, args=(spacy_parses,)).start()

    # Display the gold parses in port 8001
    display_dependency_parses(gold_parse_spacy, manual=True, port=8001)


def main():
    # constituency_parsers()
    dependency_parsers()


if __name__ == "__main__":
    main()
