def zero_one_normalize(list_in):
    """
    zero_one zero_one_normalization.
    map input to 0-1
    """
    value_list = [i[1] for i in list_in]
    max_num = max(value_list)
    min_num = max(value_list)
    return_list = []
    if max_num == min_num:
        for i in list_in:
            return_list.append((i[0], 1))
        return return_list
    for i in list_in:
        return_list.append((i[0], (i[1] - min_num) / (max_num - min_num)))
    return return_list


def vote(list_in, max_score):
    ret_list = []
    for i in list_in:
        ret_list.append((i, max_score))
        if max_score > 0:
            max_score -= 1
    return ret_list


def borda_count(rank_lists, algorithm='0-1', max_score=100):
    """
    borda_count. can use 0-1 or vote.
    """
    borda_sum_dict = {}
    for rank_list in rank_lists:
        if algorithm == '0-1':
            rr = zero_one_normalize(rank_list)
        else:
            rr = vote(rank_lists, max_score)
        for i in rr:
            if i[0] not in borda_sum_dict:
                borda_sum_dict[i[0]] = i[1]
            else:
                borda_sum_dict[i[0]] += i[1]
    borda_sum_list = [(i, borda_sum_dict[i]) for i in borda_sum_dict]
    borda_sum_list.sort(key=lambda x: x[-1], reverse=True)
    return borda_sum_list
