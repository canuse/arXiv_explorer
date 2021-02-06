from math import log

from AbstractSearchEngine.db.IndexPersistence import get_index, set_index, delete_all_index, get_all_index, \
    IndexBulkInsert
from AbstractSearchEngine.indexing.BaseAlgorithm import BaseAlgorithm, BaseIndex
from AbstractSearchEngine.utils.stemmer import unstem
from tqdm import tqdm

BM25_b = 0.3
BM25_delta = 1
BM25_preset = [0] + [(x / 1000) / ((x / 1000) - 1) * log((x / 1000)) if x != 1000 else 1 for x in range(1, 5000)]
BM25_N = 2000000


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
        """
        Update index with the given index.
        work around: The average document length is not updated for index not affected, because the number of documents
        is huge (~2M), and every day only ~500 documents are updated (0.025%), the average document length will be
        almost irrivant.
        However, it is recommended to update all index every month, or quarter, to gain better result.
        work around2: The document number is changing, which will affect the value of IDF. In our approach, the N is set
        to 2M.
        """
        document_length = list(index.document_index['WORDCOUNT'].values())
        document_number = len(document_length)
        avgdl = sum(document_length) / len(document_length)
        index_insert_handler = IndexBulkInsert(save_iter=10000)
        for term in tqdm(list(index.document_index.keys())):
            if term == 'WORDCOUNT':
                continue
            sum_tfcw = 0
            for docu in index.document_index[term].keys():
                sum_tfcw += log(index.get_term_freq(term, docu) / (1 - BM25_b + BM25_b * index.get_document_length(docu)
                                                                   / avgdl) + 1) / index.get_document_freq(term)
            k1 = 0
            while k1 < 5000:
                if BM25_preset[k1] > sum_tfcw:
                    break
                k1 += 1
            k1 = k1 / 1000
            for docu in index.document_index[term].keys():
                score = log(BM25_N / index.get_document_freq(term)) * (
                    (k1 + 1) * index.get_term_freq(term, docu) / (
                    k1 * (1 - BM25_b + BM25_b * index.get_document_length(docu) / avgdl) +
                    index.get_term_freq(term, docu)) + BM25_delta)
                # set_index(docu, term, "BM25TLS", score)
                index_insert_handler.insert((docu, term, "BM25TLS", score))
        index_insert_handler.save()

    @staticmethod
    def search_by_words(word_list):
        """
        please refer to the base function to see comment
        """
        all_document = {}
        union_document = set()
        for term in word_list:
            term_document = get_all_index(key2=term, key3="BM25TLS")
            all_document[term] = {}
            for i in term_document:
                union_document.add(i[0])
                all_document[term][i[0]] = i[3]
        total_score = []
        for arxiv_id in union_document:
            score = 0
            for term in word_list:
                if arxiv_id in all_document[term]:
                    score += all_document[term][arxiv_id]
                else:
                    score += 0
            total_score.append((arxiv_id, score))
        total_score.sort(key=lambda x: x[-1], reverse=True)
        return total_score[:100]

    @staticmethod
    def query_expansion(word_list, nrel=10, nexp=2, allow_dup=True):
        raw_article_t = BM25.search_by_words(word_list)[:nrel]
        raw_article = [i[0] for i in raw_article_t]
        length = len(word_list)
        expand_word = BM25.get_article_topic(raw_article, 100)
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
            term_document = get_all_index(key1=docu, key3="BM25TLS")
            for i in term_document:
                if i[1] in word_rank:
                    word_rank[i[1]] += i[3]
                else:
                    word_rank[i[1]] = i[3]
        new_word_rank = [(i, word_rank[i]) for i in word_rank]
        new_word_rank.sort(key=lambda x: x[-1], reverse=True)
        for i in range(min(nexp, len(new_word_rank))):
            word_list.append(new_word_rank[i][0])
        return word_list

    @staticmethod
    def get_relative_article(arxivID_list, nart=10):
        topic_term = BM25.get_article_topic(arxivID_list, 10)
        result = BM25.search_by_words(topic_term)
        ret = []
        cnt = 0
        for i in result:
            if i[0] not in arxivID_list:
                ret.append(i)
                cnt += 1
            if cnt > 10:
                break
        return ret[:10]
