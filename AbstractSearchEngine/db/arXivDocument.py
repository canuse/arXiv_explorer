from AbstractSearchEngine.models import ArxivDocument


# ArxivDocument model gives all the metadata:
# arxiv_id / submitter / authors / title / comments / doi / report_no / categories /
# journal_ref / license / abstract / versions / update_date / authors_parsed

# the following 2 functions return all the metadata
def get_all_arxiv_documents():
    # return all document in the database, including arxiv_id and abstract.
    # return type: QuerySet
    return ArxivDocument.objects.all()


def get_arxiv_document_by_id(arxiv_id):
    # return the document that matched arxiv_id, or None if not found.
    if ArxivDocument.objects.filter(arxiv_id=arxiv_id).exists():
        return ArxivDocument.objects.get(arxiv_id=arxiv_id)
    else:
        return None
