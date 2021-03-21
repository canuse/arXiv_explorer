from AbstractSearchEngine.indexing.BM25 import BM25
from AbstractSearchEngine.utils.ranking import borda_count
from AbstractSearchEngine.indexing.TFIDF import TFIDF
from functools import lru_cache


@lru_cache()
def search_by_words(word_list):
    """[summary]

    Args:
        word_list ([type]): [description]

    Returns:
        list: list of article_id。不需要score。
    """
    bm25_result, wc1 = BM25.search_by_words(word_list)
    tfidf_result, wc2 = TFIDF.search_by_words(word_list)

    result = borda_count([bm25_result, tfidf_result])
    return [x[0] for x in result], max(wc1, wc2)


def query_expansion(word_list, nrel=10, nexp=2, allow_dup=True):
    """[summary]

    Args:
        word_list ([type]): [description]
        nrel (int, optional): [description]. Defaults to 10.
        nexp (int, optional): [description]. Defaults to 2.
        allow_dup (bool, optional): [description]. Defaults to True.

    Returns:
        list: list of expended query。预计返回stem过之后的["apple banana fruit","apple banana orange".....]
    """
    bm25_result = BM25.query_expansion(word_list, nrel=nrel, nexp=nexp, allow_dup=allow_dup)
    tfidf_result = TFIDF.query_expansion(word_list, nrel=nrel, nexp=nexp, allow_dup=allow_dup)
    result = borda_count([bm25_result, tfidf_result], algorithm='vote')
    return result


def get_relative_article(arxivID_list, nart=10):
    """[summary]

    Args:
        arxivID_list ([type]): [description]
        nart (int, optional): [description]. Defaults to 10.

    Returns:
        list: list of article_id。不需要score。
    """
    bm25_result = BM25.get_relative_article(arxivID_list, nart=10)
    tfidf_result = TFIDF.get_relative_article(arxivID_list, nart=10)

    result = borda_count([bm25_result, tfidf_result])
    return [x[0] for x in result]
