from abc import ABC, abstractmethod


class BaseAlgorithm(ABC):
    def __init__(self):
        pass

    @staticmethod
    @abstractmethod
    def update_index():
        return False

    @staticmethod
    @abstractmethod
    def search_by_words(word_list):
        return []

    @staticmethod
    @abstractmethod
    def query_expansion(word_list, nrel=10, nexp=2):
        return []

    @staticmethod
    @abstractmethod
    def get_relative_article(arxivID_list, nart=10):
        return []
