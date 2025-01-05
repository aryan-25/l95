import spacy
from spacy.tokens import Doc


class SpacyDependencyParser:
    def __init__(self):
        self.nlp: spacy.Language = spacy.load("en_core_web_sm")

    def parse(self, text: str) -> Doc:
        return self.nlp(text)

    def parse_multiple(self, sentences: list[str]) -> list[Doc]:
        out: list[Doc] = []
        for sentence in sentences:
            out.append(self.parse(sentence))

        return out
