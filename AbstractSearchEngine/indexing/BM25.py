from AbstractSearchEngine.db.IndexPersistence import get_index, set_index
from AbstractSearchEngine.indexing.BaseAlgorithm import BaseAlgorithm


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
