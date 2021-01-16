from AbstractSearchEngine.models import TermAppearance
import json


def set_term_freq(term, appear_dict):
    document_freq = len(appear_dict)
    ta = TermAppearance(word=term, document_freq=document_freq, term_freq=json.dumps(appear_dict))
    ta.save()


def get_term_documents_freq(term):
    try:
        temp = TermAppearance.objects.get(word=term)
        return len(json.loads(temp.term_freq))
    except:
        return 0


def get_document_term_freq(term, document):
    try:
        temp = TermAppearance.objects.get(word=term)
        return json.loads(temp.term_freq)[document]
    except:
        return 0


def get_term_freq(term):
    return json.loads(TermAppearance.objects.get(word=term).term_freq)


def delete_all_index():
    # 删除表里面所有东西
    pass
