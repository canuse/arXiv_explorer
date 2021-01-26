from django.db import models

# model for all matedata of Arxiv paper
class ArxivDocument(models.Model):
    arxiv_id = models.TextField(unique=True, blank=True, null=True) # ArXiv ID (can be used to access the paper)
    submitter = models.TextField(blank=True, null=True) # Who submitted the paper
    authors = models.TextField(blank=True, null=True) # Authors of the paper
    title = models.TextField(blank=True, null=True) # Title of the paper
    comments = models.TextField(blank=True, null=True) # Additional info, such as number of pages and figures
    doi = models.TextField(blank=True, null=True) # [https://www.doi.org](Digital Object Identifier)
    report_no = models.TextField(blank=True, null=True)
    categories = models.TextField(blank=True, null=True) # Categories / tags in the ArXiv system
    journal_ref = models.TextField(blank=True, null=True)
    license = models.TextField(blank=True, null=True)
    abstract = models.TextField(blank=True, null=True) # The abstract of the paper
    versions = models.TextField(blank=True, null=True) # A version history
    update_date = models.TextField(blank=True, null=True)
    authors_parsed = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'arxiv_document'

"""
example:{
    "id": string "0704.0001"
    "submitter": string "Pavel Nadolsky"
    "authors": string "C. Bal\'azs, E. L. Berger, P. M. Nadolsky, C.-P. Yuan"
    "title": string "Calculation of prompt diphoton production cross sections at Tevatron and LHC energies"
    "comments":string"37 pages, 15 figures; published version"
    "journal-ref": string "Phys.Rev.D76:013009,2007"
    "doi": string "10.1103/PhysRevD.76.013009"
    "report-no": string "ANL-HEP-PR-07-12"
    "categories": string "hep-ph"
    "license": NULL
    "abstract": string "  A fully differential calculation in perturbative quantum ..."
    "versions":[
        0:{
            "version": string "v1"
            "created": string "Mon, 2 Apr 2007 19:18:42 GMT"
        }
        1:{...}
    ]
    "update_date": string "2008-11-26"
    "authors_parsed":[
        0:[
            0: string "Balázs"
            1: string "C."
            2: string ""
        ]
        1:[...]
        2:[...]
    ]
"""

# model for the value of a specific ranking algorithm of term-document pairs
class ArxivRank(models.Model):
    word = models.TextField(blank=True, null=True) # a term
    paper = models.TextField(blank=True, null=True) # which paper the term appears (use the ArXiv ID)
    algorithm = models.TextField(blank=True, null=True) # name of the algorithm (eg: TFIDF / BM25)
    rank_value = models.FloatField(blank=True, null=True) # ranking value of the algorithm

    class Meta:
        managed = False
        db_table = 'arxiv_rank'

"""
example:{
    "word": string "finit"
    "paper": string "0906.1352"
    "algorithm": string "BM25TLS"
    "rank_value": float 4.18660680409255
    }
"""

# model for after-stemming term and original word pairs
class StemPair(models.Model):
    key = models.TextField(primary_key=True) # word after stemming
    value = models.TextField(blank=True, null=True) # original word

    class Meta:
        managed = False
        db_table = 'stem_pair'

"""
example:{
    "key": string "rienc"
    "value": string "rience"
    }
"""

# model for document frequency and term frequency of a word
class TermAppearance(models.Model):
    word = models.TextField(blank=True, null=True) # a word
    document_freq = models.IntegerField(blank=True, null=True) # document frequency (number of documents the word appears)
    term_freq = models.TextField(blank=True, null=True) # term frequency (frequency of the word appears in each document)

    class Meta:
        managed = False
        db_table = 'term_appearance'

"""
example:{
    "word": string "rienc"
    "document_freq": int 101
    "term_freq":{
        "math-ph/9805011": int 5
        "2009.07997": int 6
        "cs/0701113": int 7
    }
"""