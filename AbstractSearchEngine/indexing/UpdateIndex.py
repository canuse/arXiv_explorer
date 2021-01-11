from AbstractSearchEngine.db.arXivDocument import get_all_arxiv_documents
from AbstractSearchEngine.indexing.BM25 import BM25
from AbstractSearchEngine.indexing.BaseAlgorithm import BaseIndex
from AbstractSearchEngine.utils.preprocess import preprocess
from AbstractSearchEngine.utils.stemmer import stem


def update_index():
    all_documnents = get_all_arxiv_documents()
    index = BaseIndex()
    for doc in all_documnents:
        terms = preprocess(doc.abstract)
        for term in terms:
            index.add_term(stem(term), doc.arxiv_id)
            index.add_term("WORDCOUNT", doc.arxiv_id)
    BM25.update_index(index)

