from importlib import import_module
import spacy
from errant.annotator import Annotator

# ERRANT version
__version__ = '3.0.0'

# Load an ERRANT Annotator object for a given language
def load(lang, nlp=None):
    # Make sure the language is supported
    supported = {"de", "en"}
    if lang not in supported:
        raise Exception(f"{lang} is an unsupported or unknown language")
    elif lang == "en":
        spacy_small = "en_core_web_sm"
        print(f"Ok, using the spaCy model {spacy_small} for {lang}")
    elif lang == "de":
        spacy_small = "de_core_news_sm"
        print(f"Ok, using the spaCy model {spacy_small} for {lang}")

    # Load spacy (small model if no model supplied)
    nlp = nlp or spacy.load(spacy_small, disable=["ner"])

    # Load language edit merger and edit classifier
    if lang == "en":
        #print(f"WARNING: Loading English merger and classifier for language {lang}")
        merger = import_module(f"errant.en.merger")
        classifier = import_module(f"errant.en.classifier")
    elif lang == "de":
        merger = import_module(f"errant.de.merger")
        classifier = import_module(f"errant.de.classifier")
    
    # The classifier needs spacy
    classifier.nlp = nlp

    # Return a configured ERRANT annotator
    return Annotator(lang, nlp, merger, classifier)
