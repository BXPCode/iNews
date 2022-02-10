from news.models import News, Tag, NewsTag, NewsSim
from datetime import datetime

from user.models import UserActionLog
from .textAnalysis import TextAnalysis


# 新闻处理
class NewsDeal:
    def __init__(self, news_id):
        self.news = News.objects.get(id=news_id)

    # 新闻数据更新
    def update_news_info(self, flag, user_id=1):
        # 浏览量更新
        if flag == 1:
            self.news.read_num += 1
            self.news.save()
        # 点赞量更新
        elif flag == 2:
            user_action_log = UserActionLog.objects.get(user_id_id=user_id, news_id_id=self.news.id)
            # 点赞，点赞量+1
            if user_action_log.vote:
                self.news.vote_num += 1
            # 取消点赞，点赞量-1
            else:
                self.news.vote_num -= 1
            self.news.save()
        # 评论更新
        elif flag == 3:
            self.news.comment_num += 1
            self.news.save()
        # 刷新新闻的热度
        elif flag == 4:
            # 计算新闻上传时间和当前时间的日期差
            timeSpan = (datetime.now().date() - self.news.create_time.date()).days
            # 根据 热度值=浏览量*0.1+点赞量*0.3+评论量*0.6-2的日期差的次方 计算新闻热度值
            self.news.hot_num = self.news.read_num * 0.1 + self.news.vote_num * 0.3 + self.news.comment_num * 0.6 - 2 ** timeSpan
            # 更新新闻信息表中的记录
            self.news.save()

    # 获取新闻点赞信息(templates中显示使用）
    def get_news_vote_info(self, user_id):
        # 在用户行为表中取出对该新闻的行为记录
        user_action_log = UserActionLog.objects.get(user_id_id=user_id, news_id_id=self.news.id)
        # 点赞按钮上的显示文本
        vote_content = ''
        # 如果已点赞
        if user_action_log.vote:
            # 按钮上应该显示“取消点赞”
            vote_content = '取消点赞'
        # 如果未点赞
        else:
            # 按钮上应该显示“点赞”
            vote_content = '点赞'
        # 返回显示文本
        return vote_content

    # 获取相似新闻
    def get_sim_news(self):
        # 该新闻相似度最高的10条新闻ID
        news_sim_ids = NewsSim.objects.filter(news_id_base_id=self.news.id).order_by('-sim_num')[:10]
        # 保存相似新闻的列表
        sim_news = []
        # 遍历这些新闻ID
        for news_sim_id in news_sim_ids:
            # 从新闻信息表中取出他们的详细信息
            news_temp = News.objects.get(id=news_sim_id.news_id_sim_id)
            # 添加到相似新闻列表中
            sim_news.append(news_temp)
        return  sim_news

    # 获取新闻标签
    def get_news_tag(self):
        # 如果该新闻含有标签
        try:
            # 从新闻标签表中取该新闻的所有标签ID
            tag_ids = self.news.newstag_set.all().values('tag_id_id')
            # 保存标签的列表
            tags = []
            # 遍历这些标签ID
            for tag_id in tag_ids:
                # 从标签表中取出这些标签的详细信息
                tag_temp = Tag.objects.get(id=tag_id['tag_id_id'])
                # 添加到标签列表中
                tags.append(tag_temp)
        # 否则，该新闻没有标签
        except Exception:
            # 标签列表置为空
            tags = None
        # 返回一个标签列表
        return tags

    # 计算新闻标签（新闻上传时操作）
    def cal_news_tag(self):
        # 对该新闻创建文本分析对象
        news_analysis = TextAnalysis(self.news.id)
        # 获取新闻关键词
        news_keywords = news_analysis.keywords
        print(news_keywords)
        # 获取数据库中设定的所有标签
        tags = Tag.objects.all()
        # 遍历这些标签
        for tag in tags:
            # 分离出每个标签的内涵中所有的关键词
            tag_content = tag.content.split(',')
            # 标签名称也是关键词
            tag_content.append(tag.name)
            # 遍历新闻的关键词
            for news_keyword in news_keywords:
                # 如果新闻关键词在标签关键词中
                if news_keyword[0] in tag_content:
                    # 将新闻加入到对应的标签中
                    try:
                        NewsTag.objects.get(news_id_id=self.news.id, tag_id_id=tag.id)
                    except Exception:
                        NewsTag.objects.create(news_id_id=self.news.id, tag_id_id=tag.id)
                    # 将权重值大于1的关键词插入到标签对应的内容表中，进一步丰富标签内涵
                    for n_word in news_keywords:
                        # 若标签权重大于1
                        if n_word[1] >= 1:
                            # 取出最新的标签内涵，防止重复插入
                            tag_content_temp = tag.content.split(',')
                            tag_content_temp.append(tag.name)
                            # 且关键词不在标签内涵中
                            if n_word[0] not in tag_content_temp:
                                # 将关键词加入到标签内涵中
                                tag = Tag.objects.get(id=tag.id)
                                tag.content = tag.content + ',' + n_word[0]
                                tag.save()
                        # 由于字典是按权重降序排列的，若有小于1的，直接退出循环
                        else:
                            break

    # 计算新闻相似度（新闻上传时操作）
    def cal_news_sim_num(self):
        print('cal news sim')
        # 对当前新闻创建文本分析对象
        news_analysis1 = TextAnalysis(self.news.id)
        # 获取当前新闻关键词
        set1 = set(news_analysis1.keywords)
        # 获取数据库中所有新闻记录
        news_all = News.objects.all()
        # 遍历所有新闻
        for news in news_all:
            # 对新闻创建文本分析对象
            news_analysis2 = TextAnalysis(news.id)
            # 如果是当前新闻
            if news.id == self.news.id:
                # 则跳过
                continue
            # 否则
            else:
                # 获取该新闻的关键词
                set2 = set(news_analysis2.keywords)
                # 计算两则新闻的杰卡德相似系数
                sim_num = float(len(set1 & set2) / len(set1 | set2))
                # 写入或更新到新闻相似度表中
                if sim_num:
                    try:
                        newsSim = NewsSim.objects.get(news_id_base_id=self.news.id, news_id_sim_id=news.id)
                        newsSim.sim_num = sim_num
                        newsSim.save()
                    except Exception:
                        NewsSim.objects.create(news_id_base_id=self.news.id, news_id_sim_id=news.id, sim_num=sim_num)

    # 新闻信息规范化-更新新闻摘要（新闻上传时操作）
    def update_news_abstract(self):
        # 新闻摘要为新闻正文的前40个字
        self.news.abstract = self.news.content[:40]
        # 为了显示统一，在最后加上省略号
        self.news.abstract = self.news.abstract + '...'
        self.news.save()
