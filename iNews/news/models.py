from django.db import models


# 新闻类别表
class Cate(models.Model):
    name = models.CharField('类别名', max_length=64, )

    def __str__(self):
        return '{}'.format(self.name)


# 新闻信息表
class News(models.Model):
    title = models.CharField('标题', max_length=64,default='', )
    author = models.CharField('作者', max_length=64, default='', )
    abstract = models.CharField('摘要', max_length=128, default='', )
    content = models.TextField('内容', default='')
    picture = models.ImageField('配图', default='news.jpg')
    create_time = models.DateTimeField('创建时间', auto_now_add=True, )
    cate_id = models.ForeignKey(Cate, on_delete=models.CASCADE, )
    read_num = models.IntegerField('浏览量', default=0)
    vote_num = models.IntegerField('点赞量', default=0)
    comment_num = models.IntegerField('评论量', default=0)
    hot_num = models.FloatField('热度值', default=0)

    def __str__(self):
        return '{}'.format(self.title)


# 新闻相似度表
class NewsSim(models.Model):
    # 首先获得水果模型中外键指向的表中对象：
    # 然后通过子表中自定义的外键获取子表的所有信息：
    news_id_base = models.ForeignKey(News, on_delete=models.CASCADE, )
    news_id_sim = models.ForeignKey(News, on_delete=models.CASCADE, related_name='news_sim', )
    sim_num = models.FloatField('新闻相似度', default=0)


# 标签表
class Tag(models.Model):
    name = models.CharField('标签名', max_length=64, default='')
    content = models.TextField('标签内容', default='')


# 新闻标签表
class NewsTag(models.Model):
    tag_id = models.ForeignKey(Tag, on_delete=models.CASCADE)
    news_id = models.ForeignKey(News, on_delete=models.CASCADE)
