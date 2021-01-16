from Stemmer import Stemmer
from AbstractSearchEngine.db.StemHistoryRedis import update_stem_history, query_origin_word

stemmer = Stemmer('porter')


def stem(term, record=False):
    stemmed_word = stemmer.stemWord(term)
    if record:
        update_stem_history(term, stemmed_word)
    return stemmed_word


def unstem(stemmed_term):
    return query_origin_word(stemmed_term)
