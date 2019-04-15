import xadmin
from .models import GoodsType,IndexGoodsBanner,IndexPromotionBanner,Goods,GoodsImage,GoodsSKU,IndexTypeGoodsBanner


class GoodsTypeAdmin(object):
    list_display = ('id', 'name')
xadmin.site.register(GoodsType, GoodsTypeAdmin)


class IndexGoodsBannerAdmin(object):
    list_display = ('id', 'sku','image','index')
xadmin.site.register(IndexGoodsBanner, IndexGoodsBannerAdmin)


class IndexPromotionBannerAdmin(object):
    list_display = ('id', 'name', 'url', 'image', 'index')
xadmin.site.register(IndexPromotionBanner, IndexPromotionBannerAdmin)


class GoodsAdmin(object):
    list_display = ('id', 'name', 'detail')
xadmin.site.register(Goods, GoodsAdmin)


class GoodsImageAdmin(object):
    list_display = ('id', 'sku', 'image')
xadmin.site.register(GoodsImage, GoodsImageAdmin)


class GoodsSKUAdmin(object):
    list_display = ('id', 'type', 'goods', 'name', 'desc', 'price', 'unite', 'image', 'stock', 'sales', 'status')
xadmin.site.register(GoodsSKU, GoodsSKUAdmin)


class IndexTypeGoodsBannerAdmin(object):
    list_display = ('id', 'type', 'sku', 'display_type', 'index')
xadmin.site.register(IndexTypeGoodsBanner, IndexTypeGoodsBannerAdmin)