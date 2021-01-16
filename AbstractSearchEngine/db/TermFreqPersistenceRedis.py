import redis

r_term_freq = redis.StrictRedis(host='localhost', port=6379, db=1)


def delete_all_index():
    r_term_freq.flushdb()


def set_term_freq(term, appear_dict):
    r_term_freq.delete(term)
    r_term_freq.hmset(term, appear_dict)


def get_term_documents_freq(term):
    return int(r_term_freq.hlen(term))


def get_document_term_freq(term, document):
    return int(r_term_freq.hget(term, document))


def get_document_number():
    return get_term_documents_freq("WORDCOUNT")


def get_average_document_length():
    total = r_term_freq.hgetall("WORDCOUNT").values()
    return sum([int(i) for i in total]) / len(total)


def get_document_length(docu):
    return int(r_term_freq.hget("WORDCOUNT", docu))


def get_all_document_term(term):
    return [x.decode() for x in r_term_freq.hkeys(term)]


def get_term_freq(term):
    tmp = r_term_freq.hgetall(term)
    ret = {}
    for i in tmp:
        ret[i.decode()] = int(tmp[i])
    return ret
