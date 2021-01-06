# These functions are designed to store and access index in a persistence way.

# These example function simply store index in file,
# please keep the returns and behaviors identical, but store them in SQL.
import os


def set_index(key1: str, key2: str, value) -> bool:
    """
    Set or update index
    :param key1: index key 1 (for example arxiv_id)
    :param key2: index key 2 (for example the term)
    :param value: The value of index. Note that TFIDF and BM25 uses float, but other model like doc2vec uses lists.
                  It is wiser to store them in string format in db.
    :return bool: return if the operation successes.
    """
    try:
        if os.path.exists('indexTemp'):
            pass
        else:
            os.mkdir('indexTemp')
        with open('indexTemp/' + key1 + '-' + key2, 'w') as fout:
            fout.write(value)
        return True
    except:
        return False


def get_index(key1: str, key2: str) -> float:
    """
    Query index, specially, if the key does not exist then return 0.
    :param key1: index key 1 (for example arxiv_id)
    :param key2: index key 2 (for example the term)
    :return value: The value of key. Note that we return a float value because we use TFIDF or BM25.
    """
    try:
        with open('indexTemp/' + key1 + '-' + key2, 'r') as fin:
            return float(fin.read())
    except:
        return 0


def delete_index(key1: str, key2: str) -> bool:
    """
    Delete index. Notice that we can set the value to 0 instead physically delete the file on disk.
    However, it might be unwise set value to 0 on db for it may result in a huge sparse table.
    :param key1: index key 1 (for example arxiv_id)
    :param key2: index key 2 (for example the term)
    :return bool: return if the operation successes.
    """
    try:
        return set_index(key1, key2, 0)
    except:
        return False
