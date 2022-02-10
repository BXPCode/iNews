from django.core.paginator import Paginator
from django.http import HttpResponseRedirect
from django.shortcuts import render
from news.models import News
from user.models import User, UserActionLog, UserCommentLog
from news.newsDeal.newsDeal import NewsDeal
from news.newsRec.newsRec import NewsRec, base_time_rec, base_hot_num_rec
from user.userDeal.userDeal import UserDeal
import time


# Create your views here.
def index_view(request):
    # 顶部信息，返回当前的日期
    data = time.strftime('%Y-%m-%d ', time.localtime(time.time()))
    # 首页页面跳转逻辑
    # 若用户已登录，浏览器中存放着Cookies或session值，则用户免登陆直接跳转首页
    s_username = request.session.get('username')
    s_uid = request.session.get('uid')
    c_username = request.COOKIES.get('username')
    c_uid = request.COOKIES.get('uid')
    if (s_username and s_uid) or (c_username and c_uid):
        # 获取用户信息
        username = request.session.get('username')
        user = User.objects.get(username=username)
        # 推荐列表处理
        news_rec = NewsRec(user_id=user.id)
        # 全部新闻
        news_all = News.objects.all()
        # 最新新闻
        news_recent = base_time_rec()
        # 最热新闻
        news_hot = base_hot_num_rec()
        # 基于标签的推荐
        news_your_tag = news_rec.base_tag_rec()
        # 基于协同过滤的推荐
        news_userCF = news_rec.base_user_cf_rec()
        # 分页显示，每页显示10条新闻
        paginator = Paginator(news_userCF, per_page=10)
        if request.GET.get('page', 0):
            page_num = request.GET.get('page', 0)
        else:
            page_num = 1
        c_page = paginator.get_page(int(page_num))
        # 若session值不存在
        if s_username and s_username:
            pass
        else:
            # 回写session
            request.session['username'] = c_username
            request.session['uid'] = c_uid
        # 转向首页
        return render(request, 'index/index.html', locals())
    # 转向登录页面
    return HttpResponseRedirect('/user/login')


# 浏览新闻
def content_view(request):
    # 顶部信息，返回当前的日期
    data = time.strftime('%Y-%m-%d ', time.localtime(time.time()))
    # 获取用户和新闻信息
    username = request.session.get('username')
    user = User.objects.get(username=username)
    news_id = request.GET['news_id']
    news = News.objects.get(id=news_id)
    # 创建用户和新闻处理对象
    user_deal = UserDeal(user_id=user.id)
    news_deal = NewsDeal(news_id=news_id)
    # 点击阅览新闻
    # 首先更新用户新闻日志
    # 然后获取新闻的各项信息
    if request.method == 'GET':
        # 新闻浏览量跟新
        news_deal.update_news_info(flag=1)
        # 用户行为日志表浏览量更新
        user_deal.update_user_action_log(news_id=news_id, flag=1)
        # 更新用户对标签的偏好值
        user_deal.update_user_tag_like_num(news_id=news_id)
        # 获取新闻标签信息
        tags = news_deal.get_news_tag()
        # 获取该用户对新闻点赞信息
        vote_content = news_deal.get_news_vote_info(user_id=user.id)
        is_vote = UserActionLog.objects.get(user_id_id=user.id, news_id_id=news_id)
        # 获取该新闻的所有评论
        news_comment = UserCommentLog.objects.filter(news_id_id=news_id)
        # 获取该新闻相似文章
        sim_news = news_deal.get_sim_news()
        return render(request, 'index/content.html', locals())

    # 发表评论
    elif request.method == 'POST':
        # 新闻表数据更新
        news_deal.update_news_info(flag=3)
        # 用户行为日志表更新
        user_deal.update_user_action_log(news_id=news_id, flag=3, comment=request.POST['comment'])
        # 刷新页面
        url = '/content?news_id=' + news_id
        return HttpResponseRedirect(url)


# 查看各类别下的新闻
def cate_view(request):
    # 顶部信息，返回当前的日期
    data = time.strftime('%Y-%m-%d ', time.localtime(time.time()))
    # 获取用户信息
    username = request.session.get('username')
    user = User.objects.get(username=username)
    if request.method == 'GET':
        # 推荐列表处理
        news_rec = NewsRec(user_id=user.id)
        # 最新新闻
        news_recent = base_time_rec()
        # 最热新闻
        news_hot = base_hot_num_rec()
        # 基于标签的推荐
        news_your_tag = news_rec.base_tag_rec()
        # 获取当前点击的类别
        cate_id = request.GET['cate_id']
        # 根据类别显示不同新闻
        if int(cate_id) == 10:
            news_cate = News.objects.order_by('-hot_num')[:100]
        else:
            news_cate = News.objects.filter(cate_id=cate_id).order_by('-create_time')[:100]
        # 分页显示
        paginator = Paginator(news_cate, per_page=10)
        if request.GET.get('page', 0):
            page_num = request.GET.get('page', 0)
        else:
            page_num = 1
        c_page = paginator.get_page(int(page_num))
        return render(request, 'index/cate.html', locals())


# 点赞
def vote_change_view(request):
    # 获取用户信息
    username = request.session.get('username')
    user = User.objects.get(username=username)
    # 获取新闻信息
    news_id = request.GET['news_id']
    # 更新用户行为日志中的点赞行为
    user_deal = UserDeal(user_id=user.id)
    user_deal.update_user_action_log(news_id=news_id, flag=2)
    # 修改新闻表
    news_deal = NewsDeal(news_id)
    news_deal.update_news_info(flag=2, user_id=user.id)

