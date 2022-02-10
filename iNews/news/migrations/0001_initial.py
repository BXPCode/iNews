# Generated by Django 3.2 on 2021-05-11 02:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Cate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64, verbose_name='类别名')),
            ],
        ),
        migrations.CreateModel(
            name='News',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=64, verbose_name='标题')),
                ('author', models.CharField(default='', max_length=64, verbose_name='作者')),
                ('abstract', models.CharField(default='', max_length=128, verbose_name='摘要')),
                ('content', models.TextField(default='', verbose_name='内容')),
                ('picture', models.ImageField(default='image/news.jpg', upload_to='', verbose_name='配图')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('read_num', models.IntegerField(default=0, verbose_name='浏览量')),
                ('vote_num', models.IntegerField(default=0, verbose_name='点赞量')),
                ('comment_num', models.IntegerField(default=0, verbose_name='评论量')),
                ('hot_num', models.FloatField(default=0, verbose_name='热度值')),
                ('cate_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='news.cate')),
            ],
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='', max_length=64, verbose_name='标签名')),
            ],
        ),
        migrations.CreateModel(
            name='NewsTag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('news_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='news.news')),
                ('tag_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='news.tag')),
            ],
        ),
        migrations.CreateModel(
            name='NewsSim',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sim_num', models.FloatField(default=0, verbose_name='新闻相似度')),
                ('news_id_base', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='news_sim', to='news.news')),
                ('news_id_sim', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='news.news')),
            ],
        ),
    ]
