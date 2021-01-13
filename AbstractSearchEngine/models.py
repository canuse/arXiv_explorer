from django.db import models


class ArxivDocument(models.Model):
    arxiv_id = models.TextField(unique=True, blank=True, null=True)
    submitter = models.TextField(blank=True, null=True)
    authors = models.TextField(blank=True, null=True)
    title = models.TextField(blank=True, null=True)
    comments = models.TextField(blank=True, null=True)
    doi = models.TextField(blank=True, null=True)
    report_no = models.TextField(blank=True, null=True)
    categories = models.TextField(blank=True, null=True)
    journal_ref = models.TextField(blank=True, null=True)
    license = models.TextField(blank=True, null=True)
    abstract = models.TextField(blank=True, null=True)
    versions = models.TextField(blank=True, null=True)  # This field type is a guess.
    update_date = models.TextField(blank=True, null=True)
    authors_parsed = models.TextField(blank=True, null=True)  # This field type is a guess.

    class Meta:
        managed = False
        db_table = 'arxiv_document'


class ArxivRank(models.Model):
    word = models.CharField(max_length=20, blank=True, null=True)
    paper = models.CharField(max_length=20, blank=True, null=True)
    algorithm = models.CharField(max_length=20, blank=True, null=True)
    rank_value = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'arxiv_rank'
        unique_together = (('word', 'paper', 'algorithm'),)


class StemPair(models.Model):
    key = models.CharField(primary_key=True, max_length=20)
    value = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'stem_pair'
