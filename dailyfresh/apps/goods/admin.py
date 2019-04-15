from django.contrib import admin
import xadmin

from .models import GoodsType,IndexGoodsBanner,IndexPromotionBanner,Goods,GoodsImage,GoodsSKU,IndexTypeGoodsBanner

@admin.register(GoodsType)
class GoodsTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')


@admin.register(IndexGoodsBanner)
class IndexGoodsBannerAdmin(admin.ModelAdmin):
    list_display = ('id', 'sku','image','index')

@admin.register(IndexPromotionBanner)
class IndexPromotionBannerAdmin(admin.ModelAdmin):
    list_display = ('id', 'name','url','image','index')

@admin.register(Goods)
class GoodsAdmin(admin.ModelAdmin):
    list_display = ('id', 'name','detail')


@admin.register(GoodsImage)
class GoodsImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'sku','image')

@admin.register(GoodsSKU)
class GoodsSKUAdmin(admin.ModelAdmin):
    list_display = ('id', 'type','goods','name','desc','price','unite','image','stock','sales','status')

    list_per_page = 10

    ordering = ('type',)


@admin.register(IndexTypeGoodsBanner)
class IndexTypeGoodsBannerAdmin(admin.ModelAdmin):
    list_display = ('id', 'type','sku','display_type','index')



# Register your models here.
