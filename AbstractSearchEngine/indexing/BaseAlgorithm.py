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


class BaseIndex(ABC):
    def __init__(self):
        self.document_index = {}

    @abstractmethod
    def add_term(self, term, arxiv_id):
        if term not in self.document_index:
            self.document_index[term] = {arxiv_id: 1}
        else:
            if arxiv_id not in self.document_index[term]:
                self.document_index[term][arxiv_id] = 1
            else:
                self.document_index[term][arxiv_id] += 1

    @abstractmethod
    def get_document_freq(self, term):
        if term in self.document_index:
            return len(self.document_index[term].keys())
        else:
            return 0

    @abstractmethod
    def get_term_freq(self, term, arxiv_id):
        if term in self.document_index:
            if arxiv_id in self.document_index[term]:
                return self.document_index[term][arxiv_id]
            else:
                return 0
        else:
            return 0
