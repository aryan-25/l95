import pprint
import re

from nltk.tree import Tree  # type: ignore


class Token:
    def __init__(self, token: str, base_form: str, universal_pos_tag: str, ptb_pos_tag: str):
        self.token: str = token
        self.base_form: str = base_form
        self.universal_pos_tag: str = universal_pos_tag
        self.ptb_pos_tag: str = ptb_pos_tag

    def __str__(self):
        return f"{self.token}/{self.base_form}/{self.universal_pos_tag}/{self.ptb_pos_tag}"

    def __repr__(self):
        return self.__str__()


class ConstituencyParse:
    def __init__(self, parse_str: str):
        self._parse_tree: str = parse_str
        self.nltk_tree: Tree = Tree.fromstring(parse_str)

    def annotate_leaves(self, pos_tags: list[Token]):
        # for each leaf node in the tree, replace the leaf with a new 1-level tree node: (POS tag -> leaf)

        def annotate_leaves_rec(tree, pos_tags: list[Token], idx):
            for i, child in enumerate(tree):
                # if the child node is a leaf then replace it with a new 1-level tree node
                if isinstance(child, str):
                    token: Token = pos_tags[idx]
                    tree[i] = Tree(token.universal_pos_tag, [child])
                    idx += 1  # move to the next POS tag
                else:  # recurse until we reach a leaf node
                    # update idx to the return value of the recursive call to keep track of the current POS tag
                    idx = annotate_leaves_rec(child, pos_tags, idx)

            return idx

        annotate_leaves_rec(self.nltk_tree, pos_tags, 0)

    def __str__(self):
        return self._parse_tree

    def __repr__(self):
        return self.__str__()


class DependencyArc:
    def __init__(self, token_idx: int, token: str, gram_rel: str, head_idx: int):
        self.token_idx = token_idx
        self.token = token
        self.gram_rel = gram_rel
        self.head_idx = head_idx

    def __str__(self):
        return f"{self.head_idx} to {self.token_idx} ({self.gram_rel})"

    def __repr__(self):
        return self.__str__()


class DependencyParse:
    def __init__(self, tokens: list[Token], parse_lines: list[str]):
        self.arcs: list[DependencyArc] = []
        self.tokens: list[Token] = tokens

        for line in parse_lines:
            if not line:
                continue

            dependent_idx, token, gram_rel, head_idx = line.split("\t")
            self.arcs.append(DependencyArc(int(dependent_idx), token, gram_rel, int(head_idx)))

    def spacy_representation(self):
        return {
            "words": [{"text": token.token, "tag": token.ptb_pos_tag} for token in self.tokens],
            "arcs": [
                {
                    "start": min(arc.head_idx - 1, arc.token_idx - 1),
                    "end": max(arc.head_idx - 1, arc.token_idx - 1),
                    "label": arc.gram_rel,
                    "dir": "right" if arc.head_idx < arc.token_idx else "left",
                }
                for arc in self.arcs
                if arc.gram_rel != "ROOT"
            ],
        }

    def __str__(self):
        return pprint.pformat([str(arc) for arc in self.arcs], sort_dicts=False)

    def __repr__(self):
        return self.__str__()


class Sentence:
    def __init__(
        self, text: str, tokens: list[Token], constituency_parse: ConstituencyParse, dependency_parse: DependencyParse
    ):
        self.text: str = text
        self.tokens: list[Token] = tokens
        self.constituency_parse: ConstituencyParse = constituency_parse
        self.dependency_parse: DependencyParse = dependency_parse

        # The leaves of the provided constituency parse tree are not annotated with POS tags
        # We need to add an extra level to the leaves of the tree (POS tag -> leaf)
        # This is done so that we can accurately compare the gold standard constituency parse tree with parse trees generated by other parsers
        self.constituency_parse.annotate_leaves(tokens)

    def __str__(self):
        return pprint.pformat(
            {
                "text": self.text,
                "tokens": [str(token) for token in self.tokens],
                "parse": {"constituency": self.constituency_parse, "dependency": self.dependency_parse},
            },
            sort_dicts=False,
        )

    def __repr__(self):
        return self.__str__()


def split_into_sentences(lines: list[str]) -> list[list[str]]:
    sentences: list[list[str]] = []
    curr_sentence: list[str] = []

    for line in lines:
        if re.match(r"^\d+\.\s", line) and curr_sentence:
            sentences.append(curr_sentence)
            curr_sentence = []
        curr_sentence.append(line)
    sentences.append(curr_sentence)

    return sentences


def split_into_components(sentence: list[str]) -> tuple[str, str, str, list[str]]:
    # Splits the list of lines for a sentence into 4 components:
    # 1. The tokens of the sentence
    # 2. POS tag annotations for the tokens
    # 3. Constituency parse
    # 4. Dependency parse

    sentence_text: str
    pos_tags: str
    constituency_parse: str = ""
    dependency_parse: list[str] = []

    sentence_text = sentence[0]
    sentence_text = re.sub(r"^\d+\.\s", "", sentence_text)

    pos_tags = sentence[1]

    idx = 2
    stack = []
    while idx < len(sentence):
        line = sentence[idx]

        for c in line:
            if c == "(":
                stack.append(c)
            elif c == ")":
                stack.pop()

        idx += 1
        if not stack:
            break

    constituency_parse = "".join(sentence[2:idx])
    dependency_parse = sentence[idx:]

    return sentence_text, pos_tags, constituency_parse, dependency_parse


def parse_annotations(annotation_str: str) -> list[Token]:
    pos_tags: list[Token] = []

    for token in annotation_str.split("	"):
        token, base_form, universal_pos, universal_pos = token.split("\\")
        pos_tags.append(Token(token, base_form, universal_pos, universal_pos))

    return pos_tags


def parse(filename: str) -> list[Sentence]:
    with open(filename, "r") as f:
        lines = [line[:-1] for line in f.readlines()]

        sentences = split_into_sentences(lines)

        parsed_sentences: list[Sentence] = []
        for sentence in sentences:
            sentence_text, pos_tags, constituency_parse, dependency_parse = split_into_components(sentence)

            tokens = parse_annotations(pos_tags)
            const_parse = ConstituencyParse(constituency_parse)
            dep_parse = DependencyParse(tokens, dependency_parse)
            parsed_sentences.append(Sentence(sentence_text, tokens, const_parse, dep_parse))

        return parsed_sentences
