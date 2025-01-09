To run the CoreNLP unlexicalised (`englishPCFG.ser.gz`) constituency parser with predefined PoS tags, use the following command:
```bash
java -mx1g -cp "*" edu.stanford.nlp.parser.lexparser.LexicalizedParser -sentences newline -tokenized -tagSeparator <tag_separator> -tokenizerFactory edu.stanford.nlp.process.WhitespaceTokenizer -tokenizerMethod newCoreLabelTokenizerFactory edu/stanford/nlp/models/lexparser/englishPCFG.ser.gz <pos_tag_filename>
```
where <tag_separator> and <pos_tag_filename> are the separator used in the PoS tag file and the path to the PoS tag file, respectively.

To replicate the results of Sentence 4, use the PoS tag file `4_manual_pos.txt` (located in this same directory). This file uses `/` as the separator.