import xadmin
from .models import User,Address
from xadmin import views
from xadmin.plugins.auth import UserAdmin

class BaseSetting(object):
    """增加修改主题"""
    enable_themes = True
    use_bootswatch = True

class GlobalSetting(object):
    """页头页脚title"""
    site_title = '某翁'
    site_footer = '某翁'
    menu_style = 'accordion'#左侧设置菜单下拉




class UserAdmin(object):
    pass

xadmin.site.unregister(User)
xadmin.site.register(User, UserAdmin)


class AddressAdmin(object):
    list_display = ['id','user','receiver','addr','zip_code','phone','is_default']

xadmin.site.register(Address, AddressAdmin)
