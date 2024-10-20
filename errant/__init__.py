from importlib import import_module
import spacy, spacy_udpipe  # adding support for spacy-udpipe
from errant.annotator import Annotator

# ERRANT version
__version__ = '3.0.0'

# Load an ERRANT Annotator object for a given language
def load(lang, nlp=None):
    # Make sure the language is supported
    # for the purpose of the MultiGEC-2025 shared task this means: 'we have already downloaded the udpipe models'
    supported = {"cs", "de", "en"}
    if lang not in supported:
        raise Exception(f"{lang} is an unsupported or unknown language")
    #elif lang == "en":  # this is with standard spacy
        #spacy_small = "en_core_web_sm"
    #elif lang == "de":
        #spacy_small = "de_core_news_sm"

    # Load spacy (small model if no model supplied)
    if nlp:
        nlp = nlp
    else:
        #print(f"Ok, using the spaCy model {spacy_small} for {lang}")
        #spacy.load(spacy_small, disable=["ner"])
        print(f"Ok, using the UDPipe model in {lang} for spacy-udpipe")
        nlp = spacy_udpipe.load(lang)

    # Load language edit merger and edit classifier
    if lang == "cs":
        #print(f"WARNING: Loading English merger and classifier for language {lang}")
        merger = import_module(f"errant.en.merger")
        classifier = import_module(f"errant.en.classifier")
    elif lang == "de":
        merger = import_module(f"errant.de.merger")
        classifier = import_module(f"errant.de.classifier")
    elif lang == "en":
        merger = import_module(f"errant.en.merger")
        classifier = import_module(f"errant.en.classifier")
    
    # The classifier needs spacy
    classifier.nlp = nlp

    # Return a configured ERRANT annotator
    return Annotator(lang, nlp, merger, classifier)
