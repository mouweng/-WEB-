from django.conf.urls import url
from .views import OrderPlaceView,OrderCommitView
urlpatterns = [
    url(r'^place$',OrderPlaceView.as_view(),name='place'),#首页
    url(r'^commit$',OrderCommitView.as_view(),name='commit'),#订单创建
]
