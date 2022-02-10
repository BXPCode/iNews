import os

import jieba.analyse

from iNews.settings import STOP_WORDS
from news.models import News, Tag, NewsTag, NewsSim


class TextAnalysis:
    def __init__(self, news_id):
        self.news = News.objects.get(id=news_id)
        self.newsKeywords = self.get_news_keywords()
        self.keywords = self.get_keywords()

    # 调用结巴分词获取每篇文章的关键词（非TF-IDF，按词频统计）
    def get_news_keywords(self):
        # 精确模式分词
        news_cut = jieba.cut(self.news.content+self.news.author+self.news.abstract, cut_all=False)
        # 加载停用词表
        stopwords = [line.strip() for line in open(STOP_WORDS).readlines()]
        # 去除停用词
        content_words = []
        for word in news_cut:
            if word not in stopwords and word != '\n':
                content_words.append(word)
        # 去重
        # 同时统计词汇频率
        word = dict()
        for m_word in content_words:
            word[m_word] = word.get(m_word, 0) + 1
        sort_words = sorted(word.items(), key=lambda x: x[1], reverse=True)[:10]
        # 关键词保存为列表
        keywords = []
        for s_word in sort_words:
            keywords.append(s_word[0])
        # 返回关键词
        return keywords

    # 调用结巴分词获取每篇文章的关键词,结合TF-IDF算法
    def get_keywords(self):
        keywords = jieba.analyse.extract_tags(
            # 新闻特征文本=新闻标题+新闻作者+新闻摘要
            self.news.title + self.news.author + self.news.abstract,
            # 选取前10个关键词
            topK=10,
            # 显示权重
            withWeight=True,
            # 提取地名、名词、动名词、动词
            allowPOS=('ns', 'n', 'vn', 'v')
        )
        # 返回关键词
        return keywords




