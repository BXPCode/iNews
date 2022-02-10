import math
from django.db.models import Sum
from iNews.settings import K_NUM
from news.models import NewsTag, News
from news.newsDeal.newsDeal import NewsDeal
from user.models import User, UserSim, UserRating


# 基于新闻上传时间推荐
def base_time_rec():
    # 最新新闻20条
    return News.objects.order_by('-create_time')[:20]


# 基于新闻热度值推荐
def base_hot_num_rec():
    # 计算新闻热度
    news_all = News.objects.all()
    for news in news_all:
        news_deal = NewsDeal(news.id)
        news_deal.update_news_info(flag=4)
    # 最热新闻20条
    return News.objects.order_by('-hot_num')[:20]


# 新闻推荐类
class NewsRec:
    def __init__(self, user_id):
        self.user = User.objects.get(id=user_id)

    # 基于标签的推荐
    def base_tag_rec(self):
        # 用户的标签
        user_tag = self.user.usertag_set.all().values('tag_id_id')
        # 用户标签set
        user_tag_set = set()
        for user_t in user_tag:
            user_tag_set.add(user_t['tag_id_id'])
        # 筛选出100条含有用户感兴趣的标签的新闻ID
        news_ids = NewsTag.objects.filter(tag_id_id__in=user_tag).values('news_id_id')[:100]
        # 用户浏览过的新闻集合
        user_action_log = self.user.useractionlog_set.values('news_id_id')
        # 用户浏览过的新闻总数
        user_action_total = self.user.usertag_set.aggregate(Sum('read_num'))
        # 用户浏览过的标签总数
        user_tag_read_all = self.user.usertag_set.all()
        # 新闻喜爱值
        news_rate_num = dict()
        # 遍历含有用户感兴趣的标签的新闻ID
        for news_id in news_ids:
            # 如果用户没有浏览过该新闻
            if news_id not in user_action_log:
                # 每条新闻对应的标签
                news_tag = NewsTag.objects.filter(news_id_id=news_id['news_id_id']).values('tag_id_id')
                # 新闻标签集合
                news_tag_set = set()
                for news_t in news_tag:
                    news_tag_set.add(news_t['tag_id_id'])
                # 用户浏览这些标签的次数
                tag_read = user_tag_read_all.filter(tag_id_id__in=news_tag).aggregate(Sum('read_num'))
                # 用户标签和该新闻标签的杰卡德相似系数
                u = float(len(user_tag_set & news_tag_set) / len(user_tag_set | news_tag_set))
                # 对该新闻的标签的偏好值的总和=浏览该新闻含有标签的次数总和/该用户总的浏览次数
                v = float(1 + tag_read['read_num__sum'] / (1 + user_action_total['read_num__sum']))
                # 该新闻的标签总数
                news_tag_num = NewsTag.objects.filter(news_id_id=news_id['news_id_id']).count()
                # 用户对该新闻的预测评分值=对该新闻的标签的偏好值的总和*用户标签和该新闻标签的杰卡德相似系数/log(1+该新闻的标签总数)
                news_rate_num[news_id['news_id_id']] = float(u * v / math.log(1 + news_tag_num))
        # 按预测评分值降序排列
        news_your_tag_dict = dict(sorted(news_rate_num.items(), key=lambda x: x[1], reverse=True)[:20])
        news_your_tag_list = list(news_your_tag_dict)
        news_your_tag = News.objects.filter(id__in=news_your_tag_list)
        # 返回推荐列表
        return news_your_tag

    # 协同过滤的推荐
    def base_user_cf_rec(self, k=2, num=20):
        # 取出当前的K值
        with open(K_NUM, 'r') as file_object:
            k = int(file_object.read())
        # 推荐结果
        result = dict()
        # 按相似度降序排序选取前K个用户
        sim_users = UserSim.objects.filter(user_id_base_id=self.user.id).order_by('-sim_value')[:k]
        # 遍历这些相似用户
        for sim_user in sim_users:
            # 相似用户的评分数据
            user_ratings = UserRating.objects.filter(user_id_id=sim_user.user_id_sim_id)[:num]
            # 遍历这些评分数据
            for user_rating in user_ratings:
                # 如果用户已经有对该新闻的评分数据，表示已经浏览过，则不推荐
                try:
                    UserRating.objects.get(user_id_id=self.user.id, news_id_id=user_rating.news_id_id)
                # 否则，累加进用户对该新闻的预测评分值
                except Exception:
                    result.setdefault(user_rating.news_id_id, 0)
                    result[user_rating.news_id_id] += sim_user.sim_value * user_rating.rating_num
        # 按用户的预测评分值降序排序
        news_userCF_dict = dict(sorted(result.items(), key=lambda x: x[1], reverse=True)[:num])
        news_userCF_list = list(news_userCF_dict)
        # 取新闻表中查询出这些新闻的详细信息
        news_userCF = News.objects.filter(id__in=news_userCF_list)
        # 推荐系统冷启动处理，切换式混合推荐，
        # 如果新用户刚注册时没有相似用户，无法进行协同过滤推荐，给它展示基于标签的推荐，
        # 若基于标签的也没有的话，给他展示热点新闻
        if news_userCF.count() >= 10:
            print('news cf rec')
            return news_userCF
        elif self.base_tag_rec():
            print('news you tag')
            return self.base_tag_rec()
        else:
            return base_hot_num_rec()
