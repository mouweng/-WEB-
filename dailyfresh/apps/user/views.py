from django.shortcuts import render,redirect
from django.core.urlresolvers import reverse
from django.views.generic import View
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import SignatureExpired
from django.http import HttpResponse
from django.conf import settings
from django.contrib.auth import authenticate,login,logout
from celery_tasks.tasks import send_register_active_email
from django.core.mail import send_mail
from utils.mixin import LoginRequiredMixin
from .models import User,Address
from goods.models import GoodsSKU
from order.models import OrderInfo,OrderGoods
from  django.core.paginator import Paginator
from django_redis import get_redis_connection
import re
#/user/register
def register(request):
    #pos和get时候不同的处理
    if request.method == 'GET':
        return render(request,'register.html')
    else:
        #进行注册处理
        username = request.POST.get('user_name')
        password = request.POST.get('pwd')
        email = request.POST.get('email')
        allow = request.POST.get('allow')

        # 进行数据校验
        if not all([username, password, email]):
            # 数据不完整
            return render(request, 'register.html', {'errmsg': '数据不完整'})

        # 校验邮箱
        if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
            return render(request, 'register.html', {'errmsg': '邮箱不合法'})

        # 校验协议
        if allow != 'on':
            return render(request, 'register.html', {'errmsg': '请同意协议'})

        # 校验用户名是否重复
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            # 用户名不存在
            user = None
        if user:
            # 用户名已存在
            return render(request, 'register.html', {'errmsg': '用户名已存在'})
        # 进行业务处理：进行用户注册
        user = User.objects.create_user(username, email, password)
        user.is_active = 0
        user.save()

        # 返回一个应答,跳转到首页
        return redirect(reverse('goods:index'))

class RegisterView(View):
    '''注册'''
    def get(self,request):
        return render(request,'register.html')
    def post(self,request):
        # 进行注册处理
        username = request.POST.get('user_name')
        password = request.POST.get('pwd')
        email = request.POST.get('email')
        allow = request.POST.get('allow')

        # 进行数据校验
        if not all([username, password, email]):
            # 数据不完整
            return render(request, 'register.html', {'errmsg': '数据不完整'})

        # 校验邮箱
        if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
            return render(request, 'register.html', {'errmsg': '邮箱不合法'})

        # 校验协议
        if allow != 'on':
            return render(request, 'register.html', {'errmsg': '请同意协议'})

        # 校验用户名是否重复
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            # 用户名不存在
            user = None
        if user:
            # 用户名已存在
            return render(request, 'register.html', {'errmsg': '用户名已存在'})
        # 进行业务处理：进行用户注册
        user = User.objects.create_user(username, email, password)
        user.is_active = 0
        user.save()

        # 发送激活邮件，包含激活链接
        # 激活链接中需要包含用户的身份信息

        #加密用户的身份信息,生成激活的token
        serializer = Serializer(settings.SECRET_KEY,3600)
        info = {'confirm':user.id}
        token = serializer.dumps(info) #返回byte数据
        token = token.decode()

        #发邮件
        send_register_active_email.delay(email,username,token)
        # 返回一个应答,跳转到首页
        return redirect(reverse('goods:index'))


class ActiveView(View):
    def get(self,request,token):
        '''用户激活'''
        #进行解密,获取要激活的用户信息
        serializer = Serializer(settings.SECRET_KEY, 3600)
        try:
            info = serializer.loads(token)
            #获取激活用户的id
            user_id = info['confirm']
            #根据id获取用户
            user = User.objects.get(id=user_id)
            user.is_active=1
            user.save()

            # 跳转到登录页面
            return redirect('user:login')
        except SignatureExpired as e:
            #激活链接已经过期
            return HttpResponse('激活链接已过期')


#/user/login
class LoginView(View):
    '''登录'''
    def get(self,request):
        '''显示登录界面'''
        # 判断是否记住了用户名
        if 'username' in request.COOKIES:
            username = request.COOKIES.get('username')
            checked = 'checked'
        else:
            username = ''
            checked = ''
        # 使用模板
        return render(request,'login.html',{'username':username,'checked':checked})

    def post(self,request):
        '''登录校验'''
        #接受数据
        username = request.POST.get('username')
        password = request.POST.get('pwd')

        #校验数据
        if not all([username,password]):
            return render(request,'login.html',{'errmsg':'数据不完整'})

        #业务处理:登录校验
        user = authenticate(username=username,password=password)
        if user is not None:
            if user.is_active:
                # 用户已激活
                # 记录用户的登录状态
                login(request,user)

                #获取登陆后要跳转到的地址,默认跳转到首页
                next_url = request.GET.get('next',reverse('goods:index'))

                # 页面跳转到首页
                response = redirect(next_url)

                #判断是否记住用户名
                remember = request.POST.get('remember')
                if remember== 'on':
                    # 记住用户名
                    response.set_cookie('username',username,max_age=7*24*3600)
                else:
                    response.delete_cookie('username')

                # 返回response
                return response
            else:
                # 账户未激活
                return render(request, 'login.html', {'errmsg': '账户未激活'})
        else:
            #用户名或密码错误
            return render(request, 'login.html', {'errmsg': '用户名或密码错误'})


class LogoutView(View):
    def get(self,request):
        '''退出登录'''
        # 清楚用户的session信息
        logout(request)

        #跳转到首页
        return redirect(reverse('goods:index'))


# /user
class UserInfoView(LoginRequiredMixin,View):
    def get(self,request):



        #获取用户的个人信息
        user = request.user
        address = Address.objects.get_default_address(user)

        #获取用户的历史浏览记录
        # from redis import StrictRedis
        # sr = StrictRedis(host='127.0.0.1',port=6379,db=9)
        con = get_redis_connection('default')

        # 取出用户的历史浏览记录
        history_key = 'history_%d'%user.id

        # 获取用户最新浏览的五个商品的id
        sku_ids = con.lrange(history_key,0,4)

        # 从数据库中查询用户浏览的商品的具体信息
        goods_li = []
        for id in sku_ids:
            good = GoodsSKU.objects.get(id=id)
            goods_li.append(good)

        # 组织上下文
        context = {'page':'user',
                    'address':address,
                    'goods_li':goods_li}

        return render(request,'user_center_info.html',context)

# /user/order
class UserOrderView(LoginRequiredMixin,View):

    def get(self,request,page):

        #获取用户的订单信息
        user = request.user
        orders = OrderInfo.objects.filter(user = user).order_by('-create_time')

        # 遍历获取订单商品的信息
        for order in orders:
            order_skus = OrderGoods.objects.filter(order_id=order.order_id)

            #遍历order_skus计算商品的小计
            for order_sku in order_skus:
                # 计算小计
                amount = order_sku.count * order_sku.price
                # 动态给order_sku增加属性，保存订单商品的小计
                order_sku.amount = amount

            # 动态给order增加属性， 保存订单状态标题
            order.status_name = OrderInfo.ORDER_STATUS[order.order_status]
            # 给order增加属性，保存订单商品的信息
            order.order_skus = order_skus

        # 分页
        paginator = Paginator(orders, 2)

        # 获取第page页的内容
        try:
            page = int(page)
        except Exception as e:
            page = 1

        if page>paginator.num_pages:
            page = 1

        #获取page页的实例对象
        order_page = paginator.page(page)

        num_pages = paginator.num_pages
        if num_pages < 5:
            pages = range(1,num_pages+1)
        elif page <=3:
            pages = range(1,6)
        elif num_pages - page <= 2:
            pages = range(num_pages-4,num_pages+1)
        else:
            pages = range(page-2,page+3)

        # 组织上下文
        context = {'order_page':order_page,
                   'pages':pages,
                   'page': 'order'}

        return render(request,'user_center_order.html',context)


# /user/order
class UserAddressView(LoginRequiredMixin,View):
    def get(self, request):

        user = request.user
        #获取用户的收获地址
        # try:
        #     address = Address.objects.get(user=user,is_default=True)
        # except Address.DoesNotExist:
        #     #不存在默认收货地址
        #     address=None
        address = Address.objects.get_default_address(user)

        #使用模板
        return render(request, 'user_center_site.html',{'page':'address','address':address})

    def post(self,request):

        #接受数据
        receiver = request.POST.get('receiver')
        addr = request.POST.get('addr')
        zipcode = request.POST.get('zipcode')
        phone = request.POST.get('phone')
        #校验数据

        if not all([receiver,addr,phone]):
            return render(request,'user_center_site.html',{'errmsg':'数据不完整'})

        if not re.match(r'1[3|4|5|7|8][0-9]{9}$',phone):
            return render(request,'user_center_site.html',{'errmsg':'手机格式不正确'})

        # 业务处理:地址添加
        # 如果用户已存在默认收货地址，添加的地址不作为默认收货地址，否则作为默认收货地址
        #获取登录用户对应的user
        user = request.user
        # try:
        #     address = Address.objects.get(user=user,is_default=True)
        # except Address.DoesNotExist:
        #     #不存在默认收货地址
        #     address=None
        address = Address.objects.get_default_address(user)

        if address:
            is_default = False
        else:
            is_default = True


        #添加地址
        Address.objects.create(user=user,
                               receiver=receiver,
                               addr=addr,
                               zip_code=zipcode,
                               phone=phone,
                               is_default=is_default
                               )

        #返回应答,刷新地址页面
        return redirect(reverse('user:address'))

