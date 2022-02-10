from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore, register_events, register_job
from news.newsRec.userCFRecJude import jude
from user.userDeal.userDeal import cal_user_sim

scheduler = BackgroundScheduler()
scheduler.add_jobstore(DjangoJobStore(), "default")


# 每隔10分钟运行一次
@register_job(scheduler, "interval", seconds=600, replace_existing=True)
def test_job():
    # 更新用相似度
    cal_user_sim()
    # 更新最优k值
    jude()


register_events(scheduler)
scheduler.start()
