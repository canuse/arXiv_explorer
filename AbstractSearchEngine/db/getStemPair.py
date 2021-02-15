from AbstractSearchEngine.models import StemPair

def get_stem_pair_by_key(key_head):
    # return the document that matched key_head, or None if not found.
    return StemPair.objects.filter(key.startswith(key_head))

