from abc import ABC, abstractmethod


class BaseAlgorithm(ABC):
    """
    Interface of algorithm class, every indexing algorithm should implement the following functions.
    """
    def __init__(self):
        pass

    @staticmethod
    @abstractmethod
    def update_index(index):
        """
        Update the index (by using the given index, whose format is BaseIndex).
        Only update part of the whole index, to save time.
        """
        return False

    @staticmethod
    @abstractmethod
    def search_by_words(word_list):
        """
        searching using the index and algorithm
        word_list: a list of stemmed, tokenized word
        return: a list of tuple, each tuple contains the arxiv_id and relevance
        example: [('0901.0001',12.34),('0902.0002',23.45)]
        """
        return []

    @staticmethod
    @abstractmethod
    def query_expansion(word_list, nrel=10, nexp=2, allow_dup=True):
        """
        expand the query (to get more result)
        word_list: a list of stemmed, tokenized word
        nrel: number of documents considered as relative
        nexp: number of extend query word
        allow_dup: allow duplicate in expanded query words
        return: a list of word, containing original word list and expanded words
        example: input: ['appl', 'orang'] output: ['appl', 'orang', 'banana', 'fruit']
        """
        return []

    @staticmethod
    @abstractmethod
    def get_relative_article(arxivID_list, nart=10):
        """
        Get relevance articles of the given arxiv_id list.
        arxivID_list: a list of arxiv id
        nart: number of relative articles
        return: a list of tuple, containing arxiv_id and relevance score
        """
        return []


class BaseIndex:
    """
    Class of indexing, recording DF and TF.
    use BaseIndex.document_index (a dict) to store appearance of terms, keys are stemmed word and value is another dict,
    containing appeared document and appear times.
    use key 'WORDCOUNT' to store word count of every article.
    example of BaseIndex.document_index:
    {
        'appl':{'0901.0001':1,'0901.0002':2,'0901.0005':10},
        'egg':{'0902.0001':1,'0905.0002':2},...
        'WORDCOUNT':{'0901.0001':100,'0901.0002':200,...},...
    }
    """
    def __init__(self):
        self.document_index = {}

    def add_term(self, term, arxiv_id):
        """
        add term to the index.
        """
        if term not in self.document_index:
            self.document_index[term] = {arxiv_id: 1}
        else:
            if arxiv_id not in self.document_index[term]:
                self.document_index[term][arxiv_id] = 1
            else:
                self.document_index[term][arxiv_id] += 1

    def get_document_freq(self, term):
        """
        return the document frequency of a term
        """
        if term in self.document_index:
            return len(self.document_index[term].keys())
        else:
            return 0

    def get_term_freq(self, term, arxiv_id):
        """
        return the term frequency in a document
        """
        if term in self.document_index:
            if arxiv_id in self.document_index[term]:
                return self.document_index[term][arxiv_id]
            else:
                return 0
        else:
            return 0

    def get_document_length(self, arxiv_id):
        """
        return the length of the given article
        """
        if "WORDCOUNT" not in self.document_index:
            return 0
        if arxiv_id in self.document_index["WORDCOUNT"]:
            return self.document_index["WORDCOUNT"][arxiv_id]
        else:
            return 0
