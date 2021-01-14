from .models import *
import datetime,json

def getDatial(request):
    """输入文章id，返回文章的metadata

    Args:
        request (GET): arxivID：String，article的ID

    Returns:
        list: 该article的metadata，调用ORM接口查数据库
    """
    ret_list = []
    
    arxiv_id = request.GET.get("arxivID")
    arxiv_doc = ArxivDocument.objects.get(arxiv_id=arxiv_id)
    
    # TODO: 
    # 1. ORM接口存储在.Meta的什么地方
    ret_list.append(arxiv_doc.metadata)
    return ret_list


def getRecommendArticle(request):
    """输入文章id，返回一个list，包括推荐的id
    可以假设arxivID=“”时，利用用户浏览记录推荐，非空时按输入推荐。
    用户浏览记录可以用session/cookie储存，建议session，读教程。
    
    Args:
        request (GET): arxivID：String，article的ID

    Returns:
        list，最接近的文章的id（比如默认10个）
    """
    ret_list = []
    
    arxiv_id = request.GET.get("arxivID")
    if arxiv_id == '':
        # TODO:
        # 0. session什么时候存？存什么？
        # 1. session读取什么内容？
        pass
    else: 
        arxiv_doc = ArxivDocument.objects.get(arxiv_id=arxiv_id)
        # TODO:
        # 1. 如何根据文章id，返回“推荐的文章”、“最近接受的文章”
        pass
    
    return ret_list


def timeConvert(date: str) -> datetime:
    """时间转换

    Args:
        date (str): yymmdd

    Returns:
        datetime: python datetime
    """
    assert(isinstance(date, str), True)
    assert(len(date)==6)
    
    year, month, day = int(date[0:2]), int(date[2:4]), int(date[4:6])
    year += 1900 if year >= 21 else 2000
    
    return datetime(year, month, day)


def query(request):
    """传入一个查询字符串，返回匹配到的文章id。
    
    Args:
        request (GET): queryString:String 查询的字符串
                        categories:String/Int 文章所属的领域，多个领域使用逗号分隔，例如"math.CO,quant-ph"
                        timeStart:String yymmdd 最早发表日期，both included
                        timeEnd: String yymmdd 最晚发表日期，both included
                        offset: int 起始位置(例如，offset=100,默认一页显示20条，那么返回搜索结果的第100-119项，方便前端分页。)

    Returns:
        json
        一个排序好的list，按相关性从高到低，最多count项。
        一个int，表示一共多少个结果。
        例：
        {[1,2,3,4,5,6,7,8,9,10，11，12，13，14，15，16，17，18，19，20]，50}
        表示一共有50个搜索结果，本次查询返回的20个结果是上面显示的20个
    """    
    ret_list = []
    ret_dict = {'outcome': ret_list, 'num': 0}
    
    query_string = request.GET.get("queryString")
    categories_raw = request.GET.get("categories")
    time_start = timeConvert(request.GET.get("timeStart"))  # TODO: included or not
    time_end = timeConvert(request.GET.get("timeEnd"))  # TODO: included or not
    offset = request.GET.get("offset")
    
    # TODO:
    # 1. 发表时间字段是哪个？如果是update_data，可否使用models.DateField()
    # 2. 如何根据“查询字符串”查询文章？
    
    categories = categories_raw.split(',')
    
    arvix_docs = ArxivDocument.objects.filter(categories__in=categories)

    
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
    query_string = request.GET.get("queryString")

    # TODO:
    # 1. 如何进行query补全
    
    return ret_list
