from errant.alignment import Alignment
from errant.edit import Edit
from spacy.tokens import Doc

# basic whitespace tokenizer from https://spacy.io/usage/linguistic-features#custom-tokenizer-example
class WhitespaceTokenizer:
    def __init__(self, vocab):
        self.vocab = vocab
    def __call__(self, text):
        words = text.split(" ")
        spaces = [True] * len(words)
        # Avoid zero-length tokens
        for i, word in enumerate(words):
            if word == "":
                words[i] = " "
                spaces[i] = False
        # Remove the final trailing space
        if words[-1] == " ":
            words = words[0:-1]
            spaces = spaces[0:-1]
        else:
           spaces[-1] = False
        return Doc(self.vocab, words=words, spaces=spaces)

# first use syntok for tokenisation because it deals with punctuation better than whitespace tokenisation
from syntok.tokenizer import Tokenizer
def pretokenize(txt):
    tok = Tokenizer()
    return ' '.join([str(token).strip() for token in tok.tokenize(txt)])

# to deal with Icelandic in MultiGEC-2025, AC 2024-10-23
import os
from spacy_conll import init_parser
from spacy_conll.parser import ConllParser
ice_parse = 'cat ice_in.txt | python udpipe2_client_original.py --model is --outfile ice_out.txt --input horizontal --parser "" --tagger "" --tokenizer "" '
drop_last_line = "sed '$ d' ice_out.txt  > ice_trimmed.txt"
tidy_up = "rm ice_*.txt"
import errant.cleanconll as cleanconll

# Main ERRANT Annotator class
class Annotator:

    # Input 1: A string language id: e.g. "en"
    # Input 2: A spacy processing object for the language
    # Input 3: A merging module for the language
    # Input 4: A classifier module for the language
    def __init__(self, lang, nlp=None, merger=None, classifier=None):
        self.lang = lang
        self.nlp = nlp
        self.merger = merger
        self.classifier = classifier

    # Input 1: A text string
    # Input 2: A flag for word tokenisation
    # Input 3: language, added by AC 2024-10-23
    # Output: The input string parsed by spacy_udpipe
    #def parse(self, text, tokenise=True, lang='en'):
    def parse(self, text, tokenise=True, lang='en'):  # AC 2024-11-05 making the default for tokenise True rather than False
        # if tokenise=False: Create Doc object from pretokenised text
        if not tokenise:
            text = Doc(self.nlp.vocab, text.split())
        # else if Icelandic: use UDPipe 2 (not in udpipe 1), note that UDP2 does not tokenise
        elif lang=="is":  # 2024-10-23: AC added if clause for Icelandic for MultiGEC-2025 (it's not in udpipe1 but udpipe2 via API)
            #lang="nb"
            #lang="nn"
            #text = self.nlp(text)
            print("Parsing Icelandic data with UDPipe2...")  # wanted to parse with icelandic model but problems with multiword tokens not being supported by spacy-conll (which imports the output file)
            text_tok = pretokenize(text)
            f = open('ice_in.txt', 'w')  # write
            f.write(text_tok)
            f.close()
            os.system(ice_parse)
            os.system(drop_last_line)
            cleanconll.rm_multiwords("ice_trimmed.txt")
            nlp = ConllParser(init_parser("en_core_web_sm", "spacy"))
            text = nlp.parse_conll_file_as_spacy("ice_trimmed.txt")
            os.system(tidy_up)
        #elif lang=="ru":  # russian is pre-tokenised, use the whitespace tokenizer class from above
            #self.nlp.tokenizer = WhitespaceTokenizer(self.nlp.vocab)
            #text = self.nlp(text)
        else:  # else pre-tokenize with syntok, split on whitespace, tag and parse
            text_tok = pretokenize(text)
            self.nlp.tokenizer = WhitespaceTokenizer(self.nlp.vocab)
            text = self.nlp(text_tok)
        return text

    # Input 1: An original text string parsed by spacy
    # Input 2: A corrected text string parsed by spacy
    # Input 3: A flag for standard Levenshtein alignment
    # Output: An Alignment object
    def align(self, orig, cor, lev=False):
        return Alignment(orig, cor, lev)

    # Input 1: An Alignment object
    # Input 2: A flag for merging strategy
    # Output: A list of Edit objects
    def merge(self, alignment, merging="rules"):
        # rules: Rule-based merging
        if merging == "rules":
            edits = self.merger.get_rule_edits(alignment)
        # all-split: Don't merge anything
        elif merging == "all-split":
            edits = alignment.get_all_split_edits()
        # all-merge: Merge all adjacent non-match ops
        elif merging == "all-merge":
            edits = alignment.get_all_merge_edits()
        # all-equal: Merge all edits of the same operation type
        elif merging == "all-equal":
            edits = alignment.get_all_equal_edits()
        # Unknown
        else:
            raise Exception("Unknown merging strategy. Choose from: "
                "rules, all-split, all-merge, all-equal.")
        return edits

    # Input: An Edit object
    # Output: The same Edit object with an updated error type
    def classify(self, edit):
        return self.classifier.classify(edit)

    # Input 1: An original text string parsed by spacy
    # Input 2: A corrected text string parsed by spacy
    # Input 3: A flag for standard Levenshtein alignment
    # Input 4: A flag for merging strategy
    # Output: A list of automatically extracted, typed Edit objects
    def annotate(self, orig, cor, lev=False, merging="rules"):
        alignment = self.align(orig, cor, lev)
        edits = self.merge(alignment, merging)
        for edit in edits:
            edit = self.classify(edit)
        return edits

    # Input 1: An original text string parsed by spacy
    # Input 2: A corrected text string parsed by spacy
    # Input 3: A token span edit list; [o_start, o_end, c_start, c_end, (cat)]
    # Input 4: A flag for gold edit minimisation; e.g. [a b -> a c] = [b -> c]
    # Input 5: A flag to preserve the old error category (i.e. turn off classifier)
    # Output: An Edit object
    def import_edit(self, orig, cor, edit, min=True, old_cat=False):
        # Undefined error type
        if len(edit) == 4:
            edit = Edit(orig, cor, edit)
        # Existing error type
        elif len(edit) == 5:
            edit = Edit(orig, cor, edit[:4], edit[4])
        # Unknown edit format
        else:
            raise Exception("Edit not of the form: "
                "[o_start, o_end, c_start, c_end, (cat)]")
        # Minimise edit
        if min: 
            edit = edit.minimise()
        # Classify edit
        if not old_cat: 
            edit = self.classify(edit)
        return edit
