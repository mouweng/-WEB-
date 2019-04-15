from django.shortcuts import render
from django.views.generic import View
from django.http import JsonResponse
from django_redis import  get_redis_connection
from goods.models import GoodsSKU
from utils.mixin import LoginRequiredMixin
# Create your views here.


# /cart/add
class CartAddView(View):
    '''购物车记录添加'''
    def post(self,request):
        '''购物车记录添加'''
        user = request.user
        if not user.is_authenticated:
            return JsonResponse({'res': 0, 'errmsg': '请先登录'})

        # 接收数据
        sku_id = request.POST.get('sku_id')
        count = request.POST.get('count')

        # 数据校验
        if not all([sku_id, count]):
            return JsonResponse({'res':1 , 'errmsg':'数据不完整'})

        #校验添加的商品数量
        try:
            count = int(count)
        except Exception as e:
            return JsonResponse({'res':2, 'errmsg':'商品数目出错'})

        #校验商品是否存在
        try:
            sku = GoodsSKU.objects.get(id=sku_id)
        except GoodsSKU.DoesNotExist:
            #商品不存在
            return JsonResponse({'res':3, 'errmsg':'商品不存在'})



        # 业务处理:添加购物车记录
        #先尝试获取sku_id的值
        conn = get_redis_connection('default')
        cart_key = 'cart_%d'%user.id
        # 先尝试获取sku_id的值
        cart_count = conn.hget(cart_key,sku_id)
        if cart_count:
            # 累加购物车中商品的数目
            count+=int(cart_count)
        #设置hash中的sku_id对应的值

        if count > sku.stock:
            return JsonResponse({'res':4, 'errmsg':'商品库存不足'})
        conn.hset(cart_key, sku_id, count)

        # 计算用户购物车中商品的条目数
        total_count = conn.hlen(cart_key)

        # 返回应答
        return JsonResponse({'res': 5, 'total_count':total_count ,'message': '添加成功'})


class CartInfoView(LoginRequiredMixin,View):
    '''购物车页面显示'''
    def get(self,request):

        # 获取登录的用户
        user = request.user

        # 获取用户购物车中商品的信息
        conn = get_redis_connection('default')
        cart_key = 'cart_%d'%user.id

        cart_dict = conn.hgetall(cart_key)

        skus =[]
        total_count = 0
        total_price = 0
        #遍历获取商品的信息
        for sku_id, count in cart_dict.items():
            # 根据商品的id获取商品的信息
            sku = GoodsSKU.objects.get(id=sku_id)
            # 计算商品的小计
            amount = sku.price*int(count)
            # 动态增加小计
            sku.amount = amount
            # 动态给sku对象增加一个属性，保存购物车中对应商品的数量
            sku.count = count
            skus.append(sku)
            total_count+= int(count)
            total_price+=amount

        context = {'total_count':total_count,'total_price':total_price,'skus':skus}

        return render(request, 'cart.html',context)


class CartUpdateView(View):
    '''购物车记录更新'''
    def post(self,request):
        '''购物车记录跟新'''

        user = request.user
        if not user.is_authenticated:
            return JsonResponse({'res': 0, 'errmsg': '请先登录'})

        # 接收数据
        sku_id = request.POST.get('sku_id')
        count = request.POST.get('count')

        # 数据校验
        if not all([sku_id, count]):
            return JsonResponse({'res':1 , 'errmsg':'数据不完整'})

        #校验添加的商品数量
        try:
            count = int(count)
        except Exception as e:
            return JsonResponse({'res':2, 'errmsg':'商品数目出错'})

        #校验商品是否存在
        try:
            sku = GoodsSKU.objects.get(id=sku_id)
        except GoodsSKU.DoesNotExist:
            #商品不存在
            return JsonResponse({'res':3, 'errmsg':'商品不存在'})


        #业务处理
        conn = get_redis_connection('default')
        cart_key = 'cart_%d'%user.id

        if count > sku.stock:
            return JsonResponse({'res': 4, 'errmsg': '商品库存不足'})

        #更新
        conn.hset(cart_key, sku_id, count)


        #计算用户购物车商品中的总件数
        total_count = 0
        vals = conn.hvals(cart_key)
        for val in vals:
            total_count += int(val)



        #返回应答
        return JsonResponse({'res': 5, 'total_count':total_count,'message': '更新成功'})


class CartDeleteView(View):
    '''购物车记录删除'''
    def post(self,request):
        '''删除购物车记录'''
        user = request.user
        if not user.is_authenticated:
            return JsonResponse({'res': 0, 'errmsg': '请先登录'})

        #接受参数
        sku_id = request.POST.get('sku_id')

        #数据的校验
        if not sku_id:
            return JsonResponse({'res':1 , 'errmsg':'数据不完整'})

        #校验商品是否存在
        try:
            sku = GoodsSKU.objects.get(id=sku_id)
        except GoodsSKU.DoesNotExist:
            #商品不存在
            return JsonResponse({'res':2, 'errmsg':'商品不存在'})

        # 业务处理，删除购物车记录
        conn = get_redis_connection('default')
        cart_key = 'cart_%d'%user.id
        #删除 hdel
        conn.hdel(cart_key,sku_id)

        #计算用户购物车商品中的总件数
        total_count = 0
        vals = conn.hvals(cart_key)
        for val in vals:
            total_count += int(val)

        #返回应答
        return JsonResponse({'res': 3 ,'total_count':total_count ,'message': '更新成功'})