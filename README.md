# L95 Assignment

### Structure

- `gold_standard/`
    - `gold_standard.txt`:
        - This file contains the provided gold standard data.
        - **Changes made to `gold_standard.txt`**:
            - The typo in the token "leve" in the bracketed constituency tree of Sentence 3 was corrected to "level".
            - A full stop node was added to the end of the bracketed constituency tree of Sentence 3 (as per the provided PoS tag annotation).
            - The node "didn't" in Sentence 10 was split into "did" and "n't" (as per the provided token and PoS tag annotations).
    - `gold_standard_loader.py`
        - This file parses the gold standard data into Python objects.
        - Pre-processing constituency trees:
            - The provided constituency trees omit the PoS tags of each token.
                - The `Sentence`'s `ConstituencyParse` object contains a function `annotate_leaves` that deepens `nltk_tree` by one level, adding in the PoS tag of each leaf node.

- `parser_loader/`
    - `constituency/`
        - `parser.py`
            - This file contains Python objects to load and parse a set of sentences from:
            1. Stanford's CoreNLP unlexicalised constituency parser
            2. Stanford's Stanza constituency parser
            3. Berkeley's constituency parser
            4. Berkeley's Neural constituency parser (Benepar)
    - `dependency/`
        - `parser.py`
            - This file contains Python objects to load and parse a set of sentences from:
            1. Spacy's dependency parser

- `experiments.py`
    - This file contains the code to run each gold standard sentence through the constituency and dependency parsers, and visualise/evaluate their generated results.

- `parser_tools/`
    - This directory contains the downloaded parser tools.
    - These are omitted from the repository due to their large size.
    - To run Stanford's CoreNLP parser:
        - Download the zip file from [here](https://stanfordnlp.github.io/CoreNLP/download.html) (version 4.5.8) and extract it to this (`parser_tools/`) directory.
        - Then execute the following command from this directory:
            ```bash
            java -mx4g -cp "*" edu.stanford.nlp.pipeline.StanfordCoreNLPServer -status_port 9000 -port 9000 -timeout 15000
            ```
            This will start the Stanford CoreNLP server on port 9000, and the parser loader will connect to it to parse the gold standard sentences.

- `evaluation_tools/`
    - `evaluation.py`
    This file contains code to evaluate the generated parses.
        - [`PYEVALB`](https://pypi.org/project/PYEVALB/) is used to evaluate constituency parses.