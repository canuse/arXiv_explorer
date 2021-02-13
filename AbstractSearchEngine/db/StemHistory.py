from AbstractSearchEngine.models import StemPair
# StemPair model has 2 columns: key -> word after stemming / value -> original word

def update_stem_history(word, stemmed_word):
    """
    please design a table that has two columns, column 1 is stemmed word while column 2 is original word.
    """
    try:
        tt = StemPair.objects.get(key=stemmed_word)
        tt.value = word
        tt.save()
    except:
        ta = StemPair(value=word, key=stemmed_word)
        ta.save()


def query_origin_word(stemmed_word):
    # return the latest original word
    try:
        return StemPair.objects.get(key=stemmed_word).value
    except:
        return ""

def auto_complete_query(prefix):
    """
    Auto complete the query by the input prefix.
    :param prefix: the prefix of a input word
    :return value: a list of stemmed words that match the prefix
    """
    candidate_words = []
    try:
        temp = StemPair.objects.filter(value__startswith=prefix)
        for i in temp:
            candidate_words.append(i.value)
        return candidate_words
    except:
        return []
