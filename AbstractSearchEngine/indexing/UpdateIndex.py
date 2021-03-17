import json

import django
from django.conf import settings
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'arXiv_explorer.settings')
django.setup()
from AbstractSearchEngine.indexing.UnifiedSearch import query_expansion
from AbstractSearchEngine.arxiv_spider.arxiv_spider import download_metadata
from AbstractSearchEngine.db.IndexPersistence import delete_all_index
from AbstractSearchEngine.db.StemHistory import update_stem_history
from AbstractSearchEngine.db.TermFreqPersistence import get_term_freq, set_term_freq
from AbstractSearchEngine.db.IndexPersistence import delete_all_index as delete_BM25_all_index
from AbstractSearchEngine.db.arXivDocument import get_all_arxiv_documents, get_arxiv_document_by_id
from AbstractSearchEngine.indexing.BM25 import BM25
from AbstractSearchEngine.indexing.BaseAlgorithm import BaseIndex
from AbstractSearchEngine.utils.preprocess import preprocess
from AbstractSearchEngine.utils.stemmer import stem
from tqdm import tqdm
import time
import multiprocessing


def save_index(index):
    for term in tqdm(index.document_index):
        set_term_freq(term, index.document_index[term])


def update_all_index():
    """
    rebuild the index
    """

    import gc
    all_documnents = get_all_arxiv_documents()
    index = BaseIndex()
    tt = {}
    for doc in tqdm(all_documnents):
        terms = preprocess(doc.title.lower() + ' ' + doc.abstract.lower())
        for term in terms:
            stem_term = stem(term)
            tt[stem_term] = term
            index.add_term(stem_term, doc.arxiv_id)
            index.add_term("WORDCOUNT", doc.arxiv_id)
    del all_documnents
    gc.collect()
    #for i in tqdm(list(tt.keys())):
    #    update_stem_history(tt[i], i)
    #save_index(index)
    delete_BM25_all_index(key3="BM25TLS")
    BM25.update_index(index)


def update_index(document_list):
    """
    update index with given articles
    """
    all_documnents = []
    for i in tqdm(document_list):
        all_documnents.append(get_arxiv_document_by_id(i))
    print(document_list)
    index = BaseIndex()
    prev_term_index = get_term_freq("WORDCOUNT")
    index.document_index["WORDCOUNT"] = prev_term_index
    tt = {}
    for doc in tqdm(all_documnents):
        terms = preprocess(doc.title.lower() + ' ' + doc.abstract.lower())
        for term in terms:
            stem_term = stem(term)
            tt[stem_term] = term
            if stem_term not in index.document_index:
                prev_term_index = get_term_freq(stem_term)
                index.document_index[stem_term] = prev_term_index
            index.add_term(stem_term, doc.arxiv_id)
            index.add_term("WORDCOUNT", doc.arxiv_id)
    for i in tqdm(list(tt.keys())):
        update_stem_history(tt[i], i)
    save_index(index)
    BM25.update_index(index, delete=True)


def update_index_memory_optimize(document_list):
    """
    update index with optimized memory usage
    """
    all_documnents = []
    for i in tqdm(document_list):
        all_documnents.append(get_arxiv_document_by_id(i))
    print(document_list)
    unique_term = set()
    # prev_term_index = get_term_freq("WORDCOUNT")
    # index.document_index["WORDCOUNT"] = prev_term_index
    tt = {}
    index = BaseIndex()
    for doc in tqdm(all_documnents):

        terms = preprocess(doc.title.lower() + ' ' + doc.abstract.lower())
        for term in terms:
            stem_term = stem(term)
            tt[stem_term] = term
            unique_term.add(stem_term)
            index.add_term(stem_term, doc.arxiv_id)
            index.add_term("WORDCOUNT", doc.arxiv_id)
    del all_documnents
    for term in tqdm(index.document_index):
        prev_term_index = get_term_freq(term)
        for docid in index.document_index[term]:
            prev_term_index[docid] = index.document_index[term][docid]
        set_term_freq(term, prev_term_index)
        del prev_term_index
    del index
    for i in tqdm(list(tt.keys())):
        update_stem_history(tt[i], i)

    wc = get_term_freq("WORDCOUNT")
    for i in tqdm(unique_term):
        #print(i)
        index = BaseIndex()
        index.document_index["WORDCOUNT"] = wc
        index.document_index[i] = get_term_freq(i)
        BM25.update_index(index, delete=True)
        del index


def update_data_norm():
    import unicodedata
    all_docu = get_all_arxiv_documents()
    for i in tqdm(all_docu):
        i.title = unicodedata.normalize("NFKD", i.title)
        i.abstract = unicodedata.normalize("NFKD", i.abstract)
        i.save()


if __name__ == "__main__":
    a = download_metadata()
    '''a=[]
    for i in range(9560, 10000):
        a.append("2102.0" + str(i))
    for i in range(10000, 10107):
        a.append("2102." + str(i))
    update_index_memory_optimize(a)'''
    update_index_memory_optimize(a)
