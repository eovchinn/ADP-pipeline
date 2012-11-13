Run Pipeline with:
run_spanish.sh < examples/spanish_text.txt

PREPROCESSING (Does not need to be re-run)
create malty (conll) instances (anc_to_malt.py) (ancora.malt)
Make maltparse (MP) model (maltparse1.5)
extract words, pos, and lemmas from ancora.conll to make treetagger (TT) model (to_tree.py) (ancora.treetagger)
use (full_stop.py) to replace sentence final punct pos tags with "fs" tag for TT in ancora.treetagger (ancora.treetagger.fs)
use TT included script (make-lex.perl) to create a lexicon from word-pos-lemma file (ancora.lex)
use (ancora.lex), (ancora.unknown), and (ancora.treetagger.fs) files to create TT model with (specify fs as sentence final punct) (ancora.treetagger.par)
END PREPROCESSING

For tagging, I used Treetagger 3.2 along with the Spanish parameter file:
 - treetagger 3.2 - http://www.ims.uni-stuttgart.de/projekte/corplex/TreeTagger/
 - Spanish parameter file available from the same page, apparently trained on the Spanish CRATER corpus, using the Spanish lexicon of the CALLHOME corpus
    - http://www.comp.lancs.ac.uk/linguistics/crater/corpus.html
    - http://www.ldc.upenn.edu/Catalog/catalogEntry.jsp?catalogId=LDC96L16
 - references - ftp://ftp.ims.uni-stuttgart.de/pub/corpora/tree-tagger1.pdf
                     - ftp://ftp.ims.uni-stuttgart.de/pub/corpora/tree-tagger2.pdf

For parsing, I used maltparser 1.5.
 - maltparser 1.5 - http://www.maltparser.org/download.html
 - references - http://www.maltparser.org/publications.html
    I think I've used this one in the past - http://www.bibsonomy.org/bibtex/2219fdcfa3a894d52f158905978aafe09/arnsholt

For training maltparser, I used the Ancora corpus:
 - 500,000 words
 - Ancora - http://clic.ub.edu/corpus/en
                - http://clic.ub.edu/corpus/webfm_send/13
 - reference - http://www.lrec-conf.org/proceedings/lrec2008/pdf/35_paper.pdf

examples:
CESS-CAST-P_107_19991001.malt - sample dependency output
CESS-CAST-P_107_19991001.props - sample proposition output
ancora.lex - lexicon for use with treetagger
ancora.malt - conll file to build maltparser model
ancora.treetagger - word, pos, lemmas from ancora.malt 
ancora.treetagger.fs - word, pos, lemmas from ancora.malt with 'fs' sentence-final punct-pos; to train treetagger
spanish_text.ancora.tagged - output of treetagger with ancora corpus pos tags 
spanish_text.tree.tagged - output of treetagger with default treetagger spanish pos tags 
spanish_text.conll - output of to_malt.py from treetagged file
spanish_text.tokens - output of freeling tokenizer
spanish_text.txt - raw file of spanish text from web