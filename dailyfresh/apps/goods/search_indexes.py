# 定义索引类

from haystack import indexes
from .models import GoodsSKU
#指定对于某个类的某些数据建立索引
class GoodsSKUIndex(indexes.SearchIndex, indexes.Indexable):

    # 索引字段 use_template=True 指定根据表中的哪些字段建立文件，把说明放在一个文件中
    text = indexes.CharField(document=True, use_template=True)

    # 返回模型类别
    def get_model(self):
        return GoodsSKU

    # 建立索引的数据
    def index_queryset(self, using=None):
        return self.get_model().objects.all()