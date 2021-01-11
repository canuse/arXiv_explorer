# These functions are designed to store and access index in a persistence way.

# These example function simply store index in file,
# please keep the returns and behaviors identical, but store them in SQL.
import os


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
        if os.path.exists('indexTemp'):
            pass
        else:
            os.mkdir('indexTemp')
        with open('indexTemp/' + key1 + '-' + key2 + '-' + key3, 'w') as fout:
            fout.write(value)
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
        with open('indexTemp/' + key1 + '-' + key2 + '-' + key3, 'r') as fin:
            return float(fin.read())
    except:
        return 0


def delete_index(key1: str, key2: str, key3: str) -> bool:
    """
    Delete index. Notice that we can set the value to 0 instead physically delete the file on disk.
    However, it might be unwise set value to 0 on db for it may result in a huge sparse table.
    :param key1: index key 1 (for example arxiv_id)
    :param key2: index key 2 (for example the term)
    :param key3: index key 3 (for example the algorithm(TFIDF or BM25))
    :return bool: return if the operation successes.
    """
    try:
        return set_index(key1, key2, key3, 0)
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
        files = os.listdir('indexTemp/')
        for file in files:
            fkey1, fkey2, fkey3 = file.split('-')
            flag = True
            if key1 is not None:
                flag = flag | (fkey1 == key1)
            if key2 is not None:
                flag = flag | (fkey2 == key2)
            if key3 is not None:
                flag = flag | (fkey3 == key3)
            if flag:
                set_index(fkey1, fkey2, fkey3, 0)
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
        files = os.listdir('indexTemp/')
        for file in files:
            fkey1, fkey2, fkey3 = file.split('-')
            flag = True
            if key1 is not None:
                flag = flag | (fkey1 == key1)
            if key2 is not None:
                flag = flag | (fkey2 == key2)
            if key3 is not None:
                flag = flag | (fkey3 == key3)
            if flag:
                ret_list.append([key1, key2, key3, get_index(key1, key2, key3)])
    except:
        return []
