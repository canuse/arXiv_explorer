from math import log

from AbstractSearchEngine.db.IndexPersistence import get_index, set_index, delete_all_index, get_all_index, \
    IndexBulkInsert
from AbstractSearchEngine.indexing.BaseAlgorithm import BaseAlgorithm, BaseIndex
from AbstractSearchEngine.utils.stemmer import unstem
from tqdm import tqdm
from functools import lru_cache

algorithm_name = "TFIDF"


class TFIDF(BaseAlgorithm):
    def __init__(self):
        super().__init__()
        algorithm = "TFIDF"

    @staticmethod
    def update_index(index: BaseIndex, delete=False):
        """
        Update index with the given index.
        work around: The average document length is not updated for index not affected, because the number of documents
        is huge (~2M), and every day only ~500 documents are updated (0.025%), the average document length will be
        almost irrivant.
        However, it is recommended to update all index every month, or quarter, to gain better result.
        work around2: The document number is changing, which will affect the value of IDF. In our approach, the N is set
        to 2M.
        """

        document_amount = len(index.document_index['WORDCOUNT'].values())
        index_insert_handler = IndexBulkInsert(save_iter=10000)

        for term in list(index.document_index.keys()):
            if term == 'WORDCOUNT':
                continue
            if delete:
                delete_all_index(key3=algorithm_name, key2=term)
            df = len(index.document_index[term].keys())
            for docu in index.document_index[term].keys():
                tf = index.document_index[term][docu]
                score = (1 + log(tf, 10)) * log(document_amount / df, 10)
                index_insert_handler.insert((docu, term, "TFIDF", score))
        index_insert_handler.save()

    @staticmethod
    def __search_doc_by_term(term):
        term_document = get_all_index(key2=term, key3=algorithm_name)
        result = {}
        for i in term_document:
            # [i.paper, i.word, i.algorithm, i.rank_value]
            result[i[0]] = i[-1]
        return result

    @staticmethod
    def search_by_words(word_list):
        """
        searching using the index and algorithm
        word_list: a list of stemmed, tokenized word
        return: a list of tuple, each tuple contains the arxiv_id and relevance
        example: [('0901.0001',12.34),('0902.0002',23.45)]
        """

        result = {}
        for word in word_list:
            documents = TFIDF.__search_doc_by_term(word)
            for doc in documents:
                if doc not in result:
                    result[doc] = documents[doc]
                else:
                    result[doc] += documents[doc]
        final_score = []
        for doc in result:
            final_score.append((doc, result[doc]))
        final_score.sort(key=lambda x: x[-1], reverse=True)
        return final_score[:100]

    @staticmethod
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
        raw_article_t = TFIDF.search_by_words(word_list)[:nrel]
        raw_article = [i[0] for i in raw_article_t]
        length = len(word_list)
        expand_word = TFIDF.get_article_topic(raw_article, nexp + len(word_list))
        if allow_dup:
            for i in expand_word:
                word_list.append(i)
        else:
            for i in expand_word:
                if i not in word_list:
                    word_list.append(i)
        return word_list[:length + nexp]

    @staticmethod
    def get_article_topic(arxivID_list, nexp):
        word_rank = {}
        word_list = []
        for docu in arxivID_list:
            wr = TFIDF.__search_article_by_doc(docu)
            for word in wr:
                if word in word_rank:
                    word_rank[word] += wr[word]
                else:
                    word_rank[word] = wr[word]
        new_word_rank = [(word, word_rank[word]) for word in word_rank]
        new_word_rank.sort(key=lambda x: x[-1], reverse=True)
        for i in range(min(nexp, len(new_word_rank))):
            word_list.append(new_word_rank[i][0])
        return word_list

    @staticmethod
    @lru_cache(16)
    def __search_article_by_doc(docu):
        # in development, set lru cache to 1
        term_document = get_all_index(key1=docu, key3=algorithm_name)
        result = {}
        for doc in term_document:
            # [i.paper, i.word, i.algorithm, i.rank_value]
            result[doc[1]] = doc[-1]
        return result

    @staticmethod
    def get_relative_article(arxivID_list, nart=10):
        """
        Get relevance articles of the given arxiv_id list.
        arxivID_list: a list of arxiv id
        nart: number of relative articles
        return: a list of tuple, containing arxiv_id and relevance score
        """
        topic_term = TFIDF.get_article_topic(arxivID_list, 10)
        result = TFIDF.search_by_words(topic_term)
        ret = []
        cnt = 0
        for doc in result:
            if doc[0] not in arxivID_list:
                ret.append(doc)
                cnt += 1
            if cnt > 10:
                break
        return ret[:10]
