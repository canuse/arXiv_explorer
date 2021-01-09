from abc import ABC


class BaseAlgorithm(ABC):
    def __init__(self):
        pass

    def search_by_words(self, word_list):
        return []

    def query_expansion(self, word_list, nrel=10, nexp=2):
        return []

    def get_relative_article(self, arxivID_list, nart=10):
        return []
