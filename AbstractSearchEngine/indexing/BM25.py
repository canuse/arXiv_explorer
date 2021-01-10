from AbstractSearchEngine.db.IndexPersistence import get_index, set_index
from AbstractSearchEngine.indexing.BaseAlgorithm import BaseAlgorithm


class BM25(BaseAlgorithm):
    """
    This class should implements the BM25 indexing, including:
    1. calculate the BM25 index of one term
    2. update the index (when new data comes)
    3. query by words (which includes query expansion)
    4. query expansion
    5. get top used words (for input completion)
    """

    def __init__(self):
        super().__init__()

    @staticmethod
    def search_by_words(word_list):
        return [1, 2, 3]

    @staticmethod
    def query_expansion(word_list, nrel=10, nexp=2):
        return word_list.append('example')

    @staticmethod
    def get_relative_article(arxivID_list, nart=10):
        return [1, 2, 3, 4, 5]
