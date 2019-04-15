from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from . import views
from .views import RegisterView,ActiveView,LoginView,LogoutView,UserInfoView,UserOrderView,UserAddressView
urlpatterns = [
    #url(r'^register$',views.register,name='register'),#注册
    url(r'^register$',RegisterView.as_view(),name='register'),#注册
    url(r'^active/(?P<token>.*)$',ActiveView.as_view(),name='active'),#激活
    url(r'^login$',LoginView.as_view(),name='login'),#登录
    url(r'^logout$',LogoutView.as_view(),name='logout'),#退出

    # url(r'^$',login_required(UserInfoView.as_view()),name='user'),#用户中心信息页
    # url(r'^order/',login_required(UserOrderView.as_view()),name='order'),#用户中心-订单页
    # url(r'^address/$',login_required(UserAddressView.as_view()),name='address'),#用户中心-地址页

    url(r'^$',UserInfoView.as_view(),name='user'),#用户中心信息页
    url(r'^order/(?P<page>\d+)$',UserOrderView.as_view(),name='order'),#用户中心-订单页
    url(r'^address/$',UserAddressView.as_view(),name='address'),#用户中心-地址页
]