# These functions are designed to store and access index in a persistence way.

# These example function simply store index in file,
# please keep the returns and behaviors identical, but store them in SQL.

from AbstractSearchEngine.models import ArxivRank


# ArxivRank model has 4 columns: word / paper(arvix_id) / algorithm / rank_value

def set_index(key1: str, key2: str, key3: str, value) -> bool:
    """
    Set or update index
    :param key1: index key 1 (for example arxiv_id)
    :param key2: index key 2 (for example the term)
    :param key3: index key 3 (for example the algorithm(TFIDF or BM25))
    :param value: The value of index. Note that TFIDF and BM25 uses float, but other model like doc2vec uses lists.
                  It is wiser to store them in string format in db.
    :return bool: return if the operation successes.
    """

    try:
        if ArxivRank.objects.filter(paper=key1, word=key2, algorithm=key3).exists():
            # already have the stemmed word pair, update the value
            temp = ArxivRank.objects.get(paper=key1, word=key2, algorithm=key3)
            temp.rank_value = value
            temp.save()
        else:
            # create a new row
            temp = ArxivRank(
                paper=key1,
                word=key2,
                algorithm=key3,
                rank_value=value
            )
            temp.save()
        return True
    except:
        return False


def get_index(key1: str, key2: str, key3: str) -> float:
    """
    Query index, specially, if the key does not exist then return 0.
    :param key1: index key 1 (for example arxiv_id)
    :param key2: index key 2 (for example the term)
    :param key3: index key 3 (for example the algorithm(TFIDF or BM25))
    :return value: The value of key. Note that we return a float value because we use TFIDF or BM25.
    """
    try:
        temp = ArxivRank.objects.get(paper=key1, word=key2, algorithm=key3)
        return temp.rank_value
    except:
        return 0


def delete_index(key1: str, key2: str, key3: str) -> bool:
    """
    Delete index. If the row with key(key1,key2,key3) exists, delete the row in db.
    :param key1: index key 1 (for example arxiv_id)
    :param key2: index key 2 (for example the term)
    :param key3: index key 3 (for example the algorithm(TFIDF or BM25))
    :return bool: return if the operation successes.
    """
    try:
        temp = ArxivRank.objects.get(paper=key1, word=key2, algorithm=key3)
        temp.delete()
        return True
    except:
        return False


def delete_all_index(key1=None, key2=None, key3=None):
    """
    Delete all index.
    If key1!=None, then delete all index contains key1. key2 and key3 are similar.
    For example, if key1=none, key2="apple" and key3="BM25", then this method will remove
    all index that uses BM25 and term "apple".
    :param key1: index key 1 (for example arxiv_id)
    :param key2: index key 2 (for example the term)
    :param key3: index key 3 (for example the algorithm(TFIDF or BM25))
    :return bool: return if the operation successes.
    """
    if key1 is None and key2 is None and key3 is None:
        return True
    try:
        temp = ArxivRank.objects
        if key1 is not None:
            temp = temp.filter(paper=key1)
        if key2 is not None:
            temp = temp.filter(word=key2)
        if key3 is not None:
            temp = temp.filter(algorithm=key3)
        temp.delete()
    except:
        return False


def get_all_index(key1=None, key2=None, key3=None):
    """
    get all index.
    If key1!=None, then get all index contains key1. key2 and key3 are similar.
    For example, if key1=none, key2="apple" and key3="BM25", then this method will get
    all index that uses BM25 and term "apple". the return value will be a iterable object(like list)
    :param key1: index key 1 (for example arxiv_id)
    :param key2: index key 2 (for example the term)
    :param key3: index key 3 (for example the algorithm(TFIDF or BM25))
    """
    ret_list = []
    if key1 is None and key2 is None and key3 is None:
        return []
    try:
        temp = ArxivRank.objects
        if key1 is not None:
            temp = temp.filter(paper=key1)
        if key2 is not None:
            temp = temp.filter(word=key2)
        if key3 is not None:
            temp = temp.filter(algorithm=key3)
        for i in temp:
            ret_list.append([i.paper, i.word, i.algorithm, i.rank_value])
        return ret_list
    except:
        return []


def set_index_bulk(bulk_index):
    bulk_data = []
    for i in bulk_index:
        bulk_data.append(ArxivRank(paper=i[0], word=i[1], algorithm=i[2], rank_value=i[3]))
    ArxivRank.objects.bulk_create(bulk_data)
