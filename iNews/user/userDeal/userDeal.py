import math
from news.models import News
from user.models import User, UserRating, UserActionLog, UserSim, UserCommentLog, UserTag


# 用户处理模块

# 用户相似度计算（计算资源消耗巨大，定时更新）
def cal_user_sim():
    print('开始计算用户之间的相似度...')  # 测试时打印
    # 查询用户-新闻评分表中所有记录
    user_ratings = UserRating.objects.all()
    # 取出其中所有的新闻ID，去重
    news_s_id = user_ratings.values('news_id_id').distinct()
    # 用户和相似用户行为交集数字典
    count = dict()
    # 用户行为总数字典
    user_news_count = dict()
    # 按新闻ID遍历整个用户-新闻评分表
    for news_id in news_s_id:
        # 取出某条新闻下的所有用户（即新闻-用户的倒排表）
        news_users = UserRating.objects.filter(news_id_id=news_id['news_id_id'])
        # 用户数目，侧面反应该条新闻的热度
        users_num = news_users.count()
        # 遍历某条新闻下的所有用户
        for news_user in news_users:
            # 初始化用户行为总数
            user_news_count.setdefault(news_user.user_id_id, 0)
            # 用户行为总数+1
            user_news_count[news_user.user_id_id] += 1
            # 初始化用户和相似用户行为交集字典
            count.setdefault(news_user.user_id_id, {})
            # 把遍历某条新闻下所有用户
            for news_user_sim_user in news_users:
                # 初始化用户与相似用户的交集值
                count[news_user.user_id_id].setdefault(news_user_sim_user.user_id_id, 0)
                # 如果是当前用户
                if news_user.user_id_id == news_user_sim_user.user_id_id:
                    # 则跳过
                    continue
                # 交集值优化，采用 1/(log(1+|N(i)|)公式惩罚热门物品对相似度的影响
                count[news_user.user_id_id][news_user_sim_user.user_id_id] += 1 / math.log(1 + users_num)

    # 遍历用户和相似用户交集数字典
    for user_id, sim_users in count.items():
        # 对于每个用户，遍历相似用户及与其行为交集数
        for sim_user_id, cuv in sim_users.items():
            # 如果是当前用户
            if user_id == sim_user_id:
                # 则跳过
                continue
            # （余弦相似度）相似度值=交集值/(用户行为总数和相似用户行为总数）
            sim_value = cuv / math.sqrt(user_news_count[user_id] * user_news_count[sim_user_id])
            # 若该用户和相似用户曾经有过交集，则更新相似度值
            try:
                user_sim = UserSim.objects.get(user_id_base_id=user_id, user_id_sim_id=sim_user_id)
                user_sim.sim_value = sim_value
                user_sim.save()
            # 否则，需要创建用户-相似用户的记录
            except Exception:
                UserSim.objects.create(user_id_base_id=user_id, user_id_sim_id=sim_user_id, sim_value=sim_value)


# 用户处理类
class UserDeal:
    # 根据用户ID创建用户对象
    def __init__(self, user_id):
        self.user = User.objects.get(id=user_id)

    # 用户行为数据更新（浏览、点赞、评论）
    def update_user_action_log(self, news_id, flag, comment=''):
        # 浏览次数更新
        if flag == 1:
            # 若该用户曾经浏览过该新闻，对该新闻的浏览次数+1
            try:
                # 浏览量+1
                user_action_log = UserActionLog.objects.get(user_id_id=self.user.id, news_id_id=news_id)
                user_action_log.read_num += 1
                user_action_log.save()
            # 否则，首次访问需要创建用户-新闻行为记录
            except Exception:
                UserActionLog.objects.create(user_id_id=self.user.id, news_id_id=news_id, read_num=1)
        # 点赞更新，不需要try，因为点赞之前必定存在浏览记录
        elif flag == 2:
            user_action_log = UserActionLog.objects.get(user_id_id=self.user.id, news_id_id=news_id)
            # 点赞取反（点赞与取消点赞）
            user_action_log.vote = bool(1 - user_action_log.vote)
            user_action_log.save()
        # 评论更新，不需要try，因为评论之前必定存在浏览记录
        elif flag == 3:
            # 在用户评论记录中插入
            UserCommentLog.objects.create(user_id_id=self.user.id, news_id_id=news_id, comment=comment)
            # 评论量+1
            user_action_log = UserActionLog.objects.get(user_id_id=self.user.id, news_id_id=news_id)
            user_action_log.comment_num += 1
            user_action_log.save()
        self.cal_user_rating(news_id=news_id)

    # 用户行为数据更新（对标签的偏好值,通过浏览量反映）
    def update_user_tag_like_num(self, news_id):
        # 根据新闻ID去新闻表中中查询出该新闻
        news = News.objects.get(id=news_id)
        # 去新闻标签表中查询出该新闻的所有标签
        tags = news.newstag_set.values('tag_id_id')
        # 遍历这些标签
        for tag in tags:
            # 如果是用户喜爱的标签，对标签的浏览量+1
            try:
                user_tag_read_log = UserTag.objects.get(user_id_id=self.user.id, tag_id_id=tag['tag_id_id'])
                user_tag_read_log.read_num += 1
                user_tag_read_log.save()
            # 如果是用户不感兴趣的标签，则跳过
            except Exception:
                pass

    # 用户行为数据更新（根据行为数据，计算用户对新闻评分值,可以用作定时更新，用作系统修改时重新计算）
    def cal_user_rating(self, news_id):
        # 去用户行为表中取出用户对该新闻的行为记录
        user_action_log = UserActionLog.objects.get(user_id_id=self.user.id, news_id_id=news_id)
        # 用户对该新闻的评分值=评论数*6+点赞数*3+浏览次数*1
        rating_num = user_action_log.comment_num * 6 + user_action_log.vote * 3 + user_action_log.read_num
        # 若计算过该用户对该新闻的评分值，则更新评分值
        try:
            user_rating = UserRating.objects.get(user_id_id=self.user.id, news_id_id=news_id)
            user_rating.rating_num = rating_num
            user_rating.save()
        # 否则，在用户-新闻评分表中，创建一条新的记录
        except Exception:
            UserRating.objects.create(user_id_id=self.user.id, news_id_id=news_id, rating_num=rating_num)

    # 用户行为数据更新（根据行为数据，更新用户对新闻评分值，用作实时更新，在用户操作发生时调用）
    def update_user_rating(self, news_id, update_num):
        # 若计算过该用户对该新闻的评分值，则更新评分值
        try:
            user_rating = UserRating.objects.get(user_id_id=self.user.id, news_id_id=news_id)
            user_rating.rating_num += update_num
            user_rating.save()
        # 否则，在用户-新闻评分表中，创建一条新的记录
        except Exception:
            UserRating.objects.create(user_id_id=self.user.id, news_id_id=news_id, rating_num=update_num)
