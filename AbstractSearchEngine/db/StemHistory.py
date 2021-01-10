import json


def update_stem_history(word, stemmed_word):
    """
    please design a table that has two columns, column 1 is stemmed word while column 2 is original word.
    """
    file = open('stemhistory.txt', 'r')
    k_v = json.load(file)
    file.close()
    k_v[stemmed_word] = word
    file = open('stemhistory.txt', 'w')
    json.dump(file, k_v)
    file.close()


def query_origin_word(stemmed_word):
    file = open('stemhistory.txt', 'r')
    k_v = json.load(file)
    file.close()
    if stemmed_word in k_v:
        return k_v[stemmed_word]
    else:
        return ""
