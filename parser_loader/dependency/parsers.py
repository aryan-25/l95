import spacy


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
