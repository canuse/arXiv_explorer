from AbstractSearchEngine.models import StemPair

def get_stem_pair_by_key(key):
    # return the document that matched key, or None if not found.
    if StemPair.objects.filter(key = key).exists():
        return StemPair.objects.get(key = key)
    else:
        return None
