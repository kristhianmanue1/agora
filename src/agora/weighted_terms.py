"""Opt-in exact-token IDF ranking; no translation, stemming or semantic coverage."""
import math
from collections import Counter
from .passages import terms

EN_STOP = frozenset('a an and are as at be been being by can could did do does for from had has have how i if in into is it its may might of on or our should than that the their them then there these they this those to was were what when where which who why will with would you your'.split())


def scores(paragraphs, question):
    """Sum smoothed IDF of unique matching terms, using this source's paragraphs."""
    documents = [terms(p) - EN_STOP for p in paragraphs]
    query = terms(question) - EN_STOP
    frequencies = Counter(t for document in documents for t in document)
    weights = {t: math.log((len(documents)+1)/(frequencies[t]+1))+1 for t in query}
    return [sum(weights[t] for t in sorted(query & document)) for document in documents]
