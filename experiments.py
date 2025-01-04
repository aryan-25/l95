from nltk import Tree  # type: ignore
from nltk.draw.tree import TreeWidget  # type: ignore
from nltk.draw.util import CanvasFrame  # type: ignore


import parse
from evaluation import pyevalb_score
from parsers import (
    BerkeleyConstituencyParser,
    BerkeleyNeuralConstituencyParser,
    CoreNLPConstituencyParser,
    StanzaConstituencyParser,
)


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
        matrix = pyevalb_score(
            coreNLP_parses[i], stanza_parses[i], berkeley_parses[i], berkeley_neural_parses[i], gold_parses[i]
        )

        print(sentences[i].text)

        for i, row in enumerate(matrix):
            print(row)
        print("\n")

    display_parses(coreNLP_parses, stanza_parses, berkeley_parses, berkeley_neural_parses, gold_parses)


if __name__ == "__main__":
    main()
