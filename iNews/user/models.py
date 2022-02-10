from django.db import models
from news.models import News, Tag


# Create your models here.
# 用户信息表
class User(models.Model):
    username = models.CharField('用户名', max_length=16, unique=True)
    password = models.CharField('密码', max_length=32)


# 用户关注领域的标签表以及浏览量（侧面反应偏好值）
class UserTag(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    tag_id = models.ForeignKey(Tag, on_delete=models.CASCADE)
    read_num = models.FloatField('浏览量', default=0)


# 用户行为日志
class UserActionLog(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    news_id = models.ForeignKey(News, on_delete=models.CASCADE)
    read_num = models.IntegerField('浏览', default=0)
    vote = models.BooleanField('点赞', default=False)
    comment_num = models.IntegerField('浏览', default=0)


# 用户评论记录
class UserCommentLog(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    news_id = models.ForeignKey(News, on_delete=models.CASCADE)
    comment = models.CharField('评论', max_length=128, default='')


# 用户评分表
class UserRating(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    news_id = models.ForeignKey(News, on_delete=models.CASCADE)
    rating_num = models.IntegerField('评分', default=0)


# 用户相似度表
class UserSim(models.Model):
    user_id_base = models.ForeignKey(User, on_delete=models.CASCADE, )
    user_id_sim = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_sim', )
    sim_value = models.FloatField('用户相似度', default=0)
