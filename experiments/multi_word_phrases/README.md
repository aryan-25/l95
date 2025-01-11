This directory contains the results of the experiments performed in Section 5.2 titled "Multi-word Phrases".

- `unlexicalised_original/coreNLP/` contains two text files that contain the partial parse of the first and second clause of Sentence 3 respectively (_"Prudently, they had diversified into banking and insurance"_ and _"as a result their influence was felt at the greatest level"_).
  - These structures were extracted from the CoreNLP parse generated for the entire Sentence 3.
- `unlexicalised_original/modified_gold_standard` contains the gold standard parse of the first and second clause of Sentence 3 respectively.
  - These structures were extracted from the gold standard parse of the entire Sentence 3.
- `unlexicalised_original/evalb_results` contains the `evalb` results of CoreNLP's generated partial parses of the first and second clause compared with the gold-standard partial parses, respectively.

The `unlexicalised_comma_inserted/` directory contains the parses and results of the experiment **where a comma was inserted after "result"**.

The `lexicalised_original/` directory contains the parses and results of the experiment where the **lexicalised** parser was used to parse the entire Sentence 3**. The input to the parser was the entire Sentence 3 (**without** the comma after "result"). This directory also contains the lexicalised `englishFactored.ser.gz` parser model (provided here since it is hard to find a download link of the CoreNLP parser that includes the lexicalised parser online). The file `parser.properties` contains the properties used to run the lexicalised parser. Note that the _unlexicalised_ parser is chosen by default if no properties file is provided.