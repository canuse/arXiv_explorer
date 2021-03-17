from Stemmer import Stemmer
from AbstractSearchEngine.db.StemHistory import update_stem_history, query_origin_word
from functools import lru_cache

stemmer = Stemmer('porter')


def stem(term, record=False):
    """
    stem word
    """
    stemmed_word = stemmer.stemWord(term)
    if record:
        update_stem_history(term, stemmed_word)
    return stemmed_word


@lru_cache(maxsize=None)
def unstem(stemmed_term):
    """
    unstem word
    """
    return query_origin_word(stemmed_term)
