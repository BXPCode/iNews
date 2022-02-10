from django.contrib import admin
from news.models import News
from news.newsDeal.newsDeal import NewsDeal
from news.newsDeal.pictureCut import picture_deal


# 新闻后台管理类
class NewsManager(admin.ModelAdmin):
    # 设定显示的列
    list_display = ['id', 'title', 'author', 'cate_id', 'picture', 'create_time']

    # 覆盖保存方法，在上传新闻后触发新闻数据处理操作
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        # 最新插入的新闻
        news_last = News.objects.last()
        # 为其创建新闻处理类
        news_deal = NewsDeal(news_last.id)
        # 裁剪新闻图片
        picture_deal()
        # 计算新闻摘要
        news_deal.update_news_abstract()
        # 计算新闻标签
        news_deal.cal_news_tag()
        # 计算新闻相似度
        news_deal.cal_news_sim_num()


# 在admin中注册
admin.site.register(News, NewsManager)
