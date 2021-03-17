import datetime
import json

import django
from django.conf import settings
import os
import unicodedata

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'arXiv_explorer.settings')
django.setup()
from AbstractSearchEngine.models import ArxivDocument
import os
import sys
import time

import requests
from argparse import ArgumentParser
import multiprocessing
from xml.dom.minidom import parseString
import json
import logging


def parse_metadata(xml_metadata):
    xml_tree = parseString(xml_metadata)
    id = xml_tree.getElementsByTagName('id')[0].childNodes[0].nodeValue
    submitter = xml_tree.getElementsByTagName('submitter')[0].childNodes[0].nodeValue
    authors = xml_tree.getElementsByTagName('authors')[0].childNodes[0].nodeValue
    title = unicodedata.normalize("NFKD", xml_tree.getElementsByTagName('title')[0].childNodes[0].nodeValue)
    if len(xml_tree.getElementsByTagName('comments')) == 0:
        comments = None
    else:
        comments = xml_tree.getElementsByTagName('comments')[0].childNodes[0].nodeValue
    if len(xml_tree.getElementsByTagName('doi')) == 0:
        doi = None
    else:
        doi = xml_tree.getElementsByTagName('doi')[0].childNodes[0].nodeValue
    if len(xml_tree.getElementsByTagName('journal_ref')) == 0:
        journal_ref = None
    else:
        journal_ref = xml_tree.getElementsByTagName('journal-ref')[0].childNodes[0].nodeValue
    if len(xml_tree.getElementsByTagName('report_no')) == 0:
        report_no = None
    else:
        report_no = xml_tree.getElementsByTagName('report-no')[0].childNodes[0].nodeValue
    categories = xml_tree.getElementsByTagName('categories')[0].childNodes[0].nodeValue
    if len(xml_tree.getElementsByTagName('license')) == 0:
        license = None
    else:
        license = xml_tree.getElementsByTagName('license')[0].childNodes[0].nodeValue
    abstract = unicodedata.normalize("NFKD", xml_tree.getElementsByTagName('abstract')[0].childNodes[0].nodeValue)
    raw_versions = xml_tree.getElementsByTagName('version')
    versions = []
    for index, i in enumerate(raw_versions):
        versions.append({'version': "v{0}".format(index), 'created': i.childNodes[0].childNodes[0].nodeValue})
    try:
        update_date = xml_tree.getElementsByTagName('datestamp')[0].childNodes[0].nodeValue
    except:
        update_date = str(datetime.date.today())
    authors_parsed = []
    proc_a = authors.replace('\n', '').replace(' and ', '').replace(',and ', '')
    for i in proc_a.split(','):
        tmp = i.strip().split()
        if len(tmp) == 0:
            authors_parsed.append(["", "", ""])
        if len(tmp) == 1:
            authors_parsed.append([i.strip().split()[0].strip(), '', ''])
        if len(tmp) == 2:
            authors_parsed.append([i.strip().split()[0].strip(), i.strip().split()[1].strip(), ''])
        if len(tmp) > 2:
            authors_parsed.append(
                [i.strip().split()[0].strip(), i.strip().split()[1].strip(), i.strip().split()[2].strip()])
    if ArxivDocument.objects.filter(arxiv_id=id).exists():
        return
    ad = ArxivDocument(arxiv_id=id, submitter=submitter, authors=authors, title=title, comments=comments, doi=doi,
                       report_no=report_no, categories=categories, journal_ref=journal_ref, license=license,
                       abstract=abstract, versions=json.dumps(versions), update_date=update_date,
                       authors_parsed=json.dumps(authors_parsed))
    ad.save()


def id2month(i: int):
    a = (i - 101) % 12
    b = (i - 102) // 12
    if a != 0:
        return "{:02}{:02}".format(b, a)
    else:
        return "{:02}{:02}".format(b, 12)


def download_metadata():
    with open('arxiv_download.log', 'r') as fin:
        current_arxiv_id = fin.read()
    download_arxiv_id_list = []

    raw_submit_number = requests.get("https://arxiv.org/stats/get_monthly_submissions").content.decode()
    submit_number = [int(x.split(',')[1]) for x in raw_submit_number.split()[1:]]
    start_month = current_arxiv_id.split('.')[0]
    start_id = int(start_month[:2]) * 12 + int(start_month[2:]) + 101
    if len(submit_number) == start_id + 1:
        # this month is not finished
        start_arxiv_id = int(current_arxiv_id.split('.')[1])
        end_arxiv_id = submit_number[start_id]
        for i in range(start_arxiv_id, end_arxiv_id + 1):
            download_arxiv_id_list.append(start_month + '.{:05}'.format(i))
    else:
        start_arxiv_id = int(current_arxiv_id.split('.')[1])
        end_arxiv_id = submit_number[start_id]
        for i in range(start_arxiv_id + 1, end_arxiv_id + 1):
            download_arxiv_id_list.append(start_month + '.{:05}'.format(i))
        start_arxiv_id = 1
        end_arxiv_id = submit_number[start_id + 1]
        for i in range(start_arxiv_id, end_arxiv_id + 1):
            download_arxiv_id_list.append(id2month(start_id + 1) + '.{:05}'.format(i))

    max_try = 2000
    finished = []
    last = download_arxiv_id_list[-1]

    while len(download_arxiv_id_list) > 0 and max_try > 0:
        arxiv_id = download_arxiv_id_list.pop()
        if ArxivDocument.objects.filter(arxiv_id=arxiv_id).exists():
            print("INFO:arxiv_id {0} already exist".format(arxiv_id))
            continue
        try:
            xml_metadata = requests.get(
                "http://export.arxiv.org/oai2?verb=GetRecord&identifier=oai:arXiv.org:{0}&metadataPrefix=arXivRaw".format(
                    arxiv_id), timeout=5).content.decode()
            if "idDoesNotExist" in xml_metadata:
                continue
            else:
                finished.append(arxiv_id)
            parse_metadata(xml_metadata)
            print("INFO:arxiv_id {0} finish".format(arxiv_id))
        except:
            print("ERROR:error in downloading metadata of arxiv_id {0}".format(arxiv_id))
            max_try -= 1
            download_arxiv_id_list.insert(0, arxiv_id)
    with open('arxiv_download.log', 'w') as fout:
        fout.write(last)
    return finished


if __name__ == "__main__":
    fin = download_metadata()

