from importlib import import_module
import spacy, spacy_udpipe  # adding support for spacy-udpipe
from errant.annotator import Annotator

# ERRANT version
__version__ = '3.0.0'

# Load an ERRANT Annotator object for a given language
def load(lang, nlp=None):
    # Make sure the language is supported
    # for the purpose of the MultiGEC-2025 shared task this means: 'we have already downloaded the udpipe models'
    supported = {"cs", "de", "el", "en", "et", "is", "it", "lv", "ru", "sl", "sv", "uk"}
    if lang not in supported:
        raise Exception(f"{lang} is an unsupported or unknown language")
    #elif lang == "en":  # this is with standard spacy
        #spacy_small = "en_core_web_sm"
    #elif lang == "de":
        #spacy_small = "de_core_news_sm"

    # Load appropriate spacy-udpipe model for given language
    if nlp:
        nlp = nlp
    elif lang=="is":
        print("Will use UDPipe2 API for Icelandic texts")
    else:
        #print(f"Ok, using the spaCy model {spacy_small} for {lang}")
        #spacy.load(spacy_small, disable=["ner"])
        print(f"Ok, using the UDPipe model in {lang} for spacy-udpipe")
        #nlp = spacy_udpipe.load(lang)
        nlp = spacy_udpipe.load_from_path(lang, path="./")
    
    # Load language edit merger and edit classifier (use the English one for all)
    #if lang == "en":
    merger = import_module(f"errant.en.merger")
    classifier = import_module(f"errant.en.classifier")
    
    # The classifier needs spacy-udpipe
    classifier.nlp = nlp

    # Return a configured ERRANT annotator
    return Annotator(lang, nlp, merger, classifier)
