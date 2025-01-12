import os
from multiprocessing import Process
from typing import Union

import spacy
import spacy.displacy
from nltk import Tree  # type: ignore
from nltk.draw.tree import TreeWidget  # type: ignore
from nltk.draw.util import CanvasFrame  # type: ignore
from spacy.tokens import Doc

import gold_standard.gold_standard_loader as gold_standard_loader
from parser_loader.constituency.parsers import (
    BerkeleyConstituencyParser,
    BerkeleyNeuralConstituencyParser,
    CoreNLPConstituencyParser,
    StanzaConstituencyParser,
)
from parser_loader.dependency.parsers import SpacyDependencyParser


def get_sentences(gold_standard_filename: str) -> list[gold_standard_loader.Sentence]:
    return gold_standard_loader.parse(gold_standard_filename)


def display_constituency_parses(*parses: list[Tree]):
    PADDING = 75

    cf = CanvasFrame(width=4000, height=4000)

    for i, sentence_parses in enumerate(zip(*parses)):
        for j, tree in enumerate(sentence_parses):
            tree_canvas = TreeWidget(cf.canvas(), tree)
            tree_canvas["node_font"] = "Helvetica 10 bold"
            tree_canvas["leaf_font"] = "Helvetica 10"
            tree_canvas["line_width"] = 1
            tree_canvas["xspace"] = 5
            tree_canvas["yspace"] = 10

            cf.add_widget(tree_canvas, (900 * j) + PADDING, (400 * i) + PADDING)

    cf.mainloop()


def parse_tree_to_svg(tree: Tree, filename: str) -> None:
    with open(filename, "w") as f:
        f.write(tree._repr_svg_())


def display_dependency_parses(doc: Union[list[Doc], list[dict]], manual=False, port=8000):
    spacy.displacy.serve(doc, style="dep", port=port, manual=manual)


def constituency_parsers():
    gold = get_sentences("gold_standard/gold_standard.txt")
    modified_gold = get_sentences("gold_standard/modified_gold_standard.txt")

    coreNLP_parses = CoreNLPConstituencyParser().parse_multiple(modified_gold)
    # stanza_parses = StanzaConstituencyParser().parse_multiple(modified_gold)
    # berkeley_parses = BerkeleyConstituencyParser().parse_multiple(modified_gold)
    berkeley_neural_parses = BerkeleyNeuralConstituencyParser().parse_multiple(modified_gold)
    gold_parses = [sentence.constituency_parse.nltk_tree for sentence in gold]
    modified_gold_parses = [sentence.constituency_parse.nltk_tree for sentence in modified_gold]

    parses = {
        "coreNLP": coreNLP_parses,
        # "stanza": stanza_parses,
        # "berkeley": berkeley_parses,
        "benepar": berkeley_neural_parses,
        "gold": gold_parses,
        "modified_gold": modified_gold_parses,
    }

    for i in range(len(modified_gold)):
        for parser, parser_parses in parses.items():
            if not os.path.exists(f"parser_output/{parser}"):
                os.makedirs(f"parser_output/{parser}")

            with open(f"parser_output/{parser}/sentence_{i+1}.txt", "w") as f:
                # print a flat representation of the tree with no newlines
                f.write(str(parser_parses[i]).replace("\n", ""))

            if not os.path.exists(f"parser_output/evalb_results/sentence_{i + 1}"):
                os.makedirs(f"parser_output/evalb_results/sentence_{i + 1}")

            if parser == "modified_gold" or parser == "gold":
                continue  # to skip evaluation of the gold standard against itself

            gold_evaluation_cmd = f"./evaluation_tools/EVALB/evalb parser_output/original_gold/sentence_{i + 1}.txt parser_output/{parser}/sentence_{i + 1}.txt > parser_output/evalb_results/sentence_{i + 1}/{parser}_vs_original_gold.txt"
            os.system(gold_evaluation_cmd)
            modified_gold_evaluation_cmd = f"./evaluation_tools/EVALB/evalb parser_output/modified_gold/sentence_{i + 1}.txt parser_output/{parser}/sentence_{i + 1}.txt > parser_output/evalb_results/sentence_{i + 1}/{parser}_vs_modfied_gold.txt"
            os.system(modified_gold_evaluation_cmd)

        # Use Benepar as the gold standard reference and evaluate CoreNLP against it
        rel_evaluation_cmd = f"./evaluation_tools/EVALB/evalb parser_output/benepar/sentence_{i + 1}.txt parser_output/coreNLP/sentence_{i + 1}.txt > parser_output/evalb_results/sentence_{i + 1}/coreNLP_vs_benepar.txt"

        os.system(rel_evaluation_cmd)

    display_constituency_parses(
        coreNLP_parses,
        berkeley_neural_parses,
        modified_gold_parses,
    )


def dependency_parsers():
    sentences = get_sentences("gold_standard/gold_standard.txt")

    spacy_parses = SpacyDependencyParser().parse_multiple([sentence.text for sentence in sentences])
    gold_parses: list[gold_standard_loader.DependencyParse] = [sentence.dependency_parse for sentence in sentences]

    gold_parse_spacy = [gold_parse.spacy_representation() for gold_parse in gold_parses]

    # Display the generated parses in a localhost webpage running on port 8000
    # Run this in a separate process to avoid blocking the main process
    Process(target=display_dependency_parses, args=(spacy_parses,)).start()

    # Display the gold-standard parses in a localhost webpage running on port 8001
    display_dependency_parses(gold_parse_spacy, manual=True, port=8001)


def main():
    constituency_parsers()


if __name__ == "__main__":
    main()
