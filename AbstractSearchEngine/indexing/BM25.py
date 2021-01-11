from math import log

from AbstractSearchEngine.db.IndexPersistence import get_index, set_index, delete_all_index
from AbstractSearchEngine.indexing.BaseAlgorithm import BaseAlgorithm, BaseIndex

BM25_b = 0.3
BM25_delta = 1
BM25_preset = [0] + [(x / 1000) / ((x / 1000) - 1) * log((x / 1000)) if x != 1000 else 1 for x in range(1, 3000)]


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
    def update_index(index: BaseIndex):
        delete_all_index(key3="BM25TLS")
        document_length = list(index.document_index['WORDCOUNT'].values())
        document_number = len(document_length)
        avgdl = sum(document_length) / len(document_length)
        for term in index.document_index.keys():
            if term == 'WORDCOUNT':
                continue
            sum_tfcw = 0
            for docu in index.document_index[term].keys():
                sum_tfcw += log(index.get_term_freq(term, docu) / (1 - BM25_b + BM25_b * index.get_document_length(docu)
                                                                   / avgdl) + 1) / index.get_document_freq(term)
            k1 = 0
            while k1 < 3000:
                if BM25_preset[k1] > sum_tfcw:
                    break
            k1 = k1 / 1000
            for docu in index.document_index[term].keys():
                score = log((document_number + 1) / index.get_document_freq(term)) * (
                    (k1 + 1) * index.get_term_freq(term, docu) / (
                    k1 + (1 - BM25_b + BM25_b * index.get_document_length(docu) / avgdl) +
                    index.get_term_freq(term, docu)) + BM25_delta)
                set_index(term, docu, "BM25TLS", score)

    @staticmethod
    def search_by_words(word_list):
        return [1, 2, 3]

    @staticmethod
    def query_expansion(word_list, nrel=10, nexp=2):
        return word_list.append('example')

    @staticmethod
    def get_relative_article(arxivID_list, nart=10):
        return [1, 2, 3, 4, 5]
