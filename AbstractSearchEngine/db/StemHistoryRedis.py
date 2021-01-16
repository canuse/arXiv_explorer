import redis

r_stem = redis.StrictRedis(host='localhost', port=6379, db=0)


# db=0: stem db=1: term freq db=2: BM25

def update_stem_history(word, stemmed_word):
    """
    please design a table that has two columns, column 1 is stemmed word while column 2 is original word.
    """
    r_stem.set(stemmed_word, word)


def query_origin_word(stemmed_word):
    # return the latest original word
    word = r_stem.get(stemmed_word)
    if word is None:
        return ""
    else:
        return word.decode()
