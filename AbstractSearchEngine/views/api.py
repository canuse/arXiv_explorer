import datetime
import json
from ..models import *
from ..db.arXivDocument import *
from ..indexing.UnifiedSearch import *
from ..utils.preprocess import *
from ..utils.stemmer import *


def getDatial(request):
    """输入文章id，返回文章的metadata。代表用户点击，记录session

    Args:
        request (GET): arxivID：String，article的ID

    Returns:
        json: 该article的metadata，调用ORM接口查数据库
    """
    ret_dict = {}
    
    arxiv_id = request.GET.get("arxivID")
    arxiv_doc = get_arxiv_document_by_id(arxiv_id=arxiv_id)
    
    if arxiv_doc != None:
        request.session.set['last_read'] = arxiv_id
        
        ret_dict['arxiv_id'] = arxiv_doc.arxiv_id
        ret_dict['submitter'] = arxiv_doc.submitter
        ret_dict['authors'] = arxiv_doc.authors
        ret_dict['title'] = arxiv_doc.title
        ret_dict['comments'] = arxiv_doc.comments
        ret_dict['doi'] = arxiv_doc.doi
        ret_dict['report_no'] = arxiv_doc.report_no
        ret_dict['categories'] = arxiv_doc.categories
        ret_dict['journal_ref'] = arxiv_doc.journal_ref
        ret_dict['license'] = arxiv_doc.license
        ret_dict['abstract'] = arxiv_doc.abstract
        ret_dict['versions'] = arxiv_doc.versions
        ret_dict['update_date'] = arxiv_doc.update_date
        ret_dict['authors_parsed'] = arxiv_doc.authors_parsed
        
    return json.dump(ret_dict)


def getRecommendArticle(request):
    """输入文章id，返回一个list，包括推荐的id
    可以假设arxivID=“”时，利用用户浏览记录推荐，非空时按输入推荐。
    用户浏览记录可以用session/cookie储存，建议session，读教程。
    
    Args:
        request (GET): arxivID：String，article的ID

    Returns:
        list，最接近的文章的id（比如默认10个）
    """    
    arxiv_id = request.GET.get("arxivID")
    if arxiv_id == '':
        arxiv_id = request.session.get('last_read', '-1')
        # TODO: 新用户没有搜索记录
    return get_relative_article(arxiv_list=[arxiv_id], nart=10)  # TODO:参数含义


def query(request):
    """传入一个查询字符串，返回匹配到的文章id。
    
    Args:
        request (GET): queryString:String 查询的字符串
                        categories:String/Int 文章所属的领域，多个领域使用逗号分隔，例如"math.CO,quant-ph"
                        timeStart:String yyyymm 最早发表日期(含)，both included
                        timeEnd: String yyyymm 最晚发表日期(含)，both included
                        offset: int 起始位置(例如，offset=100,默认一页显示20条，那么返回搜索结果的第100-119项，方便前端分页。)

    Returns:
        json
        一个排序好的list，按相关性从高到低，最多count项。
        一个int，表示一共多少个结果。
        例：
        {[(article_id, title, abstract, authors, update_date)*20]，50}
        表示一共有50个搜索结果，本次查询返回的20个结果是上面显示的20个
    """   
    ret_list = []
    ret_dict = {'ret_list': ret_list, 'num': 0}
    
    # 解析request信息
    query_string_raw = request.GET.get("queryString")
    categories_raw = request.GET.get("categories")
    time_start_raw = timeConvert(request.GET.get("timeStart"))
    time_end_raw = timeConvert(request.GET.get("timeEnd"))
    offset = request.GET.get("offset")
    
    # 时间提取 # TODO:如果传入时间为空怎么办
    time_start_year = time_start_raw[:4]
    time_start_month = time_start_raw[-2:]
    time_end_year = time_end_raw[:4]
    time_end_month = time_end_raw[-2:]
    
    # category info extraction
    categories = categories_raw.split(',') # TODO: 空类别
    
    # preprocess and stemming
    query_string_list = [stem(query) for query in preprocess(query_string_raw)]
    
    # return arxiv_ids by search words
    arxiv_ids = search_by_words(word_list=query_string_list)
    
    # return arxiv_docs by arxiv_ids
    arxiv_docs = get_arxiv_document_by_ids(arxiv_ids)
    
    # 条件筛选
    for doc in arxiv_docs:
        flag = True
        
        # 使用文章类别筛选
        if (len(categories) == 0) or (doc.categories in categories):
            flag = flag and True
        else:
            flag = False
        
        # 使用发表年、月筛选
        # TODO:如果doc的update_date为空怎么办
        doc_year = doc.update_date.split('-')[0]
        doc_month = doc.update_date.split('-')[1]
        if (time_start_year == doc_year) and (time_start_month <= doc_month):
            flag = flag and True
        elif (time_end_year == doc_year) and (doc_month <= time_end_month):
            flag = flag and True
        elif time_start_year <= doc_year <= time_end_year:
            flag = flag and True
        else:
            flag = False
        
        if flag:
            ret_list.append((doc.article_id, doc.title,
                         doc.abstract, doc.authors, doc.update_date))
    
    ret_dict['num'] = len(ret_list)
    
    # 边界条件
    if len(ret_list) <= offset:
        ret_dict['ret_list'] = ret_list[:]
    elif offset < len(ret_list) <= (offset+20):
        ret_dict['ret_list'] = ret_list[offset:]
    else:
        ret_dict['ret_list'] = ret_list[offset:offset+20]
    
    return json.dump(ret_dict)


def queryExpansion(request):
    """传入一个查询字符串，返回一个list，为Query Explansion后的结果。
    
    Args:
        request (GET): queryString:String 查询的字符串
                                        注意处理传入为空的情况。
                        
    Returns:
        json
        一个list，包括QE后的字符串（比如默认10个）
        例如，输入 ”apple banana“，返回["apple banana fruit","apple banana orange".....]
    """
    ret_list = []
    
    # 解析request信息
    query_string_raw = request.GET.get("queryString")
    
    # preprocess and stemming
    query_string_list = [stem(query) for query in preprocess(query_string_raw)]

    # return query_string_expanded_list by search words
    query_string_expanded_list = query_expansion(
        word_list=query_string_list, nrel=10, nexp=2, allow_dup=True)#TODO:参数含义
    
    #TODO:是这么搞unstem么
    for query in query_string_expanded_list:
        words_unstem = ''
        words = query.split(' ')
        for w in words:
            words_unstem += unstem(w) + ' '
        ret_list.append(words_unstem[:-1])
    
    return ret_list