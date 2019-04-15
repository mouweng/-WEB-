#使用celery
from django.conf import settings
from django.core.mail import send_mail
from celery import Celery
import time

#创建一个Celery的实例对象
app = Celery('celery_tasks.tasks',broker='redis://127.0.0.1:6379/8')


# 定义任务函数
@app.task
def send_register_active_email(to_email,username,token):
    '''发送激活邮件'''
    #组织邮件信息
    subject = '天天生鲜欢迎信息'
    sender = settings.EMAIL_FROM
    message = ''
    recevier = [to_email]
    html_message = '<h1>%s,欢迎您成为天天生鲜注册会员</h1>请点击下面链接激活您的账户<br/><a href="http://127.0.0.1:8000/user/active/%s">http://127.0.0.1:80000/user/active/%s</a>' % (
        username, token, token)

    send_mail(subject, message, sender, recevier, html_message=html_message)
    time.sleep(5)