from django.test import TestCase
from django.test.client import Client
from .models import *

# Create your tests here.

class ArxivDocumentTests(TestCase):

    def test_getDatial():
        from api import getDatial
        
        b = ArxivDocument(arxiv_id='abc',
                        title='hello world')
        b.save()
        
        c = Client()
        req = c.get('abc')
        
        assert(b.get(req) == 'hello world')
