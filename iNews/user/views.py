from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
import hashlib
from .models import User, UserTag
from news.models import Tag


# Create your views here.
# 用户注册页面
def register_view(request):
    # GET请求方式：打开用户注册页面
    if request.method == 'GET':
        # 取出所有标签
        tags = Tag.objects.all()
        # 创建新的tag字典（包含id）
        Tags = []
        # 为了标签在templates的CSS显示，需要加入id项
        id = ['One', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine', 'Ten', 'Eleven', 'Twelve']
        i = 0
        for tag in tags:
            Tags.append({'id': tag.id, 'name': tag.name, 'label': id[i]})
            i += 1
        # 返回用户注册页面
        return render(request, 'user/register.html', locals())
    # POST请求方式：提交注册请求
    elif request.method == 'POST':
        # 用户名
        username = request.POST['username']
        # 密码
        password_1 = request.POST['password_1']
        # 确认密码
        password_2 = request.POST['password_2']
        # 标签选择
        tags = request.POST.getlist('checkbox_list')
        # 比较密码与确认密码，如果不一致，返回注册错误信息
        if password_1 != password_2:
            return HttpResponse('两次密码输入不一致')
        # 去出用户表中查询是否存在该用户名的记录
        old_users = User.objects.filter(username=username)
        # 若存在，则表示该用户名已被注册，返回注册错误信息
        if old_users:
            return HttpResponse('用户名已注册')
        # 哈希算法-给定明文，计算出一段定长的，不可逆的值 md5，sha-256
        # 特点：定长输出，md5：32位16进制；不可逆：无法反向计算出对应的明文，雪崩效应：输入改变，输出必变
        # 哈希算法，对密码进行加密
        m = hashlib.md5()
        m.update(password_1.encode())
        password_m = m.hexdigest()
        # 创建新的用户
        try:
            # 在用户信息表中插入新的记录
            user = User.objects.create(username=username, password=password_m)
            # 在用户标签表中插入用户的标签
            for tag in tags:
                UserTag.objects.create(user_id_id=user.id, tag_id_id=int(tag))
        # 若在数据库中插入失败，则返回注册错误信息
        except Exception as e:
            return HttpResponse('注册失败')
        # 注册成功，跳转至用户登录页面
        return HttpResponseRedirect('/user/login')


# 用户登录页面
def login_view(request):
    # GET请求方式：打开用户登录页面
    if request.method == 'GET':
        # 返回用户登录页面
        return render(request, 'user/login.html')
    # POST请求方式：提交登录请求
    elif request.method == 'POST':
        # 用户名
        username = request.POST['username']
        # 密码
        password = request.POST['password']
        # 去用户信息表中查询是否存在该用户
        try:
            user = User.objects.get(username=username)
        # 若不存在，返回登录失败信息
        except Exception as e:
            return HttpResponse('用户名或密码错误')
        # 密码加密，与数据库中加密密码进行比对
        m = hashlib.md5()
        m.update(password.encode())
        # 如果比对失败，说明密码输入错误，返回登录失败信息
        if m.hexdigest() != user.password:
            return HttpResponse('用户名或密码错误')
        # 创建session对象
        request.session['username'] = username
        request.session['uid'] = user.id
        # 新闻首页跳转对象
        resp = HttpResponseRedirect('/')
        # 如果用户勾选了“记住我”
        if 'REMEMBER' in request.POST:
            # 创建Cookies对象，有效期3天
            resp.set_cookie('username', username, 3600 * 24 * 3)
            resp.set_cookie('uid', user.id, 3600 * 24 * 3)
        # 登录成功，跳转至新闻首页
        return resp
