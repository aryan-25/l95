This directory contains the results of the experiments performed in Section 5.3 titled "Pre-Processing: PoS Tags".

To run the CoreNLP unlexicalised (`englishPCFG.ser.gz`) constituency parser with predefined PoS tags, use the following command:
```bash
java -mx1g -cp "*" edu.stanford.nlp.parser.lexparser.LexicalizedParser -sentences newline -tokenized -tagSeparator <tag_separator> -tokenizerFactory edu.stanford.nlp.process.WhitespaceTokenizer -tokenizerMethod newCoreLabelTokenizerFactory edu/stanford/nlp/models/lexparser/englishPCFG.ser.gz <pos_tag_filename>
```
where <tag_separator> and <pos_tag_filename> are the separator used in the PoS tag file and the path to the PoS tag file, respectively.

To replicate the results of Sentences 4 and 5, use the PoS tag file in `sentence_4/manual_pos.txt` and `sentence_5/manual_pos.txt` respectively. Both file use `/` as the separator.