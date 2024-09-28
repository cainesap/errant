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

    # Load spacy (small model if no model supplied)
    nlp = nlp or spacy.load(f"{lang}_core_web_sm", disable=["ner"])

    # Load language edit merger
    if lang != "en":
        print(f"WARNING: Loading English merger and classifier for language {lang}")
    merger = import_module(f"errant.en.merger")

    # Load language edit classifier
    classifier = import_module(f"errant.en.classifier")
    # The English classifier needs spacy
    classifier.nlp = nlp

    # Return a configured ERRANT annotator
    return Annotator(lang, nlp, merger, classifier)