import datetime
import traceback
import json
from ..models import *
from ..db.arXivDocument import *
from ..db.getStemPair import *
from ..indexing.UnifiedSearch import *
from ..utils.preprocess import *
from ..utils.stemmer import *
from django.http import HttpResponse


def getDatial(request):
    """输入文章id，返回文章的metadata。代表用户点击，记录session

    Args:
        request (GET): arxivID：String，article的ID

    Returns:
        json: 该article的metadata，调用ORM接口查数据库
    """
    try:
        ret_dict = {}
        
        arxiv_id = request.GET.get("arxivID")
        arxiv_doc = get_arxiv_document_by_id(arxiv_id=arxiv_id)
        
        if arxiv_doc != None:
            # session initialization
            if 'last_read' not in request.session:
                request.session.set['last_read'] = []
            request.session.set['last_read'].append(arxiv_id)
            
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
            
        return HttpResponse(json.dumps(ret_dict))
    except Exception:
        traceback.print_exc()


def getRecommendArticle(request):
    """输入文章id，返回一个list，包括推荐的id
    可以假设arxivID=“”时，利用用户浏览记录推荐，非空时按输入推荐。
    用户浏览记录可以用session/cookie储存，建议session，读教程。
    
    Args:
        request (GET): arxivID：String，article的ID

    Returns:
        list，最接近的文章的id（比如默认10个）
    """    
    try:
        arxiv_id = request.GET.get("arxivID")
        
        if arxiv_id == '':
            arxiv_ids = request.session.get('last_read', [])[-10:0]
            if arxiv_ids == []:
                #TODO: random 10 articles
                pass
            else: #recommand by session
                pass
        else: #recommand by arxiv_id
            arxiv_ids = [arxiv_id]
            pass
        
        rec_arxiv_ids = get_relative_article(arxiv_list=arxiv_ids, nart=10)
        
        ret_list = []
        for rec_arxiv_id in rec_arxiv_ids:
            arxiv_doc = get_arxiv_document_by_id(arxiv_id=rec_arxiv_id)
            if arxiv_doc != None:
                tmp = {}
                tmp['arxiv_id'] = arxiv_doc.arxiv_id
                tmp['authors'] = arxiv_doc.authors
                tmp['title'] = arxiv_doc.title
                ret_list.append(tmp)
        
        return HttpResponse(json.dumps({'ret_list': ret_list}))
    except Exception:
        traceback.print_exc()


def judge_category(request_categories, article_category):
    """判断文章类别是否符合请求类别

    Args:
        request_categories (list): 请求类别
        article_categories (string): 文章类别

    Returns:
        boolean: 是否符合
    """
    
    # suggested by @canuse
    
    # default setting
    if len(request_categories) == 0:
        return False
    
    for req_category in request_categories:
        if req_category in article_category:
            return True
        
        if (req_category == 'other') and (article_category.count('.') != len(article_category.split())):
            return True

    return False


def query(request):
    """传入一个查询字符串，返回匹配到的文章id。
    
    Args:
        request (GET): queryString:String 查询的字符串
                        categories:String/Int 文章所属的领域，多个领域使用逗号分隔，例如"math.CO,quant-ph"
                        timeStart:String yyyy-mm 最早发表日期(含)，both included
                        timeEnd: String yyyy-mm 最晚发表日期(含)，both included
                        offset: int 起始位置(例如，offset=100,默认一页显示20条，那么返回搜索结果的第100-119项，方便前端分页。)

    Returns:
        json
        一个排序好的list，按相关性从高到低，最多count项。
        一个int，表示一共多少个结果。
        例：
        {[(arxiv_id, title, abstract, authors, update_date)*20]，50}
        表示一共有50个搜索结果，本次查询返回的20个结果是上面显示的20个
    """   
    try:
        ret_list = []
        ret_dict = {'ret_list': ret_list, 'num': 0}
        
        # 解析request信息
        query_string_raw = request.GET.get("queryString")
        categories_raw = request.GET.get("categories")
        time_start_raw = request.GET.get("timeStart")
        time_end_raw = request.GET.get("timeEnd")
        offset = int(request.GET.get("offset"))
        
        # 时间提取 
        time_start_year = time_start_raw[:4]
        time_start_month = time_start_raw[-2:]
        time_end_year = time_end_raw[:4]
        time_end_month = time_end_raw[-2:]
        
        # category info extraction
        categories = categories_raw.split(',')
        
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
            if judge_category(categories, doc.categories):
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
                ret_list.append((doc.arxiv_id, doc.title,
                            doc.abstract, doc.authors, doc.update_date))
        
        ret_dict['num'] = len(ret_list)
        
        # 边界条件
        if len(ret_list) <= offset:
            ret_dict['ret_list'] = ret_list[:]
        elif offset < len(ret_list) <= (offset+20):
            ret_dict['ret_list'] = ret_list[offset:]
        else:
            ret_dict['ret_list'] = ret_list[offset:offset+20]
        
        return HttpResponse(json.dumps(ret_dict))
    except Exception:
        traceback.print_exc()


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
    try:
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
        
        return HttpResponse(json.dumps({'ret_list':ret_list}))

    except Exception:
        traceback.print_exc()

  
def inputCompletion(request):
    """传入一个输入字符串，返回一个list，为输入补全后的结果。
    
    Args:
        request (GET): queryString:String 查询的字符串
                                        注意处理传入为空的情况。
                        
    Returns:
        json
        一个list，包括QE后的字符串（比如默认10个）
        例如，输入 ”apple b“，返回["apple banana", "apple book",.....]
    """
    try:
        ret_list = []       
        ret_query = ""
        # 解析request信息
        query_string_raw = request.GET.get("queryString")
        query_string_list = query_string_raw.split(" ")
        ret_query = " ".join(query_string_list[0:-1])
        last_word = query_string_list[-1]
        
        #获取补全后的单词
        completion_word_list = get_stem_pair_by_key(last_word)
        
        #拼接query
        num = 10 if len(completion_word_list) > 10 else len(completion_word_list)
        for i in range(num):
            ret_list.append(ret_query + " " + word)

        return HttpResponse(json.dumps({'ret_list':query_string_list}))

    except Exception:
        traceback.print_exc()
