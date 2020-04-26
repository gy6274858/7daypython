from __future__ import print_function
import requests
import json
import re #正则匹配
import time #时间处理模块
import jieba #中文分词
import numpy as np
import matplotlib

import matplotlib.pyplot as plt
import matplotlib.font_manager as font_manager
from PIL import Image
from wordcloud import WordCloud  #绘制词云模块
import paddlehub as hub


# 请求爱奇艺评论接口，返回response信息
def getMovieinfo(url):
    '''
    请求爱奇艺评论接口，返回response信息
    参数  url: 评论的url
    :return: response信息
    '''
    session = requests.Session()
    headers = {
        "User_Agent": "Mozilla/5.0",
        "Accept": "application/json",
        "Referer": "http:/m.iqiyi.com/v_19rqriflzg.html",
        "Origin": "http://m.iqiyi.com",
        "Host": "sns-comment,iqiyi.com",
        "Connection": "keep-alive",
        "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
        "Accept-Encoding": "gzip, deflate, br"
    }
    response = session.get(url, headers=headers)
    if response.status_code == 200:
        return response.text

    return None


# 解析json数据，获取评论
def saveMovieInfoToFile(lastId, arr):
    '''
    解析json数据，获取评论
    参数  lastId:最后一条评论ID  arr:存放文本的list
    :return: 新的lastId
    '''
    url = "https://sns-comment.iqiyi.com/v3/comment/get_comments.action?agent_type=118&agent_version=9.11.5&business_type=17&content_id=15068699100&page=&page_size=10&types=time&last_id="
    url += str(lastId)
    responseTxt = getMovieinfo(url)
    responseJson = json.loads(responseTxt)
    comments = responseJson['data']['commnets']
    for val in comments:
        if 'content' in val.keys():
            print(val['content'])
            arr.append(val['content'])
        lastId = str(val['id'])
    return lastId

#去除文本中特殊字符
def clear_special_char(content):
    '''
    正则处理特殊字符
    参数 content:原文本
    return: 清除后的文本
    '''
    s = re.sub(r"</?(.+?)>|&nbsp;|\t|\r","",content)
    s = re.sub(r"\n"," ",s)
    s = re.sub(r"\*", "\\*", s)
    s = re.sub('[^u4e00-\u9fa5^a-z^A-Z^0-9]','',s)
    s = re.sub('[\001\002\003\004\005\006\007\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f\x10\x11\x12\x13\x14\x15\x16\x17\x18\x19\x1a]+', '', s)
    s = re.sub('[a-zA-Z]','',s)
    s = re.sub('^\d+(\.\d+)?$','',s)
    return s


def fenci(text):
    '''
    利用jieba进行分词
    参数 text:需要分词的句子或文本
    return：分词结果
    '''
    jieba.load_userdict('add_words.txt')
    seg = jieba.lcut(text, cut_all=False)

    return seg

def stopwordslist(file_path):
    '''
    创建停用词表
    参数 file_path:停用词文本路径
    return：停用词list
    '''
    stopwords = [line.strip() for line in open(file_path, encoding='UTF-8').readlines()]
    return stopwords


def movestopwords(sentence, stopwords, counts):
    '''
    去除停用词,统计词频
    参数 file_path:停用词文本路径 stopwords:停用词list counts: 词频统计结果
    return：None
    '''
    out = []
    for word in sentence:
        if word not in stopwords:
            if len(word) != 1:
                counts[word] = counts.get(word, 0) + 1

    return None


def drawcounts(counts, num):
    '''
    绘制词频统计表
    参数 counts: 词频统计结果 num:绘制topN
    return：none
    '''
    x_aixs = []
    y_aixs = []
    c_order = sorted(counts.items(), key=lambda x: x[1], reverse=True)
    for c in c_order[:num]:
        x_aixs.append(c[0])
        y_aixs.append(c[1])
    matplotlib.rcParams['font.sans-serif'] = ['SimHei']
    matplotlib.rcParams['axes.unicode_minus'] = False
    plt.bar(x_aixs, y_aixs)
    plt.title('词频统计结果')
    plt.show()

    return

def drawcloud(word_f):
    '''
    根据词频绘制词云图
    参数 word_f:统计出的词频结果
    return：none
    '''
    cloud_mask = np.array(Image.open('cloud.png'))
    st=set(["东西","这是"])
    wc=WordCloud(background_color='white',
    mask=cloud_mask,
    max_words=150,
    font_path='simhei.ttf',
    min_font_size=10,
    max_font_size=100,
    width=400,
    relative_scaling=0.3,
    stopwords=st
    )
    wc.fit_words(word_f)
    wc.to_file('pic.png')


def text_detection(text, file_path):
    '''
    使用hub对评论进行内容分析
    return：分析结果

    '''
    porn_detection_lstm = hub.Module(name="porn_detection_lstm")
    f = open('aqy.txt', 'r', encoding='utf-8')
    for line in f:
        if len(line.strip()) == 1:
            continue
        else:
            test_text.append(line)
    f.close()
    input_dict = {"text": test_text}
    results = porn_detection_lstm.detection(data=input_dict, use_gpu=True, batch_size=1)
    for index, item in enumerate(results):
        if item['porn_detection_key'] == 'porn':
            print(item['text'], ':', item['porn_probs'])


# 评论是多分页的，得多次请求爱奇艺的评论接口才能获取多页评论,有些评论含有表情、特殊字符之类的
# num 是页数，一页10条评论，假如爬取1000条评论，设置num=100
if __name__ == "__main__":
    num = 20
    lastID = '0'
    arr = []
    with open('aqy.txt', 'a', encoding='utf-8') as f:
        for i in range(num):
            lastID = saveMovieInfoToFile(lastID, arr)
            time.sleep(0.5)
        for item in arr:
            Item = clear_special_char(item)
            if Item.strip() != '':
                try:
                    f.write(Item + '\n')
                except Exception as e:
                    print('含有特殊字符')
    print('共爬取评论：', len(arr))
    f = open('aqy.txt', 'r', encoding='utf-8')
    counts = {}
    for line in f:
        words = fenci(line)
        stopwords = stopwordslist('cn_stopwords.txt')
        movestopwords(words, stopwords, counts)

    drawcounts(counts, 10)
    drawcloud(counts)
    f.close

    file_path = 'aqy.txt'
    test_text = []
    text_detection(test_text, file_path)

