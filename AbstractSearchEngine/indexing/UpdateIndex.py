import json

import django
from django.conf import settings
import os



os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'arXiv_explorer.settings')
django.setup()
from AbstractSearchEngine.db.StemHistory import update_stem_history
from AbstractSearchEngine.db.TermFreqPersistence import get_term_freq, set_term_freq

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


def update_index(document_list=None):
    if document_list is None:
        all_documnents = get_all_arxiv_documents()
    else:
        all_documnents = []
        for i in document_list:
            all_documnents.append(get_arxiv_document_by_id(i))
    index = BaseIndex()
    prev_term_index = get_term_freq("WORDCOUNT")
    index.document_index["WORDCOUNT"] = prev_term_index
    tt={}
    for doc in tqdm(all_documnents):
        terms = preprocess(doc.abstract.lower())
        for term in terms:
            stem_term = stem(term)
            tt[stem_term]=term
            if stem_term not in index.document_index:
                prev_term_index = get_term_freq(stem_term)
                index.document_index[stem_term] = prev_term_index
            index.add_term(stem_term, doc.arxiv_id)
            index.add_term("WORDCOUNT", doc.arxiv_id)
    for i in tqdm(list(tt.keys())):
        update_stem_history(i, tt[i])
    save_index(index)
    BM25.update_index(index)


if __name__ == "__main__":
    a=BM25.search_by_words([stem("increase")])
