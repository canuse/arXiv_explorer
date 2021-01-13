from AbstractSearchEngine.models import StemPair
# StemPair model has 2 columns: key -> word after stemming / value -> original word

def update_stem_history(word, stemmed_word):
    """
    please design a table that has two columns, column 1 is stemmed word while column 2 is original word.
    """
    if StemPair.objects.filter(key=stemmed_word).exists():
        # already have the stemmed word pair, update the value
        temp = StemPair.objects.get(key=stemmed_word)
        temp.value = word
        temp.save()
    else:
        # create a new pair
        temp = StemPair(
            value=word,
            key=stemmed_word
        )
        temp.save()


def query_origin_word(stemmed_word):
    # return the latest original word
    return StemPair.objects.get(key=stemmed_word).value
